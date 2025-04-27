from DeckManagement.domain.models.Deck import Deck


class DeckMapper:
    @staticmethod
    def from_row(row: tuple) -> Deck:
        id, user_id, name, created_at, updated_at = row
        return Deck(id=id, user_id=user_id, name=name, created_at=created_at, updated_at=updated_at)
