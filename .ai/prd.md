# Dokument wymagań produktu (PRD) - 10xCards MVP

## 1. Przegląd produktu

10xCards to aplikacja desktopowa (MVP dla macOS) zaprojektowana, aby pomóc profesjonalistom uczącym się nowych umiejętności w efektywnym tworzeniu i przyswajaniu wiedzy za pomocą fiszek edukacyjnych. Aplikacja wykorzystuje sztuczną inteligencję (GPT-4o mini) do automatycznego generowania fiszek z dostarczonego tekstu, a także umożliwia ich manualne tworzenie. Kluczowym elementem jest integracja z algorytmem powtórek rozłożonych w czasie FSRS (za pomocą biblioteki `Py-FSRS`), który optymalizuje proces nauki. Aplikacja obsługuje wielu użytkowników na jednym komputerze, oferując opcjonalną ochronę profilu hasłem i przechowując dane lokalnie w bazie SQLite. Celem MVP jest dostarczenie podstawowych narzędzi do szybkiego tworzenia i efektywnej nauki przy użyciu fiszek, rozwiązując problem czasochłonności manualnego ich przygotowywania.

## 2. Problem użytkownika

Manualne tworzenie wysokiej jakości fiszek edukacyjnych jest procesem czasochłonnym i żmudnym. Wymaga to nie tylko syntezy materiału, ale także formułowania pytań i odpowiedzi, co może zniechęcać użytkowników, zwłaszcza profesjonalistów z ograniczonym czasem, do korzystania z metody spaced repetition – jednej z najefektywniejszych technik nauki. Istniejące aplikacje często oferują gotowe zestawy, które nie zawsze odpowiadają indywidualnym potrzebom, lub wymagają w pełni manualnego wprowadzania danych. Brak jest prostego narzędzia, które automatyzowałoby część procesu tworzenia fiszek na podstawie własnych materiałów użytkownika, integrując to jednocześnie z naukowo potwierdzonym algorytmem powtórek. Dodatkowo, użytkownicy potrzebują możliwości personalizacji swojego doświadczenia oraz zarządzania kluczowymi ustawieniami aplikacji, takimi jak dane dostępowe do usług AI czy preferencje wizualne, w jednym, łatwo dostępnym miejscu.

## 3. Wymagania funkcjonalne

### 3.1 Zarządzanie profilami użytkowników
- FR-001: Aplikacja musi umożliwiać utworzenie nowego profilu użytkownika poprzez podanie nazwy.
- FR-002: Aplikacja musi wyświetlać listę istniejących profili przy starcie.
- FR-003: Aplikacja musi umożliwiać wybór profilu z listy w celu zalogowania. (Zobacz też FR-042 dotyczące dostępu do Panelu Ustawień)
- FR-004: Użytkownik musi mieć możliwość opcjonalnego ustawienia hasła dla swojego profilu. (Przeniesione do Panelu Ustawień Użytkownika - zobacz FR-045)
- FR-005: Jeśli profil jest chroniony hasłem, aplikacja musi wymagać podania hasła przy próbie logowania.
- FR-006: Hasła muszą być przechowywane w bazie danych w formie zahashowanej (bcrypt).
- FR-007: Dane każdego użytkownika (talie, fiszki, postęp nauki, ustawienia) muszą być odizolowane od innych profili.

### 3.2 Zarządzanie taliami fiszek
- FR-008: Użytkownik musi mieć możliwość utworzenia nowej talii fiszek, podając jej nazwę.
- FR-009: Aplikacja musi wyświetlać listę talii należących do zalogowanego użytkownika.
- FR-010: Użytkownik musi mieć możliwość usunięcia istniejącej talii wraz ze wszystkimi zawartymi w niej fiszkami.
- FR-011: Użytkownik musi mieć możliwość wybrania talii, aby zobaczyć jej zawartość (listę fiszek).

### 3.3 Generowanie fiszek przez AI
- FR-012: Użytkownik musi mieć możliwość wklejenia tekstu (minimum 1000, maksimum 10000 znaków) do dedykowanego pola w celu wygenerowania fiszek dla wybranej talii.
- FR-013: Aplikacja musi wysyłać wklejony tekst do API GPT-4o mini z użyciem zdefiniowanego promptu.
- FR-014: Aplikacja musi przetworzyć odpowiedź API i wyświetlić wygenerowane fiszki (3-15) użytkownikowi do przeglądu.
- FR-015: Wygenerowane fiszki muszą mieć format "przód" (pytanie, max 200 znaków) i "tył" (odpowiedź, max 500 znaków).
- FR-016: Użytkownik musi mieć możliwość zaakceptowania pojedynczej wygenerowanej fiszki, co spowoduje jej zapisanie w wybranej talii.
- FR-017: Użytkownik musi mieć możliwość edycji pojedynczej wygenerowanej fiszki przed jej zapisaniem. Edytowana fiszka jest zapisywana w wybranej talii.
- FR-018: Użytkownik musi mieć możliwość odrzucenia pojedynczej wygenerowanej fiszki, co spowoduje, że nie zostanie ona zapisana.
- FR-019: Aplikacja musi informować użytkownika o błędach podczas komunikacji z API AI (np. problem z połączeniem, błąd API key).
- FR-020: Aplikacja musi informować użytkownika, jeśli AI nie zwróci poprawnych fiszek lub wystąpi inny problem podczas generowania.

