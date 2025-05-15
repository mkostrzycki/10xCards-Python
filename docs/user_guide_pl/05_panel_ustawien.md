# Panel Ustawień Użytkownika ⚙️

Panel Ustawień Użytkownika to centralne miejsce, w którym możesz zarządzać konfiguracją swojego profilu oraz dostosowywać niektóre aspekty działania aplikacji 10xCards do własnych preferencji. W tej sekcji omówimy, jak uzyskać dostęp do panelu oraz jakie opcje oferuje.

## Dostęp do Panelu Ustawień

1.  Aby przejść do Panelu Ustawień, musisz być zalogowany na swój profil użytkownika (FR-041).
2.  Po zalogowaniu, poszukaj przycisku "Ustawienia" (lub podobnej ikony/opcji). Zazwyczaj znajduje się on na górnym pasku aplikacji, widocznym np. na ekranie listy talii (FR-042, US-016, KA-1).
    [SCREENSHOT_PL_05_przycisk_ustawienia_PNG]
3.  Kliknięcie tego przycisku przeniesie Cię do głównego ekranu Panelu Ustawień Użytkownika (US-016, KA-2).
    [SCREENSHOT_PL_05_panel_ustawien_glowny_widok_PNG]

Panel Ustawień zazwyczaj prezentuje listę dostępnych opcji konfiguracyjnych (FR-043, US-016, KA-3). Każda z tych opcji otwiera dedykowane okno dialogowe lub sekcję, pozwalającą na dokonanie konkretnych zmian. Z Panelu Ustawień powinieneś mieć również możliwość łatwego powrotu do poprzedniego widoku (np. listy talii) za pomocą przycisku "Wróć" lub podobnego (FR-044, US-016, KA-4).

## Opcje dostępne w Panelu Ustawień

Poniżej opisano kluczowe funkcje, które znajdziesz w Panelu Ustawień:

### Zmiana nazwy profilu

Jeśli chcesz zmienić nazwę swojego profilu użytkownika:

1.  W Panelu Ustawień wybierz opcję "Zmień nazwę profilu" (lub podobną) (US-017, KA-1).
2.  Otworzy się okno dialogowe, w którym zobaczysz pole tekstowe, prawdopodobnie wypełnione Twoją aktualną nazwą profilu (US-017, KA-2).
    [SCREENSHOT_PL_05_zmiana_nazwy_profilu_okno_PNG]
3.  Wprowadź nową nazwę. Pamiętaj o zasadach:
    *   Nowa nazwa musi być unikalna wśród wszystkich istniejących profili (FR-044b, US-017, KA-3).
    *   Nazwa nie może być pusta (FR-044b, US-017, KA-4).
    *   Maksymalna długość nazwy to 30 znaków (FR-044b, US-017, KA-4).
4.  Jeśli spróbujesz zapisać niepoprawną nazwę (np. już istniejącą, pustą, zbyt długą), aplikacja powinna wyświetlić komunikat o błędzie, a zmiana nie zostanie zapisana (US-017, KA-5).
5.  Po wprowadzeniu poprawnej nowej nazwy i kliknięciu przycisku "Zapisz" (lub podobnego), nazwa Twojego profilu zostanie zaktualizowana w bazie danych (FR-044c, US-017, KA-6).
6.  Otrzymasz potwierdzenie dokonania zmiany (US-017, KA-7), a okno dialogowe prawdopodobnie zamknie się, wracając do głównego widoku Panelu Ustawień (US-017, KA-8).

### Zarządzanie hasłem profilu

Ta opcja pozwala Ci ustawić, zmienić lub całkowicie usunąć hasło chroniące Twój profil (FR-045, US-003, KA-1).

1.  W Panelu Ustawień wybierz opcję "Zarządzaj hasłem" (lub podobną).
2.  Otworzy się dedykowane okno dialogowe (US-003, KA-2).
    [SCREENSHOT_PL_05_zarzadzanie_haslem_okno_PNG]

    **Jeśli hasło nie jest jeszcze ustawione (US-003, KA-3):**
    *   Zostaniesz poproszony o wprowadzenie nowego hasła oraz jego potwierdzenie (wpisanie drugi raz w celu uniknięcia pomyłek).
        [SCREENSHOT_PL_05_ustawianie_nowego_hasla_PNG]
    *   Po zatwierdzeniu, nowe hasło zostanie zaszyfrowane (przy użyciu bcrypt) i zapisane w bazie danych dla Twojego profilu (FR-048, US-003, KA-3b).
    *   Otrzymasz potwierdzenie, że hasło zostało pomyślnie ustawione (US-003, KA-3c).

    **Jeśli hasło jest już ustawione (US-003, KA-4):**
    *   Najpierw zostaniesz poproszony o podanie swojego **aktualnego hasła** – jest to zabezpieczenie potwierdzające, że to Ty dokonujesz zmiany (FR-046, US-003, KA-4a).
        [SCREENSHOT_PL_05_zmiana_hasla_podaj_stare_PNG]
    *   Następnie będziesz mógł wprowadzić **nowe hasło** i jego potwierdzenie (US-003, KA-4b). Jeśli chcesz **usunąć hasło**, po prostu pozostaw pola nowego hasła puste (FR-047, US-003, KA-4b).
        [SCREENSHOT_PL_05_zmiana_hasla_podaj_nowe_PNG]
    *   Po wprowadzeniu poprawnego aktualnego hasła i zatwierdzeniu (US-003, KA-4c):
        *   Jeśli podałeś nowe hasło, zostanie ono zaszyfrowane (bcrypt) i zaktualizuje istniejące w bazie. Otrzymasz potwierdzenie (US-003, KA-4c.i).
        *   Jeśli pola nowego hasła pozostały puste (w celu usunięcia hasła), dotychczasowe hasło zostanie usunięte z bazy danych. Otrzymasz potwierdzenie (US-003, KA-4c.ii).
    *   Jeśli wprowadzisz niepoprawne aktualne hasło, zobaczysz komunikat o błędzie, a zmiany nie zostaną wprowadzone (US-003, KA-4d).

