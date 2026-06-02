#!/usr/bin/env python3
"""Integration for letters #490-#496 (2026-06-02 full update, Action run #27).

7 letters fetched via the URL-list drain in daily_fetch.py after another
CloudFront pager stale-page-1 incident (same fallback as 2026-05-31 and
2026-06-01).

Outcome: 6 Oppose in-corpus + 1 No position held out.

Per-letter notes:

- #490 Leslie (Leslie C. Moore): all-caps retail Oppose, brief. Stance
  unambiguous. Rationale IA + IP.

- #491 michael h kane: 2-word retail ("Not interested"). Primary +
  Literalist read as default Oppose (no explicit endorsement, brief
  refusal in docket context). Skeptic flips to Conditional on
  ambiguity. Majority Oppose 2-of-3. NR.

- #492 Anthony Calime Jr.: substantive self-directed-investor essay
  with Background / Assessment / Recommendation sections. Closing
  recommendation explicitly preserves quarterly reporting, but he then
  lists fallback investor protections "If semiannual reporting is
  allowed" - the same Skeptic-flip-to-Conditional alternative-proposal
  pattern as #486 Anderson. Primary + Literalist Oppose, Skeptic
  Conditional. Majority Oppose 2-of-3, stance_note. Date corrected
  05-27 -> 05-28 per docket; URL-only fetch defaulted to 05-27. Heavy
  rationale mass: IA, IP, MF, CB, FR.

- #493 Jay Richardson: 4-word retail Oppose ("Earnings should be
  quarterly."). NR.

- #494 Jorge Lemus: brief retail Oppose ("Please reject this proposal."
  + heart emoji). NR.

- #495 Mark Murray: retail Oppose framed as a retirement-account
  information requirement.

- #496 Pedro Cejudo: single Spanish word "Bueno". Matches the #308
  Anonymous "Thanks" and #293 Hunter precedents - single affirmation
  that does not substantively engage with the proposal. All three
  raters: No position. Held out of in-corpus.

RFC scan: none of the 7 engages a numbered RFC. Engagement set stays at
3 (#14, #99, #236).

PP-watch: none of the 7 carries a capture / political-pressure frame.
"""
import json, re
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RECORDS = PROJECT / "_meta" / "renumbered_records.json"
LETTERS = PROJECT / "Letters"

IND = {"primary": "Individual", "selfdescribed": "Individual", "letterhead": "Individual"}
OPP = {"primary": "Oppose", "literalist": "Oppose", "skeptic": "Oppose"}
OPP_SKEP_C = {"primary": "Oppose", "literalist": "Oppose", "skeptic": "Conditional"}
NOPOS = {"primary": "No position", "literalist": "No position", "skeptic": "No position"}

DATE_FIX = {
    492: "2026-05-28",
}

C = {}

C[490] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP", "US"]},
  "stance_evidence": "'I OPPOSE THE THREATENED CHANGE TO \"BI-ANNUAL REPORTING\"'",
  "rationale_evidence": "IA: 'CONSUMERS AND SMALL INVESTORS NEED QUARTERLY BUSINESS REPORTING TO OPTIMIZE THEIR INVESTMENT PORTFOLIOS'. IP: small-investor protection framing. (Inc) US: 'CONSUMERS' framing.",
  "summary": "All-caps retail Oppose from Leslie C. Moore: consumers and small investors need quarterly reporting to optimize their investment portfolios; opposes the bi-annual change."}

C[491] = {"stance": OPP_SKEP_C, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Not interested'",
  "rationale_evidence": "No rationale supplied. Body is two words.",
  "stance_note": "Two-word retail submission ('Not interested') in a SEC comment-portal context. Primary + Literalist read as default Oppose (no explicit endorsement of the proposal; brief refusal). Skeptic flips to Conditional on ambiguity. Majority Oppose (2-of-3).",
  "summary": "Two-word retail Oppose ('Not interested'). Ambiguous brevity flips Skeptic to Conditional; Primary + Literalist stay Oppose."}

C[492] = {"stance": OPP_SKEP_C, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "MF", "CB", "FR"], "literalist": ["IA", "IP", "MF"], "inclusive": ["IA", "IP", "MF", "CB", "FR"]},
  "stance_evidence": "'I recommend that regulators preserve quarterly reporting requirements for public companies.'",
  "rationale_evidence": "IA: 'rely on timely, standardized, and comparable company information to evaluate risks'. IP: 'individual investors typically rely heavily on public filings... may also reduce transparency for investors'. MF: 'each semiannual report could carry more surprise risk... sharper stock price reactions'. CB: 'rely on timely, standardized, and comparable company information' - standardization and comparability framing. FR: 'Less frequent reporting may make it easier for problems to remain hidden longer'.",
  "stance_note": "Skeptic flips to Conditional on the fallback proposal 'If semiannual reporting is allowed, it should include strong investor protections, such as...' (timely quarterly financial updates, explanation requirement, prompt material-change disclosure, equal-access protection). Same hedge pattern as #486 Anderson. Primary + Literalist stay Oppose because the headline recommendation - 'preserve quarterly reporting requirements' - is unambiguous. Majority Oppose (2-of-3).",
  "summary": "Substantive self-directed-investor Oppose: 401(k) + 529 retail investor argues quarterly reports give individual investors the only reliable checkpoint against six-month information gaps, increased information inequality, market-volatility surprise risk, harder portfolio rebalancing, and reduced management accountability. Recommends preserving quarterly reporting, with a fallback investor-protection package if semiannual is allowed."}

