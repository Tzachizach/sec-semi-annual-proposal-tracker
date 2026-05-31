#!/usr/bin/env python3
"""Integration for letters #345-#462 (2026-05-31 manual harvest, 118 records).

These were fetched via the URL-list drain in daily_fetch.py after the SEC docket's
CloudFront pager went stale (only page 1 was reachable through the index). Tzachi
harvested every letter URL from his browser; the bodies were fetched server-side.

Full 3-rater ensemble (Stance: Primary/Literalist/Skeptic; Entity: Primary/
Self-described/Letterhead; Rationale: Primary/Literalist/Inclusive). Outcome:
all 116 substantive letters Oppose; 0 Support; the only non-Oppose calls are the
skeptic rater flagging three hybrid-alternative letters Conditional (majority
still Oppose). Two records are verbatim duplicates held out of the count.

Entity: overwhelmingly Individual. Exceptions: #347 Phil Fodera (CPA) and #430
Steve Thurston (retired, two national CPA firms) -> Accountant (CPA); #424 John
Hancock (attorney at an insurance/asset-management firm) -> Investment professional
(majority; self-described attorney); #453 Corporate Governance Class -> Student.

Duplicates (verbatim re-submissions, _0 vs base variants on the docket):
  #406 Clifton Hosmer  == #403  -> stance "Duplicate" (held out)
  #423 Jeremiah Scepaniak == #421 -> stance "Duplicate" (held out)

RFC engagement: #462 Andrew Parker (amended PDF comment; relates to #99) names and
answers Request for Comment 18 and 26 on ICFR / material-weakness detection ->
rfc_questions {18, 26}. RFC-engagement count rises 3 -> 4 (#14, #99, #236, #462).
No other letter in this batch cites a numbered RFC.

FLAG: political / regulatory-capture sentiment (PP-watch, STATUS 6.6) is now broad
in the retail surge — #346, #358, #378, #397, #426, #451, #458, #460 among others.
Running count is well past the 7-10 threshold; PP likely warrants promotion from a
watch item to a coded rationale. Left uncoded here pending Tzachi's call.
"""
import json, re
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RECORDS = PROJECT / "_meta" / "renumbered_records.json"
LETTERS = PROJECT / "Letters"

IND   = {"primary":"Individual","selfdescribed":"Individual","letterhead":"Individual"}
CPA   = {"primary":"Accountant (CPA)","selfdescribed":"Accountant (CPA)","letterhead":"Accountant (CPA)"}
IPROF = {"primary":"Investment professional","selfdescribed":"Industry practitioner / technologist","letterhead":"Investment professional"}
STU   = {"primary":"Student","selfdescribed":"Student","letterhead":"Academic researcher"}
PORT  = {"primary":"Individual","selfdescribed":"Individual","letterhead":"Industry practitioner / technologist"}
OPP   = {"primary":"Oppose","literalist":"Oppose","skeptic":"Oppose"}
OPC   = {"primary":"Oppose","literalist":"Oppose","skeptic":"Conditional"}

def R(p,l,i): return {"primary":p,"literalist":l,"inclusive":i}

C = {}
def add(n, stance, entity, rat, se, re_, summ, role=None, rfc=None):
    C[n] = {"stance":stance,"entity":entity,"rationales":rat,"stance_evidence":se,
            "rationale_evidence":re_,"summary":summ}
    if role: C[n]["role_full"]=role
    if rfc: C[n]["rfc"]=rfc

add(345, OPP, IND, R(["AU","IP"],["AU","IP"],["AU","IP"]),
    "'A strong NO to eliminating these and going to a voluntary reporting system.'",
    "AU: independently audited quarterly reports as a minimal accountability standard; IP: accountability.",
    "Retail Oppose: independently audited quarterly reports are a minimal accountability standard; a voluntary system is a strong no.")
add(346, OPP, IND, R(["IP"],["IP"],["IP","IA"]),
    "'Please STOP... keep every investor current on all happenings within the company.'",
    "IP: keeping every investor current on company happenings; (Inc) IA: 'the biggest money always gets the biggest opportunities to change the rules' (capture sentiment, PP-watch).",
    "Retail Oppose: a rule that fails to keep every investor current invites corruption; the biggest money should not get to change the rules. FLAG: PP-watch.")
add(347, OPP, CPA, R(["IP"],["IP"],["IP","IA"]),
    "'I am firmly against changing the SEC quarterly reporting requirement.'",
    "IP: quarterly gives current information; semiannual leaves no time to react; (Inc) IA: 'financial hardship to all investors'.",
    "CPA Oppose: quarterly information lets investors react in time; semiannual reporting would harm all investors.",
    role="CPA")
add(348, OPP, PORT, R(["NR"],["NR"],["NR"]),
    "'Please reject this proposal.'", "NR: bare rejection.",
    "One-line Oppose: reject the proposal.")
add(349, OPP, IND, R(["IP"],["NR"],["IP"]),
    "'I would like to see quarterly reports as we have seen on a regular basis.'",
    "IP: wants the regular quarterly cadence of reports preserved.",
    "Brief retail Oppose: keep the regular quarterly cadence.")
add(350, OPP, IND, R(["IA","IP"],["IA","IP"],["IA","IP"]),
    "'This will put many of the individual investors at a disadvantage.'",
    "IA: smaller companies will stop reporting quarterly, disadvantaging individual investors; IP: relies on quarterly reports to see small/mid-cap progress.",
    "Retail Oppose: smaller companies dropping quarterly reporting would disadvantage individual investors who depend on that data, and the commenter would invest less without it.")
add(351, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Quarterly reports gives me an ideal of how the company is doing sooner than later.'",
    "IP: quarterly reports show company performance sooner.",
    "Brief retail Oppose: quarterly reports show how a company is doing sooner.")
add(352, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Making these reports available only two times per year will reduce the timeliness... and therefore reduce accuracy of investment decisions.'",
    "IP: timeliness and accuracy of quarterly financial information for decisions.",
    "Retail Oppose: semiannual reporting reduces the timeliness and accuracy of the information an individual investor relies on.")
