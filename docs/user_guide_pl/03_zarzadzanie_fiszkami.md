# Zarządzanie Fiszkami (Cards) 🃏

Fiszki to serce aplikacji 10xCards! W tej sekcji dowiesz się wszystkiego o tworzeniu fiszek – zarówno z pomocą sztucznej inteligencji, jak i manualnie – oraz o zarządzaniu nimi: przeglądaniu, edycji i usuwaniu.

Po otwarciu wybranej talii (jak opisano w sekcji "Zarządzanie Taliami"), zobaczysz widok listy fiszek należących do tej talii. [SCREENSHOT_PL_03_widok_listy_fiszek_PNG]

## Generowanie fiszek z pomocą AI

Jedną z najpotężniejszych funkcji 10xCards jest możliwość automatycznego generowania fiszek z dostarczonego tekstu dzięki integracji z modelem GPT-4o mini.

### Jak rozpocząć generowanie fiszek AI?

1.  Upewnij się, że jesteś w widoku konkretnej talii, do której chcesz dodać fiszki.
2.  Poszukaj opcji "Generuj fiszki z AI" (lub podobnej). Może to być przycisk lub pozycja w menu (US-008, KA-1).
    [SCREENSHOT_PL_03_przycisk_generuj_AI_PNG]

### Wklejanie tekstu i inicjowanie procesu

1.  Po wybraniu opcji generowania fiszek AI, pojawi się interfejs z dedykowanym polem tekstowym (US-008, KA-2).
    [SCREENSHOT_PL_03_okno_generowania_AI_PNG]
2.  Wklej w to pole tekst, z którego chcesz wygenerować fiszki (FR-012). Pamiętaj o kilku zasadach:
    *   Tekst powinien mieć **minimum 1000 znaków**.
    *   Tekst nie powinien przekraczać **maksimum 10000 znaków**.
    *   Aplikacja powinna poinformować Cię, jeśli tekst nie spełnia tych kryteriów (US-008, KA-3).
3.  Po wklejeniu tekstu i upewnieniu się, że jest poprawny, kliknij przycisk "Generuj" (lub podobny) (US-008, KA-4).
4.  Aplikacja wyśle Twój tekst (wraz ze specjalnie przygotowanym promptem) do API GPT-4o mini (FR-013).
5.  Podczas gdy AI pracuje nad Twoimi fiszkami, na ekranie powinien być widoczny wskaźnik postępu lub informacja typu "Generowanie fiszek, proszę czekać..." (US-008, KA-5).
    [SCREENSHOT_PL_03_AI_wskaznik_postepu_PNG]

### Przeglądanie, akceptowanie, edytowanie i odrzucanie fiszek od AI

Po chwili (czas generowania może zależeć od długości tekstu i obciążenia API), aplikacja otrzyma odpowiedź od AI i wyświetli Ci listę wygenerowanych propozycji fiszek (FR-014, US-008, KA-6, US-009, KA-1).

Zazwyczaj AI wygeneruje od 3 do 15 fiszek, każda składająca się z:
*   **Przodu (pytanie):** Maksymalnie 200 znaków (FR-015).
*   **Tyłu (odpowiedź):** Maksymalnie 500 znaków (FR-015).

[SCREENSHOT_PL_03_AI_lista_propozycji_fiszek_PNG]

Dla każdej zaproponowanej fiszki będziesz miał dostępne następujące opcje (US-009, KA-2):

*   **Akceptuj:** Kliknięcie tego przycisku spowoduje zapisanie fiszki w aktualnie wybranej talii (FR-016, US-009, KA-3). Fiszka zostanie oznaczona jako "ai-generated". Po zaakceptowaniu, fiszka zniknie z listy propozycji.
    [SCREENSHOT_PL_03_AI_przycisk_akceptuj_PNG]
*   **Edytuj:** Jeśli chcesz coś zmienić w zaproponowanej fiszce przed jej zapisaniem, kliknij "Edytuj" (FR-017, US-009, KA-4). Otworzy się standardowy interfejs edycji fiszki z polami "Przód" i "Tył" wypełnionymi treścią od AI. Po dokonaniu zmian i zapisaniu, edytowana fiszka trafi do Twojej talii (oznaczona jako "ai-edited") i zniknie z listy propozycji.
    [SCREENSHOT_PL_03_AI_przycisk_edytuj_PNG]
*   **Odrzuć:** Jeśli uznasz, że dana propozycja jest nieprzydatna, kliknij "Odrzuć" (FR-018, US-009, KA-5). Fiszka nie zostanie zapisana i zniknie z listy propozycji.
    [SCREENSHOT_PL_03_AI_przycisk_odrzuc_PNG]

Możesz przejrzeć wszystkie propozycje i podjąć decyzję dla każdej z nich. Po przetworzeniu wszystkich fiszek lub gdy zdecydujesz się zakończyć przegląd (np. przez dedykowany przycisk "Zakończ przegląd"), wrócisz do widoku listy fiszek w talii (US-009, KA-6, KA-7).

### Co robić w przypadku błędów generowania AI?

Czasami proces generowania fiszek przez AI może napotkać problemy. Aplikacja poinformuje Cię o tym:

*   **Błędy komunikacji z API AI:** Jeśli wystąpi problem z połączeniem internetowym, nieprawidłowy klucz API (więcej o tym w sekcji "Panel Ustawień") lub inny błąd po stronie serwera AI, zobaczysz odpowiedni komunikat (FR-019, US-008, KA-7). Np. "Nie udało się połączyć z serwerem AI. Sprawdź połączenie internetowe i konfigurację klucza API." [SCREENSHOT_PL_03_AI_blad_polaczenia_PNG]
*   **Problemy z odpowiedzią AI:** Może się zdarzyć, że AI nie zwróci poprawnie sformatowanych fiszek lub odpowiedź będzie pusta. W takim przypadku również otrzymasz stosowną informację (FR-020). Np. "AI nie wygenerowało poprawnych fiszek dla podanego tekstu. Spróbuj zmodyfikować tekst lub użyć innego fragmentu." [SCREENSHOT_PL_03_AI_blad_odpowiedzi_PNG]

