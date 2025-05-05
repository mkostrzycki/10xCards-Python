import logging
from datetime import datetime
from typing import List, Optional
from sqlite3 import IntegrityError

from CardManagement.domain.models.Flashcard import Flashcard
from CardManagement.domain.repositories.IFlashcardRepository import IFlashcardRepository


class CardService:
    """Application service for flashcard management operations"""

    def __init__(self, flashcard_repository: IFlashcardRepository):
        self.flashcard_repository = flashcard_repository
        self.logger = logging.getLogger(__name__)

    def create_flashcard(
        self, deck_id: int, front_text: str, back_text: str, source: str = "manual", ai_model_name: Optional[str] = None
    ) -> Flashcard:
        """
        Creates a new flashcard in the specified deck.

        Args:
            deck_id: The ID of the deck to add the flashcard to
            front_text: Text for the front of the flashcard (max 200 chars)
            back_text: Text for the back of the flashcard (max 500 chars)
            source: Source of the flashcard ('manual', 'ai-generated', 'ai-edited')
            ai_model_name: Name of the AI model used (if applicable)

        Returns:
            The created Flashcard with ID and timestamps

        Raises:
            ValueError: If texts are empty or too long
        """
        # Validate texts
        front_text = front_text.strip()
        back_text = back_text.strip()

        if not front_text:
            raise ValueError("Tekst na przedniej stronie nie może być pusty")
        if not back_text:
            raise ValueError("Tekst na tylnej stronie nie może być pusty")
        if len(front_text) > 200:
            raise ValueError("Tekst na przedniej stronie nie może być dłuższy niż 200 znaków")
        if len(back_text) > 500:
            raise ValueError("Tekst na tylnej stronie nie może być dłuższy niż 500 znaków")

        # Create and persist the flashcard
        flashcard = Flashcard(
            id=None,  # Will be set by repository
            deck_id=deck_id,
            front_text=front_text,
            back_text=back_text,
            fsrs_state=None,  # Initial state, will be set when first reviewed
            source=source,
            ai_model_name=ai_model_name,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        try:
            created_flashcard = self.flashcard_repository.add(flashcard)
            self.logger.info(f"Created flashcard in deck {deck_id}")
            return created_flashcard
        except Exception as e:
            self.logger.error(f"Failed to create flashcard in deck {deck_id}: {str(e)}")
            raise

    def update_flashcard(
        self,
        flashcard_id: int,
        front_text: str,
        back_text: str,
        source: Optional[str] = None,
        ai_model_name: Optional[str] = None,
    ) -> None:
        """
        Updates an existing flashcard.

        Args:
            flashcard_id: The ID of the flashcard to update
            front_text: New text for the front (max 200 chars)
            back_text: New text for the back (max 500 chars)
            source: New source if changed
            ai_model_name: New AI model name if changed

        Raises:
            ValueError: If texts are empty or too long, or if flashcard doesn't exist
        """
        # Validate texts
        front_text = front_text.strip()
        back_text = back_text.strip()

        if not front_text:
            raise ValueError("Tekst na przedniej stronie nie może być pusty")
        if not back_text:
            raise ValueError("Tekst na tylnej stronie nie może być pusty")
        if len(front_text) > 200:
            raise ValueError("Tekst na przedniej stronie nie może być dłuższy niż 200 znaków")
        if len(back_text) > 500:
            raise ValueError("Tekst na tylnej stronie nie może być dłuższy niż 500 znaków")

        # Get existing flashcard
        flashcard = self.flashcard_repository.get_by_id(flashcard_id)
        if not flashcard:
            raise ValueError("Fiszka nie istnieje")

        try:
            # Update fields
            flashcard.front_text = front_text
            flashcard.back_text = back_text
            if source:
                flashcard.source = source
            if ai_model_name:
                flashcard.ai_model_name = ai_model_name
            flashcard.updated_at = datetime.now()

            self.flashcard_repository.update(flashcard)
            self.logger.info(f"Updated flashcard {flashcard_id}")
        except Exception as e:
            self.logger.error(f"Failed to update flashcard {flashcard_id}: {str(e)}")
            raise

    def list_by_deck_id(self, deck_id: int) -> List[Flashcard]:
        """
        Lists all flashcards in a deck.

        Args:
            deck_id: The ID of the deck to list flashcards from

        Returns:
            List of Flashcard objects in the deck, ordered by creation date
        """
        try:
            flashcards: List[Flashcard] = self.flashcard_repository.list_by_deck_id(deck_id)
            self.logger.debug(f"Listed {len(flashcards)} flashcards for deck {deck_id}")
            return flashcards
        except Exception as e:
            self.logger.error(f"Failed to list flashcards for deck {deck_id}: {str(e)}")
            raise

    def delete_flashcard(self, flashcard_id: int) -> None:
        """
        Deletes a flashcard.

        Args:
            flashcard_id: The ID of the flashcard to delete

        Raises:
            ValueError: If the flashcard doesn't exist
        """
        # Verify flashcard exists
        flashcard = self.flashcard_repository.get_by_id(flashcard_id)
        if not flashcard:
            raise ValueError("Fiszka nie istnieje")

        try:
            self.flashcard_repository.delete(flashcard_id)
            self.logger.info(f"Deleted flashcard {flashcard_id}")
        except Exception as e:
            self.logger.error(f"Failed to delete flashcard {flashcard_id}: {str(e)}")
            raise

    def get_flashcard(self, flashcard_id: int) -> Optional[Flashcard]:
        """
        Retrieves a flashcard by ID.

        Args:
            flashcard_id: The ID of the flashcard to retrieve

        Returns:
            The Flashcard if found, None otherwise
        """
        try:
            flashcard = self.flashcard_repository.get_by_id(flashcard_id)
            if flashcard:
                self.logger.debug(f"Retrieved flashcard {flashcard_id}")
            else:
                self.logger.debug(f"Flashcard {flashcard_id} not found")
            return flashcard
        except Exception as e:
            self.logger.error(f"Failed to retrieve flashcard {flashcard_id}: {str(e)}")
            raise
