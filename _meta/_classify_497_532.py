#!/usr/bin/env python3
"""Integration for letters #497-#532 (2026-06-02 afternoon full update,
Action runs #28 + #29).

Background: page-1 scan of the docket showed 30 rows; 7 net-new were
fetched in the morning batch (#490-#496). This afternoon a fresh
page-1 visit + pages 2-5 paste from Tzachi revealed 26 additional
net-new by doc-id. Wrote 26 URLs to new_urls.txt and ran Action #28.

Action #28 outcome:
  - 24 of the 26 queued URLs fetched as #497-#520 (Bart Gardner doc
    2396246 returned 404 on sec.gov - SEC has the docket row but the
    letter file is not published yet, second time the drain skipped
    it; deferred for a future session).
  - The Action's index crawl ALSO captured 12 more letters that the
    page-by-page paste had missed (CloudFront pager appears to have
    returned fresh content for the runner), bringing the in-the-batch
    total to 36 records (#497-#532). The 12 extras: Josephine Foote
    landed at #525 instead of among #497-520 because of ordering;
    #524 James Young Jr. is the _0 variant of #502 (same doc-id
    2398446) - verbatim duplicate held out per the standing rule.
    True new index-crawl additions: Andrey F., Ann Johnson, Jackelyn
    Ortega, Karen Markley, Margarito Aca, Marie Mohn, Paul R. Keith,
    Ramon Amaro Lopez, Ruth, Steven Casabona.

Outcome: 35 Oppose in-corpus + 1 Duplicate held out.

Per-letter notes:

- #513 Lauren Gaunt: AU-template carrier (the "10-Q reviewed by
  independent auditors / CEO + CFO sign and are legally accountable /
  voluntary corporate communications carry none of that" line) - now
  10 letters carry the template (#331/#338/#344/#382/#467/#473/#487/
  #513/#520 plus the #382 CFA/CII echo). Includes the recurring
  small-company-investor-loses-most framing AND the 2018-2019 SEC
  history reference. Substantive.

- #520 Vernon Ramsey: substantive multi-paragraph; AU template (CEOs
  and CFOs sign, eliminates plausible deniability), 2018-2019 SEC
  history, UK 2014 study citing 90% voluntary continuance, TTM
  analysis, retirement-account framing across multiple account types.
  Most substantive of the batch.

- #524 James Young Jr.: held out as Duplicate (verbatim same as #502
  Young, two docket entries with the same doc-id base 2398446 - the
  _0 variant is the second).

- #499 Anonymous: PP-watch frame ("Who initiated this S7-2026-15?
  What do they want to hide?" - capture suspicion).
- #511 Kali Lawson: PP-watch frame ("benefits insiders at the
  expense of ordinary investors").

- #507 Harold Hoffman, #532 Steven Casabona: divestment threats (CMP)
  - "I personally would not invest in a company that does not report
  quarterly".

- #508 Jeremy Smith: substantive; transparency + technology +
  bad-actor concealment frame (FR + AU + IA + IP).

- #518 Ronald Axler: substantive; "decades without the world coming
  to an end" + computer-automation cost argument + officer-liability
  argument (the AU code in the "audit/accountability" reading).

RFC scan: none of the 36 engages a numbered RFC. Engagement set
stays at 3 (#14, #99, #236).

PP-watch: 2 new flags (#499, #511) added to the running tally.

Agreement-field convention (carried from today's earlier session):
emit lowercase 'unanimous' / 'majority' / 'split' so the site JS
strict-equality check matches.
"""
import json, re
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RECORDS = PROJECT / "_meta" / "renumbered_records.json"
LETTERS = PROJECT / "Letters"

IND = {"primary": "Individual", "selfdescribed": "Individual", "letterhead": "Individual"}
OPP = {"primary": "Oppose", "literalist": "Oppose", "skeptic": "Oppose"}
DUP_S = {"primary": "Duplicate", "literalist": "Duplicate", "skeptic": "Duplicate"}
DUP_E = {"primary": "Duplicate", "selfdescribed": "Duplicate", "letterhead": "Duplicate"}

# Date fixes (URL-only fetch defaults; corrected per docket and body)
DATE_FIX = {
    # Action #28's index-crawl additions have already-correct 05-28 dates
    # 05-27 for #507-520 already set correctly by the URL-list drain.
}

