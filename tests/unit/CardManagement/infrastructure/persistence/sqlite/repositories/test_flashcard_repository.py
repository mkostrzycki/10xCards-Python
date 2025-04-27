import sqlite3
import pytest
from src.CardManagement.domain.models.Flashcard import Flashcard
from src.CardManagement.infrastructure.persistence.sqlite.repositories.FlashcardRepositoryImpl import (
    FlashcardRepositoryImpl,
)
from datetime import datetime


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
def repository(db_connection):
    return FlashcardRepositoryImpl(db_connection)


@pytest.fixture
def sample_flashcard():
    return Flashcard(
        id=None,
        deck_id=1,
        front_text="Front",
        back_text="Back",
        fsrs_state=None,
        source="manual",
        ai_model_name=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def test_add_flashcard_success(repository, sample_flashcard):
    card = repository.add(sample_flashcard)
    assert card.id is not None
    assert card.front_text == "Front"
    assert card.back_text == "Back"
    assert card.deck_id == 1
    assert card.created_at is not None
    assert card.updated_at is not None


def test_get_by_id_found(repository, sample_flashcard):
    card = repository.add(sample_flashcard)
    found = repository.get_by_id(card.id)
    assert found is not None
    assert found.id == card.id
    assert found.front_text == card.front_text


def test_get_by_id_not_found(repository):
    assert repository.get_by_id(999) is None


def test_list_by_deck_id(repository, sample_flashcard):
    repository.add(sample_flashcard)
    repository.add(
        Flashcard(
            id=None,
            deck_id=1,
            front_text="F2",
            back_text="B2",
            fsrs_state=None,
            source="manual",
            ai_model_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    )
    cards = repository.list_by_deck_id(1)
    assert len(cards) == 2
    fronts = {c.front_text for c in cards}
    assert "Front" in fronts and "F2" in fronts


def test_list_by_deck_id_empty(repository):
    assert repository.list_by_deck_id(42) == []


def test_update_flashcard_success(repository, sample_flashcard):
    card = repository.add(sample_flashcard)
    card.front_text = "Updated Front"
    card.back_text = "Updated Back"
    card.fsrs_state = '{"srs": 1}'
    card.source = "ai-edited"
    card.ai_model_name = "gpt-4"
    repository.update(card)
    updated = repository.get_by_id(card.id)
    assert updated.front_text == "Updated Front"
    assert updated.back_text == "Updated Back"
    assert updated.fsrs_state == '{"srs": 1}'
    assert updated.source == "ai-edited"
    assert updated.ai_model_name == "gpt-4"


def test_delete_flashcard_success(repository, sample_flashcard):
    card = repository.add(sample_flashcard)
    repository.delete(card.id)
    assert repository.get_by_id(card.id) is None


def test_delete_flashcard_not_found(repository):
    # Should not raise
    repository.delete(999)


def test_get_fsrs_card_data_for_deck(repository, sample_flashcard):
    card1 = repository.add(sample_flashcard)
    card2 = repository.add(
        Flashcard(
            id=None,
            deck_id=1,
            front_text="F2",
            back_text="B2",
            fsrs_state='{"srs":2}',
            source="manual",
            ai_model_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    )
    data = repository.get_fsrs_card_data_for_deck(1)
    assert (card1.id, card1.fsrs_state) in data
    assert (card2.id, card2.fsrs_state) in data


def test_add_flashcard_integrity_error(repository, sample_flashcard):
    # Simulate NOT NULL violation (front_text)
    bad_card = Flashcard(
        id=None,
        deck_id=1,
        front_text=None,
        back_text="Back",
        fsrs_state=None,
        source="manual",
        ai_model_name=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    with pytest.raises(sqlite3.IntegrityError):
        repository.add(bad_card)


def test_update_flashcard_integrity_error(repository, sample_flashcard):
    card = repository.add(sample_flashcard)
    card.front_text = None
    with pytest.raises(sqlite3.IntegrityError):
        repository.update(card)


def test_get_fsrs_card_data_for_deck_empty(repository):
    assert repository.get_fsrs_card_data_for_deck(123) == []
