# opusjev-trade

Otonom, kısa vadeli, düşük riskli kripto işlem sistemi. **Şu an yalnızca paper (sahte bakiye) modunda.**
Tasarım: [`reports/Otonom kısa vadeli kripto botu.md`](reports/Otonom%20kısa%20vadeli%20kripto%20botu.md).

> **Sonuç (Ekim 2026):** Altı turda yüzden fazla strateji varyantı test edildi; hiçbiri önceden kayda
> geçirilmiş başarı kriterlerini geçmedi. Bulgular "Yüzden fazla deneme, sıfır avantaj" yazısında.
> Hipotez kartları `research/cards/`, deneme kaydı `research/ledger.jsonl`, karşıt incelemeler
> `research/reviews/` ve `reviews/` altında. Ham veri (Binance, Yahoo, QuantConnect) lisans nedeniyle repoda
> yok; `research/` betikleri onu yeniden indirir. Gerçek para hiçbir aşamada kullanılmadı; yatırım tavsiyesi değildir.

## Nasıl çalışır

```
Binance USDⓈ-M canlı kline (anahtarsız)
   → özellikler (yalnızca kapanmış 15dk barlar)
   → deterministik aday (rejim filtreli: yatayda ortalamaya dönüş, trendde Donchian kırılımı; stop 1.2×ATR, TP 2R)
   → ücretsiz risk ön kontrolü (reddedilecekse jev çağrılmaz)
   → jev (TypeSafe System One, Choice: take/skip; p_take < 0.6 → skip; hata/zaman aşımı/bütçe → skip)
   → veto yetkili risk yöneticisi (R1–R14: %0.5 risk/işlem, günlük -%2, haftalık -%5, zirveden -%10 tam durma,
     4 ardışık kayıpta 60 dk soğuma + yarım boyut, en fazla 3 pozisyon, ≤2x kaldıraç, günde ≤12 giriş, funding penceresi…)
   → paper broker (kötümser dolum: sonraki bar açılışı + kayma + taker; stop önce; TP aşılınca dolar; zaman stopu)
```

Aynı barları jev'siz bir **gölge motor** da işler; jev'in gerçekten değer katıp katmadığı (ablasyon) böyle ölçülür.
Her aday, jev cevabı, risk kararı ve işlem `runs/<run>/journal_*.jsonl` dosyasına yazılır.

| Modül | Görev |
|---|---|
| `opusjev/config.py` | Sabit risk/maliyet/strateji parametreleri (jev değiştiremez) |
| `opusjev/data.py` | Binance kline istemcisi + test için sentetik veri |
| `opusjev/features.py`, `signals.py` | İndikatörler ve aday üretici |
| `opusjev/decision.py` | `JevProvider`, `BaselineProvider`, günlük çağrı/harcama tavanı |
| `opusjev/risk.py` | R1–R14 risk yöneticisi |
| `opusjev/broker.py` | Kötümser paper broker |
| `opusjev/engine.py` | Backtest ve canlı için ortak motor |
| `opusjev/live.py` | 7/24 paper döngüsü, diske durum kaydı, kaldığı yerden devam |
| `opusjev/metrics.py` | Metrikler ve canlıya geçiş kapısı |

## Kurulum (lokal)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env   # TYPESAFE_API_KEY'i doldurun
set -a; source .env; set +a
pytest -q              # 58 test
```

## Kullanım

```bash
# 1) Tesisat testi (ağ gerekmez; sonuçları strateji hakkında bilgi VERMEZ)
opusjev backtest --source synthetic

# 2) Gerçek geçmiş veriyle deterministik geri test (jev'siz, ücretsiz)
opusjev backtest --source binance --days 180

# 3) jev bağlantı testi (1 çağrı, ~0.00005$)
opusjev jev-ping

# 4) ASIL TEST: canlı veri + sahte bakiye (10.000 USDT), jev + jev'siz gölge
opusjev paper --provider jev --run-dir runs/paper
# başka bir terminalde istediğiniz zaman:
opusjev report --run-dir runs/paper
```

Paper döngüsü her 15 dakikalık bar kapanışından ~3 sn sonra çalışır. `Ctrl+C` ile durdurup aynı komutla
devam ettirebilirsiniz (durum `runs/paper/state.pkl`). Bilgisayar kapalıyken çalışması için bir VPS'te:

```bash
docker build -t opusjev . && docker run -d --restart unless-stopped --env-file .env -v $PWD/runs:/app/runs --name opusjev opusjev
docker logs -f opusjev
```

## jev maliyeti

TypeSafe'in yayınladığı fiyat 1M girdi tokeni başına ~0.042$ (çıktı ücretsiz). Bir karar ~1–2k token, yani
çağrı başına ~0.00005–0.0001$. Kod günde en fazla 60 çağrı ve 0.50$ harcama tavanı uygular
(`JevConfig`). 5$ bakiye paper aşaması için fazlasıyla yeter. Fiyatı TypeSafe panelinden doğrulayın.

## Gerçek paraya geçiş

`report.md` içindeki **canlıya geçiş kapısı** (≥200 işlem, ≥4 hafta, PF ≥1.3, beklenti %95 alt sınır >0,
maks. düşüş ≤%10, Sharpe ≥1, jev > gölge) geçilmeden canlı mod yazılmayacak. Canlı moda geçiş, platform
seçimi (Binance TR spot vs. küresel vadeli; SPK/7518 riski) ve sermaye kararı **insan onayı** gerektirir.
Canlı emir modülü (borsada reduce-only stop, mutabakat) bir sonraki fazdır.

## Bilinen sınırlamalar (Faz 1)

- Funding ödemeleri paper PnL'e henüz eklenmiyor (pozisyonlar ≤4 saat tutulduğu için etkisi küçük; R11 funding saatlerinde giriş açmaz).
- Lot/tick adımlarına yuvarlama yok (6 anlamlı basamak); canlı modda `exchangeInfo` ile yapılacak.
- Claude orkestratörü (rejim incelemesi, günlük rapor) henüz bağlı değil; şimdilik `opusjev report` çıktısını Claude'a verip yorumlatabilirsiniz.
- Sentetik backtest sonuçları anlamsızdır; strateji kenarı yalnızca gerçek veride ölçülür.

## Lisans

[Unlicense](LICENSE): kamu malı. Kod ve metinler herhangi bir amaçla, izin ya da atıf gerekmeden kullanılabilir.
