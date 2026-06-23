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
| Constant | -7.76 | 0.000 | -0.031 | 0.038 | — | — |
| Accountant CPA | +1.05 | 0.344 | +0.023 | 0.517 | +1.20 | 0.077 |
| Issuer-current | +2.00 | 0.069 | +0.064 | 0.396 | +2.33 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.012 | 0.001 | +2.12 | 0.002 |
| Investment prof. | (sep.) | 1.000 | -0.015 | 0.001 | -0.16 | 0.877 |
| Academic | +1.29 | 0.367 | +0.163 | 0.345 | +1.33 | 0.084 |
| Industry pract. | +0.68 | 0.530 | +0.013 | 0.648 | +0.44 | 0.526 |
| Legal pract. | +1.80 | 0.166 | +0.105 | 0.341 | +1.05 | 0.369 |
| Trade assoc. | +1.98 | 0.186 | +0.294 | 0.273 | +1.10 | 0.432 |
| Student | +2.46 | 0.029 | +0.110 | 0.357 | +1.48 | 0.182 |
| log(words+1) | +0.70 | 0.002 | +0.010 | 0.014 | +0.83 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1996 | -100.42 | 0.138 |
| LPM   | 1996   | (OLS) | R²=0.045, adj-R²=0.040 |
| Ordinal logit | 2037 | -262.23 | 0.173 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -262.23
- Multinomial logit LL: -252.84
- LR = 2 × (-252.84 − -262.23) = 18.78, df = 10, p = 0.0432

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.0432 → reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
