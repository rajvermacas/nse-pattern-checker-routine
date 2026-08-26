# NSE hourly screen — rally + rounded base near highs

**Executed at:** 2026-08-26 17:05 IST (run wall-clock start)
**Latest data bar:** 2026-08-26 15:15 IST — the **2026-08-26 session** (`session_age_days` = 0, i.e. today's session)

Market was already closed at run time (17:05 IST), so the 15:15 stub is a genuine
close and was kept rather than dropped as an in-progress bar.

**Charts:** https://claude.ai/code/artifact/5dfd6059-ca2e-4db6-8952-ab54ab457362

These are **candidates matching a geometry, not recommendations.** Entry, sizing,
and whether to trade at all are your calls. The ranking below orders the geometry,
never the odds.

---

## 1. Coverage

| | |
|---|---|
| Universe | NSE **EQ** series (rolling settlement) — the skill's default, not a narrowed slice |
| Symbols in universe | 2,291 |
| Symbols with usable data | **2,082 (90.9%)** |
| Missing | 209 — 206 with too few bars (recent listings lacking 60d of hourly history), 28 returning no data |
| Interval / period | 1h / 60d |
| Last closed bar | 2026-08-26 15:15:00 IST |
| Symbols carrying that bar | 1,987 / 2,082 (95.4%) |

This is **not** a full-universe scan. 209 EQ symbols were never screened; any pattern
in them is invisible to this run. Two gap-fill rounds recovered nothing on the second
pass, which indicates the remainder is genuinely absent from Yahoo rather than
rate-limited — one batch was throttled mid-fetch and did recover on retry.

95.4% of covered symbols carry the reported last bar, and **all 17 hits below sit at
that bar** (`bars_behind_universe` = 0 for every one), so every price quoted here is
as of 2026-08-26 15:15 IST.

## 2. Funnel

```
2,082 symbols screened
    │
    ├─ detector (EMA stack, rally ≥10%, depth ≤10%, curvature ≥.015,
    │            R² ≥.45, |vertex| ≤.65, at-top, lip ≤4%, vol ≤.85)
    ▼
   41 raw hits
    │
    ├─ context filters cut 24:
    │     illiquid (<₹5cr/day) ......... 18 names
    │     not-at-high (<97% of 60d) .... 14 names
    │     gap-driven (>50% one bar) .... 12 names
    │     (most rejects tripped more than one)
    ▼
   17 clean hits
    │
    ├─ visual pass (below) cut 4 to distrusted, 9 to marginal
    ▼
    4 clean structural matches
```

Named rejects worth knowing about: **SOLARINDS** (95% of the rally in one bar),
**TIRUMALCHM** and **WAKEFIT** (at 87% and 93% of their 60-day high — the
downtrend-bounce case the filter exists for), **HATSUN**, **UFLEX**, **VSSL** and
**PRSMJOHNSN** (turnover below ₹5cr/day).

The 41 → 17 funnel is in the healthy band the skill describes; nothing suggests a
mis-calibrated threshold, and **no threshold was loosened** for this run.

## 3. Ranked table

Ranked by `rrr_structural` = 15% target ÷ base depth. This reduces to inverse base
depth — it says what the trade pays if it works and is **silent on how often it
works**. Do not read row 1 as most likely to succeed.

| # | Symbol | RRR | Entry (lip) | Base low | Depth % | Risk to base low % | Dist from lip % | Base bars | ≈ Sessions | Rally % | R² | Vol ratio | Turnover ₹cr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | BRIGADE | 4.18 | 671.00 | 646.90 | 3.59 | 3.59 | 2.37 | 12 | **1.7** | 13.87 | 0.866 | 0.79 | 13.7 |
| 2 | NILKAMAL | 3.12 | 2110.00 | 2008.60 | 4.81 | 4.81 | 0.33 | 18 | 2.6 | 17.97 | 0.848 | 0.09 | 6.7 |
| 3 | SEAMECLTD | 2.98 | 1716.90 | 1630.50 | 5.03 | 5.03 | 3.42 | 30 | 4.4 | 14.89 | 0.865 | 0.25 | 6.2 |
| 4 | JYOTICNC | 2.91 | 1020.00 | 967.45 | 5.15 | 5.15 | 0.72 | 23 | 3.3 | 18.78 | 0.794 | 0.50 | 53.8 |
| 5 | HAPPSTMNDS | 2.82 | 457.00 | 432.75 | 5.31 | 5.31 | 2.00 | 22 | 3.2 | 13.12 | 0.604 | 0.46 | 30.9 |
| 6 | MOREPENLAB | 2.65 | 98.25 | 92.70 | 5.65 | 5.65 | 0.37 | 20 | 2.9 | 21.75 | 0.736 | 0.50 | 119.6 |
| 7 | KIRIINDUS | 2.54 | 519.80 | 489.10 | 5.91 | 5.91 | 0.92 | 12 | **1.7** | 30.62 | 0.786 | 0.26 | 7.2 |
| 8 | GLAXO | 2.49 | 3049.90 | 2866.30 | 6.02 | 6.02 | 0.51 | 30 | 4.4 | 16.60 | 0.716 | 0.36 | 14.3 |
| 9 | GPPL | 2.43 | 173.72 | 163.00 | 6.17 | 6.17 | 2.42 | 30 | 4.4 | 13.20 | 0.795 | 0.74 | 15.1 |
| 10 | FCL | 2.27 | 50.90 | 47.53 | 6.62 | 6.62 | 0.16 | 13 | **1.9** | 21.32 | 0.873 | 0.74 | 28.5 |
| 11 | JNPR | 2.11 | 277.00 | 257.31 | 7.11 | 7.11 | 2.89 | 27 | 3.9 | 17.38 | 0.806 | 0.30 | 31.6 |
| 12 | MOTILALOFS | 1.98 | 1048.00 | 968.55 | 7.58 | 7.58 | 0.76 | 26 | 4.0 | 12.82 | 0.868 | 0.71 | 53.5 |
| 13 | INDOBORAX | 1.84 | 524.50 | 481.70 | 8.16 | 8.16 | 3.86 | 24 | 3.5 | 25.34 | 0.489 | 0.22 | 5.1 |
| 14 | COHANCE | 1.80 | 481.00 | 441.00 | 8.32 | 8.32 | 3.88 | 29 | 4.2 | 10.22 | 0.779 | 0.36 | 24.0 |
| 15 | ASIANENE | 1.74 | 490.95 | 448.75 | 8.60 | 8.60 | 2.53 | 30 | 4.4 | 30.91 | 0.609 | 0.26 | 11.0 |
| 16 | AVALON | 1.71 | 2279.30 | 2079.40 | 8.77 | 8.77 | 1.07 | 30 | 4.4 | 22.34 | 0.743 | 0.61 | 55.8 |
| 17 | RATNAVEER | 1.66 | 286.00 | 260.10 | 9.06 | 9.06 | 2.35 | 16 | 2.3 | 27.77 | 0.598 | 0.64 | 92.0 |

**Read the bar counts as sessions.** These are hourly candles at roughly 6.9 bars
per NSE session, so the widest base here is **4.4 sessions**, not 30 days — the
entire 110-bar plot window spans about three weeks. Three names build their whole
"base" in under two sessions (BRIGADE, KIRIINDUS, FCL), which is thin evidence that
a base exists at all and is the single biggest caveat on this batch.

**Two boundary passes** — a boundary pass is not the same evidence as a margin pass:

- **INDOBORAX** — turnover ₹5.09cr against the ₹5.0cr floor.
- **AVALON** — `pct_of_60d_high` 97.0% against the 97.0% floor, meaning real
  overhead supply roughly 3% above the base high.

## 4. Tiers from the visual pass

I looked at all 17 panels. The tiers below disagree with the ranking in several
places, which is the point of the step.

### Clean structural match (4)

- **MOREPENLAB** (#6) — the best structure in the batch. A sustained 22% multi-bar
  climb from ₹73 to ₹98, then a shallow, genuinely rounded 20-bar (≈2.9-session)
  base that dips to ₹93.5 and recovers; both EMAs run under the base and rise
  through it; price is pressing the lip (0.37% away). Easily the most liquid name
  here at ₹120cr/day.
- **GLAXO** (#8) — a textbook 30-bar (≈4.4-session) rounded U: down from ₹3,050 to
  ₹2,866, curved, and back to ₹3,034, with the fast EMA dipping and rising through.
  The leg into it was steep, but the base itself is the cleanest rounding on the
  sheet.
- **MOTILALOFS** (#12) — a clean ascending consolidation resolving upward on the
  final bars, EMAs stacked under and rising, ₹53cr/day. **Its rank is depressed by a
  wick** — see the sizing note below.
- **NILKAMAL** (#2) — not a cup: a flat shelf at ₹2,020–2,040 breaking out on the
  last two bars. But the volume dry-up is the most emphatic in the batch
  (ratio 0.09) and it is at a genuine 60-day high. A legitimate
  consolidation-and-breakout, just a different pattern than the one advertised.

### Marginal (9)

- **JYOTICNC** (#4) — strong, orderly uptrend, but **there is no base**: the shaded
  window is still rising. The 5.15% "depth" comes from a dip inside a continuation
  leg. Fine as a trend-continuation name, wrong as a rounded-base match.
- **FCL** (#10) — tight 13-bar base sitting 0.16% under the lip, but that is only
  **1.9 sessions**, and the approach into it is steep.
- **AVALON** (#16) — a reasonably rounded 30-bar (≈4.4-session) base, undercut by
  8.77% depth and the boundary pass on the at-high filter.
- **ASIANENE** (#15) — rounds, but deep (8.6%) and it follows a near-vertical 31%
  advance.
- **SEAMECLTD** (#3) — a flat shelf, not a cup. The fast EMA runs **flat** through
  the base rather than rising through it, and the ₹1,717 lip is a spike high, so the
  resistance is a wick rather than a built level.
- **HAPPSTMNDS** (#5) — choppy shelf, weakest-but-one fit (R² 0.604), and
  `max_bar_share` 0.48 against the 0.50 gap-driven floor: nearly half the rally came
  from one bar. It passed that filter by a hair.
- **BRIGADE** (#1) — **the #1 rank is an artifact.** Its base is only 12 bars, and a
  short base is mechanically shallow, which is exactly what RRR rewards. At ≈6.9 bars
  per session that is a **1.7-session** pullback from a spike top, with the fast EMA
  flat through it. Shallow because brief, not shallow because tight.
- **GPPL** (#9) — flat shelf at ₹163–166, and the ₹173.72 lip is set by a single
  spike candle that price has already fallen 2.4% back from.
- **KIRIINDUS** (#7) — a near-vertical 31% advance with a 12-bar (**1.7-session**)
  pause. Thin evidence that a base exists at all.

### Distrust despite passing every filter (4)

- **COHANCE** (#14) — **the base is a downtrend.** Price spiked to ₹481, fell to
  ₹443, and the fast EMA has rolled over and declines through the entire window.
  There is heavy overhead supply at ₹465–475, rejected twice earlier in the panel.
  This is a failed breakout, structurally the opposite of the setup.
- **RATNAVEER** (#17) — the V-bounce the skill exists to catch: a sharp 9% drop and
  an equally sharp recovery over 16 bars (≈2.3 sessions), sitting on top of a 37%
  run. Deepest base in the batch, and the shape is a checkmark, not a saucer.
- **INDOBORAX** (#13) — weakest fit here (R² 0.489, barely over the 0.45 floor), a
  noisy shelf after a near-vertical 25% spike, **and** the boundary liquidity pass.
  Three weak signals stacked.
- **JNPR** (#11) — the base sags rather than rounds, the fast EMA is flat-to-rolling
  through it, and the ₹277 lip is a spike wick at ₹282. It is recovering a prior
  range rather than breaking new ground.

## 5. Risk reality check — the stop-inside-base problem

**All 17 have a 3% stop landing inside the base.** Not one of these is compatible
with a fixed 3% stop; such a stop sits mid-cup and gets taken out by ordinary chop
without the pattern having failed at all.

| Symbol | Entry (lip) | 3% stop | Base low (real stop) | Real risk % | 3% stop compatible? |
|---|---|---|---|---|---|
| BRIGADE | 671.00 | 650.87 | 646.90 | 3.59 | No — 3% lands ₹4 above the base low |
| NILKAMAL | 2110.00 | 2046.70 | 2008.60 | 4.81 | No |
| SEAMECLTD | 1716.90 | 1665.39 | 1630.50 | 5.03 | No |
| JYOTICNC | 1020.00 | 989.40 | 967.45 | 5.15 | No |
| HAPPSTMNDS | 457.00 | 443.29 | 432.75 | 5.31 | No |
| MOREPENLAB | 98.25 | 95.30 | 92.70 | 5.65 | No |
| KIRIINDUS | 519.80 | 504.21 | 489.10 | 5.91 | No |
| GLAXO | 3049.90 | 2958.40 | 2866.30 | 6.02 | No |
| GPPL | 173.72 | 168.51 | 163.00 | 6.17 | No |
| FCL | 50.90 | 49.37 | 47.53 | 6.62 | No |
| JNPR | 277.00 | 268.69 | 257.31 | 7.11 | No |
| MOTILALOFS | 1048.00 | 1016.56 | 968.55 | 7.58 | No — see wick note |
| INDOBORAX | 524.50 | 508.77 | 481.70 | 8.16 | No |
| COHANCE | 481.00 | 466.57 | 441.00 | 8.32 | No |
| ASIANENE | 490.95 | 476.22 | 448.75 | 8.60 | No |
| AVALON | 2279.30 | 2210.92 | 2079.40 | 8.77 | No |
| RATNAVEER | 286.00 | 277.42 | 260.10 | 9.06 | No |

Honoring the structure means risking the full `risk_pct_to_base_low` — 3.6% to 9.1%
depending on the name. On an 8%-deep base, honoring the structure cuts position size
to roughly **37% of what a 3% stop would imply** for the same rupee risk, and it
changes the reward/risk arithmetic entirely. BRIGADE is the only name where the two
numbers are close (3.59% vs 3%), and that is because its base is 12 bars long, not
because it is tight.

### One base low is set by a single wick

**MOTILALOFS** — `base_low` ₹968.55 sits 1.94% of entry below the next lowest bar.
The closing-basis floor is ₹990.00, i.e. **5.53% risk** rather than the 7.58%
quoted. The wick is a real traded price, so `base_low` and the RRR ranking keep
using it — but that single bar both inflates the stated risk and pushes the name
down to 12th. On a closing-basis stop its RRR would be ≈2.71, which would place it
6th. **If you size this one, say which stop you are assuming:** ₹968.55 is the
conservative structural stop; ₹990.00 is the closing-basis stop and the reason the
name reads worse than it looks.

## 6. Regime note

Bases near highs resolve upward far more often in a trending index than a choppy
one — the same screener on the same universe has a very different hit rate in the
two. Whether a pattern is present today is a different question from whether it is
worth trading today, and only a backtest split by index trend state answers the
second.

---

*Charts are matplotlib renderings of yfinance data, not screenshots from any
platform. EMA seeding and session handling differ from TradingView and Kite, so
treat them as shape verification and confirm prices on your own platform before
acting. No detector threshold, filter parameter, or ranking rule was modified for
this run.*
