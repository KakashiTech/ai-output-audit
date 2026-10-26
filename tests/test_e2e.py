import json
from pathlib import Path

from audit.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_demo_run_produces_reproducible_numbers(tmp_path):
    exit_code = main(
        [
            "run",
            "--dataset",
            str(ROOT / "datasets"),
            "--adapter",
            "mock",
            "--run-dir",
            str(ROOT / "runs" / "demo-model"),
            "--out",
            str(tmp_path),
            "--rate",
            "80",
        ]
    )
    assert exit_code == 0

    payload = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    summary = payload["summary"]

    assert summary["n"] == 15
    assert summary["passed"] == 8
    assert summary["failed"] == 7
    assert summary["failure_kinds"]["hallucination"] == 1
    assert summary["failure_kinds"]["unit_error"] == 1
    assert summary["failure_kinds"]["format_error"] == 1
    assert summary["failure_kinds"]["logic_error"] == 2

    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "53.3%" in report
    assert "TRX-6010" in report
