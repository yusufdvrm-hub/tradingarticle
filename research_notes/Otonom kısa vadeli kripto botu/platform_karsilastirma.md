# Trading Venue Comparison for an Autonomous, Short-Term, Small-Win, Low-Risk LLM Crypto Bot (as of Oct 2026)

Research date: 2026-10-14. Note on the method: binance.com, developers.binance.com and hyperliquid.gitbook.io could not be fetched from this environment (DNS failure), so the exchange fee and limit figures come from search snippets of official docs or from secondary sources. Each figure below says which kind of source it came from. Check every fee figure against the live fee page or the `exchangeInfo` / account-fee endpoints before going live.

## Fees and breakeven per round trip (RT)

### Takeaway
With 0.3–1% targets, fees decide whether the strategy can work at all. Perps on Binance USDⓈ-M, OKX, Bybit and Hyperliquid cost about 0.03–0.11% per round trip, which leaves a viable margin. Spot at the base tier costs about 0.15–0.20% RT, which uses up half or more of a 0.3% target. Pump.fun's bonding curve costs about 2% RT before slippage and MEV, which makes a 0.3–1% target arithmetically impossible.

### Cited Findings
- Binance spot, regular user: 0.10% maker / 0.10% taker. Paying fees in BNB gives a 25% discount, so about 0.075% per side (secondary sources; one calls the 25% "historical"). — [udn blog](https://blog.udn.com/G_113305896286280921/192424307); [hijri-calendars blog](https://hijri-calendars.com/blog/binance-fees-explained-2026?lang=en)
- Binance spot VIP 3: 0.040% maker / 0.060% taker, or 0.030% / 0.045% with BNB. — [Analytics Insight](https://www.analyticsinsight.net/cryptocurrency-analytics-insight/maker-vs-taker-fees-what-they-mean-how-crypto-trading-fees-work-in-2026)
- Binance USDⓈ-M futures, regular user: 0.02% maker. The taker figure conflicts between sources: 0.04% per a Binance Square page and about 0.05% per Traders Union. Paying in BNB gives a 10% discount (Binance support article cited via search). — [Binance Square](https://www.binance.com/fr-AF/square/hashtag/binancefees); [Traders Union](https://tradersunion.com/brokers/crypto/view/binance/futures-fees/); [Binance support](https://www.binance.com/pt/support/articles/360033544231)
- Bybit, non-VIP: USDT perps 0.02% maker / 0.055% taker; spot 0.10% / 0.10%. Bybit VIP 5: spot 0.04% / 0.05%, perps 0.01% / 0.032%. — [Bitsgap](https://bitsgap.com/blog/bybit-trading-fees-explained-what-it-costs); [traderssecondbrain](https://traderssecondbrain.com/guides/bybit-vs-okx)
- OKX, regular user: perps 0.02% maker / 0.05% taker; spot 0.08% maker / 0.10% taker. The VIP schedule was reworked in April 2026 (9 tiers, lower entry thresholds). — [Analytics Insight](https://www.analyticsinsight.net/cryptocurrency-analytics-insight/okx-vs-bybit-fees-features-crypto-trading-options-compared); [traderssecondbrain](https://traderssecondbrain.com/tools/exchange-fees)
- Hyperliquid perps, base tier: 0.015% maker / 0.045% taker. Hyperliquid spot: 0.04% maker / 0.07% taker. Tiers use 14-day rolling volume, and spot volume counts double. Staking HYPE gives a discount of 5% (10+ HYPE) up to 40% (500k+ HYPE). The top-tier thresholds conflict between sources ($5B vs $7B). — [Dwellir](https://www.dwellir.com/blog/hyperliquid-fees-explained); [OneKey](https://onekey.so/blog/ecosystem/hyperliquid-fee-structure-how-to-optimize-trading-costs-45c553); [Hyperliquid docs](https://hyperliquid.gitbook.io/Hyperliquid-docs/trading/fees)
- Jupiter (Ultra, now **deprecated** in favour of Swap V2 `/order`): base fee 0 bps for stable–stable pairs, 2 bps for SOL–stable, 5 bps for LST–stable, 10 bps for most other pairs, and **50 bps for tokens younger than 24 hours**. In gasless mode, network, priority and ATA costs are deducted from the swap amount. — [Jupiter dev docs (Ultra fees)](https://developers.jup.ag/docs/ultra/fees); [Jupiter Swap fees](https://developers.jup.ag/docs/swap/fees)
- Pump.fun: about 1% fee on every buy and every sell on the bonding curve. The curve completes at about 85 SOL. PumpSwap's fee after graduation conflicts between sources (0.30% per the pump.fun docs vs 0.25% per secondary sources). The creator-fee structure ("Project Ascend" sliding scale) is unverified. — [MadeOnSol](https://madeonsol.com/blog/how-to-use-pump-fun); [Datawallet](https://datawallet.com/crypto/what-is-pump-fun-and-create-a-coin); [BlockEden, Apr 2026](https://blockeden.xyz/blog/2026/04/12/pumpswap-16b-volume-pumpfun-amm-raydium-solana-dex/); [The Block (PumpSwap launch)](https://www.theblock.co/amp/post/347360/pump-fun-launches-dex-called-pumpswap-to-instantly-migrate-graduated-tokens)

### Inferences (my own arithmetic from the fees above; slippage and funding excluded)
| Venue / mode | Taker+taker RT | Maker in + taker out (typical: limit entry, market stop) | Maker+maker RT | Share of a 0.3% target eaten by taker RT |
|---|---|---|---|---|
| Binance spot (regular) | 0.20% | 0.20% | 0.20% | 67% |
| Binance spot + BNB | 0.15% | 0.15% | 0.15% | 50% |
| Binance USDⓈ-M (0.02/0.05) | 0.10% (0.09% with BNB) | 0.07% | 0.04% | 33% |
| Bybit perps | 0.11% | 0.075% | 0.04% | 37% |
| OKX perps | 0.10% | 0.07% | 0.04% | 33% |
| Hyperliquid perps (base tier) | 0.09% | 0.06% | 0.03% | 30% |
| Hyperliquid spot | 0.14% | 0.11% | 0.08% | 47% |
| Jupiter, SOL–USDC | about 0.04% + priority fee + slippage | n/a (AMM, taker only) | n/a | about 13%+ |
| Jupiter, ordinary token | about 0.20% + priority fee + slippage | n/a | n/a | 67%+ |
| Jupiter, token under 24h old | about 1.0% + ... | n/a | n/a | >300% |
| Pump.fun bonding curve | about 2.0% + slippage + Jito tip | n/a | n/a | about 670% (impossible) |

- Breakeven win rate for symmetric take-profit and stop-loss of size X with RT cost c is p = (X + c) / (2X). Two examples:
  - Hyperliquid taker, X = 0.3%: p = 0.39 / 0.6 = 65%.
  - Binance spot regular, X = 0.3%: p = 0.5 / 0.6 = 83%.

  A "many small wins" strategy at 0.3% on spot taker therefore needs an unrealistically high hit rate. Use targets of at least 0.5–1%, maker entries, and perps (1x–2x leverage, used only for the cheaper fees).
- Perps add funding payments every 8 hours (Binance and Bybit) or every hour (Hyperliquid). For holds of minutes to hours this is usually small, but it can be several bps per interval during extreme regimes. I did not source current rates.
- Stop-losses fill as taker orders. In fast moves on stop-market orders, slippage can be several bps even on BTC. On memecoins it can be tens of percent.

### Gaps
- I could not open the official Binance fee page or the Hyperliquid fee docs here. Whether the Binance USDⓈ-M regular taker fee is 0.04% or 0.05% is unresolved, and the bot should read it from `/fapi/v1/commissionRate` at startup.
- I found no current Swap V2 priority-fee rate for Jupiter.
- I found no authoritative current pump.fun dynamic-fee table.

## API quality (REST/WS, rate limits, order types, SDKs)

### Takeaway
Binance has the most mature API: high weight limits, WebSocket API, a broad set of order types, and the widest SDK and ccxt coverage. Hyperliquid's API is good and ccxt supports it, but its REST weight budget is lower and it is an on-chain signer model. DEX and pump.fun bots need Solana RPC, Jito bundles and priority fees, a far more fragile stack with no native stop-loss.

### Cited Findings
- Binance spot REQUEST_WEIGHT limit is 6000 per minute per IP. Every response carries a header `X-MBX-USED-WEIGHT-*`. ORDERS limits are per account and shared across all API keys, with a 10-second interval aligned to :00, :10 and so on. Exceeding them returns HTTP 429. Repeated violations lead to an automated IP ban (HTTP 418). — [Binance WS-API rate limits](https://developers.binance.com/docs/binance-spot-api-docs/websocket-api/rate-limits); [Binance REST docs mirror](https://github.com/KenRoytman/binance-official-api-docs/blob/master/rest-api.md)
- Hyperliquid's official rate limit is an IP-based REST weight of 1200 per minute. Exchange actions weigh 1; info requests weigh 2 or 20. WebSocket is recommended for low latency. Third-party guides give conflicting figures. — [Hyperliquid docs: rate limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits); [OneKey guide](https://onekey.so/blog/ecosystem/hyperliquid-rate-limits-best-practices/)
- ccxt supports Hyperliquid with the same unified API as its 100+ other venues. Its built-in rate limiter is on by default, whereas rate limiting in the official Python SDK is manual. Testnet is reached via `set_sandbox_mode(True)` in ccxt, or the testnet URL constant in the SDK. — [ccxt docs: ccxt vs Hyperliquid API](https://docs.ccxt.com/docs/comparisons/ccxt-vs-hyperliquid-api)
- Hyperliquid has a "speedbump" design that gives order cancels priority over taker orders. This favours makers: quotes are less likely to be picked off. It is also why displayed depth is not directly comparable to Binance. — [Blockworks Research](https://blockworks-research.beehiiv.com/p/is-hyperliquid-hyper-liquid)
- Jupiter Ultra is deprecated. New integrations should use Swap V2 `/order`. — [Jupiter dev docs](https://developers.jup.ag/docs/ultra/fees)

### Inferences
- Order types: from general knowledge of the APIs, not re-verified in this session:
  - Binance spot supports OCO and OTO/OTOCO order lists, STOP_LOSS_LIMIT and LIMIT_MAKER (post-only).
  - Binance USDⓈ-M supports STOP_MARKET and TAKE_PROFIT_MARKET with `reduceOnly` and `closePosition`, GTX (post-only), and `priceProtect`.
  - Hyperliquid supports TP/SL trigger orders, reduce-only and ALO (post-only).
  - Bybit and OKX support attached TP/SL, reduce-only and post-only.
  - Jupiter and pump.fun have **no exchange-side stop-loss**. The bot must watch prices and send a swap itself, so a crashed bot or a congested chain means no stop. This is a decisive weakness for a "cut losses fast, no human" design.
- For an LLM-driven bot, the LLM should not be in the stop-loss path. Exchange-resident stops placed atomically with the entry (OTOCO, or attached TP/SL) are the main safety feature, and only CEXs and Hyperliquid provide them.
- At small trade frequency (tens to hundreds of orders per day), none of the CEX or Hyperliquid limits will bind. The LLM's own latency (seconds) will dominate exchange latency (milliseconds), so co-location and latency races are irrelevant. The bot cannot compete in sub-second HFT and should not try.

### Gaps
- I did not verify the exact Binance ORDERS caps (per 10 seconds and per day) or the exact OCO/OTOCO weights. Read them from the live `exchangeInfo.rateLimits`.
- I did not fetch official latency benchmarks for any venue.

## Testnet and paper trading

### Takeaway
Every CEX candidate and Hyperliquid has a testnet. All of them are useful for testing API plumbing (order lifecycle, reduce-only, OCO, error handling) and useless for validating P&L, because their liquidity and fills are not realistic. Pump.fun and memecoin DEXes have no meaningful testnet equivalent.

### Cited Findings
- Binance publishes Spot Testnet REST and WS APIs, including a separate testnet rate-limit page. — [Binance Spot Testnet REST](https://developers.binance.com/en/docs/products/spot/testnet/rest-api); [Testnet WS rate limits](https://developers.binance.com/legacy-docs/zh-CN/binance-spot-api-docs/testnet/websocket-api/rate-limits)
- Spot testnet data is reportedly wiped roughly monthly without notice, balances are virtual, and the testnet is not always updated in sync with live (third-party connector notes). — [binance-clj known limitations](https://cljdoc.org/d/io.github.ugurbay/binance-clj/1.0.4/doc/known-limitations)
- A Binance support reply (Nov 2024) said there is no fixed retention limit for Futures testnet funds and to treat it only as practice. This is older information. — [Reddit r/binance support thread](https://cal1.lr.ggtyler.dev/r/binance/comments/1g8i1rc/binance_support_thread/luvsjqw/?context=3)
- Spot testnet market orders have expired unfilled because of thin liquidity (ccxt issue, 2021; old). — [Lightrun/ccxt issue](https://lightrun.com/answers/ccxt-ccxt-binance-testnet-orders-expired)
- Hyperliquid testnet is reachable via ccxt sandbox mode or the SDK's testnet URL. — [ccxt docs](https://docs.ccxt.com/docs/comparisons/ccxt-vs-hyperliquid-api)

### Inferences
- Recommended validation ladder:
  1. Backtest on real historical L2/trade data with pessimistic fills: taker fees, slippage, and stop orders filling 1–3 ticks worse.
  2. Run on the testnet only to test the order state machine.
  3. Paper-trade against the **live** order book: simulate fills from the live WebSocket feed and keep no real orders.
  4. Go live with tiny size, for example $50–200 per trade, for several weeks.
- Bybit and OKX also offer "demo trading" modes that mirror live prices. Fills there are still simulated, and I did not verify the details this session.

### Gaps
- I found no source quantifying how far testnet fills differ from mainnet.
- The details of Bybit and OKX demo trading and of the Hyperliquid testnet faucet were not covered in my sources.

## Pump.fun and memecoin risks

### Takeaway
"Low-risk small wins" is not achievable on pump.fun. About 98.6–98.7% of its tokens collapse, the round-trip fee alone (about 2%) is larger than the target, there is no native stop-loss, and the bot would compete against latency-optimised sniper and MEV bots that extract value from slower participants. An LLM bot that decides in seconds is structurally the slowest participant there.

### Cited Findings
- Solidus Labs found that 98.6–98.7% of pump.fun tokens show pump-and-dump or rug characteristics. Of more than 7 million tokens launched (Jan 2024–Mar 2025), only about 97,000 kept at least $1,000 of liquidity. On Raydium, about 361k of 388k pools (≈93%) showed soft-rug traits. Caveat: the $1k-liquidity threshold measures collapse, not proven fraud, and pump.fun disputes the report. — [The Defiant](https://thedefiant.io/news/defi/alarming-99-of-memecoin-launches-on-pumpfun-are-pump-and-dumps-or-rug-pulls-report); [Forklog](https://forklog.com/en/report-98-of-pump-funs-memecoins-deemed-scams/); [Benzinga](https://www.benzinga.com/markets/cryptocurrency/25/05/45297511/98-of-pump-fun-tokens-are-frauds-the-extractive-nature-of-solana-meme-coins); [Bitcoin.com](https://news.bitcoin.com/report-exposes-98-6-of-solana-meme-coins-on-pump-fun-as-fraudulent/)
- Sandwich bots extracted an estimated $370M–$500M from Solana users over 16 months (sandwich.me at Accelerate 2025). "Wide" multi-slot sandwiches grew from about 1% to 30% of attacks. — [Solana Compass](https://solanacompass.com/learn/accelerate-25/scale-or-die-at-accelerate-2025-the-state-of-solana-mev)
- An Oct 2025 report found that 93% of attacks were "wide" sandwiches, extraction ran at 30k–60k SOL per month (record 87k SOL in Jan 2025), and up to 6% of blocks contained sandwiches. Jito banned 15 more validators. — [MEXC News](https://www.mexc.com/news/138838)
- Jito shut down its public mempool in March 2024 because of sandwich attacks. — [The Block](https://www.theblock.co/post/281504/solana-client-jito-labs-axes-mempool-function-following-increase-in-mev-attacks)
- Jupiter charges 50 bps on tokens less than 24 hours old, on top of slippage. — [Jupiter docs](https://developers.jup.ag/docs/ultra/fees)

### Inferences
- The expected value for a small-win bot on memecoins is dominated by fat left tails. One rug (−90% to −100%, unfillable because liquidity is pulled) erases hundreds of +0.5% wins. A "stop-loss" cannot execute when the pool is drained.
- MEV protection (Jito bundles, tight slippage) adds cost and failed transactions but does not remove rug risk.
- Verdict: exclude pump.fun and new-token sniping from a "low-risk" mandate. At most, keep it as a separate, ring-fenced experimental budget the user can afford to lose entirely.

### Gaps
- I found no 2026 update of the Solidus survival statistics.
- I found no 2026 Jito or sandwich loss figures.
- I found no study of sniper-bot win rates.

## Regulatory and access situation for a user in Turkey; API key security

### Takeaway
Under Law 7518 (June 2024), the SPK licenses crypto asset service providers. Binance **global** is not on SPK's lists. SPK says using unauthorised platforms is the user's own responsibility, and serving Turkish residents without a licence is an offence for the provider. Binance TR (Binance Turkey Kripto Varlık Alım Satım Platformu A.Ş.) is on SPK's transitional "operating" list. Whether it holds a full licence as of late 2026 is disputed between sources. The domestic-compliant route is Binance TR, but it is spot-only with TRY/USDT pairs. The derivatives venues (Binance USDⓈ-M, Bybit, OKX global, Hyperliquid) are not SPK-authorised for Turkish residents.

### Cited Findings
- Law No. 7518 (June 2024) places CASPs under SPK. Operating without a licence is a criminal offence for the provider. — [Bilal Alyar law firm guide](https://bilalalyar.av.tr/en-spk-crypto-license-application/)
- In 2024, SPK published applicant lists (47, later 75 firms), including Binance TR, OKX TR and others. Being listed does not mean being licensed. — [Webrazzi](https://webrazzi.com/2024/10/17/spk-ya-lisans-basvurusu-yapan-kripto-varlik-saglayicilarinin-guncel-listesi/); [Finance Magnates](https://financemagnates.com/cryptocurrency/turkeys-cmb-lists-47-crypto-providers-awaiting-licensing-under-new-law/amp); [DonanımHaber](https://www.donanimhaber.com/spk-basvuruda-bulunan-kripto-para-borsalarini-acikladi--181182)
- Binance global phased out its Turkish-language service and stopped marketing to Turkish users, while remaining accessible. — [CoinTurk](https://en.coin-turk.com/binance-announces-turkish-language-service-suspension/); [Ekonomim](https://www.ekonomim.com/finans/kripto-para/binance-turkiye-faaliyetlerini-gecici-durdurma-karari-aldi-haberi-752222)
- Binance TR's operating company appears on SPK's temporary "Faaliyette Bulunanlar" list (checked 27 Sep 2026 per the source). SPK states this is not an authorisation. Platforms not authorised in Turkey are used at the consumer's own risk. — [Pega Hukuk](https://pegahukuk.com/binance-p2p/)
- An SPK provisional CASP list was announced in Aug 2026. — [Fintechtime, Aug 2026](https://fintechtime.com/2026/08/spk-kripto-varlik-hizmet-saglayicilari-gecici-listesini-acikladi/)
- **Conflict:** a commercial blog claims that per SPK's 12 May 2026 list, 11 CASPs are licensed, Binance TR included. This contradicts the "applicant / transitional only" description above. — [copytradeinsider](https://www.copytradeinsider.com/tr/blog/turkiye-kripto-yasal-mi-2026/) vs [Pega Hukuk](https://pegahukuk.com/binance-p2p/)
- Bybit's restricted-country list (updated May 2026, secondary source) does not include Turkey. Global exchanges remain commonly used in Turkey, and MASAK enforces AML rules. — [CoinPerps](https://www.coinperps.com/learn/bybit-restricted-countries); [Koru Legal](https://korulegal.com/en/blog/foreigner-crypto-exchange-access-kyc-turkey/)

### Inferences
- Practical risks of using global Binance, Bybit or OKX derivatives from Turkey:
  - account restriction on short notice;
  - TRY on/off-ramp friction (P2P);
  - tax and reporting ambiguity;
  - no Turkish investor protection.

  Hyperliquid needs no KYC, but that does not make it legal for Turkish residents, and it adds smart-contract, bridge (USDC on Arbitrum) and oracle risks.
- API key hygiene, from general best practice rather than sources verified this session:
  - create a trade-only key with withdrawals disabled and an IP whitelist pointing to the bot server's static IP;
  - use separate sub-accounts per strategy, funded only with the risk budget;
  - prefer Ed25519/RSA keys where supported (Binance supports Ed25519 for the WS API);
  - store secrets in an env or secret manager, never in prompts the LLM can echo;
  - on Hyperliquid, use an "API/agent wallet" that can trade but not withdraw.
- The LLM must never see or handle keys. Its output should be a constrained JSON action that a deterministic risk layer validates.

### Gaps
- I could not confirm from SPK's own site whether Binance TR holds a full licence in Oct 2026.
- I could not confirm whether Binance TR's API supports algorithmic trading, its order types, or its current fees. No 2026 source was found. Binance TR's API is believed to be spot-only.
- I found no source on whether Turkish residents face personal penalties (as opposed to providers) for using unlicensed foreign platforms.

## Liquidity and spread for BTC, ETH and SOL pairs

### Takeaway
For a retail-sized bot (under $10k per order), BTC, ETH and SOL against USDT/USDC on Binance, Bybit, OKX or Hyperliquid have effectively negligible spread and impact, about 1 bps or less. Fees and stop slippage in fast moves are the real costs. Hyperliquid's top-of-book BTC depth now rivals or beats Binance by one 2026 study. Its deeper book (±1%) is still thinner than the top CEXs.

### Cited Findings
- Blockworks Research (500 ms snapshots): resting BTC depth within ±1 bps was about $3.0M on Hyperliquid vs $2.1M on Binance, and within ±2 bps $5.8M vs $4.1M. Critics note Hyperliquid's cancel-priority speedbump makes displayed depth less "firm" than Binance's. — [Blockworks Research](https://blockworks-research.beehiiv.com/p/is-hyperliquid-hyper-liquid)
- OneKey's qualitative estimates (Apr 2026, self-described as "conceptual"): BTC perp spread is typically $0.50–2.00 on Hyperliquid vs $0.10–0.50 on top CEXs. Depth within ±1% is low millions USD on Hyperliquid vs tens of millions on top CEXs. — [OneKey](https://onekey.so/blog/ecosystem/hyperliquid-liquidity-depth-20260429/)
- Kaiko (Jan 2023, old): BTC and ETH USDT spreads are the tightest in the market, and venue choice can cost several bps. — [Kaiko](https://research.kaiko.com/insights/a-cheatsheet-for-bid-ask-spreads)

### Inferences
- A BTC spread of about $0.1–2 at roughly $100k+ BTC is about 0.01–0.2 bps, so it is irrelevant next to 3–11 bps of fees. SOL/USDT is less deep but still fine at retail size.
- Restrict the universe to the top 5–10 liquid pairs. Long-tail altcoins reintroduce spread and slippage that the small-target economics cannot absorb.

### Gaps
- I found no 2026 Kaiko or Coin Metrics quantitative depth figures for ETH and SOL per venue.

## Overall recommendation (synthesis)

### Takeaway
Ranking for this mandate (autonomous, fast stops, small wins, low risk):

1. **Binance USDⓈ-M futures, used at 1x–2x**, or **Hyperliquid perps**. These offer the lowest fees, exchange-resident reduce-only stops, deep BTC/ETH/SOL books, ccxt support and testnets.
2. **Binance (or Binance TR) spot with maker entries and OCO/OTOCO.** This is the simplest and has no liquidation risk, but fees force targets of at least 0.6–1%.
3. **Bybit and OKX.** These are functionally equivalent to Binance with marginally different fees.
4. **Jupiter**, for SOL/USDC only. There are no native stops.
5. **Pump.fun and memecoins.** Not suitable; rejected for this mandate.

The Turkey regulatory picture pushes toward Binance TR (spot) for full compliance. That is a real trade-off against the better economics of perps on global venues, and the user must decide it consciously.

### Cited Findings
- See the sections above. Key inputs:
  - perp fees of 0.015–0.02% maker and 0.045–0.055% taker ([Dwellir](https://www.dwellir.com/blog/hyperliquid-fees-explained), [Bitsgap](https://bitsgap.com/blog/bybit-trading-fees-explained-what-it-costs));
  - a pump.fun collapse rate of about 98.6% ([The Defiant](https://thedefiant.io/news/defi/alarming-99-of-memecoin-launches-on-pumpfun-are-pump-and-dumps-or-rug-pulls-report));
  - SPK status of global vs TR Binance ([Pega Hukuk](https://pegahukuk.com/binance-p2p/)).

### Inferences
- **Honest caveat.** No venue makes "many small low-risk wins" profitable by itself. Most short-term retail strategies lose after fees. The venue choice only lowers the hurdle, for example from an 83% to a 65% required win rate at a symmetric 0.3% take-profit and stop-loss.
- Prefer asymmetric targets, for example a 1% take-profit with a 0.5% stop, plus maker entries and a hard daily loss cap.
- Paper-trade on live data first.
- Leverage on perps should be used only for capital efficiency and the cheaper fees, not for amplifying risk. Cross-check that liquidation prices sit far beyond the stops.

### Gaps
- Live fee verification is still needed: Binance USDⓈ-M taker 0.04% vs 0.05%, and current Hyperliquid tiers.
- The availability and capabilities of the Binance TR API need direct checking.
