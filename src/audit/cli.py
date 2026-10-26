"""CLI entry point.

Usage:
    python -m audit run --adapter mock --run-dir runs/demo-model --out reports/demo
    python -m audit run --adapter openai --model gpt-4.1-mini --out reports/live
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .adapters import AdapterError, MockAdapter, OpenAICompatibleAdapter
from .graders import grade
from .report import build_summary, write_report

EXTRACTION_PROMPT = (
    "Extrae los datos del siguiente texto y devuelve SOLO un objeto JSON "
    "válido con exactamente estas claves: {keys}. "
    "Usa números sin unidades en los campos numéricos. "
    "No inventes: si un dato no aparece, usa null.\n\nTexto:\n{source}"
)


def _load_extraction(path: Path) -> list[dict]:
    tasks = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            task = json.loads(line)
            task.setdefault("family", "extraction")
            tasks.append(task)
    return tasks


def _load_code(path: Path) -> list[dict]:
    tasks = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            task = json.loads(line)
            task.setdefault("family", "code")
            task["_dataset_dir"] = str(path.parent)
            tasks.append(task)
    return tasks


def load_dataset(dataset_dir: Path) -> list[dict]:
    tasks: list[dict] = []
    ext = dataset_dir / "extraction" / "tasks.jsonl"
    code = dataset_dir / "code" / "manifest.jsonl"
    if ext.exists():
        tasks.extend(_load_extraction(ext))
    if code.exists():
        tasks.extend(_load_code(code))
    if not tasks:
        raise SystemExit(f"no se encontraron datasets en {dataset_dir}")
    return tasks


def build_prompt(task: dict) -> str:
    if task["family"] == "extraction":
        keys = ", ".join(task["expected"].keys())
        return EXTRACTION_PROMPT.format(keys=keys, source=task["source"])
    return task["prompt"]


def cmd_run(args: argparse.Namespace) -> int:
    dataset_dir = Path(args.dataset)
    tasks = load_dataset(dataset_dir)

    if args.adapter == "mock":
        adapter = MockAdapter(args.run_dir)
        model_name = args.label or f"mock:{Path(args.run_dir).name}"
    else:
        adapter = OpenAICompatibleAdapter(
            model=args.model,
            base_url=args.base_url,
            api_key=args.api_key,
            temperature=args.temperature,
            max_retries=args.retries,
        )
        model_name = args.label or args.model

    if args.family:
        tasks = [t for t in tasks if t["family"] == args.family]
    if args.limit:
        tasks = tasks[: args.limit]

    results = []
    errors = 0
    for index, task in enumerate(tasks, start=1):
        prompt = build_prompt(task)
        try:
            output = adapter.generate(task, prompt)
        except AdapterError as exc:
            print(f"[{index}/{len(tasks)}] {task['id']}: ERROR {exc}", file=sys.stderr)
            errors += 1
            continue
        result = grade(task, output)
        results.append(result)
        mark = "ok " if result.passed else "FAIL"
        print(f"[{index}/{len(tasks)}] {mark} {task['id']} ({result.family})")

    if not results:
        print("no se evaluó ningún caso", file=sys.stderr)
        return 1

    summary = build_summary(results, model_name, args.rate)
    md_path, json_path = write_report(args.out, summary, results)

    print()
    print(f"Acierto: {summary['pass_rate'] * 100:.1f}% "
          f"(IC95 {summary['ci95'][0] * 100:.1f}-{summary['ci95'][1] * 100:.1f})")
    print(f"Fallos: {summary['failed']}/{summary['n']} | "
          f"coste/100 outputs: ${summary['cost_per_100_outputs']:.0f}")
    print(f"Informe: {md_path}")
    print(f"JSON:    {json_path}")
    if errors:
        print(f"Errores de adapter: {errors}", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="audit", description="Audita la calidad real de una salida de IA.")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="ejecuta el golden set contra un modelo")
    run.add_argument("--dataset", default="datasets")
    run.add_argument("--adapter", choices=["mock", "openai"], default="mock")
    run.add_argument("--run-dir", default="runs/demo-model", help="solo adapter=mock")
    run.add_argument("--model", default="gpt-4.1-mini")
    run.add_argument("--base-url", default=None)
    run.add_argument("--api-key", default=None)
    run.add_argument("--temperature", type=float, default=0.0)
    run.add_argument("--retries", type=int, default=6, help="reintentos ante 429/402")
    run.add_argument("--label", default=None, help="nombre del modelo en el informe")
    run.add_argument("--rate", type=float, default=80.0, help="USD/hora para estimar retrabajo")
    run.add_argument("--family", choices=["extraction", "code"], default=None)
    run.add_argument("--limit", type=int, default=None)
    run.add_argument("--out", default="reports/latest")
    run.set_defaults(func=cmd_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