add(353, OPP, IND, R(["IP","IA"],["IP","IA"],["IP","IA"]),
    "'I am opposed to modifying the current system of quarterly financial reports.'",
    "IP: verified, accurate quarterly reports are critical to retirement decisions; IA: 'I don't have other resources that I can use and trust' (retail reliance).",
    "Retired-investor Oppose: verified quarterly reports are the only trustworthy resource a self-directed retiree has for sound investment decisions.",
    role="Retired individual investor")
add(354, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'We need the surly [quarterly] reports.'", "NR: bare request to keep quarterly reports.",
    "Brief retail Oppose: keep the quarterly reports.")
add(355, OPP, IND, R(["IP"],["IP"],["IP","MF"]),
    "'As an investor, I want to be able to read quarterly reports on my investments.'",
    "IP: companies have an obligation to inform investors frequently; (Inc) MF: markets and trends are read more accurately with quarterly reporting.",
    "Retail Oppose: companies that hold investors' money owe them frequent (quarterly) performance reporting.")
add(356, OPP, IND, R(["AU","FR","IP"],["AU","FR","IP"],["AU","FR","IP"]),
    "'I encourage you to keep the current quarterly SEC filing requirements... NOT to reduce such filing requirements to a semi-annual basis.'",
    "AU: audited, fairly-stated quarterly reports; FR: more frequent reporting allows quicker discovery of fraudulent financial activity; IP: lets investors review financial health more often.",
    "Retail Oppose (Better Investing member): audited quarterly reports surface fraud faster and let individual investors review company health more often.",
    role="Individual investor / Better Investing member")
add(357, OPP, IND, R(["IA","FR"],["IA","FR"],["IA","FR","ICc"]),
    "'Please maintain quarterly reporting. As a small investor semi annual will ensure I do not have the information I need.'",
    "IA: small investor would lack needed information; FR: 'Global semi annual reporting is not showing well and has hid major frauds'; (Inc) ICc: international semiannual experience read as cautionary.",
    "Small-investor Oppose: semiannual reporting starves retail of needed information and, internationally, has hidden major frauds.")
add(358, OPP, IND, R(["FR","IA"],["FR","IA"],["FR","IA"]),
    "'I oppose allowing companies to opt out of quarterly reporting.'",
    "FR: the change 'will enable fraud and encourage insider trading'; IA: 'no benefit to investors or stakeholders who are not corporate insiders'. Capture aside ('corporate lobbyists') uncoded (PP-watch).",
    "Retail Oppose: opting out of quarterly reporting benefits only insiders and enables fraud and insider trading at the public's expense. FLAG: PP-watch.")
add(359, OPP, IND, R(["AU","IP"],["AU","IP"],["AU","IP","IA"]),
    "'as a small investor, I request that you DO NOT approve this proposal.'",
    "AU: the 10-Q is reviewed by independent auditors and signed by CEO/CFO under legal accountability, unlike the voluntary communications that would replace it; IP: needs current information for buy/sell decisions; (Inc) IA: small investor.",
    "Investment-club Oppose (31 years): halving quarterly filings removes independently audited, personally certified reports that voluntary communications cannot replace.")
add(360, OPP, IND, R(["IP","FR"],["IP","FR"],["IP","FR"]),
    "'having even less visibility on companies... is a terrible idea that seeks only to harm those not in the know.'",
    "IP: less visibility harms ordinary investors; FR: as a cost analyst, quarterly reporting catches issues before they 'fester and spread like rot'.",
    "Retail Oppose (cost analyst): semiannual reporting lets problems fester undetected and harms those without inside access.")
add(361, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'I am against reducing the number of SEC filings to two per year. Please continue quarterly filings.'",
    "NR: bare opposition.", "Brief retail Oppose: keep quarterly filings.")
add(362, OPP, IND, R(["IA","FR","IP"],["IA","FR","IP"],["IA","FR","IP"]),
    "'I'm opposed to semiannual reporting... it puts stock investors at a disadvantage.'",
    "IA: owned semiannual-reporting stocks (Roche, European banks) and found them disadvantaging; FR: 'the investor might wait 6 to 7 months... Meanwhile insiders start to SELL'; IP: 'quarterly TRANSPARENCY is CRITICAL'.",
    "Buy-and-hold Oppose: first-hand experience with semiannual reporters shows investors wait months for bad news while insiders sell; quarterly transparency is critical.")
add(363, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'having the most recent data is essential in helping the club members determine which stocks to invest in.'",
    "IP: recent data is essential for investment-club stock selection.",
    "Investment-club Oppose: recent quarterly data is essential to choosing investments.",
    role="Investment club")
add(364, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Transparency of impact to society needs to grow and not diminish.'",
    "IP: 'That which is done in obscurity leads to tyranny' — transparency argument.",
    "Brief retail Oppose: transparency must grow, not diminish; obscurity invites abuse.")
add(365, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'As an individual investor I rely on quarterly reports to make investment decisions.'",
    "IP: relies on quarterly reports for decisions.",
    "Retail Oppose: an individual investor relies on quarterly reports; halving the information is unhelpful.")
add(366, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Quarterly reports are currently the only opportunity to talk to your company in an official capacity.'",
    "IP: quarterly reports are the investor's only official window into the company.",
    "Retail Oppose: quarterly reporting is the minimum official window investors have; semiannual would deter investing.")
add(367, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'The proposed rule will leave investors too long in the dark between reporting periods.'",
    "IP: longer gaps leave investors in the dark; current climate makes frequent reporting essential.",
    "Retail Oppose: in the current climate more frequent reporting is essential; semiannual leaves investors too long in the dark.")
add(368, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Please keep the reporting period for every quarter.'", "NR: bare request.",
    "Brief retail Oppose: keep quarterly reporting.")
add(369, OPP, IND, R(["IP"],["IP"],["IP","ST"]),
    "'Please do not reduce quarterly reports to two times a year.'",
    "IP: club members rely on quarterly data for timely buy/sell decisions; (Inc) ST: quarterly reports 'help keep corporate management on course'.",
    "Investment-club Oppose: members rely on quarterly data for timely decisions, and the cadence keeps management on course.")
