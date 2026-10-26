import pytest

from solution import chunk


def test_splits_evenly():
    assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_last_chunk_shorter():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_window_larger_than_list():
    assert chunk([1, 2], 5) == [[1, 2]]


def test_rejects_invalid_window():
    with pytest.raises(ValueError):
        chunk([1], 0)
