# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-17. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1531 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1531 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1570 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.17 | 0.000 | -0.023 | 0.115 | — | — |
| Accountant CPA | +1.29 | 0.227 | +0.029 | 0.478 | +1.39 | 0.031 |
| Issuer-current | +2.06 | 0.066 | +0.085 | 0.380 | +2.41 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.012 | 0.001 | +2.07 | 0.002 |
| Investment prof. | (sep.) | 1.000 | -0.014 | 0.002 | +0.09 | 0.933 |
| Academic | +1.40 | 0.336 | +0.166 | 0.337 | +1.88 | 0.016 |
| Industry pract. | +0.82 | 0.450 | +0.017 | 0.589 | +0.71 | 0.291 |
| Legal pract. | +3.47 | 0.004 | +0.238 | 0.277 | +2.67 | 0.027 |
| Trade assoc. | +2.45 | 0.085 | +0.302 | 0.265 | +1.69 | 0.204 |
| Student | +2.55 | 0.025 | +0.128 | 0.341 | +1.59 | 0.156 |
| log(words+1) | +0.61 | 0.016 | +0.008 | 0.042 | +0.70 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1531 | -92.41 | 0.133 |
| LPM   | 1531   | (OLS) | R²=0.052, adj-R²=0.046 |
| Ordinal logit | 1570 | -244.99 | 0.153 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -244.99
- Multinomial logit LL: -236.88
- LR = 2 × (-236.88 − -244.99) = 16.21, df = 10, p = 0.0938

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.0938 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
