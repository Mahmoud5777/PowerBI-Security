
import csv
import pytest

from src.main import load_test_cases


def create_catalog(tmp_path, rows, fieldnames=None):
    file_path = tmp_path / "test_cases.csv"

    if fieldnames is None:
        fieldnames = [
            "TestId",
            "UserPrincipalName",
            "TargetRegion",
            "ScenarioType",
            "Description",
        ]

    with file_path.open(
        mode="w",
        encoding="utf-8",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(rows)

    return file_path


def valid_case():
    return {
        "TestId": "TC001",
        "UserPrincipalName": "manager.fr@example.com",
        "TargetRegion": "FR",
        "ScenarioType": "ALLOW",
        "Description": "Verify France access",
    }


def test_load_valid_catalog(tmp_path):
    file_path = create_catalog(tmp_path, [valid_case()])

    result = load_test_cases(file_path)

    assert len(result) == 1
    assert result[0]["test_id"] == "TC001"
    assert result[0]["scenario"] == "ALLOW"
    assert result[0]["target_region"] == "FR"


def test_duplicate_test_id_is_rejected(tmp_path):
    rows = [
        valid_case(),
        valid_case(),
    ]

    file_path = create_catalog(tmp_path, rows)

    with pytest.raises(ValueError, match="Duplicate TestId"):
        load_test_cases(file_path)


def test_unsupported_scenario_is_rejected(tmp_path):
    case = valid_case()
    case["ScenarioType"] = "INVALID"

    file_path = create_catalog(tmp_path, [case])

    with pytest.raises(ValueError, match="Unsupported scenario"):
        load_test_cases(file_path)


@pytest.mark.parametrize("scenario", ["ALLOW", "DENY"])
def test_target_region_is_required(tmp_path, scenario):
    case = valid_case()
    case["ScenarioType"] = scenario
    case["TargetRegion"] = ""

    file_path = create_catalog(tmp_path, [case])

    with pytest.raises(ValueError, match="TargetRegion is required"):
        load_test_cases(file_path)


def test_empty_required_value_is_rejected(tmp_path):
    case = valid_case()
    case["Description"] = ""

    file_path = create_catalog(tmp_path, [case])

    with pytest.raises(ValueError, match="Incomplete test case"):
        load_test_cases(file_path)


def test_missing_csv_field_is_rejected(tmp_path):
    file_path = tmp_path / "test_cases.csv"

    file_path.write_text(
        "TestId,UserPrincipalName,TargetRegion,ScenarioType,Description\n"
        "TC001,manager.fr@example.com,FR,ALLOW\n",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="missing CSV field"):
        load_test_cases(file_path)


def test_missing_column_is_rejected(tmp_path):
    file_path = tmp_path / "test_cases.csv"

    file_path.write_text(
        "TestId,UserPrincipalName,ScenarioType\n"
        "TC001,manager.fr@example.com,ALLOW\n",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Invalid test catalog"):
        load_test_cases(file_path)
