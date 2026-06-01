#!/usr/bin/env python3
"""Integration for letters #463-#473 (2026-06-01 update, Action run #25).

11 new letters from page 1 of the docket. CloudFront pager is stale again
(same pattern as 2026-05-31 / Action run #23): the index crawl saw only the
newest items, so pages 2 and 3 carry ~15+ more backfilled May-27 letters that
this Action run did NOT capture. Those will land via the URL-list drain
(`process_url_list` in daily_fetch.py reading `_meta/_harvest/new_urls.txt`).

SEC date typo: #463 Eileen Sickler, #464 Homer Hill, #465 John Beck are tagged
"2026-06-27" in the docket but every other entry around them is 05-27, and
Homer Hill's PDF body explicitly says "May 27, 2026". Treated as 05-27 with
the typo flagged in `date_note`.

Outcome: 11 Oppose / 0 Support / 0 Conditional / 0 Off-topic / 0 No-position.
Entities: 11 Individual (the "retired CPA" letterhead rater fires twice on
#463 Sickler and #465 Beck, but Primary + Self-described both fall on
Individual because the investor framing dominates the text body, so the
majority stays Individual — same pattern as #347 Fodera / #430 Thurston).

RFC scan: none of the 11 cites or answers a numbered RFC. Engagement count
stays 3 (#14, #99, #236).

FLAGS:
- #467 Bill Kraynak and #473 Ginger Riddle carry the "certified 10-Q vs
  voluntary corporate communications" template language that already recurs
  across #331 Burgeson, #338 Hartfelder, #344 Lewis (now #382 DeSonier
  references the same CFA / CII 2018-19 history that Riddle cites). All carry
  AU.
- #470 Christopher Craft reads as AI-drafted (he literally calls it "a draft
  of the comment paragraphs"); substantive Oppose with the full IA/IP/MF/AU/FR
  set across the three rubrics.
- #471 Ed. Brill ends with sarcasm about abolishing the SEC; the Skeptic
  rubric reads the rhetorical "Why not once a year?" alternatives as sarcasm
  (not real alternative proposals), so stance stays Oppose, not Conditional.
- 2018-rubric extensions (GU, Trade-association bucket) remain deferred; none
  of these 11 needs them.
"""
import json, re
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RECORDS = PROJECT / "_meta" / "renumbered_records.json"
LETTERS = PROJECT / "Letters"

IND = {"primary": "Individual", "selfdescribed": "Individual", "letterhead": "Individual"}
IND_CPA_LH = {"primary": "Individual", "selfdescribed": "Individual", "letterhead": "Accountant (CPA)"}
OPP = {"primary": "Oppose", "literalist": "Oppose", "skeptic": "Oppose"}

C = {}

C[463] = {"stance": OPP, "entity": IND_CPA_LH,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP", "MF"]},
  "stance_evidence": "'I hope that companies will continue to file quarterly financial information.'",
  "rationale_evidence": "IA: 'I use the 10-Qs' to evaluate companies. IP: 'transparent and provides information that investors use'. (Inc) MF: transparency framing on market function. Letterhead reads 'Stock Club Member, CPA, Retired' but the investor capacity leads the text, so Primary + Self-described land on Individual; majority Individual.",
  "summary": "Retail Oppose from a stock-club member and retired CPA: she uses 10-Qs to evaluate companies and to update her holdings, and asks the Commission to preserve quarterly required disclosures.",
  "date_note": "SEC docket tagged 2026-06-27 (likely typo — every surrounding entry is 05-27); recorded as 05-27."}

C[464] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["NR"], "inclusive": ["IP", "FR", "AU"]},
  "stance_evidence": "'Keep it quarterly !'",
  "rationale_evidence": "IP: 'big corporations need to be held accountable' frames accountability as investor protection. Literalist reads the one phrase as too thin to code (NR). (Inc) FR: accountability framing extends to fraud-prevention; (Inc) AU: certified-filing accountability sub-frame. Per-code majority lands IP only.",
  "summary": "One-line retail Oppose: keep quarterly so big corporations stay accountable.",
  "date_note": "SEC docket tagged 2026-06-27 (typo — PDF body itself reads 'May 27, 2026'); recorded as 05-27."}

