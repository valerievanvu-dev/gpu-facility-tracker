"""Hand-checkable tests: each expected number can be worked out on paper."""

from datetime import date
from pathlib import Path

import pytest

from facility_tracker import borrowing_base as bb
from facility_tracker import covenants
from facility_tracker.models import Cluster, Quarter, load_financials, load_fleet, load_terms

DATA = Path(__file__).resolve().parent.parent / "data"
AS_OF = date(2026, 9, 30)


def cluster(**kw):
    base = dict(cluster_id="X", gpu_model="H100", units=100, unit_cost=10_000,
                in_service_date=date(2026, 9, 30), customer="Customer A",
                contract_end=date(2028, 9, 30), monthly_contract_revenue=0, days_past_due=0)
    base.update(kw)
    return Cluster(**base)


def terms(**kw):
    t = load_terms(DATA / "facility.json")
    t.update(kw)
    return t


def test_new_cluster_is_worth_cost():
    assert bb.collateral_value(cluster(), AS_OF, 5, 0.15) == pytest.approx(1_000_000)


def test_fully_depreciated_cluster_keeps_residual_value():
    old = cluster(in_service_date=date(2015, 1, 1))
    assert bb.collateral_value(old, AS_OF, 5, 0.15) == pytest.approx(150_000)


def test_value_shock_is_applied_after_depreciation():
    assert bb.collateral_value(cluster(), AS_OF, 5, 0.15, value_shock=0.2) == pytest.approx(800_000)


@pytest.mark.parametrize("kw, reason", [
    (dict(customer=None, contract_end=None), "No customer contract"),
    (dict(contract_end=date(2026, 12, 31)), "Contract ends in"),
    (dict(days_past_due=75), "past due"),
])
def test_ineligible_clusters(kw, reason):
    ok, why = bb.eligibility(cluster(**kw), AS_OF, terms()["eligibility"])
    assert not ok and reason in why


def test_concentration_excess_is_removed():
    # Two equal customers: each is 50% of the eligible advance, above a 35% limit.
    fleet = [cluster(cluster_id="A"), cluster(cluster_id="B", customer="Customer B")]
    result = bb.compute(fleet, terms(concentration_limit_pct=0.35), AS_OF)
    eligible = 2 * 1_000_000 * 0.70
    assert result.eligible_advance == pytest.approx(eligible)
    assert sum(result.concentration_excess.values()) == pytest.approx(2 * (eligible / 2 - 0.35 * eligible))


def test_deficiency_when_debt_exceeds_borrowing_base():
    result = bb.compute([cluster()], terms(outstanding=1_000_000, concentration_limit_pct=1.0), AS_OF)
    assert result.borrowing_base == pytest.approx(700_000)
    assert result.deficiency == pytest.approx(300_000)


def test_dscr_and_headroom():
    t = terms(outstanding=100_000_000, all_in_rate=0.08, quarterly_amortization=3_000_000)
    q = Quarter("Q", AS_OF, revenue=20_000_000, cash_operating_expenses=10_000_000, cash_balance=50_000_000)
    dscr, ltv, liq = covenants.check_quarter(q, t, total_collateral_value=200_000_000)
    # Debt service = 100M * 8% / 4 + 3M = 5M; cash flow = 10M; DSCR = 2.0x
    assert dscr.actual == pytest.approx(2.0) and dscr.passed
    # Revenue can fall until cash flow = 1.25 * 5M = 6.25M, i.e. by 3.75M of 20M = 18.75%
    assert "19%" in dscr.headroom_note
    assert ltv.actual == pytest.approx(0.5) and ltv.passed
    assert liq.passed


def test_sample_data_ties_out():
    t = load_terms(DATA / "facility.json")
    fleet = load_fleet(DATA / "fleet.csv")
    q = load_financials(DATA / "financials.csv")["2026-Q3"]
    result = bb.compute(fleet, t, q.period_end)
    assert result.borrowing_base == pytest.approx(result.eligible_advance - sum(result.concentration_excess.values()))
    assert result.availability == pytest.approx(min(t["commitment"], result.borrowing_base) - t["outstanding"])
    assert all(r.passed for r in covenants.check_quarter(q, t, result.total_collateral_value))
