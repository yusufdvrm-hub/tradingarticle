**H008–H010: the Sharpe kills stand on the inspected code. H011: possibly wrongly killed; its overlay needs correction.** This was a static, read-only review; I did not rerun the reported results.

| Hypothesis | Verdict | Reason |
|---|---|---|
| H008 | **Bug-free kill on inspected path** | No material timing, financing or buffer defect found. L1’s 0.88 misses the registered 1.01 hurdle. L2/L3 are explicitly report-only. |
| H009 | **Bug-free kill on inspected path** | Monthly targets, drift and cash handling are consistent. No identified bug explains the 0.56 Sharpe. |
| H010 | **Bug-free Sharpe kill** | Signal signs and sizing match registration. Correlation gate has a bug, but −0.05 independently fails Sharpe ≥0.4. |
| H011 | **Possibly wrongly killed** | Execution lag differs from registration; financing and turnover depend on an unresolved implementation model. No evidence yet that fixing these bridges 0.59→1.11. |

**Findings and concrete fixes**

- **Base timing and monthly buffers are correct.** `macro.py:37–51` maps signal D to D+1-close holdings and D+2-labelled returns. `_fill`, `portfolio.py:146–153`, returns the **drifted** weights on all-NaN rows; `macro.py:50` carries that drift forward. H009 therefore holds shares between monthly decisions. The buffer suppresses a trade only when **both** thresholds hold; this matches the registered implementation.

- **Small rate-timing error, either direction:** `macro.py:45` uses D’s rate for the D+1→D+2 holding interval. Use the rate known at the interval’s starting close, consistently indexed. This is unlikely to rescue any result. The cash/borrowing signs themselves are correct (`45–48`).

- **H010 sizing is correct; financing is optimistic.** `macro.py:93–99` correctly averages three signs, divides by volatility and √N, then caps gross at three. No extra sign reversal or normalization is needed. Crediting short proceeds at full RF while omitting borrow fees (`45–46`; acknowledged in R5:36) can **inflate** performance. Specify collateral rebates and borrow charges for an executable version.

- **H010 correlation gate uses the wrong period:** `macro.py:176,184` calculates full-sample monthly correlation, although R5:27–30 specifies OOS gates. Calculate both monthly series from aligned OOS daily returns. This could wrongly pass or fail correlation, but cannot overturn the current Sharpe kill.

- **H011 trades one close too early:** `macro.py:109,112` uses `.shift(1)` on close-labelled realized returns. A decision using return D then earns D→D+1, whereas D+1-close execution should first earn D+1→D+2. Use two-row lags on this grid or explicit decision/fill timestamps. Direction of the performance effect is unknown.

- **H011 financing can overcharge a consolidated account:** `macro.py:116` correctly implements `rf + scale × (mix − rf)` for funded sleeves, but adds borrowing spread on `scale−1` while sleeve returns already include their own financing. Example: sleeve mix net exposure 0.4, scale 2 ⇒ aggregate exposure 0.8; a consolidated account needs no borrowing, yet the overlay charges 1% annually. **Fix:** aggregate scaled ETF positions and finance their aggregate net exposure once. Alternatively, explicitly register separately funded sleeves and their financing arrangement.

- **H011 turnover is not actual traded turnover:** `macro.py:109–115` keeps monthly allocation weights constant daily, implicitly rebalancing sleeve drift, but `expo.diff()` charges only changes in target exposures. It omits drift turnover and initial entry, and assumes sleeve gross≈1 despite H010 gross≤3. Missing costs inflate; failure to net opposing sleeve trades can depress results. **Fix:** calculate costs from aggregate ETF trades against drifted holdings.

**Statistics and gate fairness**

- **Excess-return Sharpe is correct** (`macro.py:121–125`). Do not switch to raw-return Sharpe to rescue candidates.
- **“Alpha DSR” is an information-ratio test against ex-post volatility-matched SPY**, not regression alpha (`135–141`). Its mean is proportional to the strategy–SPY Sharpe difference; near-zero DSR does not independently establish that a diversifier is useless. The pooled eight-variant variance and global trial count (`178–180`) also require reconciliation: the extra `+12` is not explicit in R5:33, and correlated variants are not independent trials. Freeze a documented trial universe and calibrate significance with dependence-aware resampling. **DSR is correctly separate from the economic pass/fail gates.**
- SPY+0.2/+0.3 are legitimate frozen deployment hurdles, but stringent preferences—not universal evidence of “no edge.” Add QQQ comparisons for H008 and common-date benchmarks for H011’s shorter development history. H010’s absolute-Sharpe/diversification gates are more appropriate than requiring SPY-relative alpha.
- `tests/test_macro.py:8–28` checks flat-price financing and target causality only. It does **not** establish overlay correctness, monthly drift accounting or OOS gate slicing. Those are the focused checks needed before accepting a corrected H011 verdict.