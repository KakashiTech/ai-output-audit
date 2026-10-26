import pytest

from solution import parse_duration


@pytest.mark.parametrize(
    "text,expected",
    [("1h30m", 5400), ("45s", 45), ("2h", 7200), ("0m", 0), ("1h2m3s", 3723)],
)
def test_parse_duration(text, expected):
    assert parse_duration(text) == expected
