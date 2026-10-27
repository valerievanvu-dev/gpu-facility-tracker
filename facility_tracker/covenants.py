"""Quarterly financial covenant tests and how much room is left before each one breaks."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Quarter


@dataclass(frozen=True)
class CovenantResult:
    name: str
    actual: float
    threshold: float
    direction: str  # "min" or "max"
    unit: str       # "x", "%" or "$"
    headroom_note: str

    @property
    def passed(self) -> bool:
        if self.direction == "min":
            return self.actual >= self.threshold
        return self.actual <= self.threshold


def debt_service(terms: dict) -> float:
    """Quarterly interest plus scheduled principal."""
    return terms["outstanding"] * terms["all_in_rate"] / 4 + terms["quarterly_amortization"]


def check_quarter(q: Quarter, terms: dict, total_collateral_value: float,
                 revenue_shock: float = 0.0) -> list[CovenantResult]:
    cov = terms["covenants"]
    revenue = q.revenue * (1 - revenue_shock)
    cash_flow = revenue - q.cash_operating_expenses
    ds = debt_service(terms)

    dscr = cash_flow / ds
    # Revenue decline that would bring DSCR exactly to the minimum (costs held flat).
    rev_cushion = (cash_flow - cov["min_dscr"] * ds) / revenue if revenue else 0.0

    ltv = terms["outstanding"] / total_collateral_value if total_collateral_value else float("inf")
    # Collateral value decline that would bring LTV exactly to the maximum.
    value_cushion = 1 - (terms["outstanding"] / cov["max_ltv"]) / total_collateral_value

    liquidity = q.cash_balance

    return [
        CovenantResult("Debt service coverage ratio (DSCR)", dscr, cov["min_dscr"], "min", "x",
                       f"Revenue could fall {rev_cushion:.0%} before breach" if rev_cushion >= 0
                       else f"In breach: needs {-rev_cushion:.0%} more revenue"),
        CovenantResult("Loan-to-value (LTV)", ltv, cov["max_ltv"], "max", "%",
                       f"Collateral value could fall {value_cushion:.0%} before breach" if value_cushion >= 0
                       else f"In breach: needs {-value_cushion / (1 - value_cushion):.0%} less debt"),
        CovenantResult("Minimum liquidity", liquidity, cov["min_liquidity"], "min", "$",
                       f"${(liquidity - cov['min_liquidity']) / 1e6:,.1f}M above the floor" if liquidity >= cov["min_liquidity"]
                       else f"${(cov['min_liquidity'] - liquidity) / 1e6:,.1f}M below the floor"),
    ]
