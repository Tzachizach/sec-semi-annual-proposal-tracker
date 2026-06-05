#!/usr/bin/env python3
"""Classify drained letters #726-751 (June 5 cohort + SIFMA + June 1-3 / May 31 stragglers).

All Oppose except #739 SIFMA — the SECOND comment-period extension request (60 days; cites
underwriter due-diligence questions, investor-information timeliness, comparability across
mixed cadences, the two overlapping offering-reform rulemakings, and the July 6 deadline
colliding with the 250th anniversary of American independence). No position (procedural),
Trade-association bucket (2nd member after Better Markets #701).

PP +1: #736 Theresa Duperon ("a lot of shady things are going on in the market and we have
criminals working in the White House") — explicit attribution to the political regime, per the
#607/#616 precedent. Excluded as NOT PP: #730 Dhabhar (generic motive-questioning + insiders-
vs-retail), #734 Parmelee (generic government-grift framing, no political mechanism named),
#746 Wright ("the game is already rigged" — insiders-vs-retail).
"""
import json, os
from collections import Counter
from pathlib import Path

META=Path(__file__).resolve().parent; RECORDS=META/"renumbered_records.json"
OPP,NOP="Oppose","No position"
IND="Individual"; INVP="Investment professional"; TRADE="Trade association / advocacy organization"

def st(p,l,s): return {"primary":p,"literalist":l,"skeptic":s}
def U(x): return st(x,x,x)
def en(p,sd,lh): return {"primary":p,"selfdescribed":sd,"letterhead":lh}
def EI(): return en(IND,IND,IND)
def E(x): return en(x,x,x)
def ra(p,l,i): return {"primary":p,"literalist":l,"inclusive":i}
def R(*c): return ra(list(c),list(c),list(c))

DATE={}
for n in range(726,738): DATE[n]="2026-06-05"
for n in (738,739,740): DATE[n]="2026-06-04"
DATE[741]="2026-06-03"
for n in range(742,749): DATE[n]="2026-06-01"
for n in (749,750,751): DATE[n]="2026-05-31"

NAME={729:("Colton Growney","Investment advisor (10 years), CFA charterholder"),
      733:("Lorna Pater",None),734:("Richard Parmelee",None),
      739:("Joseph Corcoran & Raymond Mosca, SIFMA","Managing Director & Associate General Counsel; AVP, Asset Management Group"),
      750:("Lawrence Schaffer II","Small business owner, LLC Serene Distribution (Tennessee)")}