### 3.4 Manualne tworzenie i edycja fiszek
- FR-021: Użytkownik musi mieć możliwość manualnego utworzenia nowej fiszki w wybranej talii, podając tekst dla strony przedniej (max 200 znaków) i tylnej (max 500 znaków).
- FR-022: Użytkownik musi mieć możliwość przeglądania listy fiszek w wybranej talii.
- FR-023: Użytkownik musi mieć możliwość edycji istniejącej fiszki (tekst przód/tył).
- FR-024: Użytkownik musi mieć możliwość usunięcia istniejącej fiszki.

### 3.5 Sesja nauki (Spaced Repetition)
- FR-025: Użytkownik musi mieć możliwość rozpoczęcia sesji nauki dla wybranej talii.
- FR-026: Aplikacja musi wykorzystywać bibliotekę `Py-FSRS` do określenia, które fiszki mają zostać pokazane w danej sesji i w jakiej kolejności.
- FR-027: Podczas sesji nauki aplikacja musi wyświetlać stronę przednią fiszki.
- FR-028: Użytkownik musi mieć możliwość odsłonięcia strony tylnej fiszki.
- FR-029: Po odsłonięciu strony tylnej, użytkownik musi mieć możliwość oceny swojej odpowiedzi za pomocą czterech opcji: "Again", "Hard", "Good", "Easy".
- FR-030: Aplikacja musi przekazać ocenę użytkownika do algorytmu FSRS w celu aktualizacji stanu powtórki dla danej fiszki.
- FR-031: Sesja nauki kończy się, gdy algorytm FSRS uzna, że nie ma więcej fiszek do pokazania w danym momencie.

### 3.6 Przechowywanie danych
- FR-032: Wszystkie dane aplikacji (profile, talie, fiszki, stan FSRS, hasła) muszą być przechowywane w lokalnej bazie danych SQLite.
- FR-033: Struktura bazy danych musi być zaprojektowana tak, aby zapewnić integralność danych i efektywne zapytania.

### 3.7 Logowanie
- FR-034: Aplikacja musi logować komunikację z API AI (wysłany prompt, otrzymana odpowiedź, ewentualne błędy) do celów debugowania.
- FR-035: Aplikacja musi logować błędy zgłaszane przez bibliotekę `Py-FSRS`.
- FR-036: Aplikacja musi logować błędy operacji na bazie danych SQLite.
- FR-037: Aplikacja musi logować inne nieoczekiwane błędy i wyjątki.
- FR-037a: Aplikacja powinna logować zmiany istotnych ustawień użytkownika (np. zmiana klucza API, domyślnego modelu LLM) dla celów audytu i wsparcia.

### 3.8 Interfejs użytkownika (UI)
- FR-038: Interfejs użytkownika musi być zaimplementowany przy użyciu biblioteki Tkinter w Pythonie (z wykorzystaniem ttkbootstrap do stylizacji).
- FR-039: Architektura kodu musi oddzielać logikę biznesową od warstwy UI, aby ułatwić ewentualną migrację UI w przyszłości.
- FR-040: Interfejs musi być intuicyjny i łatwy w obsłudze dla użytkownika docelowego.

### 3.9 Panel Ustawień Użytkownika
- FR-041: Aplikacja musi udostępniać dedykowany "Panel Ustawień Użytkownika", dostępny po zalogowaniu.
- FR-042: Dostęp do Panelu Ustawień musi być możliwy poprzez przycisk "Ustawienia" zlokalizowany na górnym pasku aplikacji, widoczny po zalogowaniu użytkownika (np. na ekranie listy talii).
- FR-043: Panel Ustawień musi pozwalać na nawigację do poszczególnych opcji konfiguracyjnych. Każda opcja (np. zmiana hasła) musi otwierać dedykowane okno dialogowe.
- FR-044: Z Panelu Ustawień użytkownik musi mieć możliwość powrotu do poprzedniego widoku (np. listy talii).

#### 3.9.1 Zmiana Nazwy Profilu (w Panelu Ustawień)
- FR-044a: Użytkownik musi mieć możliwość zmiany nazwy swojego profilu.
- FR-044b: Nowa nazwa profilu podlega tym samym ograniczeniom co przy tworzeniu profilu (np. unikalność, maksymalna długość 30 znaków, nie może być pusta).
- FR-044c: Zmiana nazwy profilu musi być zapisywana w bazie danych.

#### 3.9.2 Zarządzanie Hasłem Profilu (w Panelu Ustawień)
- FR-045: Użytkownik musi mieć możliwość ustawienia, zmiany lub usunięcia hasła do swojego profilu.
- FR-046: W przypadku zmiany lub usunięcia hasła, aplikacja musi wymagać podania aktualnego hasła.
- FR-047: Aby usunąć hasło, użytkownik musi pozostawić pole nowego hasła puste (i potwierdzić aktualne hasło).
- FR-048: Nowe hasło musi być hashowane (bcrypt) przed zapisaniem do bazy danych.

