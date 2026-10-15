Read-only review completed; no algorithms or tests run, no files written. **The main blockers are free-tier export and unenforced exposure limits.**

1. **Free-tier export fails — Momentum L81; MeanRev L98.**  
   `object_store.save(key, text)` is valid API, but Free organizations cannot write Object Store data. Both algorithms therefore lose their intended CSV output. Replace this export with downloadable result charts for equity/exposure. Free charts allow 4,000 points per series: split the roughly 7,200 sessions across dated series, preserving one continuous backtest. Logging the CSV exceeds the 10 KB/backtest quota. [Object Store](https://www.quantconnect.com/docs/v2/cloud-platform/object-store), [chart quotas](https://www.quantconnect.com/docs/v2/writing-algorithms/charting).

2. **No-leverage rule is unenforced — both L27–28; Momentum L65–78; MeanRev L86–90.**  
   IB margin permits borrowing. Sizing almost 100% from D’s close can exceed equity after opening gaps, commissions and slippage. MeanRev can also exceed 100% because surviving positions drift above their original 10% weights.  
   **Fix:** after base initialization, call `security.set_leverage(1)`; set `self.universe_settings.leverage = 1` before adding the universe. Cap new purchases against available unborrowed cash after existing holdings, pending orders and costs. Sorting sales first does **not** guarantee their fills precede purchases. A buffer reduces gap risk; exact 5%/10% sizing at an unknown opening price is impossible with fixed-share MOO orders—document that approximation.

3. **Momentum skips 21 sessions, not 22 — [L61](../qc/R6Momentum/main.py#L61).**  
   With the final observation representing D, `iloc[-22]` represents D−21. For the card’s “22 days earlier,” use:
   ```python
   score = (close.iloc[-(SKIP + 1)] / close.iloc[0] - 1)
   ```
   Before indexing, require at least `LOOKBACK` rows and nonempty eligible columns. Keep the existing 253-observation eligibility rule.

4. **Pending orders can break MeanRev’s 10-position limit — [L67–77](../qc/R6MeanRev/main.py#L67).**  
   Any open order is classified as an exit, including a partially filled entry. Unfilled entries in other symbols consume no slots. Failed exits nevertheless release slots.  
   **Fix:** retain tickets and distinguish entry orders from full-position exits. Count pending entries as occupied slots; release occupied slots only under an explicit replacement policy, and reconcile rejected/canceled exits before admitting additional positions. Add pending-order reconciliation to Momentum L64–78 too, particularly before a later rebalance.

5. **Holding age tracks submission, not execution — MeanRev L73, L91, L93–95.**  
   This miscounts delayed fills. The ordinary next-session fill is **not inherently an off-by-one error**: the present arithmetic counts ten completed holding sessions.  
   **Fix:** record the first positive fill’s trading session in `on_order_event`; count held sessions inclusively from that session. Clear entry state on failed/canceled unfilled entries.

6. **MeanRev exits can use stale signals — [L70–74](../qc/R6MeanRev/main.py#L70).**  
   `security.price` may be cached when the stock has no current bar; `is_ready` does not establish indicator freshness.  
   **Fix:** evaluate the SMA5 price exit only with a current, non-fill-forward bar whose session matches SPY’s, using `data.bars[s].close`. Keep the time-based exit separate. Apply equivalent freshness checks before Momentum buys. This is a **stale-signal/sizing risk**, not evidence that MOO fills use yesterday’s close.

7. **Indicator cleanup can miss formerly held removals — MeanRev L50–54, L93–95.**  
   A removed stock retained because it is invested has no explicit cleanup after liquidation; it may retain indicators/consolidators until another removal notification.  
   **Fix:** sweep `self.ind` after fills or daily: deregister and delete symbols outside `self.members` that have neither holdings nor open orders. Retain indicators for removed stocks while held, so their prescribed exits still work.

8. **Free-tier runtime risk — MeanRev L41–48; Momentum L56.**  
   MeanRev initially makes approximately **1,500 indicator warm-up requests**, plus security seeding. Batch history for added symbols once and update all three indicators from that stream. Momentum repeatedly retrieves up to **126,500 bars per monthly rebalance**; bounded windows plus batch initialization of newcomers would reduce repeated work. Preserve daily universe selection to remain faithful to the card. QC estimates roughly **2.5 GB for 500 subscriptions**, before engine/history overhead; the current free backtest node has **8 GB**, so this is a performance risk, not a demonstrated memory failure. [Universe memory guidance](https://www.quantconnect.com/docs/v2/writing-algorithms/universes/equity/fundamental-universes), [node specifications](https://www.quantconnect.com/docs/v2/cloud-platform/organizations/resources).

The requested API checks that **do not need correction**:

- Both `SlipInit` classes correctly call the brokerage initializer before overriding slippage. [Official pattern](https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/settlement/key-concepts).
- `has_fundamental_data`, `price`, `dollar_volume`, `symbol in data.bars`, MeanRev’s RSI argument order, `warm_up_indicator`, and `deregister_indicator` are valid. `hist["close"].unstack(0)` correctly produces time rows and symbol columns. [Fundamentals](https://www.quantconnect.com/docs/v2/writing-algorithms/universes/equity/fundamental-universes), [indicators](https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/automatic-indicators), [history shape](https://www.quantconnect.com/docs/v2/writing-algorithms/historical-data/history-responses).
- **No confirmed signal look-ahead:** MOO submitted after D’s daily bar uses a subsequent bar’s open. Current LEAN also bases constant MOO slippage on that open. [Fill source](https://github.com/QuantConnect/Lean/blob/master/Common/Orders/Fills/EquityFillModel.cs), [slippage source](https://github.com/QuantConnect/Lean/blob/master/Common/Orders/Slippage/ConstantSlippageModel.cs).
- `bar.time.date()` correctly labels the session under both daily-bar conventions. Explicitly set `self.settings.daily_precise_end_time = True` for reproducible timing; blindly replacing it with `end_time.date()` shifts legacy midnight bars to the following date. [Daily-bar timing](https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/time-modeling/periods).