C[465] = {"stance": OPP, "entity": IND_CPA_LH,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP", "MF"]},
  "stance_evidence": "'I am an individual investor. I rely heavily on the quarterly reported information...'",
  "rationale_evidence": "IA: explicit retail information-access argument — small and medium companies without Value Line / Morningstar analyst coverage. IP: 'make solid investment decisions'. (Inc) MF: market-function framing on coverage gaps. Letterhead 'Retired CPA Inactive' but the text body opens 'I am an individual investor', so Primary + Self-described land on Individual; majority Individual.",
  "summary": "Reasoned retail Oppose: individual investors rely on quarterly reports especially for small/mid-cap companies that lack Value Line and Morningstar analyst coverage; cutting to twice a year would severely limit retail knowledge.",
  "date_note": "SEC docket tagged 2026-06-27 (typo — surrounding entries are 05-27); recorded as 05-27."}

C[466] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["NR"], "inclusive": ["IP", "IA"]},
  "stance_evidence": "'I disagree with these changes... I do not want to see changes.'",
  "rationale_evidence": "IP: 'Financial decisions are based on these quarterly reports' — investor reliance. Literalist reads as too generic (NR). (Inc) IA. Per-code majority IP only.",
  "summary": "Three-sentence retail Oppose: financial decisions rest on these quarterly reports."}

C[467] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP"], "literalist": ["AU", "IA", "IP"], "inclusive": ["AU", "IA", "IP", "MF"]},
  "stance_evidence": "'As a small investor, I request that you DO NOT approve this proposal.'",
  "rationale_evidence": "AU: explicit 'the 10-Q is reviewed by independent auditors, and the CEO and CFO sign it personally and can be held legally accountable... the voluntary corporate communications that would replace them carry none of that' — the recurring campaign template. IA: 31-year Investment Club member tracking quarterly to time buys and sells; 'we need current information'. IP: investor decisions. (Inc) MF.",
  "summary": "Substantive retail Oppose from a 31-year Investment Club member: he leans on the certified-10-Q-versus-voluntary-communications template (CEO + CFO sign and are legally accountable; the voluntary disclosures carry none of that) and on a club-level workflow that uses quarterly reports to time buys and sells."}

C[468] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["NR"], "inclusive": ["IP", "IA"]},
  "stance_evidence": "'I rely on quarterly disclosures to make informed decisions.'",
  "rationale_evidence": "IP: investor reliance on disclosure. Literalist reads the single line as too generic (NR). (Inc) IA: 'informed decisions' as retail information argument. Per-code majority IP only.",
  "summary": "One-line retail Oppose: he relies on quarterly disclosures to make informed decisions."}

C[469] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'I urge the Commission to withdraw S7-2026-15.'",
  "rationale_evidence": "Bare withdrawal request, no rationale supplied.",
  "summary": "Two-line retail Oppose: he urges the Commission to withdraw the proposal, no rationale given."}

C[470] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "MF", "AU", "FR"], "literalist": ["IP", "IA", "FR"], "inclusive": ["IA", "IP", "MF", "AU", "FR", "US"]},
  "stance_evidence": "'I am writing to express my strong opposition to the proposal to shift from quarterly to semiannual reporting.'",
  "rationale_evidence": "IA: 'agile, informed decisions'; 'Form 10-Q every single quarter'. IP: 'individual investor's ability to make informed decisions'. MF: 'six-month window creates a dangerous information vacuum'; 'market volatility and erosion of trust'. AU: 'weakens our ability to keep tabs on C-suite behavior'; 'executives would face far less immediate accountability'. FR: 'opens the door to unethical corporate behavior'. (Inc) US: 'active individual investor' framing as broader US-markets argument. Letter reads as AI-drafted (he labels it 'a draft of the comment paragraphs').",
  "summary": "Substantive retail Oppose from an active individual investor and financial literacy coach. The letter (drafted in a paragraph-by-paragraph format, likely with AI assistance) frames the six-month gap as an information vacuum that degrades transparency, weakens C-suite accountability, opens the door to unethical behavior, and erodes market confidence."}