#### 3.9.3 Zarządzanie Kluczem API OpenRouter (w Panelu Ustawień)
- FR-049: Użytkownik musi mieć możliwość wprowadzenia, zaktualizowania lub usunięcia swojego klucza API OpenRouter.
- FR-050: Klucz API musi być szyfrowany (np. przy użyciu Fernet z solą przechowywaną w pliku konfiguracyjnym aplikacji) przed zapisaniem do bazy danych. Należy zaznaczyć, że jest to rozwiązanie MVP dla lokalnego przechowywania.
- FR-051: Aplikacja musi walidować poprawność klucza API przy próbie jego zapisu (np. poprzez testowe odpytanie API OpenRouter).
- FR-052: Użytkownik musi otrzymywać informację zwrotną o wyniku walidacji i zapisu klucza API (np. "Klucz API jest poprawny. Zapis klucza zakończył się sukcesem." lub "Wprowadzony klucz API jest niepoprawny. Zapis klucza anulowany.").
- FR-053: Wprowadzony klucz API nie powinien być wyświetlany w pełnej, jawnej formie w UI Panelu Ustawień po jego zapisaniu (np. wyświetlany jako zamaskowany).
- FR-054: W przypadku usunięcia klucza API, przy próbie generowania fiszek przez AI, użytkownik musi otrzymać komunikat o braku klucza i niemożności wykonania operacji.

#### 3.9.4 Wybór Domyślnego Modelu LLM (w Panelu Ustawień)
- FR-055: Użytkownik musi mieć możliwość wyboru domyślnego modelu LLM z predefiniowanej listy.
- FR-056: Lista dostępnych modeli LLM musi być przechowywana w pliku konfiguracyjnym aplikacji (`src/Shared/infrastructure/config.py`).
- FR-057: Wybrany domyślny model LLM musi być zapisywany w bazie danych dla profilu użytkownika.
- FR-058: Aktualnie wybrany (lub zastępczy) model LLM musi być widoczny na ekranie generowania fiszek.
- FR-059: W przypadku, gdy zapisany domyślny model LLM użytkownika zostanie usunięty z globalnej konfiguracji (pliku `config.py`), aplikacja musi:
    - FR-059a: Użyć pierwszego dostępnego modelu z listy jako modelu zastępczego dla generowania fiszek.
    - FR-059b: Poinformować użytkownika (np. jednorazowym komunikatem po zalogowaniu) o zmianie modelu na zastępczy i zasugerować wybór nowego domyślnego modelu w Panelu Ustawień.
    - FR-059c: Wartość domyślnego modelu w bazie danych dla tego użytkownika powinna zostać zaktualizowana (np. na `null` lub na faktycznie używany model zastępczy, do decyzji implementacyjnej).

#### 3.9.5 Wybór Schematu Kolorystycznego Aplikacji (w Panelu Ustawień)
- FR-060: Użytkownik musi mieć możliwość wyboru schematu kolorystycznego aplikacji z predefiniowanej listy (opartej na motywach ttkbootstrap).
- FR-061: Lista dostępnych schematów kolorystycznych musi być przechowywana w pliku konfiguracyjnym aplikacji (`src/Shared/infrastructure/config.py`).
- FR-062: Wybrany schemat kolorystyczny musi być zapisywany w bazie danych dla profilu użytkownika.
- FR-063: Zmiana schematu kolorystycznego musi być aplikowana natychmiast do aktywnego okna aplikacji, bez konieczności jej restartu. Pozostałe (nieaktywne/zamknięte) okna zaktualizują wygląd po ponownym otwarciu.

### 3.10 Konfiguracja Globalna Aplikacji
- FR-064: Aplikacja musi wykorzystywać centralny plik konfiguracyjny (np. `src/Shared/infrastructure/config.py`) do przechowywania globalnych ustawień, takich jak lista dostępnych modeli LLM, lista schematów kolorystycznych oraz sól dla szyfrowania klucza API.
- FR-065: Należy przewidzieć, że modyfikacje tego pliku (np. usunięcie modelu LLM) mogą wymagać odpowiedniej obsługi po stronie logiki aplikacji (jak w FR-059) oraz potencjalnie mechanizmów migracji danych użytkowników w przyszłych wersjach, jeśli struktura przechowywanych preferencji ulegnie zmianie.

## 4. Granice produktu

### 4.1 Co wchodzi w zakres MVP:
- Platforma: Aplikacja desktopowa dla macOS.
- Rdzenne funkcjonalności:
    - Zarządzanie profilami użytkowników (wiele profili na jednym komputerze).
    - Opcjonalna ochrona profilu hasłem (hashowanie bcrypt).
    - Tworzenie i zarządzanie taliami fiszek (tworzenie, usuwanie, przeglądanie listy).
    - Generowanie fiszek przez AI (GPT-4o mini) z tekstu (1k-10k znaków) z możliwością akceptacji/edycji/odrzucenia.
    - Manualne tworzenie, edycja i usuwanie fiszek (tylko tekst przód/tył).
    - Sesja nauki oparta na algorytmie FSRS (integracja `Py-FSRS`) z ocenami Again/Hard/Good/Easy.
    - Panel Ustawień Użytkownika:
        - Zmiana nazwy profilu.
        - Zarządzanie hasłem profilu (ustawianie, zmiana, usuwanie z weryfikacją aktualnego hasła).
        - Zarządzanie kluczem API OpenRouter (wprowadzanie, aktualizacja, usuwanie, szyfrowanie Fernet z solą z config.py, walidacja online, maskowanie w UI).
        - Wybór domyślnego modelu LLM (z listy w `config.py`, obsługa niedostępności modelu, informacja dla użytkownika).
        - Wybór schematu kolorystycznego aplikacji (z listy w `config.py` opartej na ttkbootstrap, natychmiastowe zastosowanie).
