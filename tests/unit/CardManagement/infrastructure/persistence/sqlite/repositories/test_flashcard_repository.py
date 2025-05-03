import sqlite3
import pytest

from src.CardManagement.domain.models.Flashcard import Flashcard
from src.CardManagement.infrastructure.persistence.sqlite.repositories.FlashcardRepositoryImpl import (
    FlashcardRepositoryImpl,
)


class MockDbProvider:
    """Test database provider that uses an in-memory SQLite database."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def get_connection(self) -> sqlite3.Connection:
        return self.connection


@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute(
        """
        CREATE TABLE Flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            front_text TEXT NOT NULL,
            back_text TEXT NOT NULL,
            fsrs_state TEXT,
            source TEXT NOT NULL,
            ai_model_name TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    yield conn
    conn.close()


@pytest.fixture
def db_provider(db_connection):
    return MockDbProvider(db_connection)


@pytest.fixture
def repository(db_provider):
    return FlashcardRepositoryImpl(db_provider)


@pytest.fixture
def sample_flashcard():
    return Flashcard(
        id=None,
        deck_id=1,
        front_text="Front Text",
        back_text="Back Text",
        fsrs_state=None,
        source="manual",
        ai_model_name=None,
        created_at=None,
        updated_at=None,
    )


def test_add_flashcard(repository, sample_flashcard):
    added = repository.add(sample_flashcard)
    assert added.id is not None
    assert added.deck_id == sample_flashcard.deck_id
    assert added.front_text == sample_flashcard.front_text
    assert added.back_text == sample_flashcard.back_text
    assert added.source == sample_flashcard.source
    assert added.created_at is not None
    assert added.updated_at is not None


def test_get_by_id(repository, sample_flashcard):
    added = repository.add(sample_flashcard)
    retrieved = repository.get_by_id(added.id)
    assert retrieved is not None
    assert retrieved.id == added.id
    assert retrieved.front_text == added.front_text
    assert retrieved.back_text == added.back_text


def test_get_by_id_not_found(repository):
    retrieved = repository.get_by_id(999)
    assert retrieved is None


def test_list_by_deck_id(repository, sample_flashcard):
    repository.add(sample_flashcard)
    second_card = Flashcard(
        id=None,
        deck_id=sample_flashcard.deck_id,
        front_text="Second Front",
        back_text="Second Back",
        fsrs_state=None,
        source="manual",
        ai_model_name=None,
        created_at=None,
        updated_at=None,
    )
    repository.add(second_card)

    # Add a card to a different deck
    different_deck_card = Flashcard(
        id=None,
        deck_id=2,
        front_text="Different Deck",
        back_text="Different Deck Back",
        fsrs_state=None,
        source="manual",
        ai_model_name=None,
        created_at=None,
        updated_at=None,
    )
    repository.add(different_deck_card)

    cards = repository.list_by_deck_id(sample_flashcard.deck_id)
    assert len(cards) == 2
    assert all(card.deck_id == sample_flashcard.deck_id for card in cards)


def test_update_flashcard(repository, sample_flashcard):
    added = repository.add(sample_flashcard)
    added.front_text = "Updated Front"
    added.back_text = "Updated Back"
    added.fsrs_state = '{"some": "state"}'

    repository.update(added)

    updated = repository.get_by_id(added.id)
    assert updated is not None
    assert updated.front_text == "Updated Front"
    assert updated.back_text == "Updated Back"
    assert updated.fsrs_state == '{"some": "state"}'


def test_delete_flashcard(repository, sample_flashcard):
    added = repository.add(sample_flashcard)
    repository.delete(added.id)

    deleted = repository.get_by_id(added.id)
    assert deleted is None


def test_get_fsrs_card_data_for_deck(repository, sample_flashcard):
    sample_flashcard.fsrs_state = '{"some": "state"}'
    added = repository.add(sample_flashcard)

    data = repository.get_fsrs_card_data_for_deck(added.deck_id)
    assert len(data) == 1
    assert data[0][0] == added.id
    assert data[0][1] == added.fsrs_state
