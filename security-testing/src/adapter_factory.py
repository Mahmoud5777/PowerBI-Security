
from collections.abc import Callable
from typing import Any

from src.adapters.base_adapter import BaseAdapter
from src.adapters.mock_adapter import MockAdapter
from src.adapters.powerbi_adapter import PowerBIAdapter


def create_adapter(
    mode: str,
    mock_data: dict[str, set[str]] | None = None,
    powerbi_executor: Callable[[str], list[dict[str, Any]]] | None = None,
) -> BaseAdapter:
    """
    Creates the appropriate adapter based on the selected mode.
    """

    adapter_mode = mode.strip().lower()

    if adapter_mode == "mock":
        if mock_data is None:
            raise ValueError("Mock data is required for MockAdapter")

        return MockAdapter(mock_data)

    if adapter_mode == "powerbi":
        if powerbi_executor is None:
            raise RuntimeError(
                "PowerBIAdapter requires a configured Power BI query executor. "
                "Real Power BI integration is not configured yet."
            )

        return PowerBIAdapter(powerbi_executor)

    raise ValueError(f"Unsupported adapter mode: {mode}")
