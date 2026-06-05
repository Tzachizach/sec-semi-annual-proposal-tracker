#!/usr/bin/env python3
"""Classify drained letters #700-725 (May 30 cohort + June 4-5 + Better Markets).

All Oppose except #701 Better Markets (comment-period extension request -> No position,
held out, Trade-association/advocacy entity). #723 Todd Mathews skeptic-flips to Conditional
on an alternative-cadence proposal (every two months). No new PP — #714 Michael George cites
Trump-administration insider-trading controversies, but as a fraud-risk analogy, not as
political-pressure attribution of the rule itself. Dates: 700=06-05, 701=06-04, 702-725=05-30.
"""
import json, os
from collections import Counter
from pathlib import Path

META=Path(__file__).resolve().parent; RECORDS=META/"renumbered_records.json"
OPP,CON,NOP="Oppose","Conditional","No position"
IND="Individual"; INDP="Industry practitioner / technologist"; TRADE="Trade association / advocacy organization"

def st(p,l,s): return {"primary":p,"literalist":l,"skeptic":s}
def U(x): return st(x,x,x)
def en(p,sd,lh): return {"primary":p,"selfdescribed":sd,"letterhead":lh}
def EI(): return en(IND,IND,IND)
def E(x): return en(x,x,x)
def ra(p,l,i): return {"primary":p,"literalist":l,"inclusive":i}
def R(*c): return ra(list(c),list(c),list(c))

DATE={700:"2026-06-05",701:"2026-06-04"}
for n in range(702,726): DATE[n]="2026-05-30"
NAME={701:("Dennis M. Kelleher & Benjamin L. Schiffrin, Better Markets, Inc.","Cofounder/President/CEO; Director of Securities Policy"),
      702:("Anonymous","Equity compensation expert"),713:("Ken Berg",None),715:("Omar Ziadeh","Software engineer"),
      720:("Saul Rosenberg","Retired"),725:("Gary Peterson","Curizen")}

