from src.CardManagement.domain.models.Flashcard import Flashcard
from datetime import datetime


class FlashcardMapper:
    @staticmethod
    def from_row(row: tuple) -> Flashcard:
        """
        Maps a DB row (tuple) to a Flashcard domain object.
        Assumes row order: id, deck_id, front_text, back_text, fsrs_state, source, ai_model_name, created_at, updated_at
        """
        (id, deck_id, front_text, back_text, fsrs_state, source, ai_model_name, created_at, updated_at) = row
        return Flashcard(
            id=id,
            deck_id=deck_id,
            front_text=front_text,
            back_text=back_text,
            fsrs_state=fsrs_state,
            source=source,
            ai_model_name=ai_model_name,
            created_at=datetime.fromisoformat(created_at) if isinstance(created_at, str) else created_at,
            updated_at=datetime.fromisoformat(updated_at) if isinstance(updated_at, str) else updated_at,
        )
