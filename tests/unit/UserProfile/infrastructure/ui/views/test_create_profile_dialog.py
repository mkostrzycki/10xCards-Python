import pytest
import tkinter as tk
from unittest.mock import MagicMock
from src.UserProfile.infrastructure.ui.views.create_profile_dialog import CreateProfileDialog


@pytest.fixture
def mock_parent(mocker):
    # Mock a parent widget (e.g., root window)
    return mocker.Mock(spec=tk.Tk)


@pytest.fixture
def mock_on_create(mocker):
    return mocker.Mock()


@pytest.fixture
def dialog(mocker, mock_parent, mock_on_create):
    # Patch Toplevel so no real window is created
    mocker.patch("tkinter.Toplevel.__init__", return_value=None)
    mocker.patch("tkinter.Toplevel.destroy", return_value=None)
    # Patch ttkbootstrap widgets
    mocker.patch("ttkbootstrap.Frame", return_value=MagicMock())
    mocker.patch("ttkbootstrap.Label", return_value=MagicMock())
    mocker.patch("ttkbootstrap.Entry", return_value=MagicMock())
    mocker.patch("ttkbootstrap.Button", return_value=MagicMock())
    # Patch geometry and focus_set
    mocker.patch("tkinter.Toplevel.geometry", return_value=None)
    mocker.patch("tkinter.Toplevel.title", return_value=None)
    mocker.patch("tkinter.Toplevel.transient", return_value=None)
    mocker.patch("tkinter.Toplevel.grab_set", return_value=None)
    mocker.patch("tkinter.Toplevel.protocol", return_value=None)
    mocker.patch("tkinter.Toplevel.bind", return_value=None)
    mocker.patch("tkinter.Toplevel.winfo_screenwidth", return_value=800)
    mocker.patch("tkinter.Toplevel.winfo_screenheight", return_value=600)
    # Patch focus_set for Entry
    entry_mock = MagicMock()
    mocker.patch("ttkbootstrap.Entry", return_value=entry_mock)
    entry_mock.focus_set = MagicMock()
    # Patch error label
    error_label_mock = MagicMock()
    mocker.patch("ttkbootstrap.Label", return_value=error_label_mock)
    d = CreateProfileDialog(mock_parent, mock_on_create)
    d._username_input = entry_mock
    d._error_label = error_label_mock
    return d


def test_dialog_initialization(dialog, mock_parent, mock_on_create):
    # Check that dialog is modal and title is set
    dialog.title.assert_called_with("Nowy profil")
    dialog.transient.assert_called_with(mock_parent)
    dialog.grab_set.assert_called_once()
    dialog._username_input.focus_set.assert_called_once()


def test_validate_input_empty(dialog):
    dialog._username_input.get.return_value = "   "
    assert not dialog._validate_input()
    assert dialog._state.error_message is not None
    dialog._error_label.configure.assert_called_with(text="Nazwa profilu nie może być pusta.")


def test_validate_input_too_long(dialog):
    dialog._username_input.get.return_value = "x" * 31
    assert not dialog._validate_input()
    assert dialog._state.error_message is not None
    dialog._error_label.configure.assert_called_with(text="Nazwa profilu nie może być dłuższa niż 30 znaków.")


def test_validate_input_valid(dialog):
    dialog._username_input.get.return_value = "validuser"
    assert dialog._validate_input() is True
    assert dialog._state.error_message is None


def test_show_error(dialog):
    dialog._show_error("Oops!")
    assert dialog._state.error_message == "Oops!"
    dialog._error_label.configure.assert_called_with(text="Oops!")


def test_clear_error(dialog):
    dialog._state.error_message = "Some error"
    dialog._clear_error()
    assert dialog._state.error_message is None
    dialog._error_label.configure.assert_called_with(text="")


def test_on_create_clicked_valid(dialog, mock_on_create):
    dialog._username_input.get.return_value = "validuser"
    dialog._validate_input = MagicMock(return_value=True)
    dialog._state.username_input = "validuser"
    dialog.destroy = MagicMock()
    dialog._on_create_clicked()
    mock_on_create.assert_called_once_with("validuser")
    dialog.destroy.assert_called_once()


def test_on_create_clicked_invalid(dialog, mock_on_create):
    dialog._validate_input = MagicMock(return_value=False)
    dialog.destroy = MagicMock()
    dialog._on_create_clicked()
    mock_on_create.assert_not_called()
    dialog.destroy.assert_not_called()


def test_on_cancel(dialog):
    dialog.destroy = MagicMock()
    dialog._on_cancel()
    dialog.destroy.assert_called_once()
