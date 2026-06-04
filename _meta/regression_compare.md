# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-04. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=586 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=586 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=611 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.09 | 0.000 | -0.021 | 0.401 | — | — |
| Accountant CPA | +1.72 | 0.124 | +0.061 | 0.410 | +1.88 | 0.008 |
| Issuer-current | +2.44 | 0.047 | +0.176 | 0.341 | +2.64 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.018 | 0.019 | +1.88 | 0.026 |
| Investment prof. | (sep.) | 1.000 | -0.019 | 0.028 | (sep.) | 0.897 |
| Academic | +2.34 | 0.132 | +0.293 | 0.267 | +2.38 | 0.005 |
| Industry pract. | +1.16 | 0.306 | +0.039 | 0.519 | +0.51 | 0.547 |
| Student | +3.29 | 0.012 | +0.312 | 0.265 | +2.48 | 0.072 |
| log(words+1) | +0.43 | 0.129 | +0.009 | 0.212 | +0.65 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 586 | -49.64 | 0.152 |
| LPM   | 586   | (OLS) | R²=0.076, adj-R²=0.064 |
| Ordinal logit | 611 | -126.76 | 0.222 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -126.76
- Multinomial logit LL: -119.75
- LR = 2 × (-119.75 − -126.76) = 14.03, df = 8, p = 0.0811

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.0811 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
