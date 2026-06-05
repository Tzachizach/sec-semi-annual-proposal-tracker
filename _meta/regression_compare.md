# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-05. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=709 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=709 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=734 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.99 | nan | -0.025 | 0.246 | — | — |
| Accountant CPA | +1.59 | nan | +0.051 | 0.429 | +1.76 | nan |
| Issuer-current | +2.48 | nan | +0.178 | 0.335 | +2.77 | nan |
| Issuer-former | (sep.) | nan | -0.015 | 0.015 | +2.07 | nan |
| Investment prof. | (sep.) | nan | -0.016 | 0.022 | (sep.) | nan |
| Academic | +1.85 | nan | +0.214 | 0.302 | +2.19 | nan |
| Industry pract. | (sep.) | nan | -0.019 | 0.030 | -0.26 | nan |
| Legal pract. | (sep.) | nan | +0.991 | 0.000 | (sep.) | nan |
| Trade assoc. | +0.00 | nan | -0.000 | 0.050 | +0.00 | nan |
| Student | +3.40 | nan | +0.314 | 0.262 | +2.62 | nan |
| log(words+1) | +0.60 | nan | +0.009 | 0.128 | +0.74 | nan |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 709 | -46.96 | 0.228 |
| LPM   | 709   | (OLS) | R²=0.151, adj-R²=0.140 |
| Ordinal logit | 734 | -126.38 | 0.256 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -126.38
- Multinomial logit LL: -120.09
- LR = 2 × (-120.09 − -126.38) = 12.57, df = 10, p = 0.2488

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.2488 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 4 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.', 'Legal pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Legal pract.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