C[471] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "MF"], "literalist": ["IP", "IA"], "inclusive": ["IA", "IP", "MF", "AL"]},
  "stance_evidence": "'As an individual investor I believe for the SEC to reduce the frequency of public reporting requirements for businesses would be a huge step backward.'",
  "rationale_evidence": "IA: 'Investors need more and better information... not less'. IP: 'make informed investment decisions'. MF: calendar-cyclic businesses, seasonal variations, comparability across half-years. (Inc) AL: the rhetorical 'why not monthly?' and 'why not once a year?' would be Alternative-cadence proposals if serious, but read as sarcasm — Inclusive carries them; Primary + Literalist do not. Skeptic stays Oppose because the alternatives are explicitly sarcastic (capped by 'let's go back a hundred years... abolish the SEC altogether and save money in a mattress').",
  "summary": "Retail Oppose with a quietly sophisticated argument about calendar-cyclic businesses (seasonal variation reduces comparability of half-year reports), wrapped in a closing rhetorical sarcasm about abolishing the SEC. Argues investors need more reporting (every 2 months, even monthly), not less."}

C[472] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'I strongly oppose moving to semiannual reporting.'",
  "rationale_evidence": "Bare opposition statement, no rationale supplied.",
  "summary": "One-line retail Oppose: strong opposition, no rationale given."}

C[473] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP"], "literalist": ["AU", "IA"], "inclusive": ["AU", "IA", "IP", "CB", "LE"]},
  "stance_evidence": "'I am opposed to the proposed changes to quarterly filings.'",
  "rationale_evidence": "AU: explicit 'a 10-Q is reviewed by independent auditors, and the CEO and CFO sign it personally and can be held legally accountable for its contents. The voluntary corporate communications that would replace them carry none of that' — the recurring template, same wording as #331/#338/#344/#467. IA: 'individual investors like me own the majority of shares in smaller public companies, the ones most likely to take the new option'. IP: 'accountability would be decreased'. (Inc) CB: she frames the reduction as net cost to investors. (Inc) LE: she cites the 2018-2019 record (CFA Institute, Council of Institutional Investors representing ~$4 trillion) as a regulatory-history argument, the same CFA-CII parallel as #382 Keith DeSonier.",
  "summary": "Substantive retail Oppose from a retired teacher: deploys the certified-10-Q-vs-voluntary-communications template (CEO + CFO sign and are legally accountable), cites the 'individual investors own the majority of shares in smaller public companies' framing the SEC itself uses, and walks through the 2018-2019 record (CFA Institute, $4T Council of Institutional Investors, the empirical research) to argue the Commission has been here before."}


# ---------- merge ----------

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

    # Date typo correction (SEC docket vs PDF body)
    if "date_note" in calls:
        rec["date"] = "2026-05-27"
        rec["date_note"] = calls["date_note"]

    # Word count
    md = next(LETTERS.glob(f"{n}_*.md"), None)
    if md:
        body = md.read_text()
        body_text = body.split("---", 2)[-1] if "---" in body else body
        rec["words"] = len(re.findall(r"\b\w+\b", body_text))

# Write
RECORDS.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
print(f"Updated {len(C)} records: #{min(C)}–#{max(C)}")

# Also rewrite each Letters/*.md header
for n, calls in C.items():
    md = next(LETTERS.glob(f"{n}_*.md"), None)
    if not md:
        continue
    text = md.read_text()
    head, sep, body = text.partition("---")
    new_head = re.sub(r"^- \*\*Stance:\*\*.*$", f"- **Stance:** {by_n[n]['stance']}", head, flags=re.MULTILINE)
    new_head = re.sub(r"^- \*\*Entity:\*\*.*$", f"- **Entity:** {by_n[n]['entity']}", new_head, flags=re.MULTILINE)
    new_head = re.sub(r"^- \*\*Rationales:\*\*.*$", f"- **Rationales:** {', '.join(by_n[n]['rationales'])}", new_head, flags=re.MULTILINE)
    new_head = re.sub(r"^- \*\*Date:\*\*.*$", f"- **Date:** {by_n[n]['date']}", new_head, flags=re.MULTILINE)
    md.write_text(new_head + sep + body)

print("Letters/*.md headers rewritten.")

# Stance counts (in-corpus, excludes Off-topic / No-position / Duplicate)
HOLD = {"Off-topic", "No position", "Duplicate"}
in_corp = [r for r in records if r["stance"] not in HOLD]
counts = Counter(r["stance"] for r in in_corp)
print(f"\nIn-corpus N={len(in_corp)} of {len(records)}: " + " / ".join(f"{n} {s}" for s, n in counts.most_common()))
