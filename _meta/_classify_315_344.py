#!/usr/bin/env python3
"""Integration for letters #315-#344 (2026-05-31 full update, Action run #23).

30 new letters, all received 2026-05-27, all retail HTML comments. Full 3-rater
ensemble (Stance: Primary/Literalist/Skeptic; Entity: Primary/Self-described/
Letterhead; Rationale: Primary/Literalist/Inclusive). Outcome: 30 Oppose, 0
Support, 0 Conditional, 0 Off-topic, 0 No-position.

Entity: 29 Individual + 1 Investment professional (#321 Christi Powell, CFP/IAR,
Falcon Financial of Oklahoma LLC). Borderline entity splits captured honestly:
#324 Krzysiak signs "crypto guru" (self-described rater -> Industry practitioner,
majority Individual); #344 Lewis "works with investors" (letterhead rater ->
Investment professional, majority Individual).

RFC scan: none of the 30 names or answers a numbered RFC. RFC-engagement count
stays 3 (#14, #99, #236).

FLAGS:
- #334 Jacques Laufer is a political vent ("Trump directed cop-out to the rich
  and influential") -> on-topic core is uncoded; capture sentiment is a PP-watch
  instance per STATUS 6.6 (now ~6, still below the 7-10 threshold).
- #315 Vautrin is apocalyptic rhetoric whose one substantive phrase
  ("democratizing aspect of the free market") the balanced rater reads as IA.
- The "certified 10-Q vs voluntary communications" talking point recurs verbatim
  across #331 Burgeson, #338 Hartfelder, #344 Lewis (shared campaign template) ->
  all carry AU.
- 2018-rubric extensions (GU, Trade-association bucket) deferred per to-do list;
  none of these 30 needs them.
"""
import json, re
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RECORDS = PROJECT / "_meta" / "renumbered_records.json"
LETTERS = PROJECT / "Letters"

IND   = {"primary":"Individual","selfdescribed":"Individual","letterhead":"Individual"}
IPROF = {"primary":"Investment professional","selfdescribed":"Investment professional","letterhead":"Investment professional"}
OPP   = {"primary":"Oppose","literalist":"Oppose","skeptic":"Oppose"}

C = {}

C[315] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IA"],"literalist":["NR"],"inclusive":["IA","US"]},
  "stance_evidence":"'If you do this, you will destroy a democratizing aspect of the free market.'",
  "rationale_evidence":"IA: quarterly reporting framed as 'democratizing' the market (leveling retail access). Literalist reads the rest as pure rhetoric (NR); (Inc) US: 'the greatest nation on earth'. Apocalyptic framing otherwise uncoded.",
  "summary":"Apocalyptic retail Oppose: removing quarterly reporting destroys a 'democratizing aspect of the free market' and hastens national decline. The substantive core is a market-access/leveling claim."}

C[316] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP","IA"]},
  "stance_evidence":"'Please do not make the mistake of removing quarterly filings and the protections they provide for individual investors.'",
  "rationale_evidence":"IP: quarterly filings as investor protections; (Inc) IA: 'for individual investors'.",
  "summary":"One-line retail Oppose: quarterly filings protect individual investors."}

C[317] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IA","IP","MF"],"literalist":["IA","IP","MF"],"inclusive":["IA","IP","MF","FR","CB"]},
  "stance_evidence":"'I am writing as an individual investor to express my strong opposition... such a change would meaningfully weaken market transparency.'",
  "rationale_evidence":"IP: transparency, accountability, oversight; IA: individual vs institutional investors with alternative data, quarterly disclosures 'level the playing field'; MF: 'market volatility driven by speculation rather than facts', longer uncertainty; (Inc) FR: 'problems to go unnoticed'; (Inc) CB: names the regulatory-burden tradeoff and rejects it.",
  "summary":"Reasoned retail Oppose: semiannual reporting widens information gaps, disadvantages individual investors against institutions with alternative data, invites speculation-driven volatility, and weakens accountability; the compliance-burden savings do not outweigh the loss of transparency.",
  "role_full":"Individual investor"}

