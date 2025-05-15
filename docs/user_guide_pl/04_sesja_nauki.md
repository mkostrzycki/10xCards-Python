# Sesja Nauki (Study Session) 🧠

Celem 10xCards jest nie tylko tworzenie fiszek, ale przede wszystkim efektywna nauka. Służy do tego dedykowana Sesja Nauki, która wykorzystuje algorytm powtórek rozłożonych w czasie FSRS (Free Spaced Repetition Scheduler), aby optymalnie zarządzać Twoimi powtórkami.

## Rozpoczynanie sesji nauki

Aby rozpocząć naukę z wybranej talii:

1.  Upewnij się, że masz wybraną talię, z której chcesz się uczyć. Sesję nauki możesz zazwyczaj rozpocząć z poziomu listy talii lub widoku listy fiszek w danej talii (US-014, KA-1).
2.  Poszukaj przycisku lub opcji "Rozpocznij naukę" (lub podobnej) i kliknij ją (FR-025, US-014, KA-2).
    [SCREENSHOT_PL_04_przycisk_rozpocznij_nauke_PNG]
3.  Aplikacja skomunikuje się z biblioteką `Py-FSRS`, aby określić, które fiszki z tej talii są gotowe do powtórki i w jakiej kolejności powinny zostać wyświetlone (FR-026, US-014, KA-3).
4.  Jeśli algorytm FSRS wskaże, że w danym momencie nie ma żadnych fiszek wymagających powtórki w tej talii, otrzymasz stosowny komunikat (np. "Gratulacje! Na tę chwilę nie ma żadnych fiszek do nauki w tej talii.") (US-014, KA-5).
    [SCREENSHOT_PL_04_brak_fiszek_do_nauki_PNG]
5.  Jeśli są fiszki do nauki, zostaniesz przeniesiony do interfejsu Sesji Nauki, gdzie wyświetlona zostanie strona przednia pierwszej fiszki (US-014, KA-4).

## Interfejs nauki (z FSRS)

Interfejs Sesji Nauki jest zaprojektowany tak, aby skupić Twoją uwagę na procesie uczenia się.

[SCREENSHOT_PL_04_interfejs_sesji_nauki_przod_PNG]

1.  **Wyświetlanie przodu fiszki:** Na ekranie zobaczysz stronę przednią (pytanie, termin) aktualnie powtarzanej fiszki (FR-027, US-015, KA-1).
2.  **Odsłanianie tyłu fiszki:** Zastanów się nad odpowiedzią. Gdy będziesz gotowy, kliknij przycisk "Odwróć", "Pokaż odpowiedź" lub podobny, aby odsłonić stronę tylną fiszki (FR-028, US-015, KA-2).
    [SCREENSHOT_PL_04_przycisk_odwroc_PNG]
3.  Po odsłonięciu, na ekranie pojawi się również strona tylna (odpowiedź, definicja) fiszki (US-015, KA-3).
    [SCREENSHOT_PL_04_interfejs_sesji_nauki_tyl_PNG]

## Ocenianie odpowiedzi (Again, Hard, Good, Easy)

Teraz kluczowy moment – samoocena. Twoja ocena jest niezbędna, aby algorytm FSRS mógł efektywnie zaplanować kolejną powtórkę tej fiszki.

Po odsłonięciu strony tylnej, pojawią się cztery przyciski oceny (FR-029, US-015, KA-4):
[SCREENSHOT_PL_04_przyciski_oceny_PNG]

*   **Again (Jeszcze raz):** Wybierz tę opcję, jeśli nie pamiętałeś odpowiedzi lub odpowiedziałeś zupełnie niepoprawnie. Fiszka pojawi się ponownie wkrótce, prawdopodobnie jeszcze w tej samej sesji nauki.
*   **Hard (Trudne):** Wybierz, jeśli odpowiedź sprawiła Ci dużą trudność, przypomniałeś ją sobie z trudem lub była częściowo niepoprawna. Fiszka wróci do powtórki wcześniej niż w przypadku oceny "Good".
*   **Good (Dobrze):** Wybierz, jeśli odpowiedziałeś poprawnie, ale wymagało to pewnego wysiłku. Jest to standardowa, "dobra" odpowiedź.
*   **Easy (Łatwe):** Wybierz, jeśli odpowiedź była dla Ciebie bardzo łatwa i nie sprawiła żadnego problemu. Fiszka wróci do powtórki znacznie później.

Po kliknięciu jednego z przycisków oceny (US-015, KA-5):

1.  Twoja ocena zostanie przekazana do biblioteki `Py-FSRS` (FR-030).
2.  Algorytm FSRS zaktualizuje stan powtórki dla tej fiszki, planując jej następne pojawienie się.
3.  Aplikacja automatycznie pobierze kolejną fiszkę do powtórki z FSRS i wyświetli jej stronę przednią, kontynuując cykl (US-015, KA-6).

## Zakończenie sesji

Sesja nauki trwa tak długo, jak długo algorytm FSRS dostarcza kolejne fiszki do powtórki.

*   Gdy algorytm FSRS uzna, że nie ma więcej fiszek do pokazania w danym momencie dla tej talii, sesja nauki zakończy się automatycznie (FR-031, US-015, KA-7).
*   Zostaniesz o tym poinformowany (np. komunikatem "To wszystko na dziś w tej talii!") i prawdopodobnie wrócisz do widoku listy fiszek lub listy talii.
    [SCREENSHOT_PL_04_koniec_sesji_PNG]

Możesz również mieć możliwość przerwania sesji nauki w dowolnym momencie, np. poprzez przycisk "Zakończ sesję". Pamiętaj jednak, że regularne kończenie pełnych sesji jest kluczowe dla efektywności metody spaced repetition. 