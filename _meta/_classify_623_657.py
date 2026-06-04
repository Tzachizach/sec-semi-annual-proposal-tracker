#!/usr/bin/env python3
"""Classify drained letters #623-657 (May 28-29 stragglers) — full 3-rater ensemble.

Stance: Primary / Literalist / Skeptic.  Entity: Primary / Self-described / Letterhead.
Rationale: Primary / Literalist / Inclusive (multi-label).  Agreement fields lowercase.

Held out of the in-corpus count:
  - #653 Jilian Sipes  -> Duplicate (verbatim re-submission, superseded by #651, doc 2403667).
  - #656 Shem Alhassan -> No position ("I'm interested" — no stance on reporting frequency).
  - #657 Scott James   -> No position (same).

PP: none qualify under the narrow definition this batch. #639 Olmeda ("remember the 99%")
and #654 Richard ("well connected friends") are the ordinary insiders-vs-retail / generic-
populist framings the definition excludes, not explicit political-pressure/capture attribution.

Date: docket-truth is 2026-05-29 for all except #655 Colene Walden (2026-05-28). The drain
fell back to URL_LIST_DEFAULT_DATE (2026-05-27) for several; corrected here.

RFC-engaged: none. Skeptic-flip-to-Conditional on alternative-cadence proposals: #625, #626.
"""
import json, os
from collections import Counter
from pathlib import Path

META = Path(__file__).resolve().parent
RECORDS = META / "renumbered_records.json"
LETTERS = META.parent / "Letters"

OPP, CON, SUP, NOP, DUP = "Oppose", "Conditional", "Support", "No position", "Duplicate"
IND = "Individual"
INVP = "Investment professional"


def st(p, l, s):       # stance triple
    return {"primary": p, "literalist": l, "skeptic": s}

def en(p, sd, lh):     # entity triple
    return {"primary": p, "selfdescribed": sd, "letterhead": lh}

def ra(p, l, i):       # rationale triple
    return {"primary": p, "literalist": l, "inclusive": i}

def U(stance):         # unanimous stance triple
    return st(stance, stance, stance)

def EI():              # entity = Individual unanimous
    return en(IND, IND, IND)

def R1(code):          # single rationale, unanimous
    return ra([code], [code], [code])