C = {}

C[497] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "CB"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP", "CB"]},
  "stance_evidence": "'Please do not suggest, allow, encourage, standardize or legalize the cutting down of the financial reports of companies.'",
  "rationale_evidence": "IA: 'depend on that information to make decisions on our investing'. IP: 'individual investor... not big institutions'. CB: 'not big institutions who get insider information' (institutional-vs-retail comparability).",
  "summary": "Substantive retail Oppose: individual investor depends on quarterly information; small investors do not get the insider information big institutions do."}

C[498] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'as an individual investor i prefer quarterly reporting to avoid losses to my retirement account'",
  "rationale_evidence": "IA: prefers quarterly reporting. IP: retirement-account framing.",
  "summary": "One-line retail Oppose: individual investor prefers quarterly reporting to avoid losses to retirement account."}

C[499] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP", "FR"]},
  "stance_evidence": "'Every 3 months is fair. Every 6 months keeps $ in the dark.'",
  "rationale_evidence": "IA: transparency / 'in the dark' framing. (Inc) IP, FR. PP-watch frame: 'Who initiated this S7-2026-15? What do they want to hide?' - capture suspicion, not coded.",
  "summary": "Brief retail Oppose: every 3 months is fair, every 6 months keeps money in the dark; closes with a capture-suspicion question ('Who initiated this? What do they want to hide?')."}

C[500] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'This proposal would harm retail investors.'",
  "rationale_evidence": "IP: bare retail-investor-harm framing.",
  "summary": "Two-line retail Oppose: this proposal would harm retail investors."}

C[501] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["NR"], "inclusive": ["IP"]},
  "stance_evidence": "'Please stop messing with regular people's money.'",
  "rationale_evidence": "IP: 'regular people's money' framing. Literalist sees no literal rubric language.",
  "summary": "Emotional retail Oppose: stop messing with regular people's money."}

C[502] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Quarterly reporting must be preserved.'",
  "rationale_evidence": "Bare preservation request, no rationale supplied.",
  "summary": "Brief retail Oppose: quarterly reporting must be preserved (signed 'Jane')."}

C[503] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Keep quarterly reporting for all SEC companies.'",
  "rationale_evidence": "Bare preservation request, no rationale supplied.",
  "summary": "One-line retail Oppose: keep quarterly reporting for all SEC companies."}

C[504] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA"], "literalist": ["IA"], "inclusive": ["IA"]},
  "stance_evidence": "'Semiannual reporting reduces transparency.'",
  "rationale_evidence": "IA: transparency framing.",
  "summary": "One-line retail Oppose: semiannual reporting reduces transparency."}

C[505] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Keep it quarterly'",
  "rationale_evidence": "Three-word preservation request, no rationale supplied.",
  "summary": "Three-word retail Oppose: keep it quarterly."}

C[506] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Please keep quarterly reporting requirements in place.'",
  "rationale_evidence": "Bare preservation request, no rationale supplied.",
  "summary": "Brief retail Oppose: please keep quarterly reporting requirements in place."}

C[507] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "CMP"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP", "CMP"]},
  "stance_evidence": "'Reducing reporting requirements to semi-annual is not acceptable to me.'",
  "rationale_evidence": "IA: 'rely on frequent reports of financial performance'. IP: investor-protection frame. CMP: divestment threat - 'will also reduce the chance that I will invest in said company'.",
  "summary": "Retail Oppose with divestment threat: relies on frequent reports; will reduce his investment in companies that opt for semiannual."}

C[508] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "FR", "AU"], "literalist": ["IA", "FR"], "inclusive": ["IA", "IP", "FR", "AU"]},
  "stance_evidence": "'I believe quarterly reports are necessary to ensure accountability and transparency.'",
  "rationale_evidence": "IA: 'six months is too long to wait for an update'. IP. FR: 'danger in a bad actor being able to use a longer reporting period to conceal fundamental problems'. AU: 'accountability and transparency' framing applied to corporate management discipline.",
  "summary": "Substantive retail Oppose: quarterly reports ensure accountability; six months too long; technology makes compliance easy; bad actors can use a longer period to conceal fundamental problems."}

