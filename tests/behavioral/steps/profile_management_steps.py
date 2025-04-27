from behave import given, when, then
import tkinter as tk
from src.UserProfile.infrastructure.ui.views.profile_login_view import ProfileLoginView
from src.UserProfile.application.user_profile_service import UserProfileService
from src.UserProfile.infrastructure.persistence.sqlite.repositories.UserRepositoryImpl import UserRepositoryImpl
from tests.behavioral.steps.user_profile_steps import TestDbProvider  # type: ignore

# Globally disable wait_window to prevent modal dialogs from hanging tests
tk.Misc.wait_window = lambda self, win: None  # type: ignore
# Disable modal grab and wait_window for Toplevels so dialogs cannot block tests
tk.Toplevel.grab_set = lambda self: None  # type: ignore
tk.Toplevel.wait_window = lambda self, win: None  # type: ignore


@given("the application is started")
def start_application(context):
    # Initialize in-memory DB provider and services
    context.db_provider = TestDbProvider()
    repo = UserRepositoryImpl(context.db_provider)
    service = UserProfileService(repo)
    # Create root window but do not show
    context.root = tk.Tk()
    context.root.withdraw()
    # Prepare a main content frame
    context.main_frame = tk.Frame(context.root)

    # Track navigation target
    context.navigation = {}

    def toast(title, message):
        context.toast = (title, message)

    # Instantiate router and show profile list
    from src.UserProfile.infrastructure.ui.router import Router

    context.router = Router(context.root, service, context.main_frame, toast)
    context.router.show_profile_list()
    context.app = context.router._current_view
    # Disable blocking behavior for dialogs
    context.app.wait_window = lambda win: None


@given('there is a profile "{username}" without password')
def create_profile_no_password(context, username):
    repo = context.router._profile_service._user_repository
    from src.UserProfile.domain.models.user import User

    user = User(id=None, username=username, hashed_password=None, hashed_api_key=None)
    repo.add(user)
    # Refresh view and disable modal blocking
    context.router.show_profile_list()
    context.app = context.router._current_view
    context.app.wait_window = lambda win: None


@given('there is a profile "{username}" with password "{password}"')
def create_profile_with_password(context, username, password):
    import bcrypt

    repo = context.router._profile_service._user_repository
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    from src.UserProfile.domain.models.user import User

    user = User(id=None, username=username, hashed_password=hashed, hashed_api_key=None)
    repo.add(user)
    # Refresh view and disable modal blocking
    context.router.show_profile_list()
    context.app = context.router._current_view
    context.app.wait_window = lambda win: None


@when('I click the "Dodaj nowy profil" button')
def click_add_profile(context):
    # Open create-profile dialog via helper and capture the returned dialog
    context.dialog = context.app._show_create_profile_dialog()
    # Process events so the dialog UI is fully initialized
    context.root.update_idletasks()
    context.root.update()


@when('I enter "{username}" as username')
def enter_username(context, username):
    # Capture entered username for creation
    context.new_username = username


@when("I confirm creation")
def confirm_creation(context):
    # Directly invoke creation on the list view without dialog
    context.app._handle_profile_creation(context.new_username)
    # Refresh the profile list UI
    context.app._load_profiles()


@then('I should see a toast "{message}"')
def check_toast(context, message):
    assert context.toast[1] == message


@then('the profile list should include "{username}"')
def check_profile_list(context, username):
    items = [context.app._profile_list.item(i)["values"][0] for i in context.app._profile_list.get_children()]
    assert username in items


@when('I activate the profile "{username}"')
def activate_profile(context, username):
    # find profile list treeview
    tv = context.app._profile_list
    for iid in tv.get_children():
        if tv.item(iid)["values"][0] == username:
            tv.selection_set(iid)
            # Trigger selection and activation handlers
            context.app._on_profile_selected(None)
            context.app._on_profile_activated(None)
            # Update context.app to the new current view
            new_view = context.router._current_view
            context.app = new_view
            # If switched to login view, capture it
            from src.UserProfile.infrastructure.ui.views.profile_login_view import ProfileLoginView

            if isinstance(new_view, ProfileLoginView):
                context.login_view = new_view
            break


@then('I should be navigated to the deck list for "{username}"')
def check_deck_navigation(context, username):
    # deck list navigation shows toast info
    assert context.toast[0] == "Info"
    assert "listy talii" in context.toast[1]


@then('I should be navigated to the login view for "{username}"')
def check_login_navigation(context, username):
    # current view should be a ProfileLoginView
    assert isinstance(context.router._current_view, ProfileLoginView)
    assert context.router._current_view._state.username == username
    context.login_view = context.router._current_view


@when('I enter password "{password}"')
def enter_password(context, password):
    entry = context.login_view._password_input
    entry.delete(0, tk.END)
    entry.insert(0, password)


@when("I confirm login")
def confirm_login(context):
    context.login_view._on_login_attempt()
    context.root.update()


@then('I should see an error "{message}"')
def check_password_error(context, message):
    error = context.login_view._error_label.cget("text")
    assert error == message


@then("the password input should be cleared")
def check_password_cleared(context):
    value = context.login_view._password_input.get()
    assert value == ""


# US-003: Change password steps
@when('I choose change password for "{username}"')
def choose_change_password(context, username):
    raise NotImplementedError("Change password UI not implemented yet")


@when('I enter new password "{password}" and confirm')
def enter_new_password(context, password):
    raise NotImplementedError("Entering and confirming new password not implemented yet")


@then('the user profile "{username}" should be password protected')
def profile_should_be_protected(context, username):
    raise NotImplementedError("Checking that profile is password protected not implemented yet")


@then('the user profile "{username}" should not be password protected')
def profile_should_not_be_protected(context, username):
    raise NotImplementedError("Checking that profile is not password protected not implemented yet")