3.  Okno dialogowe zarządzania hasłem powinno zawierać przyciski typu "Zapisz", "Ustaw", "Zmień" oraz "Anuluj" (US-003, KA-5).
4.  Po pomyślnie zakończonej operacji (ustawienie/zmiana/usunięcie hasła), wrócisz do głównego widoku Panelu Ustawień (US-003, KA-6).

### Zarządzanie kluczem API OpenRouter

Jeśli chcesz korzystać z funkcji generowania fiszek przez AI, musisz podać swój klucz API dla usługi OpenRouter.ai (lub innej skonfigurowanej). Ta sekcja pozwala na zarządzanie tym kluczem (FR-049, US-018, KA-1).

1.  W Panelu Ustawień wybierz opcję "Zarządzaj kluczem API OpenRouter" (lub podobną).
2.  Otworzy się okno dialogowe (US-018, KA-2).
    [SCREENSHOT_PL_05_zarzadzanie_kluczem_api_okno_PNG]
3.  W oknie znajdziesz pole do wprowadzenia lub edycji Twojego klucza API (US-018, KA-3).
    *   Jeśli klucz API jest już zapisany, ze względów bezpieczeństwa nie powinien być wyświetlany w pełnej, jawnej formie. Zamiast tego może być zamaskowany (np. `sk-xxxx...xxxx`) (FR-053, US-018, KA-4).
4.  Możesz:
    *   **Wprowadzić nowy klucz:** Jeśli nie masz jeszcze zapisanego klucza.
    *   **Zaktualizować istniejący klucz:** Wpisując nowy klucz w miejsce starego (zamaskowanego).
    *   **Usunąć klucz:** Poprzez dedykowany przycisk "Usuń klucz" lub poprzez wyczyszczenie pola i zapisanie (US-018, KA-5).
5.  Po kliknięciu przycisku "Zapisz" (lub "Zastosuj") (US-018, KA-6):
    *   **Walidacja:** Jeśli wprowadziłeś nowy lub zmieniłeś istniejący klucz, aplikacja spróbuje go zwalidować, np. poprzez testowe zapytanie do API OpenRouter (FR-051, US-018, KA-6a). Jest to ważne, aby upewnić się, że klucz jest poprawny, zanim zostanie zapisany.
    *   **Sukces walidacji:** Jeśli walidacja przebiegnie pomyślnie, klucz API zostanie zaszyfrowany (np. przy użyciu algorytmu Fernet z solą przechowywaną w pliku konfiguracyjnym aplikacji – jest to rozwiązanie MVP dla lokalnego przechowywania) i zapisany (lub zaktualizowany) w bazie danych (FR-050, US-018, KA-6b). Otrzymasz komunikat potwierdzający, np. "Klucz API jest poprawny. Zapis klucza zakończył się sukcesem." (FR-052).
    *   **Nieudana walidacja:** Jeśli klucz okaże się niepoprawny, nie zostanie on zapisany. Otrzymasz komunikat o błędzie, np. "Wprowadzony klucz API jest niepoprawny. Zapis klucza anulowany." (FR-052, US-018, KA-6c).
    *   **Usunięcie klucza:** Jeśli zdecydowałeś się usunąć klucz, zostanie on usunięty z bazy danych, a Ty otrzymasz potwierdzenie (US-018, KA-6d).
6.  Okno dialogowe powinno zawierać przyciski "Zapisz", opcjonalnie "Usuń klucz" oraz "Anuluj" (US-018, KA-7).
7.  Po pomyślnej operacji (zapisie lub usunięciu klucza) wrócisz do głównego widoku Panelu Ustawień (US-018, KA-8).
8.  **Ważne:** Jeśli klucz API nie jest ustawiony lub został usunięty, przy próbie skorzystania z funkcji generowania fiszek przez AI, aplikacja wyświetli komunikat informujący o braku klucza i konieczności jego skonfigurowania w Panelu Ustawień (FR-054, US-018, KA-9).
    [SCREENSHOT_PL_05_brak_klucza_api_komunikat_PNG]

### Wybór domyślnego modelu LLM

