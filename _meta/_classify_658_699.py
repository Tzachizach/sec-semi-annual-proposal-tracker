#!/usr/bin/env python3
"""Classify drained letters #658-699 (May 30 - June 4 batch) — full 3-rater ensemble.

42 letters drained via the URL-list path. All Oppose except #695 Sara Brantley
("Sounds cool" -> No position, held out). Skeptic-flips to Conditional on alternative-
cadence proposals: #660 Ramesh ($75M float threshold), #678 Boyer (monthly), #694
Valiente (conditional insider-sell), #699 Biffl (monthly). PP: #687 Jeff Wickizer
("...at least under a republican administration" — explicit partisan attribution, same
template as #607). AU-template carrier: #689 Levester Best. Accountants: #671 Laura
Bowen, #674 Stephanie Micinski. Academic: #668 Piyush Shah.

Dates: the drain fell back to 2026-05-27 (URL_LIST_DEFAULT_DATE) for most because the body
dates read "Jun. 4, 2026" (abbreviated month the regex missed). Corrected to docket-truth.
"""
import json, os
from collections import Counter
from pathlib import Path

META = Path(__file__).resolve().parent
RECORDS = META / "renumbered_records.json"

OPP, CON, NOP = "Oppose", "Conditional", "No position"
IND = "Individual"; CPA = "Accountant (CPA)"; ACAD = "Academic researcher"

def st(p,l,s): return {"primary":p,"literalist":l,"skeptic":s}
def U(x): return st(x,x,x)
def en(p,sd,lh): return {"primary":p,"selfdescribed":sd,"letterhead":lh}
def EI(): return en(IND,IND,IND)
def E(x): return en(x,x,x)
def ra(p,l,i): return {"primary":p,"literalist":l,"inclusive":i}
def R(*codes): return ra(list(codes), list(codes), list(codes))  # unanimous rationale set

DATE = {}
for n in range(658,664): DATE[n]="2026-06-04"
for n in range(664,670): DATE[n]="2026-06-03"
for n in range(670,675): DATE[n]="2026-06-02"
for n in range(675,680): DATE[n]="2026-06-01"
for n in range(680,698): DATE[n]="2026-05-31"
DATE[698]="2026-05-30"; DATE[699]="2026-05-30"

NAME={671:("Laura Bowen","Accountant; retail investor"),679:("Victor Espericueta",None),
      689:("Levester Best","Investment-club member (31 years)")}

