import os
import sys
import builtins

# Get absolute path to the project root directory
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Add project root to Python path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Add 'src' directory to Python path
# This allows imports without 'src.' prefix in tests (like in production code)
src_path = os.path.join(PROJECT_ROOT, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Monkey patch exceptions to make them work both with and without src. prefix
try:
    # AuthenticationError for session_service
    from src.Shared.domain.errors import AuthenticationError as SrcAuthError
    from Shared.domain.errors import AuthenticationError as DirectAuthError

    # Make sure the same class is used regardless of import style
    if SrcAuthError is not DirectAuthError:
        builtins.AuthenticationError = SrcAuthError

    # OpenRouter exceptions
    from src.CardManagement.infrastructure.api_clients.openrouter.exceptions import (
        AIAPIAuthError as SrcAIAPIAuthError,
        AIAPIConnectionError as SrcAIAPIConnectionError,
        AIAPIRequestError as SrcAIAPIRequestError,
        AIAPIServerError as SrcAIAPIServerError,
        AIRateLimitError as SrcAIRateLimitError,
        FlashcardGenerationError as SrcFlashcardGenerationError,
    )
    from CardManagement.infrastructure.api_clients.openrouter.exceptions import (
        AIAPIAuthError as DirectAIAPIAuthError,
        AIAPIConnectionError as DirectAIAPIConnectionError,
        AIAPIRequestError as DirectAIAPIRequestError,
        AIAPIServerError as DirectAIAPIServerError,
        AIRateLimitError as DirectAIRateLimitError,
        FlashcardGenerationError as DirectFlashcardGenerationError,
    )

    # Make sure the same classes are used regardless of import style
    if SrcAIAPIAuthError is not DirectAIAPIAuthError:
        builtins.AIAPIAuthError = SrcAIAPIAuthError
    if SrcAIAPIConnectionError is not DirectAIAPIConnectionError:
        builtins.AIAPIConnectionError = SrcAIAPIConnectionError
    if SrcAIAPIRequestError is not DirectAIAPIRequestError:
        builtins.AIAPIRequestError = SrcAIAPIRequestError
    if SrcAIAPIServerError is not DirectAIAPIServerError:
        builtins.AIAPIServerError = SrcAIAPIServerError
    if SrcAIRateLimitError is not DirectAIRateLimitError:
        builtins.AIRateLimitError = SrcAIRateLimitError
    if SrcFlashcardGenerationError is not DirectFlashcardGenerationError:
        builtins.FlashcardGenerationError = SrcFlashcardGenerationError

except ImportError:
    pass  # Skip if imports not available yet