- Przechowywanie danych: Lokalna baza danych SQLite (rozszerzona o ustawienia użytkownika).
- UI: Python z Tkinter (z wykorzystaniem ttkbootstrap).
- Logowanie: Błędy (AI, FSRS, DB, ogólne), komunikacja AI, opcjonalnie zmiany w ustawieniach.

### 4.2 Co NIE wchodzi w zakres MVP:
- Wsparcie dla innych systemów operacyjnych (Windows, Linux).
- Zaawansowany, własny algorytm powtórek (jak SuperMemo, Anki) - korzystamy z gotowego FSRS.
- Import fiszek/materiałów z plików (np. PDF, DOCX, CSV, Anki).
- Eksport fiszek (nawet do JSON) - planowane po MVP.
- Współdzielenie talii/fiszek między użytkownikami (online).
- Synchronizacja danych między urządzeniami.
- Integracje z innymi platformami edukacyjnymi.
- Aplikacje mobilne (iOS, Android).
- Formatowanie tekstu fiszek (np. Markdown).
- Dodawanie obrazków/audio/wideo do fiszek.
- Przenoszenie fiszek między taliami.
- Zaawansowane statystyki nauki.
- Funkcje społecznościowe.
- Wyszukiwanie fiszek w obrębie talii lub globalnie.

## 5. Historyjki użytkowników

---
- ID: US-001
- Tytuł: Tworzenie nowego profilu użytkownika
- Opis: Jako nowy użytkownik, chcę móc utworzyć swój profil w aplikacji, podając unikalną nazwę, abym mógł zacząć tworzyć własne talie i fiszki.
- Kryteria akceptacji:
    - 1. Na ekranie startowym widoczny jest przycisk/opcja "Dodaj nowy profil".
    - 2. Po kliknięciu pojawia się pole do wprowadzenia nazwy profilu.
    - 3. Nazwa profilu może mieć maksymalnie 30 znaków.
    - 4. Po wprowadzeniu nazwy i zatwierdzeniu, nowy profil jest tworzony w bazie danych.
    - 5. Nowy profil pojawia się na liście profili na ekranie startowym.
    - 6. Aplikacja nie pozwala na utworzenie profilu o nazwie, która już istnieje (wyświetla stosowny komunikat).
    - 7. Nazwa profilu nie może być pusta.

---
- ID: US-002
- Tytuł: Wybór istniejącego profilu
- Opis: Jako powracający użytkownik, chcę móc wybrać swój profil z listy na ekranie startowym, aby uzyskać dostęp do swoich talii i fiszek.
- Kryteria akceptacji:
    - 1. Na ekranie startowym widoczna jest lista istniejących profili użytkowników.
    - 2. Kliknięcie na nazwę profilu, który nie ma ustawionego hasła, powoduje przejście do widoku listy talii tego użytkownika.
    - 3. Kliknięcie na nazwę profilu, który ma ustawione hasło, powoduje wyświetlenie monitu o hasło.

---
- ID: US-003
- Tytuł: Ustawianie/Zmiana/Usuwanie hasła dla profilu w Panelu Ustawień
- Opis: Jako użytkownik, chcę móc ustawić, zmienić lub usunąć opcjonalne hasło dla mojego profilu w Panelu Ustawień, aby chronić dostęp do moich danych na współdzielonym komputerze.
- Kryteria akceptacji:
    - 1. W Panelu Ustawień Użytkownika dostępna jest opcja "Zarządzaj hasłem" (lub podobna).
    - 2. Po wybraniu opcji otwiera się dedykowane okno dialogowe.
    - 3. Jeśli hasło nie jest ustawione:
        - a. Użytkownik jest proszony o podanie nowego hasła i jego potwierdzenie.
        - b. Po zatwierdzeniu, hasło jest hashowane (bcrypt) i zapisywane w bazie danych dla danego profilu.
        - c. Użytkownik otrzymuje potwierdzenie, że hasło zostało ustawione.
    - 4. Jeśli hasło jest już ustawione:
        - a. Użytkownik jest proszony o podanie aktualnego hasła.
        - b. Użytkownik jest proszony o podanie nowego hasła i jego potwierdzenie. Pozostawienie pól nowego hasła pustymi oznacza chęć usunięcia hasła.
        - c. Po wprowadzeniu poprawnego aktualnego hasła i zatwierdzeniu:
            - i. Jeśli podano nowe hasło, jest ono hashowane (bcrypt) i aktualizuje istniejące w bazie. Użytkownik otrzymuje potwierdzenie.
            - ii. Jeśli pola nowego hasła pozostawiono puste, hasło jest usuwane z bazy danych. Użytkownik otrzymuje potwierdzenie.
        - d. Wprowadzenie niepoprawnego aktualnego hasła skutkuje komunikatem o błędzie.
    - 5. Okno dialogowe zawiera przycisk "Zapisz" (lub "Ustaw", "Zmień") i "Anuluj".
    - 6. Po udanej operacji użytkownik wraca do głównego widoku Panelu Ustawień.

---
- ID: US-004
- Tytuł: Logowanie do profilu chronionego hasłem
- Opis: Jako użytkownik, którego profil jest chroniony hasłem, chcę móc się zalogować, podając poprawne hasło, aby uzyskać dostęp do moich danych.
- Kryteria akceptacji:
    - 1. Po kliknięciu na chroniony profil na liście, pojawia się monit z polem do wprowadzenia hasła.
    - 2. Po wprowadzeniu poprawnego hasła i zatwierdzeniu, użytkownik przechodzi do widoku listy talii.
    - 3. Po wprowadzeniu niepoprawnego hasła, użytkownik widzi komunikat o błędzie i pozostaje na ekranie logowania/wyboru profilu.
    - 4. Nie ma widocznego limitu prób logowania w MVP.

