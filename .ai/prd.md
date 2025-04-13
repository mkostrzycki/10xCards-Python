# Dokument wymagań produktu (PRD) - 10xCards MVP

## 1. Przegląd produktu

10xCards to aplikacja desktopowa (MVP dla macOS) zaprojektowana, aby pomóc profesjonalistom uczącym się nowych umiejętności w efektywnym tworzeniu i przyswajaniu wiedzy za pomocą fiszek edukacyjnych. Aplikacja wykorzystuje sztuczną inteligencję (GPT-4o mini) do automatycznego generowania fiszek z dostarczonego tekstu, a także umożliwia ich manualne tworzenie. Kluczowym elementem jest integracja z algorytmem powtórek rozłożonych w czasie FSRS (za pomocą biblioteki `Py-FSRS`), który optymalizuje proces nauki. Aplikacja obsługuje wielu użytkowników na jednym komputerze, oferując opcjonalną ochronę profilu hasłem i przechowując dane lokalnie w bazie SQLite. Celem MVP jest dostarczenie podstawowych narzędzi do szybkiego tworzenia i efektywnej nauki przy użyciu fiszek, rozwiązując problem czasochłonności manualnego ich przygotowywania.

## 2. Problem użytkownika

Manualne tworzenie wysokiej jakości fiszek edukacyjnych jest procesem czasochłonnym i żmudnym. Wymaga to nie tylko syntezy materiału, ale także formułowania pytań i odpowiedzi, co może zniechęcać użytkowników, zwłaszcza profesjonalistów z ograniczonym czasem, do korzystania z metody spaced repetition – jednej z najefektywniejszych technik nauki. Istniejące aplikacje często oferują gotowe zestawy, które nie zawsze odpowiadają indywidualnym potrzebom, lub wymagają w pełni manualnego wprowadzania danych. Brak jest prostego narzędzia, które automatyzowałoby część procesu tworzenia fiszek na podstawie własnych materiałów użytkownika, integrując to jednocześnie z naukowo potwierdzonym algorytmem powtórek.

## 3. Wymagania funkcjonalne

### 3.1 Zarządzanie profilami użytkowników
- FR-001: Aplikacja musi umożliwiać utworzenie nowego profilu użytkownika poprzez podanie nazwy.
- FR-002: Aplikacja musi wyświetlać listę istniejących profili przy starcie.
- FR-003: Aplikacja musi umożliwiać wybór profilu z listy w celu zalogowania.
- FR-004: Użytkownik musi mieć możliwość opcjonalnego ustawienia hasła dla swojego profilu.
- FR-005: Jeśli profil jest chroniony hasłem, aplikacja musi wymagać podania hasła przy próbie logowania.
- FR-006: Hasła muszą być przechowywane w bazie danych w formie zahashowanej (bcrypt).
- FR-007: Dane każdego użytkownika (talie, fiszki, postęp nauki) muszą być odizolowane od innych profili.

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

### 3.8 Interfejs użytkownika (UI)
- FR-038: Interfejs użytkownika musi być zaimplementowany przy użyciu biblioteki Tkinter w Pythonie.
- FR-039: Architektura kodu musi oddzielać logikę biznesową od warstwy UI, aby ułatwić ewentualną migrację UI w przyszłości.
- FR-040: Interfejs musi być intuicyjny i łatwy w obsłudze dla użytkownika docelowego.

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
- Przechowywanie danych: Lokalna baza danych SQLite.
- UI: Python z Tkinter.
- Logowanie: Błędy (AI, FSRS, DB, ogólne), komunikacja AI.

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
- Tytuł: Ustawianie hasła dla profilu
- Opis: Jako użytkownik, chcę móc ustawić opcjonalne hasło dla mojego profilu, aby chronić dostęp do moich danych na współdzielonym komputerze.
- Kryteria akceptacji:
    - 1. W ustawieniach profilu istnieje opcja "Ustaw/Zmień hasło".
    - 2. Po wybraniu opcji, użytkownik jest proszony o podanie nowego hasła i jego potwierdzenie.
    - 3. Po zatwierdzeniu, hasło jest hashowane za pomocą bcrypt i zapisywane w bazie danych dla danego profilu.
    - 4. Użytkownik otrzymuje potwierdzenie, że hasło zostało ustawione/zmienione.
    - 5. Istnieje możliwość usunięcia hasła (np. przez pozostawienie pustego pola nowego hasła).

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

## 6. Metryki sukcesu

Sukces MVP będzie mierzony za pomocą następujących wskaźników:

1.  Akceptacja fiszek generowanych przez AI:
    - Cel: 75% fiszek wygenerowanych przez AI jest akceptowanych przez użytkownika bez edycji.
    - Mierzenie: Zliczanie liczby fiszek, które zostały zapisane poprzez kliknięcie przycisku "Akceptuj" w interfejsie przeglądu fiszek AI (bez wcześniejszej edycji). Wynik ten jest dzielony przez całkowitą liczbę fiszek przedstawionych użytkownikowi do przeglądu po generacji AI. Pomiar będzie realizowany przez logowanie zdarzeń w aplikacji.

2.  Wykorzystanie AI do tworzenia fiszek:
    - Cel: 75% wszystkich utworzonych (zaakceptowanych lub edytowanych) fiszek w systemie pochodzi z generatora AI.
    - Mierzenie: Zliczanie całkowitej liczby fiszek zapisanych w bazie danych ze źródłem "ai-generated" lub "ai-edited". Wynik ten jest dzielony przez całkowitą liczbę fiszek w bazie danych (źródło "ai-generated", "ai-edited", "manual"). Pomiar będzie realizowany przez analizę danych w bazie lub logowanie zdarzeń tworzenia fiszek.