# H012 kesitsel momentum (research/cards/R6.md). QuantConnect bulutunda çalışır; kurallar donuk.
# Parametreler: start_year / end_year (parça), slip_bps = 5. Stres (15 bp) çevrimdışı: traded x 10 bp.
# Çıktı: "Export" grafiği (ücretsiz planda Object Store yazılamıyor).
# region imports
from AlgorithmImports import *
# endregion

TOP_N, HOLD_N, LOOKBACK, SKIP, GROSS = 100, 20, 253, 22, 0.98


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

class R6Momentum(QCAlgorithm):
    def initialize(self):
        period(self)
        self.set_cash(100_000)
        self.settings.daily_precise_end_time = True
        slip = float(self.get_parameter("slip_bps", "5")) / 1e4
        self.set_brokerage_model(BrokerageName.INTERACTIVE_BROKERS_BROKERAGE, AccountType.MARGIN)
        self.set_security_initializer(SlipInit(self.brokerage_model, FuncSecuritySeeder(self.get_last_known_prices), slip))
        self.spy = self.add_equity("SPY", Resolution.DAILY).symbol
        self.spy_sma = self.sma(self.spy, 200, Resolution.DAILY)
        self.set_benchmark(self.spy)
        self.universe_settings.resolution = Resolution.DAILY
        self.universe_settings.leverage = 1
        self.sel_month = -1
        self.add_universe(self.select)
        self.set_warm_up(210, Resolution.DAILY)
        self.members, self.month = [], -1

    def select(self, fundamental):
        if self.time.month == self.sel_month:  # aylık seçim: ücretsiz düğümde günlük tarama bellek taşırıyor
            return Universe.UNCHANGED
        self.sel_month = self.time.month
        f = [x for x in fundamental if x.has_fundamental_data and x.price > 5 and x.dollar_volume > 0]
        self.members = [x.symbol for x in sorted(f, key=lambda x: x.dollar_volume, reverse=True)[:TOP_N]]
        return self.members

    def on_data(self, data):
        if self.spy not in data.bars:
            return
        bar = data.bars[self.spy]
        day = bar.time.date()  # işlem günü
        export(self)
        if self.is_warming_up or day.month == self.month:
            return
        self.month = day.month  # ayın ilk işlem günü kapanışı
        if not self.spy_sma.is_ready or bar.close < self.spy_sma.current.value:
            self.rebalance({}, data)
            return
        cands = [s for s in self.members if s != self.spy]
        hist = self.history(cands, LOOKBACK, Resolution.DAILY)
        if hist.empty:
            return
        close = hist["close"].unstack(0)
        if len(close) < LOOKBACK:
            return
        close = close.loc[:, close.notna().sum() >= LOOKBACK]
        if close.empty:
            return
        # son satır D; iloc[-(SKIP+1)] = D'den 22 işlem günü önce
        score = (close.iloc[-(SKIP + 1)] / close.iloc[0] - 1).dropna().sort_values(ascending=False)
        top = [s for s in score.index if s in data.bars][:HOLD_N]  # yalnızca bugün barı olanlar (bayat fiyat yok)
        self.rebalance({s: GROSS / HOLD_N for s in top}, data)

    def rebalance(self, target, data):
        self.transactions.cancel_open_orders()
        tpv = self.portfolio.total_portfolio_value
        orders = []
        for s, h in self.portfolio.items():
            if h.invested and s not in target:
                orders.append((s, -h.quantity))
        for s, w in target.items():
            q = int(w * tpv / data.bars[s].close) - int(self.portfolio[s].quantity)
            if q:
                orders.append((s, q))
        for s, q in sorted(orders, key=lambda o: o[1]):  # önce satışlar; %2 nakit tamponu açılış boşluğu için
            self.market_on_open_order(s, q)

    def on_order_event(self, e):
        if e.status == OrderStatus.FILLED:
            self.traded += abs(e.fill_quantity * e.fill_price)
