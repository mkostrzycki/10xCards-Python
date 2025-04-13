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
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row

        # Create the Users table
        self.conn.executescript(
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
        return self.conn


@given("the database is empty")
def step_impl(context):
    context.db_provider = TestDbProvider()
    context.repository = UserRepositoryImpl(context.db_provider)
    # Database is already empty as it's a new in-memory database


@given('there is a user with username "{username}"')
def step_impl(context, username):
    user = User(id=None, username=username, hashed_password="dummyhash", hashed_api_key="dummykey")
    context.current_user = context.repository.add(user)


@when("I create a user profile with")
def step_impl(context):
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
def step_impl(context):
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
def step_impl(context):
    try:
        context.repository.delete(context.current_user.id)
        context.error = None
    except Exception as e:
        context.error = e


@then("the user profile should be created successfully")
def step_impl(context):
    assert_that(context.error, is_(none()))
    assert_that(context.current_user.id, is_not(none()))


@then("I should get a username already exists error")
def step_impl(context):
    assert_that(context.error, instance_of(UsernameAlreadyExistsError))


@then("the user profile should be updated successfully")
def step_impl(context):
    assert_that(context.error, is_(none()))


@then("the user profile should be deleted successfully")
def step_impl(context):
    assert_that(context.error, is_(none()))


@then('I should be able to find the user by username "{username}"')
def step_impl(context, username):
    user = context.repository.get_by_username(username)
    assert_that(user, is_not(none()))
    assert_that(user.username, is_(username))


@then('I should not be able to find the user by username "{username}"')
def step_impl(context, username):
    user = context.repository.get_by_username(username)
    assert_that(user, is_(none()))