---
- ID: US-005
- Tytuł: Tworzenie nowej talii fiszek
- Opis: Jako zalogowany użytkownik, chcę móc utworzyć nową talię fiszek, podając jej nazwę, aby móc w niej grupować tematycznie powiązane fiszki.
- Kryteria akceptacji:
    - 1. W widoku listy talii dostępny jest przycisk/opcja "Utwórz nową talię".
    - 2. Po kliknięciu pojawia się pole do wprowadzenia nazwy talii.
    - 3. Po wprowadzeniu nazwy i zatwierdzeniu, nowa, pusta talia jest tworzona w bazie danych i powiązana z profilem użytkownika.
    - 4. Nowa talia pojawia się na liście talii użytkownika.
    - 5. Aplikacja nie pozwala na utworzenie talii o nazwie, która już istnieje dla danego użytkownika.
    - 6. Nazwa talii nie może być pusta.
    - 7. Nazwa talii może mieć maksymalnie 50 znaków.

---
- ID: US-006
- Tytuł: Przeglądanie listy talii
- Opis: Jako zalogowany użytkownik, chcę widzieć listę moich talii fiszek, abym mógł wybrać, którą chcę przeglądać, edytować lub z której chcę się uczyć.
- Kryteria akceptacji:
    - 1. Po zalogowaniu użytkownik widzi główny ekran z listą swoich talii.
    - 2. Dla każdej talii widoczna jest jej nazwa.
    - 3. Kliknięcie na nazwę talii przenosi użytkownika do widoku listy fiszek w tej talii.

---
- ID: US-007
- Tytuł: Usuwanie talii fiszek
- Opis: Jako zalogowany użytkownik, chcę móc usunąć wybraną talię fiszek wraz z całą jej zawartością, gdy nie jest mi już potrzebna.
- Kryteria akceptacji:
    - 1. W widoku listy talii istnieje opcja usunięcia talii (np. przycisk obok nazwy lub po kliknięciu prawym przyciskiem).
    - 2. Przed usunięciem aplikacja wyświetla monit z prośbą o potwierdzenie, informując, że usunięte zostaną również wszystkie fiszki w talii.
    - 3. Po potwierdzeniu, talia i wszystkie powiązane z nią fiszki oraz ich stany FSRS są usuwane z bazy danych.
    - 4. Usunięta talia znika z listy talii użytkownika.

---
- ID: US-008
- Tytuł: Generowanie fiszek przez AI z tekstu
- Opis: Jako zalogowany użytkownik, chcę móc wkleić fragment tekstu (1000-10000 znaków) i zainicjować proces generowania fiszek przez AI dla wybranej talii, aby szybko stworzyć materiały do nauki.
- Kryteria akceptacji:
    - 1. W widoku listy fiszek znajduje się opcja "Generuj fiszki z AI".
    - 2. Po wybraniu opcji pojawia się interfejs z polem tekstowym na wklejenie tekstu.
    - 3. Pole tekstowe waliduje minimalną (1000) i maksymalną (10000) długość tekstu przed wysłaniem. Komunikat informuje użytkownika o niespełnieniu wymagań.
    - 4. Po wklejeniu tekstu i kliknięciu przycisku "Generuj", aplikacja wysyła zapytanie do API GPT-4o mini z odpowiednim promptem i tekstem użytkownika.
    - 5. Podczas generowania widoczny jest wskaźnik postępu lub informacja "Generowanie...".
    - 6. Po otrzymaniu odpowiedzi z API, aplikacja przechodzi do widoku przeglądu wygenerowanych fiszek.
    - 7. W przypadku błędu komunikacji z API lub błędu przetwarzania, użytkownik widzi stosowny komunikat (np. "Nie udało się wygenerować fiszek. Spróbuj ponownie lub zmodyfikuj tekst.").

---
- ID: US-009
- Tytuł: Przeglądanie i zarządzanie fiszkami wygenerowanymi przez AI
- Opis: Jako użytkownik, po wygenerowaniu fiszek przez AI, chcę móc je przejrzeć, zaakceptować, edytować lub odrzucić pojedynczo, aby mieć kontrolę nad jakością materiałów zapisywanych w mojej talii.
- Kryteria akceptacji:
    - 1. Po udanym wygenerowaniu fiszek przez AI, użytkownik widzi listę proponowanych fiszek (przód i tył).
    - 2. Przy każdej fiszce znajdują się przyciski: "Akceptuj", "Edytuj", "Odrzuć".
    - 3. Kliknięcie "Akceptuj" powoduje zapisanie fiszki w wybranej talii (z oznaczeniem źródła jako "ai-generated") i usunięcie jej z listy proponowanych. Stan FSRS jest inicjalizowany dla tej fiszki.
    - 4. Kliknięcie "Edytuj" otwiera interfejs edycji danej fiszki (pola przód/tył są pre-wypełnione). Po zapisaniu edytowanej fiszki, jest ona zapisywana w talii (z oznaczeniem "ai-edited") i usuwana z listy proponowanych. Stan FSRS jest inicjalizowany.
    - 5. Kliknięcie "Odrzuć" powoduje usunięcie fiszki z listy proponowanych bez zapisywania jej w talii.
    - 6. Użytkownik może przejrzeć wszystkie proponowane fiszki i podjąć decyzję dla każdej z nich.
    - 7. Istnieje opcja zakończenia przeglądu (np. przycisk "Zakończ przegląd" lub automatycznie po przetworzeniu wszystkich).

