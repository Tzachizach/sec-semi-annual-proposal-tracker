#!/usr/bin/env python3
"""Integration for letters #534-#622 (2026-06-03 afternoon full update,
Action run #26910149098).

Background: morning page-0 check showed 0 net-new (CloudFront pager
stale, returning page-0 content for every page index). Tzachi pasted
pages 1-5 from his browser in the afternoon; dedup against the 529
known doc-ids identified 89 net-new (76 May 27-30 batch, 13 Jun 1-3
batch). All queued to new_urls.txt, Action #26910149098 drained all
89 as placeholders #534-#622 in 1m 35s. Action then re-disabled.

Foley & Lardner LLP letter (Lehot/Daugherty, doc 2413426) is filed
under S7-2026-18 but cross-listed on the S7-2026-15 docket; Tzachi
ID'd the PDF and dropped it in _meta/pdf_letters/. The PDF was also
fetched by the drain (#618 placeholder). Cross-filer, classified as
substantive Support letter for S7-2026-15.

Outcome: 87 Oppose + 2 Support in corpus (Foley + James Jetlife).

Per-letter highlights:

- #547 Vicki Kroc + #557 Barbara Garrison: same NAIC "Abundance
  Strategist Investment Club" template, longer variant of the
  AU-template campaign. Different commenters, kept both. AU-template
  carriers (new).
- #551 Heather Scheer: standard AU template (10-Q reviewed by
  independent auditors / CEO+CFO sign / voluntary corporate
  communications carry none of that) + 2018-2019 SEC history + UK
  90% citation + Commission's-own-data smaller-companies frame. Full
  campaign template, substantive (251w).
- #581 Mike Pechacek + #585 Kenneth A. Adams: identical text
  ("Investment Club for 31 years" + AU template language). Campaign
  template, kept both as separate commenters per the standing rule.
- #592 James Jetlife "To much over site." — read as "Too much
  oversight" → Support of the proposal (rare retail Support).
  Unanimous across all three raters.
- #593 Joseph Wagner: substantive Oppose with an alternative-cadence
  proposal (semiannual only for OTC/smaller companies; not for
  trillion-dollar issuers). Skeptic flips to Conditional per the
  pattern in #486 Anderson / #492 Calime. Stance-note set.
- #596 Elizabeth Bolint: former in-house counsel at major
  corporations. Issuer-former across all three raters.
- #597 Scott Miller: equity compensation expert. Industry
  practitioner-technologist.
- #578 Fardin Chowdhury: "Banker at JPM ECM". Investment professional
  unanimous.
- #618 Foley & Lardner LLP (Lehot/Daugherty): Support, cross-filed
  from S7-2026-18 docket; engages S7-2026-15 directly with the OP
  rationale ("decision whether to report quarterly or semiannually
  is one that boards, audit committees, and investors are best
  positioned to make"). Also acknowledges MF (cost of capital) but
  frames as "business judgment, not a regulatory one." Industry
  practitioner-technologist (corporate-law capital-markets
  practitioners).
- #612 William Michael Cunningham: Creative Investment Research,
  published author. Investment professional. Substance is brief
  ("Will lead to another financial crisis") but the letterhead is
  unambiguous.
- #621 Ron Salsbury: VP Quality at TYRX Inc. (a Medtronic
  subsidiary). Writes as individual investor but signs with the
  corporate title. Mixed entity: Primary + Self-described
  Individual, Letterhead Issuer-current. Majority Individual.

PP-watch additions (3): #601 Cindy L Meier ("SEC wants to protect
itself and other corrupt entities"), #607 Anonymous ("at least under
a republican administration"), #616 Dalvyn ("The regime is already
doing what they can to weaken the US economy"). All three attribute
the rule to political pressure / regulatory capture per the narrow
definition. Carrier tally goes from 14 to 17.

PP-watch frames that do NOT qualify (carried per the narrow rule):
#559 Armando Nieves + #589 Eleanor Bomar ("rule benefits insiders at
the expense of ordinary investors" — same as #511, the ordinary
IP/IA framing the doc explicitly excludes), #620 Brink Williams ("no
idea why the SEC would want less transparency unless they do not
prioritize the American investor's best interests" — generic
motive-questioning, no political attribution).

AU-template carriers (new, 4): #547, #551, #557, #581, #585. Counting
the long NAIC variant separately from the standard short variant.
The standard AU template ("10-Q reviewed by independent auditors /
CEO+CFO sign / voluntary corporate communications carry none of
that") is in #551, #581, #585. The longer NAIC variant
("Abundance Strategist Investment Club, Member NAIC") is in #547,
#557. Running tally moves from 10 to 15.

Date fixes (44): URL-list drain defaulted records without
body-internal date to URL_LIST_DEFAULT_DATE = 2026-05-27. Re-set per
docket truth (which itself was the docket paste). Dave Potter docket
date "June 30" is a SEC typo; doc-id 2406086 sits in the May 30
cluster (2405966-2406226), corrected to 2026-05-30 per docket-truth
+ doc-id-neighborhood inference.

Foley entity-bucket note: Foley & Lardner is a corporate-law firm
advising on capital formation. Best fit in the current 8-bucket
taxonomy is Industry practitioner-technologist (closest to
capital-markets practitioner). The pending 2018 rubric fold-in would
add a Trade-association / Advocacy bucket and potentially a Legal
practitioner bucket; once shipped, Foley should be re-bucketed.

RFC scan: none of the 89 engages a numbered RFC. Engagement set
stays at 3 (#14, #99, #236).

Agreement-field convention (carried): emit lowercase 'unanimous' /
'majority' / 'split'.
"""
import json, re
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RECORDS = PROJECT / "_meta" / "renumbered_records.json"
LETTERS = PROJECT / "Letters"

IND = {"primary": "Individual", "selfdescribed": "Individual", "letterhead": "Individual"}
INVPRO = {"primary": "Investment professional", "selfdescribed": "Investment professional", "letterhead": "Investment professional"}
INDPRACT = {"primary": "Industry practitioner-technologist", "selfdescribed": "Industry practitioner-technologist", "letterhead": "Industry practitioner-technologist"}
ISFORMER = {"primary": "Issuer-former", "selfdescribed": "Issuer-former", "letterhead": "Issuer-former"}
OPP = {"primary": "Oppose", "literalist": "Oppose", "skeptic": "Oppose"}
OPP_COND = {"primary": "Oppose", "literalist": "Oppose", "skeptic": "Conditional"}
SUP = {"primary": "Support", "literalist": "Support", "skeptic": "Support"}

# Date corrections: docket-truth dates (the paste Tzachi ran on pages
# 1-5), plus the Dave Potter SEC-date-typo fix (Jun 30 -> May 30) and
# the Jun 1-3 dates that the URL-list defaulted to 05-27.
DATE_FIX = {
    534: "2026-05-28", 535: "2026-05-28", 537: "2026-05-28",
    538: "2026-05-28", 539: "2026-05-28", 540: "2026-05-28",
    543: "2026-05-28", 545: "2026-05-28", 548: "2026-05-28",
    549: "2026-05-28", 550: "2026-05-28", 551: "2026-05-28",
    552: "2026-05-28", 555: "2026-05-28", 556: "2026-05-28",
    571: "2026-05-28",
    579: "2026-05-29", 582: "2026-05-29", 584: "2026-05-29",
    586: "2026-05-29", 588: "2026-05-29", 590: "2026-05-29",
    591: "2026-05-29", 592: "2026-05-29", 593: "2026-05-29",
    594: "2026-05-29", 595: "2026-05-29", 596: "2026-05-29",
    597: "2026-05-28", 598: "2026-05-29", 599: "2026-05-29",
    600: "2026-05-29", 601: "2026-05-29",
    602: "2026-05-30", 604: "2026-05-30", 605: "2026-05-30",
    610: "2026-05-30",
    615: "2026-06-01", 616: "2026-06-01", 617: "2026-06-01",
    618: "2026-06-02", 619: "2026-06-02", 620: "2026-06-02",
    621: "2026-06-03", 622: "2026-06-03",
}

