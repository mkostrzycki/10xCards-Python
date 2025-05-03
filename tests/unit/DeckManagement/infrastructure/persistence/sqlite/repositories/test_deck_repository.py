import sqlite3
import pytest

from src.DeckManagement.domain.models.Deck import Deck
from src.DeckManagement.infrastructure.persistence.sqlite.repositories.DeckRepositoryImpl import (
    DeckRepositoryImpl,
)


class MockDbProvider:
    """Test database provider that uses an in-memory SQLite database."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def get_connection(self) -> sqlite3.Connection:
        return self.connection


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
def db_provider(db_connection):
    return MockDbProvider(db_connection)


@pytest.fixture
def repository(db_provider):
    return DeckRepositoryImpl(db_provider)


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


def test_add_deck_duplicate_name(repository, sample_deck):
    repository.add(sample_deck)
    duplicate = Deck(id=None, user_id=1, name="Test Deck", created_at=None, updated_at=None)
    with pytest.raises(sqlite3.IntegrityError):
        repository.add(duplicate)


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


def test_list_all_decks(repository):
    decks = [
        Deck(id=None, user_id=1, name="A", created_at=None, updated_at=None),
        Deck(id=None, user_id=1, name="B", created_at=None, updated_at=None),
        Deck(id=None, user_id=1, name="C", created_at=None, updated_at=None),
    ]
    for deck in decks:
        repository.add(deck)
    result = repository.list_all(1)
    assert len(result) == 3
    # Should be sorted by name
    assert [d.name for d in result] == ["A", "B", "C"]


def test_list_all_decks_empty(repository):
    assert repository.list_all(1) == []


def test_update_deck(repository, sample_deck):
    deck = repository.add(sample_deck)
    deck.name = "Updated Name"
    repository.update(deck)
    updated = repository.get_by_id(deck.id, deck.user_id)
    assert updated.name == "Updated Name"


def test_update_deck_duplicate_name(repository):
    repository.add(Deck(id=None, user_id=1, name="First", created_at=None, updated_at=None))
    deck2 = repository.add(Deck(id=None, user_id=1, name="Second", created_at=None, updated_at=None))
    deck2.name = "First"  # Try to update to a name that already exists
    with pytest.raises(sqlite3.IntegrityError):
        repository.update(deck2)


def test_delete_deck(repository, sample_deck):
    deck = repository.add(sample_deck)
    repository.delete(deck.id, deck.user_id)
    assert repository.get_by_id(deck.id, deck.user_id) is None


def test_isolation_between_users(repository):
    deck1 = repository.add(Deck(id=None, user_id=1, name="A", created_at=None, updated_at=None))
    deck2 = repository.add(Deck(id=None, user_id=2, name="B", created_at=None, updated_at=None))
    assert repository.get_by_id(deck1.id, 2) is None
    assert repository.get_by_id(deck2.id, 1) is None
