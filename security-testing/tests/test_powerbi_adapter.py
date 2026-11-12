
import pytest

from src.adapters.powerbi_adapter import PowerBIAdapter


def test_get_visible_regions():
    def fake_executor(user):
        assert user == "manager.fr@example.com"

        return [
            {"RegionCode": "FR"},
            {"RegionCode": "DE"},
            {"RegionCode": "FR"},
        ]

    adapter = PowerBIAdapter(fake_executor)

    result = adapter.get_visible_regions("manager.fr@example.com")

    assert result == {"FR", "DE"}


def test_user_normalization():
    received_users = []

    def fake_executor(user):
        received_users.append(user)
        return [{"RegionCode": "fr"}]

    adapter = PowerBIAdapter(fake_executor)

    result = adapter.get_visible_regions(" MANAGER.FR@EXAMPLE.COM ")

    assert received_users == ["manager.fr@example.com"]
    assert result == {"FR"}


def test_empty_user_raises_error():
    adapter = PowerBIAdapter(lambda user: [])

    with pytest.raises(ValueError):
        adapter.get_visible_regions(" ")


def test_invalid_executor_raises_error():
    with pytest.raises(TypeError):
        PowerBIAdapter("not_callable")


def test_none_result_raises_error():
    adapter = PowerBIAdapter(lambda user: None)

    with pytest.raises(ValueError):
        adapter.get_visible_regions("manager.fr@example.com")


def test_invalid_row_raises_error():
    adapter = PowerBIAdapter(lambda user: ["FR"])

    with pytest.raises(ValueError):
        adapter.get_visible_regions("manager.fr@example.com")


def test_missing_region_raises_error():
    adapter = PowerBIAdapter(lambda user: [{"OtherColumn": "FR"}])

    with pytest.raises(ValueError):
        adapter.get_visible_regions("manager.fr@example.com")


def test_empty_region_raises_error():
    adapter = PowerBIAdapter(lambda user: [{"RegionCode": " "}])

    with pytest.raises(ValueError):
        adapter.get_visible_regions("manager.fr@example.com")