# Name corrections: the drain inferred name from <body parse>, but
# the Foley PDF stub has commenter="Unknown" (drain default for PDFs).
NAME_FIX = {
    618: ("Louis Lehot & Patrick Daugherty, Foley & Lardner LLP",
          "Industry practitioner-technologist"),
}

# Letterhead overrides for Foley (the IND constant is wrong)
ENT_OVERRIDE = {
    621: {"primary": "Individual", "selfdescribed": "Individual",
          "letterhead": "Issuer-current"},
}

C = {}

# ===== May 28 batch =====

C[534] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "AU"], "literalist": ["IA", "AU"], "inclusive": ["IA", "IP", "AU"]},
  "stance_evidence": "'My wife and I feel strongly that the discontinuation of quarterly reports will be a disservice... Please continue the reports requirement as it now exists!'",
  "rationale_evidence": "IA: 'see what a company is doing on an ongoing basis'. IP: small individual investor framing. AU: 'Value Line is an invaluable resource that depends heavily on the quarterly report'. Author teaches free 35-yr investing class.",
  "summary": "Substantive retail Oppose from a 35-year investing-class teacher: discontinuation is a disservice; Value Line and other resources depend heavily on the quarterly report."}

C[535] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Keep reporting to quartely.'",
  "rationale_evidence": "Four-word preservation request, no rationale supplied.",
  "summary": "Four-word retail Oppose: keep reporting to quarterly."}

C[536] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'I urge you to reject S7-2026-15. I depend on quarterly filings to help me make decisions. Filing twice a year gives corporate investors an unfair atvantage.'",
  "rationale_evidence": "IA: 'depend on quarterly filings to help me make decisions'. IP: 'twice a year gives corporate investors an unfair atvantage'.",
  "summary": "Brief retail Oppose: rejects S7-2026-15; quarterly filings necessary for decisions; twice-a-year gives corporate investors unfair advantage."}

C[537] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP"], "literalist": ["AU", "IA"], "inclusive": ["AU", "IA", "IP"]},
  "stance_evidence": "'As a small investor, I use these verified reports and signed by the CFOs and CEOs to make informed decisions when buying and/or selling stocks.'",
  "rationale_evidence": "AU: 'verified reports and signed by the CFOs and CEOs'. IA: timely-information frame. IP: 'small investor' framing.",
  "summary": "Retail Oppose: small investor uses verified reports signed by CFOs and CEOs to make informed buying/selling decisions."}

C[538] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "RI"], "literalist": ["IA"], "inclusive": ["IA", "RI", "IP"]},
  "stance_evidence": "'Quarterly reporting requirements are critical for investor knowledge when making evaluations of a public equity.'",
  "rationale_evidence": "IA: 'reduce the number of records available for analysis by 50%'. RI: 'feature development requires robust longitudinal time series data' — analyst-workflow reliance.",
  "summary": "Retail Oppose with a data-analyst frame: feature development requires longitudinal time series; cutting in half reduces records available for analysis; governance and data structures should be more robust, not less."}

C[539] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'Please keep quarterly reporting.'",
  "rationale_evidence": "IA: 'up to date financial information on the companies I am looking at'. IP: 82-yr-old investment-club treasurer framing.",
  "summary": "Retail Oppose from an 82-year-old investment-club treasurer (3 generations of members): wants up-to-date financial information; keep quarterly reporting."}

C[540] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "AU"], "literalist": ["IA", "AU"], "inclusive": ["IA", "AU"]},
  "stance_evidence": "'I vehemently oppose your proposal to allow public companies to choose not to file quarterly reports. These reports are vital to investors wishing to make informed decisions and for holding companies appropriately accountable to their shareholders.'",
  "rationale_evidence": "IA: 'vital to investors wishing to make informed decisions'. AU: 'holding companies appropriately accountable to their shareholders'.",
  "summary": "Retail Oppose: vehemently opposes; reports vital for informed decisions and holding companies accountable to shareholders."}

C[541] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'I urge you to reject S7-2026-15.'",
  "rationale_evidence": "Bare rejection request, no rationale supplied.",
  "summary": "Brief retail Oppose: urges the SEC to reject S7-2026-15."}

C[542] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Active quarterly reporting is good.'",
  "rationale_evidence": "Five-word preservation statement, no rationale supplied.",
  "summary": "Five-word retail Oppose: active quarterly reporting is good."}

C[543] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "FR"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP", "FR"]},
  "stance_evidence": "'Don't take away the individual investor's data that is used to make timely decisions.'",
  "rationale_evidence": "IA: uses quarterly reports to spot growth changes; 'hiding/concealing actionable data'. IP: 'professionals will have more timely information than me because they have access/contact with companies that I don't'. FR: concealment frame.",
  "summary": "Substantive retail Oppose: uses quarterly reports to spot growth/sales changes and time decisions; professionals get earlier information via direct company access; deleting quarterly hides actionable data from individual investors."}

C[544] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'This proposal would harm retail investors.'",
  "rationale_evidence": "IP: bare retail-investor-harm framing (template line).",
  "summary": "Two-line retail Oppose: this proposal would harm retail investors."}

C[545] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA"], "literalist": ["AU"], "inclusive": ["AU", "IA"]},
  "stance_evidence": "'I use certified quarterly information from 10-Q filings in my investing process.'",
  "rationale_evidence": "AU: 'certified quarterly information from 10-Q filings'. IA: relies on quarterly cadence.",
  "summary": "One-line retail Oppose: uses certified quarterly information from 10-Q filings in investing process."}

C[546] = {"stance": OPP, "entity": INDPRACT,
  "rationales": {"primary": ["RI", "IA", "IP"], "literalist": ["IA"], "inclusive": ["RI", "IA", "IP"]},
  "stance_evidence": "'Quarterly reporting is the lifeblood of small and medium scale investor intelligence services as well as a lifeline for individual investors. Keep reports quarterly!'",
  "rationale_evidence": "RI: 'lifeblood of small and medium scale investor intelligence services' — workflow reliance. IA: timely information. IP: individual-investor framing. Author signs as TopDown.AI (investor intelligence service).",
  "summary": "Industry-practitioner Oppose from TopDown.AI: quarterly reporting is the lifeblood of small/medium investor intelligence services and a lifeline for individual investors."}

