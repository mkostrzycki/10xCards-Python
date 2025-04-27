from datetime import datetime
from typing import Optional


class Flashcard:
    """
    Domain model representing a single flashcard belonging to a user's deck.
    Holds front/back text, FSRS state, source info, and timestamps.
    """

    def __init__(
        self,
        id: Optional[int],
        deck_id: int,
        front_text: str,
        back_text: str,
        fsrs_state: Optional[str],  # JSON blob or None
        source: str,  # 'manual' | 'ai-generated' | 'ai-edited'
        ai_model_name: Optional[str],
        created_at: datetime,
        updated_at: datetime,
    ):
        self.id = id
        self.deck_id = deck_id
        self.front_text = front_text
        self.back_text = back_text
        self.fsrs_state = fsrs_state
        self.source = source
        self.ai_model_name = ai_model_name
        self.created_at = created_at
        self.updated_at = updated_at
