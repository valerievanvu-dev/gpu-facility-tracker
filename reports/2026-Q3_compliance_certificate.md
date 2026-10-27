# Compliance certificate: 2026-Q3

**Borrower:** Northwind Inference, Inc. (fictional)  
**Facility:** Senior Secured GPU Term Facility  
**As of:** 2026-09-30

> Fictional borrower and illustrative terms, for demonstration only.

## Summary

- **Covenants:** All covenants met
- **Borrowing base:** $220.2M against $190.0M outstanding. No borrowing base deficiency
- **Availability:** $30.2M undrawn

## Financial covenants

| Covenant | Actual | Requirement | Status | Headroom |
|---|---|---|---|---|
| Debt service coverage ratio (DSCR) | 2.21x | ≥ 1.25x | Pass | Revenue could fall 14% before breach |
| Loan-to-value (LTV) | 51.6% | ≤ 75% | Pass | Collateral value could fall 31% before breach |
| Minimum liquidity | $33.5M | ≥ $15.0M | Pass | $18.5M above the floor |

## Borrowing base

| Cluster | GPU | Units | Customer | Collateral value | Eligible | Advance rate | Advance |
|---|---|---:|---|---:|---|---:|---:|
| SFO-01 | H100 | 3,072 | Customer A | $51.7M | Eligible | 70% | $36.2M |
| SFO-02 | H100 | 1,536 | Customer B | $28.8M | Eligible | 70% | $20.1M |
| DAL-01 | H200 | 2,304 | Customer C | $57.9M | Eligible | 70% | $40.5M |
| DAL-02 | B200 | 3,072 | Customer D | $112.9M | Eligible | 75% | $84.7M |
| DAL-03 | B200 | 1,536 | Customer A | $61.8M | Eligible | 75% | $46.4M |
| PHX-01 | A100 | 4,096 | Customer E | $10.4M | Contract ends in 3.0 months | 0% | $0.0M |
| PHX-02 | H100 | 768 | Customer F | $13.6M | Customer 75 days past due | 0% | $0.0M |
| PHX-03 | H200 | 1,152 | — | $31.2M | No customer contract | 0% | $0.0M |
| **Total** | | | | **$368.2M** | | | **$227.9M** |

- Less concentration excess, Customer A (above 35% limit): -$2.8M
- Less concentration excess, Customer D (above 35% limit): -$4.9M
- **Borrowing base: $220.2M**

## Stress test

Availability under combined declines in GPU collateral value (rows) and quarterly revenue (columns). Cells marked ✗ breach at least one covenant. Negative availability means a borrowing base deficiency, which requires a mandatory prepayment even if every covenant is met.

| Value decline | Revenue −0% | Revenue −10% | Revenue −20% | Revenue −30% |
|---|---:|---:|---:|---:|
| −0% | $30.2M ✓ | $30.2M ✓ | $30.2M ✗ | $30.2M ✗ |
| −10% | $8.2M ✓ | $8.2M ✓ | $8.2M ✗ | $8.2M ✗ |
| −20% | -$13.8M ✓ | -$13.8M ✓ | -$13.8M ✗ | -$13.8M ✗ |
| −30% | -$35.9M ✓ | -$35.9M ✓ | -$35.9M ✗ | -$35.9M ✗ |
| −40% | -$57.9M ✗ | -$57.9M ✗ | -$57.9M ✗ | -$57.9M ✗ |
