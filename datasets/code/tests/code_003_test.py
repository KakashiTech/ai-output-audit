from solution import safe_div


def test_regular_division():
    assert safe_div(6, 3) == 2.0


def test_fractional_result():
    assert safe_div(1, 4) == 0.25


def test_zero_denominator_returns_none():
    assert safe_div(5, 0) is None


def test_zero_numerator():
    assert safe_div(0, 5) == 0.0
