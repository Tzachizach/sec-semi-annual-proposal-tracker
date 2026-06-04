# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-04. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=618 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=618 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=643 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.88 | 0.000 | -0.028 | 0.234 | — | — |
| Accountant CPA | +1.73 | 0.123 | +0.061 | 0.410 | +1.92 | nan |
| Issuer-current | +2.31 | 0.063 | +0.175 | 0.347 | +2.61 | nan |
| Issuer-former | (sep.) | 1.000 | -0.018 | 0.015 | +1.91 | nan |
| Investment prof. | (sep.) | 1.000 | -0.019 | 0.022 | (sep.) | nan |
| Academic | +1.91 | 0.237 | +0.289 | 0.273 | +2.24 | nan |
| Industry pract. | (sep.) | 1.000 | -0.022 | 0.030 | -0.40 | nan |
| Legal pract. | (sep.) | 1.000 | +0.989 | 0.000 | (sep.) | nan |
| Student | +3.24 | 0.015 | +0.311 | 0.268 | +2.48 | nan |
| log(words+1) | +0.61 | 0.047 | +0.010 | 0.117 | +0.74 | nan |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 618 | -45.40 | 0.233 |
| LPM   | 618   | (OLS) | R²=0.159, adj-R²=0.146 |
| Ordinal logit | 643 | -122.17 | 0.259 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -122.17
- Multinomial logit LL: -115.50
- LR = 2 × (-115.50 − -122.17) = 13.33, df = 9, p = 0.1481

Under H0 (proportional odds holds), LR follows χ²(9). p = 0.1481 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 4 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.', 'Legal pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Legal pract.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
