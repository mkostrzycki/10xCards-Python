from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.user import User


class IUserRepository(ABC):
    """
    Interface defining operations for persisting and retrieving User entities.
    Implementations should handle all database interactions and data mapping.
    """

    @abstractmethod
    def add(self, user: User) -> User:
        """
        Adds a new user to the repository.

        Args:
            user: User entity to persist (without id)

        Returns:
            User entity with assigned id and timestamps

        Raises:
            UsernameAlreadyExistsError: If username is not unique
            RepositoryError: If database operation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user by their ID.

        Args:
            user_id: The unique identifier of the user

        Returns:
            User entity if found, None otherwise

        Raises:
            RepositoryError: If database operation fails
        """
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieves a user by their username.

        Args:
            username: The unique username to search for

        Returns:
            User entity if found, None otherwise

        Raises:
            RepositoryError: If database operation fails
        """
        pass

    @abstractmethod
    def list_all(self) -> List[User]:
        """
        Retrieves all users from the repository.

        Returns:
            List of all User entities

        Raises:
            RepositoryError: If database operation fails
        """
        pass

    @abstractmethod
    def update(self, user: User) -> None:
        """
        Updates an existing user's data.

        Args:
            user: User entity with updated data (must have id)

        Raises:
            UserNotFoundError: If user with given id doesn't exist
            UsernameAlreadyExistsError: If new username is not unique
            RepositoryError: If database operation fails
        """
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        """
        Deletes a user by their ID.

        Args:
            user_id: The unique identifier of the user to delete

        Raises:
            UserNotFoundError: If user with given id doesn't exist
            RepositoryError: If database operation fails
        """
        pass
