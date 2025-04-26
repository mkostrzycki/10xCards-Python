import pytest

from src.UserProfile.infrastructure.ui.views.create_profile_dialog import CreateProfileDialog


@pytest.fixture
def mock_parent(mocker):
    return mocker.patch("tkinter.Toplevel", autospec=True)


@pytest.fixture
def mock_on_create(mocker):
    return mocker.Mock()


@pytest.fixture
def dialog(mocker, mock_parent, mock_on_create):
    # Mock the necessary Tkinter widgets
    mocker.patch("tkinter.ttk.Entry", autospec=True)
    mocker.patch("tkinter.ttk.Label", autospec=True)
    mocker.patch("tkinter.ttk.Frame", autospec=True)
    mocker.patch("tkinter.ttk.Button", autospec=True)

    dialog = CreateProfileDialog(mock_parent, mock_on_create)
    # Mock the Entry widget's get() method
    dialog._username_input = mocker.Mock()
    # Mock the Label widget's configure method
    dialog._error_label = mocker.Mock()
    return dialog


def test_validate_input_accepts_valid_username(dialog, mock_on_create):
    # Arrange
    username = "validuser"
    dialog._username_input.get.return_value = username

    # Act
    result = dialog._validate_input()

    # Assert
    assert result is True
    assert dialog._state.username_input == username
    assert dialog._state.error_message is None
    dialog._error_label.configure.assert_not_called()


def test_validate_input_rejects_empty_username(dialog, mock_on_create):
    # Arrange
    dialog._username_input.get.return_value = "   "  # Spaces only

    # Act
    result = dialog._validate_input()

    # Assert
    assert result is False
    assert dialog._state.username_input == ""
    assert dialog._state.error_message == "Nazwa profilu nie może być pusta."
    dialog._error_label.configure.assert_called_once_with(text="Nazwa profilu nie może być pusta.")


def test_validate_input_rejects_too_long_username(dialog, mock_on_create):
    # Arrange
    username = "a" * 31  # 31 characters
    dialog._username_input.get.return_value = username

    # Act
    result = dialog._validate_input()

    # Assert
    assert result is False
    assert dialog._state.username_input == username
    assert dialog._state.error_message == "Nazwa profilu nie może być dłuższa niż 30 znaków."
    dialog._error_label.configure.assert_called_once_with(text="Nazwa profilu nie może być dłuższa niż 30 znaków.")


def test_validate_input_accepts_max_length_username(dialog, mock_on_create):
    # Arrange
    username = "a" * 30  # Exactly 30 characters
    dialog._username_input.get.return_value = username

    # Act
    result = dialog._validate_input()

    # Assert
    assert result is True
    assert dialog._state.username_input == username
    assert dialog._state.error_message is None
    dialog._error_label.configure.assert_not_called()


def test_show_error_updates_state_and_label(dialog):
    # Arrange
    error_message = "Test error message"

    # Act
    dialog._show_error(error_message)

    # Assert
    assert dialog._state.error_message == error_message
    dialog._error_label.configure.assert_called_once_with(text=error_message)


def test_clear_error_clears_state_and_label(dialog):
    # Arrange
    dialog._state.error_message = "Previous error"

    # Act
    dialog._clear_error()

    # Assert
    assert dialog._state.error_message is None
    dialog._error_label.configure.assert_called_once_with(text="")


def test_on_create_clicked_validates_before_calling_callback(dialog, mock_on_create):
    # Arrange
    username = "validuser"
    dialog._username_input.get.return_value = username

    # Act
    dialog._on_create_clicked()

    # Assert
    mock_on_create.assert_called_once_with(username)


def test_on_create_clicked_does_not_call_callback_on_invalid_input(dialog, mock_on_create):
    # Arrange
    dialog._username_input.get.return_value = ""  # Invalid input

    # Act
    dialog._on_create_clicked()

    # Assert
    mock_on_create.assert_not_called()


@pytest.mark.parametrize(
    "username,expected_valid",
    [
        ("normaluser", True),
        ("", False),
        ("   ", False),
        ("a" * 30, True),
        ("a" * 31, False),
        ("user123", True),
        ("user-name", True),
        ("user_name", True),
    ],
)
def test_validate_input_parameterized(dialog, username, expected_valid):
    # Arrange
    dialog._username_input.get.return_value = username

    # Act
    result = dialog._validate_input()

    # Assert
    assert result is expected_valid
