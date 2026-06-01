#!/usr/bin/env python3
"""Integration for letters #474-#489 (2026-06-01 follow-on, Action run #26).

16 letters fetched via the URL-list drain in daily_fetch.py after the
CloudFront pager stale-page-1 issue masked them on Action run #25.

Outcome: 15 Oppose in-corpus + 1 Duplicate held out.

- #485 lori carroll == #474 Lori Carroll, verbatim identical text ("Stop this
  vote, you will be screwing your investors..."), two different submission IDs
  on the docket but same author (capitalization difference only). Per the
  Duplicate-stance rule, #474 is canonical and #485 is held out as Duplicate.

- #484 Roger Scott's role line on the docket reads "Registered Investment
  Advisor and CFP" (the URL-drain default of "Individual" is wrong because the
  drain does not see the docket's submitter-role column). Entity is
  Investment professional, same precedent as #321 Christi Powell (CFP / IAR).

- #481 Michael Fleming signs his letter as "Gabriele Fleming" (the submitter
  name on the docket is the one we use; the signature is left as-is in the
  body). Both names refer to the same filer.

- #487 Gregory Pittman carries the "certified 10-Q vs voluntary
  communications" template language that recurs across #331 Burgeson, #338
  Hartfelder, #344 Lewis, #382 DeSonier, #467 Kraynak, #473 Riddle.

- #486 Steve Anderson reads as a borderline Oppose-vs-Conditional case: he
  proposes the SEC "leverage modern abilities to process information to seek
  ways to make more and better information available more quickly and more
  streamlined for investors" — an alternative-proposal frame that the Skeptic
  rubric flips to Conditional, but his closing line ("should not go backwards
  to a semiannual reporting structure") is unambiguous so Primary + Literalist
  stay Oppose; majority Oppose, agreement 2-of-3.

- #480 Justin threatens to reallocate retirement savings to international
  funds — a divestment threat (vote against), NOT a condition for support, so
  all three stance raters stay Oppose.

RFC scan: none of the 16 engages a numbered RFC.

PP-watch: #489 Nancy Ambrose ("Are you siding with the big companies? That
will make them happy.") is a brief capture-suspicion frame; adds to the
PP-watch tally pending the promote/park decision.
"""
import json, re
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RECORDS = PROJECT / "_meta" / "renumbered_records.json"
LETTERS = PROJECT / "Letters"

IND = {"primary": "Individual", "selfdescribed": "Individual", "letterhead": "Individual"}
INVP_RIA = {"primary": "Investment professional", "selfdescribed": "Individual", "letterhead": "Investment professional"}
OPP = {"primary": "Oppose", "literalist": "Oppose", "skeptic": "Oppose"}
OPP_SKEP_C = {"primary": "Oppose", "literalist": "Oppose", "skeptic": "Conditional"}

C = {}

C[474] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP", "IA"]},
  "stance_evidence": "'Stop this vote, you will be screwing your investors...'",
  "rationale_evidence": "IP: explicit investor-harm framing. (Inc) IA. Per-code majority IP.",
  "summary": "One-line retail Oppose: stop the vote, the proposal harms investors."}

C[475] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'The proposed rule weakens investor protection.'",
  "rationale_evidence": "IP: explicit, unanimous.",
  "summary": "Two-line retail Oppose: the proposed rule weakens investor protection."}

C[476] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "MF"], "literalist": ["IP", "IA"], "inclusive": ["IA", "IP", "MF", "US"]},
  "stance_evidence": "'I want to add my comment and objection to the recent consideration of only allowing USA public companies to file quarterly updates only every 6 months.'",
  "rationale_evidence": "IA: 'Long-term and short-term investors rely on the continued, every 3 month transparency'. IP: investor reliance. MF: 'six months is too long without the required release of pertinent and trade-sensitive information'. (Inc) US: 'American citizen' framing.",
  "summary": "80-year-old long-term investor Oppose: six months is too long for the release of pertinent and trade-sensitive financial information; investors rely on the every-3-month transparency."}

C[477] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Please keep quarterly reporting requirements in place.'",
  "rationale_evidence": "Bare preservation request, no rationale supplied.",
  "summary": "One-line retail Oppose: keep quarterly reporting requirements in place."}

C[478] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'I urge the Commission to withdraw S7-2026-15.'",
  "rationale_evidence": "Bare withdrawal request.",
  "summary": "Two-line retail Oppose: withdrawal request, no rationale given."}