C[547] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP", "MF"], "literalist": ["AU", "IA"], "inclusive": ["AU", "IA", "IP", "MF"]},
  "stance_evidence": "'The proposal to reduce the number of certified financial filing each year by half is NOT what we want as investors. Having these filings reviewed by independent auditors and then signed by the CEO and CFO of our holdings is critical...'",
  "rationale_evidence": "AU: NAIC-template language - 'reviewed by independent auditors and then signed by the CEO and CFO... we place our trust in these filings'. IA: 'Waiting 6 months for every financial filing would make our investment decisions extremely difficult'. IP: NAIC investment-club individual-investor framing. MF: market-timing for purchases and sales.",
  "summary": "Retail Oppose from an Abundance Strategist Investment Club member (NAIC) carrying the longer NAIC AU-template ('reviewed by independent auditors and then signed by the CEO and CFO; we place our trust in these filings'); club meets monthly to review stocks; waiting 6 months would make decisions extremely difficult."}

C[548] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA"], "literalist": ["IA"], "inclusive": ["IA"]},
  "stance_evidence": "'Investors want/need quarterly reports to help them manage their investments.'",
  "rationale_evidence": "IA: 'Most financial information comes monthly (banking, etc)... investments are the exception. Making them only twice a year will make it more difficult for investors to track important financial information'.",
  "summary": "Brief retail Oppose: financial information comes monthly in most contexts; making investments twice-yearly is an exception that hurts investor tracking."}

C[549] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA"], "literalist": ["IA"], "inclusive": ["IA"]},
  "stance_evidence": "'Please do NOT change from quarterly reports, I need the information to make timely decisions with my investments.'",
  "rationale_evidence": "IA: 'need the information to make timely decisions'.",
  "summary": "Brief retail Oppose: needs the information to make timely decisions with his investments."}

C[550] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'I am an individual investor and use the quarterly reports to stay current with my investments.'",
  "rationale_evidence": "IA: 'stay current with my investments'. IP: 'individual investor' framing.",
  "summary": "Retail Oppose: individual investor uses quarterly reports to stay current; semi-annual will not allow him to trade on latest financial information."}

C[551] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP", "CB", "ICc"], "literalist": ["AU", "IA", "IP"], "inclusive": ["AU", "IA", "IP", "CB", "ICc"]},
  "stance_evidence": "'I am commenting to strongly oppose the semi-annual reporting proposal... Half the reviewed, certified financial filings I receive each year would disappear.'",
  "rationale_evidence": "AU: the recurring AU template - 'a 10-Q which is reviewed by independent auditors, and personally signed by the CEO and CFO holding them legally accountable for its contents. The voluntary corporate communications suggested as part of the proposal that would replace them carry no such accountability to shareholders and the public'. IA: 'Individual shareholders like myself would lose the most information'. IP: 'Commission's own data show that individual investors own the majority of shares in smaller public companies'. CB: 2018-2019 SEC history (CFA Institute, CII opposed). ICc: UK 2014 'more than 90 percent of UK public companies continued to file quarterly reports on their own when they had the choice'.",
  "summary": "Substantive retail Oppose carrying the AU template (10-Q reviewed by independent auditors / CEO+CFO sign / voluntary corporate communications carry none of that); cites SEC's own data on individual-investor ownership in smaller companies; cites the 2018-2019 SEC review (CFA Institute + CII opposed); cites UK 2014 90%-voluntary-continuance."}

C[552] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "US"], "literalist": ["IA"], "inclusive": ["IA", "IP", "US"]},
  "stance_evidence": "'I strongly oppose the proposal to reduce SEC reporting to only twice a year. My family's investment portfolio depends on timely and accurate information.'",
  "rationale_evidence": "IA: 'untimely information that could be several months out of date'. IP: 'family's investment portfolio' framing. US: 'take care of U.S. citizens who depend on these reports for timely and accurate information'.",
  "summary": "Substantive retail Oppose: family investment portfolio depends on timely/accurate information; cutting to twice-yearly leaves investors with months-out-of-date information; SEC should take care of U.S. citizens who depend on these reports."}

C[553] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["MF", "IP"], "literalist": ["MF"], "inclusive": ["MF", "IP"]},
  "stance_evidence": "'Keep it quarterly. No one asked for this and passing it will undermine confidence in public markets.'",
  "rationale_evidence": "MF: 'undermine confidence in public markets'. IP: 'instead, focus on congressional insider trading and reporting rules' (alternative locus of regulatory effort, investor-protection theme).",
  "summary": "Brief retail Oppose: no one asked for this; will undermine confidence in public markets; SEC should focus on congressional insider trading rules instead."}

C[554] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "FR", "CMP", "MF", "US"], "literalist": ["IA", "FR", "MF"], "inclusive": ["IA", "FR", "CMP", "MF", "US"]},
  "stance_evidence": "'I think this proposal of 10-S reporting is not good policy with regards to trust in corporate financial disclosures.'",
  "rationale_evidence": "IA: 'runs on up to date information about listed companies'. FR: 'more potential for fraud, and malfeasance'. CMP: 'less inter/intra sector comparability'. MF: 'volatile surprise to delayed economic information release... extra quarter of delay'. US: 'US stock market is a shining example for the world'.",
  "summary": "Substantive retail Oppose written under the alias 'Gestalt Fund': US markets are a global example; quarterly cadence has worked for decades; AI accelerates information pace; delayed economic releases produce volatile surprises; semi-annual brings less transparency, less inter/intra-sector comparability, more fraud potential."}

C[555] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU"], "literalist": ["AU"], "inclusive": ["AU"]},
  "stance_evidence": "'Reports should remain quarterly. This is the only way to keep companies accountable.'",
  "rationale_evidence": "AU: 'the only way to keep companies accountable'.",
  "summary": "Two-line retail Oppose: quarterly is the only way to keep companies accountable."}

C[556] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'I am an individual investor. I am strongly opposed to the proposed rule changes because they would eliminate or restrict information vital to the investing public.'",
  "rationale_evidence": "IA: 'rely on the information in 10Q filings to make informed investment decisions'. IP: 'individual investor', 'my fellow individual investors'.",
  "summary": "Retail Oppose: individual investor; relies on 10Q filings for informed decisions; the changes would eliminate or restrict information vital to the investing public."}

C[557] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP", "MF"], "literalist": ["AU", "IA"], "inclusive": ["AU", "IA", "IP", "MF"]},
  "stance_evidence": "'We are opposed to the SEC proposal to reduce the number of certified financial filings each year by half. That is not what we want as investors.'",
  "rationale_evidence": "AU: NAIC AU-template language - 'reviewed by independent auditors and then signed by the CEO and CFO... we value and trust these quarterly filings'. IA: 'Waiting six months for every financial filing would be cumbersome'. IP: NAIC investment-club individual-investor framing. MF: 'support the timely and accurate quarterly reporting'. Same template as #547 Vicki Kroc.",
  "summary": "Retail Oppose from Barbara Garrison (Abundance Strategist Investment Club, NAIC); same NAIC AU-template variant as #547 (independent auditors, CEO+CFO sign; club meets monthly to review stocks; six months would make decisions extremely difficult to time)."}

C[558] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Quarterly reporting must be preserved.'",
  "rationale_evidence": "Bare preservation request, no rationale supplied.",
  "summary": "Brief retail Oppose: quarterly reporting must be preserved."}

C[559] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'This rule benefits insiders at the expense of ordinary investors.'",
  "rationale_evidence": "IP: insider-vs-ordinary-investor framing (same template line as #511 Kali Lawson and #589 Bomar; does not qualify as PP per the narrow definition).",
  "summary": "Two-line retail Oppose: rule benefits insiders at the expense of ordinary investors (template line)."}

