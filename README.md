# 10xCards

[![Project Status: MVP](https://img.shields.io/badge/status-MVP-green)](https://shields.io/) <!-- Placeholder: Update if status changes -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Placeholder: Update with actual license -->

## Table of Contents

1.  [Project Background](#project-background)
2.  [Project Description](#project-description)
3.  [Tech Stack](#tech-stack)
4.  [Getting Started Locally](#getting-started-locally)
5.  [Available Scripts](#available-scripts)
6.  [User Guide](#user-guide)
7.  [Project Scope (MVP)](#project-scope-mvp)
8.  [Project Status](#project-status)
9.  [License](#license)

## Project Background

This project was developed by a PHP programmer, primarily experienced with the Symfony framework. It was created entirely with the assistance of AI as part of the "10xDevs" course.

The choice of Python, Tkinter, and ttkbootstrap for the technology stack was deliberate. The primary goal was to serve as a proof of concept: to demonstrate that it's possible to build a functional desktop application using Large Language Models (LLMs) even without extensive prior experience in the specific programming language (having only written simple Python scripts before) or the UI frameworks (with no prior experience in Tkinter or ttkbootstrap, and coming from a web development background).

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

2.  **Ensure you are using Python 3.13:**
    ```bash
    # Check current version
    python3 --version
    
    # If the version is different from 3.13, make sure you have version 3.13 installed
    # and use the full path to Python 3.13, e.g.:
    # /usr/local/bin/python3.13 or python3.13
    ```

3.  **Install tkinter (if not already installed):**
    ```bash
    # On macOS with Homebrew
    brew install python-tk
    ```

4.  **Set up a virtual environment (Recommended):**
    ```bash
    # Use the specific Python 3.13 version
    python3.13 -m venv 10xCards
    source 10xCards/bin/activate # On Windows use `10xCards\Scripts\activate`
    
    # Check if Python 3.13 is used in the virtual environment
    python --version
    ```

5.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Install development dependencies (Optional, for contributing/testing):**
    ```bash
    pip install -r requirements-dev.txt
    ```

7.  **Configure AI Provider:**
    *   Obtain an API key from [Openrouter.ai](https://openrouter.ai/).
    *   The API key is configured within the application after creating a user profile and logging in.
    *   Navigate to the user settings panel to enter or update your OpenRouter API key.
    *   *(Detailed instructions on accessing the settings panel and managing the API key can be found within the application after login.)*

8.  **Run the application:**
    ```bash
    python src/main.py
    ```

## Available Scripts

*   **Run the application:** `python src/main.py`
*   **Format code (using black):** `make format` (formats `src/` and `tests/`)
*   **Lint code (using flake8):** `make lint` (lints `src/` and `tests/`)
*   **Run static type checking (using mypy):** `make check` (type checks `src/` and `tests/`)
*   **Run unit tests (pytest):** `make test` (runs tests in `tests/unit/`)
*   **Run unit tests with coverage (pytest-cov):** `make test-coverage` (HTML report in `htmlcov/`)
*   **Run behavioral tests (behave):** `make test-bdd` (runs tests in `tests/behavioral/`)
*   **Clean up temporary files:** `make clean`
*   **Run all formatting, linting, type checking, unit and behavioral tests:** `make all`

## User Guide

A detailed user guide to help you make the most of 10xCards is available here:

*   🇵🇱 **[User Guide (Polish)](docs/user_guide_pl/index.md)**
*   🇬🇧 *User Guide (English) - in progress...*

We encourage you to read it to learn more about all the features!

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
