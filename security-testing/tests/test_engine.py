
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

def test_over_restriction_fails(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.eu@example.com,FR,true\n"
        "manager.eu@example.com,DE,true\n"
        "manager.eu@example.com,ES,true\n"
    )

    adapter = MockAdapter({
        "manager.eu@example.com": {"FR", "DE"}
    })

    engine = SecurityTestEngine(matrix, adapter)
    result = engine.run_test(
        "manager.eu@example.com",
        scenario_type="MULTI_REGION",
    )

    assert result["status"] == "FAIL"
    assert result["missing_regions"] == ["ES"]


def test_authorized_user_with_data_leak_fails(tmp_path):
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
        target_region="FR",
        scenario_type="ALLOW",
    )

    assert result["status"] == "FAIL"
    assert result["unauthorized_regions"] == ["DE"]

def test_user_and_region_normalization(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        " MANAGER.FR@EXAMPLE.COM , fr , TRUE \n"
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


def test_invalid_matrix_format_raises_error(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode\n"
        "manager.fr@example.com,FR\n"
    )

    engine = SecurityTestEngine(matrix, MockAdapter({}))

    import pytest

    with pytest.raises(ValueError, match="Invalid authorization matrix format"):
        engine.run_test(
            "manager.fr@example.com",
            scenario_type="ALLOW",
        )


def test_inactive_user_with_visible_data_fails(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "old.user@example.com,FR,false\n"
    )

    adapter = MockAdapter({
        "old.user@example.com": {"FR"}
    })

    engine = SecurityTestEngine(matrix, adapter)
    result = engine.run_test(
        "old.user@example.com",
        scenario_type="INACTIVE_USER",
    )

    assert result["status"] == "FAIL"
    assert result["unauthorized_regions"] == ["FR"]


def test_unsupported_scenario_raises_error(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,FR,true\n"
    )

    engine = SecurityTestEngine(matrix, MockAdapter({}))

    import pytest

    with pytest.raises(ValueError, match="Unsupported scenario"):
        engine.run_test(
            "manager.fr@example.com",
            scenario_type="INVALID",
        )

def test_invalid_is_active_value_raises_error(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,FR,yes\n"
    )

    engine = SecurityTestEngine(matrix, MockAdapter({}))

    import pytest

    with pytest.raises(ValueError, match="Invalid IsActive value"):
        engine.load_authorizations()

def test_load_all_users_rejects_invalid_is_active(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,FR,yes\n"
    )

    engine = SecurityTestEngine(matrix, MockAdapter({}))

    import pytest

    with pytest.raises(ValueError, match="Invalid IsActive value"):
        engine.load_all_users()

def test_missing_user_raises_error(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        ",FR,true\n"
    )

    engine = SecurityTestEngine(matrix, MockAdapter({}))

    import pytest

    with pytest.raises(ValueError, match="Missing required value"):
        engine.load_authorizations()


def test_missing_region_raises_error(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,,true\n"
    )

    engine = SecurityTestEngine(matrix, MockAdapter({}))

    import pytest

    with pytest.raises(ValueError, match="Missing required value"):
        engine.load_authorizations()

def test_inactive_assignment_is_not_authorized(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,FR,true\n"
        "manager.fr@example.com,DE,false\n"
    )

    adapter = MockAdapter({
        "manager.fr@example.com": {"FR"}
    })

    engine = SecurityTestEngine(matrix, adapter)

    authorizations = engine.load_authorizations()

    assert authorizations == {
        "manager.fr@example.com": {"FR"}
    }

def test_duplicate_authorizations_are_deduplicated(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,FR,true\n"
        "manager.fr@example.com,FR,true\n"
    )

    engine = SecurityTestEngine(matrix, MockAdapter({}))

    authorizations = engine.load_authorizations()

    assert authorizations == {
        "manager.fr@example.com": {"FR"}
    }

def test_unknown_user_with_visible_data_fails(tmp_path):
    matrix = create_matrix(
        tmp_path,
        "UserPrincipalName,RegionCode,IsActive\n"
        "manager.fr@example.com,FR,true\n"
    )

    adapter = MockAdapter({
        "unknown@example.com": {"FR"}
    })

    engine = SecurityTestEngine(matrix, adapter)

    result = engine.run_test(
        "unknown@example.com",
        scenario_type="UNKNOWN_USER",
    )

    assert result["status"] == "FAIL"
    assert result["unauthorized_regions"] == ["FR"]