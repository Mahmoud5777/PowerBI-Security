
import csv
import json
from pathlib import Path


class ReportGenerator:

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_json(self, results: list[dict]) -> Path:
        report_path = self.output_dir / "security_report.json"

        report = {
            "total_tests": len(results),
            "passed": sum(r["status"] == "PASS" for r in results),
            "failed": sum(r["status"] == "FAIL" for r in results),
            "results": results,
        }

        with report_path.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=4, ensure_ascii=False)

        return report_path

    def generate_csv(self, results: list[dict]) -> Path:
        report_path = self.output_dir / "security_report.csv"

        fieldnames = [
            "user",
            "expected_regions",
            "actual_regions",
            "missing_regions",
            "unauthorized_regions",
            "status",
        ]

        with report_path.open(
            "w", encoding="utf-8-sig", newline=""
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                row = result.copy()

                for field in fieldnames:
                    if field in row and isinstance(row[field], list):
                        row[field] = ";".join(row[field])

                writer.writerow(row)

        return report_path
