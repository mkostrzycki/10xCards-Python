# 10xCards

[![Project Status: MVP](https://img.shields.io/badge/status-MVP-green)](https://shields.io/) <!-- Placeholder: Update if status changes -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Placeholder: Update with actual license -->

## Table of Contents

1.  [Project Description](#project-description)
2.  [Tech Stack](#tech-stack)
3.  [Getting Started Locally](#getting-started-locally)
4.  [Available Scripts](#available-scripts)
5.  [Project Scope (MVP)](#project-scope-mvp)
6.  [Project Status](#project-status)
7.  [License](#license)

## Project Description

10xCards is a desktop application (MVP for macOS) designed to help professionals learn new skills efficiently using flashcards. It leverages AI (GPT-4o mini via Openrouter.ai) to automatically generate flashcards from user-provided text and integrates the FSRS (Free Spaced Repetition Scheduler) algorithm via `Py-FSRS` for optimized learning sessions.

The application aims to solve the time-consuming problem of manually creating high-quality flashcards, offering a streamlined way to turn notes and materials into effective learning tools. It supports multiple user profiles on a single machine with optional password protection (using bcrypt hashing) and stores all data locally in an SQLite database.

## Tech Stack

**Frontend:**
*   Python 3 (`Tkinter`, `ttkbootstrap`)

**Backend:**
*   Python 3
*   SQLite (local database)
*   `bcrypt` (password hashing)
*   `fsrs` (spaced repetition algorithm)
*   `requests` (API communication)

**AI Integration:**
*   Openrouter.ai (for GPT-4o mini access)
*   litellm (communication with Openrouter.ai)

**Development & Testing:**
*   `pytest` (Unit/Integration Testing)
*   `behave` (Behavioral Testing)
*   `pytest-mock`, `requests-mock` (Mocking)
*   `black` (Code Formatting)
*   `flake8` (Linting)
*   `mypy` (Static Typing)

**CI/CD:**
*   GitHub Actions

## Getting Started Locally

1.  **Clone the repository:**
    ```bash
    git clone <repository-url> # Replace <repository-url> with the actual URL
    cd 10xCards_Python # Or your project directory name
    ```

2.  **Set up a virtual environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install development dependencies (Optional, for contributing/testing):**
    ```bash
    pip install -r requirements-dev.txt
    ```

5.  **Configure AI Provider:**
    *   Obtain an API key from [Openrouter.ai](https://openrouter.ai/).
    *   Set the API key as an environment variable:
        ```bash
        export OPENROUTER_API_KEY='your_api_key_here'
        # On Windows use `set OPENROUTER_API_KEY=your_api_key_here` or set it system-wide
        ```
    *   *(Note: The exact method for providing the API key might differ; check the application's configuration.)*

6.  **Run the application:**
    ```bash
    python src/main.py # Assuming src/main.py is the entry point
    ```
    *(Note: The exact run command might differ.)*

## Available Scripts

*   **Run the application:** `python src/main.py` *(Assumption)*
*   **Run unit/integration tests:** `pytest`
*   **Run behavioral tests:** `behave`
*   **Check code formatting:** `black --check .`
*   **Format code:** `black .`
*   **Lint code:** `flake8 .`
*   **Run static type checking:** `mypy src` *(Assumption: main source code is in `src`)*

## Project Scope (MVP)

**Included in MVP:**

*   **Platform:** macOS Desktop Application
*   **Core Features:**
    *   Multi-user profile management with optional password protection (bcrypt).
    *   Deck creation and management (create, delete, list).
    *   AI-powered flashcard generation (GPT-4o mini) from text (1k-10k chars) with review/accept/edit/reject workflow.
    *   Manual flashcard creation, editing, and deletion (text only, front/back).
    *   Spaced repetition learning sessions powered by FSRS (`Py-FSRS`) with Again/Hard/Good/Easy grading.
*   **Data Storage:** Local SQLite database.
*   **UI:** Python with Tkinter/ttkbootstrap.
*   **Logging:** AI communication, FSRS errors, DB errors, general exceptions.

**NOT Included in MVP:**

*   Windows or Linux support.
*   Advanced/custom SRS algorithms.
*   Import/Export features (e.g., from Anki, CSV, PDF).
*   Deck/card sharing or online synchronization.
*   Mobile applications.
*   Rich text formatting (Markdown, HTML) or media (images, audio) in flashcards.
*   Moving flashcards between decks.
*   Advanced learning statistics or visualizations.
*   Social/community features.
*   Global search functionality.

## Project Status

This project is currently in the **Minimum Viable Product (MVP)** stage. Core functionalities are being developed based on the defined scope.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. *(Placeholder: Ensure a LICENSE file exists and reflects the correct license)*