C[509] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Keep filings quartely'",
  "rationale_evidence": "Three-word preservation request, no rationale supplied.",
  "summary": "Three-word retail Oppose: keep filings quarterly."}

C[510] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'I do not believe we should let companies off from reporting on a quarterly basis. We need transparency.'",
  "rationale_evidence": "IA: '10-Q reports and other quarterly reports to make investment decisions every quarter'. IP: individual investor / BetterInvesting framing.",
  "summary": "Retail Oppose from a 20-year BetterInvesting member: uses 10-Q reports to make investment decisions every quarter; do not let companies off."}

C[511] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'This rule benefits insiders at the expense of ordinary investors.'",
  "rationale_evidence": "IP: insider-vs-ordinary-investor framing. PP-watch: capture-suspicion frame ('benefits insiders at the expense'), not yet a coded rationale.",
  "summary": "Two-line retail Oppose: this rule benefits insiders at the expense of ordinary investors. PP-watch instance."}

C[512] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "CMP"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP", "CMP"]},
  "stance_evidence": "'As an individual investor, I utilize these reports to make decisions for my investment portfolio. A lot can happen in a 3 month period that affects these decisions.'",
  "rationale_evidence": "IA: 'A lot can happen in a 3 month period'. IP: individual-investor portfolio framing. CMP: 'any business that is publicly traded has the automation and resources to continue quarterly SEC reporting' - the cost-burden argument cuts against the proposal.",
  "summary": "Retail Oppose: individual investor uses quarterly reports for portfolio decisions; publicly-traded companies have the automation and resources to continue quarterly, removing two reports per year is no significant burden relief."}

C[513] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP"], "literalist": ["AU", "IA", "IP"], "inclusive": ["AU", "IA", "IP", "MF"]},
  "stance_evidence": "'half of the required, reviewed and certified financial filings I get each year would disappear. This is unacceptable!'",
  "rationale_evidence": "AU: the recurring template - 'a 10-Q filing is reviewed by independent auditors, and the CEO and CFO sign it personally and can be held legally accountable for its contents. However, any voluntary corporate communications that would replace them carry none of that' (same wording as #331/#338/#344/#382/#467/#473/#487). IA: 'I would lose the most information'. IP: 'individual investors own the majority of shares in smaller public companies'. (Inc) MF.",
  "summary": "Retail Oppose carrying the certified-10-Q-vs-voluntary-communications campaign template (CEO + CFO sign and are legally accountable; voluntary communications carry none of that); cites SEC data that individual investors own the majority of shares in smaller public companies; cites the 2018-2019 SEC review where the empirical record opposed reducing reporting frequency."}

C[514] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'Quarterly reporting requirement should remain.'",
  "rationale_evidence": "IA: 'does not provide the investing public with timely and relevant information'. IP: 'further lessen the information available to the small investor compared to professional investors that have greater access'.",
  "summary": "Retail Oppose: quarterly should remain; semi-annual would not provide timely information and would further widen the small-investor-vs-professional information gap."}

C[515] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "FR"], "literalist": ["IA"], "inclusive": ["IA", "FR"]},
  "stance_evidence": "'Semiannual repots just do not cut it.'",
  "rationale_evidence": "IA: 'relied on quarterly reports for timely news'. FR: 'It gives the company or its officers six months to hide their shenanigans!!!!'",
  "summary": "Retail Oppose from a long-time individual investor: semiannual reports do not cut it; six months gives company officers time to hide their shenanigans."}

C[516] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'I oppose the SEC allowing public companies to file financial reports twice a year instead of quarterly.'",
  "rationale_evidence": "IA: 'lose the most information about exactly the companies we own'. IP: hampers decision-making.",
  "summary": "Retail Oppose: would lose the most information about exactly the companies the investor owns; hampers decision-making."}

C[517] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "MF"], "literalist": ["IA", "MF"], "inclusive": ["IA", "MF", "AU"]},
  "stance_evidence": "'Quarterly reporting is critical to my keeping up to date with the developments within companies.'",
  "rationale_evidence": "IA: 'reporting is 30 to 60 days delayed... This would delay updates to 7 months'. MF: 'Justifying the daily actions in the market will suffer with this delay'. (Inc) AU: management accountability framing ('Keeping management accountable is critical to assessing turnarounds, strategic developments, and acquisitions in a timely factor').",
  "summary": "Retail Oppose: existing 30-60 day delay would extend to 7 months total; daily-action justification in the market would suffer; management accountability for turnarounds and strategic developments depends on timely reporting."}

