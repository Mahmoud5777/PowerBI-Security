
from src.adapters.powerbi_adapter import PowerBIAdapter
from src.test_engine import SecurityTestEngine


def test_powerbi_adapter_with_security_engine(tmp_path):
    matrix = tmp_path / "authorization_matrix.csv"

    matrix.write_text(
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,FR,true\n"
        "manager.fr@example.com,DE,false\n",
        encoding="utf-8",
    )

    def fake_powerbi_executor(user):
        assert user == "manager.fr@example.com"
        return [{"RegionCode": "FR"}]

    adapter = PowerBIAdapter(fake_powerbi_executor)

    engine = SecurityTestEngine(str(matrix), adapter)

    result = engine.run_test(
        user_principal_name="manager.fr@example.com",
        target_region="FR",
        scenario_type="ALLOW",
    )

    assert result["status"] == "PASS"
    assert result["expected_regions"] == ["FR"]
    assert result["actual_regions"] == ["FR"]
    assert result["missing_regions"] == []
    assert result["unauthorized_regions"] == []


def test_powerbi_adapter_detects_data_leak(tmp_path):
    matrix = tmp_path / "authorization_matrix.csv"

    matrix.write_text(
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,FR,true\n",
        encoding="utf-8",
    )

    def fake_powerbi_executor(user):
        return [
            {"RegionCode": "FR"},
            {"RegionCode": "DE"},
        ]

    adapter = PowerBIAdapter(fake_powerbi_executor)

    engine = SecurityTestEngine(str(matrix), adapter)

    result = engine.run_test(
        user_principal_name="manager.fr@example.com",
        target_region="FR",
        scenario_type="ALLOW",
    )

    assert result["status"] == "FAIL"
    assert result["unauthorized_regions"] == ["DE"]