C = {
 623: {"stance":U(OPP),"entity":EI(),"rationales":R1("MF"),
   "re":"MF: 'Quarterly reports are essential to market integrity.'",
   "su":"One-line Oppose: quarterly reports are essential to market integrity."},
 624: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: 'I urge the Commission to withdraw S7-2026-15.'",
   "su":"One-line Oppose urging withdrawal of the rule; no substantive argument."},
 625: {"stance":st(OPP,OPP,CON),"entity":EI(),
   "rationales":ra(["RI","AL"],["RI"],["RI","AL","CMP"]),
   "re":"RI: 'I use the 10-Q filings to determine the current value of investing'. CMP: 'compare other quarterly data verses their peers'. AL: 'Reporting should rather increase to every sixty days'.",
   "su":"Retail Oppose who uses 10-Q filings for valuation and peer comparison; proposes increasing frequency to every 60 days. Skeptic flips to Conditional on the alternative-cadence proposal.",
   "note":"Skeptic flips to Conditional on an alternative-cadence proposal (increase to 60-day reporting); majority stays Oppose (#486/#492/#593 pattern)."},
 626: {"stance":st(OPP,OPP,CON),"entity":EI(),
   "rationales":ra(["IA","AL"],["IA"],["IA","AL"]),
   "re":"IA: 'Investors need to see current information in order to make informed decisions.' AL: 'maybe the process and paperwork could be streamlined'.",
   "su":"Oppose changing the reporting timeline; investors need current information. Concedes the paperwork could be streamlined, so Skeptic flips to Conditional.",
   "note":"Skeptic flips to Conditional on the streamlining concession; majority stays Oppose."},
 627: {"stance":U(OPP),"entity":EI(),"rationales":ra(["IA","RI"],["RI"],["IA","RI","CMP"]),
   "re":"RI: 'eliminate half the data points from curves we use to evaluate our investments'. IA: 'the most reliable method we have for determining the risks of investing'.",
   "su":"Retired investor: eliminating quarterly statements removes half the data points used to evaluate investments and raises investing risk, especially for young companies and newly-held positions.",
   "name":"Anonymous","role":"Retired investor"},
 628: {"stance":U(OPP),"entity":EI(),"rationales":R1("FR"),
   "re":"FR: 'Quarterly disclosure deters securities fraud. More disclosure, not less.'",
   "su":"Vehement one-line Oppose: quarterly disclosure deters securities fraud."},
 629: {"stance":U(OPP),"entity":EI(),"rationales":R1("IP"),
   "re":"IP: 'The proposed rule weakens investor protection.'",
   "su":"One-line Oppose: the rule weakens investor protection."},
 630: {"stance":U(OPP),"entity":EI(),"rationales":R1("IA"),
   "re":"IA: 'This proposal would harm retail investors.'",
   "su":"One-line Oppose: the proposal harms retail investors."},
 631: {"stance":U(OPP),"entity":EI(),"rationales":R1("IP"),
   "re":"IP: 'Semiannual reporting reduces transparency.'",
   "su":"One-line Oppose: semiannual reporting reduces transparency."},
 632: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: 'Please vote against the proposed rule.'",
   "su":"One-line Oppose; no substantive argument."},
 633: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: 'I am against this reduction in disclosure frequency.'",
   "su":"One-line Oppose to the reduction in disclosure frequency."},
 634: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: 'I don't consent to your unfavorable change or Rule.' Generic manipulation accusation, no political-pressure/capture attribution (not PP).",
   "su":"Rambling Oppose; refuses consent to the rule and accuses the Commission of manipulation. No substantive economic argument."},
 635: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: '...write in opposition to the proposed reduction in reporting frequency' (preceded by keyboard noise).",
   "su":"One-line Oppose (garbled prefix) to the reduction in reporting frequency.",
   "name":"Freddie Simmons"},
 636: {"stance":U(OPP),"entity":EI(),"rationales":ra(["US"],["US"],["US","IP"]),
   "re":"US: 'The transparency of the US financial system is WHY the dollar is the reserve currency of the world... it is why we are where the world invests.'",
   "su":"Emphatic Oppose: US disclosure transparency underpins the dollar's reserve-currency status and global investment in US markets; do not reduce it."},
 637: {"stance":U(OPP),"entity":en(IND,INVP,INVP),
   "rationales":ra(["IP","CMP"],["IP"],["IP","CMP","MF"]),
   "re":"IP: 'Reducing the number of times public companies report earnings reduces the transparency investors have'. CMP: 'changes in their earnings and strategies needs to be visible' (Allbirds pivot example).",
   "su":"Investment professional: less frequent reporting cuts transparency into fast-moving companies; cites Allbirds' pivot from sustainable shoes to AI as an example of changes investors would miss.",
   "role":"Investment professional"},
 638: {"stance":U(OPP),"entity":EI(),"rationales":R1("IA"),
   "re":"IA: 'this rule directly affects the retirement security of ordinary Americans. Side with Main Street.'",
   "su":"Oppose: the rule affects the retirement security of ordinary Americans; side with Main Street."},
 639: {"stance":U(OPP),"entity":EI(),"rationales":R1("IA"),
   "re":"IA: 'The corrupt corporation that is America had BETTER remember the 99%'. Ordinary 99%-vs-powerful populist framing (excluded from PP per the #559/#589 standard).",
   "su":"Angry Oppose on behalf of his own household; populist 'remember the 99%' framing. Not a substantive economic argument; not PP under the narrow definition."},
 640: {"stance":U(OPP),"entity":EI(),"rationales":R1("IP"),
   "re":"IP: 'The proposed rule weakens investor protection.'",
   "su":"One-line Oppose: the rule weakens investor protection.",
   "name":"José Pérez Leon"},
 641: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: 'Please reject this proposal.'",
   "su":"One-line Oppose; no substantive argument.",
   "name":"Pedro Gómez"},
 642: {"stance":U(OPP),"entity":EI(),"rationales":R1("IA"),
   "re":"IA: 'This rule benefits insiders at the expense of ordinary investor... people.' (the ordinary insiders-vs-retail framing — IA, not PP).",
   "su":"One-line Oppose: the rule benefits insiders at the expense of ordinary investors."},
 643: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: 'I oppose S7-2026-15.'",
   "su":"One-line Oppose; no substantive argument."},
 644: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: 'I am against this reduction in disclosure frequency.'",
   "su":"One-line Oppose to the reduction in disclosure frequency. (First of two distinct MK Leeds letters; different text from #645, kept separately.)"},
 645: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: 'Keep the reports to SEC at 3 months intervals!!!'",
   "su":"One-line Oppose: keep reporting at three-month intervals. (Second of two distinct MK Leeds letters; different text from #644, kept separately per the Homer Hill / Moylan rule.)"},
 646: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: 'i strongly disagree with this rulemaking.'",
   "su":"One-line Oppose; no substantive argument."},
 647: {"stance":U(OPP),"entity":EI(),"rationales":R1("IP"),
   "re":"IP: 'The public access to information should not be diminished or limited by design.'",
   "su":"Oppose: public access to information should not be diminished; bad legislation that does not help citizens."},
 648: {"stance":U(OPP),"entity":EI(),"rationales":ra(["MF"],["MF"],["MF"]),
   "re":"MF: 'Higher required returns means higher cost of capital for US companies.' (cost-of-capital, MF).",
   "su":"Oppose: a substantive cost-of-capital point — higher required returns raise the cost of capital for US companies."},
 649: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: 'Citadel, Fidelity, Two Sigma, and D.E. Shaw have all warned the SEC against this rule. Who does this rule actually help?' Generic motive-questioning (excluded from PP per the #620 standard).",
   "su":"Oppose: cites major investment firms' opposition and asks who the rule helps. Generic motive-questioning, not a substantive SEC-framed argument; not PP."},
 650: {"stance":U(OPP),"entity":EI(),"rationales":R1("NR"),
   "re":"NR: 'I am writing to oppose the semiannual reporting proposal.'",
   "su":"One-line Oppose; no substantive argument.",
   "name":"Martha Cain"},
 651: {"stance":U(OPP),"entity":EI(),"rationales":R1("FR"),
   "re":"FR: 'Quarterly filings... dramatically shorten the window in which [fraud] can fester... Enron. WorldCom. Madoff.'",
   "su":"Oppose: longer reporting gaps give fraud more time to grow; cites Enron, WorldCom, Madoff and the run-up to 2008 (keepitquarterly.org campaign)."},
 652: {"stance":U(OPP),"entity":EI(),"rationales":ra(["CC","IP"],["CC"],["CC","IP"]),
   "re":"CC: 'Underwriters require quarterly data to issue comfort letters for capital market transactions.' IP: 'Choose transparency over opacity.'",
   "su":"Oppose: underwriters require quarterly data for comfort letters in capital-market transactions; choose transparency over opacity."},
 653: {"stance":U(DUP),"entity":EI(),"rationales":ra([],[],[]),
   "re":"Verbatim re-submission of the same keepitquarterly.org / Enron-WorldCom-Madoff text by the same commenter (Jilian Sipes); superseded by #651 (doc 2403667).",
   "su":"Duplicate of #651 (Jilian Sipes) — same body text, different doc-id (2403746). Held out of the public count.",
   "note":"Verbatim re-submission by Jilian Sipes; superseded by #651 (doc 2403667). Held out as Duplicate."},
 654: {"stance":U(OPP),"entity":EI(),"rationales":ra(["IA","FR"],["IA"],["IA","FR"]),
   "re":"IA/FR: 'opens the doors to outside influence and pilfering by insiders and well connected friends.' Insiders-vs-retail framing (IA), not explicit political-pressure/capture attribution (not PP).",
   "su":"Oppose: reducing public-company disclosure opens the door to pilfering by insiders and the well-connected; companies that want secrecy should not incorporate and take the public's money.",
   "name":"Robert Richard","role":"Private investor"},
 655: {"stance":U(OPP),"entity":EI(),"rationales":R1("IA"),
   "re":"IA: 'Without the transparancy of regular company reports, retail investors are at a disadvantage in making investment decisions.'",
   "su":"NAIC investment-club member and retiree: opposes any change; without regular reports retail investors are at a disadvantage. Credits club participation for a comfortable retirement.",
   "role":"NAIC investment club member, retiree"},
 656: {"stance":U(NOP),"entity":EI(),"rationales":ra([],[],[]),
   "re":"No position: 'I'm interested' — states no Support/Oppose/Conditional position on reporting frequency.",
   "su":"Two-word submission ('I'm interested') stating no position on the proposal. Held out as No position."},
 657: {"stance":U(NOP),"entity":EI(),"rationales":ra([],[],[]),
   "re":"No position: 'I'm interested' — states no position on reporting frequency.",
   "su":"Two-word submission ('I'm interested') stating no position on the proposal. Held out as No position."},
}