add(370, OPP, IND, R(["IA","IP"],["IA","IP"],["IA","IP"]),
    "'quarterly reporting is critical for transparency and investor due diligence, especially for smaller companies.'",
    "IA: smaller-company disclosure ensures small investors are not left at a disadvantage; IP: transparency and due diligence.",
    "Retail Oppose (finance background): quarterly transparency protects small investors in volatile smaller companies whose value can swing sharply within a quarter.")
add(371, OPP, IND, R(["IP","AU"],["IP","AU"],["IP","AU"]),
    "'I vote NO to reducing the SEC quarterly filings requirements.'",
    "IP: uses quarterly reports for portfolio decisions; AU: filings 'hold the Companies Top Executives to be accountable so we do not have another Enron'.",
    "Retail Oppose: quarterly filings hold executives accountable and guard against another Enron.")
add(372, OPP, IND, R(["IA","IP"],["IA","IP"],["IA","IP","FR"]),
    "'I am writing as an individual retail investor to express my strong opposition.'",
    "IA: retail investors lack the proprietary research and management access institutions have, widening information asymmetry; IP: timely insight and management accountability; (Inc) FR: discourages earnings manipulation, earlier warning of distress.",
    "Reasoned retail Oppose: semiannual reporting widens the information gap institutions already enjoy and weakens the management accountability that quarterly disclosure enforces.")
add(373, OPP, IND, R(["IP"],["IP"],["IP","IA"]),
    "'This change only benefits corporations, it does not allow investors to look into the company financials.'",
    "IP: investors lose the ability to look into company financials; (Inc) IA: benefits corporations over investors.",
    "Brief retail Oppose: the change benefits corporations and blinds investors to company financials.")
add(374, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'I feel it is vitally important that public companies continue to report quarterly. This transparency is needed.'",
    "IP: transparency of quarterly reporting is needed.",
    "Brief retail Oppose: quarterly transparency is vitally important.")
add(375, OPP, IND, R(["IA"],["IA"],["IA"]),
    "'the proposed decrease in financial reporting would put individual investors like myself at a disadvantage.'",
    "IA: individual investors disadvantaged; small companies he invests in would become less transparent.",
    "Brief retail Oppose: less reporting disadvantages individual investors in the small companies that would turn opaque.")
add(376, OPP, IND, R(["IP","CMP"],["IP","CMP"],["IP","CMP","ICc"]),
    "'Please do not place that handicap on investors in US stocks. Keep our public companies as transparent as possible.'",
    "IP: relied on quarterly data and management commentary for decisions; CMP: 'Semi-annual and annual data does not always show the seasonal trends or early indicators of trouble'; (Inc) ICc: dropped a French semiannual reporter for lack of transparency.",
    "Investor/club Oppose (50 years): quarterly data reveals seasonal trends and early warnings; the commenter abandoned a French semiannual holding over the resulting opacity.")
add(377, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Do not permit the passing of the rule which will allow for bi annual reporting.'", "NR: bare opposition.",
    "One-line Oppose: do not permit semiannual reporting.")
add(378, OPP, IND, R(["IP","FR"],["IP"],["IP","FR"]),
    "'The SEC should not take any action that increases corruption and leaves investors in the dark.'",
    "IP: leaves investors in the dark; (Inc) FR: increases corruption; 'Any corporation that doesn't want to report every three months shouldn't have the privilege of being listed'. PP-watch (corruption framing).",
    "Retail Oppose: the proposal increases corruption and blinds investors; a company unwilling to report quarterly should not be listed. FLAG: PP-watch.")
add(379, OPP, IND, R(["IP"],["IP"],["IP","IA"]),
    "'This is a terrible proposal. Every investment club in America counts on quarterly reports.'",
    "IP: investment clubs count on quarterly reports for accountability and analysis; (Inc) IA: individual investors.",
    "Investment-club Oppose: clubs across the country rely on quarterly reports to hold companies accountable.")
add(380, OPP, IND, R(["IP","IA"],["IP","IA"],["IP","IA"]),
    "'This would undermine the financial transparency we rely on when deciding whether to add to our current stock holdings.'",
    "IP: relies on quarterly SEC filings for accuracy and transparency in club decisions; IA: 'We small retired investors are relying on you'.",
    "Stock-club Oppose: a self-managed portfolio grown since 1998 depends on accurate, transparent quarterly filings; small retired investors rely on that oversight.")
add(381, OPP, IND, R(["IP"],["IP"],["IP","IA"]),
    "'I STRONGLY OBJECT to this proposal to go to semiannual reporting.'",
    "IP: researches companies and updates data quarterly for analysis; (Inc) IA: individual investor with retirement in individual stocks.",
    "Retail Oppose (45 years): a self-directed retirement portfolio relies on quarterly reports for company research and analysis.")
add(382, OPP, IND, R(["AU","IA"],["AU","IA"],["AU","IA","ICc"]),
    "'Please, don't take that info away from me.'",
    "AU: the 10-Q is independently reviewed and personally certified, unlike voluntary communications; IA: individuals own the majority of shares in the smaller companies most likely to opt out, losing the most information; (Inc) ICc: UK 2014 — over 90% kept filing quarterly; cites 2018-19 CFA/CII opposition.",
    "Retail Oppose: individuals own the smaller companies likeliest to drop quarterly reporting and would lose the most certified information; the UK experiment and the 2018-19 record both cut against the change.")
add(383, OPP, IND, R(["ICc","IP"],["ICc","IP"],["ICc","IP","FR"]),
    "'This half year reporting concept is absurd and harmful to individual investors.'",
    "ICc: countries that implemented semiannual reporting 'have had poor results to the point where some are thinking of restoring' quarterly; IP: the SEC should represent individual investors, not let corporations hide news; (Inc) FR: hiding upsetting news.",
    "Retail Oppose: international experience with semiannual reporting has been poor, and the SEC should protect individual investors rather than help corporations withhold news.")
add(384, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'I respectfully urge you to continue to require that companies file their 10-Q reports quarterly.'",
    "IP: too many variables change results more often than semiannually; individual investors rely on quarterly reports.",
    "Retail Oppose: financial results shift faster than semiannually, and individual investors rely on the quarterly cadence.")