---
- ID: US-010
- Tytuł: Manualne tworzenie nowej fiszki
- Opis: Jako zalogowany użytkownik, chcę móc manualnie dodać nową fiszkę do wybranej talii, wpisując treść dla strony przedniej i tylnej, gdy chcę stworzyć własną fiszkę od zera.
- Kryteria akceptacji:
    - 1. W widoku listy fiszek dla danej talii dostępny jest przycisk/opcja "Dodaj nową fiszkę".
    - 2. Po kliknięciu pojawia się formularz z polami tekstowymi "Przód" (limit 200 znaków) i "Tył" (limit 500 znaków).
    - 3. Pola tekstowe wizualnie lub komunikatem informują o zbliżaniu się/przekroczeniu limitu znaków.
    - 4. Po wypełnieniu pól i kliknięciu "Zapisz", nowa fiszka jest tworzona w bazie danych, powiązana z talią i użytkownikiem (z oznaczeniem źródła jako "manual"). Stan FSRS jest inicjalizowany.
    - 5. Nowa fiszka pojawia się na liście fiszek w talii.
    - 6. Próba zapisania fiszki z pustym polem "Przód" lub "Tył" skutkuje błędem/komunikatem.

---
- ID: US-011
- Tytuł: Przeglądanie fiszek w talii
- Opis: Jako zalogowany użytkownik, chcę móc przeglądać listę fiszek w wybranej talii, widząc ich zawartość (przynajmniej początek), abym mógł zarządzać swoimi materiałami.
- Kryteria akceptacji:
    - 1. Po wybraniu talii z listy talii, użytkownik widzi listę zawartych w niej fiszek.
    - 2. Dla każdej fiszki widoczny jest jej tekst przedni (lub jego fragment) i ewentualnie tekst tylny (lub jego fragment).
    - 3. Lista fiszek umożliwia przewijanie, jeśli zawiera więcej elementów niż mieści się na ekranie.

---
- ID: US-012
- Tytuł: Edycja istniejącej fiszki
- Opis: Jako zalogowany użytkownik, chcę móc edytować treść strony przedniej i/lub tylnej istniejącej fiszki w talii, aby poprawić błędy lub zaktualizować informacje.
- Kryteria akceptacji:
    - 1. W widoku listy fiszek istnieje opcja edycji dla każdej fiszki (np. przycisk "Edytuj").
    - 2. Po wybraniu opcji edycji otwiera się formularz z polami "Przód" i "Tył", wypełnionymi aktualną treścią fiszki.
    - 3. Użytkownik może modyfikować tekst w obu polach (z zachowaniem limitów znaków 200/500).
    - 4. Po kliknięciu "Zapisz", zmiany są zapisywane w bazie danych dla tej fiszki.
    - 5. Zaktualizowana treść fiszki jest widoczna na liście fiszek.
    - 6. Edycja fiszki resetuje jej stan FSRS.

---
- ID: US-013
- Tytuł: Usuwanie istniejącej fiszki
- Opis: Jako zalogowany użytkownik, chcę móc usunąć pojedynczą fiszkę z talii, gdy nie jest mi już potrzebna.
- Kryteria akceptacji:
    - 1. W widoku listy fiszek istnieje opcja usunięcia dla każdej fiszki (np. przycisk "Usuń").
    - 2. Przed usunięciem aplikacja wyświetla monit z prośbą o potwierdzenie.
    - 3. Po potwierdzeniu, fiszka i jej stan FSRS są usuwane z bazy danych.
    - 4. Fiszka znika z listy fiszek w talii.

---
- ID: US-014
- Tytuł: Rozpoczynanie sesji nauki
- Opis: Jako zalogowany użytkownik, chcę móc rozpocząć sesję nauki dla wybranej talii, aby przyswajać materiał zgodnie z algorytmem spaced repetition.
- Kryteria akceptacji:
    - 1. W widoku listy talii (lub listy fiszek) dostępny jest przycisk/opcja "Rozpocznij naukę".
    - 2. Kliknięcie przycisku inicjuje sesję nauki dla danej talii.
    - 3. Aplikacja komunikuje się z biblioteką `Py-FSRS`, aby pobrać pierwszą fiszkę do powtórki zgodnie z algorytmem.
    - 4. Użytkownikowi prezentowany jest interfejs sesji nauki z widoczną stroną przednią pierwszej fiszki.
    - 5. Jeśli FSRS wskaże, że nie ma fiszek do nauki w danym momencie, użytkownik otrzymuje stosowny komunikat.

