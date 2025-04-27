Feature: Profile Management UI
  As an application user
  I want to manage my user profiles through the UI
  So that I can create, select, and log into profiles

  Background:
    Given the application is started

  Scenario: Creating a new user profile (US-001)
    When I click the "Dodaj nowy profil" button
    And I enter "newuser" as username
    And I confirm creation
    Then I should see a toast "Profil newuser został utworzony."
    And the profile list should include "newuser"

  Scenario: Not allowing duplicate profile creation (US-001)
    Given there is a profile "existinguser" without password
    When I click the "Dodaj nowy profil" button
    And I enter "existinguser" as username
    And I confirm creation
    Then I should see a toast "Nazwa profilu existinguser już istnieje."
    And the profile list should include "existinguser"

  Scenario: Selecting existing profile without password (US-002)
    Given there is a profile "nopassuser" without password
    When I activate the profile "nopassuser"
    Then I should be navigated to the deck list for "nopassuser"

  Scenario: Selecting existing profile with password (US-002)
    Given there is a profile "passuser" with password "secret"
    When I activate the profile "passuser"
    Then I should be navigated to the login view for "passuser"

  Scenario: Log in with correct password (US-004)
    Given there is a profile "passuser2" with password "secret"
    When I activate the profile "passuser2"
    And I enter password "secret"
    And I confirm login
    Then I should be navigated to the deck list for "passuser2"

  Scenario: Log in with incorrect password (US-004)
    Given there is a profile "passuser3" with password "secret"
    When I activate the profile "passuser3"
    And I enter password "wrong"
    And I confirm login
    Then I should see an error "Nieprawidłowe hasło."
    And the password input should be cleared

  # US-003: Setting or removing password for a profile
  Scenario: Setting a new password for a profile (US-003)
    Given there is a profile "newpassuser" without password
    When I choose change password for "newpassuser"
    And I enter new password "NewSecret123" and confirm
    Then the user profile "newpassuser" should be password protected
    And I should see a toast "Hasło zostało ustawione."

  Scenario: Removing password for a profile (US-003)
    Given there is a profile "removepassuser" with password "OldSecret"
    When I choose change password for "removepassuser"
    And I enter new password "" and confirm
    Then the user profile "removepassuser" should not be password protected
    And I should see a toast "Hasło zostało usunięte."
