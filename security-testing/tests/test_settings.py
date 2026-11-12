
import pytest

from src import settings


def test_default_adapter_is_mock():
    assert settings.ADAPTER_MODE == "mock"


def test_supported_adapters():
    assert settings.SUPPORTED_ADAPTERS == {"mock", "powerbi"}


def test_configuration_paths_exist():
    assert settings.AUTHORIZATION_MATRIX_PATH.exists()
    assert settings.TEST_CASES_PATH.exists()
    assert settings.MOCK_VISIBLE_REGIONS_PATH.exists()


def test_reports_directory_is_correct():
    assert settings.REPORTS_DIR.name == "reports"
    assert settings.REPORTS_DIR.exists()


def test_invalid_adapter_is_rejected(monkeypatch):
    monkeypatch.setenv("SECURITY_ADAPTER", "unknown")

    with pytest.raises(ValueError, match="Unsupported adapter"):
        import importlib
        importlib.reload(settings)

    # Restore the module after the test.
    monkeypatch.delenv("SECURITY_ADAPTER", raising=False)
    import importlib
    importlib.reload(settings)
