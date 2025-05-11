from behave import given, when, then
from cryptography.fernet import InvalidToken

from src.Shared.infrastructure.security.crypto import CryptoManager


@given("the CryptoManager is available")
def step_impl_crypto_manager_available(context):
    context.crypto_manager = CryptoManager()
    assert context.crypto_manager is not None, "CryptoManager could not be initialized"


@given('a sample API key "{api_key}"')
def step_impl_sample_api_key(context, api_key):
    context.raw_api_key = api_key


@when("the API key is encrypted")
def step_impl_encrypt_api_key(context):
    assert hasattr(context, 'raw_api_key'), "Raw API key not set in context"
    assert hasattr(context, 'crypto_manager'), "CryptoManager not set in context"
    context.encrypted_api_key = context.crypto_manager.encrypt_api_key(context.raw_api_key)
    assert isinstance(context.encrypted_api_key, bytes), "Encrypted key should be bytes"


@when("the encrypted API key is decrypted")
def step_impl_decrypt_api_key(context):
    assert hasattr(context, 'encrypted_api_key'), "Encrypted API key not set in context"
    assert hasattr(context, 'crypto_manager'), "CryptoManager not set in context"
    context.decrypted_api_key = context.crypto_manager.decrypt_api_key(context.encrypted_api_key)


@when("the encrypted API key is tampered with")
def step_impl_tamper_key(context):
    assert hasattr(context, 'encrypted_api_key'), "Encrypted API key not set in context"
    # Tamper the key by changing some bytes
    # For example, flip some bits in the middle of the key
    key_list = list(context.encrypted_api_key)
    if len(key_list) > 10:
        key_list[5] = key_list[5] ^ 0xFF  # Flip bits of a byte
    else:
        # If key is too short, just append a byte (less ideal but makes it invalid)
        key_list.append(0x00)
    context.tampered_key = bytes(key_list)
    assert context.tampered_key != context.encrypted_api_key, "Key was not tampered"


@then("the decrypted API key should match the original sample API key")
def step_impl_assert_keys_match(context):
    assert hasattr(context, 'raw_api_key'), "Raw API key not set in context"
    assert hasattr(context, 'decrypted_api_key'), "Decrypted API key not set in context"
    assert context.decrypted_api_key == context.raw_api_key, f"Decrypted key '{context.decrypted_api_key}' does not match original '{context.raw_api_key}'"


@then("attempting to decrypt the tampered key should raise an error")
def step_impl_assert_decryption_error(context):
    assert hasattr(context, 'tampered_key'), "Tampered key not set in context"
    assert hasattr(context, 'crypto_manager'), "CryptoManager not set in context"
    try:
        context.crypto_manager.decrypt_api_key(context.tampered_key)
        # If no exception is raised, the test should fail
        assert False, "Decryption of tampered key did not raise an error as expected"
    except InvalidToken:
        # This is the expected exception from Fernet for invalid tokens
        pass
    except Exception as e:
        # Handle other potential exceptions if necessary, but InvalidToken is most specific
        assert False, f"Decryption of tampered key raised an unexpected error: {type(e).__name__} - {str(e)}"