# ===== May 29 batch =====

C[560] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Keep quarterly reporting !'",
  "rationale_evidence": "Three-word preservation request. Same author as #464 Homer Hill (also Oppose/IP, 'Keep it quarterly! The big corporations need to be held accountable!'); DIFFERENT text on a DIFFERENT doc-id (2400966 vs 2397486 on 05-27), so kept separately per the standing rule (same commenter, different letters).",
  "summary": "Three-word retail Oppose. Second letter by Homer Hill (#464 was the first, 05-27)."}

C[561] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'I am in support of keeping reporting on a quarterly basis... value transparency.'",
  "rationale_evidence": "IA: 'all the more comforting to have actual reports issued quarterly'. IP: 'large amount invested for my age'. Signs as 'small business owner'.",
  "summary": "Retail Oppose from a small business owner: with all the noise from social, traditional media, finance, politicians, quarterly reports are comforting; values transparency in volatile times."}

C[562] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA"], "literalist": ["IA"], "inclusive": ["IA"]},
  "stance_evidence": "'It is critical that we have transparency at a time when the financial market is as volatile and anticipatory as it is today. Keep quarterly reporting.'",
  "rationale_evidence": "IA: transparency frame; market volatility frame.",
  "summary": "Two-line retail Oppose from a carpenter: transparency is critical in volatile markets; keep quarterly reporting."}

C[563] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA"], "literalist": ["IA"], "inclusive": ["IA"]},
  "stance_evidence": "'I rely on quarterly disclosures to make informed decisions.'",
  "rationale_evidence": "IA: 'rely on quarterly disclosures'.",
  "summary": "One-line retail Oppose: relies on quarterly disclosures for informed decisions."}

C[564] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'I am against this reduction in disclosure frequency.'",
  "rationale_evidence": "Bare opposition, no rationale supplied.",
  "summary": "One-line retail Oppose: against this reduction in disclosure frequency."}

C[565] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'This proposal would harm retail investors.'",
  "rationale_evidence": "IP: bare retail-investor-harm template line.",
  "summary": "One-line retail Oppose: proposal would harm retail investors (template line)."}

C[566] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Please vote against the proposed rule.'",
  "rationale_evidence": "Bare opposition, no rationale.",
  "summary": "One-line retail Oppose: vote against the proposed rule."}

C[567] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA"], "literalist": ["IA"], "inclusive": ["IA"]},
  "stance_evidence": "'Semiannual reporting reduces transparency.'",
  "rationale_evidence": "IA: transparency framing.",
  "summary": "One-line retail Oppose: semiannual reporting reduces transparency."}

C[568] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["MF"], "literalist": ["MF"], "inclusive": ["MF"]},
  "stance_evidence": "'Quarterly reports are essential to market integrity.'",
  "rationale_evidence": "MF: 'market integrity' framing.",
  "summary": "One-line retail Oppose: quarterly reports are essential to market integrity."}

C[569] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "FR", "MF"], "literalist": ["IA", "FR"], "inclusive": ["IA", "IP", "FR", "MF"]},
  "stance_evidence": "'I do not support semiannual reporting. For the retail investor, company information is limited, and market behavior opaque. Moving away from quarterly reporting is absolutely the wrong direction.'",
  "rationale_evidence": "IA: 'company financial information is more obfuscated and less scrutinized than ever'. IP: 'For the retail investor, company information is limited'. FR: 'contributing to market manipulation, corruption, and bubbles'. MF: market-stability frame.",
  "summary": "Substantive retail Oppose ('Dr. Robert L. Jarecki, Jr.'): for retail investors, company information is already limited and market behavior opaque; moving away from quarterly contributes to manipulation, corruption, and bubbles; more transparency, not less."}

C[570] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'The proposed rule weakens investor protection.'",
  "rationale_evidence": "IP: bare investor-protection-weakening template line.",
  "summary": "One-line retail Oppose: rule weakens investor protection (template line)."}

C[571] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "MF", "FR", "AU"], "literalist": ["IA", "MF", "AU"], "inclusive": ["IA", "MF", "FR", "AU"]},
  "stance_evidence": "'I am writing to express my strong opposition to the Commission's proposal to allow public registrants the option to switch from a quarterly to a semi-annual reporting framework (Form 10-S).'",
  "rationale_evidence": "IA: 'material changes in operational health, supply chain stability, and inventory velocity will remain obscured from the public for up to half a year'. MF: 'Amplification of Gap Risk and Idiosyncratic Volatility... massive, violent asset price gapping on earnings release dates... overnight capital destruction'. FR: 'dangerous information vacuum'. AU: legal-accountability frame (implicit).",
  "summary": "Substantive retail Oppose ('Individual Investor'): active market participant relying on timely data; six-month cycle introduces a dangerous information vacuum; operational health, supply chain, inventory velocity obscured for half a year; will produce massive jump volatility and overnight capital destruction at earnings releases."}

C[572] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Quarterly reporting must be preserved.'",
  "rationale_evidence": "Bare preservation request (template line).",
  "summary": "Brief retail Oppose: quarterly reporting must be preserved (template line)."}

C[573] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'The proposed rule weakens investor protection.'",
  "rationale_evidence": "IP: investor-protection-weakening template line.",
  "summary": "One-line retail Oppose: rule weakens investor protection (template line)."}

C[574] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Quarterly disclosure has worked for decades and should remain.'",
  "rationale_evidence": "Bare 'decades' preservation argument, no specific code engaged.",
  "summary": "One-line retail Oppose: quarterly disclosure has worked for decades and should remain."}

C[575] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["FR"], "literalist": ["FR"], "inclusive": ["FR"]},
  "stance_evidence": "'I am against this proposal. It will cause rampant fraud and will hurt everyday investors. Inside trading will be much harder to track and convict.'",
  "rationale_evidence": "FR: 'cause rampant fraud... Inside trading will be much harder to track and convict'.",
  "summary": "Retail Oppose: will cause rampant fraud; insider trading will be much harder to track and convict."}

C[576] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["SG"], "literalist": ["NR"], "inclusive": ["SG"]},
  "stance_evidence": "'Please do not adopt the elimination of quarterly reporting. Optional reporting frequency means the strongest companies stay quarterly and the weakest opt out.'",
  "rationale_evidence": "SG: explicit adverse-selection / signaling framing - 'strongest companies stay quarterly and the weakest opt out'; this is the SEC's own SG code reversed (commenter reads the signaling channel as a selection-bias harm).",
  "summary": "Brief retail Oppose with an explicit adverse-selection argument: optional reporting means strongest stay quarterly and weakest opt out."}

C[577] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP", "CB", "IA"], "literalist": ["IA"], "inclusive": ["IP", "CB", "IA"]},
  "stance_evidence": "'i am against the rule. The argument that quarterly reporting is too expensive ignores its benefits. Information lag favors institutions over individuals.'",
  "rationale_evidence": "CB: explicit counter to the cost-burden argument ('too expensive ignores its benefits'). IA: 'Information lag'. IP: 'favors institutions over individuals'.",
  "summary": "Brief retail Oppose: the too-expensive argument ignores benefits; information lag favors institutions over individuals."}

