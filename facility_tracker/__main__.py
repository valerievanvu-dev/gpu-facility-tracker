"""Command line: python -m facility_tracker --period 2026-Q3"""

from __future__ import annotations

import argparse
from pathlib import Path

from . import borrowing_base, covenants, report, stress
from .models import load_financials, load_fleet, load_terms

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Quarterly borrowing base and covenant report for a GPU-backed facility.")
    parser.add_argument("--period", default="2026-Q3", help="Quarter to report, e.g. 2026-Q3")
    parser.add_argument("--data", type=Path, default=ROOT / "data", help="Folder with facility.json, fleet.csv, financials.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "reports", help="Where to write the report files")
    parser.add_argument("--no-excel", action="store_true", help="Skip the Excel workbook")
    args = parser.parse_args()

    terms = load_terms(args.data / "facility.json")
    fleet = load_fleet(args.data / "fleet.csv")
    quarter = load_financials(args.data / "financials.csv")[args.period]
    as_of = quarter.period_end

    bb = borrowing_base.compute(fleet, terms, as_of)
    results = covenants.check_quarter(quarter, terms, bb.total_collateral_value)
    grid = stress.run(fleet, terms, quarter, as_of)

    args.out.mkdir(parents=True, exist_ok=True)
    md_path = args.out / f"{args.period}_compliance_certificate.md"
    md_path.write_text(report.markdown(terms, quarter, bb, results, grid))
    print(f"Wrote {md_path}")
    if not args.no_excel:
        xlsx_path = args.out / f"{args.period}_lender_package.xlsx"
        report.excel(xlsx_path, terms, quarter, bb, results, grid)
        print(f"Wrote {xlsx_path}")

    print()
    for r in results:
        print(f"{'PASS' if r.passed else 'FAIL'}  {r.name}: {r.headroom_note}")
    print(f"Borrowing base ${bb.borrowing_base:,.0f} | outstanding ${bb.outstanding:,.0f} | availability ${bb.availability:,.0f}")


if __name__ == "__main__":
    main()
