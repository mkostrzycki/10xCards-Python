import logging
from ttkbootstrap.toast import ToastNotification

# Konfiguracja loggera
logger = logging.getLogger(__name__)


class ToastContainer:
    """Wrapper for ttkbootstrap ToastNotification."""

    def __init__(self, parent):
        """Initialize the toast container.

        Args:
            parent: Parent widget
        """
        logger.info("Initializing ToastContainer")
        # Zachowujemy referencję do rodzica dla debugowania
        self.parent = parent

    def show_toast(self, title: str, message: str) -> None:
        """Show a toast notification.

        Args:
            title: Toast title
            message: Toast message
        """
        logger.info(f"Showing toast: {title} - {message}")

        # Najprostsza możliwa wersja bez dodatkowych parametrów
        toast = ToastNotification(
            title=title, message=message, duration=3000, position=(0, 50, "ne")  # Prawy górny róg
        )

        # Wyświetlenie toastu
        toast.show_toast()
        logger.info(f"Toast displayed: {title}")
