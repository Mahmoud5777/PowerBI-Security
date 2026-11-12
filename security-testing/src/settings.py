
import os
from pathlib import Path


# Project directories
SECURITY_TESTING_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SECURITY_TESTING_DIR.parent

# Configuration files
AUTHORIZATION_MATRIX_PATH = (
    REPOSITORY_ROOT / "contracts" / "authorization_matrix.csv"
)

TEST_CASES_PATH = SECURITY_TESTING_DIR / "config" / "test_cases.csv"

MOCK_VISIBLE_REGIONS_PATH = (
    SECURITY_TESTING_DIR / "config" / "mock_visible_regions.csv"
)

# Reports directory
REPORTS_DIR = SECURITY_TESTING_DIR / "reports"

# Adapter configuration
ADAPTER_MODE = os.getenv(
    "SECURITY_ADAPTER",
    "mock"
).strip().lower()

SUPPORTED_ADAPTERS = {"mock", "powerbi"}

