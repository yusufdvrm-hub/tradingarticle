# Trend Following / Time-Series Momentum (TSMOM) and CTA Evidence, Applied to Crypto

Research date: 2026-10-15. Labels: **[FACT]** = published number or claim from the cited source; **[INTERP]** = my reading; **[IS]** = in-sample or backtest only, no live record. Many figures here come from secondary summaries (CXO Advisory, Top Traders Unplugged, Hedgeweek, LPL) because primary PDFs were paywalled or could not be parsed in this session. Each case is flagged.

## 1. Academic evidence for TSMOM: lookbacks, sizing, decay

### Takeaway
Diversified futures trend following (1-, 3- and 12-month lookbacks, each position scaled to a volatility target) has positive returns over very long samples. Hurst-Ooi-Pedersen report positive net returns in every decade since 1880 and an average per-asset Sharpe of about 0.4. Huang-Li-Wang-Zhou (JFE 2020) show that asset-by-asset predictability is statistically weak, and that much of the profit can be matched by a strategy using historical mean returns. The edge is modest, comes from diversification, and is not a strong per-asset signal.

### Cited Findings
- [FACT] Hurst, Ooi & Pedersen, "A Century of Evidence on Trend-Following Investing" (AQR; June 2017 version):
  - Sample: 1880–2016, 67 markets (29 commodities, 11 equity indexes, 15 bond indexes, 12 currency pairs).
  - Signal: equal blend of 1-, 3- and 12-month excess-return trend signals.
  - Sizing: each position targets 10% annualized volatility, estimated from rolling 3-year windows.
  - Fees: returns are net of a simulated 2/20 fee plus estimated transaction costs (roll costs excluded). — [CXO Advisory summary, 2017-07-17](https://www.cxoadvisory.com/momentum-investing/trend-following-with-intrinsic-momentum-over-the-very-long-run)
- [FACT] Same paper:
  - Positive net returns in every decade since 1880, and each lookback is positive on its own in every decade.
  - Per-asset gross Sharpe ranges from under 0.1 to over 1.0, all positive, with an average of about 0.4. The CXO page is inconsistent on whether 0.4 is net or gross.
  - Positive in 8 of the 10 worst 60/40 drawdowns.
  - Adding a one-month skip degrades results, most of all for short lookbacks. — [CXO Advisory](https://www.cxoadvisory.com/momentum-investing/trend-following-with-intrinsic-momentum-over-the-very-long-run); [AQR abstract page](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing)
- [FACT] The AQR abstract says the paper considers the effect of growing assets in the strategy and of rising cross-market correlations since the credit crisis, which are the usual explanations for weak post-2008 performance. — [AQR](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing)
- [FACT] Huang, Li, Wang & Zhou, "Time series momentum: Is it there?", *Journal of Financial Economics* 135(3), March 2020:
  - Data: 55 futures and forwards, 1985–2015.
  - Asset-by-asset regressions of next-month return on the past 12-month return show little predictability, in-sample or out-of-sample.
  - The pooled t-statistic falls below bootstrap critical values.
  - The TSMOM strategy is profitable, but performs about the same as a strategy based on historical mean returns. — [WUSTL profile](https://profiles.wustl.edu/en/publications/time-series-momentum-is-it-there/); [Alpha Architect](https://alphaarchitect.com/2020/03/an-empirical-challenge-for-trend-following/)
- [FACT] Alpha Architect's reading is that the paper does not claim "no predictability", only that predictability is not a simple constant 12-month rule. — [Alpha Architect](https://alphaarchitect.com/2020/03/an-empirical-challenge-for-trend-following/)

### Inferences
- [INTERP] The standard academic design is a multi-speed blend (1/3/12 months), volatility-targeted sizing at the instrument level, monthly or more frequent rebalancing, and long-short positions. Blending lookbacks is the usual defence against picking a single parameter that happened to fit.
- [INTERP] The Huang et al. critique matters for crypto. With only a few liquid assets, there is no wide cross-section to diversify over. The weak per-asset signal is then all you have, and a strategy can look good mostly because crypto's mean return was high.

### Gaps
- I could not verify Moskowitz-Ooi-Pedersen (JFE 2012) specifics, such as the instrument count, sample period or the reversal beyond 12 months. The commonly cited version is 58 instruments, 1985–2009, with a 12-month lookback and 1-month hold, but this comes from memory and is unverified here.
- I did not fetch Baltas & Kosowski or Babu et al. ("You can't always trend when you want", JPM 2020). I have no verified numbers from either.
- I could not parse the Hurst PDF (no PDF tooling available), so its annualized net return and volatility are not recorded here.

## 2. Practitioner record: SG Trend, SG CTA and Barclay indices

### Takeaway
Live CTA records show trend following is lumpy. It had a weak 2010s (gap: no verified figures), a large 2022 (+27.3% for the SG Trend Index), negative to muted results in 2023 and H1 2025, and a modest recovery to roughly +2.4% for 2025. In 2026 it was up about 7.9% through July. The long-run live CAGR is about 5.2–5.3%, with a maximum drawdown of about 20.6%. That is far below backtest Sharpe ratios.

### Cited Findings
- [FACT] 2022: the SG Trend Index returned +27.3%, the best of the SG CTA indices, and 61.3% over four years. — [Hedgeweek](https://www.hedgeweek.com/trend-followers-turn-leaders-ctas-deliver-record-returns-2022/); [The Full FX](https://thefullfx.com/year-end-drop-fails-to-dampen-stellar-2022-for-trend-followers/)
- [FACT] 2023: the broader SG CTA Index lost almost 3%. I found no verified full-year 2023 figure for the SG Trend Index. — [StoneX](https://stonex.com/en/thought-leadership/ctas-on-course-for-positive-january-returns)
- [FACT] 2024: the SG Trend Index was +12.23% YTD through March 2024 and +6.07% YTD through July 2024. I found no verified full-year figure. — [TTU March 2024](https://www.toptradersunplugged.com/?p=14551); [TTU August 2024](https://www.toptradersunplugged.com/trend-following-performance-report-august-2024/)
- [FACT] 2024 index constituents: AQR Managed Futures replaced Winton's trend program, and the asset cut-off was $4.78bn. The index tracks the 10 largest trend CTAs. — [Hedgeweek, via search summary](https://www.hedgeweek.com/sg-prime-services-releases-the-cta-indices-constituents-for-2026/)
- [FACT] 2025 (all SG Trend Index; secondary source, Top Traders Unplugged):
  - −2.27% YTD through September 2025.
  - +1.41% in October.
  - +1.92% in December, with a trailing 12-month return of +2.39%.
  - Since-inception CAGR of about 5.2–5.3% and a maximum drawdown of 20.61%. — [TTU Oct 2025](https://www.toptradersunplugged.com/trend-following-performance-report-october-2025/); [TTU](https://www.toptradersunplugged.com/?p=20381)
- [FACT] 2025: the Barclay CTA Index was provisionally +3.16%. Trend-following funds were described as having lost money in H1 2025. — [TTU](https://www.toptradersunplugged.com/?p=20381); [Alternatives Watch, 2025-07-01](https://www.alternativeswatch.com/2025/07/01/trend-following-hedge-funds-loss-h1-societe-generale-index/)
- [FACT] 2026:
  - The SG Trend Index entered August 2026 up 7.9% YTD, against +3.2% for the SG Short-Term Traders Index. LPL describes the medium-term cohort as having reversed its 2025 pattern. — [LPL "A Tale of Two CTAs"](https://www.lpl.com/research/blog/a-tale-of-two-ctas.html)
  - The SG CTA Index was reportedly +15.7% through Q3 2026, against +11.7% for the S&P 500, driven by long USD, long crude and short Treasurys. — [Alpha Maven / HedgeCo](https://www.alpha-maven.com/news/hedge-fund/trend-following-hedge-funds-returned-157-through-the-third-quarter-outpacing-the-sampp-500)

### Inferences
- [INTERP] A live CAGR of about 5% with a 20% maximum drawdown implies a live Sharpe in roughly the 0.3–0.5 range. That is consistent with the Hurst average of about 0.4, and far below the 1.0+ Sharpe ratios typical of published backtests.
- [INTERP] Returns cluster in a few crisis or regime-shift years (2008, 2014, 2022). Several flat or losing years in a row are normal, not a sign the strategy is broken.

### Gaps
- No verified SG Trend Index annual figures for 2010–2019, 2023 full year or 2024 full year. No BTOP50 figures found.
- The full-year 2025 SG Trend figure is inferred from the trailing 12-month return in the December report. It is not an official SG publication.

## 3. Crypto-specific evidence

### Takeaway
Crypto shows stronger trend or momentum than traditional assets in published studies. Liu & Tsyvinski (RFS 2021) find time-series momentum at daily and weekly horizons. Detzel et al. find price-to-moving-average ratios forecast daily BTC returns in and out of sample. Zarattini-Pagani-Barbon (2025) report net Sharpe above 1.5 for a Donchian ensemble on the top 20 coins. Almost all of this is backtest evidence. Much of the gain comes from sitting out crashes, which makes the long or flat version the robust part, rather than profits from shorting.

### Cited Findings
- [FACT] Liu & Tsyvinski, "Risks and Returns of Cryptocurrency" (NBER WP 24877, 2018; *Review of Financial Studies* 34(6), 2021):
  - Reports "a strong time-series momentum effect" in BTC, XRP and ETH, and finds that investor attention proxies forecast returns.
  - Per a CXO summary, momentum shows up at daily and weekly frequencies and is weaker for ETH.
  - Weekly example (CXO, unverified against the paper): average next-week BTC return of 11.2% for the top fifth of last-week returns versus 2.6% for the bottom fifth. — [SSRN](https://papers.ssrn.com/abstract=3226806); [NBER PDF](https://www.nber.org/system/files/working_papers/w24877/w24877.pdf); [CXO summary](https://www.cxoadvisory.com/currency-trading/crypto-asset-risks-and-returns/)
- [FACT] Detzel, Liu, Strauss, Zhou & Zhu, "Learning and predictability via technical analysis: evidence from bitcoin and stocks with hard-to-value fundamentals" (*Financial Management*, 2021; working paper 2018):
  - Ratios of price to moving average forecast daily BTC returns in and out of sample.
  - MA-based strategies produce economically significant alpha and Sharpe gains over buy-and-hold.
  - Tested rules: hold BTC when price is above the 5/10/20/50/100-day SMA, otherwise hold T-bills. — [WUSTL](https://profiles.wustl.edu/en/publications/learning-and-predictability-via-technical-analysis-evidence-from-/); [CXO](https://www.cxoadvisory.com/currency-trading/timing-bitcoin-with-smas/)
- [FACT] Zarattini, Pagani & Barbon, "Catching Crypto Trends: A Tactical Approach for Bitcoin and Altcoins" (Swiss Finance Institute RP 25-80; revised 2025-04-09; SSRN 5209907):
  - Results: net-of-fees Sharpe above 1.5 and annualized alpha of 10.8% versus BTC, for a rotating portfolio of the 20 most liquid coins.
  - Data: survivorship-bias-free, January 2010 to mid-March 2025, 21,616 assets.
  - Universe filter: listed at least 1 year, with median 30-day daily volume of at least $2M.
  - The authors also propose a portfolio technique that reduces transaction costs. — [abarbon.com](https://abarbon.com/papers/catching-crypto-trends); [IDEAS/RePEc](https://ideas.repec.org/p/chf/rpseri/rp2580.html); [CXO summary, 2025-05-29](https://www.cxoadvisory.com/technical-trading/crypto-asset-trend-following-strategies/) [IS]
- [FACT] Man AHL, "In Crypto We Trend" (2024-12-19):
  - Signals: MA crossover (e.g. 50/200-day) and breakout models, with volatility scaling and equal risk across coins.
  - Costs modelled: transaction costs, shorting costs and liquidity constraints.
  - Peak Sharpe comes at about 10–15 coins for MA crossover and about 10 coins for breakouts. Faster models need fewer coins.
  - Average pairwise correlation is about 0.6, and liquidity falls off sharply after the top 15 coins by ADV.
  - Sharpe values appear only in charts, described as "higher than expected". — [Man Group](https://www.man.com/insights/in-crypto-we-trend) [IS]
- [FACT] A crypto TSMOM study (AUT working paper; date not shown):
  - Buying when the 28-day return is in the top third of its history gives Sharpe 1.51, against 0.84 for the market.
  - Gains come mainly from reduced downside risk and are strongest in bull markets.
  - Selling on negative momentum yields negative profits in most cases. — [AUT ACFR PDF](https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf) [IS]
- [FACT] Shen, Urquhart & Wang, "Bitcoin intraday time-series momentum" (*Financial Review*, 2022):
  - The first half-hour return predicts the last half-hour return.
  - Intraday momentum trading yields economic gains, especially in downturns.
  - The authors attribute it to liquidity provision rather than late-informed trading. — [Birmingham research portal](https://research.birmingham.ac.uk/en/publications/bitcoin-intraday-time-series-momentum/); [Reading eprint](https://reading-9.eprints-hosting.org/100181/3/21Sep2021Bitcoin%20Intraday%20Time-Series%20Momentum.R2.pdf)
- [FACT] Bui & Nguyen, arXiv 2602.11708 (2026-02-12):
  - Design: 6-hour-bar trend following on 150+ pairs, with monthly adaptive selection, a volatility-calibrated trailing stop and a 70/30 long/short split.
  - Claimed 2022–2024 out-of-sample result: Sharpe 2.41, maximum drawdown −12.7%, Calmar 3.18.
  - A search summary says the model uses a 4 bps taker fee plus slippage and funding, and that the 1-month TSMOM benchmark had Sharpe 0.65. I could not confirm either detail on the abstract page. — [arXiv](https://arxiv.org/abs/2602.11708) [IS; single unrefereed preprint with many tuned components]
- [FACT] A Monash Centre for Financial Studies project reports that short-lookback crypto trend strategies can show high Sharpe ratios, but frequent rebalancing costs erode profits. — [Monash](https://www.monash.edu/business/mcfs/our-research/all-projects/investment-strategy/trend-following-strategies-for-crypto-investors)
- [FACT] A cointegrated-pairs crypto study (a different strategy class) shows hourly and 5-minute versions with about 2,000–31,000 trades, where transaction costs consumed most or all of the gross return. — [Financial Innovation table](https://jfin-swufe.springeropen.com/articles/10.1186/s40854-024-00702-7/tables/7)
- [FACT] Grobys, Kolari, Sandretto, Shahzad & Äijö, "Cryptocurrency momentum has (not) its moments" (2025) covers volatility scaling and tail risk in crypto momentum. The full text was blocked, so I have no findings from it. — [Univ. Vaasa repository](https://osuva.uwasa.fi/items/2b92e591-acb3-445f-b33d-1a943a8972f5/full)

### Inferences
- [INTERP] The evidence is consistently positive at daily to weekly horizons with multi-week to multi-month lookbacks: Liu-Tsyvinski at daily and weekly, Detzel at 5–100-day SMAs, and Zarattini lookbacks of 5–360 days.
- [INTERP] Hourly or faster evidence is thin. It is either intraday-seasonality momentum (Shen et al.) or single preprints with heavy tuning. The Monash note and the pairs-trading cost table suggest that, at hourly frequency, costs (fees, spread and funding) consume most of the edge.
- [INTERP] Expect the edge to exist at daily or weekly horizons and to be fragile below about 4–6 hours. This is an inference; I found no clean daily-versus-hourly comparison on Binance.
- [INTERP] Long-only versus long-short asymmetry: the AUT result (shorting on negative momentum loses) and Detzel's long-or-cash design both suggest the robust crypto edge is crash avoidance in a long-or-flat strategy. Shorting adds funding costs and squeeze risk, and on Binance perps a short position also earns or pays funding.

### Gaps
- I found no verified 2023–2026 out-of-sample (post-publication) evaluation of a simple BTC/ETH MA or Donchian rule with costs, beyond the Bui & Nguyen preprint.
- I did not verify Corbet et al. or the other Grobys et al. MA-rule papers.
- No study gave typical annual turnover numbers for crypto trend systems.

## 4. Implementable rule specs and reported net results

### Takeaway
The best-documented rule for retail crypto is the Zarattini-Pagani-Barbon Donchian-style ensemble. It uses close-above-N-day-max breakouts across 9 lookbacks, a trailing midpoint stop, 25% volatility targeting from 90-day volatility and a 2x leverage cap, and has been stress-tested at 10–50 bps cost. Simpler alternatives are an SMA filter (Detzel: long above the 5–100-day SMA, else cash) and a 50/200 MA crossover with volatility scaling (Man AHL).

### Cited Findings
- [FACT] Zarattini-Pagani-Barbon ensemble specification:
  - **Entry:** daily close above the maximum close of the last N days, for N = 5, 10, 20, 30, 60, 90, 150, 250 and 360.
  - **Exit:** a daily trailing stop equal to the higher of the prior stop and the midpoint of the N-day maximum and minimum closes.
  - **Sizing:** 25% annualized target volatility per position, using 90-day standard deviation, with leverage capped at 200%.
  - **Ensemble:** equal-weighted portfolio of open positions across all lookbacks, rebalanced daily.
  - **Costs:** tested at 0.10%, 0.25% and 0.50% per trade. — [CXO summary](https://www.cxoadvisory.com/technical-trading/crypto-asset-trend-following-strategies/)
- [FACT] Its headline net result is Sharpe above 1.5 and alpha of 10.8% per year versus BTC, for the top-20 rotation. — [abarbon.com](https://abarbon.com/papers/catching-crypto-trends) [IS]
- [FACT] Detzel et al. rule: hold BTC when price is above its N-day SMA (N = 5, 10, 20, 50, 100), otherwise hold T-bills. — [CXO](https://www.cxoadvisory.com/currency-trading/timing-bitcoin-with-smas/)
- [FACT] Man AHL rules: 50/200-day MA crossover, or full-position breakouts through support or resistance. Both use volatility scaling and equal risk across about 10–15 coins. — [Man Group](https://www.man.com/insights/in-crypto-we-trend)
- [FACT] Academic TSMOM baseline (Hurst et al.): sign of the 1/3/12-month return, each sized to 10% volatility. — [CXO](https://www.cxoadvisory.com/momentum-investing/trend-following-with-intrinsic-momentum-over-the-very-long-run)

### Inferences
- [INTERP] For a retail Binance system, a defensible baseline is:
  - **Universe:** BTC and ETH plus the top 10–15 liquid perpetual or spot pairs (Man AHL's coin count).
  - **Signal:** a multi-lookback breakout or SMA ensemble on daily closes.
  - **Exit:** exit on signal reversal or the midpoint trailing stop, not tight percentage stops.
  - **Sizing:** inverse-volatility at the position level, with a portfolio cap.
  - **Direction:** long or flat first, testing shorts separately with perp funding included.
- [INTERP] Binance taker fees of about 0.04–0.10% per side sit at the low end of Zarattini's cost grid. A daily-rebalanced ensemble stays plausible there, but slippage on altcoins outside the top 15 is the binding cost.

### Gaps
- Exact net CAGR and maximum drawdown for the Zarattini ensemble at each cost level were paywalled. The SSRN 5209907 PDF is needed.

## 5. Failure modes: whipsaw, crowding, decay, asymmetry

### Takeaway
The main documented risks are long flat or whipsaw stretches (2023 and H1 2025 for CTAs), weak per-asset statistical significance (Huang et al.), parameter fragility (hence ensembles), high crypto cross-correlation (about 0.6) limiting diversification, and losses on the short side in crypto.

### Cited Findings
- [FACT] CTA trend lost in H1 2025, was rattled by the February 2025 reversal, and had a muted 2023. — [Alternatives Watch, 2025-03-03](https://www.alternativeswatch.com/2025/03/03/trend-following-hedge-funds-rattled-by-februarys-market-reversal-societe-generale-sg-index/); [Alternatives Watch, 2025-07-01](https://www.alternativeswatch.com/2025/07/01/trend-following-hedge-funds-loss-h1-societe-generale-index/); [StoneX](https://stonex.com/en/thought-leadership/ctas-on-course-for-positive-january-returns)
- [FACT] Higher assets under management and higher cross-market correlation since 2008 are named as challenges. — [AQR](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing)
- [FACT] TSMOM shows weak statistical evidence per asset and matches a historical-mean benchmark. — [Alpha Architect](https://alphaarchitect.com/2020/03/an-empirical-challenge-for-trend-following/)
- [FACT] Crypto pairwise correlation is about 0.6. — [Man Group](https://www.man.com/insights/in-crypto-we-trend)
- [FACT] Shorting on negative crypto momentum mostly loses money. — [AUT](https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf)
- [FACT] Short-lookback strategies lose their edge to rebalancing costs. — [Monash](https://www.monash.edu/business/mcfs/our-research/all-projects/investment-strategy/trend-following-strategies-for-crypto-investors)

### Inferences
- [INTERP] This connects to the project memory finding (opusjev backtest: the baseline has no edge, and mean reversion failed out-of-sample over 2022–25). Trend is the better-documented direction in crypto, but any test should:
  - use walk-forward validation;
  - include fees, slippage and funding;
  - compare against BTC buy-and-hold and against a "long when the historical mean is positive" null, following Huang et al.
- [INTERP] Expect live Sharpe to fall well short of the backtest. Live CTA Sharpe of about 0.3–0.5 compares with backtests of 1+, and crypto backtests of 1.5–2.4 should be discounted heavily.

### Gaps
- I found no published measure of crowding or post-publication decay specific to crypto trend.
- No study separates long-only from long-short net results for BTC/ETH perps with funding included.