add(385, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Please keep it quarterly so I can study the companies I invest in!'",
    "IP: quarterly reports let the investor study holdings.",
    "Brief retail Oppose: quarterly reporting is vital for studying the companies one invests in.")
add(386, OPP, IND, R(["IA","FR"],["IA","FR"],["IA","FR"]),
    "'PLEASE KEEP QUARTERLY REPORTING!'",
    "IA: the only reason to change is 'to keep regular investors in the dark and allow institutions and corporations'; FR: 'perpetrate all kinds of fraud'.",
    "Retail Oppose: the change exists only to keep regular investors in the dark and let institutions and corporations commit fraud.")
add(387, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Biannual reporting is not often enough for individual investors to be fully apprised of a company's financial health.'",
    "IP: semiannual reporting leaves individual investors insufficiently apprised of financial health.",
    "Retail Oppose: semiannual reporting is too infrequent for individual investors to track financial health and would limit investing.")
add(388, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Do NOT allow companies to go to semi annual reporting. Keep the quarterlies!'", "NR: bare opposition.",
    "One-line Oppose: keep quarterly reporting.")
add(389, OPP, IND, R(["IP"],["IP"],["IP","MF"]),
    "'please keep quarterly reporting... more data is better and confidence in the marketplace having correct information is a key component of why US markets have been successful.'",
    "IP: more data is better for investors; (Inc) MF: marketplace confidence in correct information underpins US market success.",
    "Retail Oppose (investor/physicist): more frequent, correct information sustains the market confidence behind US markets' success.")
add(390, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Please keep it the way it is, having companies file quarterly.'", "NR: bare request.",
    "Brief retail Oppose: keep quarterly filing.")
add(391, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'We need more visibility, not less. Please keep the quarterly three-month reporting period.'",
    "IP: visibility and transparency.",
    "Brief retail Oppose: investors need more visibility, not less.")
add(392, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'the big wigs need to be held accountable to the public for their stocks.'",
    "IP: public accountability of corporate leadership through quarterly monitoring.",
    "Retail Oppose: corporate leaders should be held publicly accountable, and quarterly monitoring is the way.")
add(393, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'I'd like to continue quarterly reporting.'", "NR: bare request.",
    "Brief retail Oppose: continue quarterly reporting.")
add(394, OPP, IND, R(["IA"],["IA"],["IA","ST","AL"]),
    "'It is not a good decision to let companies report every 6 months.'",
    "IA: small investors miss valuable information in a 6-month gap; (Inc) ST: skeptical that less reporting yields long-term focus; (Inc) AL: keep the cadence but lessen the volume of documentation.",
    "Retail Oppose: a six-month gap costs small investors valuable information; better to keep quarterly reporting and instead trim the bloated volume of required documentation.")
add(395, OPP, IND, R(["IA","IP"],["IA","IP"],["IA","IP","CB"]),
    "'I as an American Citizen and Investor am 100% against this proposal.'",
    "IA: 'company insiders a massive informational advantage over ordinary shareholders'; IP: undermines the core investor-protection mission; (Inc) CB: argues compliance relief is illusory since auditing/controls happen on a rolling basis.",
    "Retail Oppose: the change hands insiders an informational advantage, undermines investor protection, and offers only illusory compliance relief since the underlying work is continuous.")
add(396, OPP, IND, R(["IP"],["IP"],["IP","CB"]),
    "'Don't change the requirement!'",
    "IP: continuous monitoring of financial health requires quarterly reports; (Inc) CB: companies should use computer technology to reduce compliance cost (rebutting the burden rationale).",
    "Retail Oppose: quarterly reports are the minimum needed to monitor financial health, and technology should cut compliance cost rather than reporting frequency.")
add(397, OPP, IND, R(["FR"],["FR"],["FR"]),
    "'you want to give major corporations more of a chance to lie and cheat and cover up malfeasance?'",
    "FR: the change gives corporations more chance to 'lie and cheat and cover up malfeasance'. Political framing (corruption) is PP-watch.",
    "Vehement retail Oppose: the proposal hands corporations more room to lie, cheat, and cover up malfeasance. FLAG: PP-watch.")
add(398, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'twice a year reporting leaves the investor in the dark.'", "IP: semiannual leaves the investor in the dark.",
    "Brief retail Oppose: semiannual reporting leaves investors in the dark.")
add(399, OPP, IND, R(["IP"],["IP"],["IP","IA"]),
    "'Quarterly reports are important to shareholders, especially with respect to small companies.'",
    "IP: quarterly reports matter to shareholders; (Inc) IA: especially for small companies.",
    "Brief retail Oppose: quarterly reports matter to shareholders, especially in small companies.")
add(400, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'IF reported only 6 month there would be too long a period between reports.'",
    "IP: quarterly reports evaluate company and management performance with timely responsiveness.",
    "Stock-club Oppose: quarterly reports are vital for timely evaluation of company and management performance.")
add(401, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Keep the QUARTERLY REPORTING requirements. NO Semiannual reporting.'", "NR: bare opposition.",
    "One-line Oppose: keep quarterly reporting.")
add(402, OPP, IND, R(["IP","FR"],["IP"],["IP","FR"]),
    "'I rely upon quarterly reporting to make decisions regarding my retirement savings.'",
    "IP: relies on quarterly reporting for retirement decisions; (Inc) FR: 'concerned that changing this cadence... will open up the possibility of fraud or abuse'.",
    "Retail Oppose: a retiree relies on quarterly reporting and fears a longer cadence opens the door to fraud or abuse.")
add(403, OPP, IND, R(["IP"],["IP"],["IP","FR"]),
    "'Companies need to report four times a year to keep them honest.'",
    "IP: informed decisions and management accountability; (Inc) FR: quarterly reporting 'keeps them honest'.",
    "Retail Oppose: semiannual reporting destroys informed decision-making and management accountability; companies need to report quarterly to stay honest.")
add(404, OPP, IND, R(["IA","IP"],["IA","IP"],["IA","IP"]),
    "'I don't think semiannual reporting would be in the best interest of the smaller investors.'",
    "IA: asks smaller investors to 'blindly trust' between long gaps; IP: quarterly reports let them escape a decline with minimal risk.",
    "Retail Oppose: semiannual reporting forces smaller investors to trust blindly and bear declines that quarterly reports would have flagged in time.")