C[318] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IA"],"literalist":["IA"],"inclusive":["IA"]},
  "stance_evidence":"'Cutting in half the number of financial quarterly filings... would put us at a greater disadvantage than we already experience.'",
  "rationale_evidence":"IA: explicit retail information disadvantage that fewer filings would deepen.",
  "summary":"Brief retail Oppose: halving quarterly filings deepens the disadvantage retail investors already face.",
  "role_full":"Retail retirement investor"}

C[319] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IA","IP"],"literalist":["IA","IP"],"inclusive":["IA","IP"]},
  "stance_evidence":"'I oppose semi-annual reporting. Quarterly reporting does not interfere with investment decisions...'",
  "rationale_evidence":"IP: private investors rely on disclosures to make informed decisions; IA: AI and algorithm-driven trading already reduce 'private, unsophisticated investors' ability to achieve profits; semiannual reporting would make intelligent retail decisions impossible.",
  "summary":"Retail Oppose: private, unsophisticated investors already face algorithmic-trading barriers; cutting to semiannual would make informed retail decisions impossible. In an age of AI the case is for more reporting, not less.",
  "role_full":"Personal stock investor"}

C[320] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IA","IP"],"literalist":["IA","IP"],"inclusive":["IA","IP","AU"]},
  "stance_evidence":"'Please do not change SEC requirements that corporations file quarterly reports. The current scheme is extremely beneficial to independent investors like me.'",
  "rationale_evidence":"IP: audited, personally signed quarterly filings let him track earnings and spot souring investments; IA: 'Major investment firms can weather losses caused by gaps' but an individual investor needs the extra data; benefits 'the top 1%'. (Inc) AU: values the audited/signed nature.",
  "summary":"Retail Oppose: audited, personally signed quarterly filings let an independent investor catch deteriorating positions that large firms can ride out; the change benefits the top 1% and hurts individuals. Notes the SEC abandoned the same change in 2018-2019 for reasons that still hold.",
  "role_full":"Independent investor"}

C[321] = {"stance":{"primary":"Oppose","literalist":"Oppose","skeptic":"Conditional"}, "entity":IPROF,
  "rationales":{"primary":["AU","IP"],"literalist":["AU","IP"],"inclusive":["AU","IP","MF"]},
  "stance_evidence":"'I strongly oppose the idea of semi-annual reporting without requiring audit certification and the inclusion of legal jeopardy attached to management.'",
  "rationale_evidence":"AU: opposes dropping audit certification and management legal jeopardy; IP: without them, reporting would be 'rife with obfuscations'. Skeptic reads the 'without audit certification' framing as a condition (Conditional). (Inc) MF: 'impossible for investment managers to accurately assess the company'.",
  "summary":"Investment-professional Oppose (CFP/IAR): semiannual reporting stripped of audit certification and management legal accountability would be rife with obfuscation and impossible to assess. The skeptic rater reads the audit-certification framing as conditional.",
  "role_full":"CFP, IAR — Falcon Financial of Oklahoma, LLC"}

C[322] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["NR"],"literalist":["NR"],"inclusive":["NR"]},
  "stance_evidence":"'I oppose such proposal and vote to keep earning calls quarterly.'",
  "rationale_evidence":"NR: bare opposition; the aside that AI efficiency could support monthly reporting is not a taxonomy argument.",
  "summary":"Bare retail Oppose: keep quarterly, and AI efficiency could even support monthly."}

C[323] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP","IA"]},
  "stance_evidence":"'Being of retirement age, I need to make financial decisions quickly, based on timely information. 6 months is NOT timely.'",
  "rationale_evidence":"IP: timeliness of disclosure for decision-making; (Inc) IA: a retiree relies more heavily on periodic reports.",
  "summary":"Retiree Oppose: timely information drives quick financial decisions, and six months is not timely.",
  "role_full":"Retired / individual investor"}

