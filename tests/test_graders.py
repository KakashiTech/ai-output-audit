from audit.graders import grade_code, grade_extraction, parse_json_object

BASE_TASK = {
    "id": "t1",
    "family": "extraction",
    "source": "The ABC-100 regulator accepts 2.7 V to 5.5 V and draws 12 uA. Package is SOT-23-5.",
    "expected": {
        "part_number": "ABC-100",
        "vin_min": 2.7,
        "vin_max": 5.5,
        "iq_typ_ua": 12,
        "package": "SOT-23-5",
    },
}


def test_parses_json_wrapped_in_prose():
    parsed = parse_json_object('Aquí tienes: {"a": 1} — espero que sirva')
    assert parsed == {"a": 1}


def test_parses_fenced_json():
    parsed = parse_json_object('```json\n{"a": 1}\n```')
    assert parsed == {"a": 1}


def test_unparseable_output_is_format_error():
    result = grade_extraction(BASE_TASK, "no pienso devolver json")
    assert not result.passed
    assert result.failures[0].kind == "format_error"


def test_correct_output_passes():
    output = (
        '{"part_number": "ABC-100", "vin_min": 2.7, "vin_max": 5.5, '
        '"iq_typ_ua": 12, "package": "SOT-23-5"}'
    )
    assert grade_extraction(BASE_TASK, output).passed


def test_missing_field_is_omission():
    output = '{"part_number": "ABC-100", "vin_min": 2.7, "vin_max": 5.5, "iq_typ_ua": 12}'
    result = grade_extraction(BASE_TASK, output)
    assert [f.kind for f in result.failures] == ["omission"]
    assert result.failures[0].field == "package"


def test_invented_identifier_is_hallucination():
    output = (
        '{"part_number": "ABC-999", "vin_min": 2.7, "vin_max": 5.5, '
        '"iq_typ_ua": 12, "package": "SOT-23-5"}'
    )
    result = grade_extraction(BASE_TASK, output)
    assert result.failures[0].kind == "hallucination"
    assert result.failures[0].severity == 4


def test_factor_1000_is_unit_error():
    output = (
        '{"part_number": "ABC-100", "vin_min": 2.7, "vin_max": 5.5, '
        '"iq_typ_ua": 0.012, "package": "SOT-23-5"}'
    )
    result = grade_extraction(BASE_TASK, output)
    assert result.failures[0].kind == "unit_error"


def test_value_taken_from_wrong_place_is_substitution():
    source = "ABC-100 accepts 2.7 V to 5.5 V. Shutdown current 0.8 uA. Quiescent 12 uA. SOT-23-5."
    task = {
        **BASE_TASK,
        "source": source,
        "expected": {**BASE_TASK["expected"], "iq_typ_ua": 12},
    }
    output = (
        '{"part_number": "ABC-100", "vin_min": 2.7, "vin_max": 5.5, '
        '"iq_typ_ua": 0.8, "package": "SOT-23-5"}'
    )
    result = grade_extraction(task, output)
    assert result.failures[0].kind == "substitution"


def test_code_grader_passes_correct_solution(tmp_path):
    test_file = tmp_path / "test_solution.py"
    test_file.write_text(
        "from solution import double\n\n"
        "def test_double():\n"
        "    assert double(3) == 6\n"
    )
    task = {
        "id": "c1",
        "family": "code",
        "test": "test_solution.py",
        "_dataset_dir": str(tmp_path),
    }
    result = grade_code(task, "```python\ndef double(x):\n    return x * 2\n```")
    assert result.passed


def test_code_grader_catches_wrong_solution(tmp_path):
    test_file = tmp_path / "test_solution.py"
    test_file.write_text(
        "from solution import double\n\n"
        "def test_double():\n"
        "    assert double(3) == 6\n"
    )
    task = {
        "id": "c1",
        "family": "code",
        "test": "test_solution.py",
        "_dataset_dir": str(tmp_path),
    }
    result = grade_code(task, "def double(x):\n    return x + 2\n")
    assert not result.passed
    assert result.failures[0].kind == "logic_error"
