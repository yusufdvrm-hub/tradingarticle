# Trader practice and measured performance: retail, bots, professional systematic (crypto emphasis)

Compiled 2026-10-15. Labels: [AUDITED/ACADEMIC] = peer-reviewed or regulator data; [SELF-REPORTED] = fund/firm/vendor claim, unaudited; [SECONDARY] = press or aggregator, primary not checked; [ANECDOTE] = single user. 18 searches; few primary PDFs were fetched, so exact numbers should be spot-checked against the linked originals before going into a final report.

## Q1. Retail profitability: day traders, CFD accounts, crypto retail, prop firms

### Takeaway
Every large-sample dataset found agrees: most retail active traders lose money, and the ones who keep going do not learn their way into profit. In Brazil, 97% of day traders who persisted 300+ days lost money. Taiwan day traders lose in aggregate. EU regulators found that 74–89% of retail CFD accounts lose. BIS found most crypto-app users lost money on bitcoin, and that retail bought exactly when large holders sold. Prop-firm pass/payout data is not published by the firms; the only industry figure (from a tech vendor) says about 7% of challenge buyers ever get a payout.

### Cited Findings
- **Brazil (Chague, De-Losso & Giovannetti, "Day Trading for a Living?", 2019/2020), [ACADEMIC]**: uses all Brazilian equity-index mini-futures day traders 2013–2015. Of those who day-traded on at least 300 days, 97% lost money. Only 0.4% earned more than a bank teller's starting wage (FGV version; the SSRN abstract says 1.1% beat the minimum wage and 0.5% beat a bank teller, so the numbers vary by version). The best individual earned about US$310/day "with great risk." No evidence of learning. — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101); [FGV repository](https://repositorio.fgv.br/items/e87d04fc-4b4c-4a56-ab5a-1c84c1afde1b/full); [Quantpedia summary](https://quantpedia.com/?p=4771)
  - CNN Brasil describes the persistent group as about 1,500 traders, of whom about 45 did not lose. [SECONDARY] — [CNN Brasil](https://www.cnnbrasil.com.br/business/day-trade-o-que-e-como-fazer-e-vale-a-pena/)
- **Taiwan (Barber, Lee, Liu, Odean [& Zhang], "Do Day Traders Rationally Learn About Their Ability?", later "Learning, Fast or Slow", Review of Asset Pricing Studies 10(1), 2020), [ACADEMIC]**: complete Taiwan transaction data 1992–2006. Aggregate day-trader performance is negative, and the vast majority are unprofitable. Unprofitable traders are more likely to quit, but too slowly for rational learning. The abstract states that 97% of day traders are likely to lose money in future day trading. — [Working paper PDF (Berkeley)](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/day%20trading%20and%20learning%20110217.pdf); [RePEc listing, RAPS 2020](https://ideas.repec.org/a/oup/rasset/v10y2020i1p61-93..html)
  - The same group has a separate paper on the cross-section of day-trader skill, which finds a small persistent top tier. — [Berkeley PDF "Day Trading Skill"](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf). The often-quoted "<1% predictably profitable" figure was **not verified in this session** (see Gaps).
- **EU CFDs (ESMA product intervention, 27 March 2018), [REGULATOR]**: national authorities' analyses found that 74–89% of retail CFD accounts typically lose money, with average losses per client of €1,600–€29,000. ESMA blamed excessive leverage, structurally negative expected returns (for binaries) and provider–client conflicts of interest. Measures: leverage caps of 30:1 to 2:1 (**2:1 for crypto CFDs**), a 50% margin close-out rule, negative-balance protection, and a mandatory risk warning stating each firm's "% of retail accounts lose money." — [ESMA](https://www.esma.europa.eu/node/84933); [Investment Executive](https://www.investmentexecutive.com/news/regulation/esma-to-ban-binary-options-restrict-cfds/)
  - Interpretation: the mandatory per-broker warning means current loss percentages are on every EU/UK CFD broker's site. They were not collected here.
- **Crypto retail (BIS Bulletin No 69, "Crypto shocks and retail losses", Cornelli, Doerr, Frost & Gambacorta, 20 Feb 2023), [REGULATOR/RESEARCH]**:
  - App download data for Aug 2015–Dec 2022 indicates that a majority of retail crypto-app users in nearly all economies lost money on their bitcoin. — [BIS](https://www.bis.org/publ/bisbull69.htm); [PDF](https://www.bis.org/publ/bisbull69.pdf)
  - Around the Terra/Luna and FTX collapses, large holders ("whales") sold while small retail holders bought. — [BIS](https://www.bis.org/publ/bisbull69.htm)
  - Press summaries put the modelled median loss at about US$431 on US$900 invested (−47.9%). This is a modelled figure under BIS assumptions (users buy US$100/month after downloading) and has not been checked against the PDF. [SECONDARY] — [Ecofin Agency](https://www.ecofinagency.com/finance/1104-44420-bitcoin-retail-investors-lost-47-89-of-invested-funds-on-average-bis-bulletin)
- **Prop firms**:
  - FTMO publishes no pass rate or payout rate. Its only verified disclosure found is a cumulative total of more than US$650m paid to traders since 2015, against 4.5m registered clients. — [TradeInformer, "What FTMO tells us about prop firm finances"](https://www.tradeinformer.com/prop-weekly/what-ftmo-tells-us-about-prop-firm-finances)
  - Industry figure: FPFX Tech (a prop-firm back-office vendor) found that about 14% of challenge takers got funded and about 7% of all traders achieved a payout, across about 300,000 accounts. [SELF-REPORTED, vendor] — [Finance Magnates via TradingView](https://www.tradingview.com/news/financemagnates%3A3a251e333094b%3A0-exclusive-only-7-of-300-000-prop-trading-accounts-achieved-payouts/)
  - The Funded Trader reported that only about 1 in 20 traders pass. [SELF-REPORTED] — [Finance Magnates](https://www.financemagnates.com/forex/only-1-in-20-traders-pass-prop-firm-challenges-reports-the-funded-trader/)
  - A third-party 2026 compilation estimates that 5–14% of challenges reach funding and about 7% get paid. It is an unaudited aggregation. — [Track360](https://track360.io/blog/prop-trading-industry-statistics-2026)

### Inferences
- Four independent settings (Brazilian futures, Taiwanese equities, EU CFDs, global crypto apps) give the same answer: active retail trading has negative expected value after costs, and persistence does not fix it. Any retail strategy needs to beat this base rate with explicit cost and leverage control, not discretionary skill.
- Prop-firm economics are mostly funded by challenge fees. At about 7% payout, the challenge model is closer to a lottery fee than to proof of edge.
- The BIS "whales sell, retail buys the crash" pattern implies that retail flow in crypto is systematically on the wrong side during stress. That is consistent with liquidation-cascade and contrarian-flow edges for whoever provides liquidity, not for the median retail account.

### Gaps
- Barber–Lee–Liu–Odean "The cross-section of speculator skill" (~2014/2017): the commonly quoted figure that <1% of day traders are predictably profitable net of fees was not confirmed in this session. Verify it from the paper before citing it.
- Current (2025–2026) ESMA/FCA broker loss percentages were not collected. Each EU broker's website shows its own figure.
- No exchange-published retail PnL distribution was found for Binance, Coinbase or others.
- No audited prop-firm pass or payout data exists. All figures are vendor or firm claims.

## Q2. Automated retail bots and copy trading: measured outcomes

### Takeaway
Measured, representative data on retail bot profitability essentially does not exist. Freqtrade, 3Commas, Pionex and Binance grid bots publish no outcome distributions, and what circulates is cherry-picked or anecdotal. The best evidence is on copy trading. Lead traders' own profits largely do not carry over to their followers, and in a controlled experiment the ability to copy raises risk-taking. User surveys show very high bot churn.

### Cited Findings
- **Copy-trading outcomes (90-day study of more than 100,000 copy relationships on Binance, Bybit and MEXC, 2025/26)** [SECONDARY, original report not seen; relayed by KuCoin, a competitor]:
  - Across all three exchanges, 97% of lead traders were profitable on their own positions, but only 43.6% delivered positive returns to the people copying them.
  - On Binance specifically, followers had a 66.5% win rate, net follower PnL was +572,979 USDT, and 72.45% of leaders delivered positive follower returns.
  - Sources: [KuCoin blog](https://www.kucoin.com/blog/is-crypto-copytrading-profitable-in-2026); [ainvest](https://www.ainvest.com/news/leader-copying-losing-point-2608/)
  - Interpretation: the gap between 97% and 43.6% is consistent with execution lag, slippage, and leaders being selected on survivorship. Win rate is not PnL.
- **Binance lead-trader incentives**: lead traders receive a 10% profit share from copiers plus 10% of copiers' trading fees. That rewards attracting volume, not follower returns. — [Coin Bureau review](https://coinbureau.com/Review/binance-copy-trading-review)
- **Copy trading raises risk-taking (Apesteguia, Oechssler & Weidenholzer, "Copy Trading", Management Science 66(12), 2020), [ACADEMIC, lab experiment]**: showing subjects others' results raised their risk-taking, and the increase was larger when they could copy directly. The authors conclude that copy trading encourages excessive risk-taking. — [BSE](https://bse.eu/research/publications/copy-trading); [Heidelberg DP 649](https://archiv.ub.uni-heidelberg.de/volltextserver/id/eprint/24778/contents)
- **Bot usage and churn (Adam Cochran survey, 2020, n=10,388, mostly r/CryptoCurrency)**: 38% had used a bot at least once, 93% of paying users stopped within a month, and 88% cited lack of trust in the bot or its developers. The survey measured usage and trust, not profit. — [Decrypt](https://decrypt.co/47577/crypto-traders-want-trading-bots-but-dont-trust-them-heres-why); [Cochran Substack](https://adamcochran.substack.com/p/86-of-crypto-capital-is-traded-by?open=false)
- The claim that "73% of automated crypto trading accounts fail within six months" circulates, attributed to For Traders/Coincub. No primary dataset was found, so treat it as weak. — [lenz.io aggregator](https://lenz.io/q/are-retail-crypto-trading-bots-profitable)
- **Grid bots**: no independent large-sample study was found. Binance Square backtests [ANECDOTE] show the structural problem:
  - A BTC/USDT grid in April 2025 returned +7.35% while BTC itself returned +14.15%. Grids underperform a rising market.
  - A SUI/USDT grid earned +197.52 USDT of "grid profit" but had a total ROI of −33.31% in a downtrend. Grid profit hides inventory losses.
  - Source: [Binance Square #GridBot](https://www.binance.com/square/hashtag/GridBot)
- A Stevens Institute student project on Bybit BTC data found that ML-based variants did not beat plain grid strategies. [ACADEMIC-STUDENT, low weight] — [Stevens FSC](https://fsc.stevens.edu/cryptocurrency-market-making-improving-grid-trading-strategies-in-bitcoin/)

### Inferences
- A grid bot is short volatility and mean-reverting: it sells into rallies and accumulates into declines. In trending crypto it underperforms buy-and-hold on the way up and holds a growing losing inventory on the way down. The "grid profit" metric that platforms display excludes that inventory PnL, which is a presentation bias.
- Copy-trading leaderboards are survivorship-filtered by design: losing leaders disappear, and rankings reward recent variance. Leader PnL is not evidence of edge for the copier.
- The absence of any platform publishing aggregate bot-user PnL is itself weak evidence that the aggregate is unflattering. This is an inference, not a fact.

### Gaps
- No measured live-outcome data was found for Freqtrade (open source, no telemetry), 3Commas, Pionex or Binance grid bots.
- No official Binance statistics on lead-trader or follower PnL distributions were found.
- The 100k-copy-trade study's original publisher and methodology were not seen.

## Q3. Professional systematic track records

### Takeaway
Real, long, mostly audited systematic records exist, but they split sharply. Medallion (closed, high-frequency and short horizon, employees only) is extraordinary. Renaissance's outside-investor funds (RIEF) are ordinary-to-good. Trend-following CTAs (SG Trend Index; AQR, Man AHL, Winton) earn a modest long-run premium with multi-year drawdowns: 2024 was +2.6%, and 2025 was about −10.5% at mid-year before recovering to about −2.3% by end-September. In crypto, market-neutral funds were the only category positive in 2025 (about +14% through November), while directional and fundamental funds lost. Quant-directional funds led in 2024 (+53.7%).

### Cited Findings
- **Renaissance Medallion** [SECONDARY, unaudited publicly]:
  - 1988–2021: about 66% annualised before fees and about 39% after fees. — [Institutional Investor](https://www.institutionalinvestor.com/article/2bswzoz7x91fqht87wvsw/portfolio/the-famed-medallion-fund-is-crushing-it-other-rentech-funds-not-so-much)
  - 2020: +76%. Long-run average net return about 40%, and reportedly no losing year in nearly four decades. — [247WallSt, 21 June 2026](https://247wallst.com/investing/2026/06/21/the-greatest-fund-ever-why-jim-simons-medallion-fund-keeps-winning-without-him/?.tsrc=rss)
  - A WSJ headline reposted by HFR says Medallion was "up 24% year to date" (the page appears to be from 2026, so the year is unconfirmed). — [HFR](https://www.hfr.com/media/in-the-news/wsj-renaissance%C2%92s-10-billion-medallion-fund-gains-24-year-to-date/)
- **Renaissance RIEF** (outside-investor fund): +22.7% in 2024, its best year since 2011 (+34%). Institutional Investor describes it as a "2024 rebirth"; sourced from a hedge-fund database, not a fund statement. RIEF had heavy losses in 2020 (Oct 2020 coverage). — [Institutional Investor, "Renaissance's 2024 rebirth"](https://www.institutionalinvestor.com/index%2ephp/article/2e0uykr3vn5booz0smrcw/hedge-funds/renaissances-2024-rebirth); [II, "Renaissance suffers huge losses October"](https://www.institutionalinvestor.com/article/renaissance-suffers-huge-losses-october)
  - Interpretation: the Medallion/RIEF gap is evidence that the extraordinary edge is capacity-constrained and short-horizon. The same firm's scalable, longer-horizon products earn ordinary returns.
- **Trend-following CTAs, SG indices (Société Générale)** [INDEX DATA, reported via Alternatives Watch]:
  - SG Trend Index: 2024 +2.6%. 2025 YTD was about −10.5% by 26 June, recovering to −2.27% YTD by end-September (September alone +5.73%). — [Alternatives Watch Jul 2025](https://www.alternativeswatch.com/2025/07/01/trend-following-hedge-funds-loss-h1-societe-generale-index/); [Alternatives Watch Sep 2025](https://www.alternativeswatch.com/2025/09/02/ctas-trend-following-hedge-funds-rebound-h1-rout-societe-generale-indices/); [SG CTA update 2025](https://content.sgmarkets.com/CTA_UPDATE_KEEPING_UP_WITH_THE_TRENDFOLLOWERS_2025)
  - SG CTA Index: −2.52% in Q1 2025, and down more than 8% YTD by late May 2025. — [Alternatives Watch Jun 2025](https://www.alternativeswatch.com/2025/06/02/trend-following-hedge-funds-endure-more-pain-societe-generale-indices/); [Alternatives Watch Mar 2025](https://www.alternativeswatch.com/2025/03/03/trend-following-hedge-funds-rattled-by-februarys-market-reversal-societe-generale-sg-index/)
  - Constituents: Winton rejoined the SG Trend Index for 2025, and Man AHL Alpha is in the SG CTA Index. AQR Managed Futures was reportedly above 8% in Q1 2025 (Reuters via secondary sources). — [Alternatives Watch](https://www.alternativeswatch.com/2025/09/02/ctas-trend-following-hedge-funds-rebound-h1-rout-societe-generale-indices/); [LPL "A Tale of Two CTAs"](https://www.lpl.com/research/blog/a-tale-of-two-ctas.html)
- **Crypto hedge funds**:
  - 2024 (Galaxy VisionTrack indices) [INDEX, fund self-reported inputs]: Quant Directional +53.7%, Fundamental +40.4%, Market Neutral about +18.5%. Most crypto hedge funds failed to beat bitcoin. — [Galaxy VisionTrack 2024 whitepaper](https://glxy.galaxy.com/hubfs/Asset%20Management/VisionTrack/GLXY_2024_Whitepaper_VisionTrack.pdf); [BNN Bloomberg, 15 Jan 2025](https://bnnbloomberg.ca/markets/crypto/2025/01/15/crypto-hedge-funds-had-great-2024-but-failed-to-top-bitcoin)
  - 2025 (through November) [SECONDARY]:
    - Market-neutral crypto funds were about +14.4%, the only positive category.
    - Directional funds were about −2.5% and fundamental funds about −23%. The same article also says directional funds fell 23%, so the figures are internally inconsistent.
    - Losses were tied to the 10–11 October 2025 flash crash (more than $2bn liquidated) and to decaying basis-trade yields.
    - Sources: [CoinEdition](https://coinedition.com/why-crypto-hedge-funds-are-losing-money-in-2025/); [HedgeCo](https://hedgeco.net/news/12/2025/hedge-funds-finish-2025-strong-capital-inflows-performance-surge.html); [Hedgeweek](https://www.hedgeweek.com/funds/14/)
  - An HFR-based report put crypto funds at +6.7% YTD in mid-2025. — [MEXC news aggregator](https://www.mexc.com/news/140096); [HFR crypto data](https://thefullfx.com/hfr-expands-crypto-fund-performance-data/)
  - Conflicting claim: SQ Magazine says crypto hedge funds averaged +36% in 2025, with quant funds +48%. It cites no primary source and contradicts the above, so treat it as unreliable. — [SQ Magazine](https://sqmagazine.co.uk/crypto-hedge-funds-statistics.md)
  - An earlier PwC/Elwood survey (year unclear, likely the 2020 or 2021 cohort) found quantitative strategies the best-performing category at an average of +58%. [SELF-REPORTED survey] — cited in [Sygnum](https://www.sygnum.com/?p=1326)

### Inferences
- The strategy families with long, real-money institutional evidence are (1) diversified trend following and carry (CTA indices, decades of data, low Sharpe, long drawdowns) and (2) market-neutral, arbitrage and basis in crypto (positive in both 2024 and 2025, but yields compress as capital arrives). Short-horizon statistical arbitrage works spectacularly only at Medallion's scale of infrastructure, which is not replicable by retail.
- Crypto quant-directional results (+53.7% in 2024) are beta-heavy in a bull year, and the negative 2025 shows that. They are not clean evidence of alpha.
- Survivorship and self-reporting bias affect all crypto fund indices: funds report voluntarily and dead funds drop out.

### Gaps
- Full-year 2025 and YTD 2026 figures were not found for the SG Trend/CTA indices, Galaxy VisionTrack, or Crypto Fund Research.
- Medallion 2024/2025 annual returns could not be verified.
- No Man AHL- or Winton-specific 2024–2026 returns were found.
- The latest PwC/AIMA Global Crypto Hedge Fund Report (2024/2025 edition) was not retrieved.

## Q4. Practitioner consensus on what retail can realistically exploit, and r/algotrading reports

### Takeaway
The verified practitioner material is thin. Carver's documented position is that realistic Sharpe ratios rarely exceed 1.0, that costs must be measured in Sharpe-ratio units per round trip, and that you need strong evidence before choosing a faster, costlier rule over a slower, cheaper one. That points retail toward slow, diversified trend and carry with cost discipline. No Reddit consensus could be retrieved directly.

### Cited Findings
- **Robert Carver, "Systematic Trading" (Harriman House)**, as summarised by CXO Advisory:
  - Costs are measured as the share of annualised raw Sharpe ratio lost per round trip, multiplied by turnover.
  - Realistic Sharpe ratios rarely exceed 1.0.
  - A faster variant needs considerable evidence of superiority before it is preferred over a slower, cheaper one.
  - Source: [CXO Advisory](https://www.cxoadvisory.com/big-ideas/a-few-notes-on-systematic-trading)
- **Carver's strategy mix**: trend (momentum, breakout, relative momentum) plus carry (futures-curve shape) across a diversified futures set. With limited capital he trades 30–35 instruments by building a fractional "virtual" portfolio and holding the whole contracts that best match it ("dynamic optimisation"), which also cuts turnover costs. "Advanced Futures Trading Strategies" covers the minimum capital per instrument. — [Algorithmic Advantage podcast summary](https://thealgorithmicadvantage.substack.com/p/033-rob-carver-the-comprehensive); [Top Traders Unplugged TTU90](https://www.toptradersunplugged.com/captivate-podcast/ttu90-why-diversification-is-key-ft-robert-carver-author-trader-2of2/); [Harriman House, Advanced Futures Trading Strategies](https://harriman.house/?p=1768352); [Harriman House, Leveraged Trading](https://www.harriman-house.com/leveragedtrading)
- **Forum practice [ANECDOTE]**: one ProRealCode user reports that their most reliable live intraday futures systems are breakouts followed by fading strength (mean reversion). This is one person's experience, not a survey. — [ProRealCode forum](https://www.prorealcode.com/topic/working-strategies-thats-live/)
- **Reddit: no r/algotrading or r/algotradingcrypto threads were retrievable** with the search tool. The only Reddit-derived data is the 2020 Cochran r/CryptoCurrency survey on bot usage and churn (Q2). — [Decrypt](https://decrypt.co/47577/crypto-traders-want-trading-bots-but-dont-trust-them-heres-why)

### Inferences
- Taken together, the evidence suggests the families retail can realistically run with real-money support are:
  - Slow, diversified trend following (CTA evidence).
  - Carry and funding/basis harvesting in crypto (market-neutral fund evidence, though with yield decay and exchange counterparty risk).
  - Plain rebalancing.
  - Above all, cost and leverage minimisation, since the retail studies show costs plus overtrading are what kill accounts.
- High-frequency, discretionary day trading, copy trading and grid bots have either negative large-sample evidence or none at all.
- This is consistent with the existing project memory finding (opusjev backtest: the baseline has no edge, and mean reversion failed out of sample 2022–25).

### Gaps
- Carver's specific small-account rules (minimum capital formulas, his "speed limit" on costs as a fraction of Sharpe ratio, often quoted as about one third of expected SR), Ernie Chan's "retail advantages" argument (capacity, no benchmark constraints), Kevin Davey's walk-forward and incubation process, and Robot Wealth/Quantpedia retail recommendations were **not retrieved**. They should come from the qoppac.blogspot.com, epchan.blogspot.com, robotwealth.com and quantpedia.com primary pages.
- The practitioner consensus from Reddit could not be read directly. An honest summary is "not retrieved," not "no consensus."
