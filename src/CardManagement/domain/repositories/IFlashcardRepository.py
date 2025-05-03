from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from CardManagement.domain.models.Flashcard import Flashcard


class IFlashcardRepository(ABC):
    """
    Abstract repository interface for Flashcard persistence.
    """

    @abstractmethod
    def add(self, flashcard: Flashcard) -> Flashcard:
        """
        Adds a new flashcard and returns the instance with assigned 'id' and timestamps.
        """

    @abstractmethod
    def get_by_id(self, flashcard_id: int) -> Optional[Flashcard]:
        """
        Retrieves a flashcard by its ID. Returns None if not found.
        """

    @abstractmethod
    def list_by_deck_id(self, deck_id: int) -> List[Flashcard]:
        """
        Returns a list of flashcards belonging to the given deck.
        """

    @abstractmethod
    def update(self, flashcard: Flashcard) -> None:
        """
        Updates an existing flashcard (content or FSRS state).
        """

    @abstractmethod
    def delete(self, flashcard_id: int) -> None:
        """
        Deletes a flashcard by its ID.
        """

    @abstractmethod
    def get_fsrs_card_data_for_deck(self, deck_id: int) -> List[Tuple[int, Optional[str]]]:
        """
        Retrieves tuples (flashcard_id, fsrs_state) for all flashcards in the deck.
        """
