# Dependency Management Rules (requirements.txt)

-   **File:** Use `requirements.txt` for main application dependencies.
-   **Pinning:** Pin exact versions of all dependencies using `==` (e.g., `requests==2.28.1`). Avoid loose constraints (`>=`, `~=`) unless strictly necessary and justified.
-   **Development Dependencies:** Use a separate file, e.g., `requirements-dev.txt`, for development-only tools (like `pytest`, `flake8`, `black`, `behave`, `mypy`, `pytest-cov`, `requests-mock`). This file should typically include `-r requirements.txt`.
-   **Updates:** Update dependencies deliberately and test thoroughly afterwards.
-   **Cleanliness:** Keep the files sorted alphabetically and remove unused dependencies.
-   **Virtual Environments:** Always use a virtual environment (`venv`, `conda`, etc.) for development and installation to isolate project dependencies. 