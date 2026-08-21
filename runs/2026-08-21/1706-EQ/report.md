# NSE hourly pattern screen — rally + rounded base near highs

**Executed at:** 2026-08-21 **17:06 IST** (run start)
**Latest data bar:** 2026-08-21 **15:15 IST** — the **2026-08-21** session (`session_age_days` = 0, so this is today's session)
**Chart (all 11 panels):** https://claude.ai/code/artifact/99635bc6-7db7-4c1d-9010-ab62a79bb829

Data snapshot completed 17:11 IST. Market was closed at run time, so the 15:15
stub is a genuine close and was kept rather than dropped.

> These are **candidates matching a geometry, not recommendations.** The screener
> finds a shape; it says nothing about whether the shape resolves upward. Entry,
> sizing, and whether to trade at all are your calls. Prices are matplotlib
> renderings of yfinance data — confirm every level on your own platform before
> acting.

---

## 1. Coverage

| | |
|---|---|
| Universe | **EQ** (full NSE rolling-settlement list) — the skill's default, not a narrowed slice |
| Symbols in universe | 2,291 |
| Symbols with usable data | **2,106 (91.9%)** |
| Missing | 185 — 182 with too few bars (recent listings lack 60d of hourly history), 11 returned nothing from Yahoo |
| Interval / period | 1h / 60d |
| Last closed bar | 2026-08-21 15:15:00 |
| Symbols carrying that bar | 2,027 / 2,106 (**96.2%**) — universe consensus is the same bar |

This is **not** a full-universe scan: 185 EQ symbols (8.1%) were not screened at
all. Coverage is in line with the ~92% the skill documents as normal for
yfinance NSE hourly data.

All 11 surviving hits carry `bars_behind_universe = 0`, so every level quoted
below is priced at the 15:15 bar — no hit is stale relative to the universe.

## 2. Funnel

```
2,106 symbols screened
    │
    ├─ detector (screener.py) ─────────────────────────────► 44 raw hits
    │     first-failing gate, across the 2,062 rejected:
    │       ema_stack              1,501   (71% of universe — no uptrend)
    │       curvature                337   (base too flat to be a base)
    │       base depth               146   (>10% deep = a correction, not a rest)
    │       ema_rising                37
    │       rally_pct                 24
    │       volume / r2 / at-top / vertex / other  17
    │
    ├─ context filters (postfilter.py) ───────────────────► 11 clean hits
    │     33 rejected (reasons overlap):
    │       gap-driven   21   one candle >50% of the "rally" — a gap-and-base
    │                         is a different setup (JUBLFOOD 0.51, KRBL 0.87,
    │                         SOLARINDS 0.82, HFCL 0.53, HINDCOPPER 0.57, …)
    │       illiquid     17   turnover < ₹5cr/day — pretty geometry, unfillable
    │                         entry (HALDER ₹0.07cr, BEEKAY ₹0.04cr, TIIL ₹3.57cr, …)
    │       not-at-high  12   base_high < 97% of the true 60d high — a downtrend
    │                         bounce into overhead supply (RATNAMANI 84.4%,
    │                         SKMEGGPROD 71.5%, KPIL 96.6%, AEGISLOG 96.8%, …)
    │
    └─ visual pass (§4) ──────────────────────────────────► 2 clean / 4 marginal / 5 distrusted
```

The 44 → 11 ratio and the EMA-stack dominance are both in the healthy range the
skill describes. **No threshold was loosened or touched.** The detector's own
diagnostic puts `min_curvature = 0.015` between the universe p75 (0.0067) and
p90 (0.0164), well below p99 (0.0478) — correctly calibrated, so 44 raw hits is
a real reading of the tape and not a threshold artifact.

## 3. Ranked table

Ranked by `rrr_structural` = 15% target ÷ base depth. **RRR ranks the geometry,
not the odds** — it states what a trade pays if it works and is silent on how
often it works. The top row is not the most likely to succeed.

| # | Symbol | Close | Entry (lip) | Base low | Depth % | Risk % to base low | Dist from lip % | Rally % / bars | Base bars | R² | Vol ratio | Turnover ₹cr | % of 60d high | RRR | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | LMW | 19,849.0 | 20,150.00 | 19,384.00 | 3.80 | 3.80 | 1.49 | 21.6 / 44 | 29 | 0.663 | 0.41 | 5.27 | 100.0 | 3.95 | ✅ clean |
| 2 | MARINE | 375.65 | 384.85 | 369.45 | 4.00 | 4.00 | 2.39 | 15.3 / 41 | 13 | 0.808 | 0.54 | 22.80 | 97.4 | 3.75 | ⚠️ marginal |
| 3 | MOTISONS | 17.02 | 17.23 | 16.42 | 4.70 | 4.70 | 1.22 | 28.2 / 31 | 20 | 0.745 | 0.30 | 13.77 | 98.9 | 3.19 | ❌ distrust |
| 4 | JYOTICNC | 990.00 | 991.95 | 944.15 | 4.82 | 4.82 | 0.20 | 20.9 / 45 | 14 | 0.847 | 0.59 | 50.88 | 100.0 | 3.11 | ⚠️ marginal |
| 5 | DYCL | 458.80 | 468.75 | 444.10 | 5.26 | 5.26 | 2.12 | 17.9 / 45 | 30 | 0.531 | 0.41 | 10.19 | 99.1 | 2.85 | ⚠️ marginal |
| 6 | PAYTM | 1,632.0 | 1,638.40 | 1,546.30 | 5.62 | 5.62 | 0.39 | 14.9 / 36 | 30 | 0.717 | 0.60 | 430.46 | 98.9 | 2.67 | ✅ clean |
| 7 | YATRA | 117.26 | 119.70 | 112.57 | 5.96 | 5.96 | 2.04 | 17.2 / 45 | 23 | 0.665 | 0.36 | 6.16 | 98.4 | 2.52 | ❌ distrust |
| 8 | AZAD | 2,837.8 | 2,898.20 | 2,722.00 | 6.08 | 6.08 | 2.08 | 21.1 / 31 | 24 | 0.710 | 0.36 | 71.76 | 97.0 | 2.47 | ⚠️ marginal |
| 9 | LASERPOWER | 338.05 | 341.95 | 320.10 | 6.39 | 6.39 | 1.14 | 19.8 / 28 | 21 | 0.564 | 0.42 | 39.72 | 100.0 | 2.35 | ❌ distrust |
| 10 | PTCIL | 20,701.0 | 20,750.00 | 19,134.00 | 7.79 | 7.79 | 0.24 | 10.4 / 27 | 29 | 0.841 | 0.40 | 15.74 | 100.0 | 1.93 | ❌ distrust |
| 11 | ROLEXRINGS | 182.90 | 189.40 | 173.51 | 8.39 | 8.39 | 3.43 | 17.8 / 36 | 30 | 0.593 | 0.14 | 22.36 | 100.0 | 1.79 | ❌ distrust |

Three names passed on a filter boundary and should be read as such:

- **LMW** — turnover ₹5.27cr against the ₹5.00cr floor. It cleared liquidity by 5%.
- **AZAD** — `pct_of_60d_high` 97.0% against a 97.0% floor, *and* `max_bar_share`
  0.48 against a 0.50 cut. Two boundaries at once.
- **MARINE** — `pct_of_60d_high` 97.4% against the 97.0% floor.

## 4. Visual pass — the tiers

I opened `hits.png` and read all eleven panels. The numbers and the charts
disagree substantially, which is the point of this step: **the two highest-R²
names in the batch (JYOTICNC 0.847, PTCIL 0.841) are both in the bottom two
tiers**, exactly the trap the skill warns about — a V fits a parabola better
than a saucer does.

### ✅ Clean structural match (2)

**PAYTM** — the best structure in the batch and it is not close. A 36-bar
multi-leg advance (1,330 → 1,655) with no single dominant candle, then a base
that genuinely *rounds*: down to 1,546, a smooth curve through the low, and a
symmetric recovery to 1,632 sitting 0.39% under the lip. Both fast EMAs run
underneath the base and rise through it in the final third. ₹430cr/day turnover
means the entry is actually fillable. Nothing to distrust here beyond the base
depth, which §5 covers.

**LMW** — a sustained multi-leg climb from ~16,000 to ~20,100 across 44 bars,
then a shallow 3.8% rest at a new 60-day high, EMAs rising through it. The base
is closer to a *flat* base than a saucer, but a shallow flat base at the highs
is the healthy version of this setup, not a defect. **The real caveat is
liquidity, not geometry:** ₹5.27cr/day on a ₹20,000 stock is thin, and a
₹20,150 entry with a ₹19,384 structural stop is a large rupee risk per share in
a book that trades ~260 shares an hour. Fills, not the pattern, are the
constraint.

### ⚠️ Marginal (4)

**MARINE** — the rally leg is textbook: a clean, sustained 41-bar trend from 268
to 385 with EMAs stacked underneath the whole way. But the base is only **13
bars, about two sessions** — too short to be a base yet, and the lip is set by a
single spike candle to ~392 that also left overhead supply immediately to the
left. This is a two-day pullback that the parabola fit is happy to call a cup.
Worth watching; not yet a base.

**JYOTICNC** — **the shaded window is not a base at all.** It is the final
vertical leg of the rally driving straight into the lip: the last ~14 bars run
945 → 990 almost without a pause, and price closed 0.20% from the entry. There
is no rest to break out of, so there is no low-risk entry left — you would be
buying the top of a vertical move with a stop 4.8% below. There is also a
gap-down scar at bar ~36 (850 → 745) in the window's history. High R² (0.847)
here measures a smooth *advance*, not a base.

**DYCL** — the base does round: 468 → ~446 → 458, with the fast EMA dipping
through and turning up at the end. But **R² 0.531 sits right at the noise floor**
the skill flags (treat anything under 0.55 as unconfirmed), and on the chart the
"cup" is visibly more chop than saucer — a sharp drop off the high, then a
ragged shelf. Structure is plausible, confirmation is not there.

**AZAD** — the pullback from 2,900 to 2,760 and back to 2,838 is an acceptable
rounded rest, and turnover (₹72cr) is fine. What I distrust is the rally that
precedes it: after 60 bars of slow grind (2,300 → 2,500) the move to 2,950
happens in ~18 bars dominated by one candle at **48% of the entire leg**, one
point under the 50% gap-driven cut that removed 21 other names. Combined with
`pct_of_60d_high` landing exactly on 97.0, this is a name that passed twice by a
rounding margin. A gap-and-base has different odds than a rally-and-base, and
this is much closer to the former than the number admits.

### ❌ Distrust despite passing every filter (5)

**MOTISONS** — 60 bars of flat drift around ₹14.0–14.5, then a **near-vertical
~25% ramp in roughly 12 bars** to 17.5, then a 20-bar shelf. `max_bar_share`
0.30 keeps it under the gap filter only because the spike was spread over three
or four candles instead of one. This is an event move being digested, not a
trend that paused. The setup the pattern is meant to capture requires a
pre-existing uptrend; here there is none — the entire advance *is* the anomaly.

**YATRA** — the "rally" is a **V-recovery off the window low**: 107 → 102.5 →
120 in about 22 bars. What follows is a flat, slightly-declining 23-bar shelf,
not a rounded base, and the 119.70 lip is a single wick high from bar ~62 that
sits as overhead supply directly to the left of the current price. Passed
`pct_of_60d_high` at 98.4% because the 60-day window happens to start near the
lows. Wrong shape and wrong context.

**LASERPOWER** — **the preceding 60 bars are a downtrend** (300 → 280). The
advance is a 28-bar V-reversal off that low, and the shaded region is a rising
choppy channel rather than a base — R² 0.564, barely above the noise floor. It
does print a new 60-day high (100.0%), but only because the 60-day window is
itself a decline. This is what a reversal attempt looks like, and it is not the
rally-then-rest structure being screened for.

**PTCIL** — **the textbook version of the trap this step exists to catch.**
Second-highest R² in the batch (0.841) fitted to a V, not a saucer: a spike to
20,600, a hard 7.8% drop to 19,134, a brief chop, then a **vertical re-run to the
highs across the last ~8 bars**, closing 0.24% from the lip. Also the weakest
rally in the batch (10.4%) and the second-deepest base. Buying here is chasing a
vertical move with the widest structural stop on the list.

**ROLEXRINGS** — a flat, choppy 30-bar shelf that tagged 189.4 and is **now
rolling back over**: the final candles are red and price sits 3.43% below the
lip, the furthest of any name here. It is moving away from the trigger, not
coiling under it. `vol_ratio` 0.14 is low enough to fall in the range the skill
flags as more likely a yfinance volume artifact than a genuine dry-up, so the
one bullish-looking number is also the least trustworthy. Deepest base (8.39%)
and worst RRR (1.79).

## 5. Risk reality check — the stop-inside-base problem

**`stop_inside_base` is `True` for all 11 names. There are no exceptions today.**

A 3% stop off the lip lands *inside* every base on this list, mid-cup, where
ordinary chop takes it out without the pattern having failed at all. The
structural stop is the base low, and honoring it costs between 3.8% and 8.4%:

| Symbol | Entry (lip) | 3% stop | Base low | 3% stop sits *above* base low by | Real structural risk | Position size vs a 3% assumption |
|---|---|---|---|---|---|---|
| LMW | 20,150.00 | 19,545.50 | 19,384.00 | 0.80% of entry | **3.80%** | 0.79× |
| MARINE | 384.85 | 373.30 | 369.45 | 1.00% | **4.00%** | 0.75× |
| MOTISONS | 17.23 | 16.71 | 16.42 | 1.68% | **4.70%** | 0.64× |
| JYOTICNC | 991.95 | 962.19 | 944.15 | 1.82% | **4.82%** | 0.62× |
| DYCL | 468.75 | 454.69 | 444.10 | 2.26% | **5.26%** | 0.57× |
| PAYTM | 1,638.40 | 1,589.25 | 1,546.30 | 2.62% | **5.62%** | 0.53× |
| YATRA | 119.70 | 116.11 | 112.57 | 2.96% | **5.96%** | 0.50× |
| AZAD | 2,898.20 | 2,811.25 | 2,722.00 | 3.08% | **6.08%** | 0.49× |
| LASERPOWER | 341.95 | 331.69 | 320.10 | 3.39% | **6.39%** | 0.47× |
| PTCIL | 20,750.00 | 20,127.50 | 19,134.00 | 4.79% | **7.79%** | 0.39× |
| ROLEXRINGS | 189.40 | 183.72 | 173.51 | 5.39% | **8.39%** | 0.36× |

Read the last column as: honoring the structure on PAYTM means roughly **half**
the position a 3%-stop assumption would size, and on ROLEXRINGS about **a
third**. That is not a detail — it changes the reward/risk arithmetic of every
row. A 15% target against a 5.62% structural stop on PAYTM is 2.67:1, not the
5:1 a 3% stop would imply.

The two names I trust structurally are also the two cheapest to stop correctly
(LMW 3.80%, PAYTM 5.62%), which is a happier coincidence than usual.

## 6. Regime note

Bases near highs resolve upward far more often in a trending index than a choppy
one, and this screener has a very different hit rate in the two. That 1,501 of
2,106 symbols (71%) failed the EMA-stack gate is itself a tape reading: most of
the NSE universe is not in an uptrend right now, which argues for treating even
the clean names as individual setups rather than evidence of broad strength.
Whether a pattern is present today and whether it is worth trading today are
different questions, and only a backtest split by index trend state answers the
second. None was run here.

---

*Generated by the `nse-pattern-screener` pipeline. Universe EQ, 1h/60d, run
2026-08-21 17:06 IST on the 2026-08-21 15:15 session. No detector threshold,
filter parameter, or ranking rule was modified for this run.*
