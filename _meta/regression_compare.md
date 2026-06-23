# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-23. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1996 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1996 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=2037 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.12 | 0.000 | -0.018 | 0.151 | — | — |
| Accountant CPA | +1.25 | 0.244 | +0.025 | 0.481 | +1.34 | 0.039 |
| Issuer-current | +2.08 | 0.057 | +0.066 | 0.381 | +2.48 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.010 | 0.001 | +2.14 | 0.001 |
| Investment prof. | (sep.) | 1.000 | -0.012 | 0.002 | -0.04 | 0.971 |
| Academic | +1.78 | 0.214 | +0.173 | 0.320 | +2.15 | 0.005 |
| Industry pract. | +0.84 | 0.436 | +0.015 | 0.583 | +0.73 | 0.271 |
| Legal pract. | +2.62 | 0.019 | +0.113 | 0.339 | +1.66 | 0.133 |
| Trade assoc. | +2.79 | 0.049 | +0.308 | 0.255 | +1.94 | 0.144 |
| Student | +2.55 | 0.023 | +0.113 | 0.344 | +1.56 | 0.159 |
| log(words+1) | +0.55 | 0.024 | +0.007 | 0.057 | +0.68 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1996 | -102.75 | 0.118 |
| LPM   | 1996   | (OLS) | R²=0.042, adj-R²=0.037 |
| Ordinal logit | 2037 | -269.08 | 0.152 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -269.08
- Multinomial logit LL: -260.16
- LR = 2 × (-260.16 − -269.08) = 17.84, df = 10, p = 0.0577

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.0577 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