---
- ID: US-015
- Tytuł: Przeprowadzanie sesji nauki
- Opis: Jako użytkownik w trakcie sesji nauki, chcę widzieć przód fiszki, móc odsłonić jej tył, a następnie ocenić swoją znajomość (Again/Hard/Good/Easy), aby algorytm FSRS mógł zaplanować kolejną powtórkę.
- Kryteria akceptacji:
    - 1. W interfejsie sesji nauki widoczny jest tekst strony przedniej bieżącej fiszki.
    - 2. Dostępny jest przycisk/opcja "Odwróć".
    - 3. Po kliknięciu "Odwróć", widoczny staje się również tekst strony tylnej fiszki.
    - 4. Po pokazaniu odpowiedzi, pojawiają się cztery przyciski oceny: "Again", "Hard", "Good", "Easy".
    - 5. Kliknięcie jednego z przycisków oceny powoduje przekazanie tej oceny do biblioteki `Py-FSRS` dla bieżącej fiszki.
    - 6. Aplikacja pobiera kolejną fiszkę do powtórki z FSRS i wyświetla jej stronę przednią, kontynuując cykl.
    - 7. Sesja kończy się (lub użytkownik jest informowany), gdy FSRS nie zwraca kolejnej fiszki do powtórki. Aplikacja wraca do widoku listy fiszek/talii.

---
- ID: US-016
- Tytuł: Dostęp do Panelu Ustawień Użytkownika
- Opis: Jako zalogowany użytkownik, chcę mieć łatwy dostęp do Panelu Ustawień, aby móc zarządzać konfiguracją swojego profilu i preferencjami aplikacji.
- Kryteria akceptacji:
    - 1. Po zalogowaniu, na górnym pasku aplikacji (np. w widoku listy talii) widoczny jest przycisk "Ustawienia".
    - 2. Kliknięcie przycisku "Ustawienia" przenosi użytkownika do ekranu Panelu Ustawień Użytkownika.
    - 3. Ekran Panelu Ustawień zawiera listę dostępnych opcji konfiguracyjnych (np. "Zmień nazwę profilu", "Zarządzaj hasłem", "Klucz API OpenRouter", "Domyślny model LLM", "Schemat kolorystyczny").
    - 4. Na ekranie Panelu Ustawień dostępny jest przycisk "Wróć" (lub analogiczny), który pozwala powrócić do poprzedniego widoku (np. listy talii).

---
- ID: US-017
- Tytuł: Zmiana nazwy profilu w Panelu Ustawień
- Opis: Jako użytkownik, chcę móc zmienić nazwę swojego profilu w Panelu Ustawień, jeśli zdecyduję, że obecna nazwa mi nie odpowiada.
- Kryteria akceptacji:
    - 1. W Panelu Ustawień dostępna jest opcja "Zmień nazwę profilu".
    - 2. Po wybraniu opcji otwiera się okno dialogowe z polem do wprowadzenia nowej nazwy profilu, pre-wypełnionym aktualną nazwą.
    - 3. Nowa nazwa profilu musi być unikalna wśród istniejących profili.
    - 4. Nowa nazwa profilu nie może być pusta i może mieć maksymalnie 30 znaków.
    - 5. Próba zapisania niepoprawnej nazwy (np. pustej, zbyt długiej, już istniejącej) skutkuje wyświetleniem komunikatu o błędzie, a zmiana nie jest zapisywana.
    - 6. Po wprowadzeniu poprawnej nowej nazwy i kliknięciu "Zapisz", nazwa profilu jest aktualizowana w bazie danych.
    - 7. Użytkownik otrzymuje potwierdzenie zmiany nazwy.
    - 8. Okno dialogowe zamyka się, a użytkownik wraca do Panelu Ustawień, gdzie widoczna jest (jeśli dotyczy) zaktualizowana nazwa lub jest pewność, że zmiana została dokonana.

---
- ID: US-018
- Tytuł: Zarządzanie kluczem API OpenRouter w Panelu Ustawień
- Opis: Jako użytkownik, chcę móc wprowadzić, zaktualizować lub usunąć mój klucz API OpenRouter w Panelu Ustawień, aby kontrolować dostęp aplikacji do usług AI.
- Kryteria akceptacji:
    - 1. W Panelu Ustawień dostępna jest opcja "Zarządzaj kluczem API OpenRouter" (lub podobna).
    - 2. Po wybraniu opcji otwiera się okno dialogowe.
    - 3. W oknie dialogowym znajduje się pole do wprowadzenia/edycji klucza API.
    - 4. Jeśli klucz API jest już zapisany, jest on wyświetlany w formie zamaskowanej (np. `sk-xxxx...xxxx`).
    - 5. Użytkownik może wprowadzić nowy klucz, zmodyfikować istniejący (wpisując nowy w jego miejsce) lub usunąć klucz (np. poprzez dedykowany przycisk "Usuń klucz" lub czyszcząc pole i zapisując).
    - 6. Po kliknięciu "Zapisz" (lub "Zastosuj"):
        - a. Jeśli wprowadzono nowy/zmieniony klucz, aplikacja próbuje go zwalidować online (np. przez testowe zapytanie do OpenRouter).
        - b. Jeśli walidacja powiedzie się, klucz jest szyfrowany (Fernet z solą z `config.py`) i zapisywany/aktualizowany w bazie danych. Użytkownik otrzymuje komunikat "Klucz API jest poprawny. Zapis klucza zakończył się sukcesem."
        - c. Jeśli walidacja nie powiedzie się, klucz nie jest zapisywany. Użytkownik otrzymuje komunikat "Wprowadzony klucz API jest niepoprawny. Zapis klucza anulowany."
        - d. Jeśli użytkownik zdecydował się usunąć klucz, jest on usuwany z bazy danych. Użytkownik otrzymuje potwierdzenie.
    - 7. Okno dialogowe zawiera przyciski "Zapisz", "Usuń klucz" (opcjonalnie) i "Anuluj".
    - 8. Po udanej operacji (zapis/usunięcie) użytkownik wraca do głównego widoku Panelu Ustawień.
    - 9. Jeśli klucz API nie jest ustawiony lub został usunięty, próba skorzystania z funkcji generowania fiszek AI skutkuje komunikatem informującym o braku klucza i konieczności jego skonfigurowania.

