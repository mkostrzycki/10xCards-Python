import logging
from datetime import datetime
from typing import List, Optional
from sqlite3 import IntegrityError

from src.DeckManagement.domain.models.Deck import Deck
from src.DeckManagement.domain.repositories.IDeckRepository import IDeckRepository


class DeckService:
    """Application service for deck management operations"""

    def __init__(self, deck_repository: IDeckRepository):
        self.deck_repository = deck_repository
        self.logger = logging.getLogger(__name__)

    def create_deck(self, name: str, user_id: int) -> Deck:
        """
        Creates a new deck for the user.
        
        Args:
            name: The name of the deck (max 50 chars)
            user_id: The ID of the user creating the deck
            
        Returns:
            The created Deck with ID and timestamps
            
        Raises:
            ValueError: If name is empty or too long
            IntegrityError: If a deck with this name already exists for the user
        """
        # Validate name
        name = name.strip()
        if not name:
            raise ValueError("Nazwa talii nie może być pusta")
        if len(name) > 50:
            raise ValueError("Nazwa talii nie może być dłuższa niż 50 znaków")

        # Check for duplicate name
        existing = self.deck_repository.get_by_name(name, user_id)
        if existing:
            raise IntegrityError("Talia o tej nazwie już istnieje")

        # Create and persist the deck
        deck = Deck(
            id=None,  # Will be set by repository
            user_id=user_id,
            name=name,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        try:
            created_deck = self.deck_repository.add(deck)
            self.logger.info(f"Created deck '{name}' for user {user_id}")
            return created_deck
        except Exception as e:
            self.logger.error(f"Failed to create deck '{name}' for user {user_id}: {str(e)}")
            raise

    def get_deck(self, deck_id: int, user_id: int) -> Optional[Deck]:
        """
        Retrieves a deck by ID for the given user.
        
        Args:
            deck_id: The ID of the deck to retrieve
            user_id: The ID of the user who owns the deck
            
        Returns:
            The Deck if found and owned by the user, None otherwise
        """
        try:
            deck = self.deck_repository.get_by_id(deck_id, user_id)
            if deck:
                self.logger.debug(f"Retrieved deck {deck_id} for user {user_id}")
            else:
                self.logger.debug(f"Deck {deck_id} not found for user {user_id}")
            return deck
        except Exception as e:
            self.logger.error(f"Failed to retrieve deck {deck_id} for user {user_id}: {str(e)}")
            raise

    def list_decks(self, user_id: int) -> List[Deck]:
        """
        Lists all decks for the given user.
        
        Args:
            user_id: The ID of the user whose decks to list
            
        Returns:
            List of Deck objects owned by the user, ordered by name
        """
        try:
            decks = self.deck_repository.list_all(user_id)
            self.logger.debug(f"Listed {len(decks)} decks for user {user_id}")
            return decks
        except Exception as e:
            self.logger.error(f"Failed to list decks for user {user_id}: {str(e)}")
            raise

    def delete_deck(self, deck_id: int, user_id: int) -> None:
        """
        Deletes a deck and all its flashcards.
        
        Args:
            deck_id: The ID of the deck to delete
            user_id: The ID of the user who owns the deck
            
        Raises:
            ValueError: If the deck doesn't exist or doesn't belong to the user
        """
        # Verify deck exists and belongs to user
        deck = self.deck_repository.get_by_id(deck_id, user_id)
        if not deck:
            raise ValueError("Talia nie istnieje lub nie należy do tego użytkownika")

        try:
            self.deck_repository.delete(deck_id, user_id)
            self.logger.info(f"Deleted deck {deck_id} for user {user_id}")
        except Exception as e:
            self.logger.error(f"Failed to delete deck {deck_id} for user {user_id}: {str(e)}")
            raise

    def rename_deck(self, deck_id: int, user_id: int, new_name: str) -> None:
        """
        Renames an existing deck.
        
        Args:
            deck_id: The ID of the deck to rename
            user_id: The ID of the user who owns the deck
            new_name: The new name for the deck (max 50 chars)
            
        Raises:
            ValueError: If new_name is empty or too long, or if deck doesn't exist
            IntegrityError: If another deck with new_name exists for the user
        """
        # Validate new name
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Nazwa talii nie może być pusta")
        if len(new_name) > 50:
            raise ValueError("Nazwa talii nie może być dłuższa niż 50 znaków")

        # Get existing deck
        deck = self.deck_repository.get_by_id(deck_id, user_id)
        if not deck:
            raise ValueError("Talia nie istnieje lub nie należy do tego użytkownika")

        # Check if new name would create a duplicate
        if new_name != deck.name:
            existing = self.deck_repository.get_by_name(new_name, user_id)
            if existing:
                raise IntegrityError("Talia o tej nazwie już istnieje")

        try:
            # Update the deck
            deck.name = new_name
            deck.updated_at = datetime.now()
            self.deck_repository.update(deck)
            self.logger.info(f"Renamed deck {deck_id} to '{new_name}' for user {user_id}")
        except Exception as e:
            self.logger.error(f"Failed to rename deck {deck_id} for user {user_id}: {str(e)}")
            raise
