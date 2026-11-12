
from dataclasses import dataclass


@dataclass
class ComparisonResult:
    expected_regions: set[str]
    actual_regions: set[str]
    missing_regions: set[str]
    unauthorized_regions: set[str]
    passed: bool


def compare_regions(
    expected_regions: set[str],
    actual_regions: set[str],
) -> ComparisonResult:
    """
    Compare les régions attendues avec les régions réellement visibles.
    """

    missing = expected_regions - actual_regions
    unauthorized = actual_regions - expected_regions

    return ComparisonResult(
        expected_regions=expected_regions,
        actual_regions=actual_regions,
        missing_regions=missing,
        unauthorized_regions=unauthorized,
        passed=not missing and not unauthorized,
    )