C[578] = {"stance": OPP, "entity": INVPRO,
  "rationales": {"primary": ["MF", "IA"], "literalist": ["MF"], "inclusive": ["MF", "IA"]},
  "stance_evidence": "'We need quarterly reporting, this is going to cause the next mark crash'",
  "rationale_evidence": "MF: 'next mark[et] crash'. Signs as 'Banker at JPM ECM' - investment-banking professional.",
  "summary": "Brief Investment professional Oppose from a JPM ECM banker: need quarterly reporting; this is going to cause the next market crash."}

C[579] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'I am deeply concerned about reducing the reporting requirements to the SEC.'",
  "rationale_evidence": "IA: 'not getting timely updates on financial decisions and actions and standings'. IP: 'increase risk to investors'.",
  "summary": "Retail Oppose: reducing reporting could increase risk to investors by not getting timely updates."}

C[580] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["MF", "EX"], "literalist": ["MF"], "inclusive": ["MF", "EX"]},
  "stance_evidence": "'I respectfully oppose Rule S7-2026-15... An information vacuum causes investors to overreact to peer-firm news as a proxy for silent firms.'",
  "rationale_evidence": "MF: price-discovery / information-vacuum frame. EX: explicit spillover frame ('peer-firm news as a proxy for silent firms') - matches the SEC's own EX code on quarterly-filer spillover effects.",
  "summary": "Brief retail Oppose with an explicit spillover argument: information vacuum causes investors to overreact to peer-firm news as a proxy for silent firms."}

C[581] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP"], "literalist": ["AU", "IA", "IP"], "inclusive": ["AU", "IA", "IP"]},
  "stance_evidence": "'We need current information to make informed decisions. We would loose over half of the reviewed, certified financial filings annually if this is approved.'",
  "rationale_evidence": "AU: the recurring AU template - 'the 10-Q is reviewed by independent auditors, and the CEO and CFO sign it personally and can be held legally accountable for its contents. The voluntary corporate communications that would replace them carry none of that'. IA: 'We need current information to make informed decisions'. IP: 'as a small investor'.",
  "summary": "Substantive retail Oppose carrying the standard AU template; 31-year Investment Club member; we update stock reports quarterly; waiting twice-yearly would impact decision-making; as a small investor, DO NOT approve. (Same campaign-template text as #585 Kenneth A. Adams.)"}

C[582] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA", "IP"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'I am independent investor who uses the quarterly reports to guide my investing decisions.'",
  "rationale_evidence": "IA: '10-Q to provide a complete picture of the financial health of a company'. IP: 'do not have access to all of the information that an institutional investment firm such as Fidelity might be able to access... will unfairly penalize individual investors as we will not have access to the same timely information as institutional investors'.",
  "summary": "Retail Oppose: independent investor relies on 10-Q for complete picture; moving to semi-annual unfairly penalizes individuals vs institutional investors with greater access."}

C[583] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'I am vehemently opposed to S7-2026-15. Markets thrive on information, not obscurity. Has anyone asked retail investors?'",
  "rationale_evidence": "IA: 'Markets thrive on information, not obscurity'. IP: 'Has anyone asked retail investors?'",
  "summary": "Brief retail Oppose: vehemently opposed; markets thrive on information, not obscurity; has anyone asked retail investors?"}

C[584] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'As an individual investor, quarterly reports are my only method of tracking my investments.'",
  "rationale_evidence": "IA: 'quarterly reports are my only method of tracking my investments... waiting 6 months to get an audited report is too long'. IP: 'don't have professional advisors or AI helping me'.",
  "summary": "Retail Oppose: individual investor; quarterly reports are his only tracking method; doesn't have professional advisors or AI; waiting 6 months for an audited report is too long."}

C[585] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "IP"], "literalist": ["AU", "IA", "IP"], "inclusive": ["AU", "IA", "IP"]},
  "stance_evidence": "'We need current information to make informed decisions. We would loose over half of the reviewed, certified financial filings annually if this is approved.'",
  "rationale_evidence": "AU: standard AU template - 'the 10-Q is reviewed by independent auditors, and the CEO and CFO sign it personally and can be held legally accountable for its contents. The voluntary corporate communications that would replace them carry none of that'. IA + IP same as #581. Verbatim identical to #581 Mike Pechacek (different commenter); kept separately per the campaign-template precedent.",
  "summary": "Substantive retail Oppose carrying the standard AU template; 31-year Investment Club member; we update stock reports quarterly. (Verbatim same text as #581 Mike Pechacek; campaign template, different commenter, kept separately.)"}

C[586] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'Quarterly reports are vital to members of my investment club. We depend on standardized and accurate quarterly information to make informed group decisions.'",
  "rationale_evidence": "IA: 'standardized and accurate quarterly information'. IP: investment-club individual-investor framing.",
  "summary": "Retail Oppose from a Valley Womens Investment Club member: quarterly reports are vital to club members; standardized accurate information needed for group decisions."}

C[587] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'i refuse to support this regulation.'",
  "rationale_evidence": "Bare refusal, no rationale supplied.",
  "summary": "Six-word retail Oppose: refuses to support this regulation."}

C[588] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP"], "literalist": ["IA"], "inclusive": ["IA", "IP"]},
  "stance_evidence": "'Bad idea! If you can't see how a company is doing quarterly it makes it differcult to see what is happening in the company...'",
  "rationale_evidence": "IA: 'see how a company is doing quarterly'. IP: 'As an individual invester you want to see quarterly information'.",
  "summary": "Brief retail Oppose: bad idea; individual investor needs quarterly visibility into company performance to time buy/sell decisions."}

C[589] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'This rule benefits insiders at the expense of ordinary investors.'",
  "rationale_evidence": "IP: insider-vs-ordinary-investor template line (same as #511 and #559; does not qualify as PP per the narrow definition).",
  "summary": "Three-line retail Oppose: rule benefits insiders at the expense of ordinary investors (template line)."}

C[590] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "FR"], "literalist": ["IA"], "inclusive": ["IA", "FR"]},
  "stance_evidence": "'Stop hiding from the public. That's what is wrong with this country. Lack of transparency is corruption.'",
  "rationale_evidence": "IA: 'transparency'. FR: 'hiding from the public... corruption' (concealment frame). Does not qualify as PP - 'lack of transparency is corruption' is a generic concealment-suspicion frame without political-pressure attribution.",
  "summary": "Three-line retail Oppose: stop hiding from the public; lack of transparency is corruption."}

# ===== May 30 batch =====

C[591] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'I respectfully oppose the proposed Form 10-S. Quarterly reporting protects retail investors.'",
  "rationale_evidence": "IP: 'protects retail investors'.",
  "summary": "Two-line retail Oppose: respectfully opposes Form 10-S; quarterly reporting protects retail investors."}

C[592] = {"stance": SUP, "entity": IND,
  "rationales": {"primary": ["CB"], "literalist": ["NR"], "inclusive": ["CB"]},
  "stance_evidence": "'To much over site.' (i.e., 'Too much oversight' - read as Support of the proposal to reduce oversight burden)",
  "rationale_evidence": "CB: reduction-of-oversight-burden framing implicit in 'too much oversight'.",
  "summary": "Three-word retail Support: 'too much oversight' (i.e., supports the proposal to reduce SEC reporting burden)."}

