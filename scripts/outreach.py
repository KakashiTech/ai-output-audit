#!/usr/bin/env python3
"""Consola de outreach con aprobación humana.

Flujo:
  outbox/drafts/    -> borradores generados desde el CSV
  outbox/approved/  -> el humano mueve aquí lo que aprueba
  outbox/sent/      -> el script mueve lo enviado
  inbox/            -> respuestas descargadas por IMAP

Seguridad:
  * Sin ``--send`` no se envía nada: solo simula.
  * Solo se leen los JSON de ``--dir`` (por defecto ``outbox/approved``).
  * Las credenciales se leen de un archivo local fuera del repo.

Uso:
  python3 scripts/outreach.py draft --csv data/targets.csv \\
      --template templates/agency_es.txt --out outbox/drafts
  python3 scripts/outreach.py send --dir outbox/approved --limit 10 --send
  python3 scripts/outreach.py fetch --limit 20 --out inbox
  python3 scripts/outreach.py status
"""

from __future__ import annotations

import argparse
import csv
import imaplib
import json
import os
import re
import smtplib
import ssl
import sys
import time
from datetime import datetime, timezone
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV = Path.home() / ".config" / "ai-output-audit" / "mail.env"
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def load_env(path: Path) -> None:
    """Load KEY=VALUE pairs without overwriting the real environment."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_template(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines or not lines[0].lower().startswith("asunto:"):
        raise ValueError("la plantilla debe empezar con una línea 'Asunto:'")
    subject = lines[0].split(":", 1)[1].strip()
    body = "\n".join(lines[1:]).strip()
    if not subject or not body:
        raise ValueError("la plantilla no tiene asunto o cuerpo")
    return subject, body


def render(text: str, row: dict[str, str]) -> str:
    try:
        result = text.format_map(row)
    except KeyError as exc:
        raise ValueError(f"falta la columna {exc.args[0]!r} en el CSV") from exc
    unresolved = PLACEHOLDER_RE.search(result)
    if unresolved:
        raise ValueError(f"placeholder sin resolver: {unresolved.group(0)}")
    return result


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:60] or "sin-nombre"


def read_targets(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    with path.open(encoding="utf-8", newline="") as fh:
        for raw in csv.DictReader(fh):
            row = {(k or "").strip(): (v or "").strip() for k, v in raw.items()}
            email = row.get("email", "")
            if not EMAIL_RE.match(email):
                continue
            if row.get("estado", "").lower() not in ("", "nuevo"):
                continue
            if email.lower() in seen:
                continue
            seen.add(email.lower())
            rows.append(row)
    return rows


def build_draft(subject_t: str, body_t: str, row: dict[str, str]) -> dict:
    return {
        "to": row["email"],
        "subject": render(subject_t, row),
        "body": render(body_t, row),
        "meta": {
            key: row.get(key, "")
            for key in ("nombre", "empresa", "ciudad", "senal")
        },
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def cmd_draft(args: argparse.Namespace) -> int:
    template = Path(args.template).read_text(encoding="utf-8")
    subject_t, body_t = parse_template(template)
    rows = read_targets(Path(args.csv))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    created = skipped = 0
    for index, row in enumerate(rows, start=1):
        try:
            draft = build_draft(subject_t, body_t, row)
        except ValueError as exc:
            print(f"omitido {row.get('email')}: {exc}", file=sys.stderr)
            skipped += 1
            continue
        name = f"{index:03d}-{slugify(row.get('empresa') or row['email'])}.json"
        path = out / name
        if path.exists() and not args.force:
            skipped += 1
            continue
        path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
        created += 1

    print(f"{created} borradores en {out}; {skipped} omitidos")
    return 0


def _draft_preview(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_send(args: argparse.Namespace) -> int:
    directory = Path(args.dir)
    files = sorted(directory.glob("*.json"))[: args.limit]
    if not files:
        print(f"no hay borradores en {directory}")
        return 0

    if not args.send:
        print("SIMULACIÓN: no se envía nada. Añade --send para enviar de verdad.")
        for path in files:
            draft = _draft_preview(path)
            print(f"- {draft['to']}: {draft['subject']}")
        return 0

    load_env(Path(args.env))
    required = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM"]
    missing = [key for key in required if not os.environ.get(key)]
    if missing:
        print(f"faltan variables en {args.env}: {', '.join(missing)}", file=sys.stderr)
        return 2

    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    sender = os.environ["SMTP_FROM"]
    sender_name = os.environ.get("SMTP_FROM_NAME", "").strip()

    sent_dir = Path(args.sent_dir)
    sent_dir.mkdir(parents=True, exist_ok=True)
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    sent = failed = 0
    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls(context=context)
        smtp.login(user, password)
        for path in files:
            draft = _draft_preview(path)
            if not EMAIL_RE.match(draft.get("to", "")):
                print(f"ERROR {path.name}: destinatario inválido", file=sys.stderr)
                failed += 1
                continue
            message = EmailMessage()
            message["From"] = f"{sender_name} <{sender}>" if sender_name else sender
            message["To"] = draft["to"]
            message["Subject"] = draft["subject"]
            if draft.get("in_reply_to"):
                message["In-Reply-To"] = draft["in_reply_to"]
                message["References"] = draft["in_reply_to"]
            message.set_content(draft["body"])
            try:
                smtp.send_message(message)
            except Exception as exc:  # noqa: BLE001 - queremos seguir con el resto
                print(f"ERROR {path.name}: {exc}", file=sys.stderr)
                failed += 1
                continue
            path.rename(sent_dir / path.name)
            with log_path.open("a", encoding="utf-8") as log:
                log.write(
                    json.dumps(
                        {
                            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "to": draft["to"],
                            "subject": draft["subject"],
                            "file": path.name,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            sent += 1
            print(f"enviado {draft['to']}")
            time.sleep(args.delay)

    print(f"{sent} enviados; {failed} fallidos")
    return 0 if failed == 0 else 1


def cmd_fetch(args: argparse.Namespace) -> int:
    load_env(Path(args.env))
    required = ["IMAP_HOST", "IMAP_USER", "IMAP_PASSWORD"]
    missing = [key for key in required if not os.environ.get(key)]
    if missing:
        print(f"faltan variables en {args.env}: {', '.join(missing)}", file=sys.stderr)
        return 2

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    conn = imaplib.IMAP4_SSL(os.environ["IMAP_HOST"])
    try:
        conn.login(os.environ["IMAP_USER"], os.environ["IMAP_PASSWORD"])
        conn.select("INBOX")
        status, data = conn.search(None, "UNSEEN")
        if status != "OK":
            print("no se pudo buscar en INBOX", file=sys.stderr)
            return 1
        ids = data[0].split()[-args.limit :]
        saved = 0
        for uid in ids:
            status, payload = conn.fetch(uid, "(RFC822)")
            if status != "OK" or not payload or not isinstance(payload[0], tuple):
                continue
            message = BytesParser(policy=policy.default).parsebytes(payload[0][1])
            body_part = message.get_body(preferencelist=("plain",))
            body = body_part.get_content() if body_part else message.get_content()
            text = (
                f"# {message.get('subject', '(sin asunto)')}\n\n"
                f"**De:** {message.get('from', '')}  \n"
                f"**Para:** {message.get('to', '')}  \n"
                f"**Fecha:** {message.get('date', '')}  \n\n"
                f"---\n\n{body}\n"
            )
            name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uid.decode()}.md"
            (out / name).write_text(text, encoding="utf-8")
            if args.mark_seen:
                conn.store(uid, "+FLAGS", "\\Seen")
            saved += 1
        print(f"{saved} mensajes guardados en {out}")
        return 0
    finally:
        try:
            conn.logout()
        except Exception:  # noqa: BLE001
            pass


def cmd_status(_: argparse.Namespace) -> int:
    for folder in ("outbox/drafts", "outbox/approved", "outbox/sent", "inbox"):
        path = ROOT / folder
        count = len(list(path.glob("*"))) if path.exists() else 0
        print(f"{folder:18} {count}")
    log = ROOT / "outbox" / "sent.jsonl"
    if log.exists():
        lines = log.read_text(encoding="utf-8").splitlines()[-5:]
        print("\nÚltimos envíos:")
        for line in lines:
            row = json.loads(line)
            print(f"- {row['ts']} {row['to']}: {row['subject']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="outreach", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    draft = sub.add_parser("draft", help="genera borradores desde el CSV")
    draft.add_argument("--csv", default="data/targets.csv")
    draft.add_argument("--template", required=True)
    draft.add_argument("--out", default="outbox/drafts")
    draft.add_argument("--force", action="store_true")
    draft.set_defaults(func=cmd_draft)

    send = sub.add_parser("send", help="envía lo aprobado (sin --send solo simula)")
    send.add_argument("--dir", default="outbox/approved")
    send.add_argument("--sent-dir", default="outbox/sent")
    send.add_argument("--log", default="outbox/sent.jsonl")
    send.add_argument("--env", default=str(DEFAULT_ENV))
    send.add_argument("--limit", type=int, default=10)
    send.add_argument("--delay", type=float, default=3.0)
    send.add_argument("--send", action="store_true")
    send.set_defaults(func=cmd_send)

    fetch = sub.add_parser("fetch", help="descarga respuestas no leídas")
    fetch.add_argument("--out", default="inbox")
    fetch.add_argument("--env", default=str(DEFAULT_ENV))
    fetch.add_argument("--limit", type=int, default=20)
    fetch.add_argument("--mark-seen", action="store_true")
    fetch.set_defaults(func=cmd_fetch)

    status = sub.add_parser("status", help="cuenta borradores, enviados y respuestas")
    status.set_defaults(func=cmd_status)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
