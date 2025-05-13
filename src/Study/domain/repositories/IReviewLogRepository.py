from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class IReviewLogRepository(ABC):
    """Repository interface for managing review logs in the spaced repetition system."""

    @abstractmethod
    def add(
        self,
        user_id: int,
        flashcard_id: int,
        review_log_data: Dict[str, Any],
        rating: int,
        reviewed_at: datetime,
        scheduler_params_json: str,
    ) -> None:
        """Add a new review log entry.

        Args:
            user_id: The ID of the user who performed the review.
            flashcard_id: The ID of the flashcard that was reviewed.
            review_log_data: The serialized FSRS ReviewLog data as a dictionary.
            rating: The rating given by the user (1-4).
            reviewed_at: The datetime when the review was performed.
            scheduler_params_json: JSON string of the FSRS scheduler parameters used for this review.
        """
        pass

    @abstractmethod
    def get_review_logs_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all review logs for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            List of dictionaries containing review log data.
        """
        pass

    @abstractmethod
    def get_review_logs_for_flashcard(self, user_id: int, flashcard_id: int) -> List[Dict[str, Any]]:
        """Get all review logs for a specific flashcard for a user.

        Args:
            user_id: The ID of the user.
            flashcard_id: The ID of the flashcard.

        Returns:
            List of dictionaries containing review log data.
        """
        pass

    @abstractmethod
    def get_last_review_log_for_flashcard(self, user_id: int, flashcard_id: int) -> Optional[Dict[str, Any]]:
        """Get the most recent review log for a specific flashcard for a user.

        Args:
            user_id: The ID of the user.
            flashcard_id: The ID of the flashcard.

        Returns:
            Dictionary containing review log data, or None if no logs exist.
        """
        pass

    @abstractmethod
    def delete_review_logs_for_flashcard(self, user_id: int, flashcard_id: int) -> int:
        """Delete all review logs for a specific flashcard for a user.

        Args:
            user_id: The ID of the user.
            flashcard_id: The ID of the flashcard.

        Returns:
            Number of deleted rows.
        """
        pass

    @abstractmethod
    def delete_review_logs_for_user(self, user_id: int) -> int:
        """Delete all review logs for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            Number of deleted rows.
        """
        pass