C[593] = {"stance": OPP_COND, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "FR", "CMP", "AL", "MF"], "literalist": ["AU", "IA"], "inclusive": ["AU", "IA", "FR", "CMP", "AL", "MF"]},
  "stance_evidence": "'I am writing to express my opposition to the Commission's proposed rule S7-2026-15... I urge you to rework or abandon the proposal.'",
  "rationale_evidence": "AU: 'Quarterly reporting is one of the few mechanisms that ensures standardized, timely, and accurate financial information, according to US GAAP'. IA: 'standardized, timely, and accurate'. FR: 'Semi-annual reporting, on the other hand, would allow press releases, spin, and false narratives to drive valuations much longer, and corrections would be much steeper'. CMP: 'the proposed rule treats all companies equally - from a longstanding, trillion dollar brand to a new, million dollar startup. Treating such disparity equally is a fundamental flaw'. AL: explicit alternative-cadence proposal - 'A better approach would have been to make this rule available for smaller companies, such as those traded Over-The-Counter (like OTCQX and OTCQB), but unavailable for larger companies'. MF: market-discipline frame.",
  "stance_note": "Skeptic flips to Conditional per the pattern in #486 Anderson / #492 Calime: Wagner offers a concrete alternative-cadence proposal (scaled relief for smaller / OTC issuers only) and writes 'rework or abandon the proposal'.",
  "summary": "Substantive Oppose with an alternative-cadence proposal: GAAP-standardized timely reports prevent press-release spin from driving valuations; rule treats trillion-dollar and million-dollar issuers identically (fundamental flaw); better approach would scale semiannual to smaller / OTC-traded issuers only."}

C[594] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA"], "literalist": ["IA"], "inclusive": ["IA"]},
  "stance_evidence": "'Please allow transparency to continue as it is.'",
  "rationale_evidence": "IA: transparency framing.",
  "summary": "One-line retail Oppose: allow transparency to continue as it is."}

C[595] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Public companies should have to continue to report their financial state every 3 months'",
  "rationale_evidence": "Bare preservation statement, no rationale supplied.",
  "summary": "One-line retail Oppose: public companies should report every 3 months."}

C[596] = {"stance": OPP, "entity": ISFORMER,
  "rationales": {"primary": ["AU", "FR", "IA"], "literalist": ["AU", "FR"], "inclusive": ["AU", "FR", "IA"]},
  "stance_evidence": "'Quarterly reporting discourages this weakness. It is better to have mechanisms that support honesty for the public, and investors, and help corporations stay fair and honest.'",
  "rationale_evidence": "AU: 'mechanisms that support honesty' / accountability framing. FR: 'human temptation of number manipulation to be very strong - because bonuses, salary and promotions are conditional on meeting certain numbers'. IA: traffic-laws analogy.",
  "summary": "Issuer-former Oppose from a former in-house counsel: across multiple major corporations, saw the human temptation of number manipulation tied to comp-on-numbers; quarterly reporting acts like traffic laws - a mechanism that unconsciously keeps things orderly and fair."}

C[597] = {"stance": OPP, "entity": INDPRACT,
  "rationales": {"primary": ["AU", "US"], "literalist": ["AU"], "inclusive": ["AU", "US"]},
  "stance_evidence": "'As an equity compensation expert, I appreciate SEC filing obligations, as they protect American investors and demand some accountability and clarity from public company leaders.'",
  "rationale_evidence": "AU: 'demand some accountability and clarity from public company leaders... You simply cannot assume individuals will act in the best interest of their countrymen with their personal compensation on the line'. US: 'protecting Americans by keeping the reporting quarterly'.",
  "summary": "Industry-practitioner Oppose from an equity compensation expert: SEC filing obligations protect American investors; cannot assume executives will act in best interest when compensation is on the line."}

C[598] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Should keep reporting with no 6 month backout.'",
  "rationale_evidence": "Eight-word preservation request, no rationale supplied.",
  "summary": "Eight-word retail Oppose: should keep reporting with no 6-month backout."}

C[599] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "IP", "RI", "MF"], "literalist": ["IA"], "inclusive": ["IA", "IP", "RI", "MF"]},
  "stance_evidence": "'Please do NOT change the reporting requirements for public companies from quarterly to semi-annually.'",
  "rationale_evidence": "IA: 'Investors need factual information on a timely basis'. IP: 'rely on information from companies in deciding how to update my portfolio'. RI: 'many sources of unbiased investor information rely on company reports, such as Value Line and Morningstar and increasingly, AI' - explicit downstream-workflow reliance. MF: 'Any action that reduces the public part of publicly traded companies reduces public trust, in them and in the SEC'.",
  "summary": "Substantive retail Oppose: relies on company reports for portfolio updates; Value Line, Morningstar, and AI tools depend on company reports; reducing 'public' part of publicly traded reduces public trust in companies and in the SEC."}

C[600] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "MF", "AU"], "literalist": ["IA", "MF"], "inclusive": ["IA", "MF", "AU"]},
  "stance_evidence": "'I am against the proposed Form 10-S. Quarterly reporting preserves timely transparency, giving investors and regulators a frequent, unfiltered view of a company's operational health before small problems become large ones.'",
  "rationale_evidence": "IA: 'timely transparency, giving investors and regulators a frequent, unfiltered view'. MF: 'strengthens market discipline by reducing the information gaps that can lead to volatility, speculation, or mispricing'. AU: 'quarterly cadence enforces consistent management accountability... evaluated in real time rather than hidden within six-month reporting windows'.",
  "summary": "Substantive retail Oppose: quarterly preserves timely transparency before small problems become large; market discipline reduces volatility, speculation, mispricing; enforces consistent management accountability in real time."}

C[601] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Are you serious...we are dealing with the worst corruption ever and SEC wants to protect itself and other corrupt entities...stop stop stop...'",
  "rationale_evidence": "No engaged rationale; the letter is an expression of outrage. PP-watch: explicit regulatory-capture attribution ('SEC wants to protect itself and other corrupt entities') qualifies as PP per the narrow definition.",
  "summary": "Brief retail Oppose: outrage at corruption; SEC wants to protect itself and other corrupt entities. PP-watch instance (capture attribution)."}

# ===== May 30 (continued) =====

C[602] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'I want quarterly reports! Twice a year is not enough.'",
  "rationale_evidence": "Bare preservation request, no rationale supplied.",
  "summary": "Two-line retail Oppose: wants quarterly reports; twice a year is not enough."}

C[603] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["FR"], "literalist": ["FR"], "inclusive": ["FR"]},
  "stance_evidence": "'Keep the quarterly oversight. It is not appropriate to stop oversight to satisfy executives that want to hide illegal or inappropriate behavior.'",
  "rationale_evidence": "FR: 'executives that want to hide illegal or inappropriate behavior' (concealment frame).",
  "summary": "Two-line retail Oppose: not appropriate to stop oversight to satisfy executives that want to hide illegal or inappropriate behavior."}

C[604] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA"], "literalist": ["IA"], "inclusive": ["IA"]},
  "stance_evidence": "'I believe that the SEC should continue to require quarterly reports. Investors depend on them to know how their company is doing and a lot can change in 6 months.'",
  "rationale_evidence": "IA: 'a lot can change in 6 months'.",
  "summary": "Brief retail Oppose: investors depend on quarterly reports; a lot can change in 6 months."}

