import os
import sys

# Get the project root directory (3 levels up from this file)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Get the src directory path
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

# Add the src directory to the Python path
# This allows tests to import modules from src without the 'src.' prefix
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