C[479] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'The proposed rule weakens investor protection.'",
  "rationale_evidence": "IP: explicit, unanimous. Same one-line wording as #475 J9nes — possible coordinated template.",
  "summary": "Two-line retail Oppose: the proposed rule weakens investor protection. Same one-line phrasing as #475 J9nes."}

C[480] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "CMP", "US"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP", "CMP", "US", "MF"]},
  "stance_evidence": "'There is no profit percent that is worth the risk of 6 months of no news... hope this does prevent this horrible proposal.'",
  "rationale_evidence": "IA: '6 months of no news', 'leave me in the dark'. IP: 'so little visibility... can not trust the information'. CMP: 'I will have to reallocate a large percent or all of my retirement savings from US based companies and index funds to international ones'. US: explicit US-vs-international framing. (Inc) MF: 'rapidly changing environment'.",
  "summary": "Substantive retail Oppose with a divestment threat: a middle-aged professional invested almost exclusively in US companies and index funds threatens to reallocate to international funds if the proposal goes through, because six months of no news leaves him in the dark in a rapidly changing environment."}

C[481] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP", "FR"], "literalist": ["AU", "IA", "IP", "FR"], "inclusive": ["AU", "IA", "IP", "FR", "MF"]},
  "stance_evidence": "'Please do not reduce the number of filings.'",
  "rationale_evidence": "AU: 'QUARTERLY, audited and certified financial filings' — the only way to verify what management says. IA: 'private investors will be kept in the dark'. IP: 'I research the company myself'. FR: 'companies and brokerage houses more latitude to game the system by releasing misleading or totally false information to the financial press without any real way of checking their financials'.",
  "summary": "Substantive retail Oppose from a self-directed private investor: he uses audited and certified quarterly filings as the only check on company-issued or brokerage-house statements; halving the filings opens the door to misleading or false press releases that retail investors cannot verify. Signed 'Gabriele Fleming' (same filer as the docket-named 'Michael Fleming')."}

C[482] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'I do not support semiannual reporting.'",
  "rationale_evidence": "Bare opposition, no rationale supplied.",
  "summary": "Two-line retail Oppose: no support for semiannual reporting, no rationale given."}

C[483] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["MF", "CB"], "literalist": ["MF", "CB"], "inclusive": ["MF", "CB", "IP"]},
  "stance_evidence": "'I urge the SEC to leave well-enough alone. Quarterly reports are good for transparency.'",
  "rationale_evidence": "MF: 'good for transparency'. CB: 'the increased regulatory flexibility that supposedly justifies the change is not borne out by research on the subject' — directly contests the SEC's own cost-benefit framing.",
  "summary": "Brief but pointed retail Oppose: quarterly reports support transparency, and the regulatory-flexibility benefit the proposal claims is not supported by the research."}

C[484] = {"stance": OPP, "entity": INVP_RIA,
  "rationales": {"primary": ["IA", "MF"], "literalist": ["IA"], "inclusive": ["IA", "MF", "IP"]},
  "stance_evidence": "'I and other professionals and the public rely on mandated quarterly reports to keep our analysis up to date. Please do not change existing policy.'",
  "rationale_evidence": "IA: 'professionals and the public rely... to keep our analysis up to date'. MF: 'keep our analysis up to date' as a market-function timeliness frame. (Inc) IP.",
  "summary": "Brief Oppose from a Registered Investment Advisor and CFP: professionals and the public rely on mandated quarterly reports to keep their analyses up to date.",
  "role_full": "Registered Investment Advisor and CFP"}

# #485 lori carroll — verbatim Duplicate of #474 Lori Carroll
C[485] = {"stance": {"primary": "Duplicate", "literalist": "Duplicate", "skeptic": "Duplicate"},
  "entity": IND,
  "rationales": {"primary": [], "literalist": [], "inclusive": []},
  "stance_evidence": "Verbatim re-submission of #474 Lori Carroll ('Stop this vote, you will be screwing your investors...').",
  "rationale_evidence": "Held out as Duplicate per the standing rule.",
  "summary": "DUPLICATE (held out): verbatim re-submission of #474 Lori Carroll. Two distinct docket IDs but identical text; same author (capitalization difference only)."}