C={
 700:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'investors are kept in the dark about stock performance'; retiree managing funds in a downturn.","su":"Retiree: reject the proposal; investors should not be kept in the dark about stock performance, especially retirees managing funds in a downturn."},
 701:{"s":U(NOP),"e":E(TRADE),"r":ra([],[],[]),
   "re":"No position (procedural): a comment-period EXTENSION request — Better Markets asks for 60 more days (120 total), noting the proposal is 279 pages with 58 RFCs while the shorter 2018 request got 90 days; it explicitly defers its substantive position ('looks forward to providing its own substantive comments'). Argues at length for quarterly reporting's value to retail (IA/IP) but takes no Support/Oppose/Conditional stance.",
   "su":"Better Markets (Dennis Kelleher, Cofounder/President/CEO; Benjamin Schiffrin, Director of Securities Policy) — a non-profit financial-reform advocacy organization — requests a 60-day extension of the comment period (to 120 days total), arguing the 279-page, 58-RFC proposal needs more time and that the far shorter 2018 request got 90 days. It defers its substantive position to a later filing. Classified No position (procedural extension request); entity Trade association / advocacy organization. Cross-docket: Better Markets also commented in 2018 (#044).",
   "note":"Procedural comment-period extension request; defers a substantive stance. Held out as No position. First letter in the Trade-association / advocacy entity bucket."},
 702:{"s":U(OPP),"e":en(IND,INDP,INDP),"r":R("FR","IA"),"re":"FR/IA: 'You simply cannot assume individuals will act in the best interest of their countrymen with their personal compensation on the line'; SEC filings demand accountability for public-company leaders.","su":"Equity-compensation expert: SEC filing obligations protect investors and demand accountability from public-company leaders whose pay is on the line; reducing visibility hurts the investing public."},
 703:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: quarterly reporting informs shareholders of company health; delay can devastate investment assets in a fast-moving world.","su":"Opposes: quarterly reporting informs shareholders; in a fast-moving world delay can devastate investors' assets."},
 704:{"s":U(OPP),"e":EI(),"r":R("FR","IP"),"re":"IP: 'The SEC was created to ensure full and fair disclosure'; FR: '6 months would allow longer grifts.'","su":"Reject: a 3-month requirement is not burdensome; six months would allow longer grifts; the SEC exists for full and fair disclosure."},
 705:{"s":U(OPP),"e":EI(),"r":R("IA","FR"),"re":"IA: reports let him make changes sooner than six months later; FR: longer gaps make it 'seem like... companies are hiding their losses and profits' and harder to hold them accountable.","su":"Former active investor: quarterly reports let investors act sooner and hold companies accountable; longer gaps look like companies hiding losses, profits, and mistakes."},
 706:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'My investment information is much more current if the SEC reports are quarterly.'","su":"Objects: investment information is much more current under quarterly reporting; keep the quarterly system."},
 707:{"s":U(OPP),"e":EI(),"r":R("RI","IA"),"re":"RI: 'As an individual invested the quarterly reports are very important to me. I watch my holdings carefully.'","su":"BetterInvesting individual investor: quarterly reports are very important for watching holdings closely, including large positions; opposes semiannual."},
 708:{"s":U(OPP),"e":EI(),"r":R("MF"),"re":"MF: removing quarterly reporting 'will discourage individual investors... and drive them towards alternative assets,' damaging public markets.","su":"Consulting engineer (Northrop Grumman), writing as an investor: quarterly reporting is essential; removing it would push individual investors toward alternative assets and damage public markets."},
 709:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'it will put retail investors at a significant disadvantage.'","su":"One line: opposes; the rule puts retail investors at a significant disadvantage."},
 710:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'More information for investors is critical. Less timely information is BAD.'","su":"Brief Oppose: more, timelier information for investors is critical."},
 711:{"s":U(OPP),"e":EI(),"r":R("MF"),"re":"MF: 'Less disclosure means slower price discovery.'","su":"Opposes: less disclosure means slower price discovery."},
 712:{"s":U(OPP),"e":EI(),"r":R("NR"),"re":"NR: 'How is only semi-annual reporting a good thing?? Keep the quarterly reporting!!'","su":"Brief Oppose: keep quarterly reporting."},
 713:{"s":U(OPP),"e":EI(),"r":R("IA","CMP"),"re":"IA: retail relies on public disclosures while institutions have private research/alt-data; CMP: optional semiannual makes companies harder to compare; Form 8-K is not an adequate substitute for the 10-Q.","su":"Substantive Oppose: quarterly 10-Qs underpin market trust; retail relies on public disclosures; Form 8-K is no substitute; optional semiannual reduces comparability across peers."},
 714:{"s":U(OPP),"e":EI(),"r":R("IA","FR","MF"),"re":"IA: institutions buy alt-data/channel checks while retail relies on the 10-Q; MF: stale data and 'unpriced stock shocks'; FR: a 180-day window 'exponentially increases the risk of insider trading' (cites Trump-administration pandemic-briefing controversies as a fraud-risk analogy, not political-pressure attribution).","su":"Strong Oppose: a six-month cadence exacerbates information asymmetry and volatility and lengthens the window for insider trading; cites pandemic-era insider controversies as a cautionary example."},
 715:{"s":U(OPP),"e":EI(),"r":R("IP"),"re":"IP: 'The SEC was created to ensure full and fair disclosure. Reducing reporting is a net negative for all investors.'","su":"Software engineer: opposes; the SEC exists for full and fair disclosure and reducing reporting is a net negative for all investors."},
 716:{"s":U(OPP),"e":EI(),"r":R("IP"),"re":"IP: 'Average investors should not be kept in the dark. We need transparency.'","su":"Brief Oppose: average investors should not be kept in the dark; transparency is needed."},
 717:{"s":U(OPP),"e":EI(),"r":R("MF","RI"),"re":"MF/RI: 'The loss of quarterly reporting raises the risk threshold for me as an investor.'","su":"Individual investor (mentions Two Rivers Investment Group): losing quarterly reporting raises his investment risk threshold; urges disapproval."},
 718:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'I rely on the quarterly reports to track... how well management is doing... A lot can go wrong in 3 months and even more could go wrong in 6 months.'","su":"Relies on quarterly reports to track management performance; six months would impair his ability to monitor the companies he invests in."},
 719:{"s":U(OPP),"e":EI(),"r":R("IA","FR"),"re":"IA: 'Information asymmetry harms ordinary investors most'; FR: 'Less reporting means more insider trading opportunities.'","su":"Opposes: information asymmetry harms ordinary investors and less reporting means more insider-trading opportunities."},
 720:{"s":U(OPP),"e":EI(),"r":R("MF"),"re":"MF: 'Every six months is way too long. Situations and competition makes major changes faster and faster these days.'","su":"Retired investor (Saul Rosenberg): keep quarterly reporting as has been done for half a century; six months is too long given how fast competition and conditions change."},
 721:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'Quarterly reporting is essential for investors to understand the health and direction of publicly traded companies, now more than ever.'","su":"Brief Oppose: quarterly reporting is essential to understand company health and direction."},
 722:{"s":U(OPP),"e":EI(),"r":R("RI","CB"),"re":"RI: quarterly reporting is 'the best tool' to monitor public companies; CB: 'With AI tools this should present a hardship to these companies' (i.e. automation makes it cheap, rebutting the burden claim).","su":"BetterInvesting individual investor: quarterly reporting is the best tool to monitor public companies, and AI tools mean it should not be a hardship for issuers."},
 723:{"s":st(OPP,OPP,CON),"e":EI(),"r":R("IA","AL"),"re":"IA: 'Removing quarterly reports tilts the playing field toward institutions'; AL: 'the SEC should increase the reporting to once every two months.'","su":"Small investor: opposes; the rule tilts toward institutions; proposes increasing reporting to every two months. Skeptic flips to Conditional on the alternative-cadence proposal.","note":"Skeptic flips to Conditional on the alternative-cadence proposal (every two months); majority stays Oppose."},
 724:{"s":U(OPP),"e":EI(),"r":R("FR","IA"),"re":"FR: less public information 'increase[s] pressure for certain types of professional investors to get information through unofficial/illegal channels'; IA: harder for honest investors.","su":"Opposes: reducing public information makes investing harder for honest investors and pressures professionals toward unofficial/illegal information channels."},
 725:{"s":U(OPP),"e":EI(),"r":R("IP"),"re":"IP: 'the public needs to know legal detail about any company traded publicly to make a reasoned investment decision.'","su":"Opposes: the public needs detailed disclosure on any publicly traded company to make reasoned investment decisions."},
}


