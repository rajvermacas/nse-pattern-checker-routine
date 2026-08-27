# NSE hourly screen — rally + rounded base near highs

| | |
|---|---|
| **Executed at** | **2026-08-27 17:05 IST** (`run_ts_ist`) — run wall-clock start |
| **Latest data bar** | **2026-08-27 15:15** (`last_closed_bar`), session **2026-08-27** |
| **Session age** | `session_age_days = 0` — the newest bar is **today's** session. Not stale. |
| Data snapshot taken | 2026-08-27 17:11 IST (post-fetch) |
| Universe / interval | NSE **EQ**, 1h candles, 60d history |
| Market open at run | No — the 15:15 stub bar is a genuine close and is retained |

**Charts:** https://claude.ai/code/artifact/7f6756b4-a502-4e4a-ad8e-bef3f7af694e — all
eight panels, plus the tiering below. Look at them before acting on anything here.

> These are **candidates matching a geometry, not recommendations**. Entry, sizing,
> and whether to trade at all are your calls. Nothing here was backtested.

---

## 1. Coverage

| | |
|---|---|
| Symbols in universe | 2,288 (full NSE EQ series, from the NSE archive) |
| Symbols with usable data | **2,086 — 91.2%** |
| Dropped | 234 (`no_data_returned` 34, `too_few_bars` 200) |
| Carrying the reported last bar | 1,977 of 2,288 — **94.8%** of those fetched |

This is **not a complete scan.** 202 EQ symbols were screened on no data at all —
mostly recent listings without 60 days of hourly history and symbols that don't map
to `SYMBOL.NS` on Yahoo (`3BBLACKBIO`, `ABANSENT`, `ABMKNO`, `ACGL`, `ADDIND`,
`ADVIKCA`, `AKCAPIT`, `ALFREDHE`, `ALUFLUOR`, `AMAL`, …). Coverage is in line with
the ~92% this pipeline normally returns, and comfortably above the 80% floor, but a
qualifying setup inside those 202 names would not appear below.

Two Yahoo batches were rate-limited mid-fetch; the gap-fill rounds recovered 32 of
the 234 missing symbols and the second round recovered none, which is the signature
of genuinely absent data rather than throttling. **`UNIVERSE` was not overridden** —
this is the skill's default full-EQ slice, not a narrower index.

**Staleness check:** all 8 survivors report `bars_behind_universe = 0`, so every
level quoted below is priced at the 2026-08-27 15:15 bar. No per-hit staleness
adjustment was needed.

---

## 2. Funnel

```
2,086 symbols with data
     ↓  detector (EMA stack, rally ≥10%, curvature ≥0.015, R² ≥0.45, depth ≤10%, at-top)
   33 raw hits
     ↓  context filters
    8 clean hits
     ↓  visual pass (below)
    2 clean · 3 marginal · 3 distrusted
```

**What the context filters cut — 25 names, by reason:**

| Filter | Cut | Names |
|---|---|---|
| Liquidity < ₹5cr/day | 20 | ALBERTDAVD, KRISHIVAL, ADVENTHTL, MARATHON, MASTERTR, A2ZINFRA, JUNIPER, MAXESTATES, DEVX, WONDERLA, PROZONER, BLUSPRING, THEMISMED, DICIND, SURAJLTD, MARALOVER, KAMATHOTEL, DOLPHIN, PREMIERPOL, INDORAMA |
| Not actually at a high (<97% of 60d high) | 10 | ADVENTHTL 88.4%, MASTERTR 81.4%, SPORTKING 95.6%, A2ZINFRA 93.0%, DEVX 93.4%, PROZONER 86.8%, TIRUMALCHM 87.2%, THEMISMED 96.3%, SURAJLTD 86.9%, MARALOVER 92.1% |
| Gap-driven rally (one bar > 50% of the move) | 9 | MARATHON 0.82, MASTERTR 1.07, PRAJIND 0.91, PROZONER 1.21, TIRUMALCHM 0.71, DICIND 0.76, MARALOVER 0.66, TURTLEMINT 0.76, KENNAMET 0.55 |

(Names appear under more than one filter where they failed more than one.)

Liquidity is doing most of the work, as usual — thin names produce clean geometry
and unfillable entries. The 33 → 8 ratio is a healthy funnel; nothing suggests a
mis-calibrated threshold this run.

---

## 3. Ranked table

Ranked by `rrr_structural` = 15% target ÷ risk-to-base-low. **This ranks the
geometry, not the odds** — it states what a trade pays if it works and is silent on
how often it works. The top name is not the most likely to succeed.

