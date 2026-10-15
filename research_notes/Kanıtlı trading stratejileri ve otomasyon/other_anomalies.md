# Other anomalies: momentum/reversal, mean reversion, pairs/stat-arb, seasonality, market making, and publication decay (crypto focus, as of Oct 2026)

Scope note: this covers academic and practitioner evidence. Sources marked [practitioner] are blogs, vendors, or unreviewed code. Sources marked [secondary] are summaries I could not check against the original paper. [IS-only] means no out-of-sample or net-of-cost test was found. Several primary PDFs (SSRN, ResearchGate, Springer, the AUT-hosted Han-Kang-Ryu PDF) returned 403 or a login wall, so some numbers below come from abstracts or summaries.

## Q1. Cross-sectional momentum and short-term reversal in crypto

### Takeaway
At weekly sorts, crypto has a documented cross-sectional momentum factor in-sample (Liu-Tsyvinski-Wu, 2014-2018 data). But later work with realistic frictions finds cross-sectional momentum weak and fragile. Time-series momentum is stronger. Short horizons (about 1 day to 1 week) tend toward reversal, and reversal's gross edge is mostly eaten by costs. Momentum lives at about 1-2 weeks and flips to reversal from about 4 weeks.

### Cited Findings
- **Liu, Tsyvinski & Wu, "Common Risk Factors in Cryptocurrency", Journal of Finance 77(2), 2022, pp. 1133-1177, DOI 10.1111/jofi.13119 (NBER w25882, May 2019).** Three factors (crypto market, size, momentum) capture the cross-section of expected crypto returns. Ten characteristics give significant long-short strategies, and the three-factor model explains all of them. Coins are sorted into quintiles **weekly**. Sample: coins with market cap above $1M, 2014-2018, growing from 109 to 1,583 coins. [IS for the factor discovery; I found no net-of-cost result in the summaries.] — [SUFE newsletter summary](https://academicnewsletter.sufe.edu.cn/info/359095); [Alpha Architect [practitioner/secondary]](https://alphaarchitect.com/factors-investing-in-cryptocurrency/); [NBER WP](https://www.nber.org/papers/w25882.pdf); [SSRN](https://papers.ssrn.com/abstract=3379131)
  - Discrepancy: Alpha Architect cites an *Economic Modelling* 2020 version. The SSRN and JF records support JF 2022. — [Alpha Architect](https://alphaarchitect.com/2022/06/factors-investing-in-cryptocurrency)
- **Dobrynskaya, "Cryptocurrency Momentum and Reversal", Journal of Alternative Investments 26(1), 2023, pp. 65-76.** Sample: coins with market cap above $1M, 2014-2020. Momentum with ranking and holding periods up to 2 weeks is positive and significant. 2-4 weeks is insignificant. From 4 weeks up to 2 years there is significant reversal. — [HSE publication record](https://publications.hse.ru/view/811744977); 2-4-week breakdown only from [Arch Finance blog [secondary]](https://blog.arch.finance/momentum-investing-strategy-and-the-crypto-market)
  - HSE's write-up: a 30% long/short portfolio with a 2-week ranking/holding period earned about 70% per annum (gross; the snippet was truncated). "Starting from four weeks, such portfolios become loss-making." — [HSE news](https://www.hse.ru/en/news/research/559533243.html)
- **Han, Kang & Ryu (Sungkyunkwan), "Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions", SSRN 4675565 (posted about Jan 2024, working paper).**
  - Once transaction costs and daily price swings are accounted for, many momentum portfolios get liquidated. Many with statistically significant returns earn insignificant profits.
  - Evidence for time-series momentum is strong. Evidence for cross-sectional momentum is weak.
  - Momentum is concentrated in large winners. Losers often rebound and cause significant losses on the short leg.
  - The paper also reports reversal rather than momentum at short look-back and holding periods. Costs hit hardest with frequent rebalancing. Six long-short portfolios beat the market on Sharpe after costs.
  — [SSRN abstract](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4675565); [AUT conference PDF](https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf) (both 403 for me; claims come from search-result abstracts)
- "Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets" (2014-2020 data): momentum at about 2-4 weeks, reversal beyond a month. The gross edge per trade is small next to round-trip costs. — [ResearchGate](https://www.researchgate.net/publication/354881251_Up_or_down_Short-term_reversal_momentum_and_liquidity_effects_in_cryptocurrency_markets) [secondary; abstract only]
- **A four-factor crypto model (China Accounting and Finance Review, 2024, DOI 10.1108/CAFR-06-2024-0077)** finds a short-term reversal effect that persists across 1- to 4-week proxies, plus a size effect. I could not see a cost analysis. — [DOI](https://doi.org/10.1108/CAFR-06-2024-0077)
- **"New behaviorally-based cross-sectional reversal portfolios…" (Finance Research Letters, 2025).** Conventional reversal portfolios don't clearly earn positive returns, and profitability depends on the sample period. The paper includes out-of-sample tests on mega-cap coins, 2017-2023. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S154461232501058X)
- **"Cross-sectional interactions in cryptocurrency returns" (International Review of Financial Analysis, 2024/25).** An out-of-sample long-short strategy built on interactions among 40 signals reaches a Sharpe above 1. The authors say it stays profitable at moderate costs, mainly on the long side. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1057521924007415)
- A 2020-2025 study of 8 major coins: time-series momentum earned 31.96% a year and beat cross-sectional momentum risk-adjusted. Cross-sectional momentum had a 55.0% max drawdown and lower profitability. — [Baltic Journal / journals.vu.lt](https://www.journals.vu.lt/BATP/en/article/download/44540/42590/138419) [small universe, short sample]
- A student backtest (2020-2026) found 1-day cross-sectional reversal net-negative once turnover costs were included. — [GitHub prams2104 [practitioner, unreviewed]](https://github.com/prams2104/crypto-momentum-backtest)

### Inferences
- The robust pattern across papers: about 1-2 weeks is momentum (weak cross-sectionally after costs), about 4 weeks and longer is reversal, and daily is reversal that is small relative to costs. Weekly rebalancing beats daily mainly because of turnover cost, not because the signal is better.
- Cross-sectional long-short in crypto needs a short leg. On Binance that means perps for altcoins, with funding costs and borrow limits. Han-Kang-Ryu's finding that losers rebound hard suggests the short leg is where retail long-short momentum dies. A long-only "top winners among large caps" variant is closer to what survives, and that is effectively time-series/trend exposure.
- Micro caps: the early factor papers (market cap above $1M) include very illiquid coins, and their gross premia are likely overstated for anything tradeable on Binance.

### Gaps
- I could not get Han-Kang-Ryu's exact cost assumptions, sample period, or large- versus small-cap tables (PDF returned 403).
- I found no 2025-2026 peer-reviewed out-of-sample paper that specifically re-tests Liu-Tsyvinski-Wu's momentum factor after publication (2022 onward).
- I found no study restricted to Binance-listed perps with funding costs included for cross-sectional momentum.

## Q2. Mean reversion / short-term reversal at intraday and daily horizons

### Takeaway
Intraday reversal in crypto is real and much more pervasive than in US equities. The best 2026 evidence says it is too small to pay for retail costs: about 1.3 bp gross per trade against a 5 bp round trip.

### Cited Findings
- **Kitron & Wengrowicz, "Short-horizon mean reversion in cryptocurrency markets: a matched cross-market measurement", arXiv 2608.21888, 22 Aug 2026.**
  - At 15-minute horizons, 90% of 183 Binance pairs show significant directional reversal, against 2.7% of 187 US stocks and ETFs. This holds in every coin-year since 2021.
  - The effect is about direction, not size: lag-1 autocorrelation is near zero for majors, but betting against the previous candle captures it.
  - Reversal is concentrated after moves driven by aggressive taker orders, consistent with compensated liquidity provision.
  - **The gross edge peaks around 1.3 bp per trade against 5 bp round-trip cost**, so it is not tradeable at typical spot costs.
  - Robustness: an artifact battery, a permutation null, and a frozen 6-month holdout.
  — [arXiv abstract](https://arxiv.org/abs/2608.21888)
- **Padyšák & Vojtko (Quantpedia), "Seasonality, Trend-following, and Mean reversion in Bitcoin", SSRN 4081000, 2015-2021 Gemini data.** BTC is trend-following at local maxima and mean-reverting at local minima (10- to 50-day lookbacks, with 10 days working best). The composite MIN10/MAX10 strategy is tested only at the 10-day setting, and no costs are reported. [IS-only] — [Quantpedia [practitioner]](https://quantpedia.com/strategies/intraday-seasonality-in-bitcoin)

### Inferences
- Short-term reversal behaves like a liquidity-provision premium. Taking it with market orders pays the spread you are trying to earn. It is only plausibly capturable with maker (limit) orders, which turns it into a market-making problem (see Q5).
- At daily horizons, cross-sectional reversal results (Q1) are sample-dependent and cost-sensitive. Treat daily mean reversion as unproven net of costs. The user's own memory note says MR failed out-of-sample over 2022-25, which is consistent with this.

### Gaps
- I did not retrieve equity short-term reversal net-of-cost literature (e.g. Jegadeesh 1990, Lehmann 1990, Avramov et al.) in this pass.

## Q3. Pairs trading / cointegration stat-arb in crypto, and equity decay

### Takeaway
Crypto pairs trading looks good gross and in-sample, but underperforms the equity benchmark literature, is unstable across sub-periods, and is cost-dominated at high frequency. Equity pairs-trading profitability has trended down since the 1990s and now mainly pays during crises.

### Cited Findings
- **Fil & Kristoufek, "Pairs Trading in Cryptocurrency Markets", IEEE Access 8 (2020), 172644-172651, DOI 10.1109/ACCESS.2020.3024619.** The strategy can work under certain conditions but strongly underperforms the benchmark literature. Distance and cointegration methods behave quite differently across sub-periods. The sample is small and the period short (critique in a later thesis). — [EUR thesis citing it [secondary]](https://thesis.eur.nl/pub/67552/Thesis-Pairs-trading-.pdf); [ResearchGate](https://www.researchgate.net/publication/346845365_Pairs_Trading_in_Cryptocurrency_Markets)
- A comparative crypto pairs study (distance vs cointegration vs a Hurst/GHE hybrid) found GHE pair selection consistently best out-of-sample. Costs and execution lag matter a great deal. Binance fees were modeled at 10/10 bps maker/taker, falling to 2/4 bps at the top VIP tier. — [ResearchGate (comparative study)](https://www.researchgate.net/publication/376180709_Pairs_trading_in_cryptocurrency_markets_A_comparative_study_of_statistical_methods) [secondary]
- **"Copula-based trading of cointegrated cryptocurrency pairs", Financial Innovation (Springer), 2025.** One approach posted large gross returns on 5-minute data but went **net negative** after costs in both tests. A level-based copula variant stayed net positive with lower costs and drawdowns. — [Springer](https://link.springer.com/article/10.1186/s40854-024-00702-7)
- Adaptive copula pairs with a market overlay (Quantitative Finance and Economics, 2026): the authors stress that net performance depends on transaction costs and design. — [AIMS Press](https://www.aimspress.com/article/doi/10.3934/QFE.2026016?viewType=HTML)
- Critique of an earlier dynamic-cointegration crypto thesis: profitability claims are unreliable because of ignored costs and selection bias. — [arXiv 2109.10662](https://arxiv.org/pdf/2109.10662/1000)
- An open-source walk-forward test of Binance 1-minute pairs with FDR control for multiple testing, at 0.10% cost per unit traded ("Does cointegration pairs trading survive multiple testing?"). I did not verify the results. — [GitHub [practitioner]](https://github.com/Ayansheikh034/crypto-pairs-trading)
- **Do & Faff, "Does Simple Pairs Trading Still Work?", Financial Analysts Journal 66(4), 2010, pp. 83-95.** Confirms a continuing **downward trend** in pairs-trading profitability (Gatev-Goetzmann-Rouwenhorst distance method). It still performs strongly in prolonged turbulence, including the GFC. — [IDEAS/RePEc](https://ideas.repec.org/a/taf/ufajxx/v66y2010i4p83-95.html); [CFA Institute](https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/does-simple-pairs-trading-still-work)
- "Gold Standard Pairs Trading Rules: Are They Valid?" (arXiv 2010.01157) corroborates Do & Faff: very strong in crises, including Covid-19, but generally lags the market benchmark otherwise. — [arXiv](https://arxiv.org/pdf/2010.01157)
- An equity case study, PEP/KO (arXiv 2609.35359, 2026): the pair was cointegrated in-sample, but mean reversion in the spread weakened and the strategy failed out-of-sample. — [arXiv](https://arxiv.org/html/2609.35359)

### Inferences
- Crypto majors are highly co-moving (one dominant BTC factor), so many "cointegrated" pairs are spurious or break in regime shifts. Multiple-testing control (FDR) at pair selection is essential (see Q6).
- For a retail Binance bot at hourly to daily frequency, pairs trading is implementable mechanically (both legs on USDⓈ-M perps). The expected edge is thin. At taker-fee level, 4 legs per round trip (about 4 × 4-5 bp) roughly cancel typical spread-reversion profits unless holds are long.

### Gaps
- I could not access Fil & Kristoufek's frequency-specific results (daily vs hourly vs 5-minute) or their net Sharpe figures.
- Leung & Nguyen (2019) was not retrieved.
- I found no peer-reviewed post-2022 out-of-sample crypto pairs study on Binance perps that includes funding costs.

## Q4. Seasonality and calendar/intraday effects in crypto

### Takeaway
Time-of-day effects are the best-documented calendar effects in crypto, tied to the opening hours of traditional markets. The famous BTC "overnight" (22:00-00:00 UTC) effect is in-sample with no costs. Day-of-week effects appear to collapse into a single Sunday-night hour once intraday fixed effects are controlled for. Funding-settlement effects are documented for spreads, not returns.

### Cited Findings
- **BTC overnight seasonality (Padyšák & Vojtko, SSRN 4081000; Gemini data 2015-2021).** The rule buys BTC at 22:00 UTC and holds 2 hours. Returns at the 22:00 and 23:00 UTC hours are positive and significant at 5%. Reported performance: about 33% annual return, 20.93% volatility, -34.04% max drawdown, Sharpe 1.58. **No transaction costs reported.** Weak in bear markets. [IS-only; out-of-sample implementation section showed no results.] — [Quantpedia [practitioner]](https://quantpedia.com/strategies/intraday-seasonality-in-bitcoin)
- **"The crypto world trades at tea time: intraday evidence from centralized exchanges across the globe", Review of Quantitative Finance and Accounting (Springer), 2024.** Returns are lowest in the early-morning UTC hours and highest in the early afternoon and evening UTC. Patterns are not driven only by trading halts. — [Springer](https://link.springer.com/article/10.1007/s11156-024-01304-1) (paywalled; claims from abstract snippet)
- **Jasiak & Zhong, Energy Economics, 2024.** Native coins and tokens share common intraday periodicity set by NYSE, LSE and Hang Seng opening hours. — [search snippet; IDEAS listing](https://ideas.repec.org/a/eee/reveco/v96y2024ipbs1059056024006506.html) [secondary]
- Jahanshahloo, Corbet & Oxley ("Seeking Sigma"): NYSE trading sessions lead Bitcoin activity. The effects strengthened over time but weakened at weekends. — via [Quantpedia related papers [secondary]](https://quantpedia.com/strategies/intraday-seasonality-in-bitcoin)
- **"Are Day-of-the-Week Effects in Cryptocurrencies Real? Intraday Evidence from Active and Less Active Cryptocurrencies" (SSRN, May 2026; also Aalipour, Mehdian & Rezvanian per Quantpedia).** At hourly frequency, day-of-week effects are **entirely concentrated in 23:00-00:00 UTC on Sunday night**. Controlling for intraday fixed effects removes all weekly-seasonal significance. Effects are limited to a few intraday intervals and largely absent in less active coins. No costs or out-of-sample tests were mentioned. — [mlquants Substack review [secondary]](https://mlquants.substack.com/p/are-day-of-the-week-effects-in-cryptocurrencies); [Quantpedia](https://quantpedia.com/strategies/intraday-seasonality-in-bitcoin)
- "A new perspective of the day-of-the-week effect on Bitcoin returns: an event-study hourly approach" (Oeconomia Copernicana). — [oeconomia.pl](https://oeconomia.pl/index.php/oc/article/view/2091) (not read)
- "Turn-of-the-candle effect in Bitcoin returns" (PLOS/PMC, 2023): well-defined intraday seasonal patterns around the turn of hourly candles, plus a simple trading rule. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10015199/)
- **Funding settlement:** in crypto perpetuals, intraday **spread** patterns are significant and tied to funding settlement, peaking about 2 hours after standard settlement times. Based on 9.1M hourly funding observations across 26 exchanges, 14 Nov 2025 to 13 Jan 2026 (very short window). — [MDPI IJFS 14(5):103, 2026](https://www.mdpi.com/2227-7072/14/5/103)
- Scheduled FOMC statements create intraday macro event risk in crypto (Finance Research Letters, 2026). — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1544612326006021) (abstract only)

### Inferences
- The day-of-week effect appears to be an artifact of one hour (Sunday 23:00 UTC), which overlaps the 22:00-00:00 UTC overnight window. These are likely one phenomenon: the US evening/Asia open window, with the weekend-to-Monday transition as one instance.
- At hourly frequency a 2-hour hold costs a full round trip each day. At Binance retail taker fees (about 0.1% spot, about 0.05% perps taker, per published schedules, to be verified), 365 round trips a year cost roughly 18-73% annually before slippage. That would erase much or all of a 33% gross return. The overnight-BTC rule is implementable but almost certainly unprofitable net at retail taker cost. It is only plausible with maker fills or VIP fees.
- Since the BTC overnight effect was popularised by Quantpedia (2022), the McLean-Pontiff logic (Q6) predicts post-publication decay. I found no independent 2023-2026 out-of-sample check.

### Gaps
- No verified post-2021 out-of-sample test of the 22:00-00:00 UTC BTC effect.
- No direct study of *returns* (not spreads) around Binance funding timestamps (00/08/16 UTC).
- Turn-of-month and options-expiry (Deribit Friday 08:00 UTC) effects in crypto: no reliable source found in this pass.
- No crypto-specific "overnight vs intraday" (US-session) return decomposition with costs found.

## Q5. Market making and liquidity provision for retail

### Takeaway
Retail market making on Binance is technically possible (Hummingbot), but structurally disadvantaged. At standard tiers there is no maker rebate, fills are adversely selected by faster traders, and inventory builds during trends. Rebates exist only in invite/volume-gated liquidity-provider programs. I found no rigorous evidence that retail market-making bots are profitable.

### Cited Findings
- Binance maker/taker fees depend on VIP level. Futures tiers are generally lower than spot, and futures VIP volume requirements are about 5× spot. Paying fees in BNB gives a 10% discount. — [Binance support](https://www.binance.com/es/support/articles/360033544231)
- Binance ran a **USDⓈ-M Futures Liquidity Provider Program (2023)** paying **negative maker fees (rebates)** to top quoters in 5 tiers, qualified by maker volume share or quoting rank. I found no confirmation it is current in 2026. A 2025 page refers to a USDC-margined perps LP program, with terms not retrieved. — [Binance Square](https://www.binance.com/en/square/post/583227)
- Third-party 2026 fee guides cite a standard futures maker fee of about 0.02%. — [TradersUnion [practitioner/secondary]](https://tradersunion.com/brokers/crypto/view/binance/futures-fees/)
- Binance.US launched a separate maker-rebate program (2022) for selected participants. — [The Block](https://www.theblock.co/post/169646/binance-us-launches-rebate-and-rewards-program-to-boost-liquidity)
- Hummingbot "pure market making" places bids and asks around mid and refreshes them on a timer, and is spot-only. Perpetual market making is a separate strategy. — [Hummingbot docs [practitioner]](https://hummingbot.org/strategies/pure-market-making)
- Pure market making carries adverse-selection risk (informed traders pick off stale quotes) and builds directional inventory during trends. — [The Ledger Mind [practitioner]](https://theledgermind.com/market-making-bot-design/)
- Slower traders are adversely selected by faster RL-based market makers, and the effect grows as markets get more competitive. — [arXiv 2510.27334 (2025)](https://arxiv.org/html/2510.27334v1)
- Supporting evidence that liquidity provision earns the short-term reversal: Kitron & Wengrowicz (2026) find 15-minute reversal concentrated after aggressive taker moves, consistent with compensated liquidity provision. — [arXiv 2608.21888](https://arxiv.org/abs/2608.21888)
- Hummingbot's community material (interviews with "liquidity miners") shows that much historical retail MM profit came from external liquidity-mining rewards, not spread capture. — [Hummingbot blog [practitioner]](https://hummingbot.org/blog/interview-with-liquidity-miner-dominator008/) [interpretation of the source; verify]

### Inferences
- The economics: a retail account at VIP0 pays a positive maker fee, so spread capture on liquid pairs (BTC/ETH spreads around 1 tick, about 0.1 bp) is impossible. Only wide-spread, illiquid alts leave room, and those carry the worst adverse selection and inventory risk. Residential latency (to Tokyo/AWS) adds to the picking-off.
- A realistic retail use of "maker" is to *execute* other signals with post-only limit orders to cut costs, not to run market making as a standalone strategy.

### Gaps
- No quantitative study of retail Hummingbot profitability found.
- Current (Oct 2026) Binance VIP maker/taker table and LP program terms not verified from the live page.

## Q6. Publication decay and backtest overfitting

### Takeaway
Published anomalies lose about a quarter of their return out-of-sample (statistical bias) and more than half after publication. The bar for a new factor should be t > 3. Backtest selection should be checked with PBO/CSCV. Every crypto anomaly above should be discounted accordingly, especially the in-sample-only ones.

### Cited Findings
- **McLean & Pontiff, "Does Academic Research Destroy Stock Return Predictability?", Journal of Finance 71(1), 2016.** Across 97 predictors, portfolio returns are **26% lower out-of-sample** (pre-publication, after the sample ends) and **58% lower post-publication**. The approximately 32-point gap is attributed to publication-informed trading. The out-of-sample drop is an upper bound on data mining. The working-paper version reported 25% and 56%. — [Gwern-hosted PDF](https://www.gwern.net/doc/economics/2016-mclean.pdf); [SUFE summary](https://academicnewsletter.sufe.edu.cn/info/359722); [CXO Advisory](https://www.cxoadvisory.com/big-ideas/effects-of-market-adaptation)
- **Harvey, Liu & Zhu, "…and the Cross-Section of Expected Returns", Review of Financial Studies 29(1), 2016.** Hundreds of factors have been tested, so new factors need **t > 3.0**, not 2.0. — [SUFE summary](https://academicnewsletter.sufe.edu.cn/info/353765) (the commonly cited count of 316 factors was not verified in this pass)
- **Bailey, Borwein, López de Prado & Zhu, "The Probability of Backtest Overfitting", Journal of Computational Finance (2016/17; SSRN 2326253).** Introduces PBO and combinatorially symmetric cross-validation (CSCV). Standard hold-out tests are unreliable for investment backtests. — [SSRN](https://papers.ssrn.com/abstract=2326253); [Risk.net](https://www.risk.net/2471206); [R `pbo` vignette](https://archive.linux.duke.edu/cran/web/packages/pbo/vignettes/pbo.html)
- Bailey, Borwein, López de Prado & Zhu, "Pseudo-Mathematics and Financial Charlatanism" (Notices of the AMS, 2014): the more configurations tried, the higher the probability that the backtest is overfit. — [WMU ScholarWorks](https://scholarworks.wmich.edu/math_pubs/40/)
- Quantpedia's in-sample vs out-of-sample analysis of trading strategies (practitioner replication of decay). — [Quantpedia [practitioner]](https://quantpedia.com/in-sample-vs-out-of-sample-analysis-of-trading-strategies/)

### Inferences
- Applying McLean-Pontiff haircuts mechanically, Dobrynskaya's about 70% gross 2-week momentum or the BTC overnight Sharpe of 1.58 should be expected at roughly half or less after publication, before costs. Crypto markets have fast-adapting, bot-heavy participants, so decay may be faster than in equities. That is a speculation; no crypto-specific decay study was found.
- A practical gate for this project: require t > 3 in-sample, a PBO estimate below about 0.2 across the parameter grid, a walk-forward with real Binance fees and funding, and a frozen holdout, as Kitron & Wengrowicz did.

### Gaps
- No crypto-specific McLean-Pontiff-style study of post-publication decay found.