def majority_rationales(t):
    c=Counter()
    for codes in (t["primary"],t["literalist"],t["inclusive"]):
        for x in codes: c[x]+=1
    return sorted([x for x,n in c.items() if n>=2])


def main():
    recs=json.loads(RECORDS.read_text()); by_n={r["n"]:r for r in recs}
    miss=[n for n in C if n not in by_n]
    if miss: raise SystemExit(f"missing: {miss}")
    for n,c in C.items():
        r=by_n[n]
        if n in NAME:
            r["name"]=NAME[n][0]
            if NAME[n][1]: r["role"]=NAME[n][1]
        if n in DATE: r["date"]=DATE[n]
        s=c["s"]; r["primary_stance"]=s["primary"]; r["literalist_stance"]=s["literalist"]; r["skeptic_stance"]=s["skeptic"]
        mv=Counter(s.values()).most_common(1)[0][0]; r["majority_stance"]=mv; r["stance"]=mv
        r["agreement"]="unanimous" if len(set(s.values()))==1 else "majority"
        e=c["e"]; r["entity_primary"]=e["primary"]; r["entity_selfdescribed"]=e["selfdescribed"]; r["entity_letterhead"]=e["letterhead"]
        ev=Counter(e.values()).most_common(1)[0][0]; r["entity_majority"]=ev; r["entity"]=ev
        r["entity_agreement"]="unanimous" if len(set(e.values()))==1 else "majority"
        rr=c["r"]; r["rationales_primary"]=rr["primary"]; r["rationales_literalist"]=rr["literalist"]; r["rationales_inclusive"]=rr["inclusive"]
        r["rationales_majority"]=majority_rationales(rr); r["rationales"]=r["rationales_majority"]
        cats=[set(rr["primary"]),set(rr["literalist"]),set(rr["inclusive"])]
        r["rationale_agreement"]="unanimous" if cats[0]==cats[1]==cats[2] else "majority"
        r["rationale_evidence"]=c.get("re",""); r["summary"]=c.get("su",r.get("summary",""))
        if "note" in c: r["stance_note"]=c["note"]
    tmp=RECORDS.with_suffix(".json.tmp"); tmp.write_text(json.dumps(recs,ensure_ascii=False,indent=2)); os.replace(tmp,RECORDS)
    HELD={"Duplicate","Off-topic","No position","Unclassified"}
    inc=[r for r in recs if (r.get("majority_stance") or r.get("stance")) not in HELD]
    print(f"[classify 700-725] total={len(recs)} in-corpus={len(inc)}")
    print("  stance:", dict(Counter(r['stance'] for r in inc)))
    print("  held:", dict(Counter((r.get('majority_stance') or r.get('stance')) for r in recs if (r.get('majority_stance') or r.get('stance')) in HELD)))
    print("  Trade-assoc entity:", sum(1 for r in recs if r.get('entity')==TRADE))
    print("  unclassified left:", [r['n'] for r in recs if (r.get('majority_stance') or r.get('stance'))=='Unclassified'])


if __name__=="__main__": main()
