import sqlite3
from typing import List, Optional
from DeckManagement.domain.models.Deck import Deck
from DeckManagement.domain.repositories.IDeckRepository import IDeckRepository
from DeckManagement.infrastructure.persistence.sqlite.mappers.DeckMapper import DeckMapper


class DeckRepositoryImpl(IDeckRepository):
    """
    SQLite implementation of IDeckRepository.
    All SQL is parameterized and filtered by user_id to ensure user data isolation.
    Propagates sqlite3.IntegrityError and other DB exceptions to the application layer.
    """

    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        # Enforce foreign key constraints for every connection (critical for ON DELETE CASCADE)
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def add(self, deck: Deck) -> Deck:
        """
        Adds a new deck for the given user. Returns the deck with assigned ID and timestamps.
        Raises sqlite3.IntegrityError if the name is not unique for the user.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO Decks (user_id, name) VALUES (?, ?)", (deck.user_id, deck.name))
            deck.id = cursor.lastrowid
            deck.created_at, deck.updated_at = self._fetch_timestamps(deck.id)
            self.conn.commit()
            return deck
        except sqlite3.IntegrityError:
            self.conn.rollback()
            # Propagate to application layer for user feedback/logging
            raise

    def get_by_id(self, deck_id: int, user_id: int) -> Optional[Deck]:
        """
        Fetches a deck by its ID for the given user. Returns None if not found.
        Ensures user_id filter for row-level security.
        """
        row = self.conn.execute(
            "SELECT id, user_id, name, created_at, updated_at FROM Decks WHERE id = ? AND user_id = ?",
            (deck_id, user_id),
        ).fetchone()
        return DeckMapper.from_row(row) if row else None

    def get_by_name(self, name: str, user_id: int) -> Optional[Deck]:
        """
        Fetches a deck by its name for the given user. Returns None if not found.
        Ensures user_id filter for row-level security.
        """
        row = self.conn.execute(
            "SELECT id, user_id, name, created_at, updated_at FROM Decks WHERE name = ? AND user_id = ?",
            (name, user_id),
        ).fetchone()
        return DeckMapper.from_row(row) if row else None

    def list_all(self, user_id: int) -> List[Deck]:
        """
        Returns all decks for the given user, ordered by name.
        Ensures user_id filter for row-level security.
        """
        rows = self.conn.execute(
            "SELECT id, user_id, name, created_at, updated_at FROM Decks WHERE user_id = ? ORDER BY name", (user_id,)
        ).fetchall()
        return [DeckMapper.from_row(r) for r in rows]

    def update(self, deck: Deck) -> None:
        """
        Updates an existing deck's name for the given user.
        Raises sqlite3.IntegrityError if the new name is not unique for the user.
        """
        try:
            self.conn.execute(
                "UPDATE Decks SET name = ? WHERE id = ? AND user_id = ?", (deck.name, deck.id, deck.user_id)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise

    def delete(self, deck_id: int, user_id: int) -> None:
        """
        Deletes a deck by ID for the given user.
        """
        self.conn.execute("DELETE FROM Decks WHERE id = ? AND user_id = ?", (deck_id, user_id))
        self.conn.commit()

    def _fetch_timestamps(self, deck_id: Optional[int]):
        # Helper to fetch created_at and updated_at after insert
        if deck_id is None:
            raise ValueError("deck_id cannot be None when fetching timestamps")
        row = self.conn.execute("SELECT created_at, updated_at FROM Decks WHERE id = ?", (int(deck_id),)).fetchone()
        return row[0], row[1]  # type: ignore
