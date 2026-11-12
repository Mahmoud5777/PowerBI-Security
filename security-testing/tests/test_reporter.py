
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

def test_security_anomaly_counters(tmp_path):
    from src.reporter import ReportGenerator

    reporter = ReportGenerator(str(tmp_path))

    results = [
        {
            "status": "FAIL",
            "unauthorized_regions": ["DE"],
            "missing_regions": [],
        },
        {
            "status": "FAIL",
            "unauthorized_regions": [],
            "missing_regions": ["ES"],
        },
        {
            "status": "PASS",
            "unauthorized_regions": [],
            "missing_regions": [],
        },
    ]

    report_path = reporter.generate_json(results)

    import json

    with report_path.open(encoding="utf-8") as file:
        report = json.load(file)

    assert report["total_tests"] == 3
    assert report["failed"] == 2
    assert report["unauthorized_access_tests"] == 1
    assert report["over_restriction_tests"] == 1