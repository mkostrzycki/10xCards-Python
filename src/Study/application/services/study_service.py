"""Study service for spaced repetition system."""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple, Any

from CardManagement.domain.models.Flashcard import Flashcard
from CardManagement.domain.repositories.IFlashcardRepository import IFlashcardRepository
from Study.domain.repositories.IReviewLogRepository import IReviewLogRepository
from Shared.application.session_service import SessionService
from Shared.infrastructure.config import get_config

logger = logging.getLogger(__name__)


class StudyService:
    """Service responsible for spaced repetition study sessions using FSRS algorithm."""

    def __init__(
        self,
        flashcard_repository: IFlashcardRepository,
        review_log_repository: IReviewLogRepository,
        session_service: SessionService,
    ):
        """Initialize the study service.

        Args:
            flashcard_repository: Repository for flashcard data access.
            review_log_repository: Repository for review logs data access.
            session_service: Service for accessing current user data.
        """
        self.flashcard_repo = flashcard_repository
        self.review_log_repo = review_log_repository
        self.session_service = session_service

        self._config = get_config()
        self._default_fsrs_parameters = tuple(self._config.get("FSRS_DEFAULT_PARAMETERS", []))
        self._default_desired_retention = self._config.get("FSRS_DEFAULT_DESIRED_RETENTION", 0.9)
        self._default_learning_steps_minutes = self._config.get("FSRS_DEFAULT_LEARNING_STEPS_MINUTES", [1, 10])
        self._default_relearning_steps_minutes = self._config.get("FSRS_DEFAULT_RELEARNING_STEPS_MINUTES", [10])
        self._maximum_interval = self._config.get("FSRS_MAXIMUM_INTERVAL", 36500)
        self._enable_fuzzing = self._config.get("FSRS_ENABLE_FUZZING", True)

        # Scheduler will be initialized during start_session
        self.scheduler: Any = None

        # Session state
        self.current_study_session_queue: List[Tuple[Flashcard, Any]] = []
        self.current_card_index: int = -1
        self.current_deck_id: Optional[int] = None

        # Dynamically import fsrs to avoid issues if the library is not available during type checking
        try:
            global Scheduler, FSRSCard, FSRSRating, FSRSReviewLog, State
            from fsrs import Scheduler, Card as FSRSCard, Rating as FSRSRating, ReviewLog as FSRSReviewLog, State

            logger.info("Successfully imported FSRS library")
        except ImportError as e:
            logger.error(f"Failed to import FSRS library: {e}")
            # Allow the class to be defined but scheduler will be None
            # This will cause runtime errors if methods are called without the library

    def start_session(self, deck_id: int) -> Optional[Tuple[Flashcard, Any]]:
        """Start a new study session for a deck.

        Args:
            deck_id: ID of the deck to study.

        Returns:
            The first flashcard to review and its FSRS card state, or None if no cards are due.

        Raises:
            ValueError: If no user is logged in or deck_id is invalid.
            RuntimeError: If FSRS library is not available.
        """
        user = self.session_service.get_current_user()
        if not user or not user.id:
            logger.error("Attempted to start study session without logged in user")
            raise ValueError("User must be logged in to start a study session")

        user_id = user.id

        # Clear previous session state
        self.end_session()

        # Set current deck
        self.current_deck_id = deck_id

        # Initialize FSRS scheduler
        self._initialize_scheduler(user_id)

        # Load and prepare cards
        all_cards = self._load_and_prepare_fsrs_cards(deck_id, user_id)

        # Filter and sort due cards
        due_cards = self._filter_and_sort_due_cards(all_cards)

        # Update session state
        self.current_study_session_queue = due_cards

        if due_cards:
            self.current_card_index = 0
            logger.info(f"Started study session for deck {deck_id} with {len(due_cards)} due cards")
            return due_cards[0]
        else:
            logger.info(f"Started study session for deck {deck_id} but no cards are due")
            return None

    def get_current_card_for_review(self) -> Optional[Tuple[Flashcard, Any]]:
        """Get the current card in the study session.

        Returns:
            The current flashcard and its FSRS card state, or None if no session is active or all cards reviewed.
        """
        if not self.current_study_session_queue or self.current_card_index < 0:
            return None

        try:
            return self.current_study_session_queue[self.current_card_index]
        except IndexError:
            logger.error(
                f"Invalid card index: {self.current_card_index} for queue of length {len(self.current_study_session_queue)}"
            )
            return None

    def record_review(self, flashcard_id: int, rating_value: int) -> Tuple[Flashcard, Any]:
        """Record a review for the current card with the given rating.

        Args:
            flashcard_id: ID of the flashcard being reviewed.
            rating_value: Rating value (1-4) corresponding to FSRS ratings (Again, Hard, Good, Easy).

        Returns:
            The updated flashcard and its new FSRS card state.

        Raises:
            ValueError: If flashcard_id doesn't match current card or rating is invalid.
            RuntimeError: If FSRS scheduler is not initialized or other errors occur.
        """
        if not self.scheduler:
            raise RuntimeError("FSRS scheduler not initialized. Start a session first.")

        user = self.session_service.get_current_user()
        if not user or not user.id:
            raise ValueError("User must be logged in to record reviews")

        user_id = user.id

        # Get current card
        current_card = self.get_current_card_for_review()
        if not current_card:
            raise ValueError("No active card to review")

        flashcard, fsrs_card = current_card

        # Verify flashcard_id matches current card
        if not flashcard.id or flashcard.id != flashcard_id:
            raise ValueError(f"Flashcard ID mismatch: expected {flashcard.id}, got {flashcard_id}")

        # Validate rating
        if rating_value < 1 or rating_value > 4:
            raise ValueError(f"Invalid rating value: {rating_value}. Must be between 1 and 4.")

        try:
            # Convert rating to FSRS Rating object
            fsrs_rating = FSRSRating(rating_value)

            # Review card with FSRS
            updated_fsrs_card, review_log = self.scheduler.review_card(fsrs_card, fsrs_rating)

            # Update flashcard FSRS state in domain model
            flashcard.fsrs_state = json.dumps(updated_fsrs_card.to_dict())

            # Save updated flashcard to repository
            self.flashcard_repo.update(flashcard)

            # Save review log
            scheduler_params_json = json.dumps(list(self.scheduler.parameters))
            self.review_log_repo.add(
                user_id=user_id,
                flashcard_id=flashcard_id,
                review_log_data=review_log.to_dict(),
                rating=rating_value,
                reviewed_at=review_log.review_datetime,
                scheduler_params_json=scheduler_params_json,
            )

            # Update current card in session queue
            self.current_study_session_queue[self.current_card_index] = (flashcard, updated_fsrs_card)

            logger.info(f"Recorded review for flashcard {flashcard_id} with rating {rating_value}")
            return flashcard, updated_fsrs_card

        except Exception as e:
            logger.error(f"Error recording review: {e}", exc_info=True)
            raise RuntimeError(f"Failed to record review: {str(e)}") from e

    def proceed_to_next_card(self) -> Optional[Tuple[Flashcard, Any]]:
        """Move to the next card in the study session.

        Returns:
            The next flashcard and its FSRS card state, or None if no more cards are available.
        """
        if not self.current_study_session_queue:
            return None

        self.current_card_index += 1

        if self.current_card_index < len(self.current_study_session_queue):
            return self.current_study_session_queue[self.current_card_index]
        else:
            # End of queue reached
            return None

    def get_session_progress(self) -> Tuple[int, int]:
        """Get the current progress of the study session.

        Returns:
            A tuple of (current_position, total_cards) where current_position is 1-indexed.
            Returns (0, 0) if no session is active.
        """
        if not self.current_study_session_queue:
            return (0, 0)

        total = len(self.current_study_session_queue)

        if self.current_card_index < 0:
            return (0, total)
        elif self.current_card_index >= total:
            return (total, total)
        else:
            return (self.current_card_index + 1, total)

    def end_session(self) -> None:
        """End the current study session and clear session state."""
        self.current_study_session_queue = []
        self.current_card_index = -1
        self.current_deck_id = None
        # Don't clear scheduler as it can be reused

    def _initialize_scheduler(self, user_id: int) -> None:
        """Initialize the FSRS scheduler with parameters.

        Args:
            user_id: ID of the current user (for future personalized parameters).

        Raises:
            RuntimeError: If FSRS library is not available.
        """
        if "Scheduler" not in globals():
            raise RuntimeError("FSRS library not loaded. Cannot initialize scheduler.")

        # TODO: In the future, load user-specific parameters from a repository
        # For now, use default parameters from config

        learning_steps = [timedelta(minutes=m) for m in self._default_learning_steps_minutes]
        relearning_steps = [timedelta(minutes=m) for m in self._default_relearning_steps_minutes]

        self.scheduler = Scheduler(
            parameters=self._default_fsrs_parameters,
            desired_retention=self._default_desired_retention,
            learning_steps=tuple(learning_steps),
            relearning_steps=tuple(relearning_steps),
            maximum_interval=self._maximum_interval,
            enable_fuzzing=self._enable_fuzzing,
        )

        logger.debug(f"Initialized FSRS scheduler with default parameters for user {user_id}")

    def _load_and_prepare_fsrs_cards(self, deck_id: int, user_id: int) -> List[Tuple[Flashcard, Any]]:
        """Load flashcards from the repository and prepare FSRS card objects.

        Args:
            deck_id: ID of the deck to load cards from.
            user_id: ID of the current user.

        Returns:
            List of tuples containing (Flashcard, FSRSCard).

        Raises:
            RuntimeError: If FSRS library is not available.
        """
        if "FSRSCard" not in globals():
            raise RuntimeError("FSRS library not loaded. Cannot prepare cards.")

        flashcards = self.flashcard_repo.list_by_deck_id(deck_id)
        result = []

        for flashcard in flashcards:
            try:
                # If the card has FSRS state, deserialize it
                if flashcard.fsrs_state:
                    fsrs_card_dict = json.loads(flashcard.fsrs_state)
                    fsrs_card = FSRSCard.from_dict(fsrs_card_dict)
                else:
                    # New card for FSRS
                    fsrs_card = FSRSCard()
                    # Save initial state
                    flashcard.fsrs_state = json.dumps(fsrs_card.to_dict())
                    self.flashcard_repo.update(flashcard)

                result.append((flashcard, fsrs_card))

            except json.JSONDecodeError as e:
                logger.error(f"Error deserializing FSRS state for flashcard {flashcard.id}: {e}")
                # Treat as new card
                fsrs_card = FSRSCard()
                flashcard.fsrs_state = json.dumps(fsrs_card.to_dict())
                self.flashcard_repo.update(flashcard)
                result.append((flashcard, fsrs_card))

        logger.debug(f"Loaded and prepared {len(result)} cards for deck {deck_id}")
        return result

    def _filter_and_sort_due_cards(self, all_session_cards: List[Tuple[Flashcard, Any]]) -> List[Tuple[Flashcard, Any]]:
        """Filter cards that are due for review and sort them.

        Args:
            all_session_cards: List of all cards in the session.

        Returns:
            Filtered and sorted list of cards that are due for review.
        """
        now = datetime.now(timezone.utc)
        due_cards = []

        for flashcard, fsrs_card in all_session_cards:
            # Check if card is due (due <= now)
            if fsrs_card.due <= now:
                due_cards.append((flashcard, fsrs_card))

        # Sort by due date (ascending)
        due_cards.sort(key=lambda item: item[1].due)

        return due_cards
