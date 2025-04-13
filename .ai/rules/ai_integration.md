# AI Integration (Openrouter.ai) Rules

-   **Encapsulation:**
    -   Implement client for communicating with the Openrouter.ai API using litellm in `src/CardManagement/infrastructure/api_clients/openrouter/`. This client handles HTTP requests, authentication (API key), and basic response parsing using litellm module.
    -   Create an Application Service (e.g., `src/CardManagement/application/services/AIService.py`) that uses the client. This service coordinates the AI interaction, prepares data, handles higher-level logic, and translates responses into domain/DTO objects.
-   **Prompts:** Store AI prompts as constants (e.g., `FLASHCARD_GENERATION_PROMPT`) within the `AIService` or a dedicated configuration module imported by the service. Keep prompts clear and well-defined.
-   **Error Handling:**
    -   The API client should handle basic network errors (e.g., connection issues) and raise specific custom exceptions (e.g., `AIAPIConnectionError`, `AIAPIAuthError`).
    -   The `AIService` should catch client exceptions and potentially raise its own, more abstract exceptions (e.g., `FlashcardGenerationError`) if needed by the calling presenter.
    -   Handle specific API error responses (e.g., rate limits, invalid requests) returned by Openrouter.ai and translate them into appropriate exceptions or return values.
    -   Log all requests and responses (or relevant summaries) to the AI API for debugging purposes, being mindful of potentially sensitive data in prompts or responses.
-   **API Keys:** Manage the Openrouter.ai API key securely. Do not hardcode it directly in the source code. Use environment variables or a configuration file mechanism (loaded via `Shared` infrastructure) to provide the key to the API client.