add(405, OPP, IND, R(["IA","IP"],["IA","IP"],["IA","IP","MF"]),
    "'I respectfully urge the Commission to retain the quarterly reporting framework.'",
    "IA: insiders and sophisticated participants have alternative channels (industry data, supply-chain signals, private communications) that widen information asymmetry; IP: monitoring performance trends and emerging risks; (Inc) MF: abrupt, outsized market reactions when disclosures finally occur.",
    "Reasoned retail Oppose: a six-month interval deepens opacity and widens the information advantage insiders already hold, raising the odds of abrupt market reactions.")
add(406, {"primary":"Duplicate","literalist":"Duplicate","skeptic":"Duplicate"}, IND,
    R([],[],[]), "Verbatim duplicate of #403 (same submission, base vs _0 variant).",
    "Held out as a duplicate of #403.",
    "Duplicate re-submission of #403 (Clifton Hosmer); identical text. Held out of the count.")
add(407, OPP, IND, R(["IP","IA"],["IP","IA"],["IP","IA"]),
    "'Six months is too long for investors to go without updated financial information.'",
    "IP: a fast-changing company's situation needs timely disclosure; IA: keeping everyday investors informed.",
    "Retail Oppose: six months is too long between updates for everyday investors, and reducing company paperwork should not cost transparency.")