C = {
 658:{"s":U(OPP),"e":EI(),"r":R("IA","MF"),"re":"IA: retail deprived of info insiders have; MF: volatile economy changes 'on a dime'.","su":"Retired Sr. Business Analyst (ex Disclosure/Primark/Thomson Financial): quarterly financials are necessary for all investors in a volatile economy; semiannual would endanger all but insiders."},
 659:{"s":U(OPP),"e":EI(),"r":R("IA","IP"),"re":"IA: 'increases the information gap between corporate insiders and everyday investors'; IP: SEC mission to protect investors.","su":"Marine veteran, construction manager, retail investor: opposes; quarterly reports are one of the few tools retail has; reducing frequency widens the insider information gap and weakens investor protection."},
 660:{"s":st(OPP,OPP,CON),"e":EI(),"r":R("IA","CB","AL"),"re":"IA: insiders have continuous access; CB: AI makes a 10-Q cheap for large caps; AL: proposes semiannual only below a $75M float threshold.","su":"Retail investor (2 decades, options strategies): a 180-day blind spot disadvantages retail; proposes semiannual optional only for companies under ~$75M float, quarterly mandatory for large/mid caps. Skeptic flips to Conditional on the threshold proposal.","note":"Skeptic flips to Conditional on an alternative-cadence proposal (semiannual only below a $75M float threshold); majority stays Oppose."},
 661:{"s":U(OPP),"e":EI(),"r":R("MF","ICc","IA","FR"),"re":"MF: UK/EU 2014 shows liquidity dries up and spreads widen; FR: adverse selection — Form 10-S used by distressed issuers; IA: 180-day void favors institutional alt-data.","su":"Substantive Oppose: three mechanisms — liquidity reduction (UK/EU 2014 evidence), systemic adverse selection (distressed issuers use 10-S), and sanctioned information asymmetry."},
 662:{"s":U(OPP),"e":EI(),"r":R("IP","IA"),"re":"IP: reports 'essential for ensuring transparency and accountability'; IA: relies on them to avoid losing retirement savings.","su":"Energy compliance manager who trades to supplement income: keep quarterly reporting — essential for transparency and to avoid pitfalls."},
 663:{"s":U(OPP),"e":EI(),"r":R("IA","FR"),"re":"IA: six-month gap leaves retail 'flying blind' while insiders have full visibility; FR: Enron/WorldCom cautionary tales.","su":"Retail investor: opposes; information asymmetry is unfair, skeptical the 'voluntary' framing will hold, and longer gaps raise fraud risk (Enron, WorldCom)."},
 664:{"s":U(OPP),"e":EI(),"r":R("IP"),"re":"IP: 'Quarterly reporting is important to a fair and transparent open market.'","su":"Pilot: quarterly reporting is important to a fair and transparent market and must be kept."},
 665:{"s":U(OPP),"e":EI(),"r":R("IA","FR"),"re":"IA: insiders/institutions keep current info while retail is 'last to find out'; FR: Enron/WorldCom/2008 — opacity lets problems fester.","su":"Retail investor: cutting reporting in half leaves ordinary investors blind for six months; raises insider advantage and fraud risk; 'optional' will become de facto standard."},
 666:{"s":U(OPP),"e":EI(),"r":R("IA","SG"),"re":"IA: insiders gain advantage from earlier access; SG: only struggling/opaque firms opting in becomes a red flag.","su":"Three concerns: decreased transparency, increased insider/information-asymmetry risk, and a 10-S 'red flag' signaling effect."},
 667:{"s":U(OPP),"e":EI(),"r":R("US","ICc"),"re":"US: US markets are the global standard of transparency and stability; ICc: other countries' semiannual markets are smaller and show no benefit.","su":"Opposes: US markets are the world's largest and the global standard for transparency; no evidence semiannual reporting helped smaller foreign markets."},
 668:{"s":U(OPP),"e":E(ACAD),"r":R("IP","ST","CB"),"re":"IP/oversight: Boeing 737 MAX analogy — reduced independent oversight lets issues go undetected; ST: 3->6 months won't change managerial incentives; CB: AI automation makes savings modest.","su":"Assistant Professor (PhD): independent, timely oversight matters (737 MAX analogy); the long-termism rationale is unpersuasive; automation makes the cost savings modest."},
 669:{"s":U(OPP),"e":EI(),"r":R("ICc","IA"),"re":"ICc: Wirecard (EU), UK 2014 analyst-coverage loss, Singapore reconsidering; IA: businesses/lawyers know problems before shareholders.","su":"Citizen/investor: the 'global standard' is not working where tried — Wirecard, the UK's 2014 shift, Singapore reconsidering; detrimental to shareholders."},
 670:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'Letting companies sit on that information while insiders trade on it... tilting the table further toward Wall Street.'","su":"Small-business founder and retail investor: quarterly filings let him spot red flags; six months is an eternity; 'optional' becomes standard; savings accrue to companies, costs to retail."},
 671:{"s":U(OPP),"e":E(CPA),"r":R("IA","FR"),"re":"IA: structural disadvantage for those without a seat at the table; FR (accountant lens): Enron/WorldCom/2008 — quarterly cadence limits how long fraud goes undetected.","su":"Accountant and retail investor: information gap disadvantages retail; as an accountant, the fraud implications concern her most — semiannual doubles the window for undetected fraud."},
 672:{"s":U(OPP),"e":EI(),"r":R("IA","MF","CMP"),"re":"IA: institutions afford alt data (satellite/credit-card); MF: bigger surprises and volatile swings; CMP: biannual filings disrupt backtesting/data models.","su":"Trader/backtester: less transparency, bigger surprises, insider alt-data advantage, harder fraud detection, and disrupted historical data models."},
 673:{"s":U(OPP),"e":EI(),"r":R("IP"),"re":"IP: points to the SEC's three-pillar mission — none of which is acquiescing to corporate interests. Generic motive-questioning (not PP).","su":"Notes comments are overwhelmingly opposed and asks whose interests the proposal serves; cites the SEC's mission statement."},
 674:{"s":U(OPP),"e":E(CPA),"r":R("ICc","AU","CB"),"re":"ICc: UK/EU research finds no long-term-decision improvement; AU: quarterly reporting maintains strong internal controls; CB: savings overstated (firms already do monthly closes).","su":"CPA: international research does not support the long-termism premise; quarterly reporting sustains internal controls; cost savings are overstated and weaker-control firms may cut oversight."},
 675:{"s":U(OPP),"e":EI(),"r":R("FR"),"re":"FR: Citadel's hedge-fund + market-maker conflict; semiannual lets them 'cook the books twice a year instead of four'.","su":"Opposes: does not help retail; flags Citadel's market-maker/hedge-fund conflict of interest; halving reporting would be disastrous."},
 676:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'Investors need timely information to make sound decisions.'","su":"Site engineer: against the proposal; investors need timely information and transparency."},
 677:{"s":U(OPP),"e":EI(),"r":R("IA","MF"),"re":"IA: semiannual 'serves those with insider knowledge'; MF: would reduce confidence and market participation.","su":"Electrical engineer: quarterly reporting supports long-term stability; semiannual serves insiders and would reduce confidence and market participation."},
 678:{"s":st(OPP,OPP,CON),"e":EI(),"r":R("AL"),"re":"AL: 'in today's digital age we should have mandatory monthly reporting.'","su":"Information-security forensic analyst: reject the shift; if anything reporting should be monthly. Skeptic flips to Conditional on the alternative-cadence (monthly) proposal.","note":"Skeptic flips to Conditional on the alternative-cadence proposal (mandatory monthly); majority stays Oppose."},
 679:{"s":U(OPP),"e":EI(),"r":R("IA","MF"),"re":"IA: information gap favors institutions/insiders; MF: efficient price discovery and investor confidence depend on disclosure.","su":"Individual investor: timely information is one of the few tools to compete with institutions; quarterly reporting supports transparency, price discovery, governance, and confidence."},
 680:{"s":U(OPP),"e":EI(),"r":R("NR"),"re":"NR: 'Keep it quarterly. I want to know what I am investing in.'","su":"One line: keep it quarterly — wants to know what he is investing in."},
 681:{"s":U(OPP),"e":EI(),"r":R("FR"),"re":"FR: 'Quarterly reporting deters fraud and discourages manipulation.'","su":"Opposes: quarterly reporting deters fraud and manipulation and supports a transparent, growth-positive market."},
 682:{"s":U(OPP),"e":EI(),"r":R("IA","CC"),"re":"IA: wants to see what is happening for his 401k; CC: 'They need to keep their books anyway.'","su":"Opposes: information should be available more than twice a year; companies keep their books anyway and should keep disclosing."},
 683:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: quarterly reporting 'helps retail investors close the gap with powerful institutional investors'.","su":"Retail investor: opposes lengthening the reporting period; quarterly cadence closes the gap with institutional investors."},
 684:{"s":U(OPP),"e":EI(),"r":R("FR"),"re":"FR: 'Making it 1/2 a year would allow companies to fleece investors in new ways.'","su":"Calls the rule insane; longer gaps let companies fleece investors; suggests (rhetorically) weekly reporting."},
 685:{"s":U(OPP),"e":EI(),"r":R("FR","AU"),"re":"FR: removing the requirement 'will create more opportunities for fraud'; AU: cash flow can be manipulated more without quarterly reporting.","su":"Quarterly reporting forces transparency; removing it creates fraud opportunities and lets cash flow be manipulated."},
 686:{"s":U(OPP),"e":EI(),"r":R("IA","FR","ICc"),"re":"IA: executives get six months of silence to sell; FR: doubling the window helps bad actors conceal ruin; ICc: international attempts caused volatility and frauds, forcing reversals.","su":"Retail investor: opposes; six-month silence aids insider selling and fraud concealment; international attempts failed; 'voluntary' will become the norm."},
 687:{"s":U(OPP),"e":EI(),"r":R("FR","PP"),"re":"FR: 'everywhere you see biannual reporting you will find fraud'; PP: '...at least under a republican administration' — explicit partisan attribution (same template as #607).","su":"Opposes: not a world standard; associates biannual reporting with fraud and attributes the direction to the current (republican) administration. PP-watch flag."},
 688:{"s":U(OPP),"e":EI(),"r":R("NR"),"re":"NR: 'This is lunacy. Please reject the proposed reduction in reporting frequency.'","su":"Site reliability engineer: brief Oppose — reject the reduction in reporting frequency."},
 689:{"s":U(OPP),"e":EI(),"r":R("AU","RI"),"re":"AU: '10-Q is reviewed by independent auditors, and the CEO and CFO sign it personally... voluntary corporate communications carry none of that' (AU template); RI: 31-year investment club relies on quarterly reports.","su":"31-year investment-club member: carries the AU template (auditor-reviewed, CEO/CFO-certified 10-Q vs unaccountable voluntary communications); the club needs current certified filings to make decisions.","note":"AU-template carrier."},
 690:{"s":U(OPP),"e":EI(),"r":R("NR"),"re":"NR: 'You literally are saying you agree with corporate greed and corruption if you vote Yes.' Generic greed/corruption outburst — no political-pressure/capture attribution (not PP).","su":"Opposes: the SEC should increase disclosure, not reduce it; voting yes endorses corporate greed and corruption. No substantive economic argument."},
 691:{"s":U(OPP),"e":EI(),"r":R("FR"),"re":"FR: semiannual 'will greatly increase the ability of those who are not dealing in good faith to hide their actions.'","su":"Licensed HVAC technician: opposes; semiannual will not change short-sighted management but will help bad-faith actors hide their actions."},
 692:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: ordinary investors lack the access of executives/insiders/institutions; six months is too long to go dark.","su":"Retail investor: opposes; quarterly reports matter because ordinary investors lack insider access; 'optional' becomes standard."},
 693:{"s":U(OPP),"e":EI(),"r":R("MF"),"re":"MF: 'keep it quarterly otherwise you may see a total market crash!'","su":"Brief Oppose: keep reporting quarterly or risk a market crash."},
 694:{"s":st(OPP,OPP,CON),"e":EI(),"r":R("IA","AL"),"re":"IA: 'it will benefit insiders more than anyone else'; AL: conditional — 'if you do indeed apply it, then... enforce that insiders can only sell company stock twice a year'.","su":"Opposes; if adopted, proposes a parallel rule locking insiders (and politicians) to twice-a-year stock sales after earnings. Skeptic flips to Conditional on the conditional proposal.","note":"Skeptic flips to Conditional on a conditional alternative (insider-sell restriction if the rule is adopted); majority stays Oppose."},
 695:{"s":U(NOP),"e":EI(),"r":ra([],[],[]),"re":"No position: 'Sounds cool' — states no Oppose/Support/Conditional position on reporting frequency.","su":"Two-word submission ('Sounds cool') stating no position. Held out as No position."},
 696:{"s":U(OPP),"e":EI(),"r":R("NR"),"re":"NR: 'Is it NOT the idea to be as transparent as possible!' — pro-transparency thread amid unrelated tangents.","su":"Rambling submission opposing reduced transparency ('be as transparent as possible'); the rest digresses into unrelated topics. No substantive economic argument."},
 697:{"s":U(OPP),"e":EI(),"r":R("IP","MF"),"re":"IP: 'reduces transparency'; MF: 'may increase volatility'.","su":"Brief Oppose: semiannual reporting reduces transparency and may increase volatility."},
 698:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'We don't get enough [transparency] compared to insiders and large investors, and therefore are at a disadvantage.'","su":"Retail trader: keep quarterly earnings; transparency is key and retail is already at a disadvantage to insiders and large investors."},
 699:{"s":st(OPP,OPP,CON),"e":EI(),"r":R("IA","CB","AL"),"re":"IA: public filings are his primary source vs insiders; CB: the 'burden' is a pretext (an accountant produces it with a few clicks); AL: reports should be more frequent (monthly).","su":"Individual investor: public filings are his primary information source; the compliance 'burden' is a pretext to increase information disparity; disclosures should be more frequent, e.g. monthly. Skeptic flips to Conditional on the alternative-cadence proposal.","note":"Skeptic flips to Conditional on the alternative-cadence proposal (more frequent / monthly); majority stays Oppose."},
}


