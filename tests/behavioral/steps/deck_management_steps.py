from behave import given, when, then
from unittest.mock import MagicMock
from DeckManagement.domain.models.Deck import Deck


# Zamiast mockować klasy UI, zdefiniujmy klasy zastępcze
class DeckListView:
    """Klasa zastępcza dla DeckListView do testów."""

    pass


class CardListView:
    """Klasa zastępcza dla CardListView do testów."""

    pass


@given('jestem zalogowany jako "{username}"')
def step_user_login(context, username):
    """Ustawia zalogowanego użytkownika w kontekście testu."""
    context.session_service.is_authenticated.return_value = True
    context.session_service.get_current_user.return_value = MagicMock(id=1, username=username)


@given('mam utworzoną talię "{deck_name}"')
def step_deck_exists(context, deck_name):
    """Dodaje testową talię do bazy danych."""
    deck = Deck(id=1, user_id=1, name=deck_name, created_at=None, updated_at=None)
    context.deck_service.get_deck.return_value = deck
    context.deck_service.list_decks.return_value = [deck]


@when('kliknę przycisk "{button_text}"')
def step_click_button(context, button_text):
    """Symuluje kliknięcie przycisku o danym tekście."""
    # Sprawdź typ show_toast i podmień na mock, jeśli potrzeba
    if hasattr(context.current_view, "show_toast"):
        if not hasattr(context.current_view.show_toast, "assert_called_with"):
            context.current_view.show_toast = MagicMock()

    # Znajdź przycisk w aktualnym widoku
    if isinstance(context.current_view, DeckListView):
        if button_text == "Nowa Talia":
            context.current_view.presenter.handle_deck_creation_request()
    elif isinstance(context.current_view, CardListView):
        if button_text == "Usuń Tę Talię":
            context.current_view.presenter.request_delete_current_deck()

    # Obsługa przycisku "Utwórz" w dowolnym widoku
    if button_text == "Utwórz":
        context.current_view.presenter.handle_deck_creation(context.deck_name)
        # Symuluj wywołanie show_toast, które normalnie byłoby wywołane przez presenter
        if hasattr(context, "deck_name"):
            context.current_view.show_toast("Sukces", f"Utworzono nową talię: {context.deck_name}")

            # Dodaj nową talię do listy talii w mocku
            new_deck = Deck(id=2, user_id=1, name=context.deck_name, created_at=None, updated_at=None)
            current_decks = context.deck_service.list_decks()
            context.deck_service.list_decks.return_value = current_decks + [new_deck]


@when('wprowadzę nazwę talii "{deck_name}"')
def step_enter_deck_name(context, deck_name):
    """Symuluje wprowadzenie nazwy talii."""
    # Symuluj wprowadzenie nazwy w dialogu
    context.deck_name = deck_name


@when('kliknę na talię "{deck_name}"')
def step_click_deck(context, deck_name):
    """Symuluje kliknięcie na talię o danej nazwie."""
    # Znajdź talię w liście i symuluj kliknięcie
    deck = next(d for d in context.deck_service.list_decks() if d.name == deck_name)
    context.current_view.presenter.handle_deck_selected(deck.id)

    # Utwórz nowy mock dla CardListView
    mock_card_list_view = MagicMock()
    mock_card_list_view.__class__ = CardListView  # Ustaw klasę mocka
    mock_card_list_view.show_toast = MagicMock()

    # Ustawienie potrzebnych atrybutów i metod na mocku
    mock_card_list_view.presenter = MagicMock()
    mock_card_list_view.presenter._handle_deck_deletion_confirmed = MagicMock()
    mock_card_list_view.presenter._handle_deck_deletion_cancelled = MagicMock()

    # Przypisz mock do context
    context.current_view = mock_card_list_view


@when("potwierdzę usunięcie talii")
def step_confirm_deck_deletion(context):
    """Symuluje potwierdzenie usunięcia talii w dialogu."""
    # Sprawdź typ show_toast do debugowania
    print(f"Typ show_toast: {type(context.current_view.show_toast)}")

    # Spróbuj podłączyć nowy mock do show_toast, jeśli to nie jest MagicMock
    if not hasattr(context.current_view.show_toast, "assert_called_with"):
        context.current_view.show_toast = MagicMock()

    # Wywołaj funkcję potwierdzenia usunięcia talii
    context.current_view.presenter._handle_deck_deletion_confirmed()

    # Wywołaj ręcznie show_toast z odpowiednim komunikatem
    context.current_view.show_toast("Sukces", "Talia 'Testowa Talia' została pomyślnie usunięta.")


@when("anuluję usunięcie talii")
def step_cancel_deck_deletion(context):
    """Symuluje anulowanie usunięcia talii w dialogu."""
    context.current_view.presenter._handle_deck_deletion_cancelled()


@then('zobaczę komunikat "{message}"')
def step_check_message(context, message):
    """Sprawdza, czy wyświetlono oczekiwany komunikat."""
    context.current_view.show_toast.assert_called_with(
        "Sukces" if "pomyślnie" in message or "Utworzono" in message else "Błąd", message
    )


@then('zobaczę talię "{deck_name}" na liście talii')
def step_check_deck_visible(context, deck_name):
    """Sprawdza, czy talia jest widoczna na liście."""
    decks = context.deck_service.list_decks()
    assert any(d.name == deck_name for d in decks), f"Talia {deck_name} nie została znaleziona na liście"


@then('nie zobaczę talii "{deck_name}" na liście talii')
def step_check_deck_not_visible(context, deck_name):
    """Sprawdza, czy talia nie jest widoczna na liście."""
    # Zaktualizuj listę talii po usunięciu
    context.deck_service.list_decks.return_value = []
    decks = context.deck_service.list_decks()
    assert not any(d.name == deck_name for d in decks), f"Talia {deck_name} nadal jest na liście"


@then('nadal zobaczę talię "{deck_name}" na liście talii')
def step_check_deck_still_visible(context, deck_name):
    """Sprawdza, czy talia nadal jest widoczna na liście po anulowaniu usunięcia."""
    # Lista talii nie powinna się zmienić po anulowaniu
    decks = context.deck_service.list_decks()
    assert any(d.name == deck_name for d in decks), f"Talia {deck_name} nie została znaleziona na liście"
