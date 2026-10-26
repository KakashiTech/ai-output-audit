"""Adapters: how the harness talks to a model under test.

Two options:

* ``mock``  - replay recorded outputs from a JSONL file. Lets anyone audit a
  model they do not have credentials for, and makes results reproducible.
* ``openai`` - any OpenAI-compatible endpoint (OpenAI, Ollama, vLLM, LM Studio,
  OpenRouter...). No SDK, just urllib, so the harness stays dependency-free.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path


class AdapterError(RuntimeError):
    pass


class MockAdapter:
    name = "mock"

    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir)
        self._cache: dict[str, dict[str, str]] = {}

    def _load(self, family: str) -> dict[str, str]:
        if family in self._cache:
            return self._cache[family]
        path = self.run_dir / f"{family}.jsonl"
        if not path.exists():
            raise AdapterError(f"no hay outputs grabados en {path}")
        records = {}
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                records[row["task_id"]] = row["output"]
        self._cache[family] = records
        return records

    def generate(self, task: dict, prompt: str) -> str:
        records = self._load(task["family"])
        if task["id"] not in records:
            raise AdapterError(f"falta output para {task['id']} en {self.run_dir}")
        return records[task["id"]]


class OpenAICompatibleAdapter:
    name = "openai-compatible"

    def __init__(
        self,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
        temperature: float = 0.0,
        timeout_s: int = 120,
    ):
        self.model = model
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.temperature = temperature
        self.timeout_s = timeout_s

    def generate(self, task: dict, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "temperature": self.temperature,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Eres un asistente técnico. Responde solo con el "
                            "artefacto pedido, sin explicaciones ni disculpas."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            }
        ).encode()
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                body = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:500]
            raise AdapterError(f"HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise AdapterError(f"no se pudo conectar a {self.base_url}: {exc.reason}") from exc
        return body["choices"][0]["message"]["content"]
