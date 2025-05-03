from typing import List, Optional, Protocol
from DeckManagement.domain.models.Deck import Deck


class IDeckRepository(Protocol):
    """
    Repository interface for Deck persistence. All methods must filter by user_id to ensure data isolation.
    """

    def add(self, deck: Deck) -> Deck:
        """Adds a new deck. Returns the deck with assigned ID and timestamps. Raises IntegrityError on duplicate name."""
        ...

    def get_by_id(self, deck_id: int, user_id: int) -> Optional[Deck]:
        """Fetches a deck by its ID for the given user. Returns None if not found."""
        ...

    def get_by_name(self, name: str, user_id: int) -> Optional[Deck]:
        """Fetches a deck by its name for the given user. Returns None if not found."""
        ...

    def list_all(self, user_id: int) -> List[Deck]:
        """Returns all decks for the given user, ordered by name."""
        ...

    def update(self, deck: Deck) -> None:
        """Updates an existing deck's name. Requires user_id in the deck object."""
        ...

    def delete(self, deck_id: int, user_id: int) -> None:
        """Deletes a deck by ID for the given user."""
        ...
