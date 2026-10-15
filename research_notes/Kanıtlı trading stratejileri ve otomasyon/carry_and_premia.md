# Carry and risk-premium strategies (funding carry, cash-and-carry basis, volatility risk premium)

Research date: 2026-10-15. Every figure carries its source date. Labels: [ACADEMIC] = peer-reviewed or working paper; [PRACTITIONER] = named practitioner or firm write-up; [VENDOR] = exchange or protocol marketing, or a party with a commercial interest; [AGGREGATOR] = low-quality secondary or AI-generated site, use with caution.

## 1. Crypto funding-rate carry and cash-and-carry: academic evidence, realized returns by year, failures, Ethena track record

### Takeaway
Funding carry on BTC perps was real and large. On Binance BTC it averaged about 13.7% a year over 2020-2025, but it fell sharply: about 36% in 2021, 4-8% in 2022-2023, about 13% in 2024 and about 5% in 2025. Academic papers find the mispricing shrinking as arbitrage capital arrives. Ethena, the largest live funding-carry book, paid roughly 18-19% in 2024, then about 4-5% from late 2025 into 2026, and lost more than half its supply after the 10 Oct 2025 crash. The strategy's main risks are not the small daily P&L swings. They are venue failure (FTX in 2022), negative-funding regimes, and forced deleveraging (ADL in Oct 2025).

### Cited findings