---
- ID: US-019
- Tytuł: Wybór domyślnego modelu LLM w Panelu Ustawień
- Opis: Jako użytkownik, chcę móc wybrać preferowany domyślny model LLM z listy dostępnych modeli w Panelu Ustawień, aby dostosować generowanie fiszek AI do moich potrzeb.
- Kryteria akceptacji:
    - 1. W Panelu Ustawień dostępna jest opcja "Wybierz domyślny model LLM" (lub podobna).
    - 2. Po wybraniu opcji otwiera się okno dialogowe z listą rozwijaną (lub innym selektorem) dostępnych modeli LLM. Lista modeli jest pobierana z pliku `src/Shared/infrastructure/config.py`.
    - 3. Aktualnie wybrany domyślny model jest zaznaczony na liście.
    - 4. Użytkownik może wybrać model z listy i kliknąć "Zapisz".
    - 5. Wybrany model jest zapisywany jako domyślny dla profilu użytkownika w bazie danych.
    - 6. Użytkownik otrzymuje potwierdzenie zapisu.
    - 7. Okno dialogowe zamyka się, a użytkownik wraca do Panelu Ustawień.
    - 8. Wybrany model (lub jego identyfikator) jest wyświetlany na ekranie generowania fiszek.
    - 9. Jeśli zapisany domyślny model użytkownika zostanie usunięty z globalnej konfiguracji (z `config.py`):
        - a. Przy następnym logowaniu lub próbie użycia AI, użytkownik otrzymuje jednorazowy komunikat informujący, że jego poprzedni domyślny model nie jest już dostępny i został ustawiony model zastępczy (pierwszy z aktualnej listy), z sugestią wyboru nowego modelu w Panelu Ustawień.
        - b. Do generowania fiszek używany jest model zastępczy.

---
- ID: US-020
- Tytuł: Wybór schematu kolorystycznego aplikacji w Panelu Ustawień
- Opis: Jako użytkownik, chcę móc wybrać preferowany schemat kolorystyczny aplikacji z listy dostępnych motywów w Panelu Ustawień, aby dostosować wygląd interfejsu do moich upodobań.
- Kryteria akceptacji:
    - 1. W Panelu Ustawień dostępna jest opcja "Wybierz schemat kolorystyczny" (lub podobna).
    - 2. Po wybraniu opcji otwiera się okno dialogowe z listą rozwijaną (lub innym selektorem) dostępnych schematów kolorystycznych (np. motywów ttkbootstrap). Lista schematów jest pobierana z pliku `src/Shared/infrastructure/config.py`.
    - 3. Aktualnie aktywny schemat jest zaznaczony na liście.
    - 4. Użytkownik może wybrać schemat z listy.
    - 5. Po wybraniu schematu i kliknięciu "Zastosuj" (lub "Zapisz"):
        - a. Wybrany schemat jest natychmiast aplikowany do aktywnego okna aplikacji (Panel Ustawień i okno dialogowe wyboru schematu).
        - b. Wybrany schemat jest zapisywany jako preferencja dla profilu użytkownika w bazie danych.
        - c. Użytkownik otrzymuje potwierdzenie (może być wizualne poprzez zmianę wyglądu).
    - 6. Okno dialogowe zamyka się, a użytkownik wraca do Panelu Ustawień, który również odzwierciedla nowy schemat.
    - 7. Inne otwarte okna aplikacji mogą nie zaktualizować schematu natychmiast, ale zastosują go po ponownym otwarciu lub przy następnym uruchomieniu aplikacji. (Do doprecyzowania: MVP zakłada zmianę dla aktywnego okna, reszta przy ponownym otwarciu).

## 6. Metryki sukcesu

Sukces MVP będzie mierzony za pomocą następujących wskaźników:

1.  Akceptacja fiszek generowanych przez AI:
    - Cel: 75% fiszek wygenerowanych przez AI jest akceptowanych przez użytkownika bez edycji.
    - Mierzenie: Zliczanie liczby fiszek, które zostały zapisane poprzez kliknięcie przycisku "Akceptuj" w interfejsie przeglądu fiszek AI (bez wcześniejszej edycji). Wynik ten jest dzielony przez całkowitą liczbę fiszek przedstawionych użytkownikowi do przeglądu po generacji AI. Pomiar będzie realizowany przez logowanie zdarzeń w aplikacji.

2.  Wykorzystanie AI do tworzenia fiszek:
    - Cel: 75% wszystkich utworzonych (zaakceptowanych lub edytowanych) fiszek w systemie pochodzi z generatora AI.
    - Mierzenie: Zliczanie całkowitej liczby fiszek zapisanych w bazie danych ze źródłem "ai-generated" lub "ai-edited". Wynik ten jest dzielony przez całkowitą liczbę fiszek w bazie danych (źródło "ai-generated", "ai-edited", "manual"). Pomiar będzie realizowany przez analizę danych w bazie lub logowanie zdarzeń tworzenia fiszek.
