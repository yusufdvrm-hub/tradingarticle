# X/Reddit community experience: autonomous and LLM-driven crypto trading bots (2024–2026)

> Method note: from this sandbox, reddit.com, old.reddit.com, Reddit's `.json` endpoints and most news domains could not be fetched directly: the proxy returned 403 or DNS failed for reddit.com, cointelegraph.com, forklog.com, li.fi, iweaver.ai and buildix.trade. Web search worked, and github.com pages could be fetched. As a result, most findings below come from search-engine summaries and secondary coverage of Reddit and X posts, not from reading the threads themselves. Unless marked "verified", treat every P&L figure as self-reported or secondary.

## 1. What do Reddit communities report about LLM-driven trading bots (P&L, post-mortems, "I gave Claude/GPT $X")?

### Takeaway
Community "I gave ChatGPT/Claude $X" experiments are almost all small, short and self-reported, with no trade logs. Most cover stocks or options rather than crypto. Experienced r/algotrading-style practitioners consistently say an LLM without grounded live data hallucinates, and that an LLM's value has to be proven against a mechanical baseline. I found no auditable, long-horizon, profitable LLM crypto bot posted on Reddit.

### Cited Findings
- **r/algotrading (via a mirror): a Claude-connected agentic account on Robinhood's beta.** It traded only TQQQ or SQQQ once a day. The poster reported a winning streak over 5 days and backtest figures of 45% annualized return, 6.6% max drawdown and 2.07 Sharpe, and admitted that half the backtest was in-sample. Self-reported, equities not crypto. — [r/algotrading mirror](https://r.datuan.dev/r/algotrading/rising), surfaced via search summary
- **r/algotrading-linked post: $400 given to ChatGPT.** On day 2 the model told the author it could not see live stock prices, and the author ended up building their own platform. This is an anecdote that shows the "no grounded data" failure. — [mirror snapshot](https://reddit.sentinel-team.org/posts/1r35gpb/snapshots/2026-02-13T00%3A02%3A56.654302Z) (search summary only; the page itself could not be fetched)
- **Claude 3.7 Sonnet experiment with live financial API access and a Jupyter environment.** The author said that without grounded data, models "still tend to hallucinate a lot when used to help with trading." — same search summary as above ([r/algotrading mirror](https://r.datuan.dev/r/algotrading/rising))
- **r/dataisbeautiful: GPT-4o picking small-cap stocks with $100.** The plan was a 6-month experiment. The portfolio was reported up about 25% after the first month. Short horizon, self-reported. — [Yahoo Finance coverage](https://www.yahoo.com/finance/news/someone-gave-chatgpt-100-let-130416462.html)
- **r/ChatGPT: $400 into Robinhood, ChatGPT picks options trades, also pitted against Grok.** Coverage notes "no tickers, no trade logs, no brokerage receipts", so the claims are unverified. — [Finance Magnates via TradingView](https://www.tradingview.com/news/financemagnates:e4103eb3e094b:0-redditor-claims-chatgpt-is-his-personal-trade-whisperer/)
- **NewsBTC test, $20K in stocks and crypto.** It reported +$1,359 on crypto and +$587 on stocks in one month. A media stunt, not a controlled study. — [AOL/GOBankingRates](https://www.aol.com/chatgpt-given-20k-invest-stocks-155928386.html)
- **Polymarket Claude bots.** Community claims put win rates at 56–72%. CryptoBriefing flagged a circulated PDF promoting a "68.4%" Claude bot that contained fabricated screenshots, so it is a documented example of fake performance marketing. — [letsdatascience summary](https://letsdatascience.com/news/claude-posts-684-success-rate-on-polymarket-b7bc0ad1)
- **Practitioner pattern: run a fixed mechanical rule "in shadow" next to the LLM.** One individual builder's paper-trading bot journals every order and runs a fixed rule in parallel as a baseline, to test whether the LLM adds value over indicators. — search summary of r/algotrading-adjacent results ([mirror](https://r.datuan.dev/r/algotrading/rising))
- **Rebuttal piece against viral "Claude made $10k overnight" claims.** — [Medium](https://medium.com/@info_38412/claude-didnt-earn-10k-overnight-and-that-isn-t-how-markets-work-b2bb2717aa76)

### Inferences
- The visible "LLM trader" content on Reddit and X skews toward viral wins posted early in an experiment (survivorship and selection bias). The honest posts are mostly about tooling problems such as missing data and hallucination, not about lasting profit.
- Running an LLM next to a mechanical "shadow baseline" is the community's de facto evaluation standard and worth copying.

### Gaps
- I could not open threads in r/CryptoCurrency, r/Daytrading, r/solana, r/ClaudeAI, r/LocalLLaMA, r/freqtrade or r/hummingbot directly because Reddit was blocked, so there are no thread-level quotes, upvote counts or comment consensus from those subreddits.
- I found no Reddit post-mortem of a Claude- or GPT-driven *crypto* bot that included verifiable trade logs.

## 2. Public LLM trading competitions: Alpha Arena (nof1.ai) and others

### Takeaway
Alpha Arena Season 1 (Oct 17/18 – Nov 3, 2025) gave six LLMs $10k each of real money to trade perpetuals on Hyperliquid. Qwen3 Max won with about +22% and DeepSeek V3.1 was the only other model in profit. GPT-5, Gemini 2.5 Pro, Grok 4 and Claude Sonnet 4.5 each lost roughly 30–63%, with exact figures differing by source. Season 1.5 (US equities, Nov–Dec 2025) saw most models lose money; the reported winner was a "mystery" Grok 4.20. Overtrading and poor discipline, not prediction quality, were the main loss drivers. As of an August 2026 check, no public Season 2 results existed.

### Cited Findings
- **Season 1 setup.** Six models with $10,000 each traded crypto perpetuals on Hyperliquid with no human intervention: Claude Sonnet 4.5, DeepSeek V3.1 Chat, Gemini 2.5 Pro, GPT-5, Grok 4 and Qwen3 Max. The season ended Nov 3, 2025 at 17:00 ET. — [cryptoast](https://cryptoast.fr/competition-trading-ia-hyperliquid-remporte-challenge/); [Odaily](https://www.odaily.news/en/newsflash/455170)
- **Qwen3 Max won** with an account value of about $12,231.82 (+22.3%), a 30.2% win rate and 43 trades in total. — [GNcrypto](https://www.gncrypto.news/news/qwen-wins-alpha-arena-season-1-with-22-percent-returns/); [RootData](https://www.rootdata.com/news/412456)
- **DeepSeek V3.1 came second** at about +4.89% and was the only other model in profit. — [iweaver results](https://www.iweaver.ai/blog/alpha-arena-ai-trading-season-1-results/) (search summary)
- **The losers' figures conflict between sources:**

  | Model | One tally | Another source |
  |---|---|---|
  | Claude Sonnet 4.5 | -42.01% ($5,799) | -30.8% |
  | Gemini 2.5 Pro | -45.55% ($5,445) | -56.7% |
  | Grok 4 | — | -45.3% |
  | GPT-5 | — | -62.7% (about $3,733) |

  RootData's headline is "all four major models incurred losses exceeding 30%". — [iweaver](https://www.iweaver.ai/blog/alpha-arena-ai-trading-season-1-results/); [RootData](https://www.rootdata.com/news/412456); [Benzinga: "ChatGPT lost 63%"](https://fr.benzinga.com/quote/cryptocurrency/25/11/48651974/chatgpt-lost-63-trying-to-trade-crypto-but-one-china-ai-made-a-healthy-profit)
  - A marketing page cites "Claude Sonnet 4.5 +13%, GPT-5 -74%". This contradicts every other source and should be treated as unreliable.
- **Mid-season swings were huge.** Qwen was reported at $17,496 at one point, and Western models were reported down "80% in one week". Leaderboard figures also left out unrealized P&L until positions closed, so interim standings were unreliable. — [Bitcoin Magazine](https://bitcoinmagazine.com/business/alpha-arena-reveals-ai-trading-flaws-western-models-lose-80-capital-in-one-week); [Phemex](https://phemex.com/news/article/alpha-arena-ai-trading-competition-to-conclude-on-november-4-30877)
- **Founder caveat.** Jay Azhang (founder of nof1) called it one small experiment with a constrained asset universe and a limited action space, and a stress test rather than a product. — search summaries of [iweaver](https://www.iweaver.ai/blog/alpha-arena-ai-trading-season-1-results/), [Medium](https://medium.com/@farhat.hanne/alpha-arena-when-ais-fight-who-will-survive-3b179c84f7fa)
- **Azhang on time series.** He is quoted as saying: "LLMs don't really handle numerical time series data very well, but that's all the context we gave them." He also noted that each model showed a consistent bias, an investing "personality". — secondary coverage via search ([Medium](https://medium.com/@farhat.hanne/alpha-arena-when-ais-fight-who-will-survive-3b179c84f7fa), [techntrek](https://techntrek.is-a.dev/posts/2025-10-llm-trading))
- **Season 1.5 (US tokenized and real equities, Nov 20 – Dec 3/4, 2025).** It reportedly ran four parallel competition modes, and an undisclosed "Grok 4.20" won. Chinese coverage says only 6 of 32 model×mode results were profitable and portfolios lost about a third overall. In one round Qwen placed 1,418 trades versus 158 for Grok 4.20, so overtrading was the main loss driver. Another report: "seven of eight models lost money." — [Forklog](https://forklog.com/en/ai-model-grok-4-2-triumphs-in-trading-tournament/); [Wallstreetcn](https://wallstreetcn.com/articles/3771681); [BigGo Finance](https://finance.biggo.com/news/5BSX_Z0BaoGGrU-ID27J); [Bitget](https://www.bitget.com/news/detail/12560605073584)
- **Season 2.** As of an August 6, 2026 check, nof1.ai's public site still showed Season 1.5 and had no Season 2 leaderboard. A CoinDesk report around May 2026 mentioned a "Season Two". Earlier statements said Season 2 would add human traders and nof1's own models. — search summary citing [traderank.ai](https://www.traderank.ai/blog/alpha-arena-alternatives-2026)
- **Other competition: LI.FI.** Five LLMs, including Claude Opus 4.6 and GPT-5.4, got $1,000 each in crypto. GPT behaved as a "cautious pragmatist" with 8 trade attempts in 7 days, 6 of which executed. — [LI.FI](https://li.fi/knowledge-hub/we-let-5-llms-trade-crypto-autonomously-and-the-result-shocked-us) (search summary; full results not retrieved)
- **Open-source clones of the Arena exist,** for example HammerGPT/Hyper-Alpha-Arena, an AI trading platform for Hyperliquid and Binance futures. — [gittrend](https://gittrend.io/repo/HammerGPT/Hyper-Alpha-Arena)
- **An independent builder's prompt-engineering write-up** inspired by the Arena. — [Medium @kojott](https://medium.com/@kojott/teaching-an-ai-to-trade-system-prompt-engineering-and-performance-monitoring-9d55258cca06)

### Inferences
- Across both public seasons, most frontier models lost money at the median. The winners were the ones that traded *less* (Qwen in Season 1 with 43 trades; Grok 4.20 in Season 1.5 with 158 trades versus 1,418). That points to trade frequency and discipline, not model intelligence, as the first thing to control.
- With n=1 per model and about two weeks per season, the rankings are statistically meaningless as evidence of model skill, as nof1 itself admits.

### Gaps
- I could not reach nof1.ai or alphaarena.ai directly, so there is no primary-source final leaderboard, no fee totals and no published per-model prompt or behavior analysis.
- No verified Season 2 results were found as of October 2026.

## 3. Open-source projects: activity, architecture and LLM use

### Takeaway
The mature, battle-tested execution engines (Freqtrade, Hummingbot) are rule- or ML-based. LLM support either sits on top as an agent harness (Hummingbot's Condor) or is absent from the core (Freqtrade). The very popular LLM projects (TradingAgents, ai-hedge-fund) are research or paper-trading frameworks that explicitly do not trade real money.

### Cited Findings
- **TradingAgents (TauricResearch):** about 111.2k stars, 21.4k forks, latest release v0.6.0 in October 2026.
  - Built on LangGraph, with a multi-agent pipeline: analysts (fundamentals, sentiment, news, technical) → bull/bear researcher debate → trader → risk team → portfolio manager → *simulated* exchange.
  - Supports OpenAI, Anthropic, Google, xAI, DeepSeek, Qwen, OpenRouter and Ollama/vLLM, among others. Described as "designed for research… not intended as financial… advice."
  - — [GitHub](https://github.com/TauricResearch/TradingAgents)
- **TradingAgents latency.** An academic survey found TradingAgents adds more than 4 minutes of total decision latency, which risks stale prices, late stop-losses and slippage. — [arXiv SoK](https://arxiv.org/pdf/2609.19705) (search summary)
- **ai-hedge-fund (virattt):** about 64.0k stars, 11.2k forks.
  - "Investor agents" run on one model API key. It offers paper trading with a hash-chained ledger and an approval step, plus backtesting.
  - "The system does not actually make any trades"; for education and research only.
  - — [GitHub](https://github.com/virattt/ai-hedge-fund)
- **Freqtrade:** about 55.4k stars, 11.5k forks, more than 33k commits.
  - Spot and futures, including Hyperliquid, Binance, Bybit, OKX, Kraken and others.
  - FreqAI provides "self-trains to the market via adaptive machine learning" and reinforcement-learning requirements.
  - The README makes no mention of LLM integration.
  - — [GitHub](https://github.com/freqtrade/freqtrade)
- **Hummingbot:** about 20.5k stars, 5.0k forks, tagged "market-making" and "ai-agents".
  - Market-making controllers include pmm_mister and simple_pmm, plus Avellaneda.
  - **Condor** is "the AI harness for building and running agentic strategies," connecting LLM decisions to execution through the Hummingbot API, controlled from Telegram or a web dashboard.
  - — [GitHub](https://github.com/hummingbot/hummingbot)
- **ElizaOS / ai16z ecosystem:**
  - The AI16Z token peaked around $2.47 (more than $2.6B market cap) on Jan 2, 2025.
  - It migrated 1:6 to ELIZAOS in November 2025, with supply rising from 6.6B to 11B.
  - By August 2026 founder Shaw Walters called the token "dead": price about $0.00031, market cap about $2.3M, down 97%. The foundation is closing while the software continues without a token.
  - — [CoinDesk, Aug 5, 2026](https://www.coindesk.com/markets/2026/08/05/ai-agent-token-once-worth-usd2-4-billion-ends-with-founder-calling-it-dead)
- **ai16z class action.** A proposed class action alleges the founders faked the AI agent and misled investors. These are allegations, not findings. — [ClaimDepot](https://www.claimdepot.com/cases/ai16z-class-action-alleges-founders-faked-ai-agent-misled-investors-in-26b-crypto-scheme)
- **AI agent tokens such as AIXBT** suffered repeated sector drawdowns; AIXBT fell 21–25% in single sell-offs during 2025. — [crypto.news](https://crypto.news/ai-agents-notch-16-dip-biggest-drawdown-amid-market-correction/); [InsideBitcoins](https://insidebitcoins.com/news/ai-agent-tokens-plummet-9-as-virtual-zerebro-ai16z-aixbt-all-plunge)

### Inferences
- The "AI agent" crypto narrative of 2024–25 (ai16z, AIXBT, Virtuals) was mostly token speculation rather than proven trading performance. Agent tokens collapsing is not evidence about the quality of agent-based trading, but it shows that "AI agent trading" branding was a marketing vector.
- For a real short-term bot, the practical stack the community converges on is Freqtrade or Hummingbot (or a custom ccxt engine) for execution and risk, with any LLM layered on top.

### Gaps
- I did not check star counts or activity for Jesse, OctoBot or Hyper-Alpha-Arena because GitHub API access was denied and those pages were not fetched.
- I found no community data on how many Freqtrade users run LLM-augmented strategies, or with what results.

## 4. pump.fun / Solana sniper and copy-trading bots: experiences and scams

### Takeaway
Malicious "pump.fun / Solana trading bot" GitHub repos and npm packages that steal private keys are a documented and recurring threat in 2025. Successful sniping is largely an insider game, where deployer-funded sniper wallets buy in the same block as launch. On-chain data shows about half of pump.fun wallets lose money.

### Cited Findings
- **solana-pumpfun-bot (July 2025, GitHub account "zldp2002").** SlowMist found a fake copy of a real open-source tool:
  - Popularity was inflated with multiple GitHub accounts, and commits were concentrated in a short window.
  - It pulled in a dependency, `crypto-layout-utils`, which had been removed from npm and was re-hosted on a GitHub release to avoid review. A second package, `bs58-encrypt-utils`, was also involved.
  - The de-obfuscated payload scanned local files for wallet data and private keys and uploaded them to a remote server.
  - — [Cointelegraph](https://cointelegraph.com/news/solana-trading-bot-github-malware-scam); [MEXC/SlowMist](https://www.mexc.com/news/malicious-npm-package-steals-private-keys-solana-user-assets-are-stolen/33630); [TechFlow](https://www.techflowpost.com/en-US/newsletter/90374)
- **`@wagni_bot/pumpfun-sdk` v1.2.0** was flagged as malicious. Its postinstall script walked the home directory harvesting wallet files and developer credentials, and its name typosquatted the legitimate pump.fun SDK. — [Hacktron/osv](https://www.hacktron.ai/package/npm/%40wagni_bot%2Fpumpfun-sdk/1.2.0)
- **SlowMist advice:** be highly vigilant about GitHub projects of unknown origin that handle wallets, and test in isolated environments that hold no sensitive data. — [Cointelegraph](https://cointelegraph.com/news/solana-trading-bot-github-malware-scam)
- **About 49–50.6% of wallets lost money** trading pump.fun tokens in March 2026, per a viral Dune dashboard. This is a single analyst's dashboard, not audited research. — search summary citing [MEXC news](https://www.mexc.com/news/992439)
- **"Exit Liquidity Machines" (Pine Analytics):** token deployers fund sniper wallets that buy in the launch block, and 87% of such snipes were profitable. In other words, retail sniper bots compete against insiders who have an information edge. — [Pine Analytics Substack](https://pineanalytics.substack.com/p/exit-liquidity-machines)
- **Commercial sniper bots** (Gumroad pages, "MEV front-run" GitHub repos) make unverified marketing claims such as "real-time token sniping, anti-MEV". — [Gumroad](https://pumpfun.gumroad.com/l/trading-bot-v1); [GitHub Frontrunx](https://github.com/Frontrunx/solana-pumpfun-sniper-bot)

### Inferences
- Any project should treat third-party pump.fun or Solana bot code as hostile by default. Pin and audit dependencies, run in a sandbox, use a dedicated hot wallet holding minimal funds, and never paste a seed phrase or private key into an unaudited bot.

### Gaps
- I found no first-hand Reddit or X P&L reports from pump.fun sniper or copy-trade bot users (Reddit was blocked), and no independent performance data for copy-trading bots.

## 5. Common failure modes reported

### Takeaway
The recurring failure modes are:
- overtrading and fees;
- hallucination or missing grounded data;
- LLM latency, which rules out high-frequency or short-term execution by the LLM;
- training-data leakage that inflates backtests;
- overconfidence in sizing;
- malicious code and key theft.

### Cited Findings
- **Overtrading drove losses in Alpha Arena 1.5** (1,418 trades versus 158 for the winner); the winners were the low-frequency models. — [Wallstreetcn](https://wallstreetcn.com/articles/3771681); [BigGo](https://finance.biggo.com/news/5BSX_Z0BaoGGrU-ID27J)
- **Hallucination.** On FinanceBench, 8.3% (Claude 3 Opus) to 22.7% (Llama 3 70B) of incorrect answers contained a fabricated number. A Reddit Claude 3.7 experiment reported heavy hallucination without grounded data. — search summary of [arXiv 2607.15414](https://arxiv.org/pdf/2607.15414) and related; [r/algotrading mirror](https://r.datuan.dev/r/algotrading/rising)
- **Latency.** TradingAgents takes more than 4 minutes per decision, with risks of stale prices, late stops and slippage. HFT "still best handled by non-LLM frameworks". — [arXiv SoK](https://arxiv.org/pdf/2609.19705); [FlowHunt](https://www.flowhunt.io/blog/llm-trading-bots-comparison/)
- **Backtest contamination.** The LLM has already seen the historical period, and naive LLM buy/sell strategies underperform simple momentum or mean-reversion baselines (vendor blog, not peer-reviewed). TradingAgents v0.5.2 added "backtests limited to data published by each analysis date" to address this leakage. — [Gaper.io](https://gaper.io/can-llms-crack-algorithmic-trading-code); [TradingAgents](https://github.com/TauricResearch/TradingAgents)
- **Overconfidence.** LLMs produce high-confidence probabilities under genuine uncertainty, which is risky for position sizing. — [arXiv 2604.03888 (PolySwarm)](https://arxiv.org/html/2604.03888v1) (search summary)
- **Pipeline safety.** None of the 15 academic LLM trading agents surveyed had fast-path interrupts or safe-mode pipelines. An external risk layer clips many unsupported LLM intents. — [arXiv SoK](https://arxiv.org/pdf/2609.19705); [arXiv 2605.28850](https://arxiv.org/pdf/2605.28850)
- **Key theft through malicious bot repos** (see section 4). — [Cointelegraph](https://cointelegraph.com/news/solana-trading-bot-github-malware-scam)

### Inferences
- Fees and funding: Alpha Arena's high trade counts on perpetuals with leverage imply that fees and funding consumed a meaningful share of P&L, but I found no published fee breakdown.

### Gaps
- I found no sourced practitioner reports specifically about exchange account bans or API-key leaks from LLM bots, beyond the malware cases.
- No quantified fee drag figures from Alpha Arena were found.

## 6. Consensus on the best role for an LLM

### Takeaway
The weight of evidence points to the LLM as a slow-loop supervisor rather than the trigger-puller. That means a regime, sentiment or news filter, a strategy selector or parameter advisor, or a journaling and analysis layer, sitting over a deterministic, rule-based execution and risk engine with hard limits. The evidence for this is Alpha Arena's median losses, latency figures, hallucination rates, Azhang's admission about time series, and practitioner designs that use shadow baselines and approval steps.

### Cited Findings
- Azhang: LLMs "don't really handle numerical time series data very well." — secondary via search ([Medium](https://medium.com/@farhat.hanne/alpha-arena-when-ais-fight-who-will-survive-3b179c84f7fa))
- An Alpha Arena lessons summary credits Qwen's win to avoiding overtrading: "discipline beats prediction." — search summary ([buildix](https://www.buildix.trade/blog/nof1-alpha-arena-lessons-ai-trading-byok-strategy-advisor-2026))
  - Buildix's own framing is "LLM as strategy advisor (BYOK)", which also matches its product pitch, so treat it as biased.
- Architecture signals from the major frameworks:
  - Hummingbot puts LLMs in Condor, an agent harness *above* deterministic controllers. — [Hummingbot](https://github.com/hummingbot/hummingbot)
  - TradingAgents and ai-hedge-fund route LLM output through risk-manager or portfolio-manager agents and approval steps, and only into simulated execution. — [TradingAgents](https://github.com/TauricResearch/TradingAgents); [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund)
- An external risk layer filtering LLM intents is the recommended safety pattern in the academic audit. — [arXiv 2605.28850](https://arxiv.org/pdf/2605.28850)
- Practitioners run mechanical shadow baselines to test whether the LLM adds value. — [r/algotrading mirror](https://r.datuan.dev/r/algotrading/rising)

### Inferences
- For an autonomous *short-term* crypto bot, multi-second LLM latency, more than 4 minutes for multi-agent frameworks, makes direct per-trade LLM decisions unsuitable. LLM calls should run on a slower cadence (hourly or on events) to set regime, bias or allowed strategies and limits. A rule-based engine (for example Freqtrade or Hummingbot controllers) handles entries, exits and risk, with hard max-trade-frequency and max-drawdown caps.

### Gaps
- I found no controlled public study directly comparing "LLM as regime filter over rules" with "LLM direct decisions" on live crypto. The consensus above is inferred from the indirect evidence listed.