C[324] = {"stance":OPP, "entity":{"primary":"Individual","selfdescribed":"Industry practitioner / technologist","letterhead":"Individual"},
  "rationales":{"primary":["NR"],"literalist":["NR"],"inclusive":["NR"]},
  "stance_evidence":"'Bruh wtf every 6 months yo this can't be real cuh. Need my financial reports quarterly ya heard.'",
  "rationale_evidence":"NR: bare opposition in slang. Self-described rater tags the 'crypto guru' signoff as Industry practitioner / technologist; majority Individual.",
  "summary":"Bare retail Oppose in slang: six months is too long, keep quarterly. Signs 'crypto guru'.",
  "role_full":"Individual"}

C[325] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP","IA"]},
  "stance_evidence":"'It is very important that the free, full and timely disclosure of information on companies be maintained. I support that the system not be changed.'",
  "rationale_evidence":"IP: free, full, timely disclosure; (Inc) IA: relies on investing to support retirement without charity.",
  "summary":"Retail Oppose: free, full, timely disclosure supports a self-funded retirement and should not change.",
  "role_full":"Individual investor"}

C[326] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP"]},
  "stance_evidence":"'As technology gets better and cheaper, there's no reason to permit less frequent financial reporting.'",
  "rationale_evidence":"IP: relies on SEC filings for 'real data instead of the spin' of press releases; wants decades-old certified standards held. The technology-is-cheap point rebuts compliance burden but maps to no anti-code.",
  "summary":"Retail Oppose: cheaper technology argues for the same or more frequent reporting, not less; SEC filings give real data rather than corporate spin.",
  "role_full":"Individual investor"}

C[327] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IA","IP"],"literalist":["IA","IP"],"inclusive":["IA","IP"]},
  "stance_evidence":"'As a fundamental retail investor, quarterly reporting is vital to my retirement.'",
  "rationale_evidence":"IP: quarterly data shows company direction for income and growth, monitoring; IA: 'doesn't assist the day-by-day investor', the SEC is 'vital in securing data for the retail investor'; lowering standards does not help shareholders.",
  "summary":"Retail Oppose: quarterly data lets a fundamental retail investor track company direction; cutting frequency and lowering standards fails the day-by-day investor.",
  "role_full":"Retail investor"}

C[328] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP","FR"]},
  "stance_evidence":"'Changing the rules to get rid of the quarterly reporting rule is a disastrous idea! Companies will hide behind the lack of accountability!'",
  "rationale_evidence":"IP: lost accountability leaves investors uninformed and at risk; (Inc) FR: companies 'hide' problems. The employee-vulnerability point has no taxonomy code.",
  "summary":"Retail Oppose: removing quarterly reporting lets companies hide behind lost accountability, leaving investors uninformed and employees, who learn employer health from financials, more vulnerable."}

C[329] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP"]},
  "stance_evidence":"'I oppose the proposal to stop the quarterly reports. I am an investor... I rely on the reports for information and investing strategy.'",
  "rationale_evidence":"IP: 25-year investor relies on quarterly reports to track each company's growth.",
  "summary":"Retail Oppose: a long-term investor of 25-plus years relies on quarterly reports to track company growth.",
  "role_full":"Individual investor"}

C[330] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["NR"],"literalist":["NR"],"inclusive":["NR"]},
  "stance_evidence":"'Please Keep 3 month reporting.'",
  "rationale_evidence":"NR: bare request to keep quarterly reporting.",
  "summary":"Bare retail Oppose: keep three-month reporting."}