add(408, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Keep quarterly reporting.'", "NR: bare request.", "One-line Oppose: keep quarterly reporting.")
add(409, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Any changes to elongate or alter quarterly reporting requirements undermine the very investor the SEC was built to protect.'",
    "IP: altering quarterly reporting undermines investor protection.",
    "Retail Oppose: altering quarterly reporting undermines the investors the SEC exists to protect.")
add(410, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Require quarterly reporting.'", "NR: bare request.", "One-line Oppose: require quarterly reporting.")
add(411, OPP, IND, R(["IA"],["IA"],["IA","ICc"]),
    "'If the big primes have access to early reporting then keep the quarterly report schedule.'",
    "IA: institutions ('big primes') have early access, so retail needs the quarterly schedule; (Inc) ICc: 'semi-annual is not working well where it has been tried'.",
    "Retail Oppose: while institutions get early access, retail investors need the quarterly schedule, and semiannual reporting has not worked where tried.")
add(412, OPP, IND, R(["IA","ICc"],["IA","ICc"],["IA","ICc","MF","CB"]),
    "'I urge the SEC commission to reject this proposal and maintain the current quarterly reporting standard.'",
    "IA: institutions buy alternative data to estimate earnings in real time while retail relies on quarterly reports; ICc: 'Similar shifts in Europe showed that cutting quarterly reports does not actually improve long-term corporate investment or save meaningful costs'; (Inc) MF/CB: a six-month information gap with negligible savings.",
    "Reasoned retail Oppose: Europe's experience shows cutting quarterly reports neither aids long-term investment nor saves much, while it widens Wall Street's data advantage over retail.")
add(413, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Please keep existing reporting schedule.'", "NR: bare request.",
    "One-line Oppose: keep the existing reporting schedule.")
add(414, OPP, IND, R(["IP"],["IP"],["IP","IA"]),
    "'The current requirement protects the retail investor.'",
    "IP: quarterly public filings protect the retail investor; (Inc) IA: retail.",
    "Brief retail Oppose: quarterly public filings protect the retail investor.")
add(415, OPP, IND, R(["IA","MF"],["IA","MF"],["IA","MF","IP"]),
    "'I am writing to express my strong opposition to the SEC's proposal to make quarterly reporting optional.'",
    "IA: a six-month 'information vacuum' favors insiders with real-time visibility, leaving public investors on stale information; MF: increased cost of capital, heightened volatility; the companies likeliest to opt out are troubled issuers whose investors most need updates; (Inc) IP: investor confidence.",
    "Reasoned retail Oppose: an optional six-month gap creates an information vacuum favoring insiders, raises cost of capital and volatility, and lets the riskiest issuers disclose least.")
add(416, OPP, IND, R(["IA","IP"],["IA","IP"],["IA","IP"]),
    "'I oppose any effort to reduce public company reporting from quarterly to twice a year.'",
    "IA: executives and institutions already have more access and resources; reducing reporting widens that gap; IP: accountability, transparency, and tracking performance with current information.",
    "Retail Oppose: public companies benefit from public capital and owe regular disclosure; cutting reporting widens the access gap ordinary investors already face.")
add(417, OPP, IND, R(["IA","MF","IP"],["IA","MF","IP"],["IA","MF","IP"]),
    "'I urge the Commission to maintain the mandatory quarterly reporting schedule.'",
    "IA: longer gaps widen the knowledge gap between insiders and retail; MF: concentrating price-moving information into fewer events increases volatility; IP: the investor-protection mandate outweighs filing-cost relief.",
    "Reasoned retail Oppose: halving public reporting widens the insider/retail gap and concentrates price-moving news into fewer, more volatile events; investor protection outweighs the cost relief.")
add(418, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Keep it quarterly!'", "NR: bare request.", "One-line Oppose: keep it quarterly.")
add(419, OPP, IND, R(["IP"],["IP"],["IP","FR"]),
    "'I feel deeply uncomfortable with this proposal as a retail investor.'",
    "IP: relies on quarterly earnings being required and uniform for decisions; (Inc) FR: a reduction in data 'increases the likelihood of abuse'.",
    "Retail Oppose: a retiree relies on universal quarterly earnings; less data raises abuse risk and would push the commenter out of the market.")
add(420, OPP, IND, R(["IP","FR"],["IP","FR"],["IP","FR"]),
    "'This modified ruling serves to obscure information, allow for more insider trading and erode trust.'",
    "IP: investors need a transparent window into companies; FR: the change obscures information and allows more insider trading.",
    "Retail Oppose: transparency gives normal investors a window into companies; the change obscures information, invites insider trading, and erodes trust. Entities unwilling to be accountable should stay private.")
add(421, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Keep quarterly reporting! transparency is key to accountability and healthy markets.'",
    "IP: transparency drives accountability and healthy markets.",
    "Brief retail Oppose: transparency is key to accountability and healthy markets.")
add(422, OPP, IND, R(["IA"],["IA"],["IA"]),
    "'As an individual investor, I will be at a severe disadvantage to institutional investors with access to more resources.'",
    "IA: individual investors at a severe disadvantage to better-resourced institutions.",
    "Brief retail Oppose: a longer cadence severely disadvantages individual investors against better-resourced institutions.")
add(423, {"primary":"Duplicate","literalist":"Duplicate","skeptic":"Duplicate"}, IND,
    R([],[],[]), "Verbatim duplicate of #421 (same submission, base vs _0 variant).",
    "Held out as a duplicate of #421.",
    "Duplicate re-submission of #421 (Jeremiah Scepaniak); identical text. Held out of the count.")
add(424, OPC, IPROF, R(["AL","IP"],["AL"],["AL","IP","CMP"]),
    "'I do not believe that reducing the frequency of transparency is the appropriate solution.'",
    "AL: recommends a hybrid — quarterly MD&A and key performance indicators including earnings, with more comprehensive disclosures semiannually; IP: preserving timely insight for investors. The IPO/accredited-investor commentary is an off-topic tangent (uncoded). Skeptic reads the hybrid as Conditional.",
    "Attorney/asset-management Oppose with a hybrid proposal: keep quarterly MD&A and earnings KPIs while moving fuller disclosures to semiannual, preserving timely insight while easing burden.",
    role="Attorney, insurance / asset-management firm")
add(425, OPP, IND, R(["MF","IA"],["MF","IA"],["MF","IA"]),
    "'This rule change will make US capital markets nearly 50% less efficient.'",
    "MF: market efficiency derives from public information; less information raises the risk premium, lowers valuations, and reduces productive investment; IA: those with management access (bankers, institutions) benefit even more from unequal access despite Reg FD.",
    "Market-efficiency Oppose: halving public information widens insiders' access advantage, raises the risk premium, and lowers valuations and productive investment.")
add(426, OPP, IND, R(["IA"],["NR"],["IA"]),
    "'Rich keep getting richer. What about a government for the common people and not the 1%.'",
    "IA: frames the change as favoring the wealthy over private investors. Largely political (PP-watch); literalist reads it as NR.",
    "Political retail Oppose: the change favors the rich over ordinary private investors. FLAG: PP-watch.")
add(427, OPP, IND, R(["IP","FR"],["IP","FR"],["IP","FR"]),
    "'Part of keeping a company accountable is frequency.'",
    "IP: frequency is part of accountability; FR: less frequent reporting increases risk and susceptibility to fraud.",
    "Retail Oppose: reporting frequency is part of accountability; reducing it increases susceptibility to fraud.")
add(428, OPP, IND, R(["IA","CMP","IP"],["IA","CMP","IP"],["IA","CMP","IP","AL","ST","MF"]),
    "'I respectfully urge the Commission to retain mandatory quarterly reporting on Form 10-Q.'",
    "CMP: cites the release's own comparability concern about comparing quarterly vs semiannual filers; IA: institutions/insiders retain access while retail depends on filings; IP: timely, standardized, comparable information and liability discipline; (Inc) AL: targeted relief for smaller issuers instead of a broad option; (Inc) ST: distinguishes quarterly reporting from quarterly earnings guidance; (Inc) MF: standardized vs fragmented messaging.",
    "Comprehensive Oppose: semiannual reporting erodes comparability and standardization and widens the retail information gap; if relief is needed, target smaller issuers rather than weakening the quarterly cadence for all.")
add(429, OPP, IND, R(["FR"],["FR"],["FR"]),
    "'Twice a year instead of quarterly will make scam companies have plenty more time to forge.'",
    "FR: longer gaps give scam and fake companies more time to forge and avoid delisting.",
    "Retail Oppose: a longer cadence gives scam and fraudulent companies more time to forge results and dilute American investors.")
add(430, OPC, CPA, R(["FR","IA"],["FR","IA"],["FR","IA","AL","AU"]),
    "'This is giving the fox the henhouse.'",
    "FR: semiannual reporting makes it easier to manipulate and hide issues and aids insider manipulation; IA: less accountability favors executives and insiders over investors; (Inc) AL: scale reporting up for larger companies and require monthly top-line revenue; (Inc) AU: as a former CPA, notes modern systems can soft-close books anytime, so the burden claim is overstated. Skeptic reads the scaling fallback as Conditional.",
    "Retired-CPA Oppose: semiannual reporting eases manipulation and insider gaming; modern systems make near-real-time reporting feasible, so larger companies should report more, not less.",
    role="Retired (two national CPA firms)")
add(431, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Please keep the reporting requirements to be quarterly to keep the existing transparency into company health.'",
    "IP: transparency into company health for informed decisions.",
    "Brief retail Oppose: quarterly reporting preserves transparency into company health.")
add(432, OPP, IND, R(["FR"],["FR"],["FR","MF"]),
    "'Public disclosure prevents fraud from becoming systemic.'",
    "FR: cites First Brands and its private creditors as a case where lack of transparency let fraud reach industry-threatening scale; (Inc) MF: systemic economic vulnerability.",
    "Retail Oppose: public disclosure keeps fraud from becoming systemic, as the First Brands collapse showed; reducing reporting creates an economy-wide vulnerability.")
add(433, OPP, IND, R(["IP"],["IP"],["IP","IA"]),
    "'A lot can happen in 6 months, and at that point by the time i find out a stock is starting to flounder it will likely be too late.'",
    "IP: relies on quarterly calls to decide hold/sell; a 6-month gap means learning of trouble too late; (Inc) IA: private investor.",
    "Retail Oppose: quarterly reporting lets a private investor catch a floundering stock before it is too late.")
add(434, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'The quarterly SEC filings currently required are critical to my success.'",
    "IP: quarterly financial results are the key factor in buy/trim/eliminate decisions; a 6-month wait adds risk.",
    "Long-term investor Oppose (since 1997): quarterly results are the critical input to hold/trim/sell decisions, and a six-month wait adds unnecessary risk.")
add(435, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Your gonna lose half the investment in stocks.'",
    "NR: opposes the change but offers no developed taxonomy argument (predicts a flight to crypto/commodities).",
    "Retail Oppose: predicts the change would drive investors out of stocks toward crypto and commodities.")
add(436, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'The public needs as much of a window as possible into corporate finance. More transparency!'",
    "IP: maximal transparency/window into corporate finance.",
    "Brief retail Oppose: the public needs the widest possible window into corporate finance.")
add(437, OPP, IND, R(["IA","IP"],["IA","IP"],["IA","IP","FR"]),
    "'I strongly oppose reducing public company reporting requirements from quarterly to semi-annual.'",
    "IA: institutions use analyst networks and management access while retail depends on public filings, widening the advantage; IP: transparency, accountability, and equal access; (Inc) FR: problems (deteriorating finances, governance failures, aggressive accounting) remaining hidden longer.",
    "Reasoned retail Oppose: halving disclosure widens the institutional information advantage and lets governance and accounting problems stay hidden longer; accountability should rise with public ownership.")
add(438, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Semiannual reporting does not provide enough transparency.'", "IP: insufficient transparency.",
    "Brief retail Oppose: semiannual reporting does not provide enough transparency.")
add(439, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Do not change the reporting time periods.'", "NR: bare opposition.",
    "One-line Oppose: do not change the reporting periods.")
add(440, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'You would render me blind in my own future.'",
    "IP: quarterly results are vital analysis for club and personal portfolios; removing them blinds the investor.",
    "Investor/club Oppose: quarterly results are vital analysis; removing them blinds investors to their own financial future.")
add(441, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'I depend on quarterly company reports for timely data to assess a company's financial health.'",
    "IP: standardized quarterly reporting tracks earnings, debt, and trends and surfaces red flags in time to sell.",
    "Retail Oppose: standardized quarterly reports give the timely data needed to assess financial health and spot red flags before it is too late.")
add(442, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'TRANSPARENCY IS THE STRENGTH OF THE AMERICAN MARKET.'",
    "IP: transparency and corporate accountability to the public.",
    "Brief retail Oppose: hold companies accountable; transparency is the strength of the American market.")
add(443, OPP, IND, R(["IP"],["IP"],["IP","AL"]),
    "'Please keep the reporting quarterly, I rely on this information.'",
    "IP: relies on the information; (Inc) AL: suggests every-other-month reporting rather than less frequent.",
    "Retail Oppose: keep quarterly reporting; in a faster world the smarter move is more frequent, not semiannual.")
add(444, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Businesses must continue to provide quarterly reports to ensure investors can assess... their investments.'",
    "IP: quarterly reports let investors assess operations and financial status.",
    "Brief retail Oppose: quarterly reports let investors assess the operations and financial status of their investments.")
add(445, OPC, IND, R(["IP","AL"],["IP","AL"],["IP","AL"]),
    "'I am opposed to this rule change. However, eliminating or replacing full quarterly reporting to just an update to the yearly revenue and earnings would be acceptable.'",
    "IP: needs timely updates to revenue and earnings; AL: would accept a lighter quarterly update (revenue/earnings, or within 30 days of any internal update) instead of full 10-Qs. Skeptic reads the acceptable-alternative as Conditional.",
    "Retail Oppose with an alternative: opposes the rule but would accept a lighter quarterly revenue/earnings update in place of the full 10-Q.")
add(446, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Please keep quarterly reporting.'", "NR: bare request.", "One-line Oppose: keep quarterly reporting.")
add(447, OPP, IND, R(["IP"],["IP"],["IP","AL"]),
    "'Please retain the current required reporting periodicity at QUARTERLY.'",
    "IP: quarterly snapshots reveal trends and reduce investor risk; semiannual obscures significant trends with stale data; (Inc) AL: notes monthly/bimonthly could help but adds burden, while quarterly adds no new burden.",
    "Retail Oppose: quarterly snapshots reveal trends and limit investor risk; semiannual reporting buries significant trends in stale data while saving no real burden.")
add(448, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'Six months is too long to go with no information on how the company is doing.'",
    "IP: six months with no information is too long.",
    "One-line Oppose: six months without information on a company is too long.")
add(449, OPP, IND, R(["US","IP"],["US","IP"],["US","IP","MF"]),
    "'Moving away from a system of transparency is not in the best interest of individuals nor institutions.'",
    "US: 'US equities demand a premium because of our enhanced regulatory regime'; IP: quarterly reports provide clarity for retail and professional investors; (Inc) MF: the premium reflects market quality.",
    "Retail Oppose: US equities command a premium because of the enhanced regulatory regime; abandoning quarterly transparency serves neither individuals nor institutions.")
add(450, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'I am opposed to the semiannual reporting. Don't change the current rules!'", "NR: bare opposition.",
    "One-line Oppose: do not change the current rules.")
add(451, OPP, IND, R(["FR"],["FR"],["FR"]),
    "'Reducing the reporting requirements is reckless at best, and flat out corrupt at worst.'",
    "FR: those in financial oversight and white-collar-crime investigation know the change invites financial malfeasance at scale. Political (corruption) framing is PP-watch.",
    "Retail Oppose: reducing reporting paves the way for financial malfeasance at scale. FLAG: PP-watch.")
add(452, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'quarterly statement and commentaries provide better insight of how a company is doing.'",
    "IP: quarterly statements give better insight; with AI capabilities growing monthly, semiannual is too slow.",
    "Brief retail Oppose: quarterly statements give better insight, and in an AI era semiannual reporting is too slow.")
add(453, OPP, STU, R(["IP","AU"],["IP","AU"],["IP","AU","CB"]),
    "'We have studied governance principles this semester and submit the following considerations.'",
    "IP: mandatory reporting engenders trust (board-oversight assurance, negative assurance of no material change avoids an information vacuum); AU: verification processes inspire confidence in interim reports; (Inc) CB: cost savings may be overstated since boards/auditors must engage regularly regardless (Caremark duties).",
    "Corporate-governance class Oppose: mandatory interim reporting builds the trust behind capital-formation efficiency, and the cost savings are likely overstated because boards and auditors must engage regularly anyway.",
    role="Corporate Governance Class")
add(454, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Every single big corporation or company should have to file every month.'",
    "NR: wants more-frequent (monthly) reporting rather than less; no developed taxonomy argument.",
    "Retail Oppose: companies and officials should file monthly, not less often.")
add(455, OPP, IND, R(["FR","IA"],["FR","IA"],["FR","IA"]),
    "'Allowing companies 6 months between disclosures is wrong and will only increase insider trading.'",
    "FR: a six-month gap increases insider trading; IA: cutting out individual investors and raising risk for the 'have nots'.",
    "Retail Oppose: a six-month disclosure gap increases insider trading and raises the risk borne by individual investors.")
add(456, OPP, IND, R(["IA","IP"],["IA","IP"],["IA","IP","FR"]),
    "'I am submitting this comment to declare my absolute opposition to the S7-2026-15 Semiannual Reporting proposal.'",
    "IA: a six-month 'information vacuum' leaves retail and watchdogs in the dark while insiders exploit their knowledge; IP: the SEC's mandate is to protect everyday investors and ensure fair markets; (Inc) FR: insiders trade on non-public knowledge and hide mismanagement.",
    "Vehement retail Oppose: the change creates a six-month information vacuum that lets insiders exploit non-public knowledge while the public is left in the dark.")
add(457, OPP, IND, R(["IP"],["IP"],["IP"]),
    "'The public should have access to timely information. Do not allow semiannual reporting.'",
    "IP: timely public access to information.",
    "One-line Oppose: the public should have timely information.")
add(458, OPP, IND, R(["IP"],["IP"],["IP","FR"]),
    "'Investors deserve more information not less. This change opens the door for more corruption.'",
    "IP: investors deserve more information, not less; (Inc) FR: opens the door for more corruption. Political ('drain the swamp') framing is PP-watch.",
    "Retail Oppose: investors deserve more information, not less; increase reporting frequency rather than open the door to corruption. FLAG: PP-watch.")
add(459, OPP, IND, R(["MF","FR"],["MF","FR"],["MF","FR"]),
    "'Timely financial reporting is key to a healthy stock market.'",
    "MF: timely reporting helps investors shape the economy toward productive outcomes; FR: reducing reporting makes insider manipulation and outright deception easier and more likely.",
    "Retail Oppose: timely reporting underpins a healthy, productive market; reducing it makes insider manipulation and deception likelier.")
add(460, OPP, IND, R(["NR"],["NR"],["NR"]),
    "'Do the job with integrity. Follow the rules. Stop showing favoritism.'",
    "NR: an integrity/fairness appeal with no substantive disclosure argument. Political (favoritism) framing is PP-watch.",
    "Retail Oppose: an appeal to follow the existing rules with integrity and stop showing favoritism. FLAG: PP-watch.")
add(461, OPP, IND, R(["IP"],["IP"],["IP","IA"]),
    "'When critical decisions need to be made, more information is always better than less.'",
    "IP: investors, like patients on continuous vital-sign monitoring, need frequent reporting to make timely decisions; (Inc) IA: retired physician relying on his own monitoring.",
    "Retired-physician Oppose: investors, like a monitored surgical patient or a pilot watching the gauges, need frequent reporting; the SEC must not abrogate its duty to protect them.",
    role="Retired physician / individual investor")
add(462, {"primary":"Conditional","literalist":"Conditional","skeptic":"Conditional"}, IND,
    R(["AU","FR","IP","IA","CMP","AL"],["AU","FR","IP","AL"],["AU","FR","IP","IA","CMP","AL","MF"]),
    "'semiannual reporting should be restricted to mostly mature companies that have consistently avoided [material revisions / misstatements / ICFR failures]'; 'narrowing the scope of who will be eligible for semiannual reporting... will increase capital markets efficiency and decrease the administrative burden'; 'I would like to see conditions on the proposed semi-annual reporting rule'.",
    "AL: the operative position is a carve-out — bar companies with recent material revisions/misstatements/ICFR period-end failures (and lingering significant deficiencies) from semiannual reporting for at least three years, while permitting it for mature, clean issuers; AU: ICFR / material-weakness detection (PCAOB AS 2201; the early-warning intent defeated in practice); FR: heightened risk that material misstatements due to error or fraud go undetected (RFC 26); IP: investor-protection concerns (RFC 18); IA: significant deficiencies 'disclosed exclusively to institutional investors'; CMP: he names decreased comparability/consistency as a cost; (Inc) MF. Cites EGC material-weakness rates and SOX-404 adverse-ICFR data.",
    "Substantive Conditional (canonical Andrew Parker; this amended PDF replaces the original #99, which Tzachi held out as a duplicate). Same position as #99, expanded: he supports OPTIONAL semiannual reporting but only for mature, clean issuers, and would bar companies with recent ICFR/material-weakness conditions for three years and add disclosure conditions. Engages RFC 18 and RFC 26 with ICFR / SOX-404 detail. Tzachi's 2026-05-31 dedup call kept #462 over #99; the 3-rater stance stays Conditional (the amended letter is longer, not a different position).",
    role="Individual",
    rfc={"engaged":[18,26],"cited_explicitly":True,"note":"Andrew Parker amended PDF comment; replaces #99. Names and answers Request for Comment 18 (investor-protection concerns) and 26 (ICFR / timely detection of material misstatements and control deficiencies under semiannual reporting)."})


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
    if "rfc" in c: rec["rfc_questions"]=c["rfc"]

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
    missing=[n for n in range(345,463) if n not in C]
    if missing: print("[warn] no classification for:",missing)
    for n,c in C.items():
        if n not in by: print("[warn] record missing",n); continue
        update_record(by[n],c)
    RECORDS.write_text(json.dumps(recs,indent=2,ensure_ascii=False)+"\n")
    print(f"[ok] updated renumbered_records.json ({len(recs)} records); classified {len(C)} (345-462)")
    patched=0
    for n in C:
        for p in LETTERS.glob(f"{n}_*"):
            if p.suffix==".md": patch_letter_header(p,by[n]); patched+=1
    print(f"[ok] patched {patched} letter headers")

if __name__=="__main__": main()
