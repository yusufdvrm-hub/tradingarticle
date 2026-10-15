# X/Reddit, first-hand (2026-10-15)

Follow-up to `x_reddit_topluluk.md`, whose cloud session could not reach Reddit or X. This pass read the threads
themselves through agent-reach's OpenCLI backend (logged-in Chrome session, read-only). Reddit scores and comment
counts are as of 2026-10-15. X search hit its session rate limit (HTTP 429) after the first five queries, so X
coverage is thinner than Reddit.

**Reliability caveat for everything below.** Several of the most-upvoted r/algotrading posts of 2026 are about
the sub being flooded with AI-written posts and replies ("Dead Internet Theory in r/algotrading", 610 points,
[1q67z33](https://www.reddit.com/r/algotrading/comments/1q67z33/); "This sub is unusable", 279 points,
[1vomkhv](https://www.reddit.com/r/algotrading/comments/1vomkhv/)). Many replies quoted below read as LLM-written.
P&L claims are self-reported unless a repo or log is linked. Weight the *methods* people describe (IS/OOS splits,
pre-registration, cost models) over their headline numbers.

## 1. Does an LLM in the decision loop add edge? First-hand reports

**Takeaway:** every report with a head-to-head comparison says no. Where people measured an LLM gate against the
same signals without it, the plain rule won or the LLM's choices were worse than the trades it skipped. Nobody in
these threads showed a live, logged, multi-month profitable LLM-decided crypto system.

- **"Spent months on the AI layer of my trading platform. A frozen rule beats it."** (r/algotradingcrypto,
  2026-10, [1wzc8qh](https://www.reddit.com/r/algotradingcrypto/comments/1wzc8qh/)). Signal engine → XGBoost
  pre-filter → LLM (Llama) returning EXECUTE/SKIP with confidence, size, stop, target. That's the same shape as
  opusjev's jev gate, except jev doesn't set size or stops. The rule-only book was green while the LLM books gave
  back ~60% of that. In the author's follow-up over 4,000 signals with identical exits, the trades the LLM
  **executed** averaged −0.86% and the ones it **skipped** averaged −0.40%. The filter selected worse trades.
- **"I ran 24,000+ experiments testing AI vs rule-based systems for crypto trading"** (r/algotrading, 2026-04,
  [1ssiiv9](https://www.reddit.com/r/algotrading/comments/1ssiiv9/)). The claim: rule-based systems won in every
  configuration, and LLM non-determinism (same prompt, different answer) was the deciding problem. Score 0 and
  called "AI slop" in the comments, so it's weak evidence. Listed for completeness.
- **"Has anyone actually built a profitable trading workflow around Claude or ChatGPT… 3+ months real money?"**
  (r/algotradingcrypto, 2026-07, [1uo87ng](https://www.reddit.com/r/algotradingcrypto/comments/1uo87ng/)).
  - Most replies: the LLM helps write code; strategy ideas from it were "90% utter crap"; "asking a model to say
    up or down is a coin flip with extra steps."
  - The useful pattern named was turning qualitative input (filings, news) into a numeric score that feeds a
    normal model.
  - One reply claims a BERT → XGBoost → Opus cascade that is "live and profitable", with no numbers or logs.
- **"My GPT / Claude trading bot evolved! I gave ChatGPT $400 eight months ago"** (r/ClaudeAI, 2026-02, 429
  points, [1r35gpb](https://www.reddit.com/r/ClaudeAI/comments/1r35gpb/)). This is the thread the earlier note
  only saw through a mirror.
  - It turned into an S&P 500 options screener where GPT/Claude explains the output rather than deciding trades.
  - Asked about the result, the author answered "~$1200" from $400 after 8 months, with no log.
  - The author also said of an earlier version: "The old one did like 300%, but it was all BS. Just luck."
  - One commenter caught Claude "inserting imaginary volatility numbers" in a script it wrote for them.
- **"Claude algo bot week 2, 100% wins"** (r/algotrading, 2026-06, 530 points,
  [1uczfiw](https://www.reddit.com/r/algotrading/comments/1uczfiw/)). One TQQQ/SQQQ trade per day through
  Robinhood's agentic beta: 5 trades. Top replies point out that 5 wins is about a coin-flip streak. Equities,
  not crypto.

## 2. Out-of-sample results that practitioners report for crypto

**Takeaway:** these agree with our own finding. Directional technical strategies on liquid crypto (hourly
RSI/mean reversion/momentum, cross-sectional momentum) look good in-sample and flip negative out-of-sample.
The only things reported to survive are market-neutral premium harvesting, and even that is contested once
basis and execution are modelled.

- **"I backtested every popular crypto strategy out-of-sample. Almost all of them curve-fit."**
  (r/algotradingcrypto, 2026-05, [1tt3od5](https://www.reddit.com/r/algotradingcrypto/comments/1tt3od5/)).
  Optimized on the first 60% of history, then validated on the remaining 40% with parameters locked.
  - Hourly BTC mean reversion, momentum and RSI: all positive in-sample (RSI: Sharpe 1.06, +29.6%/yr) and all
    negative out-of-sample, with near-zero fees. The author's conclusion: curve-fit, not costs.
  - Cross-sectional momentum on 26 liquid coins: +54%/yr in-sample → −77%/yr out-of-sample. The author says
    the academic edge sits in microcaps you can't trade at size.
  - Cross-exchange and triangular arbitrage: dead after costs.
  - Survived: funding-rate carry (long spot / short perp) and covered calls when IV is high. Both are
    market-neutral.
  - A commenter reports the same pattern with evolved strategies: median in-sample PF ~2 deflating out of sample.
- **"Delta-neutral funding rate carry on BTC/ETH/SOL perps: pre-registered, falsified"** (r/algotradingcrypto,
  2026-07, [1uo3u1f](https://www.reddit.com/r/algotradingcrypto/comments/1uo3u1f/), code at
  [github.com/Mykola-Quant/funding-rate-carry-falsification](https://github.com/Mykola-Quant/funding-rate-carry-falsification)).
  - The rules were locked in a pre-registration file before any data was touched.
  - Negative out-of-sample in every symbol × variant.
  - BTC/ETH: round-trip costs of ~0.48% exceed funding income.
  - SOL: funding cleared costs in-sample (0.55% vs 0.48%), but drift between the spot and perp legs (−0.23%)
    ate it.
  - This contradicts the "carry survives" claim above. The difference is whether execution costs and basis
    are modelled per trade.
- **"Funding-rate 'APY' numbers are mostly fiction"** (r/algotradingcrypto, 2026-08,
  [1vuq8o0](https://www.reddit.com/r/algotradingcrypto/comments/1vuq8o0/)).
  - Carry has four fee legs.
  - The highest advertised rates sit in the thinnest order books; at £25k size almost all of them collapse to
    about zero after slippage.
  - Rates mean-revert within hours.
  - Majors net roughly 10–16% annualised at £1k size. The meme-coin yields are high precisely because the
    hedge is hard to hold.
  - The author runs a scanner product, so it's a vendor source.
- **"A model with zero directional information beats the trained direction model"** (r/algotradingcrypto,
  2026-10, [1x0mxht](https://www.reddit.com/r/algotradingcrypto/comments/1x0mxht/)).
  - LightGBM on ~530 Binance perps with 43 features: price, open interest, funding, long/short ratio, taker
    volume.
  - It used purged walk-forward validation and calibrated probabilities.
  - Its next-day direction forecast had a Brier score of 0.2525, versus 0.2532 for the trailing base rate and
    0.2500 for always saying 50%. No edge in any of 12 regime × volatility cells.
  - The author is switching from "will it go up" to "which coins will beat the market today" (relative
    prediction).
- **"8 months on a crypto bot… 71% of it from one year, DSR 0.319"** (r/algotradingcrypto, 2026-09,
  [1w607iq](https://www.reddit.com/r/algotradingcrypto/comments/1w607iq/)). 49 strategies × parameter sweeps
  (7,700+ combinations) on 12 coins, daily and 4h bars.
  - Most of the profit came from one year.
  - A Deflated Sharpe of 0.319 means it isn't significant after accounting for the number of trials.
  - The author concedes the out-of-sample test is clean per strategy but not for the selection process, since
    the gates and regime detector were built while seeing all 8 years.
- **"I backtested 324 parameter combinations"** (r/algotradingcrypto, 2026-07,
  [1uupxeg](https://www.reddit.com/r/algotradingcrypto/comments/1uupxeg/)). Hourly ETH-EUR with an
  EMA/ADX/RSI trend system.
  - Best on 3 years: +68.6%.
  - Rerun over 6.6 years at commenters' request, the median of the 324 combinations was −13.8%.
- **"I backtested 100+ retail trading strategies (~700 versions) with real costs and dead companies"**
  (r/algotrading, 2026-10, 270 points, [1x2owmo](https://www.reddit.com/r/algotrading/comments/1x2owmo/)).
  US stocks, not crypto.
  - Only three ideas held up.
  - Momentum's edge shrank once delisted stocks were included and older years were added.
  - A commenter's gold trend system: PF 1.07 over 2015–2026, with the pass bar (PF ≥1.2) written down before
    testing. Ours behaved the same way.
  - On hourly bars, the apparent edge was "a few 1-tick spikes that got eaten by gaps and slippage."
- **"Before you start any strategy development… an edge is a reason someone pays you"** (r/algotrading,
  2026-08, [1vsmrbs](https://www.reddit.com/r/algotrading/comments/1vsmrbs/)). Start from who pays you (forced
  traders, inventory unwinds, information arriving late) rather than from an indicator. Comments flag the post
  as AI-written, but the framing is standard among practitioners and it's the step our spec skipped.

## 3. Jev (TypeSafe) on Reddit and X

**Takeaway:** independent users describe Jev as a fast, cheap, zero-shot classifier that is useful for routing,
guardrails and smoke-tests on text. I found nobody showing it adds edge to trading. The trading-specific
material on X is promotional, and Reddit users report an astroturf campaign.

- **Benchmark of Jev against LLMs, BERT and Laya on healthcare voice-AI classification** (r/AI_India, 2026-09,
  [1wmvyqz](https://www.reddit.com/r/AI_India/comments/1wmvyqz/), code
  [github.com/dhruvmehra/jevbench](https://github.com/dhruvmehra/jevbench)). Text classification, not markets.
- **"Jev raised $40m… an open clone matched its api in 3 days"** (r/LLMDevs, 2026-09,
  [1wncmkp](https://www.reddit.com/r/LLMDevs/comments/1wncmkp/)).
  - The debate is about calibration. Jev is calibrated on TypeSafe's aggregate traffic, not on your data.
    "if you're serious you're refitting temperatures on your own data either way."
  - That bears on our fixed `p_take < 0.6` cut-off: a raw 0.6 from Jev isn't a calibrated probability for our
    trade outcomes.
- **"What Everyone Is Getting Wrong About TypeSafe AI's Jev"** (r/learnmachinelearning, 2026-09,
  [1wmhwdu](https://www.reddit.com/r/learnmachinelearning/comments/1wmhwdu/)).
  - Commenters: there is no architecture write-up and no third-party evals, while influencers do the
    marketing.
  - One user reports Jev isn't order-invariant: changing the order of the options changed its decisions.
  - That matters for our prompt, where the take/skip order and feature order are fixed but untested.
- **"Jev / TypesafeAI is revolutionary as LLM's"** (r/ArtificialInteligence, 2026-09, 188 points,
  [1wkhsyh](https://www.reddit.com/r/ArtificialInteligence/comments/1wkhsyh/)).
  - Second-highest comment (74 points): "This is an astroturfed post. It has the exact same messaging that's
    plastered all over X ('Jev is insane')… They hired a marketing firm."
  - Users who report real use describe a pre-filter in front of an expensive LLM call, cutting cost 70–80% and
    latency from seconds to milliseconds.
- **X, the same Jev trading copy on three accounts.** The same text ("honestly this should be f*cking illegal…
  Jev answers in 70 to 500 milliseconds… returns BUY / SELL / HOLD and a probability") appeared on
  [@thegreatest_sv](https://x.com/i/status/2107851693232975941) on 2026-10-07, then on
  [@ch3nweiii](https://x.com/i/status/2109024479691104494) and [@Asteri_eth](https://x.com/i/status/2108869799199592586)
  on 2026-10-10. Identical copy across accounts points to a coordinated campaign, and none of the three shows
  results. Our own measurement: about 0.8 s per call over the network, not 70–500 ms.
- **X, the most-viewed Jev trading posts (from 2026-09-16, launch week):**
  - [@MoonGotchi, 2026-09-19](https://x.com/i/status/2101320141065609294) (24k likes, 1.4M views): "Jev is
    INSANE. I built this in an evening… a real-time trading bot… Fully autonomous. So far it has lost me
    $31,680." It parodies the hype format, but the loss is presented as real and was reshared as "Someone lost
    $32k automating a trading bot using jev". This is the only Jev-trading P&L figure I found, and it's negative.
  - [@jarrodwatts, 2026-09-16](https://x.com/i/status/2100356151468585346) (5k likes): a demo bot that asks Jev
    "buy or sell" on a price feed every 300 ms block on Monad. It's a demo with no P&L. Others promote
    "jev-trader" ([@RoundtableSpace](https://x.com/i/status/2101850147378376897)) and an "HFT with Jev" article
    ([@RohOnChain](https://x.com/i/status/2101311813908652069), 5.5M views) claiming "calibrated buy/sell
    decisions in under 100 ms". Neither shows results.
  - Claims like "$100 → $23,879" ([@savipww](https://x.com/i/status/2107411099477832032)) have no verifiable
    logs. They read as engagement farming.
  - Same week, a counterpoint ([@arixxbt, 2026-10-08](https://x.com/i/status/2108237167780589774)): 1,000
    coin-flip bots on pure-noise prices, fees included, and the best one turned $1,000 into $8,120. It
    illustrates the survivorship behind "my bot made X" posts.

## 4. Alpha Arena (from X, primary)

- **Season 1.5 final** ([@jay_azhang, 2025-12-05](https://x.com/i/status/1996984618751611006), 2.6k likes): the
  "Mystery Model" (Grok 4.20) won, up 12% on average and profitable in all four competitions; GPT-5.1 came
  second and Gemini 3 third. This is the founder's own post and confirms what the earlier note had only from
  secondary sources.
- **Season 2:** as of 2026-10-15, X searches turned up only teasers ("Season 2 coming", promotional account,
  2026-05) and no leaderboard. Grok's own reply on 2026-03-01 also says nothing after Season 1.5.

## 5. What this means for opusjev

- Our three negative results match what others report with the same method: directional technical entries,
  15m–1h, liquid majors, optimized then validated. Others found the same failure independently, so it's
  unlikely to be a bug in our engine.
- Head-to-head reports of LLM gates are negative. The [1wzc8qh](https://www.reddit.com/r/algotradingcrypto/comments/1wzc8qh/)
  case is the closest analogue to jev-as-filter, and its filter chose worse trades than the ones it skipped.
  So even if a signal survives out-of-sample, the jev-versus-shadow ablation is a real test, not a formality.
  Calibrate jev's `p_take` on our own outcomes before trusting the 0.6 cut-off.
- The only class reported to survive is market-neutral premium harvesting (funding carry, option premium).
  Even that was falsified once costs and basis drift were modelled at small size. It also isn't the
  "short-term directional" bot the spec describes.
- If the project continues, the practitioner advice that fits:
  - start from a mechanism (who pays and why), not from an indicator;
  - pre-register the pass bar and the variants before touching data;
  - deflate results for the number of trials.

## Gaps

- X has a per-session rate limit: 5 searches, a 20-minute cooldown, then 5 more.
  - "Hourly mean reversion overfit" returned nothing.
  - "Out-of-sample crypto failed" errored.
  - The "Hyperliquid LLM bot" search surfaced only paper-trading diaries (e.g. a Grok-run bot at $52 → $38.44
    after 30 trades, [@VBahenan](https://x.com/i/status/2109297127734014346)).
  - X is mostly promotional for this topic; Reddit carried almost all the methodical material.
- No first-hand Jev-in-trading results with logs were found anywhere. The one P&L figure (−$31,680) has no
  log either.
- Reddit search relevance is loose; "top of year" sorting surfaces popular posts that only loosely match the
  query. Threads were picked by hand from those lists.