C[331] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["AU","IP"],"literalist":["AU","IP"],"inclusive":["AU","IP","IA"]},
  "stance_evidence":"'By dropping our information down to twice a year our decision making would be severely affected... As a small investor, I request that you DO NOT approve this proposal.'",
  "rationale_evidence":"AU: the 10-Q is reviewed by independent auditors and signed by CEO and CFO under legal accountability, while the 'voluntary corporate communications that would replace them carry none of that'; IP: needs current, certified information to make buy/sell decisions; (Inc) IA: 'small investor'.",
  "summary":"Investment-club Oppose: a 30-year club uses quarterly reports for buy/sell decisions; halving them removes independently audited, personally signed filings that voluntary communications cannot replace.",
  "role_full":"Individual / investment-club member"}

C[332] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP","MF","IA"]},
  "stance_evidence":"'I am writing to express my strong opposition to the proposal of changing the 10-Q reporting requirement from a quarterly to a semi-annual basis.'",
  "rationale_evidence":"IP: relies on quarterly filings across 50-plus holdings to hold/buy/sell; frequent reporting keeps numbers reliable and transparent; 'investor protection'. (Inc) MF: 'market integrity'; (Inc) IA: individual investor.",
  "summary":"Retail Oppose: an individual holding 50-plus companies relies on quarterly filings to monitor positions; reducing frequency undercuts reliability, investor protection, and market integrity.",
  "role_full":"Individual investor"}

C[333] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP"]},
  "stance_evidence":"'I consider quarterly reports for the companies I own stock in or am considering owning as important in timely decisions.'",
  "rationale_evidence":"IP: quarterly reports support timely ownership decisions.",
  "summary":"Brief retail Oppose: quarterly reports matter for timely decisions on holdings and prospects.",
  "role_full":"Retired personal investor"}

C[334] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["NR"],"literalist":["NR"],"inclusive":["NR"]},
  "stance_evidence":"'The is crazy proposal. Who do you think this would help? Another Trump directed cop-out to the rich and influential!'",
  "rationale_evidence":"NR: no substantive disclosure argument. The 'cop-out to the rich and influential' / 'Trump directed' framing is a regulatory-capture sentiment, uncoded and logged as a PP-watch instance.",
  "summary":"Political retail Oppose: dismisses the proposal as a 'Trump directed cop-out to the rich and influential'. No substantive disclosure argument; FLAG: PP-watch (capture sentiment).",
  "role_full":"Retiree"}

C[335] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP"]},
  "stance_evidence":"'Please let's keep providing Quarterly reports for transparency and accountability.'",
  "rationale_evidence":"IP: transparency and accountability for regular analysis and financial decisions.",
  "summary":"Brief retail Oppose: keep quarterly reports for transparency and accountability."}

C[336] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP","ST"]},
  "stance_evidence":"'I think quarterly reports are essential for analyzing potential investments. They are also essential to spot problems with an investment...'",
  "rationale_evidence":"IP: quarterly reports analyze investments and spot problems early; (Inc) ST: surface mention that management should focus on long-term company health rather than stock prices.",
  "summary":"Retail Oppose: quarterly reports are essential to analyze investments and spot problems; management should still prioritize long-term company health over stock prices."}

C[337] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["CMP","IP"],"literalist":["CMP","IP"],"inclusive":["CMP","IP"]},
  "stance_evidence":"'As a long-term Investor I use Form 10-Q filings to monitor a company's financial health, short-term performance, and emerging risks between annual reports.'",
  "rationale_evidence":"IP: monitors financial health and emerging risks between annual reports; CMP: compares the current quarter's balance sheet, income, and cash-flow statements 'against the same period from the previous year to spot trends' (granularity/comparability across time).",
  "summary":"Retail Oppose: a long-term investor uses 10-Q filings to monitor risks and to compare each quarter against the prior-year quarter for trends; semiannual aggregation would erase that granularity.",
  "role_full":"Long-term investor"}