def majority_rationales(triple):
    c=Counter()
    for codes in (triple["primary"],triple["literalist"],triple["inclusive"]):
        for x in codes: c[x]+=1
    return sorted([x for x,n in c.items() if n>=2])


def main():
    records=json.loads(RECORDS.read_text())
    by_n={r["n"]:r for r in records}
    miss=[n for n in C if n not in by_n]
    if miss: raise SystemExit(f"missing: {miss}")
    for n,c in C.items():
        rec=by_n[n]
        if n in NAME:
            rec["name"]=NAME[n][0]
            if NAME[n][1]: rec["role"]=NAME[n][1]
        if n in DATE: rec["date"]=DATE[n]
        s=c["s"]; rec["primary_stance"]=s["primary"]; rec["literalist_stance"]=s["literalist"]; rec["skeptic_stance"]=s["skeptic"]
        mv=Counter(s.values()).most_common(1)[0][0]; rec["majority_stance"]=mv; rec["stance"]=mv
        rec["agreement"]="unanimous" if len(set(s.values()))==1 else "majority"
        e=c["e"]; rec["entity_primary"]=e["primary"]; rec["entity_selfdescribed"]=e["selfdescribed"]; rec["entity_letterhead"]=e["letterhead"]
        ev=Counter(e.values()).most_common(1)[0][0]; rec["entity_majority"]=ev; rec["entity"]=ev
        rec["entity_agreement"]="unanimous" if len(set(e.values()))==1 else "majority"
        r=c["r"]; rec["rationales_primary"]=r["primary"]; rec["rationales_literalist"]=r["literalist"]; rec["rationales_inclusive"]=r["inclusive"]
        rec["rationales_majority"]=majority_rationales(r); rec["rationales"]=rec["rationales_majority"]
        cats=[set(r["primary"]),set(r["literalist"]),set(r["inclusive"])]
        rec["rationale_agreement"]="unanimous" if cats[0]==cats[1]==cats[2] else "majority"
        rec["rationale_evidence"]=c.get("re",""); rec["summary"]=c.get("su",rec.get("summary",""))
        if "note" in c: rec["stance_note"]=c["note"]
    tmp=RECORDS.with_suffix(".json.tmp"); tmp.write_text(json.dumps(records,ensure_ascii=False,indent=2)); os.replace(tmp,RECORDS)
    HELD={"Duplicate","Off-topic","No position","Unclassified"}
    inc=[r for r in records if (r.get("majority_stance") or r.get("stance")) not in HELD]
    print(f"[classify 658-699] total={len(records)} in-corpus={len(inc)}")
    print("  stance:", dict(Counter(r['stance'] for r in inc)))
    held=Counter((r.get('majority_stance') or r.get('stance')) for r in records if (r.get('majority_stance') or r.get('stance')) in HELD)
    print("  held out:", dict(held))
    pp=[r['n'] for r in records if 'PP' in (r.get('rationales') or [])]
    print(f"  PP total: {len(pp)} (new this batch: 687={687 in pp})")
    unc=[r['n'] for r in records if (r.get('majority_stance') or r.get('stance'))=='Unclassified']
    print("  remaining Unclassified:", unc)


if __name__=="__main__":
    main()
