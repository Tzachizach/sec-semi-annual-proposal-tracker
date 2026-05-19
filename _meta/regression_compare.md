# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-19. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=244 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=244 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=267 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -5.63 | 0.000 | -0.034 | 0.355 | — | — |
| Accountant CPA | +1.36 | 0.239 | +0.065 | 0.464 | +1.41 | 0.052 |
| Issuer-current | +1.82 | 0.147 | +0.159 | 0.408 | +2.14 | 0.001 |
| Issuer-former | (sep.) | 1.000 | -0.030 | 0.031 | +0.70 | 0.536 |
| Investment prof. | (sep.) | 1.000 | -0.034 | 0.047 | (sep.) | 0.964 |
| Academic | +2.13 | 0.248 | +0.422 | 0.227 | +2.36 | 0.021 |
| Industry pract. | (sep.) | 1.000 | -0.033 | 0.047 | -0.50 | 0.659 |
| Student | +3.46 | 0.024 | +0.465 | 0.213 | +3.22 | 0.088 |
| log(words+1) | +0.46 | 0.163 | +0.015 | 0.172 | +0.59 | 0.001 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 244 | -30.97 | 0.196 |
| LPM   | 244   | (OLS) | R²=0.132, adj-R²=0.103 |
| Ordinal logit | 267 | -91.92 | 0.214 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -91.92
- Multinomial logit LL: -86.79
- LR = 2 × (-86.79 − -91.92) = 10.25, df = 8, p = 0.2478

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.2478 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): the same 4 entity buckets carry zero Support letters and are flagged separated — Accountant CPA, Issuer-former, Investment professional, Industry practitioner.
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
