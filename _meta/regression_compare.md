# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-22. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=273 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=273 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=298 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.43 | 0.000 | -0.056 | 0.138 | — | — |
| Accountant CPA | +1.31 | 0.255 | +0.062 | 0.482 | +1.40 | 0.053 |
| Issuer-current | +1.59 | 0.202 | +0.150 | 0.438 | +1.94 | 0.003 |
| Issuer-former | (sep.) | 0.933 | -0.035 | 0.015 | +1.32 | 0.126 |
| Investment prof. | (sep.) | 0.968 | -0.038 | 0.027 | (sep.) | 0.916 |
| Academic | +1.10 | 0.493 | +0.244 | 0.341 | +1.66 | 0.056 |
| Industry pract. | (sep.) | 0.976 | -0.045 | 0.031 | -0.97 | 0.391 |
| Student | +3.38 | 0.032 | +0.458 | 0.225 | +3.18 | 0.101 |
| log(words+1) | +0.66 | 0.034 | +0.021 | 0.065 | +0.68 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 273 | -34.41 | 0.198 |
| LPM   | 273   | (OLS) | R²=0.111, adj-R²=0.084 |
| Ordinal logit | 298 | -101.58 | 0.211 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -101.58
- Multinomial logit LL: -96.33
- LR = 2 × (-96.33 − -101.58) = 10.51, df = 8, p = 0.2313

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.2313 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
