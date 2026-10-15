# H013 kısa vadeli ortalamaya dönüş, RSI(2) (research/cards/R6.md). QuantConnect bulutunda çalışır; kurallar donuk.
# Parametreler: start_year / end_year (parça), slip_bps = 5. Stres (15 bp) çevrimdışı: traded x 10 bp.
# Çıktı: "Export" grafiği (ücretsiz planda Object Store yazılamıyor).
# region imports
from AlgorithmImports import *
# endregion

TOP_N, MAX_POS, SIZE, RSI_IN, MAX_DAYS, BUFFER = 100, 10, 0.10, 10, 10, 0.98


class SlipInit(BrokerageModelSecurityInitializer):
    def __init__(self, brokerage_model, seeder, slip):
        super().__init__(brokerage_model, seeder)
        self.slip = slip

    def initialize(self, security):
        super().initialize(security)
        security.set_slippage_model(ConstantSlippageModel(self.slip))
        security.set_leverage(1)
        # MOO alımları gönderimde kontrol ediliyor, aynı açılıştaki satışlar henüz dolmamış -> red; brüt ≤ 0,98 kuralla korunur
        security.set_buying_power_model(NullBuyingPowerModel())


def export(algo):
    """Özsermaye, yatırım oranı, KÜMÜLATİF işlem hacmi (QC grafiği ~6 günde bir örnekliyor; fark = aralıktaki hacim)."""
    p = algo.portfolio
    algo.plot("Export", "equity", p.total_portfolio_value)
    algo.plot("Export", "invested", p.total_holdings_value / p.total_portfolio_value)
    algo.plot("Export", "traded", algo.traded)


def period(algo):
    """Parça: start_year 1 Ocak → end_year 1 Ocak (2026 ise 15 Ekim). Ücretsiz düğüm 28 yılı tek seferde kaldırmıyor."""
    y0, y1 = int(algo.get_parameter("start_year", "1998")), int(algo.get_parameter("end_year", "2026"))
    algo.set_start_date(y0, 1, 2)
    algo.set_end_date(*((2026, 10, 15) if y1 == 2026 else (y1, 1, 1)))
    algo.traded = 0.0

class R6MeanRev(QCAlgorithm):
    def initialize(self):
        period(self)
        self.set_cash(100_000)
        self.settings.daily_precise_end_time = True
        slip = float(self.get_parameter("slip_bps", "5")) / 1e4
        self.set_brokerage_model(BrokerageName.INTERACTIVE_BROKERS_BROKERAGE, AccountType.MARGIN)
        self.set_security_initializer(SlipInit(self.brokerage_model, FuncSecuritySeeder(self.get_last_known_prices), slip))
        self.spy = self.add_equity("SPY", Resolution.DAILY).symbol
        self.set_benchmark(self.spy)
        self.universe_settings.resolution = Resolution.DAILY
        self.universe_settings.leverage = 1
        self.sel_month = -1
        self.add_universe(self.select)
        self.ind, self.members, self.entry_day, self.n_days = {}, set(), {}, 0

    def select(self, fundamental):
        if self.time.month == self.sel_month:  # aylık seçim: ücretsiz düğümde günlük tarama bellek taşırıyor
            return Universe.UNCHANGED
        self.sel_month = self.time.month
        f = [x for x in fundamental if x.has_fundamental_data and x.price > 5 and x.dollar_volume > 0]
        self.members = {x.symbol for x in sorted(f, key=lambda x: x.dollar_volume, reverse=True)[:TOP_N]}
        return list(self.members)

    def on_securities_changed(self, changes):
        for sec in changes.added_securities:
            s = sec.symbol
            if s == self.spy or s in self.ind:
                continue
            ind = (self.rsi(s, 2, MovingAverageType.WILDERS, Resolution.DAILY),
                   self.sma(s, 200, Resolution.DAILY), self.sma(s, 5, Resolution.DAILY))
            for i in ind:
                self.warm_up_indicator(s, i, Resolution.DAILY)
            self.ind[s] = ind

    def on_data(self, data):
        if self.spy not in data.bars:
            return
        bar = data.bars[self.spy]
        self.n_days += 1
        export(self)
        busy = {o.symbol for o in self.transactions.get_open_orders()}
        held = [s for s, h in self.portfolio.items() if h.invested]
        # çıkışlar: kapanış > SMA5 (yalnızca bugünkü barla) veya 10 işlem günü
        exits, proceeds = set(), 0.0
        for s in held:
            if s in busy:
                continue
            ind = self.ind.get(s)
            above = s in data.bars and ind is not None and ind[2].is_ready and data.bars[s].close > ind[2].current.value
            if above or self.n_days - self.entry_day.get(s, self.n_days) >= MAX_DAYS:
                self.market_on_open_order(s, -self.portfolio[s].quantity)
                exits.add(s)
                proceeds += self.portfolio[s].holdings_value
        # bekleyen girişler slot tüketir; bekleyen çıkışlar slotu ancak dolunca boşaltır
        pending_buys = {s for s in busy if not self.portfolio[s].invested}
        slots = MAX_POS - (len(held) - len(exits)) - len(pending_buys)
        self.cleanup(busy)
        if slots <= 0:
            return
        cands = []
        for s, (rsi, sma200, _) in self.ind.items():
            if s not in self.members or s in busy or self.portfolio[s].invested or s not in data.bars:
                continue
            if rsi.is_ready and sma200.is_ready and data.bars[s].close > sma200.current.value and rsi.current.value < RSI_IN:
                cands.append((rsi.current.value, s))
        tpv = self.portfolio.total_portfolio_value
        budget = (self.portfolio.cash + proceeds) * BUFFER  # kaldıraç yok: nakit + bugünkü satışlar
        for _, s in sorted(cands)[:slots]:
            q = int(min(SIZE * tpv * BUFFER, budget) / data.bars[s].close)
            if q > 0:
                self.market_on_open_order(s, q)
                budget -= q * data.bars[s].close

    def cleanup(self, busy):
        for s in [s for s in self.ind if s not in self.members and s not in busy and not self.portfolio[s].invested]:
            for i in self.ind.pop(s):
                self.deregister_indicator(i)

    def on_order_event(self, e):
        if e.status != OrderStatus.FILLED:
            return
        self.traded += abs(e.fill_quantity * e.fill_price)
        if self.portfolio[e.symbol].invested and e.fill_quantity > 0:
            self.entry_day[e.symbol] = self.n_days  # dolum günü (sinyal günü sayacı; çıkış 10 seans sonra)
        elif not self.portfolio[e.symbol].invested:
            self.entry_day.pop(e.symbol, None)
