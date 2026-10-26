from audit.report import validity_notes


def test_ceiling_is_flagged_on_perfect_small_sample():
    summary = {"n": 15, "pass_rate": 1.0, "ci95": [0.796, 1.0], "failed": 0}
    notes = " ".join(validity_notes(summary))
    assert "Techo" in notes
    assert "Cero fallos" in notes


def test_no_ceiling_flag_for_mid_rate():
    summary = {"n": 15, "pass_rate": 0.533, "ci95": [0.301, 0.752], "failed": 7}
    notes = " ".join(validity_notes(summary))
    assert "Techo" not in notes
    assert "Muestra pequeña" in notes


def test_large_sample_has_no_small_sample_warning():
    summary = {"n": 200, "pass_rate": 0.7, "ci95": [0.63, 0.76], "failed": 60}
    assert validity_notes(summary) == []