**Academic**
- [ACADEMIC] Schmeling, Schrimpf & Todorov, "Crypto carry", BIS WP 1087 (Apr 2023; also CEPR DP 20719, 2025). The futures-spot carry in BTC and ETH "can become very large (up to 60% p.a.)" and averages above 10% a year, far above carry in equities, bonds, FX or commodities. They attribute it to trend-chasing small investors who want leveraged long exposure, combined with scarce arbitrage capital. Running the arbitrage is risky because margins spike and positions get liquidated during drawdowns, and high carry predicts future crashes. — [BIS WP 1087](https://www.bis.org/publ/work1087.pdf); [RePEc listing](https://www.bis.org/RePEc/bis/biswps/work1087.redif); [CEPR DP20719](https://cepr.org/publications/dp20719)
  - Gap: I could not extract the paper's return or Sharpe tables (see Gaps).
- [ACADEMIC] He, Manela, Ross & von Wachter, "Fundamentals of Perpetual Futures" (arXiv 2212.06888; v6 dated 21 Aug 2024, v7 also exists). Data are hourly Binance perp and spot prices from 2020-01-08 to 2024-03-11, with funding paid every 8 hours. — [arXiv v7 HTML](https://arxiv.org/html/2212.06888v7)
  - BTC random-maturity arbitrage Sharpe ratios: 11.65 with no fees; 3.35 at "high" (retail) fees; 3.27 at retail fees after effective bid-ask spreads. Sharpe with no fees: ETH 12.77, BNB 17.66, DOGE 14.90, ADA 19.76. — [arXiv v7](https://arxiv.org/html/2212.06888v7); [arXiv PDF](https://arxiv.org/pdf/2212.06888)
  - Zero-cost annualized excess return for BTC by year: 2020 49.6%, 2021 64.8%, 2022 60.0%, 2023 41.7%, 2024 (to March) 21.4%; 52.6% for the full sample. Full-sample max drawdown is -3.82% for BTC, -2.62% for ETH and -13.90% for DOGE. — [arXiv v7, Table 5](https://arxiv.org/html/2212.06888v7)
  - Return split for BTC (full sample): 37.61 points come from perp-spot price convergence (trading the deviation in and out) and only 14.94 points from funding. The funding share shrank in 2022-2023. — [arXiv v7, Table 7](https://arxiv.org/html/2212.06888v7)
  - The average deviation fell about 80% after 2022. BTC mean ρ went from 0.69 to 0.17 and ETH from 0.92 to 0.16, a decline of about 22 percentage points a year. The authors link this to more arbitrage capital, and note that Alameda and Three Arrows pivoted away from the trade around late 2021 to early 2022. — [arXiv v7](https://arxiv.org/html/2212.06888v7)
  - Negative-funding episodes: in March 2020 (COVID), funding was substantially negative on most exchanges. In November 2022 (FTX collapse), funding was significantly negative on solvent exchanges while perps traded above spot on FTX itself. — [arXiv v7](https://arxiv.org/html/2212.06888v7)

**Realized funding by year (Binance BTC perp)**
- [PRACTITIONER] Haghani & White, Elm Wealth, "Perpetual Futures" (4 Aug 2026), from Binance public historical data. The figures are average 8-hour funding and its annualized equivalent: 2020 ~0.016% (~18.8%), 2021 ~0.028% (~35.9%), 2022 ~0.004% (~4.3%), 2023 ~0.007% (~8.2%), 2024 ~0.011% (~12.7%), 2025 ~0.005% (~5.3%). Six-year average ~13.7%, against T-bills averaging ~3%, a gap of ~11%. That gap is about 3x the CME BTC futures financing spread and 7-20x the spread on bond and equity index futures (0.5-1.5%). — [Elm Wealth](https://elmwealth.com/perpetual-futures/)
  - Mechanics from the same source: the baseline interest component is 0.01% per 8h (~11.6% a year compounded). The cap is 0.30% per 8h on USDT-margined BTC contracts and ~0.75% on coin-margined contracts. — [Elm Wealth](https://elmwealth.com/perpetual-futures/)
- Recent snapshots (dated, not calendar averages): the trailing one-year average on Binance BTCUSDT was about 3.3% (Laevitas, read via search, Oct 2026); the 5-exchange current figure was about 11.5% annualized (defirate, Oct 2026); BTC funding was 0.01% per 8h on 27 Jun 2026 (convextrade). — [Laevitas](https://app.laevitas.ch/assets/perpswaps/BTC/funding); [defirate](https://defirate.com/perp/); [convextrade](https://convextrade.com/metrics/btc-funding)
  - These are search-snippet readings. Verify them on the live pages before use.

**Ethena USDe / sUSDe as a live, large-scale track record**
- Yield history. Every figure below comes from secondary sources, and the sources conflict:
  - [AGGREGATOR] sUSDe hit an all-time high of about 35% in Q1 2024 and a low of about 4.1% in Aug 2024. The reserve fund was about $61M in Mar 2026, roughly 1.1% of supply. — [eco.com](https://eco.com/support/en/articles/14798653-susde-explained-ethena-s-yield-bearing-stablecoin)
  - [AGGREGATOR] The 2024 average was about 18-19% APY. The 2025 range was about 4-15%, with underlying funding averaging about 5% in 2025. One note gives an average APY of 8.2% for Sep 2024 to Feb 2026. — [stablecoininsider Q1 2026 report](https://stablecoininsider.org/ethena-usde-q1-2026-report/); [eco.com 2026](https://eco.com/support/en/articles/15254002-ethena-usde-and-susde-2026-delta-neutral-yield); [coinpaprika](https://coinpaprika.com/education/yield-bearing-stablecoins/)
  - [AGGREGATOR] About 4.76% APY on 28 Sep 2026, with a 30-day average of 4.79%. Aavescan shows about 4% in late Jul 2026. Q1 2026 was about 3-8% in weak or negative funding. — [stablecoininsider](https://stablecoininsider.org/ethenas-staked-usde-stablecoin/); [aavescan](https://aavescan.com/rates/ethena-susde); [earnpark](https://earnpark.com/en/posts/ethena-fees-apy-interest-rates-explained-2026/)
  - [AGGREGATOR] In a trailing 365-day window (as of ~Apr 2026), funding was negative on about 21% of days. — [coinstats](https://coinstats.app/ai/a/investment-analysis-ethena-usde)
- Oct 2025 stress. USDe supply fell from about $14.7B on 9 Oct 2025 to about $6.3-6.4B by late December, an outflow of about $8.3B, while the yield dropped to about 4.3%. During the 10-11 Oct crash USDe printed about $0.65 on Binance only. Ethena blamed a Binance internal oracle and said DEX prices held. About $5.2B of USDe sat on Binance on 9 Oct. — [Forklog](https://forklog.com/en/news/usde-capitalisation-by-ethena-plummets-by-8-3-billion-since-october); [Cointelegraph](https://regional-front.cointelegraph.com/news/ethena-usde-market-cap-drops-october-crash-deleveraging); [Netcoins](https://www.netcoins.com/blog/ethenas-usde-depeg-an-overview-and-its-relation-to-the-ena-token); [Whale Alert](https://whale-alert.io/stories/917144d7ab20/Ethenas-USDe-loses-83B-in-net-outflows-and-briefly-depegs-after-Oct-10-liquidation-market-wide-volumes-and-confidence-fall)
- [AGGREGATOR/unverified] Reports from 2026 describe Ethena diversifying ("USDe 2.0") into gold, BTC, multi-strategy hedging and an equity basis trade, i.e. moving away from pure crypto funding. — [BingX Learn](https://bingx.com/en/learn/article/usde-2-ethena-internet-bond-diversification-2026); [GitHub analysis (unofficial)](https://github.com/Ricosworks1/blockchain-payment-flow-analysis/releases/tag/comparative-analysis-ethena-usde-equity-basis-trade-sept-2026)

**Failure episodes**
- FTX (Nov 2022): funding went negative on solvent venues (see He et al. above). Elm Wealth notes that an exchange insurance fund is not deposit insurance and that in bankruptcies such funds can be frozen into the creditor pool, citing FTX and Celsius. — [Elm Wealth](https://elmwealth.com/perpetual-futures/)
- 10 Oct 2025 crash and auto-deleveraging (ADL):
  - [ACADEMIC] On Hyperliquid, ADL closed about $2.1B of positions in 12 minutes. The authors estimate its queue over-used ADL by about 28x relative to an optimal policy, imposing about $653M of unnecessary haircuts on winners, and argue Binance over-used ADL even more. Binance does not publish auditable ADL data, so treat these as estimates. — [arXiv 2512.01112](https://arxiv.org/html/2512.01112v2)
  - A second paper puts the production ADL's over-liquidation of trader profits at up to $51.7M. — [arXiv 2602.15182](https://arxiv.org/html/2602.15182v1)
  - [PRACTITIONER/newsletter, weaker] ADL closed the short perp legs of delta-neutral and market-maker books without recognising the hedge, leaving the spot leg unhedged in a falling market. — [Das Crypto newsletter](https://das-crypto-newsletter.beehiiv.com/p/crypto-leverage-is-built-different); [Arch Lending blog](https://archlending.com/blog/auto-deleveraging-crypto/); [The Defiant autopsy](https://thedefiant.io/newsletter/defi-daily/the-ultimate-10-10-crash-autopsy)
  - About $19B of leveraged positions were liquidated within hours (10x Research estimate). — [Elm Wealth](https://elmwealth.com/perpetual-futures/); [Whale Alert](https://whale-alert.io/stories/917144d7ab20/Ethenas-USDe-loses-83B-in-net-outflows-and-briefly-depegs-after-Oct-10-liquidation-market-wide-volumes-and-confidence-fall)
- Regulatory: CME has sued to block US perpetual futures, arguing they are swaps. — [Elm Wealth](https://elmwealth.com/perpetual-futures/)

### Inferences
- The headline academic Sharpe ratios (3-12) mostly reflect trading in and out of perp-spot deviations at hourly frequency, with price convergence contributing about 72% of BTC returns. A retail "buy spot, short perp, hold" book earns mainly the funding leg. For BTC that leg was about 15% a year in 2020-Mar 2024 (He et al.) and about 5% in 2025 (Elm). Do not quote the academic Sharpe for the passive retail version.
- The edge is decaying. Deviations fell about 80% after 2022, Binance BTC funding averaged ~5% in 2025, the trailing one-year Binance BTCUSDT average is ~3.3% (Oct 2026), and sUSDe yields ~4-5% (2026). Against T-bills at ~3.5%, the 2025-26 excess return for passive BTC carry is close to zero after costs. The large years (2021, 2024) coincided with bull markets, so the carry is pro-cyclical, which is what BIS describes.
- Ethena is the best live evidence. A multi-billion-dollar book earned double digits in 2024 and low single digits in 2025-26. Its main stress came from capital flight and venue mechanics (the Binance oracle and ADL), not from negative funding itself.
- For retail on a single CEX, the largest risk is counterparty or venue risk (FTX-type insolvency, ADL breaking the hedge, a local-venue depeg of collateral). Holding both legs on one venue concentrates that risk. Splitting across venues trades it for transfer risk and extra margin.

### Gaps
- I could not extract the BIS WP 1087 tables (carry-trade Sharpe, drawdowns, exchange breakdown). Only the abstract and contribution-level numbers were retrievable.
- He et al. report BTC Sharpe ratios at retail fees but no yearly return table at retail fees in the part I read. Their sample ends Mar 2024.
- I found no official Ethena yield time series (dashboard or DefiLlama were not fetched). All Ethena figures are secondary and conflicting, so the 2024 average (~18-19%) and 2025 range (~4-15%) should be confirmed at ethena.fi or DefiLlama.
- I found no clean, sourced annual funding series for 2019 or for ETH by year. Christin et al. was not located in this pass.
- Binance's ADL impact on hedged retail books is not publicly quantified.

## 2. How much gross funding is lost to fees, basis drift, rebalancing and margin; rule designs and thresholds

### Takeaway
At Binance retail fees, a full round trip on both legs costs roughly 0.24-0.30% of notional. That is minor for a book held months in a 10%+ funding regime and decisive in a 3-5% regime or with frequent rotation. A larger hidden cost is capital efficiency: the perp margin and any idle USDT earn nothing, so the return on total capital is below the funding rate. Academic entry thresholds for trading the deviation at retail fees are very wide (about ±179% annualized), so retail realistically harvests only funding.

### Cited findings
- Binance base fees (VIP0): spot 0.1% maker and taker (~0.075% with the BNB discount); USDT-M futures 0.02% maker / 0.05% taker. Binance support says the BNB discount on futures is 10% and requires BNB in the futures wallet; secondary sources conflict on this. USDC-M perps were reported at 0% maker / 0.04% taker. — [Binance support 360033544231](https://www.binance.com/es/support/articles/360033544231); [Finder](https://www.finder.com/binance-futures-fees); [Bitsgap](https://bitsgap.com/blog/binance-trading-fees-explained-what-it-costs)
- He et al. fee tiers (one-way maker): high/individual is 0.0675% spot and 0.0144% futures; medium is 0.045% and 0.0072%; low is 0.0225% and 0.0018%. A round trip costs 2 × (spot + futures). The no-arbitrage band, i.e. the deviation needed before entry pays, is about ±179.4 annualized percentage points at high fees, ±114.3 at medium and ±53.2 at low. A data-driven threshold chosen from the past 6 months performed the same or worse. Bid-ask spread plus price impact was under 0.35 bp (Kaiko data). — [arXiv v7](https://arxiv.org/html/2212.06888v7)
- Margin and leverage: perps commonly run 20-100x with 1-5% initial margin. Exchanges can liquidate without a margin call, and liquidation fees go to the insurance fund. — [Elm Wealth](https://elmwealth.com/perpetual-futures/)
- BIS: the risk of the arbitrage comes from margin spikes and liquidations in drawdowns, and from scarce arbitrage capital. — [BIS WP 1087](https://www.bis.org/publ/work1087.pdf)
- [ACADEMIC, not fully read] A 2026 arXiv paper studies dynamic collateral control for permissionless spot-perp basis trading, i.e. rebalancing margin to avoid liquidation on the short leg. — [arXiv 2605.05089](https://arxiv.org/pdf/2605.05089)

### Inferences (my arithmetic, not sourced figures)
- Taker round trip at VIP0 is 2 × (0.10% + 0.05%) = 0.30% of notional; with BNB discounts it is about 2 × (0.075% + 0.045%) ≈ 0.24%. At 2025's ~5.3% funding, that is about 1 month of carry; at 2021's ~36% it is about 3 days. Maker orders roughly halve the perp-leg cost but add leg risk while one side is unfilled.
- Capital efficiency without portfolio or cross-collateral margin: holding N of spot plus a short perp of N at 3x needs N/3 of margin, so capital = 1.33N and the return on capital ≈ funding ÷ 1.33. Example: 5.3% gross becomes ~4.0%, minus fees, versus ~3.5% T-bills. Lower perp leverage is safer but dilutes the return further. Higher leverage raises the chance of short-leg liquidation in a sharp rally, which turns the "neutral" book into a naked long spot position. If the venue allows spot to serve as perp collateral (portfolio margin), this drag shrinks but liquidation becomes cross-linked.
- Basis drift: a perp trading above spot at entry and converging at exit costs the entry premium. He et al.'s decomposition shows this convergence term is larger than funding. Retail entering during hot funding usually pays an elevated perp premium, which partly offsets the funding gained.
- Common practitioner rule shapes (inference; no single authoritative source found):
  - Enter when trailing funding (e.g. a 3-7 day average) exceeds a hurdle of roughly risk-free rate + amortized round-trip cost.
  - Hold through brief negative prints.
  - Exit when the trailing average stays below the hurdle.
  - Rebalance when the leg-notional mismatch or margin ratio drifts past a band (e.g. ±5-10% notional, or margin ratio > 50%).
  - Treat these numbers as illustrative, not evidence-based.

### Gaps
- I found no independent published study of net-of-fee, retail-scale, passive funding-carry returns by year. That figure has to be backtested from Binance funding history (rate × 3 × 365) with fees, margin and idle-cash drag.
- No rigorous source gives entry and exit thresholds for the passive hold version, only the deviation-trading bounds above.

## 3. Perp-only funding strategies (no spot leg) and their directional risk

### Takeaway
Without a spot leg, a funding strategy is a directional position. Being short the perp to collect positive funding means being short the asset, and in crypto positive funding coincides with uptrends. One day's adverse move (BTC often moves 3-5%) wipes out months of carry at 5-15% a year. Funding is a signal or overlay here, not a premium harvest.

### Cited findings
- Funding is high when leveraged, trend-chasing long demand is high (BIS). Carry is large in boom periods, and high carry predicts subsequent crashes. — [BIS WP 1087](https://www.bis.org/publ/work1087.pdf)
- Funding is capped at 0.30% per 8h on Binance USDT-M BTC (≈2,600% annualized) and can flip negative in crashes (Mar 2020, Nov 2022). — [Elm Wealth](https://elmwealth.com/perpetual-futures/); [arXiv v7](https://arxiv.org/html/2212.06888v7)
- Cross-exchange perp-perp spreads: He et al. show funding and deviations co-move across exchanges, and on FTX in Nov 2022 the sign was the opposite of solvent venues. A perp-perp hedge across venues is therefore exposed to exactly that venue-specific divergence. — [arXiv v7](https://arxiv.org/html/2212.06888v7)

### Inferences
- Rough break-even: at 10% annual funding a naked short collects ~0.027% a day, so a single +3% day costs about 110 days of carry. Perp-only funding harvesting is not market-neutral, and any test should report it as a directional strategy with a funding tilt.
- Cross-exchange perp-perp (long the perp with low funding, short the one with high funding) is closer to neutral. It doubles venue risk, needs margin on both legs and is exposed to ADL on either side.

### Gaps
- I found no academic study of naked funding-signal strategies (e.g. contrarian short when funding is extreme) with out-of-sample results in this pass.

## 4. Volatility risk premium (VRP): crypto (Deribit BTC/ETH) and equities; tail risk; Binance access at retail scale

### Takeaway
BTC carries a large variance risk premium, about 7x the S&P 500's in variance units (2017-2022). A Deribit practitioner backtest of selling short-dated BTC strangles earned about 27-30% a year in 2020-Apr 2025, with a 24% max drawdown, and one variant went bankrupt. The premium exists, but its tail is extreme and small samples flatter it. Binance now lets all users write BTC and ETH options after a suitability test, so it is accessible at retail scale, but undefined-risk short options are the most account-killing strategy in this set.

### Cited findings
- [ACADEMIC] Almeida, Grith, Miftachov & Wang, "Risk Premia in the Bitcoin Market" (arXiv 2410.15195). Using Deribit options from Jul 2017 to Dec 2022, the BTC VRP is about 0.14 a year in variance units (27-day horizon): 0.17 in low-vol regimes and 0.12 in high-vol regimes. That is "much higher than" the S&P 500's ~2% (citing Bollerslev et al. 2009). Negative BTC returns of 1-3 standard deviations explain only about a third of the return premium. — [arXiv 2410.15195](https://arxiv.org/html/2410.15195v2); [summary](https://harbourfrontquant.substack.com/p/return-and-variance-risk-premia-in)
- [VENDOR/PRACTITIONER — Deribit-hosted] "Option Backtest – Selling Weekend Vol, Revisited" (Cryptarbitrage, Deribit Insights, 21 May 2025). The test sells a 0.35-delta BTC strangle on Friday 16:00 UTC, expiring Sunday 08:00 UTC, with Deribit fees plus 5% slippage, flat size and a 1 BTC start. — [Deribit Insights](https://insights.deribit.com/?p=99807)
  - 2020-01 to 2024-08: 212 trades (169 wins), +124.9%, APR 27.4%, max drawdown 23.8%.
  - 2024-09 to 2025-04: 34 trades, APR 45.8%, max drawdown 3.9%.
  - Full 2020-01 to 2025-04: APR 29.7%, max drawdown 23.8%.
  - ETH, Fridays: APR 20.3%, max drawdown 27.2%.
  - Every day at half size: APR 23.8%, max drawdown 26.5% (0.45 BTC), which the author judged too deep.
  - Sunday-only: APR -17.7%, max drawdown 102%, i.e. the account would have been liquidated.
  - The author warns that negatively skewed strategies look too good over short samples.
- Deribit's CEO argues VaR understates tail risk for short-vol strategies and that expected shortfall should be used instead (secondary report). — [KuCoin news](https://www.kucoin.com/news/flash/bitcoin-3-sigma-days-exceed-2018-despite-lower-volatility)
- BTC 1-month ATM implied volatility was about 37.7% on 6 Sep 2026 (Glassnode via Crypto Briefing), with a persistent smile indicating downside hedging demand. — [Crypto Briefing](https://cryptobriefing.com/bitcoin-options-atm-implied-volatility-37-percent/)
- KMPV (below) find carry, including equity index options carry, predicts returns, and that carry strategies across asset classes lose together in global recessions. — [NBER w19325](https://www.nber.org/papers/w19325)
- Binance access:
  - Binance's European-style BTC options (Dec 2020) allowed users to "write and sell options as an issuer"; USDT-settled. — [The Block](https://www.theblock.co/news/markets/2020-12-28-binance-lists-european-style-bitcoin-options-deribit-89374); [CryptoPotato](https://cryptopotato.com/binance-launches-european-style-bitcoin-options-traders-can-issue-their-own-contracts/)
  - BTC options writing was opened to all users, with a mandatory suitability assessment and margin collateral; date not confirmed. ETH options writing was opened to all users on 22 Dec 2025 on the same terms. — [FinanceFeeds](https://financefeeds.com/binance-opens-bitcoin-options-to-all-users/); [Tangem news](https://tangem.com/en/news/markets/6981-binance-unlocks-ethereum-options-writing-for-all-users/)
  - Binance's 2026 gold and silver options (ADGM entity) and US stock/ETF options are buy-only for retail. — [Crypto Briefing](https://cryptobriefing.com/binance-gold-silver-options-adgm/); [The Paypers](https://thepaypers.com/crypto-web3-and-cbdc/news/binance-launches-options-on-us-stocks-and-etfs)

### Inferences
- The BTC VRP is large and documented, but the only crypto option-selling P&L evidence found is a single Deribit-hosted backtest. It shows a 24-27% drawdown at flat size, and Deribit has an interest in promoting options trading. With $1k-100k the minimum contract size (0.01 BTC on Deribit; Binance similar) allows reasonable sizing. Defined-risk structures (iron condors, put spreads) cap the tail at the cost of a smaller premium; that is a standard trade-off and was not quantified here.
- Short vol is correlated with the other premia in this file: it loses in crashes, exactly when funding carry and FX carry also suffer. Combining them does not diversify the tail.

### Gaps
- I found no peer-reviewed study of net returns from systematic crypto straddle or strangle selling.
- No equity short-straddle or put-writing figures (e.g. CBOE PUT index) were retrieved in this pass. The equity side here relies on the ~2% S&P VRP number and KMPV.
- Binance option liquidity, spreads and minimum sizes for retail writers were not verified.

## 5. Carry in other asset classes (FX carry, Koijen-Moskowitz-Pedersen-Vrugt) as context for persistence and crash risk

### Takeaway
Carry is a pervasive premium across asset classes, but it is crash-prone. FX carry returns are negatively skewed because positions unwind suddenly when funding liquidity dries up, and carry strategies across asset classes fail together in global recessions. Crypto carry fits this pattern, with higher levels and faster decay.

### Cited findings
- [ACADEMIC] Koijen, Moskowitz, Pedersen & Vrugt, "Carry" (JFE 2018; NBER w19325). Carry is the return if prices stay unchanged and is observable in advance. It predicts returns in both the cross-section and the time series in global equities, global bonds, currencies, commodities, US Treasuries, credit and equity index options. Correlations across asset classes are low unconditionally, but carry strategies sometimes lose together, and those episodes coincide with global recessions. The paper won second prize in the 2018 Fama-DFA awards. — [NBER w19325](https://www.nber.org/papers/w19325); [CBS](https://cbs.dk/node/526518)
- [ACADEMIC] Brunnermeier, Nagel & Pedersen, "Carry Trades and Currency Crashes" (NBER WP 14473, Nov 2008; NBER Macro Annual 2008). Moves between high- and low-rate currencies are negatively skewed because carry positions unwind suddenly when funding liquidity and risk appetite fall. Liquidity measures predict FX moves. Carry losses reduce future crash risk but raise its price. Their examples include the Oct 1998 USD/JPY crash. — [NBER w14473](https://www.nber.org/papers/w14473)
- Elm Wealth: the crypto perp financing spread (~11% over T-bills, 2020-25) is 7-20x the spread in traditional index futures (0.5-1.5%), which shows how anomalous crypto carry is relative to TradFi. — [Elm Wealth](https://elmwealth.com/perpetual-futures/)

### Inferences
- The TradFi pattern is that carry persists for decades as compensation for crash risk, but in modest size. Crypto carry looks like an immature-market version: very large while arbitrage capital was scarce, and now converging toward TradFi-like levels (He et al. deviation decay; 2025-26 funding near T-bills). The BIS mechanism (leverage demand from trend-chasers) suggests it will re-expand in future speculative booms, which is when crash risk is also highest.

### Gaps
- The KMPV headline Sharpe (~1.2 for diversified carry, from memory) was not confirmed against the paper text, so it is not cited.
- No 2008 or 2024 (yen unwind, Aug 2024) FX-carry drawdown figures were retrieved.
