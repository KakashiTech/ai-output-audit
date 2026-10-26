"""Graders: turn a model output into pass/fail plus a typed failure list.

Two families ship today:

* ``extraction`` - deterministic field comparison against a golden record.
* ``code``      - the generated code is executed against hidden tests.

Both are falsifiable without a human in the loop, which is the whole point:
the audit must be reproducible by the client.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from .core import Failure, TaskResult

FENCE_RE = re.compile(r"```(?:python|json)?\s*(.*?)```", re.DOTALL)


def extract_code_block(text: str) -> str:
    match = FENCE_RE.search(text)
    return match.group(1).strip() if match else text.strip()


def parse_json_object(text: str) -> dict | None:
    """Parse the first JSON object found in a model response.

    Models love to wrap JSON in prose. We are strict about validity but
    forgiving about packaging, otherwise every audit measures formatting
    instead of correctness.
    """
    candidate = extract_code_block(text)
    try:
        value = json.loads(candidate)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        pass
    start = candidate.find("{")
    if start == -1:
        return None
    try:
        value, _ = json.JSONDecoder().raw_decode(candidate[start:])
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        return None


def _normalise(value):
    if isinstance(value, str):
        return value.strip().lower()
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value)
    return value


def _numbers_close(a: float, b: float, rel: float = 1e-6) -> bool:
    if b == 0:
        return abs(a) < rel
    return abs(a - b) / abs(b) < rel


def grade_extraction(task: dict, output: str) -> TaskResult:
    """Compare one extraction output against the expected record.

    Failure taxonomy is the product here, not the score. ``hallucination``
    means the model invented a value that is not in the source at all;
    ``substitution`` means it grabbed a real number from the wrong place;
    ``unit_error`` means it was off by a power of ten.
    """
    expected: dict = task["expected"]
    source: str = task.get("source", "")
    parsed = parse_json_object(output)
    failures: list[Failure] = []

    if parsed is None:
        return TaskResult(
            task_id=task["id"],
            family=task["family"],
            passed=False,
            failures=[
                Failure(
                    kind="format_error",
                    field=None,
                    detail="respuesta no contiene un objeto JSON parseable",
                    severity=2,
                )
            ],
            output=output,
        )

    source_lc = source.lower()

    for key, want in expected.items():
        if key not in parsed or parsed[key] in (None, ""):
            failures.append(
                Failure(
                    kind="omission",
                    field=key,
                    detail=f"campo ausente (se esperaba {want!r})",
                    severity=2,
                )
            )
            continue

        got = parsed[key]

        if isinstance(want, (int, float)) and not isinstance(want, bool):
            try:
                got_num = float(got)
            except (TypeError, ValueError):
                failures.append(
                    Failure(
                        kind="wrong_value",
                        field=key,
                        detail=f"se esperaba un número, llegó {got!r}",
                        severity=3,
                    )
                )
                continue
            if _numbers_close(got_num, float(want)):
                continue
            ratio = abs(got_num) / abs(float(want)) if want else 0
            if ratio and (ratio >= 100 or ratio <= 0.01):
                factor = f"~{ratio:.0f}x mayor" if ratio >= 1 else f"~{1 / ratio:.0f}x menor"
                failures.append(
                    Failure(
                        kind="unit_error",
                        field=key,
                        detail=f"{got_num!r} vs {want!r} ({factor})",
                        severity=3,
                    )
                )
            elif str(got).strip().lower() in source_lc:
                failures.append(
                    Failure(
                        kind="substitution",
                        field=key,
                        detail=f"tomó {got!r} de otro sitio del texto",
                        severity=2,
                    )
                )
            else:
                failures.append(
                    Failure(
                        kind="wrong_value",
                        field=key,
                        detail=f"{got_num!r} vs {want!r}",
                        severity=3,
                    )
                )
            continue

        # String fields
        if _normalise(got) == _normalise(want):
            continue
        if str(got).strip().lower() not in source_lc:
            failures.append(
                Failure(
                    kind="hallucination",
                    field=key,
                    detail=f"{got!r} no aparece en la fuente (esperado {want!r})",
                    severity=4,
                )
            )
        else:
            failures.append(
                Failure(
                    kind="substitution",
                    field=key,
                    detail=f"{got!r} está en el texto pero no es el valor correcto ({want!r})",
                    severity=2,
                )
            )

    return TaskResult(
        task_id=task["id"],
        family=task["family"],
        passed=not failures,
        failures=failures,
        output=output,
    )


def grade_code(task: dict, output: str, timeout_s: int = 30) -> TaskResult:
    """Execute generated code against hidden tests in a throwaway directory.

    Warning: this runs model-generated code. For real client work, run it in
    a container or a throwaway VM. Here the blast radius is a temp dir.
    """
    code = extract_code_block(output)
    test_path = Path(task["test"])
    if not test_path.is_absolute():
        test_path = Path(task["_dataset_dir"]) / test_path
    test_code = test_path.read_text(encoding="utf-8")

    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="audit-") as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "solution.py").write_text(code, encoding="utf-8")
        (tmp_path / "test_solution.py").write_text(test_code, encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONPATH"] = tmp
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "--no-header",
                "-p",
                "no:cacheprovider",
                "test_solution.py",
            ],
            cwd=tmp,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    duration = time.monotonic() - started
    stdout = (proc.stdout or "") + (proc.stderr or "")
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    assertion = next((ln for ln in lines if ln.startswith("E ") and "assert" in ln), None)
    tail = assertion or (lines[-1] if lines else "sin salida")
    tail = " ".join(tail.split())
    if len(tail) > 300:
        tail = tail[:297] + "..."

    if proc.returncode == 0:
        failures: list[Failure] = []
    elif proc.returncode in (2, 3, 4, 5):
        failures = [
            Failure(
                kind="runtime_error",
                field=None,
                detail=tail or "el código no se pudo importar/ejecutar",
                severity=3,
            )
        ]
    else:
        failures = [
            Failure(
                kind="logic_error",
                field=None,
                detail=tail or "los tests ocultos fallan",
                severity=3,
            )
        ]

    return TaskResult(
        task_id=task["id"],
        family=task["family"],
        passed=not failures,
        failures=failures,
        output=output,
        duration_s=duration,
    )


GRADERS = {
    "extraction": grade_extraction,
    "code": grade_code,
}


def grade(task: dict, output: str) -> TaskResult:
    return GRADERS[task["family"]](task, output)
