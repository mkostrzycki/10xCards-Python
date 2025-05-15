# Plan Wdrożenia Dokumentacji Użytkownika (PL & EN) dla 10xCards

## Cel Główny:
Stworzenie kompleksowej, łatwej w nawigacji i bogatej w zrzuty ekranu dokumentacji użytkownika dla aplikacji 10xCards w językach polskim (PL) i angielskim (EN), z maksymalnym wykorzystaniem modelu LLM do generowania i adaptacji treści.

## Faza 0: Przygotowanie i Konfiguracja

1.  **Zdefiniowanie Struktury Katalogów:**
    *   Katalog główny: `docs/`
    *   Dokumentacja polska: `docs/user_guide_pl/`
        *   Pliki Markdown: `docs/user_guide_pl/00_wstep.md`, `docs/user_guide_pl/01_pierwsze_kroki.md`, itd.
        *   Obrazki: `docs/user_guide_pl/images/`
    *   Dokumentacja angielska: `docs/user_guide_en/`
        *   Pliki Markdown: `docs/user_guide_en/00_introduction.md`, `docs/user_guide_en/01_getting_started.md`, itd.
        *   Obrazki: `docs/user_guide_en/images/`
2.  **Ustalenie Konwencji Nazewnictwa:**
    *   **Pliki Markdown (PL):** `NN_tytul_sekcji.md` (np. `01_pierwsze_kroki.md`)
    *   **Pliki Markdown (EN):** `NN_section_title.md` (np. `01_getting_started.md`)
    *   **Obrazki (PL):** `pl_NN_opis_obrazka.png` (np. `pl_01_ekran_logowania.png`)
    *   **Obrazki (EN):** `en_NN_image_description.png` (np. `en_01_login_screen.png`)
    *   **Placeholdery w Markdown:** `[SCREENSHOT_PL_NN_opis_obrazka_PNG]` i `[SCREENSHOT_EN_NN_image_description_PNG]`
3.  **Przygotowanie Materiałów Wejściowych dla LLM:**
    *   Główny dokument: `prd.md` (załączony).
    *   Ustalona struktura User Guide (z poprzedniej wiadomości).

## Faza 1: Generowanie Wstępnego Szkicu Dokumentacji Polskiej (Zadanie dla LLM)

1.  **Dane wejściowe dla LLM:**
    *   Pełna treść pliku `prd.md`.
    *   Szczegółowa struktura User Guide (podana w poprzedniej odpowiedzi).
    *   Konwencja dotycząca placeholderów dla obrazków (np. `[SCREENSHOT_PL_01_nazwa_funkcji_opis_PNG]`).
2.  **Polecenie dla LLM:**
    ```
    Na podstawie załączonego dokumentu PRD oraz podanej struktury User Guide, wygeneruj wstępny szkic dokumentacji użytkownika w języku polskim. 
    Dla każdej funkcji i kroku opisanego w PRD, stwórz odpowiednią sekcję w dokumentacji. 
    W miejscach, gdzie niezbędny będzie zrzut ekranu ilustrujący daną funkcję lub krok, wstaw placeholder zgodnie z konwencją: [SCREENSHOT_PL_numerSekcji_krótkiOpisObrazka_PNG]. 
    Numeruj placeholdery sekwencyjnie w ramach całego dokumentu. 
    Skup się na jasnym i zwięzłym opisie kroków, które użytkownik musi wykonać. 
    Zachowaj ton instruktażowy i przyjazny. Podziel dokument na pliki zgodnie z ustaloną strukturą (np. 00_wstep.md, 01_pierwsze_kroki.md itd.).
    ```
3.  **Oczekiwany rezultat:**
    *   Zestaw plików `.md` w katalogu `docs/user_guide_pl/` zawierający wstępny tekst dokumentacji z placeholderami na obrazki.

## Faza 2: Tworzenie Zrzutów Ekranu dla Wersji Polskiej (Zadanie dla Użytkownika)

1.  **Proces:**
    *   Użytkownik przechodzi przez każdy plik `.md` wygenerowany przez LLM.
    *   Dla każdego placeholdera `[SCREENSHOT_PL_...]` wykonuje odpowiednią akcję w aplikacji 10xCards i robi zrzut ekranu.
    *   Zapisuje zrzuty ekranu w katalogu `docs/user_guide_pl/images/` używając nazwy pliku zdefiniowanej w placeholderze (np. `pl_01_ekran_logowania.png`).
2.  **Cel:**
    *   Zebranie wszystkich niezbędnych zrzutów ekranu dla polskiej wersji dokumentacji.

## Faza 3: Uzupełnianie i Rafinacja Dokumentacji Polskiej (Zadanie dla LLM + Użytkownik)

