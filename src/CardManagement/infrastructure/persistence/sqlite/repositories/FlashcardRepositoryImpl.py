import sqlite3
from typing import List, Optional, Tuple
from CardManagement.domain.models.Flashcard import Flashcard
from CardManagement.domain.repositories.IFlashcardRepository import IFlashcardRepository
from CardManagement.infrastructure.persistence.sqlite.mappers.FlashcardMapper import FlashcardMapper


class FlashcardRepositoryImpl(IFlashcardRepository):
    """
    SQLite implementation of IFlashcardRepository.
    All SQL is parameterized. Propagates sqlite3.IntegrityError and other DB exceptions to the application layer.
    """

    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def add(self, flashcard: Flashcard) -> Flashcard:
        """Adds a new flashcard and returns the instance with assigned 'id' and timestamps."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO Flashcards (deck_id, front_text, back_text, fsrs_state, source, ai_model_name)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    flashcard.deck_id,
                    flashcard.front_text,
                    flashcard.back_text,
                    flashcard.fsrs_state,
                    flashcard.source,
                    flashcard.ai_model_name,
                ),
            )
            flashcard_id = cursor.lastrowid
            assert flashcard_id is not None, "flashcard_id should never be None after insert!"
            self.conn.commit()
            result = self.get_by_id(flashcard_id)
            if result is None:
                raise RuntimeError(f"Failed to fetch Flashcard after insert (id={flashcard_id})")
            return result
        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise

    def get_by_id(self, flashcard_id: int) -> Optional[Flashcard]:
        """Retrieves a flashcard by its ID. Returns None if not found."""
        row = self.conn.execute(
            "SELECT id, deck_id, front_text, back_text, fsrs_state, source, ai_model_name, created_at, updated_at FROM Flashcards WHERE id = ?",
            (flashcard_id,),
        ).fetchone()
        return FlashcardMapper.from_row(row) if row else None

    def list_by_deck_id(self, deck_id: int) -> List[Flashcard]:
        """Returns a list of flashcards belonging to the given deck."""
        rows = self.conn.execute(
            "SELECT id, deck_id, front_text, back_text, fsrs_state, source, ai_model_name, created_at, updated_at FROM Flashcards WHERE deck_id = ? ORDER BY created_at ASC",
            (deck_id,),
        ).fetchall()
        return [FlashcardMapper.from_row(row) for row in rows]

    def update(self, flashcard: Flashcard) -> None:
        """Updates an existing flashcard (content or FSRS state)."""
        try:
            self.conn.execute(
                """
                UPDATE Flashcards
                SET front_text = ?, back_text = ?, fsrs_state = ?, source = ?, ai_model_name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    flashcard.front_text,
                    flashcard.back_text,
                    flashcard.fsrs_state,
                    flashcard.source,
                    flashcard.ai_model_name,
                    flashcard.id,
                ),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise

    def delete(self, flashcard_id: int) -> None:
        """Deletes a flashcard by its ID."""
        self.conn.execute("DELETE FROM Flashcards WHERE id = ?", (flashcard_id,))
        self.conn.commit()

    def get_fsrs_card_data_for_deck(self, deck_id: int) -> List[Tuple[int, Optional[str]]]:
        """Retrieves tuples (flashcard_id, fsrs_state) for all flashcards in the deck."""
        rows = self.conn.execute("SELECT id, fsrs_state FROM Flashcards WHERE deck_id = ?", (deck_id,)).fetchall()
        return [(row[0], row[1]) for row in rows]
