from typing import List, Optional
from DeckManagement.domain.models.Deck import Deck


class IDeckRepository:
    """
    Repository interface for Deck persistence. All methods must filter by user_id to ensure data isolation.
    """

    def add(self, deck: Deck) -> Deck:
        """Adds a new deck. Returns the deck with assigned ID and timestamps. Raises IntegrityError on duplicate name."""
        raise NotImplementedError

    def get_by_id(self, deck_id: int, user_id: int) -> Optional[Deck]:
        """Fetches a deck by its ID for the given user. Returns None if not found."""
        raise NotImplementedError

    def get_by_name(self, name: str, user_id: int) -> Optional[Deck]:
        """Fetches a deck by its name for the given user. Returns None if not found."""
        raise NotImplementedError

    def list_all(self, user_id: int) -> List[Deck]:
        """Returns all decks for the given user, ordered by name."""
        raise NotImplementedError

    def update(self, deck: Deck) -> None:
        """Updates an existing deck's name. Requires user_id in the deck object."""
        raise NotImplementedError

    def delete(self, deck_id: int, user_id: int) -> None:
        """Deletes a deck by ID for the given user."""
        raise NotImplementedError
