"""Load facility terms, the GPU fleet and quarterly financials from the data folder."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Cluster:
    cluster_id: str
    gpu_model: str
    units: int
    unit_cost: float
    in_service_date: date
    customer: str | None
    contract_end: date | None
    monthly_contract_revenue: float
    days_past_due: int

    @property
    def original_cost(self) -> float:
        return self.units * self.unit_cost


@dataclass(frozen=True)
class Quarter:
    period: str
    period_end: date
    revenue: float
    cash_operating_expenses: float
    cash_balance: float


def _date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def load_terms(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_fleet(path: Path) -> list[Cluster]:
    with open(path, newline="") as f:
        return [
            Cluster(
                cluster_id=row["cluster_id"],
                gpu_model=row["gpu_model"],
                units=int(row["units"]),
                unit_cost=float(row["unit_cost"]),
                in_service_date=_date(row["in_service_date"]),
                customer=row["customer"] or None,
                contract_end=_date(row["contract_end"]),
                monthly_contract_revenue=float(row["monthly_contract_revenue"] or 0),
                days_past_due=int(row["days_past_due"] or 0),
            )
            for row in csv.DictReader(f)
        ]


def load_financials(path: Path) -> dict[str, Quarter]:
    with open(path, newline="") as f:
        quarters = [
            Quarter(
                period=row["period"],
                period_end=_date(row["period_end"]),
                revenue=float(row["revenue"]),
                cash_operating_expenses=float(row["cash_operating_expenses"]),
                cash_balance=float(row["cash_balance"]),
            )
            for row in csv.DictReader(f)
        ]
    return {q.period: q for q in quarters}
