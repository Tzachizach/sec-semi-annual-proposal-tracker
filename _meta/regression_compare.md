# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-19. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1864 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1864 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1904 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.03 | 0.000 | -0.019 | 0.155 | — | — |
| Accountant CPA | +1.23 | 0.253 | +0.025 | 0.484 | +1.32 | 0.043 |
| Issuer-current | +2.02 | 0.065 | +0.065 | 0.386 | +2.42 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.011 | 0.001 | +2.08 | 0.002 |
| Investment prof. | (sep.) | 1.000 | -0.012 | 0.002 | +0.04 | 0.971 |
| Academic | +1.73 | 0.226 | +0.171 | 0.323 | +2.08 | 0.007 |
| Industry pract. | +0.87 | 0.416 | +0.016 | 0.580 | +0.77 | 0.247 |
| Legal pract. | +2.56 | 0.022 | +0.112 | 0.342 | +1.60 | 0.149 |
| Trade assoc. | +2.73 | 0.053 | +0.307 | 0.257 | +1.88 | 0.155 |
| Student | +2.49 | 0.027 | +0.112 | 0.347 | +1.50 | 0.177 |
| log(words+1) | +0.55 | 0.026 | +0.007 | 0.057 | +0.67 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1864 | -101.71 | 0.116 |
| LPM   | 1864   | (OLS) | R²=0.042, adj-R²=0.036 |
| Ordinal logit | 1904 | -265.05 | 0.143 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -265.05
- Multinomial logit LL: -256.93
- LR = 2 × (-256.93 − -265.05) = 16.23, df = 10, p = 0.0932

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.0932 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