C[486] = {"stance": OPP_SKEP_C, "entity": IND,
  "rationales": {"primary": ["IA", "MF", "AL"], "literalist": ["IA", "MF"], "inclusive": ["IA", "MF", "AL", "IP", "CB"]},
  "stance_evidence": "'After receiving public comments, the Commission should not go backwards to a semiannual reporting structure.'",
  "rationale_evidence": "IA: 'reduces the timeliness of available information and materially impairs the quality of available information'. MF: 'leverage modern abilities to process information to seek ways to make more and better information available more quickly'. AL: explicit alternative proposal that the SEC should make quarterly reporting 'less burdensome to the business and more useful to the investor' instead of eliminating it. (Inc) IP, CB.",
  "rationale_agreement_override": True,
  "stance_note": "Skeptic flips to Conditional on the alternative-proposal language ('make reports less burdensome and more useful'); Primary + Literalist stay Oppose because the conclusion is unambiguous ('should not go backwards'). Majority Oppose (2-of-3).",
  "summary": "Substantive long-term-investor Oppose with a built-in counter-proposal: rather than eliminating quarterly reporting, the Commission should leverage modern processing to make quarterly reports less burdensome to companies and more useful to investors. Closing line unambiguously rejects the semiannual structure."}

C[487] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP"], "literalist": ["AU", "IA", "IP"], "inclusive": ["AU", "IA", "IP", "MF"]},
  "stance_evidence": "'I'm against reducing quarterly reporting in half.'",
  "rationale_evidence": "AU: the recurring template — 'a 10-Q is reviewed by independent auditors, and the CEO and CFO sign it personally and can be held legally accountable for its contents. The voluntary corporate communications that would replace them carry none of that' (same wording as #331/#338/#344/#382/#467/#473). IA: 'Investors would lose the most information about exactly the companies we own'. IP.",
  "summary": "Retail Oppose carrying the certified-10-Q-vs-voluntary-communications campaign template (CEO + CFO sign and are legally accountable; voluntary communications carry none of that); reiterates the 'small companies are the ones most likely to opt in, so investors in those companies lose the most' framing."}

C[488] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "MF"], "literalist": ["MF"], "inclusive": ["IA", "MF", "IP"]},
  "stance_evidence": "'I want quarterly reporting of financial performance to stay as it is.'",
  "rationale_evidence": "MF: 'speed the economy is changing' — six-month intervals not enough. IA: timeliness of information. (Inc) IP.",
  "summary": "Brief retail Oppose: at the speed the economy is changing, six-month intervals are not enough to stay on top of things."}

C[489] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA"], "literalist": ["NR"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'Why do you want to give us less important information to work with?'",
  "rationale_evidence": "IA: less information to work with. The 'Are you siding with the big companies?' framing is a capture-suspicion (PP-watch), not yet a coded rationale.",
  "summary": "Three-line retail Oppose that frames the proposal as the SEC siding with big companies, leaving investors with less information. PP-watch instance (regulatory-capture suspicion)."}


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
    if "role_full" in calls:
        rec["role"] = calls["role_full"]
    if "stance_note" in calls:
        rec["stance_note"] = calls["stance_note"]

    md = next(LETTERS.glob(f"{n}_*.md"), None)
    if md:
        body = md.read_text()
        body_text = body.split("---", 2)[-1] if "---" in body else body
        rec["words"] = len(re.findall(r"\b\w+\b", body_text))

# Write
RECORDS.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
print(f"Updated {len(C)} records: #{min(C)}–#{max(C)}")

# Letters/*.md header rewrites
for n, calls in C.items():
    md = next(LETTERS.glob(f"{n}_*.md"), None)
    if not md:
        continue
    text = md.read_text()
    head, sep, body = text.partition("---")
    new_head = re.sub(r"^- \*\*Stance:\*\*.*$", f"- **Stance:** {by_n[n]['stance']}", head, flags=re.MULTILINE)
    new_head = re.sub(r"^- \*\*Entity:\*\*.*$", f"- **Entity:** {by_n[n]['entity']}", new_head, flags=re.MULTILINE)
    new_head = re.sub(r"^- \*\*Rationales:\*\*.*$", f"- **Rationales:** {', '.join(by_n[n]['rationales'])}", new_head, flags=re.MULTILINE)
    if "role_full" in calls:
        new_head = re.sub(r"^- \*\*Role/Affiliation:\*\*.*$", f"- **Role/Affiliation:** {calls['role_full']}", new_head, flags=re.MULTILINE)
    md.write_text(new_head + sep + body)

print("Letters/*.md headers rewritten.")

# Stance counts
HOLD = {"Off-topic", "No position", "Duplicate"}
in_corp = [r for r in records if r["stance"] not in HOLD]
counts = Counter(r["stance"] for r in in_corp)
print(f"\nIn-corpus N={len(in_corp)} of {len(records)}: " + " / ".join(f"{n} {s}" for s, n in counts.most_common()))
held = Counter(r["stance"] for r in records if r["stance"] in HOLD)
print(f"Held out: " + " / ".join(f"{n} {s}" for s, n in held.most_common()))
