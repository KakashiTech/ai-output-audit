"""Report generation: markdown for humans, JSON for machines.

The markdown report is the deliverable a client pays for. It must survive
being forwarded to a CTO who did not attend the call, so every number carries
its denominator and its uncertainty.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .core import SEVERITY_LABEL, TaskResult, rework_cost, wilson_interval


def build_summary(results: list[TaskResult], model: str, rate: float) -> dict:
    n = len(results)
    passed = sum(1 for r in results if r.passed)
    failures = [f for r in results for f in r.failures]
    lo, hi = wilson_interval(passed, n)

    by_family: dict[str, dict] = {}
    for family in sorted({r.family for r in results}):
        fam = [r for r in results if r.family == family]
        fam_pass = sum(1 for r in fam if r.passed)
        by_family[family] = {
            "n": len(fam),
            "passed": fam_pass,
            "pass_rate": round(fam_pass / len(fam), 4) if fam else 0.0,
            "failures": sum(len(r.failures) for r in fam),
        }

    kinds = Counter(f.kind for f in failures)
    severity = Counter(f.severity for f in failures)
    cost = rework_cost(failures, hourly_rate=rate)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": model,
        "n": n,
        "passed": passed,
        "failed": n - passed,
        "pass_rate": round(passed / n, 4) if n else 0.0,
        "ci95": [round(lo, 4), round(hi, 4)],
        "by_family": by_family,
        "failure_kinds": dict(kinds.most_common()),
        "severity_counts": {str(k): v for k, v in sorted(severity.items(), reverse=True)},
        "cost": cost,
        "cost_per_100_outputs": round(cost["usd"] * (100 / n), 2) if n else 0.0,
    }


def _fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_markdown(summary: dict, results: list[TaskResult], max_examples: int = 10) -> str:
    ci_lo, ci_hi = summary["ci95"]
    lines: list[str] = []
    add = lines.append

    add(f"# Auditoría de salida de IA — `{summary['model']}`")
    add("")
    add(f"**Fecha:** {summary['generated_at']}  ")
    add(f"**Casos evaluados:** {summary['n']}  ")
    add(f"**Método:** golden set + graders deterministas (ejecución de código y comparación campo a campo).")
    add("")
    add("## Veredicto")
    add("")
    add(
        f"> Tasa de acierto: **{_fmt_pct(summary['pass_rate'])}** "
        f"(IC 95%: {_fmt_pct(ci_lo)} – {_fmt_pct(ci_hi)}). "
        f"{summary['failed']} de {summary['n']} outputs fallaron."
    )
    add("")
    add(
        f"Coste estimado de retrabajo si esto se repite 100 veces: "
        f"**${summary['cost_per_100_outputs']:.0f}** "
        f"({summary['cost']['minutes'] * (100 / summary['n']) / 60:.1f} h a ${summary['cost']['hourly_rate']:.0f}/h)."
    )
    add("")

    add("## Por familia de tarea")
    add("")
    add("| Familia | Casos | Aciertos | Tasa | Fallos |")
    add("|---|---:|---:|---:|---:|")
    for family, data in summary["by_family"].items():
        add(
            f"| `{family}` | {data['n']} | {data['passed']} | "
            f"{_fmt_pct(data['pass_rate'])} | {data['failures']} |"
        )
    add("")

    add("## Taxonomía de fallos")
    add("")
    if summary["failure_kinds"]:
        add("| Tipo | Ocurrencias | Qué significa |")
        add("|---|---:|---|")
        meaning = {
            "hallucination": "valor inventado que no existe en la fuente",
            "unit_error": "error de unidad o factor (~10x, ~1000x)",
            "substitution": "tomó un dato real del lugar equivocado",
            "omission": "campo ausente",
            "wrong_value": "valor numérico incorrecto",
            "format_error": "salida no parseable",
            "logic_error": "el código se ejecuta pero falla los tests",
            "runtime_error": "el código no compila ni importa",
        }
        for kind, count in summary["failure_kinds"].items():
            add(f"| `{kind}` | {count} | {meaning.get(kind, '—')} |")
    else:
        add("Sin fallos en esta muestra.")
    add("")

    add("## Severidad")
    add("")
    add("| Severidad | Fallos |")
    add("|---|---:|")
    for level in ("4", "3", "2", "1"):
        if level in summary["severity_counts"]:
            add(f"| {SEVERITY_LABEL[int(level)]} | {summary['severity_counts'][level]} |")
    add("")

    add(f"## Fallos reproducidos (máx. {max_examples})")
    add("")
    shown = 0
    for result in results:
        if result.passed:
            continue
        for failure in result.failures:
            if shown >= max_examples:
                break
            field = f" `{failure.field}`" if failure.field else ""
            add(f"{shown + 1}. **{result.task_id}**{field} — `{failure.kind}` "
                f"(sev {failure.severity}): {failure.detail}")
            shown += 1
        if shown >= max_examples:
            break
    if shown == 0:
        add("Ninguno.")
    add("")

    add("## Metodología")
    add("")
    add("- Cada caso tiene una respuesta de referencia verificable, no una opinión.")
    add("- `extraction`: comparación campo a campo + detección de invención y de error de unidad.")
    add("- `code`: el código generado se ejecuta contra tests ocultos en un directorio temporal.")
    add("- El intervalo de confianza es Wilson al 95%; con n pequeño el rango es ancho a propósito.")
    add("- Los minutos de retrabajo por severidad son un supuesto editable, no una medición.")
    add("")
    add("## Limitaciones")
    add("")
    add("- El golden set es sintético y pequeño: mide el método, no el modelo en producción del cliente.")
    add("- Un acierto no prueba corrección semántica, solo conformidad con el criterio definido.")
    add("- Ejecutar código generado requiere aislamiento (contenedor/VM) en trabajo real.")
    add("")
    return "\n".join(lines)


def write_report(out_dir: str | Path, summary: dict, results: list[TaskResult]) -> tuple[Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    md_path = out / "report.md"
    json_path = out / "report.json"
    md_path.write_text(render_markdown(summary, results), encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {"summary": summary, "results": [r.as_dict() for r in results]},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return md_path, json_path
