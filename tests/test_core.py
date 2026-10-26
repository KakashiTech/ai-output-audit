import math

import pytest

from audit.core import Failure, rework_cost, wilson_interval


def test_wilson_interval_bounds_are_proportions():
    lo, hi = wilson_interval(8, 15)
    assert 0.0 <= lo <= 8 / 15 <= hi <= 1.0


def test_wilson_interval_narrows_with_more_data():
    narrow = wilson_interval(80, 150)
    wide = wilson_interval(8, 15)
    assert (narrow[1] - narrow[0]) < (wide[1] - wide[0])


def test_wilson_handles_empty_sample():
    assert wilson_interval(0, 0) == (0.0, 1.0)


def test_wilson_matches_closed_form_for_simple_case():
    # p = 0.5, n = 10 -> interval centred on 0.5
    lo, hi = wilson_interval(5, 10)
    assert math.isclose((lo + hi) / 2, 0.5, abs_tol=1e-9)


def test_rework_cost_weights_severity():
    cheap = rework_cost([Failure("omission", "x", "", 2)])
    dear = rework_cost([Failure("hallucination", "x", "", 4)])
    assert dear["minutes"] > cheap["minutes"]
    assert dear["usd"] >= 0
