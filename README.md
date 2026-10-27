# GPU Facility Tracker

Every quarter, a company that borrows against its GPUs (graphics processing units) owes its lenders the same package: a borrowing base certificate, a covenant compliance certificate and supporting schedules. At most companies this lives in a spreadsheet that someone rebuilds by hand.

This project automates that package. Point it at three files (the facility terms, the GPU fleet and the quarterly financials) and it produces:

- a **compliance certificate** in Markdown, ready to paste into a lender update
- a **lender workbook** in Excel with the covenant tests, the borrowing base schedule (with live formulas) and a stress grid
- a **stress test** showing how much room is left if GPU resale values and rental revenue fall together

All data in this repository is fictional. The borrower, customers and facility terms are illustrative, not based on any real company or loan.

## What it calculates

**Borrowing base.** How much the borrower may draw against its GPUs:

1. Values each GPU cluster with straight-line depreciation from cost down to a residual value, by chip generation.
2. Keeps only eligible collateral: clusters under a customer contract with at least six months left, and customers no more than 60 days past due.
3. Applies an advance rate by chip (for example 75% for B200s, 50% for older A100s).
4. Removes any amount above the single-customer concentration limit (35% in the sample).

If debt outstanding exceeds the borrowing base, the report flags a deficiency and the mandatory prepayment.

**Financial covenants.** Each test reports pass or fail, plus the headroom in plain terms:

| Covenant | What it measures | Headroom shown as |
|---|---|---|
| Debt service coverage ratio (DSCR) | Quarterly cash flow ÷ interest and scheduled principal | How far revenue can fall before breach |
| Loan-to-value (LTV) | Debt ÷ value of all GPU collateral | How far GPU values can fall before breach |
| Minimum liquidity | Cash on hand against a floor | Dollars above the floor |

**Stress grid.** Reruns everything across GPU value declines of 0–40% and revenue declines of 0–30%, so you can see where the facility breaks before the lender asks.

## Sample output (2026-Q3, fictional data)

| Covenant | Actual | Requirement | Status | Headroom |
|---|---|---|---|---|
| Debt service coverage ratio (DSCR) | 2.21x | ≥ 1.25x | Pass | Revenue could fall 14% before breach |
| Loan-to-value (LTV) | 51.6% | ≤ 75% | Pass | Collateral value could fall 31% before breach |
| Minimum liquidity | $33.5M | ≥ $15.0M | Pass | $18.5M above the floor |

Borrowing base: **$220.2M** against $190.0M outstanding, leaving $30.2M available. Three clusters are excluded (an expiring contract, a past-due customer and uncontracted capacity), and two customers are trimmed for concentration. A 20% drop in GPU values would create a borrowing base deficiency even though every covenant still passes, which is exactly the kind of risk a quarterly spreadsheet tends to miss.

See the full certificate in [`reports/2026-Q3_compliance_certificate.md`](reports/2026-Q3_compliance_certificate.md).

## Run it

```bash
pip install -r requirements.txt
python -m facility_tracker --period 2026-Q3
python -m pytest
```

To use your own numbers, edit the three files in `data/`:

- `facility.json`: commitment, outstanding balance, rate, amortization, advance rates, eligibility rules, concentration limit and covenant levels
- `fleet.csv`: one row per GPU cluster with model, units, cost, in-service date, customer, contract end, monthly revenue and days past due
- `financials.csv`: one row per quarter with revenue, cash operating expenses and cash balance

## How it was built

I built this with AI coding agents, then checked it the way I would check an analyst's model. Every core calculation has a unit test whose expected answer can be worked out on paper, and a tie-out test confirms that the borrowing base, availability and covenant results reconcile with each other on the sample data.

## Simplifications

This is a demonstration, not a production credit system. Real facilities define these terms in the credit agreement, and the agreement governs. In particular, the concentration test here is a single pass, the depreciation curve is straight-line rather than an appraisal, and debt service assumes a flat balance through the quarter.

## About

Built by [Valerie Van Vu](https://valerievu.com).
