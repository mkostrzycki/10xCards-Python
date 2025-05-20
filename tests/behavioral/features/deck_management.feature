Feature: Zarządzanie taliami fiszek
  Jako użytkownik
  Chcę zarządzać moimi taliami fiszek
  Aby efektywnie organizować materiały do nauki

  Background:
    Given jestem zalogowany jako "TestUser"
    And mam utworzoną talię "Testowa Talia"

  Scenario: Tworzenie nowej talii
    When kliknę przycisk "Nowa Talia"
    And wprowadzę nazwę talii "Python Podstawy"
    And kliknę przycisk "Utwórz"
    Then zobaczę komunikat "Utworzono nową talię: Python Podstawy"
    And zobaczę talię "Python Podstawy" na liście talii

  Scenario: Usuwanie talii
    When kliknę na talię "Testowa Talia"
    And kliknę przycisk "Usuń Tę Talię"
    And potwierdzę usunięcie talii
    Then zobaczę komunikat "Talia 'Testowa Talia' została pomyślnie usunięta."
    And nie zobaczę talii "Testowa Talia" na liście talii

  Scenario: Anulowanie usuwania talii
    When kliknę na talię "Testowa Talia"
    And kliknę przycisk "Usuń Tę Talię"
    And anuluję usunięcie talii
    Then nadal zobaczę talię "Testowa Talia" na liście talii
