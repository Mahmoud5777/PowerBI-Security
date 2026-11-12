from src import settings
import csv
import sys
from pathlib import Path

from src.reporter import ReportGenerator
from src.test_engine import SecurityTestEngine
from src.adapter_factory import create_adapter

# --------------------------------------------------
# Project paths
# --------------------------------------------------

MATRIX_PATH = settings.AUTHORIZATION_MATRIX_PATH
TEST_CASES_PATH = settings.TEST_CASES_PATH
MOCK_DATA_PATH = settings.MOCK_VISIBLE_REGIONS_PATH
REPORTS_PATH = settings.REPORTS_DIR


# --------------------------------------------------
# Load mock visible regions
# --------------------------------------------------

def load_mock_data(file_path: Path) -> dict[str, set[str]]:
    visible_regions: dict[str, set[str]] = {}

    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)

        required = {"UserPrincipalName", "RegionCode"}

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Invalid mock data CSV format")

        for row in reader:
            user = row["UserPrincipalName"].strip().lower()
            region = row["RegionCode"].strip().upper()

            if user and region:
                visible_regions.setdefault(user, set()).add(region)

    return visible_regions


# --------------------------------------------------
# Load test catalog
# --------------------------------------------------

def load_test_cases(file_path: Path) -> list[dict]:
    test_cases = []
    seen_test_ids = set()

    supported_scenarios = {
        "ALLOW",
        "DENY",
        "UNKNOWN_USER",
        "INACTIVE_USER",
        "MULTI_REGION",
    }

    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)

        required = {
            "TestId",
            "UserPrincipalName",
            "TargetRegion",
            "ScenarioType",
            "Description",
        }

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Invalid test catalog CSV format")

        for line_number, row in enumerate(reader, start=2):

            if any(row.get(field) is None for field in required):
                raise ValueError(
                    f"Invalid test case at line {line_number}: "
                    "missing CSV field"
                )

            test_id = row["TestId"].strip()
            user = row["UserPrincipalName"].strip()
            scenario = row["ScenarioType"].strip().upper()
            target = row["TargetRegion"].strip().upper() or None
            description = row["Description"].strip()

            if not test_id or not user or not description:
                raise ValueError(
                    f"Incomplete test case at line {line_number}"
                )

            if test_id in seen_test_ids:
                raise ValueError(
                    f"Duplicate TestId '{test_id}' "
                    f"at line {line_number}"
                )

            if scenario not in supported_scenarios:
                raise ValueError(
                    f"Unsupported scenario '{scenario}' "
                    f"at line {line_number}"
                )

            if scenario in {"ALLOW", "DENY"} and not target:
                raise ValueError(
                    f"TargetRegion is required for {scenario} "
                    f"at line {line_number}"
                )

            seen_test_ids.add(test_id)

            test_cases.append({
                "test_id": test_id,
                "user": user,
                "target_region": target,
                "scenario": scenario,
                "description": description,
            })

    return test_cases


# --------------------------------------------------
# Execute security tests
# --------------------------------------------------

def run_security_tests() -> int:
    try:
        print("=" * 55)
        print("       POWER BI AUTOMATED SECURITY TESTING")
        print("=" * 55)

        # Check required files
        required_files = {
            "Authorization matrix": MATRIX_PATH,
            "Test catalog": TEST_CASES_PATH,
        }

        if settings.ADAPTER_MODE == "mock":
            required_files["Mock visible regions"] = MOCK_DATA_PATH

        for name, path in required_files.items():
            if not path.is_file():
                raise FileNotFoundError(
                    f"{name} file not found: {path}"
                )

        # Load data
        print("\n[1/4] Loading configuration...")

        mock_data = None

        if settings.ADAPTER_MODE == "mock":
            print("Loading mock data...")
            mock_data = load_mock_data(MOCK_DATA_PATH)

        print(f"Selected adapter: {settings.ADAPTER_MODE}")

        print("[2/4] Loading test catalog...")
        test_cases = load_test_cases(TEST_CASES_PATH)

        if not test_cases:
            raise ValueError("The test catalog contains no test cases.")

        # Initialize components
        adapter = create_adapter(
            settings.ADAPTER_MODE,
            mock_data=mock_data,
        )

        engine = SecurityTestEngine(MATRIX_PATH, adapter)
        reporter = ReportGenerator(str(REPORTS_PATH))

        if not test_cases:
            raise ValueError("The test catalog contains no test cases.")

        # Initialize components
        adapter = create_adapter(
            settings.ADAPTER_MODE,
            mock_data=mock_data,
        )

        engine = SecurityTestEngine(MATRIX_PATH, adapter)
        reporter = ReportGenerator(str(REPORTS_PATH))

        # Execute scenarios
        print("[3/4] Executing security tests...\n")

        results = []

        for test_case in test_cases:
            try:
                result = engine.run_test(
                    user_principal_name=test_case["user"],
                    target_region=test_case["target_region"],
                    scenario_type=test_case["scenario"],
                )

                result["test_id"] = test_case["test_id"]
                result["description"] = test_case["description"]

            except Exception as error:
                result = {
                    "test_id": test_case["test_id"],
                    "user": test_case["user"].strip().lower(),
                    "scenario": test_case["scenario"],
                    "target_region": test_case["target_region"],
                    "description": test_case["description"],
                    "expected_regions": [],
                    "actual_regions": [],
                    "missing_regions": [],
                    "unauthorized_regions": [],
                    "status": "ERROR",
                    "error": str(error),
                }

            results.append(result)

            print(
                f"{result['test_id']} | "
                f"{result['scenario']} | "
                f"{result['status']}"
            )

        # Generate reports
        print("\n[4/4] Generating reports...")

        json_path = reporter.generate_json(results)
        csv_path = reporter.generate_csv(results)

        passed = sum(r["status"] == "PASS" for r in results)
        failed = sum(r["status"] == "FAIL" for r in results)
        errors = sum(r["status"] == "ERROR" for r in results)

        unauthorized_access_tests = sum(
            bool(r.get("unauthorized_regions")) for r in results
        )

        over_restriction_tests = sum(
            bool(r.get("missing_regions")) for r in results
        )

        print("\n" + "=" * 55)
        print("                 TEST SUMMARY")
        print("=" * 55)
        print(f"Total tests : {len(results)}")
        print(f"Passed      : {passed}")
        print(f"Failed      : {failed}")
        print(f"Errors      : {errors}")
        print(f"Data leaks  : {unauthorized_access_tests}")
        print(f"Over-restrictions : {over_restriction_tests}")
        print(f"\nJSON report : {json_path}")
        print(f"CSV report  : {csv_path}")
        print("=" * 55)

        return 1 if failed or errors else 0

    except (OSError, ValueError, RuntimeError) as error:
        print(f"\n[ERROR] {error}", file=sys.stderr)
        return 2


# --------------------------------------------------
# Application entry point
# --------------------------------------------------

if __name__ == "__main__":
    sys.exit(run_security_tests())