C[338] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["AU","IP"],"literalist":["AU","IP"],"inclusive":["AU","IP"]},
  "stance_evidence":"'I do not think it would be wise to drop quarterly reporting of financial information for companies.'",
  "rationale_evidence":"AU: 'A 10-Q is reviewed by independent auditors, and the CEO and CFO sign it personally and can be held legally accountable... The voluntary corporate communications that would replace them carry none of that'; IP: investors need this information for sound decisions.",
  "summary":"Retail Oppose: dropping quarterly reporting halves the independently reviewed, personally certified filings investors rely on; voluntary communications carry none of that accountability."}

C[339] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IA","IP"],"literalist":["IA","IP"],"inclusive":["IA","IP"]},
  "stance_evidence":"'I... oppose the SEC's proposal to replace quarterly reporting with semiannual reporting.'",
  "rationale_evidence":"IA: 'retail investors like myself and clubs will have less timely public information while the institutional investors will not lose much due to their deeper and more connected resources and access'; IP: quarterly reports track holdings, evaluate opportunities, and identify problems early.",
  "summary":"Retail Oppose: semiannual reporting leaves retail investors and investment clubs on stale information while institutions, with deeper resources and access, lose little; it weakens transparency and delays problem detection.",
  "role_full":"Personal investor / investment-club"}

C[340] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP"]},
  "stance_evidence":"'It is critical to continue to require companies to file quarterly reports... twice a year is not adequate.'",
  "rationale_evidence":"IP: quarterly data lets investors and interested parties analyze company performance; twice a year is inadequate.",
  "summary":"Brief retail Oppose: quarterly filings are critical for analyzing company data, and twice a year is not adequate."}

C[341] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IA","IP"],"literalist":["IA","IP"],"inclusive":["IA","IP"]},
  "stance_evidence":"'Please keep statements on a quarterly basis. It is the only window that a small investor has into the current state of any particular company.'",
  "rationale_evidence":"IP: quarterly statements are the window into a company's current state; IA: 'the only window that a small investor has', protecting the average investor.",
  "summary":"Retail Oppose: quarterly statements are the only window a small investor has into a company's current state.",
  "role_full":"Small investor"}

C[342] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["FR","IA"],"literalist":["FR","IA"],"inclusive":["FR","IA"]},
  "stance_evidence":"'Keep it quarterly... a 6 month cadence gives a huge advantage to institutions and insiders.'",
  "rationale_evidence":"IA: a six-month cadence 'gives a huge advantage to institutions and insiders' who react faster than individuals; FR: it gives companies 'more opportunity to wait on bad news'.",
  "summary":"Retail Oppose: a six-month cadence advantages institutions and insiders and lets companies sit on bad news, both at the individual investor's expense."}

C[343] = {"stance":OPP, "entity":IND,
  "rationales":{"primary":["IP"],"literalist":["IP"],"inclusive":["IP","IA","MF"]},
  "stance_evidence":"'I strongly oppose the move to only collect information from companies on a half year basis instead of quarterly.'",
  "rationale_evidence":"IP: against delayed, untimely, untrustworthy information ('Thou shalt not distort, delay, or sequester information'; 'all others bring data'); a public company should provide more information, not less. (Inc) IA: institutional investors expect monthly updates; (Inc) MF: markets fluctuate more quickly, not less.",
  "summary":"Retail Oppose: public listing carries a duty to provide more information, not less; delayed, sequestered data muddies the market, and the commenter would shift investments off public exchanges rather than accept it. Signs 'NAIC'.",
  "role_full":"Individual investor (NAIC)"}

C[344] = {"stance":OPP, "entity":{"primary":"Individual","selfdescribed":"Individual","letterhead":"Investment professional"},
  "rationales":{"primary":["AU","IA","IP"],"literalist":["AU","IA","IP"],"inclusive":["AU","IA","IP"]},
  "stance_evidence":"'I am writing to oppose the proposal to allow public companies to reduce financial reporting from quarterly to semiannual filings.'",
  "rationale_evidence":"AU: the 10-Q is 'reviewed by independent auditors, signed personally by the CEO and CFO, and subject to legal accountability', unlike less formal communications; IP: quarterly data evaluates companies, monitors performance, assesses risk; IA: the change 'would especially harm individual investors, who often own shares in the smaller public companies most likely to stop quarterly reporting'. Letterhead rater tags 'works with investors' as Investment professional; majority Individual.",
  "summary":"Retail Oppose: independently audited, personally certified 10-Qs cannot be replaced by less formal communications; the change hits individual investors hardest because smaller companies are likeliest to drop quarterly reporting.",
  "role_full":"Individual investor"}