| # | Symbol | Close | Entry (lip) | Base low | Depth % | Risk to base low % | Dist from lip % | Vol ratio | R² | Curv | Base bars | Turnover ₹cr | RRR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | BRIGADE | 656.75 | 671.00 | 646.90 | 3.59 | **3.59** | 2.12 | 0.61 | 0.696 | 0.020 | 19 (~2.8 sess) | 13.7 | 4.18 |
| 2 | NILKAMAL | 2081.60 | 2110.00 | 2005.00 | 4.98 | **4.98** | 1.35 | 0.08 | 0.555 | 0.024 | 30 (~4.4 sess) | 6.0 | 3.01 |
| 3 | MOREPENLAB | 96.70 | 99.67 | 92.70 | 6.99 | **6.99** | 2.98 | 0.48 | 0.458 | 0.022 | 30 (~4.4 sess) | 122.2 | 2.15 |
| 4 | HAPPYFORGE | 2250.80 | 2278.80 | 2111.30 | 7.35 | **7.35** | 1.23 | 0.76 | 0.640 | 0.027 | 30 (~4.4 sess) | 15.4 | 2.04 |
| 5 | AVALON | 2242.50 | 2279.20 | 2079.40 | 8.77 | **8.77** | 1.61 | 0.65 | 0.735 | 0.040 | 30 (~4.4 sess) | 55.8 | 1.71 |
| 6 | WELCORP | 2406.80 | 2436.70 | 2204.10 | 9.55 | **9.55** | 1.23 | 0.79 | 0.702 | 0.049 | 22 (~3.2 sess) | 115.1 | 1.57 |
| 7 | TECHNOCRAF | 359.60 | 373.00 | 336.76 | 9.72 | **9.72** | 3.59 | 0.74 | 0.793 | 0.039 | 27 (~3.9 sess) | 39.5 | 1.54 |
| 8 | ASIANENE | 492.70 | 497.95 | 448.75 | 9.88 | **9.88** | 1.05 | 0.29 | 0.725 | 0.048 | 30 (~4.4 sess) | 11.6 | 1.52 |

**Two boundary passes** — a pass at the edge of a filter is not the same evidence as
a pass with margin:

- **HAPPYFORGE** — `pct_of_60d_high` 97.5% against a 97.0% floor
- **AVALON** — `pct_of_60d_high` 97.0% against a 97.0% floor, i.e. exactly on it

---

## 4. Tiers from the visual pass

I looked at all eight panels. This is where I disagree with the numbers.

### Clean structural match (2)

**BRIGADE** — The best structure in the batch. A sustained four-session rally
(20–25 Aug, 588 → 671, max bar share 0.22 so no single candle carries it), then an
orderly shallow pullback to 646.90 and a turn back up. Both EMAs run under the base
and rise through it. At 100% of the 60-day high with no overhead supply. *Caveat:*
the base is only 19 bars ≈ 2.8 sessions — the shallowest and shortest here. It is
early rather than wrong; a two-and-a-half-session pause has not been tested the way
a four-session one has, and it is closer to a high-tight flag than a classic cup.

**MOREPENLAB** — A genuinely sustained rally: 74 → 99.67 across 14–24 Aug on many
bars (max bar share 0.19), and by far the deepest liquidity in the batch at ₹122cr/day.
Base rounds adequately over 4.4 sessions with EMAs rising underneath, at 100% of the
60-day high. *Caveats:* R² 0.458 is a boundary pass over the 0.45 floor, and the base
zigzags more than it rounds — visibly the least smooth of the ones I'm calling clean.
Entry at 99.67 is also chasing a 35% move off the 12 Aug low.

### Marginal (3)

**NILKAMAL** — Turnover ₹5.97cr sits barely over the ₹5cr liquidity floor, so this
is the thinnest name that survived and the one most likely to be unfillable at size.
The rally is near-vertical (1,780 → 2,110 in about two sessions) and the "base" is a
flat shelf with a spike into 2,110 today rather than a saucer. `vol_ratio` 0.08 is
extreme — that is 8% of prior volume, which reads more like the name stopped trading
than like a healthy dry-up. The stock also failed once already at 1,940 on 14 Aug and
fell 8%, which is a choppy character, not a trending one.

**WELCORP** — The underlying move is real and impressive: a two-month flat base at
1,850–1,870 broken decisively on 21–24 Aug to 2,437, back at the lip, ₹115cr/day.
But the geometry is not what this screen claims to find. The "base" is a two-session
V-shaped shakeout to 2,204 and an immediate recovery, not a rounded base, and
`max_bar_share` 0.45 sits just under the 0.50 gap-driven cutoff — that 21 Aug candle
carries nearly half the rally. This is a momentum breakout-retest. Different setup,
different odds; it should not be read as the same thing as BRIGADE.

**ASIANENE** — The most convincing *rally* in the batch: 33% across five sessions
from a clean prior base, bar share 0.17, volume dried to 0.29, price 1.05% off the
lip with EMAs turning up underneath. What holds it back is the base — 9.88% deep,
descending into a sharp V recovery rather than rounding. That makes the structural
stop nearly 10%, which is close to unusable at any reasonable size.

### Distrust, despite passing every filter (3)

