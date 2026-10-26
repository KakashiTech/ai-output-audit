"""Generate a reproducible demo run.

The outputs below emulate a model that is mostly right and occasionally wrong
in the four ways that actually cost money: invented identifiers, unit errors,
field omission and unparseable formatting. Regenerating this file must always
produce the same audit numbers, otherwise the demo is worthless.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "demo-model"


def ext(**kwargs) -> str:
    return json.dumps(
        {
            "part_number": kwargs["part"],
            "vin_min": kwargs["vin_min"],
            "vin_max": kwargs["vin_max"],
            "iq_typ_ua": kwargs["iq"],
            "package": kwargs["package"],
            "temp_min_c": kwargs["tmin"],
            "temp_max_c": kwargs["tmax"],
        },
        ensure_ascii=False,
    )


EXTRACTION = {
    "ext_001": ext(part="APX7301", vin_min=2.7, vin_max=5.5, iq=12, package="SOT-23-5", tmin=-40, tmax=125),
    # toma la corriente de shutdown (0.8 uA) en vez de la de reposo (45 uA)
    "ext_002": ext(part="LRB-4820", vin_min=4.5, vin_max=36, iq=0.8, package="MSOP-8", tmin=-40, tmax=150),
    "ext_003": ext(part="VX-2210", vin_min=3.0, vin_max=18, iq=3.5, package="DFN-6", tmin=-55, tmax=125),
    # error de unidad: 1.2 uA convertido a mA
    "ext_004": ext(part="NW-1104", vin_min=0.9, vin_max=3.6, iq=0.0012, package="WLCSP-4", tmin=-20, tmax=85),
    # identificador inventado que no existe en la fuente
    "ext_005": ext(part="TRX-6010", vin_min=8, vin_max=60, iq=150, package="TO-220-3", tmin=-40, tmax=125),
    "ext_006": ext(part="SXL-3302", vin_min=2.5, vin_max=16, iq=22, package="SOIC-8", tmin=-40, tmax=105),
    # omite el encapsulado
    "ext_007": json.dumps(
        {
            "part_number": "HLP-7541",
            "vin_min": 1.8,
            "vin_max": 5.0,
            "iq_typ_ua": 0.35,
            "temp_min_c": -40,
            "temp_max_c": 85,
        }
    ),
    "ext_008": ext(part="MTR-8800", vin_min=6, vin_max=100, iq=90, package="HTSSOP-16", tmin=-40, tmax=150),
    # formato inaceptable: prosa en vez de JSON
    "ext_009": (
        "Claro, aquí tienes los datos del QNX-2214: es un controlador USB-C "
        "que acepta de 2.9 V a 32 V, consume 7.5 uA en standby, viene en QFN-12 "
        "y aguanta de -40 C a 125 C. Avísame si necesitas algo más."
    ),
    "ext_010": ext(part="BLT-5503", vin_min=1.1, vin_max=4.2, iq=18, package="SOT-23-3", tmin=0, tmax=70),
}


CODE = {
    "code_001": '''```python
import re


def parse_duration(text: str) -> int:
    total = 0
    for value, unit in re.findall(r"(\\d+)([hms])", text):
        total += int(value) * {"h": 3600, "m": 60, "s": 1}[unit]
    return total
```''',
    # off-by-one: se come el último trozo cuando la lista no es múltiplo exacto
    "code_002": '''```python
def chunk(lst, n):
    if n <= 0:
        raise ValueError("n must be positive")
    return [lst[i:i + n] for i in range(0, len(lst) - 1, n)]
```''',
    "code_003": '''```python
def safe_div(a, b):
    if b == 0:
        return None
    return a / b
```''',
    "code_004": '''```python
def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc
```''',
    # off-by-one: devuelve len(xs)-n ventanas en vez de len(xs)-n+1
    "code_005": '''```python
def moving_average(xs, n):
    if n <= 0 or n > len(xs):
        raise ValueError("invalid window")
    return [sum(xs[i:i + n]) / n for i in range(len(xs) - n)]
```''',
}


def write_jsonl(path: Path, records: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for task_id, output in records.items():
            fh.write(json.dumps({"task_id": task_id, "output": output}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    write_jsonl(RUN / "extraction.jsonl", EXTRACTION)
    write_jsonl(RUN / "code.jsonl", CODE)
    print(f"escrito en {RUN}")
