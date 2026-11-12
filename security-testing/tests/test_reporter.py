
import json

from src.reporter import ReportGenerator


def test_generate_json_report(tmp_path):
    results = [
        {
            "user": "manager.fr@example.com",
            "expected_regions": ["FR"],
            "actual_regions": ["FR"],
            "missing_regions": [],
            "unauthorized_regions": [],
            "status": "PASS",
        },
        {
            "user": "manager.de@example.com",
            "expected_regions": ["DE"],
            "actual_regions": ["DE", "FR"],
            "missing_regions": [],
            "unauthorized_regions": ["FR"],
            "status": "FAIL",
        },
    ]

    generator = ReportGenerator(str(tmp_path))
    report_path = generator.generate_json(results)

    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["total_tests"] == 2
    assert report["passed"] == 1
    assert report["failed"] == 1


def test_generate_csv_report(tmp_path):
    results = [
        {
            "user": "manager.fr@example.com",
            "expected_regions": ["FR"],
            "actual_regions": ["FR"],
            "missing_regions": [],
            "unauthorized_regions": [],
            "status": "PASS",
        }
    ]

    generator = ReportGenerator(str(tmp_path))
    report_path = generator.generate_csv(results)

    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8-sig")

    assert "manager.fr@example.com" in content
    assert "PASS" in content
