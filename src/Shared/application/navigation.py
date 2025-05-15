"""Navigation related interfaces and classes."""

from typing import Protocol, Type, Any


class NavigationControllerProtocol(Protocol):
    """Protocol defining the navigation interface required by views."""

    def navigate(self, path: str) -> None:
        """Navigate to a specified path.

        Args:
            path: The path to navigate to.
        """
        ...

    def navigate_to_view(self, view_class: Type, **kwargs: Any) -> None:
        """Navigate to a view of specified class, passing keyword arguments.

        Args:
            view_class: The class of the view to navigate to
            kwargs: Arguments to pass to the view constructor
        """
        ...
