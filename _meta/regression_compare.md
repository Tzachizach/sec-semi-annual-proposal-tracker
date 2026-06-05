# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-05. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=684 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=684 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=709 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.92 | nan | -0.025 | 0.250 | — | — |
| Accountant CPA | +1.55 | nan | +0.051 | 0.434 | +1.73 | nan |
| Issuer-current | +2.46 | nan | +0.178 | 0.337 | +2.74 | nan |
| Issuer-former | (sep.) | nan | -0.016 | 0.014 | +2.03 | nan |
| Investment prof. | (sep.) | nan | -0.017 | 0.022 | (sep.) | nan |
| Academic | +1.84 | nan | +0.214 | 0.304 | +2.17 | nan |
| Industry pract. | (sep.) | nan | -0.019 | 0.029 | -0.28 | nan |
| Legal pract. | (sep.) | nan | +0.991 | 0.000 | (sep.) | nan |
| Trade assoc. | +0.00 | nan | +0.000 | 0.534 | +0.00 | nan |
| Student | +3.37 | nan | +0.314 | 0.263 | +2.59 | nan |
| log(words+1) | +0.59 | nan | +0.009 | 0.128 | +0.73 | nan |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 684 | -46.72 | 0.227 |
| LPM   | 684   | (OLS) | R²=0.151, adj-R²=0.140 |
| Ordinal logit | 709 | -125.80 | 0.254 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -125.80
- Multinomial logit LL: -119.55
- LR = 2 × (-119.55 − -125.80) = 12.51, df = 10, p = 0.2521

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.2521 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 4 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.', 'Legal pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Legal pract.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
