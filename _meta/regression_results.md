# SEC S7-2026-15 — regression results

_Last run: 2026-05-14. Will update as the docket grows._

## Specification

- **Outcome:** binary indicator, 1 if letter is Support, 0 if Oppose.
- **Sample:** 141 letters classified as either Oppose (135) or Support (6). Conditional letters and PDF-only letters dropped.
- **Independent variables:**
  - 7 entity-type dummies (reference: Individual).
  - `log(words+1)` — natural log of letter word count.

## Logit results

| Variable | Coef | SE | p-value | Odds ratio | 95% CI for OR |
|---|---:|---:|---:|---:|---|
| Constant | -4.96 | 2.03 | 0.015 | 0.01 | [0.00, 0.38] |
| Accountant (CPA) | -9.80 | (huge) | 0.972 | ≈ 0 | (separated) |
| Issuer / Corporate — current | +1.89 | 1.31 | 0.147 | 6.63 | [0.51, 85.76] |
| Issuer / Corporate — former | -9.11 | (huge) | 0.974 | ≈ 0 | (separated) |
| Investment professional | -11.82 | (huge) | 0.987 | ≈ 0 | (separated) |
| Academic researcher | +2.51 | 2.01 | 0.211 | 12.31 | [0.24, 628.45] |
| Industry practitioner / technologist | -12.60 | (huge) | 0.990 | ≈ 0 | (separated) |
| Student | +3.44 | 1.56 | 0.027 | 31.32 | [1.48, 661.24] |
| log(words+1) | +0.33 | 0.43 | 0.445 | 1.38 | [0.60, 3.19] |

**Fit:** McFadden pseudo-R² = 0.250, N = 141.

## Interpretation

Run `python3 _scripts/run_regression.py` again after new letters are added to refresh the numbers above.
Reading the coefficients: positive values increase the odds of Support relative to Oppose. The reference category for entity dummies is Individual.

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimation: `statsmodels.discrete.discrete_model.Logit`, default optimizer.