
from src.comparator import compare_regions


def test_authorized_access():
    result = compare_regions({"FR"}, {"FR"})
    assert result.passed is True


def test_unauthorized_access():
    result = compare_regions({"FR"}, {"FR", "DE"})
    assert result.passed is False
    assert result.unauthorized_regions == {"DE"}


def test_missing_authorized_region():
    result = compare_regions({"FR", "DE"}, {"FR"})
    assert result.passed is False
    assert result.missing_regions == {"DE"}


def test_multiple_authorized_regions():
    result = compare_regions({"FR", "DE", "ES"}, {"FR", "DE", "ES"})
    assert result.passed is True
