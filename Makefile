# Makefile for 10xCards Project

# Activate virtual environment - adjust if your shell/setup differs slightly
# Using .SHELLFLAGS = -c stops Make from trying to use /bin/sh for every line
SHELL=/bin/bash
.SHELLFLAGS = -ec

# Define directories
SRC_DIR = src
TEST_DIR = tests

# Phony targets don't represent files
.PHONY: all install format lint check test clean

# Default target
all: lint check test

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
	pytest $(TEST_DIR)
	@echo "Tests complete."

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -delete
	@echo "Cleanup complete." 