def stance_agreement(s):
    vals=list(s.values()); return "unanimous" if vals.count(vals[0])==3 else "majority"
def majority_codes(r):
    c=Counter()
    for codes in r.values():
        for x in set(codes): c[x]+=1
    return sorted([x for x,k in c.items() if k>=2])
def rationale_agreement(r):
    sets=[tuple(sorted(set(v))) for v in r.values()]
    if len(set(sets))==1: return "unanimous"
    if sets[0]!=sets[1] and sets[1]!=sets[2] and sets[0]!=sets[2]: return "split"
    return "majority"

def update_record(rec,c):
    s,e,r=c["stance"],c["entity"],c["rationales"]
    maj=Counter(s.values()).most_common(1)[0][0]
    rec["primary_stance"]=s["primary"]; rec["literalist_stance"]=s["literalist"]; rec["skeptic_stance"]=s["skeptic"]
    rec["majority_stance"]=maj; rec["stance"]=maj; rec["agreement"]=stance_agreement(s)
    me=Counter(e.values()).most_common(1)[0][0]
    rec["entity_primary"]=e["primary"]; rec["entity_selfdescribed"]=e["selfdescribed"]; rec["entity_letterhead"]=e["letterhead"]
    rec["entity_majority"]=me; rec["entity"]=me
    rec["entity_agreement"]="unanimous" if Counter(e.values()).most_common(1)[0][1]==3 else "majority"
    rec["rationales_primary"]=sorted(r["primary"]); rec["rationales_literalist"]=sorted(r["literalist"]); rec["rationales_inclusive"]=sorted(r["inclusive"])
    maj_r=majority_codes(r); rec["rationales"]=maj_r; rec["rationales_majority"]=maj_r
    rec["rationale_agreement"]=rationale_agreement(r); rec["rationale_evidence"]=c["rationale_evidence"]
    rec["stance_evidence"]=c.get("stance_evidence","")
    rec["summary"]=c["summary"]
    if "role_full" in c: rec["role"]=c["role_full"]

HEADER=[("**Date:**","date"),("**Role/Affiliation:**","role"),("**Stance:**","stance"),("**Entity:**","entity"),("**Rationales:**","rationales_str"),("**Source:**","url")]
def patch_letter_header(p,rec):
    t=p.read_text()
    def fmt(f):
        if f=="rationales_str": return ", ".join(rec.get("rationales",[]))
        v=rec.get(f,""); return str(v) if v is not None else ""
    for marker,f in HEADER:
        pat=re.compile(r"^- "+re.escape(marker)+r".*$",re.MULTILINE)
        if pat.search(t): t=pat.sub(f"- {marker} {fmt(f)}".rstrip(),t,count=1)
    p.write_text(t)

def main():
    recs=json.loads(RECORDS.read_text()); by={r["n"]:r for r in recs}
    for n,c in C.items():
        if n not in by: print("[warn] missing",n); continue
        update_record(by[n],c)
    RECORDS.write_text(json.dumps(recs,indent=2,ensure_ascii=False)+"\n")
    print(f"[ok] updated renumbered_records.json ({len(recs)} records)")
    patched=0
    for n in C:
        for p in LETTERS.glob(f"{n}_*"):
            if p.suffix==".md": patch_letter_header(p,by[n]); patched+=1
    print(f"[ok] patched {patched} letter headers")

if __name__=="__main__": main()