W obu przypadkach zazwyczaj najlepszym rozwiązaniem jest sprawdzenie konfiguracji, połączenia internetowego lub próba z innym fragmentem tekstu.

## Manualne tworzenie i zarządzanie fiszkami

Oprócz generowania fiszek z pomocą AI, zawsze masz możliwość pełnej manualnej kontroli nad swoimi materiałami.

### Tworzenie nowej fiszki ręcznie

Chcesz dodać własną, precyzyjnie sformułowaną fiszkę? Nic prostszego!

1.  W widoku listy fiszek dla wybranej talii, znajdź i kliknij przycisk "Dodaj nową fiszkę" (lub podobny) (US-010, KA-1).
    [SCREENSHOT_PL_03_przycisk_dodaj_manualnie_PNG]
2.  Pojawi się formularz z dwoma polami tekstowymi (US-010, KA-2):
    *   **Przód:** Tutaj wpisz pytanie, termin lub część informacji, którą chcesz zapamiętać. Limit znaków: 200 (FR-021).
    *   **Tył:** Tutaj wpisz odpowiedź, definicję lub drugą część informacji. Limit znaków: 500 (FR-021).
    [SCREENSHOT_PL_03_formularz_manualnego_dodawania_PNG]
    Aplikacja powinna informować Cię o zbliżaniu się do limitu znaków lub jego przekroczeniu (US-010, KA-3).
3.  Po wypełnieniu obu pól, kliknij przycisk "Zapisz" (lub podobny).
4.  Nowa fiszka zostanie utworzona, zapisana w bazie danych, powiązana z bieżącą talią i Twoim profilem (oznaczona jako "manual") (FR-021, US-010, KA-4). Dla nowej fiszki zostanie również zainicjalizowany stan w systemie powtórek FSRS.
5.  Nowo utworzona fiszka od razu pojawi się na liście fiszek w talii (US-010, KA-5).
6.  Pamiętaj, że zarówno pole "Przód", jak i "Tył" muszą być wypełnione. Próba zapisania fiszki z pustym którymkolwiek z tych pól powinna skutkować komunikatem o błędzie (US-010, KA-6).

### Przeglądanie fiszek w talii

Po otwarciu talii zobaczysz listę wszystkich fiszek, które się w niej znajdują (FR-022, US-011, KA-1). Dla każdej fiszki na liście powinien być widoczny przynajmniej tekst przedniej strony (lub jego fragment), a opcjonalnie także fragment tekstu tylnej strony (US-011, KA-2). [SCREENSHOT_PL_03_lista_fiszek_w_talii_przyklad_PNG]

Jeśli lista fiszek jest długa i nie mieści się w całości na ekranie, powinna być możliwość jej przewijania (US-011, KA-3).

### Edycja istniejącej fiszki

Znalazłeś błąd w fiszce lub chcesz ją zaktualizować? Możesz to zrobić w każdej chwili.

1.  Na liście fiszek w talii, znajdź fiszkę, którą chcesz zmodyfikować. Przy każdej fiszce powinna znajdować się opcja edycji (np. przycisk "Edytuj" lub ikona ołówka) (FR-023, US-012, KA-1).
    [SCREENSHOT_PL_03_przycisk_edytuj_fiszke_PNG]
2.  Po kliknięciu opcji edycji, otworzy się formularz identyczny jak przy tworzeniu nowej fiszki, ale pola "Przód" i "Tył" będą już wypełnione aktualną treścią wybranej fiszki (US-012, KA-2).
    [SCREENSHOT_PL_03_formularz_edycji_fiszki_PNG]
3.  Możesz dowolnie modyfikować tekst w obu polach, pamiętając o limitach znaków (200 dla przodu, 500 dla tyłu) (US-012, KA-3).
4.  Po dokonaniu zmian, kliknij przycisk "Zapisz". Zmiany zostaną zapisane w bazie danych dla tej fiszki (US-012, KA-4).
5.  Zaktualizowana treść fiszki będzie od razu widoczna na liście fiszek (US-012, KA-5).
6.  **Ważne:** Edycja fiszki resetuje jej stan w systemie powtórek FSRS (US-012, KA-6). Oznacza to, że system potraktuje ją jak nową fiszkę przy planowaniu kolejnych powtórek.

### Usuwanie fiszki

Jeśli dana fiszka nie jest Ci już potrzebna, możesz ją usunąć z talii.

1.  Na liście fiszek w talii, znajdź fiszkę, którą chcesz usunąć. Przy każdej fiszce powinna znajdować się opcja usunięcia (np. przycisk "Usuń" lub ikona kosza) (FR-024, US-013, KA-1).
    [SCREENSHOT_PL_03_przycisk_usun_fiszke_PNG]
2.  Ze względów bezpieczeństwa, przed ostatecznym usunięciem fiszki aplikacja wyświetli monit z prośbą o potwierdzenie (US-013, KA-2).
    [SCREENSHOT_PL_03_potwierdzenie_usuniecia_fiszki_PNG]
3.  Jeśli jesteś pewien, potwierdź usunięcie.
4.  Fiszka oraz jej stan w systemie FSRS zostaną trwale usunięte z bazy danych (US-013, KA-3).
5.  Usunięta fiszka zniknie z listy fiszek w talii (US-013, KA-4). 