C[518] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "FR", "AU"], "literalist": ["FR", "AU"], "inclusive": ["IA", "FR", "AU", "CMP"]},
  "stance_evidence": "'Quarterly statements have been required for decades without the world coming to an end.'",
  "rationale_evidence": "IA: 'keep others in the dark longer'. FR: 'serves to help those who want to deceive'. AU: 'officers of companies personally liable for misrepresentations. Fining companies doesn't affect those who cause the misdeeds'. (Inc) CMP: cost-of-reporting argument - 'super fast computers to help the process, so the burden have been greatly diminished'.",
  "summary": "Substantive retail Oppose: decades-of-precedent argument plus a counter-proposal that the right fix is stronger personal liability for officers, not less-frequent reporting; computers have reduced the reporting burden, not increased it."}

C[519] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "FR"], "literalist": ["IA", "FR"], "inclusive": ["IA", "IP", "FR"]},
  "stance_evidence": "'Quarterly reports increases transparency.'",
  "rationale_evidence": "IA: 'crucial in looking up potential stocks or managing currently held stocks'. IP: investor protection through transparency. FR: 'Mistakes or bad decisions can be more evident and any correction... accomplished more quickly'.",
  "summary": "Retail Oppose: quarterly reports are crucial for potential and currently-held stocks; mistakes and bad decisions become more evident; corrections happen faster."}

C[520] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP", "MF", "US", "CB"], "literalist": ["AU", "IA", "IP"], "inclusive": ["AU", "IA", "IP", "MF", "US", "CB"]},
  "stance_evidence": "'The elimination of Semi-Annual A 10-Q Reporting is a blatant ploy to put individual investors at a disadvantage.'",
  "rationale_evidence": "AU: the recurring template - 'these documents, signed by the CEOs and CFOs eliminates plausible deniability of financial position'. IA: 'timely of investment trends... Canary-in-the-Coal Mine'. IP: extensive retirement-account framing across multiple account types. MF: market-stability framing. US: 'Nation's financial strength, stability'. CB: 2018-2019 SEC history + UK 2014 study ('where 90% of companies continued Reporting by choice').",
  "summary": "Substantive multi-paragraph retail Oppose with the AU template (CEO/CFO signatures eliminate plausible deniability) + 2018-2019 SEC history + UK 2014 90%-voluntary-continuance citation + TTM analysis + retirement-account framing across stock funds, 401(k), 457(b), Thrift Savings, Roth, 529, individual portfolios. One of the most substantive letters in the batch."}

C[521] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "FR"], "literalist": ["IA", "FR"], "inclusive": ["IA", "FR", "IP"]},
  "stance_evidence": "'We need more transparency, not less. Less fraud, not more.'",
  "rationale_evidence": "IA: transparency frame. FR: explicit fraud-risk frame.",
  "summary": "One-line retail Oppose: more transparency, not less; less fraud, not more."}

C[522] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'Quarterly reporting is necessary for stakeholders to evaluate investments and assets.'",
  "rationale_evidence": "IA: stakeholder evaluation framing. IP.",
  "summary": "One-line retail Oppose: quarterly reporting is necessary for stakeholders to evaluate investments and assets."}

C[523] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'keep querterly reports. we the people should what is going.sharing is caring'",
  "rationale_evidence": "Brief preservation request, no rationale supplied.",
  "summary": "Brief retail Oppose: keep quarterly reports; sharing is caring."}

C[524] = {"stance": DUP_S, "entity": DUP_E,
  "rationales": {"primary": [], "literalist": [], "inclusive": []},
  "stance_evidence": "Verbatim same text as #502 James Young Jr. (doc-id base 2398446; this is the _0 variant).",
  "rationale_evidence": "n/a - held out as Duplicate.",
  "stance_note": "Held out as Duplicate. Same author, same text, two SEC docket entries on the same doc-id base (2398446 and 2398446_0). #502 is canonical.",
  "summary": "Verbatim duplicate of #502 James Young Jr. Held out as Duplicate per the standing rule."}

