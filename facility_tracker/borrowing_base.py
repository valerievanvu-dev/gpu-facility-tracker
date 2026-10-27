"""Borrowing base: how much the borrower may draw against its GPU collateral.

Steps, in the order a lender would check them:
1. Value each GPU cluster: straight-line depreciation from cost to a residual value.
2. Keep only eligible clusters: under contract with enough term left, and not past due.
3. Apply an advance rate by GPU model (newer chips get a higher rate).
4. Remove any amount above the single-customer concentration limit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .models import Cluster

DAYS_PER_MONTH = 30.4375


@dataclass(frozen=True)
class ClusterLine:
    cluster: Cluster
    collateral_value: float
    eligible: bool
    reason: str
    advance_rate: float
    advance_amount: float


@dataclass(frozen=True)
class BorrowingBase:
    as_of: date
    lines: list[ClusterLine]
    total_collateral_value: float
    eligible_advance: float
    concentration_excess: dict[str, float]
    borrowing_base: float
    commitment: float
    outstanding: float

    @property
    def availability(self) -> float:
        """Undrawn room. Negative means a borrowing base deficiency."""
        return min(self.commitment, self.borrowing_base) - self.outstanding

    @property
    def deficiency(self) -> float:
        return max(0.0, -self.availability)


def collateral_value(cluster: Cluster, as_of: date, useful_life_years: float,
                     residual_pct: float, value_shock: float = 0.0) -> float:
    """Depreciated value of a cluster, optionally haircut by a market value shock."""
    age_years = max(0.0, (as_of - cluster.in_service_date).days / 365.25)
    depreciated_share = min(age_years / useful_life_years, 1.0) * (1 - residual_pct)
    value = cluster.original_cost * (1 - depreciated_share)
    return value * (1 - value_shock)


def months_remaining(contract_end: date | None, as_of: date) -> float:
    if contract_end is None:
        return 0.0
    return (contract_end - as_of).days / DAYS_PER_MONTH


def eligibility(cluster: Cluster, as_of: date, rules: dict) -> tuple[bool, str]:
    if cluster.customer is None:
        return False, "No customer contract"
    remaining = months_remaining(cluster.contract_end, as_of)
    if remaining < rules["min_contract_months_remaining"]:
        return False, f"Contract ends in {remaining:.1f} months"
    if cluster.days_past_due > rules["max_days_past_due"]:
        return False, f"Customer {cluster.days_past_due} days past due"
    return True, "Eligible"


def compute(fleet: list[Cluster], terms: dict, as_of: date,
            value_shock: float = 0.0) -> BorrowingBase:
    lines: list[ClusterLine] = []
    for c in fleet:
        value = collateral_value(c, as_of, terms["useful_life_years"][c.gpu_model],
                                 terms["residual_value_pct"], value_shock)
        ok, reason = eligibility(c, as_of, terms["eligibility"])
        rate = terms["advance_rates"][c.gpu_model] if ok else 0.0
        lines.append(ClusterLine(c, value, ok, reason, rate, value * rate))

    eligible_advance = sum(line.advance_amount for line in lines)

    # Single-customer concentration: no customer may support more than the
    # limit's share of the eligible advance. (Simplified one-pass test.)
    by_customer: dict[str, float] = {}
    for line in lines:
        if line.eligible:
            by_customer[line.cluster.customer] = by_customer.get(line.cluster.customer, 0.0) + line.advance_amount
    cap = terms["concentration_limit_pct"] * eligible_advance
    excess = {cust: amt - cap for cust, amt in by_customer.items() if amt > cap}

    return BorrowingBase(
        as_of=as_of,
        lines=lines,
        total_collateral_value=sum(line.collateral_value for line in lines),
        eligible_advance=eligible_advance,
        concentration_excess=excess,
        borrowing_base=eligible_advance - sum(excess.values()),
        commitment=terms["commitment"],
        outstanding=terms["outstanding"],
    )
