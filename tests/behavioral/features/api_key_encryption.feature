Feature: API Key Encryption and Decryption
  Background:
    Given the CryptoManager is available

  Scenario: Successfully encrypt and decrypt an API key
    Given a sample API key "my_super_secret_api_key_123!@#ABC"
    When the API key is encrypted
    And the encrypted API key is decrypted
    Then the decrypted API key should match the original sample API key

  Scenario: Successfully encrypt and decrypt an API key with special characters
    Given a sample API key "key_with_special_chars_&*()[]{}|\;:,'"<>.?/~`"
    When the API key is encrypted
    And the encrypted API key is decrypted
    Then the decrypted API key should match the original sample API key

  Scenario: Attempt to decrypt an invalid or tampered key
    Given a sample API key "another_key_for_testing_tampering"
    When the API key is encrypted
    And the encrypted API key is tampered with
    Then attempting to decrypt the tampered key should raise an error
