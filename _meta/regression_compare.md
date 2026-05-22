# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-22. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=278 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=278 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=303 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.49 | 0.000 | -0.056 | 0.134 | — | — |
| Accountant CPA | +1.32 | 0.249 | +0.062 | 0.479 | +1.42 | 0.050 |
| Issuer-current | +1.60 | 0.200 | +0.150 | 0.437 | +1.95 | 0.003 |
| Issuer-former | (sep.) | 0.943 | -0.034 | 0.015 | +1.34 | 0.122 |
| Investment prof. | (sep.) | 0.975 | -0.038 | 0.028 | (sep.) | 0.915 |
| Academic | +1.10 | 0.498 | +0.245 | 0.340 | +1.66 | 0.056 |
| Industry pract. | (sep.) | 0.982 | -0.045 | 0.031 | -0.97 | 0.393 |
| Student | +3.39 | 0.032 | +0.458 | 0.225 | +3.19 | 0.100 |
| log(words+1) | +0.66 | 0.032 | +0.021 | 0.064 | +0.69 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 278 | -34.49 | 0.199 |
| LPM   | 278   | (OLS) | R²=0.112, adj-R²=0.085 |
| Ordinal logit | 303 | -101.81 | 0.213 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -101.81
- Multinomial logit LL: -96.53
- LR = 2 × (-96.53 − -101.81) = 10.56, df = 8, p = 0.2278

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.2278 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
