Feature: User Profile Management
  As an application user
  I want to manage my user profile
  So that I can use the application with my personal settings

  Background:
    Given the database is empty

  Scenario: Creating a new user profile
    When I create a user profile with:
      | username | password  | api_key     |
      | testuser | pass123  | sk-test-key  |
    Then the user profile should be created successfully
    And I should be able to find the user by username "testuser"

  Scenario: Attempting to create a duplicate username
    Given there is a user with username "testuser"
    When I create a user profile with:
      | username | password  | api_key     |
      | testuser | pass456  | sk-test-key2 |
    Then I should get a username already exists error

  Scenario: Updating user profile
    Given there is a user with username "oldname"
    When I update the user profile with:
      | username | password      | api_key         |
      | newname  | newpass123   | sk-new-test-key |
    Then the user profile should be updated successfully
    And I should be able to find the user by username "newname"
    And I should not be able to find the user by username "oldname"

  Scenario: Deleting user profile
    Given there is a user with username "testuser"
    When I delete the user profile
    Then the user profile should be deleted successfully
    And I should not be able to find the user by username "testuser" 