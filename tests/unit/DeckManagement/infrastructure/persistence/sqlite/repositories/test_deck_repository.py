import sqlite3
import pytest
from src.DeckManagement.domain.models.Deck import Deck
from src.DeckManagement.infrastructure.persistence.sqlite.repositories.DeckRepositoryImpl import DeckRepositoryImpl


@pytest.fixture
def db_connection():
    # In-memory SQLite DB for isolation
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute(
        """
        CREATE TABLE Decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, name)
        );
    """
    )
    yield conn
    conn.close()


@pytest.fixture
def repository(db_connection):
    return DeckRepositoryImpl(db_connection)


@pytest.fixture
def sample_deck():
    return Deck(id=None, user_id=1, name="Test Deck", created_at=None, updated_at=None)


def test_add_deck_success(repository, sample_deck):
    deck = repository.add(sample_deck)
    assert deck.id is not None
    assert deck.name == "Test Deck"
    assert deck.user_id == 1
    assert deck.created_at is not None
    assert deck.updated_at is not None


def test_add_duplicate_deck_name(repository, sample_deck):
    repository.add(sample_deck)
    duplicate = Deck(id=None, user_id=1, name="Test Deck", created_at=None, updated_at=None)
    with pytest.raises(sqlite3.IntegrityError):
        repository.add(duplicate)


def test_add_same_name_different_user(repository, sample_deck):
    repository.add(sample_deck)
    other_user_deck = Deck(id=None, user_id=2, name="Test Deck", created_at=None, updated_at=None)
    deck2 = repository.add(other_user_deck)
    assert deck2.id is not None
    assert deck2.user_id == 2


def test_get_by_id_found(repository, sample_deck):
    deck = repository.add(sample_deck)
    found = repository.get_by_id(deck.id, deck.user_id)
    assert found is not None
    assert found.id == deck.id
    assert found.name == deck.name


def test_get_by_id_not_found(repository):
    assert repository.get_by_id(999, 1) is None


def test_get_by_name_found(repository, sample_deck):
    deck = repository.add(sample_deck)
    found = repository.get_by_name(deck.name, deck.user_id)
    assert found is not None
    assert found.id == deck.id


def test_get_by_name_not_found(repository):
    assert repository.get_by_name("Nope", 1) is None


def test_list_all_decks(repository, sample_deck):
    repository.add(sample_deck)
    repository.add(Deck(id=None, user_id=1, name="Deck2", created_at=None, updated_at=None))
    decks = repository.list_all(1)
    assert len(decks) == 2
    names = {d.name for d in decks}
    assert "Test Deck" in names and "Deck2" in names


def test_list_all_decks_empty(repository):
    assert repository.list_all(1) == []


def test_update_deck_success(repository, sample_deck):
    deck = repository.add(sample_deck)
    deck.name = "Updated Name"
    repository.update(deck)
    updated = repository.get_by_id(deck.id, deck.user_id)
    assert updated.name == "Updated Name"


def test_update_deck_duplicate_name(repository, sample_deck):
    repository.add(sample_deck)
    deck2 = repository.add(Deck(id=None, user_id=1, name="Other", created_at=None, updated_at=None))
    deck2.name = "Test Deck"
    with pytest.raises(sqlite3.IntegrityError):
        repository.update(deck2)


def test_delete_deck_success(repository, sample_deck):
    deck = repository.add(sample_deck)
    repository.delete(deck.id, deck.user_id)
    assert repository.get_by_id(deck.id, deck.user_id) is None


def test_delete_deck_wrong_user(repository, sample_deck):
    deck = repository.add(sample_deck)
    # Attempt to delete as another user (should not delete anything, no error)
    repository.delete(deck.id, 999)
    assert repository.get_by_id(deck.id, deck.user_id) is not None


def test_isolation_between_users(repository):
    deck1 = repository.add(Deck(id=None, user_id=1, name="A", created_at=None, updated_at=None))
    deck2 = repository.add(Deck(id=None, user_id=2, name="B", created_at=None, updated_at=None))
    assert repository.get_by_id(deck1.id, 2) is None
    assert repository.get_by_id(deck2.id, 1) is None