C[525] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA"], "literalist": ["IA"], "inclusive": ["IA"]},
  "stance_evidence": "'Eliminating quaterly reports is penny-wise-and -pound -foolish! Investors and businesses need timely information!'",
  "rationale_evidence": "IA: 'need timely information'.",
  "summary": "Two-line retail Oppose: penny-wise pound-foolish; investors and businesses need timely information."}

C[526] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'Please do not eliminate the quarterly reporting this would essentially eliminate half of the timely information I receive.'",
  "rationale_evidence": "IA: 'eliminate half of the timely information I receive'. IP: individual-investor framing.",
  "summary": "Retail Oppose: individual investor relies on quarterly information; semiannual would eliminate half of the timely information."}

C[527] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'I urge you to reject S7-2026-15.'",
  "rationale_evidence": "Bare rejection request, no rationale supplied.",
  "summary": "Brief retail Oppose: urges the SEC to reject S7-2026-15."}

C[528] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'Quarterly reporting is necessary for stakeholders to evaluate investments and assets. This is vital to the integrity and transparency of publicly traded companies.'",
  "rationale_evidence": "IA: integrity-and-transparency framing. IP: stakeholder evaluation.",
  "summary": "Retail Oppose: quarterly reporting necessary for stakeholders to evaluate investments and assets; vital to the integrity and transparency of publicly traded companies."}

C[529] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'Delaying such reports to every 6 months reduces the crucial financial data I rely on to make investment decisions.'",
  "rationale_evidence": "IA: 'rely on the quarterly financial reports'. IP: 50-year-investor framing.",
  "summary": "Retail Oppose from a 50-year investor: relies on quarterly reports; delaying to 6 months reduces crucial financial data; if it ain't broken, don't fix it."}

C[530] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA"], "literalist": ["IA"], "inclusive": ["IA"]},
  "stance_evidence": "'Semiannual reporting reduces transparency.'",
  "rationale_evidence": "IA: transparency framing.",
  "summary": "One-line retail Oppose: semiannual reporting reduces transparency."}

C[531] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "MF"], "literalist": ["MF"], "inclusive": ["IA", "MF"]},
  "stance_evidence": "'Quarterly reports are essential to market integrity.'",
  "rationale_evidence": "MF: 'market integrity' framing. IA: implicit information-availability.",
  "summary": "One-line retail Oppose: quarterly reports are essential to market integrity."}

C[532] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP", "CMP"], "literalist": ["IP"], "inclusive": ["IP", "CMP"]},
  "stance_evidence": "'I personally would not invest in a company that does not report quarterly.'",
  "rationale_evidence": "IP: 'retail investor AGAIN comes up with the short stick'. CMP: divestment threat - 'would not invest in a company that does not report quarterly'.",
  "summary": "Retail Oppose with divestment threat: retail investor again comes up with the short stick; would not invest in companies that opt for semiannual."}


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
    rec["agreement"] = "unanimous" if len(set(calls["stance"].values())) == 1 else "majority"

    rec["entity_primary"] = calls["entity"]["primary"]
    rec["entity_selfdescribed"] = calls["entity"]["selfdescribed"]
    rec["entity_letterhead"] = calls["entity"]["letterhead"]
    ev = Counter(calls["entity"].values()).most_common(1)[0][0]
    rec["entity_majority"] = ev
    rec["entity"] = ev
    rec["entity_agreement"] = "unanimous" if len(set(calls["entity"].values())) == 1 else "majority"

    rec["rationales_primary"] = calls["rationales"]["primary"]
    rec["rationales_literalist"] = calls["rationales"]["literalist"]
    rec["rationales_inclusive"] = calls["rationales"]["inclusive"]
    rec["rationales_majority"] = majority_rationales(calls["rationales"])
    rec["rationales"] = rec["rationales_majority"]
    cats = [set(calls["rationales"]["primary"]),
            set(calls["rationales"]["literalist"]),
            set(calls["rationales"]["inclusive"])]
    rec["rationale_agreement"] = "unanimous" if cats[0] == cats[1] == cats[2] else "majority"
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
