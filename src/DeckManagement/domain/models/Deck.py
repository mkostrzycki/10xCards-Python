from datetime import datetime
from typing import Optional


class Deck:
    def __init__(
        self, id: Optional[int], user_id: int, name: str, created_at: Optional[datetime], updated_at: Optional[datetime]
    ):
        self.id = id
        self.user_id = user_id
        self.name = name  # max 50 chars
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def create_new(cls, user_id: int, name: str) -> "Deck":
        """
        Factory method for creating a new Deck instance (id and timestamps are None until persisted).
        Business-level validation (length, non-empty) should be performed in the application layer.
        """
        return cls(id=None, user_id=user_id, name=name.strip(), created_at=None, updated_at=None)
