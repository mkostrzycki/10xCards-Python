# Architektura UI dla 10xCards

## 1. Przegląd struktury UI

UI aplikacji 10xCards opiera się na sekwencyjnej, stackowej nawigacji między widokami, z zachowanym nagłówkiem (Back, pasek postępu, przycisk Ustawienia) i stopką (informacje o motywie i modelu AI). Globalny menubar zawiera opcje File, Settings i Help→Keyboard Shortcuts. Komunikaty („flash messages”) wyświetlane są jako toasty w górnym rogu aplikacji. Layout oparty na `grid` z `weight` dla responsywnego skalowania i minimalnym rozmiarem okna 800×600 (skalowanym DPI).

## 2. Lista widoków

### 2.1 ProfileListView
- Ścieżka: `/profiles`
- Główny cel: Wyświetlenie istniejących profili, wybór profilu lub utworzenie nowego.
- Kluczowe informacje: lista profili (username, ikona kłódki przy chronionych), przycisk „Dodaj profil”.
- Kluczowe komponenty: `Listbox` (lub `Treeview`), `Button` Dodaj, `ToastContainer`.
- UX/Dostępność/Security: obsługa klawiatury (Enter wybiera, BackSpace wychodzi), ARIA-labels, walidacja nazwy (max 30 znaków), maskowanie inputu hasła.

### 2.2 ProfileLoginView
- Ścieżka: `/profiles/login`
- Główny cel: Weryfikacja hasła chronionego profilu.
- Kluczowe informacje: pole hasła (maskowane), przycisk Zaloguj, komunikaty błędów.
- Kluczowe komponenty: `Entry(show="*")`, `Button`, `ToastContainer`.
- UX/Dostępność/Security: focus na polu hasła, bezpieczeństwo maskowania, brak limitu prób.

### 2.3 DeckListView
- Ścieżka: `/decks`
- Główny cel: Lista talii bieżącego użytkownika, tworzenie i usuwanie talii.
- Kluczowe informacje: lista talii sortowana rosnąco według created_at, etykieta „Sort: Oldest first”, przycisk „Utwórz nową talię”.
- Kluczowe komponenty: `HeaderBar`, `Treeview/Listbox`, `Button` Nowa talia, ikona usuwania, `ToastContainer`.
- UX/Dostępność/Security: potwierdzenie kasowania, klawiaturowe skróty (BackSpace).

### 2.4 CardListView
- Ścieżka: `/decks/{deck_id}/cards`
- Główny cel: Przeglądanie fiszek w talii, manualne tworzenie i dostęp do generatora AI.
- Kluczowe informacje: lista fiszek (fragment przodu), przyciski Dodaj fiszkę i Generuj z AI.
- Kluczowe komponenty: `Treeview`, `Button` Dodaj, `Button` Generuj AI, ikony edycji/usuwania.
- UX/Dostępność/Security: limity długości pól frontendowe, potwierdzenie usuwania.

### 2.5 AIReviewView
- Ścieżka: `/decks/{deck_id}/ai-review`
- Główny cel: Przegląd wygenerowanych przez AI fiszek (3-15 propozycji).
- Kluczowe informacje: siatka kart z przodem/tyłem, przyciski Accept (a), Edit (e), Reject (x), wskaźnik postępu generowania.
- Kluczowe komponenty: `Grid` z `FlashcardTile`, `Button` Akceptuj/Edycja/Odrzuć, `ProgressBar` podczas generowania.
- UX/Dostępność/Security: klawiszowe skróty, aria-labels, walidacja formatu wejściowego (1000–10000 znaków).

### 2.6 FlashcardEditView
- Ścieżka: `/cards/{card_id}/edit` (osadzony panel)
- Główny cel: Edycja lub akceptacja nowej fiszki (manual lub AI).
- Kluczowe informacje: pola Front (max 200) i Back (max 500), przyciski Zapisz i Anuluj.
- Kluczowe komponenty: `Frame` osadzone w głównym widoku, `Entry`/`Text`, `Button`.
- UX/Dostępność/Security: wizualne licznik znaków, walidacja przed zapisem, reset stanu FSRS.

### 2.7 StudySessionView (FullScreenSessionView)
- Ścieżka: `/session`
- Główny cel: Przeprowadzenie sesji spaced repetition.
- Kluczowe informacje: front karty, button Odwróć, oceny (Again, Hard, Good, Easy), wskaźnik postępu (%), Stopka z motywem i modelem.
- Kluczowe komponenty: `HeaderBar`, `FlashcardDisplay`, `ButtonGroup` ocen, `Button` Next, `FooterBar`.
- UX/Dostępność/Security: pełen ekran, klawiszowe skróty (., q), odpowiednie focusy.

### 2.8 SettingsView
- Ścieżka: `/settings`
- Główny cel: Konfiguracja motywu, modelu AI, API key.
- Kluczowe informacje: `Combobox` Theme, `Combobox` AI Model, `Entry` API Key, przycisk Zapisz.
- Kluczowe komponenty: `Label`+`Combobox`, `Entry`, `Button`, `ToastContainer`.
- UX/Dostępność/Security: maskowanie API key, walidacja, bezpieczne przechowywanie przez repozytorium.

### 2.9 HelpShortcutsView
- Ścieżka: `/help/shortcuts`
- Główny cel: Wyświetlenie mapy klawiszowych skrótów.
- Kluczowe informacje: lista skrótów i opisów.
- Kluczowe komponenty: `Dialog` lub osadzony panel, `Treeview`.
- UX/Dostępność: czytelny tekst, focus trap w panelu.

## 3. Mapa podróży użytkownika

1. Uruchomienie → ProfileListView
2. [Nowy profil] → formularz nazwy → zapis → powrót do ProfileListView
3. [Wybór chronionego] → ProfileLoginView → poprawne hasło → DeckListView
4. [Wybór talii] → CardListView
5. [Generuj AI] → AIReviewView → Akceptuj/Edycja/Odrzuć → powrót do CardListView
6. [Dodaj manual] → FlashcardEditView → Zapisz → powrót do CardListView
7. [Start sesji] → StudySessionView → cykl odsłaniania/oceny → End Session (q) → CardListView
8. [Settings] (Cmd+, lub menu) → SettingsView → Zapisz → powrót do bieżącego widoku
9. [Help→Shortcuts] → HelpShortcutsView → Zamknij → powrót

## 4. Układ i struktura nawigacji

- NavigationController ze stackiem widoków (push/pop). Nagłówek z przyciskiem Back (pop).
- Globalny MenuBar (File, Settings, Help).
- Persistent HeaderBar i FooterBar renderowane w `AppView`, zmieniające się zależnie od active view.
- Modalność: brak modali — wszystkie panele są osadzone jako dzieci głównego view.
- ToastManager nad `AppView` do globalnych komunikatów.

## 5. Kluczowe komponenty

- NavigationController: zarządza stosem widoków.
- HeaderBar: Back, ProgressBar, SettingsButton.
- FooterBar: Theme/Model display.
- MenuBar: File, Settings, Help→Shortcuts.
- ToastManager: sukces/error, auto-dismiss + manual close.
- ShortcutManager: mapuje klawisze na akcje Presenterów.
- ProfileList, DeckList, CardList: generyczne listy z sortowaniem.
- AIReviewGrid: siatka kafelków z akcjami.
- FlashcardForm: formularz dodawania/edycji.
- FullScreenSession: sesja nauki w trybie pełnoekranowym.
- SettingsForm: konfiguracja globalna.
- PasswordPrompt: reużywany panel logowania.
