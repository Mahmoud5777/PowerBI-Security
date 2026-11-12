
import csv
import json
from pathlib import Path


class ReportGenerator:

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_json(self, results: list[dict]) -> Path:
        """Génère un rapport JSON avec le résumé des tests."""

        report_path = self.output_dir / "security_report.json"

        report = {
            "total_tests": len(results),
            "passed": sum(
                result["status"] == "PASS" for result in results
            ),
            "failed": sum(
                result["status"] == "FAIL" for result in results
            ),
            "errors": sum(
                result["status"] == "ERROR" for result in results
            ),
            "unauthorized_access_tests": sum(
                bool(result.get("unauthorized_regions"))
                for result in results
            ),
            "over_restriction_tests": sum(
                bool(result.get("missing_regions"))
                for result in results
            ),
            "results": results,
        }

        with report_path.open("w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False
            )

        return report_path

    def generate_csv(self, results: list[dict]) -> Path:
        """Génère un rapport CSV détaillé."""

        report_path = self.output_dir / "security_report.csv"

        fieldnames = [
            "test_id",
            "user",
            "scenario",
            "target_region",
            "description",
            "expected_regions",
            "actual_regions",
            "missing_regions",
            "unauthorized_regions",
            "status",
            "error",
        ]

        with report_path.open(
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                extrasaction="ignore"
            )

            writer.writeheader()

            for result in results:
                row = result.copy()

                for field in fieldnames:
                    value = row.get(field)

                    if isinstance(value, list):
                        row[field] = ";".join(value)

                writer.writerow(row)

        return report_path
