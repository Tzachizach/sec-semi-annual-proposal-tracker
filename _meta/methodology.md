# Classification methodology — S7-2026-15 comment-letter tracker

## Why three raters

Classifying a comment letter as "Support" or "Oppose" is inherently subjective, especially for letters that propose modifications, offer compromises, or hedge. A single classifier's call reflects that classifier's priors. The accounting and management-research literature on LLM annotation (Carlson & Burbano, *SMJ* 2026; Liu, *CHB* 2026; Tornberg 2024) recommends running multiple prompt variants and reporting agreement to give readers a sense of how robust the labels are.

The site shows three independent classifications of each letter, plus a majority vote, plus an "agreement" flag so readers know which letters were easy vs. contested.

## The three rubrics

**Rater 1 — Primary (balanced).** The original classification used since the tracker launched. Reads each letter holistically and assigns Support / Oppose / Conditional based on the dominant position. Conditional is used when the writer proposes a substantive modification or condition.

**Rater 2 — Literalist (conservative default).** Defaults to Oppose unless the letter contains explicit, unconditional endorsement language ("I support…", "I urge the Commission to adopt…", "I am writing in favor…"). Conditional is reserved for letters with explicit "if X then yes" structure. Asks: would a strict pre-LLM keyword search agree?

**Rater 3 — Skeptic (hedge-aware default).** Defaults to Conditional unless the letter is unambiguous and one-directional. Any qualification, concession to the other side, suggested alternative, or "but / however" trigger flips the call to Conditional. Asks: would a careful reader hesitate at all?

The three rubrics are designed to bracket the space of reasonable disagreement. Literalist and Skeptic are deliberately set as opposing priors so that letters where they agree are likely robust, and letters where they disagree are likely the genuinely-hard cases.

## Agreement statistics (N = 137)

- **Unanimous (all three rubrics agree):** 105 letters (76.6%)
- **2-of-3 agreement:** 32 letters (23.4%)
- **3-way splits:** 0 (impossible with 3 raters and 3 categories)

Pairwise raw agreement:
- Primary vs. Literalist: 89.8%
- Primary vs. Skeptic: 85.4%
- Literalist vs. Skeptic: 78.1%

Cohen's κ:
- Primary vs. Literalist: 0.573 (moderate)
- Primary vs. Skeptic: 0.619 (substantial)
- Literalist vs. Skeptic: 0.355 (fair) — the largest gap, as expected since these are deliberately opposing priors

Fleiss' κ (3-rater): **0.503** — moderate agreement, comparable to the 0.40–0.60 range typically reported in published comment-letter and policy-text annotation work, and roughly matching the human-rater κ of 0.6–0.7 reported by the recent LLM-validation literature once Conditional is included as a category.

## Stance distribution by rater

| Stance | Primary | Literalist | Skeptic | Majority |
|---|---:|---:|---:|---:|
| Oppose | 113 | 125 | 97 | 113 |
| Conditional | 16 | 7 | 36 | 18 |
| Support | 8 | 5 | 4 | 6 |

The pattern is what the rubrics predict: Literalist absorbs hedged letters into Oppose; Skeptic absorbs them into Conditional. Primary sits between them. Majority vote is therefore close to Primary but pulls a few letters into Conditional where Primary called Oppose.

## How to read the agreement flag on the site

Each letter card shows a small badge:
- **Unanimous** — all three rubrics agree. High-confidence classification.
- **2/3 majority** — two rubrics agree, one dissents. Read the letter; reasonable disagreement.
- (No 3-way splits possible.)

The dashboard charts use the **Majority** label by default. The Primary label is also shown for continuity with earlier snapshots of the data.

## Reproducibility

All three rater outputs are stored in `_meta/`:
- `rater_literalist.json` — per-letter literalist call + trigger language
- `rater_skeptic.json` — per-letter skeptic call + trigger language
- `three_rater_results.json` — merged with majority + agreement flag
- `renumbered_records.json` — each record now also carries `primary_stance`, `literalist_stance`, `skeptic_stance`, `majority_stance`, `agreement`

The full rubrics are in `_meta/methodology.md` (this file). Source references for the multi-prompt-ensemble approach are in `_meta/methodology_papers/INDEX.md`.

## Planned: crowd validation

A blind-judgment-with-reveal voting mechanism is being added to the public site (see `_meta/methodology_papers/INDEX.md` under "Blind-judgment-with-reveal designs"). Each visitor will be shown a letter without the algorithmic classification, asked to judge it on a Likert scale and on a small per-issue rubric (cadence, assurance, retail concern, etc.), then shown the algorithmic call and the running crowd distribution. The crowd's aggregate will be reported alongside the three rubrics as a fourth rater.
