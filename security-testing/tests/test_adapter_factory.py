
import pytest

from src.adapter_factory import create_adapter
from src.adapters.mock_adapter import MockAdapter
from src.adapters.powerbi_adapter import PowerBIAdapter


def test_create_mock_adapter():
    mock_data = {
        "manager.fr@example.com": {"FR"}
    }

    adapter = create_adapter("mock", mock_data=mock_data)

    assert isinstance(adapter, MockAdapter)
    assert adapter.get_visible_regions(
        "manager.fr@example.com"
    ) == {"FR"}


def test_create_powerbi_adapter():
    def fake_executor(user):
        return [{"RegionCode": "FR"}]

    adapter = create_adapter(
        "powerbi",
        powerbi_executor=fake_executor
    )

    assert isinstance(adapter, PowerBIAdapter)
    assert adapter.get_visible_regions(
        "manager.fr@example.com"
    ) == {"FR"}


def test_mock_adapter_requires_data():
    with pytest.raises(ValueError, match="Mock data is required"):
        create_adapter("mock")


def test_powerbi_adapter_requires_executor():
    with pytest.raises(RuntimeError, match="query executor"):
        create_adapter("powerbi")


def test_unsupported_adapter_is_rejected():
    with pytest.raises(ValueError, match="Unsupported adapter"):
        create_adapter("unknown")
