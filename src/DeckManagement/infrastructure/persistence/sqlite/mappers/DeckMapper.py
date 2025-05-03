from datetime import datetime
from typing import Tuple, Optional

from DeckManagement.domain.models.Deck import Deck


class DeckMapper:
    @staticmethod
    def from_row(row: Optional[Tuple[int, int, str, str, str]]) -> Deck:
        """
        Maps a database row to a Deck domain model.

        Args:
            row: Tuple containing (id, user_id, name, created_at, updated_at)
                created_at and updated_at are ISO format datetime strings

        Returns:
            Deck domain model

        Raises:
            ValueError: If row is None or datetime parsing fails
        """
        if row is None:
            raise ValueError("Cannot map None to Deck")

        id, user_id, name, created_at_str, updated_at_str = row

        try:
            created_at = datetime.fromisoformat(created_at_str)
            updated_at = datetime.fromisoformat(updated_at_str)
        except ValueError as e:
            raise ValueError(f"Failed to parse timestamps from database: {e}")

        return Deck(id=id, user_id=user_id, name=name, created_at=created_at, updated_at=updated_at)