C[605] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP", "IA", "US"], "literalist": ["IP", "IA"], "inclusive": ["IP", "IA", "US"]},
  "stance_evidence": "'Small investors managing our own retirement accounts continue to need historically furnished quarterly financial reports from companies.'",
  "rationale_evidence": "IP: 'Small investors managing our own retirement accounts'. IA: 'minimal company knowledge and protection from losing our money'. US: 'keeping cap gains taxes flowing to US Treasury'.",
  "summary": "Retail Oppose: small investors with retirement accounts need quarterly reports for minimal company knowledge and protection; also helps keep capital-gains taxes flowing to US Treasury."}

C[606] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "FR"], "literalist": ["IA"], "inclusive": ["IA", "FR"]},
  "stance_evidence": "'RETIRED!, This is a terrible idea. I'm retired and cannot afford to wait 6 months for information to make portfolio changes.'",
  "rationale_evidence": "IA: 'cannot afford to wait 6 months for information to make portfolio changes'. FR: 'Has Enron taught us nothing?' (historical fraud reference).",
  "summary": "Brief retail Oppose from a retired investor: cannot afford to wait 6 months for portfolio-change information; has Enron taught us nothing?"}

C[607] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["FR", "US"], "literalist": ["FR"], "inclusive": ["FR", "US"]},
  "stance_evidence": "'There no world in which this will be a good thing. This is not a world standard and everywhere you see biannual reporting you will find fraud.'",
  "rationale_evidence": "FR: 'everywhere you see biannual reporting you will find fraud'. US: 'not a world standard'. PP-watch: explicit political attribution - 'at least under a republican administration' - qualifies as PP per the narrow definition.",
  "summary": "Brief Anonymous retail Oppose: not a world standard; biannual reporting is associated with fraud; the United States way under a republican administration. PP-watch instance (political attribution)."}

C[608] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["NR"], "literalist": ["NR"], "inclusive": ["NR"]},
  "stance_evidence": "'Are you all out of your minds?? Why is this terrible idea even being proposed? NO!!!'",
  "rationale_evidence": "Bare exclamation of opposition, no engaged rationale.",
  "summary": "Three-line Anonymous retail Oppose: are you all out of your minds; terrible idea; NO."}

C[609] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'We need sufficient time to ensure a (supposed) level field.'",
  "rationale_evidence": "IP: level-playing-field framing.",
  "summary": "One-line retail Oppose: need sufficient time to ensure a level playing field."}

C[610] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP"], "literalist": ["IP"], "inclusive": ["IP"]},
  "stance_evidence": "'I am opposed to the proposal to drop Form 10-Q. This is unethical, sketchy, and should be illegal. The fact that it's being considered is a huge cause for concern for the ordinary investor.'",
  "rationale_evidence": "IP: 'cause for concern for the ordinary investor'.",
  "summary": "Brief retail Oppose: drop-10-Q is unethical, sketchy, should be illegal; huge cause for concern for the ordinary investor."}

C[611] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["AU", "IA", "FR", "MF"], "literalist": ["AU", "IA"], "inclusive": ["AU", "IA", "FR", "MF"]},
  "stance_evidence": "'I am writing in opposition to the proposed Form 10-S. Accountability and transparency should be a priority.'",
  "rationale_evidence": "AU: 'Accountability'. IA: 'transparency'. FR: 'institutional bad actors'. MF: 'weaken our economy'.",
  "summary": "Brief retail Oppose: accountability and transparency should be a priority; do not weaken the economy in favor of institutional bad actors."}

C[612] = {"stance": OPP, "entity": INVPRO,
  "rationales": {"primary": ["MF"], "literalist": ["MF"], "inclusive": ["MF"]},
  "stance_evidence": "'Will lead to another financial crisis.'",
  "rationale_evidence": "MF: financial-crisis frame. Letterhead Creative Investment Research; author has published books on minority-owned business and the JOBS Act.",
  "summary": "Investment-professional Oppose from William Michael Cunningham (Creative Investment Research, author of books on minority-owned business and the JOBS Act): will lead to another financial crisis."}

C[613] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["FR"], "literalist": ["FR"], "inclusive": ["FR"]},
  "stance_evidence": "'I oppose S7-2026-15. Allowing corporations to reduce reporting could allow malfeasance to go undetected for longer periods of time and hide problems within the business.'",
  "rationale_evidence": "FR: 'allow malfeasance to go undetected... hide problems within the business'.",
  "summary": "Brief retail Oppose from an engineer: reduced reporting could allow malfeasance to go undetected longer and hide problems within the business."}

C[614] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["FR"], "literalist": ["FR"], "inclusive": ["FR"]},
  "stance_evidence": "'I urge you to reject the proposed reduction in reporting frequency. Less reporting means more insider trading opportunities.'",
  "rationale_evidence": "FR: 'more insider trading opportunities'.",
  "summary": "Two-line retail Oppose: less reporting means more insider trading opportunities."}

# ===== Jun 1 batch =====

C[615] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "RI"], "literalist": ["IA"], "inclusive": ["IA", "RI"]},
  "stance_evidence": "'Keep quarterly reporting mandatory. Even Make it monthly. We need to be able to see the trends in materials manufacturing for construction pricing.'",
  "rationale_evidence": "IA: trends visibility. RI: non-investor downstream-workflow reliance - 'trends in materials manufacturing for construction pricing' - construction-industry use case for quarterly company data.",
  "summary": "Brief Oppose from a licensed architect/contractor: keep quarterly mandatory, even monthly; needs trends in materials manufacturing for construction pricing."}

C[616] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["FR", "MF"], "literalist": ["FR"], "inclusive": ["FR", "MF"]},
  "stance_evidence": "'Keep quarterly reporting! These companies and feckless CEOs are going to attempt the same rug pull Elon is attempting with SpaceX and TRUST ME you do NOT want to be the one everyone points to as for why we have another economic crash like 2008.'",
  "rationale_evidence": "FR: 'rug pull' / fraud framing. MF: 'economic crash like 2008'. PP-watch: 'The regime is already doing what they can to weaken the US economy, why would you guys volunteer to take the fall for them?' - explicit political-pressure / regime attribution, qualifies as PP per the narrow definition.",
  "summary": "Retail Oppose from a civil engineer: feckless CEOs will pull the same rug Elon is attempting with SpaceX; another 2008-style economic crash; the regime is weakening the US economy. PP-watch instance (regime attribution)."}

C[617] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["CB", "AU"], "literalist": ["AU"], "inclusive": ["CB", "AU"]},
  "stance_evidence": "'Keep quarterly reporting. Now that we have computer, wait, yes we do have computers.'",
  "rationale_evidence": "CB: implicit counter to cost-burden argument - 'now that we have computers'. AU: 'The SEC is supposed to be the financial Watch Dog, so, you set the standards and Companies Comply. Don't let the Fox Guard the Hen House'.",
  "summary": "Brief retail Oppose: now that we have computers, the cost-burden argument fails; SEC is the financial Watch Dog and sets standards; don't let the fox guard the hen house."}

# ===== Jun 2 batch =====

