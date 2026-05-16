# Entity classification methodology

Letters are classified by who is writing — what kind of commenter the writer is — across **eight buckets**. The taxonomy was refined with input from Brian Monsen, drawing on his experience classifying FASB comment letters. Each letter is independently classified under three rubrics, and the headline entity on the tracker is the **majority of three**.

## The eight buckets

1. **Individual** — Default dump bucket. Retail/personal commenters. We deliberately use "Individual" (not "Individual investor") because the investor claim is costless — every American with a retirement account could truthfully make it — and using the term dilutes the *Investment professional* signal.
2. **Accountant (CPA)** — CPA or chartered accountant credential, speaking from that professional lens.
3. **Issuer / Corporate — current** — Active corporate role at a public-company issuer or operating corporation (CFO, audit chair, financial reporting manager, etc.).
4. **Issuer / Corporate — former** — Retired or former corporate executives writing personally. Distinct population from current insiders — their commenting incentives plausibly differ (e.g., board-seat-seeking rather than investor advocacy).
5. **Investment professional** — Active asset managers, hedge fund principals, financial advisors, RIAs, equity analysts/traders.
6. **Academic researcher** — University faculty appointment (professor, named chair, etc.).
7. **Industry practitioner / technologist** — Non-academic professional credentials outside corporate-issuer / investment-firm worlds: CISSP, software developer, IT auditor, compliance professional, technical program manager, etc.
8. **Student** — Currently enrolled student.

## The three rubrics

**Rater 1 — Primary (balanced).** Holistic read with the "follow-the-letterhead" principle as a tiebreaker: classify by the affiliation under which the writer is *speaking*, not just the credentials they list. Since SEC web-form submissions don't show actual letterhead, this rater uses four cues to infer speaking-as-individual vs. speaking-on-behalf-of-institution: (a) register and prose quality, (b) length, (c) whether the substance engages with issuer cost-burden concerns vs. retail-investor protection, (d) whether the institution is named for credibility or for attribution.

**Rater 2 — Self-described (literal first identifier).** Takes the very first identifier the writer offers, with no override. "CPA and retail investor" → Accountant; "Individual investor and former CFO" → Individual. Strict literal version of how the writer chose to introduce themselves.

**Rater 3 — Letterhead / functional (strongest institutional affiliation).** Deliberately opposing prior — overrides self-description with the strongest functional credential. Priority order: current institutional role > former institutional role > formal professional credential > sector descriptor > self-id. A "CEO, ACME Corp" who calls themselves "an individual investor" goes to *Issuer / Corporate — current* under this rubric.

The three are designed to bracket the space of reasonable disagreement. Letters where all three agree are unambiguous; letters where they disagree flag the genuinely-hard cases (the "CPA and retail investor" pattern, the short-letter-from-a-CEO pattern, the consulting-business-owner pattern, etc.).

## Agreement statistics (N = 137)

- **Unanimous (all three agree):** 125 letters (91.2%)
- **2-of-3 majority:** 12 letters (8.8%)
- **3-way splits:** 0

Pairwise raw agreement:
- Primary vs Self-described: 91.2%
- Primary vs Letterhead: 93.4%
- Self-described vs Letterhead: 97.8%

Cohen's κ:
- Primary vs Self-described: 0.814
- Primary vs Letterhead: 0.863
- Self-described vs Letterhead: 0.957

Fleiss' κ (3-rater): **0.880** — substantial agreement, notably higher than the stance ensemble (κ = 0.503). Role-string parsing is more mechanical than reading-between-the-lines for hedged stance language, which is what we'd expect.

## Headline distribution by rater

| Bucket | Primary | Self-described | Letterhead | **Majority** |
|---|---:|---:|---:|---:|
| Individual | 101 | 96 | 94 | **94** |
| Accountant (CPA) | 7 | 9 | 9 | **9** |
| Issuer / Corporate — current | 5 | 7 | 8 | **8** |
| Issuer / Corporate — former | 2 | 5 | 5 | **5** |
| Investment professional | 8 | 8 | 8 | **8** |
| Academic researcher | 4 | 4 | 4 | **4** |
| Industry practitioner / technologist | 8 | 6 | 7 | **7** |
| Student | 2 | 2 | 2 | **2** |

## The eleven contested letters

These are the 11 letters where the three raters disagreed:
- **#1, #36** (substance vs. credential — "CPA and retail investor" / "Individual investor and compliance professional"): Primary went Individual / Industry practitioner; Self-described and Letterhead pushed to Accountant / Industry practitioner.
- **#3, #6** ("former bank/realtor employee" or "former hotel real-estate manager"): Self-described said Individual (first identifier); Letterhead and Primary pushed to Issuer-former.
- **#13 Skyler Mathis** (Texas CPA + Financial Reporting Manager at Par Pacific): all three landed on Issuer / Corporate — current via the letterhead rule.
- **#25 Isaiah Owolabi** (LL.M. + Founder/CEO ESGine): Self-described and Letterhead went Issuer-current; Primary read it as practitioner.
- **#56 David Bach** (Bach Financial Literacy Consulting): Primary went Industry practitioner; Self-described and Letterhead split.
- **#62 John Cheppo** ("Retired (decades in companies)"): Self-described went Issuer-former; Primary read the role string as too generic to credibly tag and stayed at Individual.
- **#69 Marly Reese** ("Investor & CPA"): Self-described kept Individual (investor leads); Primary and Letterhead pushed to Accountant.
- **#94 Nathan Powers** ("Owner, Good Faith Co" + "on behalf of regular everyday investors"): substance/register pulled Primary toward Individual, while role pulled Letterhead toward Issuer-current.

The majority of three plus an agreement badge on each row gives readers a transparent view of which calls are robust and which are debatable.

## Reproducibility

Source data: `_meta/renumbered_records.json` (each record now carries `entity_primary`, `entity_selfdescribed`, `entity_letterhead`, `entity_majority`, `entity_agreement`).

Per-rater outputs:
- `_meta/entity_rater_primary.json`
- `_meta/entity_rater_selfdescribed.json`
- `_meta/entity_rater_letterhead.json`
- `_meta/entity_three_rater.json` (merged with majority + agreement)
