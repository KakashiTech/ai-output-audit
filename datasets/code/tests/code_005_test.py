import pytest

from solution import moving_average


def test_basic_window():
    assert moving_average([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]


def test_window_of_one():
    assert moving_average([1, 2, 3], 1) == [1.0, 2.0, 3.0]


def test_window_equals_length():
    assert moving_average([1, 2, 3], 3) == [2.0]


def test_rejects_invalid_window():
    with pytest.raises(ValueError):
        moving_average([1, 2], 0)
    with pytest.raises(ValueError):
        moving_average([1, 2], 3)