1.  **Proces (iteracyjny, sekcja po sekcji lub plik po pliku):**
    *   Użytkownik wybiera sekcję/plik `.md`.
    *   Zamienia placeholdery `[SCREENSHOT_PL_...]` na rzeczywiste tagi Markdown dla obrazków: `![Opis obrazka](images/nazwa_obrazka.png)`.
    *   **Polecenie dla LLM (dla każdej sekcji z obrazkami):**
        ```
        Przeanalizuj poniższy fragment dokumentacji użytkownika oraz załączony opis/nazwę zrzutu ekranu: [NAZWA_PLIKU_OBRAZKA.PNG - np. pl_02_tworzenie_talii_dialog.png].
        Opis obrazka: [KRÓTKI_OPIS_CO_WIDAĆ_NA_OBRAZKU_JEŚLI_LLM_NIE_WIDZI_OBRAZÓW_BEZPOŚREDNIO]
        Upewnij się, że tekst dokładnie opisuje kroki widoczne na zrzucie ekranu i jest spójny z obrazem. 
        Dostosuj opisy, aby były jak najbardziej precyzyjne i pomocne dla użytkownika. 
        Jeśli na obrazku są widoczne konkretne nazwy przycisków, pól tekstowych, upewnij się, że są one poprawnie odzwierciedlone w tekście.
        Oto fragment do analizy:
        ---
        [WSTAW_FRAGMENT_MD_Z_OBRAZKIEM]
        ---
        ```
    *   Użytkownik przegląda sugestie LLM, wprowadza poprawki i akceptuje zmiany.
2.  **Oczekiwany rezultat:**
    *   W pełni uzupełniona i zrefinowana polska wersja dokumentacji z poprawnie wstawionymi i opisanymi zrzutami ekranu.

## Faza 4: Tłumaczenie i Adaptacja na Wersję Angielską (Zadanie dla LLM)

1.  **Dane wejściowe dla LLM:**
    *   Finalna, zrecenzowana wersja polskiej dokumentacji (`docs/user_guide_pl/*.md`).
    *   Konwencja dotycząca placeholderów dla obrazków w wersji angielskiej (np. `[SCREENSHOT_EN_01_feature_name_description_PNG]`).
2.  **Polecenie dla LLM:**
    ```
    Przetłumacz poniższą dokumentację użytkownika z języka polskiego na język angielski. 
    Zachowaj strukturę dokumentu i formatowanie Markdown. 
    W miejscach, gdzie w wersji polskiej znajdują się odwołania do obrazków (np. ![Opis PL](images/pl_obrazek.png)), zamień je na angielskie placeholdery zgodnie z konwencją: [SCREENSHOT_EN_numerSekcji_krótkiOpisObrazkaPoAngielsku_PNG], starając się, aby opis w placeholderze odpowiadał oryginalnemu obrazkowi.
    Upewnij się, że tłumaczenie jest naturalne, gramatycznie poprawne i dostosowane do anglojęzycznego użytkownika (np. terminologia techniczna, zwroty).
    Oto dokumentacja do tłumaczenia:
    ---
    [WSTAW_CALA_POLSKA_DOKUMENTACJE_MD]
    ---
    ```
3.  **Oczekiwany rezultat:**
    *   Zestaw plików `.md` w katalogu `docs/user_guide_en/` zawierający przetłumaczony tekst dokumentacji z placeholderami na angielskie obrazki.

## Faza 6: Tworzenie/Adaptacja Zrzutów Ekranu dla Wersji Angielskiej (Zadanie dla Użytkownika)

1.  **Proces:**
    *   Użytkownik przegląda angielską wersję dokumentacji i listę placeholderów `[SCREENSHOT_EN_...]`.
    *   **Scenariusz A: UI aplikacji jest identyczne w obu językach.**
        *   Użytkownik kopiuje odpowiednie obrazki z `docs/user_guide_pl/images/` do `docs/user_guide_en/images/`.
        *   Zmienia nazwy skopiowanych plików, aby pasowały do angielskich placeholderów (np. `pl_01_ekran_logowania.png` -> `en_01_login_screen.png`).
    *   **Scenariusz B: UI aplikacji różni się w zależności od języka (np. inne etykiety przycisków).**
        *   Użytkownik przełącza aplikację na język angielski (jeśli taka opcja istnieje) lub przygotowuje wersję z angielskim UI.
        *   Wykonuje nowe zrzuty ekranu dla każdego placeholdera, zapisując je w `docs/user_guide_en/images/` z odpowiednimi angielskimi nazwami.
2.  **Cel:**
    *   Zebranie/przygotowanie wszystkich niezbędnych zrzutów ekranu dla angielskiej wersji dokumentacji.

## Faza 7: Uzupełnianie i Rafinacja Dokumentacji Angielskiej (Zadanie dla LLM + Użytkownik)

1.  **Proces (analogiczny do Fazy 3, ale dla wersji angielskiej):**
    *   Użytkownik wybiera sekcję/plik `.md` w wersji angielskiej.
    *   Zamienia placeholdery `[SCREENSHOT_EN_...]` na rzeczywiste tagi Markdown: `![Image description](images/image_name.png)`.
    *   **Polecenie dla LLM (dla każdej sekcji z obrazkami):**
        ```
        Analyze the following section of the user documentation and the provided screenshot description/filename: [IMAGE_FILENAME.PNG - e.g., en_02_create_deck_dialog.png].
        Image description: [BRIEF_DESCRIPTION_OF_WHAT_IS_ON_THE_SCREENSHOT_IF_LLM_CANNOT_SEE_IMAGES_DIRECTLY]
        Ensure the text accurately describes the steps visible in the screenshot and is consistent with the image. 
        Adjust the descriptions to be as precise and helpful as possible for the user. 
        If specific button names or text fields are visible in the image, ensure they are correctly reflected in the text.
        Here is the section to analyze:
        ---
        [PASTE_MD_SECTION_WITH_IMAGE_HERE]
        ---
        ```
    *   Użytkownik przegląda sugestie LLM, wprowadza poprawki i akceptuje zmiany.
2.  **Oczekiwany rezultat:**
    *   W pełni uzupełniona i zrefinowana angielska wersja dokumentacji.