**HAPPYFORGE** — The 21 Aug peak of ~2,340 sits **above** the 2,278.80 lip, so there
is overhead supply inside the pattern itself; the filter passed it only because the
lip is measured from the base window, not the swing high. Then a sharp break to
~2,200 and a bounce — a V, not a saucer. Add the boundary 97.5% pass and a `base_low`
of 2,111.30 set by a **single wick** (1.15% of entry below the next-lowest bar).
Both stop readings are quoted in §5; on a closing basis the floor is 2,151.10 and the
risk 5.60% rather than 7.35%. That wick also depresses its RRR rank, so #4 understates
the geometry — but the structure is still one I would not take.

**AVALON** — The same shape as HAPPYFORGE and a worse version of it. A blow-off spike
to ~2,345 on 20 Aug, a break, then a descending drift into 2,079 and a V bounce. It
passed `pct_of_60d_high` at *exactly* 97.0%. Its R² of 0.735 is the second-highest in
the batch, and that is precisely the trap this visual step exists to catch: a V-shaped
reversal fits a parabola better than a genuine rounded base does. Rank #5 on numbers,
last on structure.

**TECHNOCRAF** — Distrusted on data quality before geometry. Its 14 Aug bar spans
215 → 335 on the panel and its history starts later than every other name, which
suggests a bad print or an unadjusted corporate action; if so, the rally percentage
and the 60-day-high comparison are both computed on corrupt inputs. Separately, the
base is a flat shelf at 340–345, not a rounded base, and the 373.00 lip was printed
by a single spike bar *today* that price then closed 3.59% below — the largest
distance-from-lip in the batch. Its R² of 0.793 is the highest here and means nothing.

---

## 5. Risk reality check — the stop-inside-base problem

**All 8 of 8 have the conventional 3% stop landing inside the base.** A stop there
sits mid-cup and gets taken out by ordinary chop *without the pattern having failed
at all*. The structural stop is the base low, and it is the only stop this geometry
supports.

| Symbol | Entry (lip) | 3% stop | Base low = real stop | Real risk % | 3% stop compatible? |
|---|---|---|---|---|---|
| BRIGADE | 671.00 | 650.87 | 646.90 | 3.59% | **No** — but closest of the eight; only 3.97 pts of slack |
| NILKAMAL | 2110.00 | 2046.70 | 2005.00 | 4.98% | **No** — 3% stop sits mid-base |
| MOREPENLAB | 99.67 | 96.68 | 92.70 | 6.99% | **No** — real risk is 2.3× the assumed |
| HAPPYFORGE | 2278.80 | 2210.44 | 2111.30 | 7.35% | **No** — see wick note below |
| AVALON | 2279.20 | 2210.82 | 2079.40 | 8.77% | **No** — real risk is ~2.9× |
| WELCORP | 2436.70 | 2363.60 | 2204.10 | 9.55% | **No** — see wick note below |
| TECHNOCRAF | 373.00 | 361.81 | 336.76 | 9.72% | **No** — real risk is ~3.2× |
| ASIANENE | 497.95 | 483.01 | 448.75 | 9.88% | **No** — deepest base in the batch |

Honoring the structure means risking **3.59% to 9.88%** depending on the name. On
ASIANENE that is roughly a third of the position size a 3% assumption implies, and it
changes the reward/risk arithmetic completely. Do not size any of these as if a 3%
stop were compatible with the pattern, because on none of them is it.

**Wick-set base lows — two readings, and which one the sizing assumes:**

- **HAPPYFORGE** is flagged `base_low_is_wick = true`. `base_low` 2,111.30 sits 1.15%
  of entry below the next-lowest bar; the closing-basis floor is 2,151.10, i.e.
  **5.60% risk instead of 7.35%**. The wick is a real traded price, so `base_low` and
  the RRR rank keep using it and **the sizing above assumes the conservative 7.35%**.
  Worth knowing that its #4 rank is partly an artifact of that one bar.
- **WELCORP** is not flagged (its low is only 0.41% below the next bar) but its two
  readings still diverge widely: closing-basis floor 2,271.20 = **6.79% risk** against
  the 9.55% quoted. **The sizing above assumes 9.55%.**

---

## Regime note

Bases near highs resolve upward far more often in a trending index than a choppy one.
The same screener over the same universe has a materially different hit rate in the
two regimes. That a pattern is present today is a different question from whether it
is worth trading today, and only a backtest split by index trend state answers the
second. Nothing here is such a backtest.

## Method notes

- **No threshold was loosened or tuned this run.** All detector and filter parameters
  are at their committed defaults. The 8 names above came out of a strict pass.
- Charts are matplotlib renderings of yfinance data. EMA seeding and session handling
  differ from TradingView and Kite — treat them as shape verification and confirm
  every price on your own platform before acting.
- Pipeline exit code 0. Fetch was resumable across 58 batches of 40 symbols, serial.
