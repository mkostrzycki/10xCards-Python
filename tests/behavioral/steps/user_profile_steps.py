import sqlite3
from behave import given, when, then
from hamcrest import assert_that, is_, is_not, none, instance_of

from src.UserProfile.domain.models.user import User
from src.UserProfile.domain.repositories.exceptions import UsernameAlreadyExistsError
from src.UserProfile.infrastructure.persistence.sqlite.repositories.UserRepositoryImpl import (
    UserRepositoryImpl,
)


class TestDbProvider:
    """Test database provider that uses an in-memory SQLite database."""

    def __init__(self):
        self._conn: sqlite3.Connection = sqlite3.connect(":memory:")
        self._conn.row_factory = sqlite3.Row

        # Create the Users table
        self._conn.executescript(
            """
            CREATE TABLE Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                hashed_password TEXT,
                hashed_api_key TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TRIGGER update_users_updated_at
            AFTER UPDATE ON Users
            FOR EACH ROW
            BEGIN
                UPDATE Users SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
            END;
        """
        )

    def get_connection(self) -> sqlite3.Connection:
        return self._conn


@given("the database is empty")
def setup_empty_database(context):
    context.db_provider = TestDbProvider()
    context.repository = UserRepositoryImpl(context.db_provider)
    # Database is already empty as it's a new in-memory database


@given('there is a user with username "{username}"')
def create_initial_user(context, username):
    user = User(id=None, username=username, hashed_password="dummyhash", hashed_api_key="dummykey")
    context.current_user = context.repository.add(user)


@when("I create a user profile with")
def create_user_profile(context):
    # Get data from the first row of the table (excluding header)
    row = context.table[0]
    user = User(
        id=None,
        username=row["username"],
        hashed_password=row["password"],  # In real app this would be hashed
        hashed_api_key=row["api_key"],  # In real app this would be hashed
    )
    try:
        context.current_user = context.repository.add(user)
        context.error = None
    except Exception as e:
        context.error = e


@when("I update the user profile with")
def update_user_profile(context):
    row = context.table[0]
    user = User(
        id=context.current_user.id,
        username=row["username"],
        hashed_password=row["password"],  # In real app this would be hashed
        hashed_api_key=row["api_key"],  # In real app this would be hashed
    )
    try:
        context.repository.update(user)
        context.error = None
    except Exception as e:
        context.error = e


@when("I delete the user profile")
def delete_user_profile(context):
    try:
        context.repository.delete(context.current_user.id)
        context.error = None
    except Exception as e:
        context.error = e


@then("the user profile should be created successfully")
def verify_user_created(context):
    assert_that(context.error, is_(none()))
    assert_that(context.current_user.id, is_not(none()))


@then("I should get a username already exists error")
def verify_duplicate_username_error(context):
    assert_that(context.error, instance_of(UsernameAlreadyExistsError))


@then("the user profile should be updated successfully")
def verify_user_updated(context):
    assert_that(context.error, is_(none()))


@then("the user profile should be deleted successfully")
def verify_user_deleted(context):
    assert_that(context.error, is_(none()))


@then('I should be able to find the user by username "{username}"')
def verify_user_exists(context, username):
    user = context.repository.get_by_username(username)
    assert_that(user, is_not(none()))
    assert_that(user.username, is_(username))


@then('I should not be able to find the user by username "{username}"')
def verify_user_not_exists(context, username):
    user = context.repository.get_by_username(username)
    assert_that(user, is_(none()))
