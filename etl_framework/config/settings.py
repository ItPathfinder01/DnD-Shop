import os  # import the built-in module for interacting with the operating system (env variables, file paths)

# Read the API base URL from the environment variable "API_BASE_URL".
# If the variable is not set, fall back to "http://localhost:8000" (local DnD Shop server).
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Read the request timeout (in seconds) from the environment variable "API_TIMEOUT".
# os.getenv() always returns a string, so we wrap it with int() to convert it to a number.
# Default value is 10 seconds — enough for a local server to respond.
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))

# Build the absolute path to the "testdata" folder.
# __file__ is the path to this file (settings.py).
# os.path.dirname(__file__) gives the folder that contains settings.py → "config/"
# os.path.join(..., "..", "testdata") goes one level up and into "testdata/"
# This way the path works correctly regardless of where pytest is launched from.
TESTDATA_DIR = os.path.join(os.path.dirname(__file__), "..", "testdata")

SUPERADMIN_EMAIL = os.getenv("SUPERADMIN_EMAIL", "demiurg@test.com")
SUPERADMIN_PASSWORD = os.getenv("SUPERADMIN_PASSWORD", "demiurg")