# Foley & Lardner letter
C[618] = {"stance": SUP, "entity": INDPRACT,
  "rationales": {"primary": ["OP", "AL", "MF"], "literalist": ["OP", "AL"], "inclusive": ["OP", "AL", "MF"]},
  "stance_evidence": "'We support the proposed Form 10-S as an optional alternative to three Form 10-Qs. The decision whether to report quarterly or semiannually is one that boards, audit committees, and investors are best positioned to make based on a company's industry, business model, and investor expectations.'",
  "rationale_evidence": "OP: explicit optionality / flexibility frame - 'decision whether to report quarterly or semiannually is one that boards, audit committees, and investors are best positioned to make'. AL: explicit alternative-cadence / OP-on-AL frame - the proposal is itself the alternative, lawyers endorse the optional Form 10-S structure. MF: explicit acknowledgment - 'Cutting two quarterly reports could increase the cost of capital. But that is a business judgment, not a regulatory one'. Cross-filed letter (filed on S7-2026-18 docket, lists S7-2026-15 + S7-2026-17 + S7-2026-18 + CLL-16 in Re).",
  "stance_note": "Cross-filed at S7-2026-18 docket URL but addresses S7-2026-15 substantively in Part I.C. The 8-bucket entity taxonomy does not yet have a Trade-association / Advocacy or Legal-practitioner bucket; coded as Industry practitioner-technologist for now. Re-bucket after the 2018 rubric fold-in ships.",
  "summary": "Substantive Support from Louis Lehot and Patrick Daugherty (Foley & Lardner LLP, Silicon Valley + Chicago, capital-formation lawyers with 70+ combined years advising founders, boards, underwriters, and investors); explicit OP/AL/MF framing - choice should rest with boards, audit committees, investors; cutting two reports could raise cost of capital, but that is a business judgment, not a regulatory one; expect few to elect semiannual in the near term; cross-filed with S7-2026-17, S7-2026-18, CLL-16."}

C[619] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP", "IA", "FR"], "literalist": ["IA"], "inclusive": ["IP", "IA", "FR"]},
  "stance_evidence": "'I oppose SEC Proposal S7-2026-15. Letting public companies go six months without required financial reporting is bad for ordinary investors.'",
  "rationale_evidence": "IP: 'Retail investors should not be forced to buy, sell, or hold stocks using stale information while executives and large institutions have a clearer picture'. IA: 'stale information'. FR: 'gives insiders more time to act on information before the public sees it'.",
  "summary": "Retail Oppose from a Chicago software developer (Justin Kobylarz): six months without required reporting gives insiders more time to act on information before the public sees it; retail should not be forced to trade on stale information while executives and institutions have a clearer picture."}

C[620] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IA", "US"], "literalist": ["IA"], "inclusive": ["IA", "US"]},
  "stance_evidence": "'Quarterly reporting must be preserved. I don't see why companies don't report monthly.'",
  "rationale_evidence": "IA: 'less transparency' framing. US: 'American investor's best interests'. Does not qualify as PP - 'unless they do not prioritize the American investor's best interests' is motive-questioning without political-attribution.",
  "summary": "Retail Oppose from a Realtor: quarterly must be preserved; companies could report monthly with a click of a mouse; no idea why SEC would want less transparency unless they do not prioritize the American investor's best interests."}

# ===== Jun 3 batch =====

C[621] = {"stance": OPP, "entity": ENT_OVERRIDE[621],
  "rationales": {"primary": ["MF", "IP", "IA"], "literalist": ["MF", "IA"], "inclusive": ["MF", "IP", "IA"]},
  "stance_evidence": "'Keep quarterly reporting. It's essential for individual investors. Factors affecting stock price happen much too quickly with computerized trading.'",
  "rationale_evidence": "MF: 'Factors affecting stock price happen much too quickly with computerized trading'. IP: 'essential for individual investors'. IA: timeliness frame. Signs as VP Quality TYRX Inc. - mixed entity (Letterhead: Issuer-current at a Medtronic subsidiary; Self-described + Primary: Individual since substance is investor-side, not issuer-side).",
  "summary": "Brief Oppose from Ronald Salsbury (VP Quality, TYRX Inc.): quarterly essential for individual investors; computerized trading makes stock prices move too quickly for semiannual cadence. Letterhead-mixed entity (Individual majority, Issuer-current letterhead)."}

C[622] = {"stance": OPP, "entity": IND,
  "rationales": {"primary": ["IP", "FR", "CMP"], "literalist": ["IP"], "inclusive": ["IP", "FR", "CMP"]},
  "stance_evidence": "'Keep quarterly reporting! If you create a two-tiered system, where company insiders and institutional investors know critical news months before everyday investors, those everyday/individual investors will choose to remove their capital from the market.'",
  "rationale_evidence": "IP: 'two-tiered system... company insiders and institutional investors know critical news months before everyday investors'. FR: insider-information-gap framing. CMP: explicit divestment threat - 'everyday/individual investors will choose to remove their capital from the market' (same CMP usage as #507 Hoffman, #532 Casabona).",
  "summary": "Retail Oppose from a small-business owner (McCabe Fine Woodworking, West Chester PA): two-tiered information system would push everyday investors to remove their capital from the market; we expect our regulatory bodies to REGULATE."}


def majority_rationales(per_rater):
    counts = Counter()
    for codes in per_rater.values():
        for c in codes:
            counts[c] += 1
    return sorted([c for c, n in counts.items() if n >= 2])


records = json.loads(RECORDS.read_text())
by_n = {r["n"]: r for r in records}

# Apply name fix for Foley first (must run before letter-md header rewrite below)
for n, (nm, role) in NAME_FIX.items():
    rec = by_n[n]
    rec["name"] = nm
    rec["role"] = role

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
    rec = by_n[n]
    new_head = re.sub(r"^- \*\*Stance:\*\*.*$", f"- **Stance:** {rec['stance']}", head, flags=re.MULTILINE)
    new_head = re.sub(r"^- \*\*Entity:\*\*.*$", f"- **Entity:** {rec['entity']}", new_head, flags=re.MULTILINE)
    new_head = re.sub(r"^- \*\*Rationales:\*\*.*$", f"- **Rationales:** {', '.join(rec['rationales'])}", new_head, flags=re.MULTILINE)
    if n in DATE_FIX:
        new_head = re.sub(r"^- \*\*Date:\*\*.*$", f"- **Date:** {DATE_FIX[n]}", new_head, flags=re.MULTILINE)
    # Update top-line title if name was fixed (Foley)
    if n in NAME_FIX:
        new_head = re.sub(r"^# Letter \d+ —.*$",
                          f"# Letter {n} — {NAME_FIX[n][0]}",
                          new_head, flags=re.MULTILINE)
        new_head = re.sub(r"^- \*\*Role/Affiliation:\*\*.*$",
                          f"- **Role/Affiliation:** {NAME_FIX[n][1]}",
                          new_head, flags=re.MULTILINE)
    md.write_text(new_head + sep + body)

print("Letters/*.md headers rewritten.")

HOLD = {"Off-topic", "No position", "Duplicate"}
in_corp = [r for r in records if r["stance"] not in HOLD]
counts = Counter(r["stance"] for r in in_corp)
print(f"\nIn-corpus N={len(in_corp)} of {len(records)}: " + " / ".join(f"{n} {s}" for s, n in counts.most_common()))
held = Counter(r["stance"] for r in records if r["stance"] in HOLD)
if held:
    print(f"Held out: " + " / ".join(f"{n} {s}" for s, n in held.most_common()))
