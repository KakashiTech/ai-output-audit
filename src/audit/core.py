"""Core data model, statistics and failure taxonomy.

The harness is deliberately dependency-free: everything here is standard
library. A client should be able to run it without trusting a supply chain.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Failure taxonomy
#
# Severity is the expected cost of NOT catching the failure in production.
# 4 = silently wrong fact that propagates downstream
# 3 = wrong by a factor / wrong unit (dangerous in engineering data)
# 2 = missing or malformed field (visible, cheap to fix)
# 1 = cosmetic
# ---------------------------------------------------------------------------

SEVERITY_MINUTES: dict[int, int] = {4: 60, 3: 30, 2: 15, 1: 5}

SEVERITY_LABEL: dict[int, str] = {
    4: "crítico",
    3: "alto",
    2: "medio",
    1: "bajo",
}


@dataclass(frozen=True)
class Failure:
    kind: str
    field: str | None
    detail: str
    severity: int

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "field": self.field,
            "detail": self.detail,
            "severity": self.severity,
        }


@dataclass
class TaskResult:
    task_id: str
    family: str
    passed: bool
    failures: list[Failure] = field(default_factory=list)
    output: str = ""
    duration_s: float = 0.0

    def as_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "family": self.family,
            "passed": self.passed,
            "failures": [f.as_dict() for f in self.failures],
            "output": self.output,
            "duration_s": round(self.duration_s, 3),
        }


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Small golden sets are the norm in this business (20-500 cases). Reporting
    a bare percentage hides how uncertain it is, which is exactly the same
    sin we accuse AI vendors of. So we always report an interval.
    """
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def rework_cost(failures: list[Failure], hourly_rate: float = 80.0) -> dict:
    """Translate failures into money.

    Clients do not buy percentages. They buy "this costs you $X per 100
    outputs". The minutes are a starting assumption, not a law of physics:
    they are exposed in the report so the client can argue with them.
    """
    minutes = sum(SEVERITY_MINUTES.get(f.severity, 10) for f in failures)
    hours = minutes / 60
    return {
        "minutes": minutes,
        "hours": round(hours, 2),
        "usd": round(hours * hourly_rate, 2),
        "hourly_rate": hourly_rate,
    }
