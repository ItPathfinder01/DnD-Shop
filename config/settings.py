import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))

TESTDATA_DIR = os.path.join(os.path.dirname(__file__), "..", "testdata")
