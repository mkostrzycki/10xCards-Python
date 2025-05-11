# Makefile for 10xCards Project

# Activate virtual environment - adjust if your shell/setup differs slightly
# Using .SHELLFLAGS = -c stops Make from trying to use /bin/sh for every line
SHELL=/bin/bash
.SHELLFLAGS = -ec

# Define directories
SRC_DIR = src
TEST_DIR = tests

# Phony targets don't represent files
.PHONY: all install format lint check test test-bdd clean

# Default target
all: lint check test test-bdd

# Install dependencies
install: requirements-dev.txt
	@echo "Installing development dependencies..."
	source .venv/bin/activate && \
	pip3 install -r requirements-dev.txt
	@echo "Installation complete."

# Format code
format: 
	@echo "Formatting code with black..."
	source .venv/bin/activate && \
	black $(SRC_DIR) $(TEST_DIR)
	@echo "Formatting complete."

# Lint code
lint:
	@echo "Linting code with flake8..."
	source .venv/bin/activate && \
	flake8 $(SRC_DIR) $(TEST_DIR)
	@echo "Linting complete."

# Type check code
check:
	@echo "Type checking with mypy..."
	source .venv/bin/activate && \
	mypy $(SRC_DIR) $(TEST_DIR)
	@echo "Type checking complete."

# Run tests
test:
	@echo "Running tests with pytest..."
	source .venv/bin/activate && \
	pytest $(TEST_DIR)/unit
	@echo "Tests complete."

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage analysis..."
	source .venv/bin/activate && \
	pytest $(TEST_DIR)/unit --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated. View detailed HTML report in htmlcov/index.html"

# Run behavioral tests
test-bdd:
	@echo "Running behavioral tests with behave..."
	source .venv/bin/activate && \
	behave $(TEST_DIR)/behavioral
	@echo "Behavioral tests complete."

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .coverage htmlcov
	@echo "Cleanup complete."