# Docket-truth dates (override the URL-list default fallback).
DATE = {n: "2026-05-29" for n in C}
DATE[655] = "2026-05-28"


def majority_rationales(triple):
    counts = Counter()
    for codes in (triple["primary"], triple["literalist"], triple["inclusive"]):
        for c in codes:
            counts[c] += 1
    return sorted([c for c, n in counts.items() if n >= 2])


def main():
    records = json.loads(RECORDS.read_text())
    by_n = {r["n"]: r for r in records}
    miss = [n for n in C if n not in by_n]
    if miss:
        raise SystemExit(f"missing records: {miss}")

    for n, c in C.items():
        rec = by_n[n]
        if "name" in c:
            rec["name"] = c["name"]
        if "role" in c:
            rec["role"] = c["role"]
        if n in DATE:
            rec["date"] = DATE[n]

        sc = c["stance"]
        rec["primary_stance"] = sc["primary"]
        rec["literalist_stance"] = sc["literalist"]
        rec["skeptic_stance"] = sc["skeptic"]
        mv = Counter(sc.values()).most_common(1)[0][0]
        rec["majority_stance"] = mv
        rec["stance"] = mv
        rec["agreement"] = "unanimous" if len(set(sc.values())) == 1 else "majority"

        ec = c["entity"]
        rec["entity_primary"] = ec["primary"]
        rec["entity_selfdescribed"] = ec["selfdescribed"]
        rec["entity_letterhead"] = ec["letterhead"]
        ev = Counter(ec.values()).most_common(1)[0][0]
        rec["entity_majority"] = ev
        rec["entity"] = ev
        rec["entity_agreement"] = "unanimous" if len(set(ec.values())) == 1 else "majority"

        rc = c["rationales"]
        rec["rationales_primary"] = rc["primary"]
        rec["rationales_literalist"] = rc["literalist"]
        rec["rationales_inclusive"] = rc["inclusive"]
        rec["rationales_majority"] = majority_rationales(rc)
        rec["rationales"] = rec["rationales_majority"]
        cats = [set(rc["primary"]), set(rc["literalist"]), set(rc["inclusive"])]
        rec["rationale_agreement"] = "unanimous" if cats[0] == cats[1] == cats[2] else "majority"
        rec["rationale_evidence"] = c.get("re", "")
        rec["summary"] = c.get("su", rec.get("summary", ""))
        if "note" in c:
            rec["stance_note"] = c["note"]

    tmp = RECORDS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(records, ensure_ascii=False, indent=2))
    os.replace(tmp, RECORDS)

    # Report.
    HELD = {DUP, NOP, "Off-topic", "Unclassified"}
    incorp = [r for r in records if (r.get("majority_stance") or r.get("stance")) not in HELD]
    from collections import Counter as Ct
    sc = Ct(r["stance"] for r in incorp)
    print(f"[classify 623-657] done. total={len(records)} in-corpus={len(incorp)}")
    print(f"  stance split: {dict(sc)}")
    held = Ct((r.get('majority_stance') or r.get('stance')) for r in records if (r.get('majority_stance') or r.get('stance')) in HELD)
    print(f"  held out: {dict(held)}")
    unclassified = [r['n'] for r in records if (r.get('majority_stance') or r.get('stance'))=='Unclassified']
    print(f"  remaining Unclassified: {unclassified}")


if __name__ == "__main__":
    main()