C[493] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Earnings should be quarterly.'",
  "rationale_evidence": "Bare preservation request, no rationale supplied.",
  "summary": "Four-word retail Oppose: earnings should be quarterly."}

C[494] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Please reject this proposal.'",
  "rationale_evidence": "Bare rejection request (plus heart emoji), no rationale supplied.",
  "summary": "Brief retail Oppose: please reject this proposal."}

C[495] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'My retirement accounts are heavily invested into companies and having this information provided quarterly is a requirement.'",
  "rationale_evidence": "IA: 'having this information provided quarterly is a requirement'. IP: retirement-account framing (investor protection through information access).",
  "summary": "One-line retail Oppose: retirement accounts heavily invested; quarterly information is a requirement."}

C[496] = {"stance": NOPOS, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Bueno'",
  "rationale_evidence": "Single-word Spanish affirmation; no engagement with the proposal.",
  "stance_note": "Matches the #308 Anonymous 'Thanks' and #293 Hunter precedents: single affirmation that does not substantively engage with the proposal merits. All three raters return No position. Held out of in-corpus.",
  "summary": "Single Spanish word 'Bueno' - does not substantively engage with the proposal. Held out as No position per the precedent set by #308 ('Thanks')."}


def majority_rationales(per_rater):
    counts = Counter()
    for codes in per_rater.values():
        for c in codes:
            counts[c] += 1
    return sorted([c for c, n in counts.items() if n >= 2])

records = json.loads(RECORDS.read_text())
by_n = {r["n"]: r for r in records}

for n, calls in C.items():
    rec = by_n[n]
    rec["primary_stance"] = calls["stance"]["primary"]
    rec["literalist_stance"] = calls["stance"]["literalist"]
    rec["skeptic_stance"] = calls["stance"]["skeptic"]
    sv = Counter(calls["stance"].values()).most_common(1)[0][0]
    rec["majority_stance"] = sv
    rec["stance"] = sv
    rec["agreement"] = "Unanimous" if len(set(calls["stance"].values())) == 1 else "2-of-3"

    rec["entity_primary"] = calls["entity"]["primary"]
    rec["entity_selfdescribed"] = calls["entity"]["selfdescribed"]
    rec["entity_letterhead"] = calls["entity"]["letterhead"]
    ev = Counter(calls["entity"].values()).most_common(1)[0][0]
    rec["entity_majority"] = ev
    rec["entity"] = ev
    rec["entity_agreement"] = "Unanimous" if len(set(calls["entity"].values())) == 1 else "2-of-3"

    rec["rationales_primary"] = calls["rationales"]["primary"]
    rec["rationales_literalist"] = calls["rationales"]["literalist"]
    rec["rationales_inclusive"] = calls["rationales"]["inclusive"]
    rec["rationales_majority"] = majority_rationales(calls["rationales"])
    rec["rationales"] = rec["rationales_majority"]
    cats = [set(calls["rationales"]["primary"]),
            set(calls["rationales"]["literalist"]),
            set(calls["rationales"]["inclusive"])]
    rec["rationale_agreement"] = "Unanimous" if cats[0] == cats[1] == cats[2] else "2-of-3"
    rec["rationale_evidence"] = calls.get("rationale_evidence", "")
    rec["summary"] = calls.get("summary", rec.get("summary", ""))
    if "stance_note" in calls:
        rec["stance_note"] = calls["stance_note"]

    if n in DATE_FIX:
        rec["date"] = DATE_FIX[n]

    md = next(LETTERS.glob(f"{n}_*.md"), None)
    if md:
        body = md.read_text()
        body_text = body.split("---", 2)[-1] if "---" in body else body
        rec["words"] = len(re.findall(r"\b\w+\b", body_text))

RECORDS.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
print(f"Updated {len(C)} records: #{min(C)}-#{max(C)}")

for n, calls in C.items():
    md = next(LETTERS.glob(f"{n}_*.md"), None)
    if not md:
        continue
    text = md.read_text()
    head, sep, body = text.partition("---")
    new_head = re.sub(r"^- \*\*Stance:\*\*.*$", f"- **Stance:** {by_n[n]['stance']}", head, flags=re.MULTILINE)
    new_head = re.sub(r"^- \*\*Entity:\*\*.*$", f"- **Entity:** {by_n[n]['entity']}", new_head, flags=re.MULTILINE)
    new_head = re.sub(r"^- \*\*Rationales:\*\*.*$", f"- **Rationales:** {', '.join(by_n[n]['rationales'])}", new_head, flags=re.MULTILINE)
    if n in DATE_FIX:
        new_head = re.sub(r"^- \*\*Date:\*\*.*$", f"- **Date:** {DATE_FIX[n]}", new_head, flags=re.MULTILINE)
    md.write_text(new_head + sep + body)

print("Letters/*.md headers rewritten.")

HOLD = {"Off-topic", "No position", "Duplicate"}
in_corp = [r for r in records if r["stance"] not in HOLD]
counts = Counter(r["stance"] for r in in_corp)
print(f"\nIn-corpus N={len(in_corp)} of {len(records)}: " + " / ".join(f"{n} {s}" for s, n in counts.most_common()))
held = Counter(r["stance"] for r in records if r["stance"] in HOLD)
print(f"Held out: " + " / ".join(f"{n} {s}" for s, n in held.most_common()))
