import sys
import os

# Determine the project root directory.
# __file__ in environment.py is tests/behavioral/environment.py
# Project root is two levels up from the directory of this file.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Determine the path to the 'src' directory
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

# Add the 'src' directory to sys.path if it's not already there.
# This allows behave steps to import modules from 'src' as top-level (e.g., 'from Shared...').
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# You can add further global setup for your tests here, for example:
# def before_all(context):
#     print("Starting Behave tests...")
#
# def after_all(context):
#     print("Finished Behave tests.")
