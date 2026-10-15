# System Architecture & Paper-Trading Path for an LLM-Orchestrated Crypto Bot (Claude orchestrator + "jev" decision module + deterministic risk layer)

Research date: 2026-10-14. Several primary-doc domains (freqtrade.io, hummingbot.org, developers.binance.com) failed DNS from the research sandbox; Freqtrade and ccxt facts were taken directly from their GitHub source/docs (raw.githubusercontent.com), Hummingbot and Binance facts from search snippets of their official pages. Claude pricing was fetched live from platform.claude.com.

## 1. Layered design — which parts must be deterministic vs LLM

### Takeaway
Everything that touches money, timing, or exchange state (data ingestion, indicators, position sizing, risk limits, order placement, reconciliation, kill switch) must be deterministic code; the LLM layer ("jev" and/or Claude) should only emit a bounded, schema-validated *proposal* (e.g., `{action: long|short|flat|hold, symbol, confidence, thesis}`) that the risk manager can veto or resize. Real-money benchmarks show LLMs trading directly are high-variance and frequently lose money, which reinforces keeping them out of the hot path.

### Cited Findings
- Freqtrade explicitly warns that strategy callbacks run inside the trading loop and "you should avoid doing heavy calculations in callbacks to avoid delays during operations" — i.e., slow operations (like an LLM call) in the execution loop are a known hazard. — [Freqtrade strategy-callbacks docs (GitHub)](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/strategy-callbacks.md)
- Freqtrade exposes `confirm_trade_entry()` which "can be used to abort a trade entry at the latest second", plus `custom_stake_amount`, `custom_stoploss`, `custom_exit`, `adjust_trade_position`, `leverage` callbacks — natural hook points for an external veto/decision module. — [Freqtrade strategy-callbacks docs](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/strategy-callbacks.md)
- nof1 "Alpha Arena" Season 1 (Oct–Nov 2025; LLMs trading $10k each on Hyperliquid perps with identical prompts): Qwen3-Max +22.3%, while Claude Sonnet 4.5 −30.8%, Grok 4 −45.3%, Gemini 2.5 Pro −56.7%, GPT-5 −62.7% (final figures from a secondary/vendor blog). Mid-run snapshots ranked models very differently, showing high variance. — [helloacm summary](https://helloacm.com/alpha-arena-how-ai-performs-in-the-real-crypto-market/); [Decrypt](https://decrypt.co/345006/ai-crypto-trading-showdown-deepseek-grok-winning-gemini-implodes); [Benzinga: "ChatGPT lost 63%"](https://fr.benzinga.com/quote/cryptocurrency/25/11/48651974/chatgpt-lost-63-trying-to-trade-crypto-but-one-china-ai-made-a-healthy-profit)
- Alpha Arena Season 1.5 (2 weeks to ~Dec 2025): only one model (later identified as Grok 4.20, +12% avg) remained profitable as of Dec 8; commentators attributed losses partly to frequent trading/fees. — [Forklog](https://forklog.com/en/ai-model-grok-4-2-triumphs-in-trading-tournament/amp); [buildix blog (vendor)](https://www.buildix.trade/blog/nof1-alpha-arena-lessons-ai-trading-byok-strategy-advisor-2026)
- Claude structured outputs: "Numeric constraints: `minimum`, `maximum`, `multipleOf` are not supported by the API" (SDK helpers move them into descriptions and validate locally) — so bounds on size/leverage cannot be enforced by the model schema alone and must be re-checked in code. — [Claude structured outputs docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs.md)

### Inferences
Recommended layer split (deterministic = D, LLM = L):
1. **Market data ingestion (D)** — exchange WebSocket streams (klines, trades, book ticker/depth) via ccxt.pro or the exchange SDK; REST backfill on gaps; sequence/timestamp checks; stale-data watchdog that blocks trading if feed > N seconds old.
2. **Feature/indicator engine (D)** — pandas/numpy/TA-Lib on closed bars only (no look-ahead); same code path for backtest, sim, and live.
3. **Signal engine (D)** — rule-based candidate generator (e.g., breakout, mean reversion). Produces *candidates*, which is what gates LLM spend.
4. **LLM decision layer (L)** — "jev" as a pluggable `DecisionProvider` interface (`decide(context) -> Proposal`), with Claude as either the orchestrator/reviewer or an alternate provider. Input: compact feature snapshot + open positions + recent PnL + regime notes; output: strict JSON proposal. Timeout (e.g., 10–20 s) → default to `hold`.
5. **Risk manager with veto (D)** — hard limits independent of the LLM: max position size % equity, max leverage, max concurrent positions, per-symbol exposure, daily loss limit, max drawdown circuit breaker, min time between trades, whitelist of symbols, price-sanity (proposed entry within X% of last price), mandatory stop-loss. Can reject or downsize; never upsizes.
6. **Execution/order manager (D)** — idempotent client order IDs, order-state machine, exchange filters (tick size/lot size/min notional), stop orders placed on exchange, retries with backoff, rate-limit compliance.
7. **State store (D)** — SQLite/Postgres: orders, fills, positions, equity curve, every LLM request/response + risk verdict (audit log).
8. **Monitoring/alerting (D)** — Telegram alerts, heartbeat, Prometheus/Grafana or simple dashboard; kill switch.
9. **Claude as orchestrator (L, off the hot path)** — periodic regime reviews, daily report generation, anomaly triage, parameter-change *proposals* that require human approval; not per-tick order routing.
- Design principle: LLM outputs are *advice*; the system must remain safe (flat or protected by exchange-side stops) if the LLM is down, slow, or wrong.

### Gaps
- No primary-source engineering write-up found describing a production LLM-in-the-loop crypto bot architecture; layered design above is synthesized from framework docs and general practice.

## 2. LLM in the loop — cost, latency, call frequency, guardrails

### Takeaway
At current (Oct 2026) Claude prices a compact decision call costs roughly $0.0005 (Haiku 5.5) to ~$0.01–0.02 (Opus 5.5) excluding thinking tokens, so calling per *candidate signal* (tens/day) is cheap, while calling per bar across many pairs (thousands/day) multiplies cost and latency; use structured outputs/strict tools plus deterministic re-validation to prevent hallucinated orders.

### Cited Findings
- Current Claude API prices per MTok (input / 5m cache write / 1h cache write / cache hit / output): **Opus 5.5** $4 / $5 / $8 / $0.20 / $20; **Sonnet 5.5** $2 / $2.50 / $4 / $0.10 / $10; **Haiku 5.5** (prompts ≤100k) $0.10 / $0.125 / $0.20 / $0.01 / $0.50 (prompts >100k: $0.50 in / $2.50 out); Fable 5.1 $10 / $50. — [Claude pricing docs](https://platform.claude.com/docs/en/about-claude/pricing.md)
- Cache hits cost 0.1× base input generally, 0.05× on Opus 5.5 and Sonnet 5.5; 5-minute cache write 1.25×, 1-hour write 2×; "caching pays off after one cache read for the 5-minute duration". — [Claude pricing docs](https://platform.claude.com/docs/en/about-claude/pricing.md)
- Batch API gives 50% discount on input and output (async; suitable for nightly reviews/backtest labeling, not live decisions). Opus 5.5 batch: $2/$10 per MTok. — [Claude pricing docs](https://platform.claude.com/docs/en/about-claude/pricing.md)
- Tool use adds a tool-use system prompt of 286 tokens for Opus 5.5 / Sonnet 5.5 / Haiku 5.5 (auto/none). — [Claude pricing docs](https://platform.claude.com/docs/en/about-claude/pricing.md)
- Fast mode for Opus 5.5 ($8/$40 per MTok, up to ~2.5× faster output) is Claude-API only. — [Claude pricing docs](https://platform.claude.com/docs/en/about-claude/pricing.md); Anthropic claude-api skill reference (bundled docs, cached 2026-10-06)
- Opus 5.5: thinking cannot be disabled; effort (`low`…`max`, default `medium`) is the control. Sonnet 5.5: `thinking: {type: "between_tools"}` turns thinking off. Forced `tool_choice` (`any`/`tool`) returns 400 on Opus 5.5/Sonnet 5.5 — use `auto` + `strict: true` or structured outputs. — Anthropic claude-api skill reference (bundled, cached 2026-10-06; mirrors platform.claude.com model-migration docs)
- Structured outputs (`output_config.format` with `json_schema`) use constrained decoding: "Claude returns valid JSON that matches your schema"; `strict: true` on tools guarantees schema-valid tool inputs. Supported on Opus 5.5, Sonnet 5.5, Haiku 5.5 and others. — [Claude structured outputs docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs.md)
- Caveats: on `stop_reason: "refusal"` or `"max_tokens"` output may not match schema; enum values may differ in capitalization; schema grammars compile on first use and are cached 24 h; changing `output_config.format` invalidates the prompt cache; `minimum/maximum` not supported; `additionalProperties` must be false. — [Claude structured outputs docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs.md)
- Prompt caching is prefix-based (tools → system → messages); volatile content (timestamps) must go after the last breakpoint or the cache silently misses; 5-minute TTL is refreshed by each read, so calls < 5 min apart keep it warm. — Anthropic claude-api skill, prompt-caching reference (bundled; mirrors [prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching.md))

### Inferences
- **Worked cost example (my arithmetic, ex-thinking tokens):** per decision = 3,000-token cached static prefix (instructions + schema + tool defs) + 1,500 fresh tokens (feature snapshot, positions) + 300 output tokens.
  - Haiku 5.5: 3000×$0.01 + 1500×$0.10 + 300×$0.50 per MTok ≈ **$0.0003/call**.
  - Sonnet 5.5: 3000×$0.10 + 1500×$2 + 300×$10 ≈ **$0.0063/call**.
  - Opus 5.5: 3000×$0.20 + 1500×$4 + 300×$20 ≈ **$0.0126/call**.
  - Thinking tokens are billed as output tokens (standard Anthropic billing; verify) and can easily be several hundred to thousands of tokens — budget 2–5× the above for Opus at medium effort; use `effort: low` for routine calls.
- **Frequency tiers to stay within a credit budget:**
  - Per bar for every pair (e.g., 10 pairs × 5-min bars = 2,880 calls/day): ~$18/day on Sonnet 5.5, ~$36+/day on Opus 5.5 → generally not worth it.
  - **Per candidate signal (recommended)**: deterministic signal engine fires maybe 10–50 candidates/day → <$1/day on Sonnet, ~$0.5–2/day on Opus incl. thinking.
  - **Hourly/4-hourly regime review** (Claude orchestrator, larger context, Opus): 6–24 calls/day → ~$0.5–3/day.
  - **Daily post-mortem/report**: Batch API at 50% off.
  - Implement a hard daily LLM spend cap in code (count `usage` tokens × price) — when exceeded, fall back to deterministic-only or `hold`.
- **Latency:** For 1m–5m scalping, a multi-second LLM round-trip plus thinking makes the LLM unsuitable as a per-tick decider; it fits 15m+ bars or "approve/reject this candidate" roles. Pre-place exchange-side stop-loss so exits never wait on the LLM.
- **Guardrails against hallucinated orders:**
  1. Strict JSON schema with enums (`action ∈ {open_long, open_short, close, hold}`, `symbol ∈ whitelist`), `additionalProperties: false`.
  2. LLM proposes *intent + confidence*, never raw quantity; risk manager computes size from equity and stop distance.
  3. Re-validate numerics in code (since `minimum/maximum` are not enforced): price within ±X% of mid, stop on correct side, R:R ≥ threshold, leverage ≤ cap.
  4. Check `stop_reason` (refusal / max_tokens) → treat as `hold`.
  5. Case-insensitive enum compare; reject unknown symbols.
  6. Idempotency: one proposal ID → at most one order; dedupe repeated proposals.
  7. Prompt-injection hygiene: if news/social text is fed in, pass it as data and never let it change risk params.
  8. Same guardrail wrapper applies to "jev" regardless of provider — define a provider-agnostic `Proposal` pydantic model.

### Gaps
- No published measured latency (TTFT/total) figures for Opus 5.5 / Sonnet 5.5 / Haiku 5.5 were found; measure in-environment.
- "jev" is unspecified — its pricing/latency could not be researched; treat it as a provider behind the same interface.

## 3. Paper-trading options and recommended progression

### Takeaway
Use a staged pipeline: (1) vectorized/event backtest on historical data → (2) local paper simulator (or Freqtrade dry-run) fed by *live* mainnet data → (3) exchange testnet/demo for API/order-lifecycle integration → (4) small live capital. Each environment has blind spots: dry-run/sim fills are optimistic, testnets have unrealistic liquidity and periodic resets.

### Cited Findings
- **Freqtrade dry-run:** simulated wallet starting at `dry_run_wallet` (default 1000; can be per-currency dict); orders "are simulated, and will not be posted to the exchange"; "Market orders fill based on orderbook volume the moment the order is placed, with a maximum slippage of 5%"; limit orders fill "once the price reaches the defined level" or time out; limit orders crossing price by >1% become market orders; with `stoploss_on_exchange` "the stop_loss price is assumed to be filled"; open orders kept open after restart "with the assumption that they were not filled while being offline". API keys optional (read-only ops only). Separate DB recommended when switching to live "to avoid dry-run trades ... tainting your statistics". — [Freqtrade configuration docs (GitHub)](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/configuration.md)
- Freqtrade `fee` config: "Fee used during backtesting / dry-runs ... falls back to the exchange default fee ... applied twice for each trade". — [Freqtrade configuration docs](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/configuration.md)
- Freqtrade on Binance Futures: must follow Binance "Futures Trading Quantitative Rules"; orderbook must be used for pricing; requires One-way position mode & Single-Asset mode for isolated futures. — [Freqtrade exchanges docs](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/exchanges.md)
- **ccxt sandbox:** `exchange.set_sandbox_mode(True)` must be called "immediately after creating the exchange before any other call"; sandbox keys must be created on the exchange's sandbox site. — [ccxt Manual (GitHub)](https://raw.githubusercontent.com/ccxt/ccxt/master/wiki/Manual.md)
- ccxt binance source maps sandbox ("test") URLs to `testnet.binance.vision` (spot) and `testnet.binancefuture.com` (futures), and has a separate `enable_demo_trading()` mode mapping to `demo-api.binance.com` / `demo-fapi.binance.com` / `demo-dapi.binance.com`; demo trading raises NotSupported if sandbox mode is enabled. — [ccxt binance.py source](https://raw.githubusercontent.com/ccxt/ccxt/master/python/ccxt/binance.py)
- ccxt's comparison page states testnet via `setSandboxMode` is not supported for the `binanceusdm` class (use `binance` class with futures options or demo trading). — [ccxt vs Binance USDⓈ-M API](https://docs.ccxt.com/docs/comparisons/ccxt-vs-binanceusdm-api)
- **Binance Spot Testnet:** data periodically deleted ("periodic reset", e.g., 2026-08-05 and 2026-09-09); "Testnet features are not always synced with the live exchange" and some settings (e.g., price range rules) "may not be indicative of settings on the live exchange". Binance also runs a separate **Spot Demo Mode** with its own changelog/maintenance. — [Binance Spot Testnet changelog](https://developers.binance.com/en/docs/products/spot/testnet/CHANGELOG); [Binance Spot Demo Mode changelog](https://developers.binance.com/docs/binance-spot-api-docs/demo-mode/CHANGELOG)
- **Hummingbot paper trade:** enabled per exchange via `paper_trade_exchanges` in `conf_client.yml` (default list includes Binance, KuCoin, Kraken, Gate.io); connect `<exchange>_paper_trade`; default simulated balances (BTC, ETH, SOL, USDC, USDT, …); API keys not required for some strategies; go live by choosing the connector without the `_paper_trade` suffix. — [Hummingbot paper trade docs](https://hummingbot.org/global-configs/paper-trade/)
- General: simulations fill orders fully whereas live limit orders may partially fill; slippage from low volume/market impact is not reflected. — [Capitalise.ai: differences between modes](https://support.capitalise.ai/en/articles/6148015-differences-between-modes)

### Inferences
| Option | Pros | Cons |
|---|---|---|
| Binance Spot/Futures testnet (via ccxt sandbox) | Real API, real order lifecycle, auth, filters, WebSocket user streams — best for integration tests | Thin/unrealistic order books and prices diverge from mainnet; periodic resets wipe state; feature drift vs live → PnL there is meaningless |
| Binance Demo Trading (ccxt `enable_demo_trading`) | Closer to mainnet-like market experience per Binance; separate keys | Still simulated matching; verify fee/liquidity realism; maintenance windows |
| ccxt sandbox generally | One flag switch, same code as live | Only as good as the exchange's testnet |
| Freqtrade dry-run | Mature, live mainnet data, orderbook-aware market fills, fees, Telegram/FreqUI, same strategy runs live | Optimistic fills (limit = touched → filled, stops assumed filled, no queue position); LLM calls must be kept out of slow callbacks; framework conventions (candle-based) |
| Hummingbot paper trade | Good for market-making/limit-order strategies, many connectors | Paper connector simplifications; Hummingbot geared to MM/arbitrage rather than directional LLM strategies |
| Custom local simulator on live/replayed L2 + trades | Full control: fee tiers, latency injection, queue-position model, partial fills, funding; can replay recorded data deterministically for regression | Most engineering effort; easy to build subtly optimistic fills |

Recommended combination:
1. **Backtest** (Freqtrade backtesting or custom event-driven) with fees + slippage; for LLM-dependent logic, replay recorded LLM decisions or run a cheap model in Batch mode to limit cost and avoid look-ahead (note: LLM training data may "know" historical prices → backtest of LLM judgment is contaminated; forward testing is the real test).
2. **Forward paper on live mainnet data** (Freqtrade dry-run or own simulator) for 2–4+ weeks — this is the primary evaluation gate. Add pessimistic fill rules (limit fills only if price trades *through* the level; extra 1–2 bps slippage; taker fees by default).
3. **Testnet/Demo** in parallel for 1 week to validate order placement, rejections, reconnects, user-data stream, reconciliation — not for PnL.
4. **Small live** (e.g., 5–10% of intended capital, minimum order sizes) with all kill switches, then scale stepwise.

### Gaps
- Could not fetch Binance's current testnet/demo documentation directly (DNS failure); base URLs above come from ccxt source, not Binance docs. Demo mode fee/liquidity realism not verified.
- Hummingbot paper-trade fill model details (slippage/fees) not confirmed from primary docs.

## 4. Go-live gate criteria used by practitioners

### Takeaway
There is no industry standard; practitioner thresholds cluster around a minimum sample (≈40–200+ trades), multi-week duration spanning more than one regime, profit factor ≳1.3–1.5 after fees, a pre-defined max drawdown cap, positive net expectancy per trade after fees/slippage, and live/paper consistency with backtest — followed by a small-size live pilot with hard loss limits.

### Cited Findings
- Example forward-test template: min 40 trades over 60 days; promote only if max drawdown < 5% and profit factor > 1.5 (vendor sample plan, not authority). — [agensi forward-test readiness lab](https://www.agensi.io/skills/forward-test-readiness-lab)
- Aspirational "holy grail" targets: profit factor > 3 and annual drawdown < 3% (research goal, not go-live bar). — [Automated Trading Strategies (Substack)](https://automatedtradingstrategies.substack.com/p/if-you-havent-found-the-holy-grail)
- Regime coverage matters more than raw trade count — months of one-way market only test one regime. Paper fills are "the optimistic case, no real slippage or partial fills". Recommended: go live small with max daily loss, max trades, max position size, kill switch. — [Reddit snapshot (community discussion)](https://reddit.sentinel-team.org/posts/1tdeu7b/snapshots/2026-05-15T19%3A02%3A50.96329Z); [Elite Trader: Paper trading goals](https://elitetrader.com/et/threads/paper-trading-goals.285671/)
- Net average profit per trade after commission and slippage highlighted as key metric. — [BabyPips forum](https://forums.babypips.com/t/backtesting-of-strategy-before-going-live/313929)
- Alpha Arena: overtrading/fees cited as a driver of LLM losses → trade count alone is not a virtue. — [buildix blog](https://www.buildix.trade/blog/nof1-alpha-arena-lessons-ai-trading-byok-strategy-advisor-2026)

### Inferences
Proposed concrete gate (all must pass, measured on forward paper with pessimistic fills, net of fees, funding and LLM cost):
- Sample: **≥ 200 closed trades** for a short-term bot (≥ 100 absolute minimum) **and ≥ 3–4 weeks**, covering at least one up, down and chop period (or explicitly label the regime gap).
- **Profit factor ≥ 1.3** (prefer ≥ 1.5); **expectancy > 0** with 95% bootstrap CI lower bound > 0, *after* fees + slippage + LLM API cost.
- **Max drawdown ≤ 10%** of paper equity (or ≤ ½ of the drawdown you'd tolerate live); no single day worse than the daily loss limit.
- **Sharpe (daily) ≥ 1** annualized-ish over the window, noting short-sample noise.
- **Consistency:** forward-paper win rate, avg win/loss and trade frequency within ~±25–30% of backtest; if paper is much better than backtest, suspect a bug.
- **Operational:** zero unreconciled position mismatches; zero risk-limit breaches; 99%+ uptime; all LLM failures defaulted to safe `hold`; every decision logged.
- **LLM ablation:** LLM-filtered strategy must beat the same deterministic signals without the LLM (A/B shadow run) — otherwise the LLM is only adding cost.
- Live pilot: small capital, same criteria re-evaluated after ~50–100 live trades; auto-demote to paper if live drawdown > X or live expectancy diverges from paper.

### Gaps
- No authoritative/academic standard for minimum trade counts or PF thresholds was found; figures above are judgment synthesized from practitioner sources.

## 5. Operations — 24/7 running, security, recovery, audit

### Takeaway
Run in Docker on a static-IP VPS (systemd or `restart: unless-stopped`), keep secrets out of code, use trade-only exchange keys with withdrawals disabled and IP whitelisting, enforce a multi-level kill switch, alert via Telegram, log every LLM decision with rationale, and reconcile local state with the exchange on every start and periodically.

### Cited Findings
- Bot API keys should have only Read + Trade permissions; withdrawals disabled in case the key leaks. Binance offers "IP Access Restriction" — untick "Unrestricted" and fill "Restrict Access to IPs". — [Binance Square: API key security](https://www.binance.com/ar/square/post/352164452539201); [Cobo manual: generate Binance API key](https://manuals.cobo.com/en/portal/exchange-wallets/generate-binance-api-key)
- Reported Binance policy: unrestricted (no IP whitelist) keys with trading permission get deleted after inactivity (~30 days) / 90 days — vendor and forum claims, not verified against Binance docs. Most cloud platforms lack fixed outbound IPs, so a VPS with static IP or fixed-egress proxy is needed for whitelisting. — [QuotaGuard (vendor)](https://www.quotaguard.com/blog/binance-api-ip-whitelist-cloud-static-ip); [CoinTracker forum](https://feedback.cointracker.io/features/p/binance-api-key-whitelisting)
- Freqtrade: dry-run DB defaults to `tradesv3.dryrun.sqlite`, live to `tradesv3.sqlite`; open orders persist across restarts; separate DB recommended for live. — [Freqtrade configuration docs](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/configuration.md)
- In Freqtrade dry-run, open orders after restart are assumed not filled while offline — i.e., the framework does *not* reconstruct missed fills in simulation; live recovery relies on exchange queries. — [Freqtrade configuration docs](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/configuration.md)

### Inferences
- **Hosting:** VPS near exchange region (e.g., Tokyo/Singapore/Frankfurt for Binance — verify), static IP, Docker Compose services: `ingest`, `bot` (strategy+risk+execution), `db` (Postgres), `monitor`; `restart: unless-stopped` or systemd unit with `Restart=always`; NTP time sync (exchange signed requests reject clock skew).
- **Secrets:** `.env` excluded from git or Docker secrets / SOPS / cloud secret manager; separate keys per environment (testnet/demo/live); Anthropic API key with a workspace spend limit; rotate regularly.
- **Exchange key hygiene:** Read+Trade only, withdrawals off, IP whitelist, sub-account with only the capital at risk, futures leverage capped at the account level too.
- **Kill switch levels:** (a) automatic: daily loss limit / max DD / stale data / repeated order errors / LLM spend cap → stop new entries; (b) panic: cancel all + flatten; (c) manual: Telegram `/stop`, `/flatten`, file flag, and ultimately revoking the API key.
- **Alerts:** Telegram bot for fills, risk vetoes, errors, heartbeat (missing heartbeat → external watchdog alert, e.g., healthchecks-style ping).
- **Audit log:** for every decision store timestamp, input snapshot hash + features, model/provider ID & version, prompt version, raw response, parsed proposal, rationale text, token usage/cost, risk verdict (+reasons), resulting order IDs. Enables post-mortems and LLM-vs-baseline evaluation.
- **Crash recovery/reconciliation:** on startup and every N minutes: fetch open orders, positions, balances, recent fills from exchange; diff vs DB; exchange is source of truth; resolve orphan orders (cancel or adopt), missing stops (re-place), unknown positions (alert + flatten or adopt per policy); use deterministic `clientOrderId` so retries don't duplicate orders; don't trade until reconciliation passes.

### Gaps
- Binance's official current API-key policies (auto-deletion, withdrawal-whitelist requirements) could not be confirmed from Binance's own docs.

## 6. Recommended tech stack — build vs extend

### Takeaway
Python is the default; the pragmatic path is **extend Freqtrade** (dry-run, backtesting, Telegram, persistence, exchange quirks already solved) with the LLM call moved to an asynchronous side-service whose cached verdicts are consumed in `confirm_trade_entry()`/`custom_exit()`, or **build a lean custom core on ccxt/ccxt.pro** if the LLM-centric, event-driven, multi-model orchestration is the main product. Hummingbot fits market-making better than directional LLM trading.

### Cited Findings
- Freqtrade provides dry-run with simulated wallet, persistence DB, fee handling, Binance spot/futures support, and strategy callbacks (`confirm_trade_entry`, `custom_stake_amount`, `custom_stoploss`, `custom_exit`, `adjust_trade_position`, `leverage`, `order_filled`). — [Freqtrade configuration docs](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/configuration.md); [Freqtrade strategy callbacks](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/strategy-callbacks.md); [Freqtrade exchanges](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/exchanges.md)
- Freqtrade cautions against heavy computation inside callbacks. — [Freqtrade strategy callbacks](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/strategy-callbacks.md)
- ccxt unifies 100+ exchanges, sandbox switching via one call, Binance demo-trading mode; ccxt publishes a "build your first trading bot" tutorial. — [ccxt Manual](https://raw.githubusercontent.com/ccxt/ccxt/master/wiki/Manual.md); [ccxt blog](https://docs.ccxt.com/blog/build-your-first-crypto-trading-bot)
- Hummingbot paper trade connectors per exchange; primarily designed around market-making strategies (Pure MM, Cross-Exchange MM, Avellaneda). — [Hummingbot paper trade docs](https://hummingbot.org/global-configs/paper-trade/)
- Claude surfaces: Claude API + tool use (you own the loop), Tool Runner, Managed Agents (Anthropic-hosted loop+sandbox), and Claude Agent SDK (Claude Code harness as a library, you host). — Anthropic claude-api skill reference (bundled); [Agent SDK docs](https://code.claude.com/docs/en/agent-sdk)

### Inferences
| | Extend Freqtrade | Build on ccxt (+ccxt.pro) |
|---|---|---|
| Time to paper trading | Days | Weeks |
| Dry-run/backtest/Telegram/FreqUI | Built-in | Must build |
| LLM integration | Must keep async (sidecar service writes verdicts to Redis/DB; callbacks read with timeout) | Native async event loop, natural fit |
| Fill realism control | Fixed dry-run model (optimistic) | Fully customizable |
| Multi-provider (jev + Claude) orchestration | Awkward inside strategy class | Clean `DecisionProvider` abstraction |
| Risk | Framework conventions, candle-centric | More bugs in execution/reconciliation code you write |

- **Suggested concrete stack:** Python 3.12, `ccxt`/`ccxt.pro` (or Freqtrade), `pydantic` for Proposal schemas, `anthropic` SDK (Messages API with structured outputs, prompt caching; `claude-sonnet-5-5` or `claude-haiku-5-5` for per-candidate calls, `claude-opus-5-5` for regime reviews/orchestration), Postgres or SQLite, Redis (optional), Docker Compose, `python-telegram-bot`, Prometheus/Grafana or simple FastAPI dashboard.
- **Role of Claude Agent SDK/Claude Code:** best used for development, offline analysis, daily report generation, and supervised parameter proposals — not as the always-on low-latency trading loop (its harness is built for agentic coding/file tasks). The live decision path should be plain Messages API calls with strict schemas.
- **Hybrid recommendation:** Start with Freqtrade dry-run + LLM sidecar to get a working paper bot quickly and generate forward-test statistics; if the fill model or callback constraints become limiting, migrate execution to a custom ccxt core while keeping the same `DecisionProvider` and risk modules.

### Gaps
- Could not access freqtrade.io/hummingbot.org directly for any 2026-specific LLM/AI plugin features (e.g., FreqAI updates); no first-party "LLM strategy plugin" found for either framework.