10xCards może wspierać różne modele językowe (LLM) do generowania fiszek (za pośrednictwem OpenRouter). Tutaj możesz wybrać, który model ma być używany domyślnie (FR-055, US-019, KA-1).

1.  W Panelu Ustawień wybierz opcję "Wybierz domyślny model LLM" (lub podobną).
2.  Otworzy się okno dialogowe z listą rozwijaną (lub innym selektorem), zawierającą dostępne modele LLM (US-019, KA-2). Lista tych modeli jest predefiniowana i przechowywana w pliku konfiguracyjnym aplikacji (np. `src/Shared/infrastructure/config.py`) (FR-056).
    [SCREENSHOT_PL_05_wybor_modelu_llm_okno_PNG]
3.  Twój aktualnie wybrany domyślny model LLM powinien być zaznaczony na liście (US-019, KA-3).
4.  Wybierz preferowany model z listy i kliknij przycisk "Zapisz" (lub podobny) (US-019, KA-4).
5.  Wybrany model zostanie zapisany jako domyślny dla Twojego profilu użytkownika w bazie danych (FR-057, US-019, KA-5). Otrzymasz potwierdzenie zapisu (US-019, KA-6).
6.  Okno dialogowe zamknie się, a Ty wrócisz do Panelu Ustawień (US-019, KA-7).
7.  Wybrany domyślny model LLM (lub jego identyfikator) powinien być widoczny na ekranie generowania fiszek, abyś wiedział, który model zostanie użyty (FR-058, US-019, KA-8).
    [SCREENSHOT_PL_05_model_llm_widoczny_na_ekranie_generowania_PNG]

    **Obsługa niedostępności modelu (FR-059):**
    Może się zdarzyć, że model LLM, który wcześniej ustawiłeś jako domyślny, zostanie usunięty z globalnej listy dostępnych modeli w aplikacji (np. po aktualizacji pliku konfiguracyjnego przez deweloperów). W takiej sytuacji:
    *   Aplikacja powinna użyć pierwszego dostępnego modelu z aktualnej listy jako modelu zastępczego do generowania fiszek (FR-059a, US-019, KA-9b).
    *   Przy następnym logowaniu lub przy pierwszej próbie użycia funkcji AI, powinieneś otrzymać jednorazowy komunikat informujący, że Twój poprzedni domyślny model nie jest już dostępny, został ustawiony model zastępczy, oraz sugestię, abyś wybrał nowy domyślny model w Panelu Ustawień (FR-059b, US-019, KA-9a).
        [SCREENSHOT_PL_05_model_llm_niedostepny_komunikat_PNG]
    *   Wartość domyślnego modelu w bazie danych dla Twojego profilu powinna zostać odpowiednio zaktualizowana (np. na `null` lub na faktycznie używany model zastępczy – szczegóły zależą od implementacji) (FR-059c).

### Wybór schematu kolorystycznego aplikacji

Aby dostosować wygląd aplikacji do swoich upodobań, możesz wybrać jeden z predefiniowanych schematów kolorystycznych (motywów) (FR-060, US-020, KA-1).

1.  W Panelu Ustawień wybierz opcję "Wybierz schemat kolorystyczny" (lub podobną).
2.  Otworzy się okno dialogowe z listą rozwijaną (lub innym selektorem) dostępnych schematów kolorystycznych (US-020, KA-2). Lista tych schematów, opartych np. na motywach biblioteki `ttkbootstrap`, jest przechowywana w pliku konfiguracyjnym aplikacji (np. `src/Shared/infrastructure/config.py`) (FR-061).
    [SCREENSHOT_PL_05_wybor_schematu_kolorystycznego_okno_PNG]
3.  Aktualnie aktywny schemat kolorystyczny powinien być zaznaczony na liście (US-020, KA-3).
4.  Wybierz preferowany schemat z listy (US-020, KA-4).
5.  Po wybraniu schematu i kliknięciu przycisku "Zastosuj" lub "Zapisz" (US-020, KA-5):
    *   Wybrany schemat kolorystyczny powinien być **natychmiast aplikowany** do aktywnego okna aplikacji (czyli Panelu Ustawień oraz okna dialogowego wyboru schematu) (FR-063, US-020, KA-5a). Dzięki temu od razu zobaczysz efekt swojej zmiany.
    *   Wybrany schemat zostanie zapisany jako Twoja preferencja dla Twojego profilu użytkownika w bazie danych (FR-062, US-020, KA-5b).
    *   Otrzymasz potwierdzenie (może być ono czysto wizualne – poprzez zmianę wyglądu aplikacji) (US-020, KA-5c).
6.  Okno dialogowe zamknie się, a Ty wrócisz do Panelu Ustawień, który również powinien już odzwierciedlać nowo wybrany schemat kolorystyczny (US-020, KA-6).
7.  Pozostałe, nieaktywne lub zamknięte wcześniej okna aplikacji zaktualizują swój wygląd po ich ponownym otwarciu lub przy następnym uruchomieniu aplikacji (zgodnie z założeniami MVP, zmiana jest natychmiastowa dla aktywnego okna, reszta przy ponownym otwarciu) (US-020, KA-7). 