"""Stress grid: what happens if GPU resale values and rental revenue fall together."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from . import borrowing_base, covenants
from .models import Cluster, Quarter

VALUE_SHOCKS = [0.0, 0.10, 0.20, 0.30, 0.40]
REVENUE_SHOCKS = [0.0, 0.10, 0.20, 0.30]


@dataclass(frozen=True)
class StressCell:
    value_shock: float
    revenue_shock: float
    availability: float
    all_covenants_pass: bool
    failed: list[str]


def run(fleet: list[Cluster], terms: dict, q: Quarter, as_of: date) -> list[StressCell]:
    cells = []
    for vs in VALUE_SHOCKS:
        bb = borrowing_base.compute(fleet, terms, as_of, value_shock=vs)
        for rs in REVENUE_SHOCKS:
            results = covenants.check_quarter(q, terms, bb.total_collateral_value, revenue_shock=rs)
            failed = [r.name for r in results if not r.passed]
            cells.append(StressCell(vs, rs, bb.availability, not failed, failed))
    return cells
