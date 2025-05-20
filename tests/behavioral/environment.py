import sys
import os
from unittest.mock import MagicMock, patch
import logging

# Determine the project root directory.
# __file__ in environment.py is tests/behavioral/environment.py
# Project root is two levels up from the directory of this file.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Determine the path to the 'src' directory
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

# Add the 'src' directory to sys.path if it's not already there.
# This allows behave steps to import modules from 'src' as top-level (e.g., 'from Shared...').
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Konfiguracja loggera
logger = logging.getLogger(__name__)

# Patchowanie modułów tkinter i ttkbootstrap
# Zamiast mockować całe moduły, użyjemy patcha w testach
tkinter_patch = patch("tkinter.Misc.wait_window", lambda self, win: None)
toplevel_grab_patch = patch("tkinter.Toplevel.grab_set", lambda self: None)
toplevel_wait_patch = patch("tkinter.Toplevel.wait_window", lambda self, win: None)

# Rozpocznij wszystkie patche
tkinter_patch.start()
toplevel_grab_patch.start()
toplevel_wait_patch.start()


def before_all(context):
    """Inicjalizacja przed wszystkimi testami"""
    logger.info("Starting Behave tests with mocked UI")


def after_all(context):
    """Sprzątanie po wszystkich testach"""
    logger.info("Finished Behave tests")

    # Zatrzymaj wszystkie patche
    tkinter_patch.stop()
    toplevel_grab_patch.stop()
    toplevel_wait_patch.stop()


def before_scenario(context, scenario):
    """Inicjalizuje kontekst przed wykonaniem scenariusza."""
    # Inicjalizacja mocków dla testów zarządzania taliami
    if "Zarządzanie taliami fiszek" in scenario.feature.name:
        # Inicjalizacja serwisów
        context.session_service = MagicMock()
        context.deck_service = MagicMock()
        context.card_service = MagicMock()
        context.navigation_controller = MagicMock()

        # Utwórz mock dla widoku z poprawnym show_toast
        context.current_view = MagicMock()
        # Upewnij się, że show_toast jest osobnym MagicMock, a nie tylko metodą mocka
        context.current_view.show_toast = MagicMock()
