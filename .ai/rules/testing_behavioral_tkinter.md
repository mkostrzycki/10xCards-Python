# Testowanie Behawioralne (Behave) z Tkinter

-   **Framework:** Używaj `Behave` do pisania testów behawioralnych dla aplikacji Tkinter. Scenariusze definiuj w plikach `.feature` w języku Gherkin, a implementacje kroków w Pythonie.
-   **Struktura Aplikacji:** Projektuj aplikację Tkinter tak, aby widgety były łatwo dostępne z poziomu testów (np. jako atrybuty instancji głównej klasy aplikacji). Ułatwi to symulację interakcji i weryfikację stanu.
-   **Obsługa Pętli Zdarzeń:**
    -   **Nigdy nie używaj `mainloop()` w testach**, ponieważ blokuje to ich wykonanie.
    -   Zamiast tego, po każdej symulowanej akcji (np. `button.invoke()`) lub przed asercją stanu widgetu, używaj `app.update()` lub `app.update_idletasks()`, aby przetworzyć oczekujące zdarzenia Tkinter i odświeżyć stan GUI.
-   **Symulacja Interakcji:**
    -   Proste akcje, jak kliknięcie przycisku, symuluj za pomocą metody `invoke()` odpowiedniego widgetu (`context.app.button.invoke()`).
    -   Bardziej złożone interakcje (np. wpisywanie tekstu) symuluj za pomocą metod widgetów (`.insert()`, `.delete()`) lub, w razie potrzeby, przez generowanie zdarzeń (`.event_generate()`).
-   **Asercje Stanu:**
    -   W krokach `Then`, weryfikuj stan widgetów, odczytując ich właściwości za pomocą metody `cget("property_name")` (np. `context.app.label.cget("text")`) lub innych odpowiednich metod (`.get()` dla pól tekstowych).
    -   Upewnij się, że wywołałeś `update()` lub `update_idletasks()` przed asercją, aby mieć pewność, że stan widgetu jest aktualny.
-   **Kontekst Behave:** Przechowuj instancję aplikacji Tkinter w obiekcie `context` Behave (`context.app`), aby była dostępna we wszystkich krokach scenariusza. Inicjuj aplikację w kroku `Given`.
-   **Przykładowy Krok:**
    ```python
    from behave import when, then
    from your_app_module import YourApp # Załóżmy, że to jest Twoja klasa aplikacji Tkinter

    @when('Użytkownik klika przycisk "{button_text}"')
    def step_impl(context, button_text):
        # Znajdź przycisk (zakładając, że jest atrybutem context.app)
        # Może wymagać bardziej złożonej logiki szukania widgetu, jeśli nie jest bezpośrednio dostępny
        button = getattr(context.app, "some_button_attribute_name") # Dostosuj wg swojej aplikacji
        assert button.cget("text") == button_text # Dodatkowa weryfikacja
        button.invoke()
        context.app.update() # Przetwórz zdarzenie kliknięcia

    @then('Etykieta "{label_id}" powinna wyświetlać tekst "{expected_text}"')
    def step_impl(context, label_id, expected_text):
        # Znajdź etykietę (zakładając, że jest atrybutem)
        label = getattr(context.app, label_id) # Dostosuj wg swojej aplikacji
        context.app.update_idletasks() # Upewnij się, że stan jest aktualny
        actual_text = label.cget("text")
        assert actual_text == expected_text, f"Expected '{expected_text}', but got '{actual_text}'"

    ```
-   **Modularność:** Dąż do oddzielenia logiki biznesowej od kodu GUI, co ułatwi zarówno testowanie jednostkowe logiki, jak i testowanie behawioralne interfejsu.