C={
 726:{"s":U(OPP),"e":EI(),"r":R("IA","FR"),"re":"IA: quarterly reporting keeps individual investors informed; FR: 'duped by corporations' / books secret for six months.","su":"PhD retail investor: quarterly reporting keeps individuals informed about corporate risk; do not let companies keep their books secret for six months."},
 727:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'I'm not buying what I can't research.'","su":"One line: will not buy what cannot be researched; keep quarterly reporting."},
 728:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: retiree needs frequent updates on his financial situation.","su":"Retiree: frequent updates are imperative to avoid becoming 'a ward of the state'; keep quarterly reporting."},
 729:{"s":U(OPP),"e":E(INVP),"r":R("MF"),"re":"MF: semiannual reporting 'will reduce available information... making our capital markets less efficient and more prone to manipulation.'","su":"Investment advisor (10 years, CFA): semiannual reporting reduces information, makes capital markets less efficient and more manipulable — bad outcomes for issuers and investors alike."},
 730:{"s":U(OPP),"e":EI(),"r":R("IA","FR"),"re":"FR/IA: 'pave the way for more corruption and grift from insiders at the expense of retail investors.' Generic motive-questioning ('In whose interest is the SEC acting?') — not PP per the #620/#673 standard.","su":"Opposes: less frequent reporting enables insider grift at retail's expense; if quarterly reporting costs money, companies can trim executive pay."},
 731:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'I cannot make informed decisions about investing if I don't have up to date information.'","su":"Nurse practitioner: keep quarterly reporting; cannot invest informed without current information."},
 732:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'I'm not an industry insider... there will be market slippage while insiders take positions... before the public knows.'","su":"Investor since the 1970s: relies on contemporaneous audited financials; insiders would trade ahead of the public during the gap; enforcement after the fact does not undo retail losses."},
 733:{"s":U(OPP),"e":EI(),"r":R("RI","IA"),"re":"RI: 'I count on those quarterly reports to help me with my decisions I make with my retirement accounts.'","su":"Retail investor: counts on quarterly reports for retirement-account decisions; keep quarterly reporting."},
 734:{"s":U(OPP),"e":EI(),"r":R("IA","IP"),"re":"IP/IA: the rule 'will remove transparency about how our retirement funds are reported to us.' Generic 'grift on the American people' framing — no political mechanism named, not PP per the narrow definition.","su":"Opposes 'this new grift on the American people': the rule removes transparency and the ability to manage retirement investments with current performance information."},
 735:{"s":U(OPP),"e":EI(),"r":R("IA","MF"),"re":"IA: 'granting insiders an unfair advantage over retail investors'; MF: 'increase market volatility... trade on speculation rather than timely data.'","su":"Structured Oppose: six-month windows exacerbate information asymmetry and increase volatility as investors trade on speculation."},
 736:{"s":U(OPP),"e":EI(),"r":R("FR","PP"),"re":"FR: 'a lot of shady things are going on in the market'; PP: 'we have criminals working in the White House. That's impactful.' — explicit attribution to the political regime (qualifies per the #607/#616 precedent).","su":"Opposes: keep quarterly reporting because of market 'shady things' and — explicitly — 'criminals working in the White House.' PP-watch flag.","note":"PP-coded: explicit political-regime attribution ('criminals working in the White House')."},
 737:{"s":U(OPP),"e":EI(),"r":R("IP"),"re":"IP: quarterly reporting is 'open, and accessible to investors. Keeps you fellas honest.'","su":"Brief Oppose: quarterly reporting is open, accessible, and keeps companies honest; hands off."},
 738:{"s":U(OPP),"e":EI(),"r":R("IA","CMP","CC","ST"),"re":"IA: six-month gap widens the insider/public divide; CMP: 8-K releases lack financials/MD&A and mixed cadences destroy comparability; CC: lenders and debt covenants still require quarterly tracking; ST: short-termism is a governance issue, not a disclosure issue.","su":"Substantive Oppose: information asymmetry, the inadequacy of voluntary 8-K releases (fragmented disclosure, lost comparability), speculative cost savings given covenant requirements, and a rebuttal of the short-termism rationale."},
 739:{"s":U(NOP),"e":E(TRADE),"r":ra([],[],[]),
   "re":"No position (procedural): SIFMA + SIFMA AMG request a 60-day extension of the comment period. Reasons: underwriter due-diligence questions, timeliness of investor information, comparability across mixed cadences, two overlapping offering-reform rulemakings (S7-2026-17, S7-2026-18), and the July 6 deadline coinciding with the 250th anniversary of American independence. Defers substantive comments.",
   "su":"SIFMA (Joseph Corcoran, MD & Associate General Counsel) and SIFMA AMG (Raymond Mosca, AVP) — the leading broker-dealer/asset-manager trade association — request a 60-day extension of the comment period, citing the proposal's complexity (underwriter due diligence, investor-information timeliness, comparability), two overlapping offering-reform proposals, and the July 6 deadline's collision with the U.S. semiquincentennial. The second formal extension request on the docket (after Better Markets #701). Classified No position (procedural); entity Trade association / advocacy organization.",
   "note":"Second comment-period extension request (after Better Markets). Held out as No position; Trade-association bucket."},
 740:{"s":U(OPP),"e":EI(),"r":R("US","CB"),"re":"US: 'These quarterly reports are what gives the world faith to invest into US markets'; CB: companies should 'invest in better infrastructure' rather than report less.","su":"Opposes: quarterly reports underpin global faith in US markets; if reporting is hard, companies should invest in better infrastructure."},
 741:{"s":U(OPP),"e":EI(),"r":R("FR"),"re":"FR: 'Reducing reporting frequency increases the risk of market manipulation.'","su":"Brief Oppose: withdraw the proposal; less frequent reporting raises manipulation risk."},
 742:{"s":U(OPP),"e":EI(),"r":R("FR","IP"),"re":"IP: 'The SEC was created to ensure full and fair disclosure'; FR: 'With so much rampant fraud... reducing visibility of financials would only encourage more.'","su":"Opposes: the SEC exists for full and fair disclosure; reduced visibility encourages more fraud."},
 743:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'Information asymmetry harms ordinary investors most.'","su":"One line: opposes; information asymmetry harms ordinary investors most."},
 744:{"s":U(OPP),"e":EI(),"r":R("FR"),"re":"FR: 'Less disclosure means more opportunity for corporate misconduct.'","su":"Brief Oppose: less disclosure means more corporate misconduct."},
 745:{"s":U(OPP),"e":EI(),"r":R("IP"),"re":"IP: the shift 'decreases investor transparency.'","su":"Brief Oppose: decreases investor transparency; not the right direction."},
 746:{"s":U(OPP),"e":EI(),"r":R("IA"),"re":"IA: 'The game is already rigged. Please don't make it worse!' (insiders-vs-retail framing — not PP).","su":"Brief Oppose: the game is already rigged against ordinary investors; do not make it worse."},
 747:{"s":U(OPP),"e":EI(),"r":R("FR"),"re":"FR: 'Reducing reporting frequency increases the risk of market manipulation.'","su":"Brief Oppose: manipulation risk; do not take information away from the public."},
 748:{"s":U(OPP),"e":EI(),"r":R("FR"),"re":"FR: 'We need to reduce fraud in our system, not increase it.'","su":"Brief Oppose: the system needs less fraud, not more."},
 749:{"s":U(OPP),"e":EI(),"r":R("FR","MF"),"re":"FR: 'Allowing companies to hide their bad numbers whilst continuing to offer shares' is 'buying a pig in a poke'; MF: 'This action would absolutely chill our stock market. Serious investors will turn their backs on US companies.'","su":"Vivid Oppose: a six-month dark period lets companies hide bad numbers while selling shares; serious investors would shun US companies and the market would chill."},
 750:{"s":U(OPP),"e":EI(),"r":R("IP","IA"),"re":"IP: 'the public is protected from losses in their stock portfolios that they rely on for retirement.'","su":"Small business owner (Tennessee): calls the change an atrocity; public companies should keep filing quarterly so the retirement-investing public is protected."},
 751:{"s":U(OPP),"e":EI(),"r":R("IA","FR"),"re":"IA/FR: timely disclosure prevents 'insiders from slowly dumping stock during a longer blackout from public filings.'","su":"Medical-device sales professional: harmful to consumers and retirement savers; timely transparency prevents insiders from quietly dumping stock during a longer blackout."},
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
    print(f"[classify 726-751] total={len(recs)} in-corpus={len(inc)}")
    print("  stance:", dict(Counter(r['stance'] for r in inc)))
    print("  held:", dict(Counter((r.get('majority_stance') or r.get('stance')) for r in recs if (r.get('majority_stance') or r.get('stance')) in HELD)))
    print("  PP:", sum(1 for r in recs if 'PP' in (r.get('rationales') or [])))
    print("  Trade-assoc:", sum(1 for r in recs if r.get('entity')==TRADE))
    print("  unclassified left:", [r['n'] for r in recs if (r.get('majority_stance') or r.get('stance'))=='Unclassified'])


if __name__=="__main__": main()
