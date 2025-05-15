## 1. Service Description

`OpenRouterService` is a thin, reusable layer that wraps the OpenRouter.ai Chat Completion REST API via the `litellm` SDK.  
It hides HTTP specifics, enforces project-wide safety & logging rules, and exposes **domain-centric** methods (e.g. `generate_flashcards`) to the rest of the CardManagement slice.

Key goals:
1. Provide a **single entry-point** for all LLM interactions.
2. Keep the UI/business layers agnostic of HTTP, tokens, retries & billing.
3. Centralise prompt construction, model parameters and response validation.
4. Surface **typed results** and **custom exceptions** only.
5. Facilitate mocking in unit tests and playback in behavioural tests.

---

## 2. Constructor

```python
class OpenRouterService:
    def __init__(
        self,
        api_client: "OpenRouterAPIClient",
        session_service: SessionService,
        logger: logging.Logger,
        default_model: str = "gpt-4o-mini",
    ) -> None:
        """Create a new service instance.

        Args:
            api_client: Low-level HTTP client (defined below).
            session_service: Provides current user & therefore their API key.
            logger: Pre-configured application logger.
            default_model: Fallback model when caller does not specify one.
        """
```

* Inject all hard dependencies (respecting DDD-Lite & SOLID).
* `logger` comes from `Shared.infrastructure.logging`.

---

## 3. Public Methods & Attributes

| Method | Signature | Responsibility |
|--------|-----------|----------------|
| `chat_completion` | `(messages: list[ChatMessage], *, model: str | None = None, response_format: ResponseFormat | None = None, **params) -> ChatCompletionDTO` | Generic passthrough for advanced use-cases; validates response_format & serialises DTO. |
| `generate_flashcards` | `(raw_text: str, deck_id: int) -> list[FlashcardDTO]` | High-level helper that sends `FLASHCARD_GENERATION_PROMPT` and returns validated flashcard objects ready for persistence. |
| `explain_error` | `(exc: Exception) -> str` | Developer-friendly mapping of caught exceptions ⟶ human message (useful for UI toasts). |

> `ChatMessage`, `ResponseFormat` and `ChatCompletionDTO` are `@dataclass` DTOs located in `CardManagement.application.dtos`.

---

## 4. Private Methods & Attributes

| Name | Purpose |
|------|---------|
| `_build_default_params()` | Returns a dict with safe defaults: `{ "temperature": 0.5, "max_tokens": 1024 }`. |
| `_format_prompt(raw_text)` | Injects `raw_text` into constant `FLASHCARD_GENERATION_PROMPT`, returns list[ChatMessage] ready for the client. |
| `_parse_flashcard_response(json_str)` | Parses/validates AI JSON to `FlashcardDTO` list ( > raises `FlashcardGenerationError`). |
| `_get_user_api_key()` | Retrieves **plain** key for current session via `session_service.get_current_user()`. Raises `AIAPIAuthError` if missing. |
| `_handle_litellm_error(err)` | Normalises & re-raises as project-specific exception. |

---

## 5. Error Handling

| # | Scenario | Raised Exception | Mitigation |
|---|----------|-----------------|------------|
| 1 | Missing/invalid user API key | `AIAPIAuthError` | Prompt user to set key in profile settings. |
| 2 | Network connectivity / DNS | `AIAPIConnectionError` | Retry w/ exponential backoff (3 attempts) & log after final failure. |
| 3 | 4xx from OpenRouter (bad request, quota) | `AIAPIRequestError(code, msg)` | Surface to UI; include actionable hint. |
| 4 | 5xx from OpenRouter | `AIAPIServerError` | Retry 3×, then bubble up. |
| 5 | Rate-limit (HTTP 429) | `AIRateLimitError(retry_after)` | Service schedules retry or UI suggests waiting. |
| 6 | Invalid JSON in LLM answer | `FlashcardGenerationError("Invalid JSON schema …")` | Ask model again or fallback to manual creation. |

Each custom error inherits from `OpenRouterError` → `AppError` (per python_style rule).

---

## 6. Security Considerations

1. **Plain vs Hashed key** – key must be *retrievable*; therefore store **encrypted** (e.g. Fernet) not hashed.  
   * Migration script updates `Users.hashed_api_key` → `encrypted_api_key` storing `Fernet.encrypt(key.encode())`.  
   * Encryption key lives in `Shared.infrastructure.config.SECRET_KEY` loaded from `.env`.
2. **Transport** – enforce HTTPS; `litellm` does this by default.
3. **Logging** – never log raw keys or full prompts. Log only hashes of keys & prompt metadata (length, word count). Mask sensitive user data.
4. **Resource limits** – respect `max_tokens`, temperature caps; prevent prompt injection by validating `raw_text` length.

---

## 7. Step-by-Step Deployment Plan

### 7.1 Database Migration
1. Create SQL migration `V2__store_api_key_plain.sql` inside `infrastructure/persistence/sqlite/migrations/`:
   ```sql
   ALTER TABLE Users RENAME COLUMN hashed_api_key TO encrypted_api_key;
   -- back-fill will be handled by Python script using bcrypt check ⚠️
   ```
2. Add trigger to keep `updated_at` correct (reuse pattern from db-plan).

### 7.2 Shared Infrastructure
1. Add `Shared/infrastructure/config.py` with helper to read `.env` & expose `SECRET_KEY`.
2. Add `Shared/infrastructure/security/crypto.py` wrapping `Fernet` encrypt/decrypt.

### 7.3 OpenRouterAPIClient (`src/CardManagement/infrastructure/api_clients/openrouter/client.py`)
1. Wrap `litellm.completion()`; sign requests with header `Authorization: Bearer <key>`.
2. Accept explicit `api_key` per call (no globals) to remain stateless.
3. Map `litellm.exceptions` → custom exceptions.
4. Automatic retries/backoff using `tenacity` or manual loop.

#### Example Usage
```python
client = OpenRouterAPIClient(logger)
result = client.chat_completion(
    api_key=user_key,
    messages=[{"role": "system", "content": SYSTEM_MSG}, {"role": "user", "content": user_input}],
    model="gpt-4o-mini",
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "flashcards", "strict": True, "schema": FLASHCARD_SCHEMA},
    },
    temperature=0.3,
)
```

### 7.4 AIService (`src/CardManagement/application/services/ai_service.py`)
1. Inject `OpenRouterAPIClient` & `SessionService`.
2. Implement public methods as in section 3.
3. Keep `FLASHCARD_GENERATION_PROMPT` & `FLASHCARD_SCHEMA` constants at top of file.

### 7.5 UI Integration
1. Extend `AIGenerateView` workflow:
   * On "Generate" button click, call `ai_service.generate_flashcards()`.
   * Display progress spinner; then list DTOs for accept/edit/reject.
2. Remember to convert DTO → domain model via `FlashcardFactory` & persist via repository.

### 7.6 Profile Settings
1. Add "Set API key" dialog to `UserProfile` slice.
2. Validate key by calling `client.verify_key()` (simple `GET /models`).

### 7.7 Testing
1. Unit tests: mock `OpenRouterAPIClient` to return fixed JSON.
2. Behavioural tests: use `requests_mock` to fake OpenRouter responses.
3. Add `pytest` coverage expectations >= 90 % for new modules.

### 7.8 CI/CD
1. Add `pip install litellm>=1.66` to `requirements.txt` & lock file.
2. Run `black`, `flake8`, `mypy` on new code in GitHub Actions.
