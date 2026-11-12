
from src.test_engine import SecurityTestEngine
from src.adapters.mock_adapter import MockAdapter


def create_matrix(tmp_path, content):
    matrix = tmp_path / "authorization_matrix.csv"
    matrix.write_text(content, encoding="utf-8")
    return str(matrix)


def test_authorized_user_passes(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,FR,true\n"
    )

    adapter = MockAdapter({
        "manager.fr@example.com": {"FR"}
    })

    engine = SecurityTestEngine(matrix, adapter)
    result = engine.run_test(
        "manager.fr@example.com",
        target_region="FR",
        scenario_type="ALLOW",
    )

    assert result["status"] == "PASS"
    assert result["expected_regions"] == ["FR"]
    assert result["actual_regions"] == ["FR"]


def test_unauthorized_region_fails(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,FR,true\n"
    )

    adapter = MockAdapter({
        "manager.fr@example.com": {"FR", "DE"}
    })

    engine = SecurityTestEngine(matrix, adapter)
    result = engine.run_test(
        "manager.fr@example.com",
        target_region="DE",
        scenario_type="DENY",
    )

    assert result["status"] == "FAIL"
    assert result["unauthorized_regions"] == ["DE"]


def test_inactive_user_has_no_access(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "old.user@example.com,FR,false\n"
    )

    adapter = MockAdapter({
        "old.user@example.com": set()
    })

    engine = SecurityTestEngine(matrix, adapter)
    result = engine.run_test(
        "old.user@example.com",
        scenario_type="INACTIVE_USER",
    )

    assert result["status"] == "PASS"
    assert result["expected_regions"] == []
    assert result["actual_regions"] == []


def test_unknown_user_has_no_access(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,FR,true\n"
    )

    adapter = MockAdapter({})

    engine = SecurityTestEngine(matrix, adapter)
    result = engine.run_test(
        "unknown@example.com",
        scenario_type="UNKNOWN_USER",
    )

    assert result["status"] == "PASS"
    assert result["expected_regions"] == []
    assert result["actual_regions"] == []


def test_multi_region_user_passes(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.eu@example.com,FR,true\n"
        "manager.eu@example.com,DE,true\n"
        "manager.eu@example.com,ES,true\n"
    )

    adapter = MockAdapter({
        "manager.eu@example.com": {"FR", "DE", "ES"}
    })

    engine = SecurityTestEngine(matrix, adapter)
    result = engine.run_test(
        "manager.eu@example.com",
        scenario_type="MULTI_REGION",
    )

    assert result["status"] == "PASS"
    assert result["expected_regions"] == ["DE", "ES", "FR"]
    assert result["actual_regions"] == ["DE", "ES", "FR"]
