# NSE hourly pattern screen — rally + rounded base near highs

**Executed at:** 2026-08-28 **17:04 IST** (data snapshot finished 17:10 IST)
**Latest data bar screened:** **2026-08-28 15:15 IST** — session **2026-08-28**
**Session age:** 0 days — this *is* today's session, screened after the close.

**Chart of all 10 hits (one click, full size):**
https://claude.ai/code/artifact/6ef533f3-da02-4f57-80ce-8e932f8c555f

These are **candidates matching a geometry, not recommendations.** The screener
finds a shape. Whether any of them is worth trading, at what size, or at all,
is your call. Prices are yfinance data rendered by matplotlib — EMA seeding and
session handling differ from TradingView and Kite, so confirm levels on your own
platform before acting.

---

## 1. Coverage

| | |
|---|---|
| Universe | **EQ** (full NSE rolling-settlement list) — 2,287 symbols |
| Usable data | **2,182 / 2,287 = 95.4%** |
| Missing | 105 symbols — 26 returned nothing from Yahoo, the rest lacked 60 days of hourly history (recent listings, symbols that don't map to `SYMBOL.NS`) |
| Interval / history | 1h, 60d |
| Last closed bar | 2026-08-28 15:15 |
| Symbols carrying that bar | 2,078 / 2,182 (95.2%) — universe consensus last bar is also 2026-08-28 15:15 |

This is not a full-universe scan: 105 EQ symbols were not screened at all.
The market was closed at run time (17:04 IST), so the 15:15 stub bar is a
genuine close and was **kept**, not dropped.

**All 10 hits below have `bars_behind_universe = 0`** — every one is priced at
the 15:15 bar, so the universe timestamp is the correct price time for all of
them. No per-hit staleness caveat applies today.

## 2. Funnel

```
2,182 symbols scanned
    │  detector: EMA stack, EMA rising, rally ≥10%, base depth ≤10%,
    │            curvature ≥0.015, R² ≥0.45, |vertex| ≤0.65, at-top,
    │            lip ≤4%, vol dry-up ≤0.85          (0 crashed)
    ▼
   38 raw hits
    │  context filters
    ▼
   10 clean hits
```

What the 28 rejections cut (reasons overlap):

| Filter | Cut | What it was catching |
|---|---|---|
| **Liquidity** < ₹5 cr/day | 22 names | Pretty geometry, unfillable entry — CYBERMEDIA at ₹0.01cr, SILINV ₹0.06cr, BANG ₹0.03cr |
| **Not at a real high** < 97% of 60d high | 9 names | Downtrend bounces reading as "base near the window high" — GRAUWEIL at 82.5%, BANG 86.2%, PROZONER 86.8% |
| **Gap-driven rally** one bar > 50% of the move | 19 names | Gap-and-base ≠ rally-and-base — PROZONER 1.21, PAUSHAKLTD 1.19, STAR 1.11, GENUSPOWER 1.02 |

Worth noting: **KLBRENG-B** had the strongest raw geometry in the entire batch
(curvature 0.063, R² 0.885) and was killed by the gap filter at 0.85 — a single
bar was 85% of its "rally". That is the filter doing exactly its job.

**1 of the 10 survivors passed on an edge, not with margin:** KRBL at
`max_bar_share 0.50` against a 0.50 cut. A boundary pass is weaker evidence
than a margin pass, and it is flagged again in the tiers below.

## 3. Ranked table

Ranked by structural RRR (15% target ÷ risk to base low). **RRR ranks the
geometry, not the odds** — it says what a trade pays if it works and is
completely silent on how often it works. The top name is not the most likely
to succeed.

| # | Symbol | RRR | Entry (lip) | Base low | Depth % | Risk to base low % | Dist from lip % | Base bars | R² | Curv | Vol ratio | Turnover ₹cr | % of 60d high |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **MCX** | 4.31 | 3362.00 | 3245.00 | 3.48 | 3.48 | 0.89 | 16 (~2.5 sess) | 0.894 | 0.021 | 0.69 | 571.3 | 100.0 |
| 2 | **HINDZINC** | 4.12 | 631.20 | 608.25 | 3.64 | 3.64 | 1.46 | 15 (~2.3 sess) | 0.760 | 0.020 | 0.44 | 245.4 | 100.0 |
| 3 | **IDBI** | 3.05 | 96.23 | 91.50 | 4.92 | 4.92 | 3.69 | 15 (~2.2 sess) | 0.860 | 0.018 | 0.48 | 19.3 | 100.0 |
| 4 | **PARADEEP** | 3.01 | 168.00 | 159.61 | 4.99 | 4.99 | 1.49 | 19 (~2.8 sess) | 0.557 | 0.027 | 0.53 | 26.7 | 100.0 |
| 5 | **TIMEX** | 2.68 | 657.00 | 620.25 | 5.59 | 5.59 | 0.15 | 15 (~2.2 sess) | 0.818 | 0.023 | 0.63 | 10.7 | 100.0 |
| 6 | **KRBL** | 2.64 | 452.70 | 427.00 | 5.68 | 5.68 | 3.79 | 18 (~2.6 sess) | 0.656 | 0.019 | 0.59 | 15.3 | 100.0 |
| 7 | **FCL** | 2.43 | 51.03 | 47.88 | 6.17 | 6.17 | 1.96 | 16 (~2.3 sess) | 0.777 | 0.036 | 0.68 | 31.9 | 99.4 |
| 8 | **SOLARA** | 2.26 | 644.40 | 601.55 | 6.65 | 6.65 | 3.21 | 25 (~3.6 sess) | 0.775 | 0.029 | 0.18 | 6.2 | 98.6 |
| 9 | **REDINGTON** | 2.01 | 378.45 | 350.15 | 7.48 | 7.48 | 3.13 | 29 (~4.2 sess) | 0.663 | 0.025 | 0.76 | 75.3 | 100.0 |
| 10 | **PTCIL** | 1.94 | 22200.00 | 20480.00 | 7.75 | 7.75 | 0.41 | 26 (~3.8 sess) | 0.592 | 0.052 | 0.56 | 32.3 | 100.0 |

## 4. Tiers — from actually looking at the charts

I opened every panel, then re-rendered all ten single-column because several
calls hinged on whether the fast EMA runs *under* the base or through it. Four
names moved down a tier on the second look. **The ranking above and the tiers
below disagree, and where they disagree the charts win.** The #2, #3, #8 and #9
names by RRR are all in the bottom tier.

### Clean structural match — 3

**MCX** (RRR 4.31, entry 3362) — the best chart in the batch by a distance.
A sustained stair-step advance from 2,640 to 3,360 across three full weeks,
with both EMAs rising underneath the entire move and never lost. The base is a
tight 16-bar shelf at the high, 3.48% deep, fast EMA running right beneath it.
₹571cr/day turnover, the most liquid name here. **Caveat: it is a flat shelf,
not a rounded cup** — if what you want is specifically a saucer, this isn't one.
It is a better structure than most of the actual saucers below.

**FCL** (RRR 2.43, entry 51.03) — closest to the pattern as intended. Two weeks
of genuine quiet accumulation at 41–44, then a stepwise multi-session advance
to 51 with no single bar dominating (max bar share 0.27). The base is an orderly
shallow pullback to 47.88 and a recovery to 50.03. Both EMAs rise underneath and
the fast EMA runs under the base. Rally is sustained, not one candle.

**TIMEX** (RRR 2.68, entry 657) — sustained, orderly climb from 522 to 657
across five sessions with broad participation, EMAs stacked and rising below the
whole move. The base is a pullback to 620 followed by a decisive push to a new
high. **Two caveats:** the base is a shallow two-day flag rather than a cup, and
at 0.15% from the lip there is nothing here to buy at a discount — price is
already at the high. Also the thinnest of the three at ₹10.7cr/day.

### Marginal — 3

**PARADEEP** (RRR 3.01) — 2.5 weeks flat at 145–152, then a vertical 13.5% move
to 168 in about two sessions. Structure is intact and price is back at highs
with EMAs steeply rising underneath, but this is a **breakout-and-flag, not a
rally-and-base**: the advance is two days old and the "base" is one pullback
inside it. Nothing wrong with it — it just isn't the pattern, and a two-day-old
vertical move is a different risk proposition.

**KRBL** (RRR 2.64) — the underlying advance from 372 to 452 is real and
sustained over two weeks with EMAs underneath. But price at 435.55 is still
**3.79% below the lip and sitting on a fast EMA that has flattened** — the base
has not reclaimed anything yet. Compounding it, this is the **edge pass**: max
bar share landed exactly on the 0.50 cut, so one bar was half the rally leg.
Two independent reasons to wait.

**PTCIL** (RRR 1.94) — genuine sustained advance from 19,000 to 22,200 with EMAs
rising beneath, and price is breaking to a new high right now (0.41% from lip).
But the "base" is a **deep 7.75% V**, not a rounded base, and R² 0.592 is the
weakest fit in the batch. The trend is trustworthy; the base label is not, and
7.75% structural risk is the worst in the table.

### Distrust despite passing every filter — 4

**IDBI** (RRR 3.05, R² 0.860) — **the textbook version of the trap this step
exists to catch.** Two weeks of steady *downtrend* from 84 to 81, then a
vertical gap-and-go from 82 to 96 in three sessions. What the detector called a
base is the **first pullback off that spike, still in progress** — price is
falling from 96.23 to 92.68 and resting on a fast EMA it is still descending
toward. There is no right side to this base. The high R² is fitting the top of a
spike, not a saucer. The preceding trend is *down*, which is the opposite of
what the setup requires.

**HINDZINC** (RRR 4.12 — #2 by rank) — the left half of the chart is an
unambiguous two-week decline from 607 to 555. The 14.45% "rally" the detector
measured **is the right leg of a V-recovery**, not a fresh advance. It did print
a genuine new 60-day high at 631, which is why the at-the-high filter passed it,
but the base is two sessions of chop with the fast EMA running *through* it
rather than under it: spike to 631, drop to 611, bounce to 622. Rank 2 on
geometry, bottom tier on structure.

**SOLARA** (RRR 2.26) — near-vertical 29.7% move from 520 to 655 in three
sessions off a flat shelf, then a **rolling top**: high 644, drop to 601, chop
back to 623, with the fast EMA rolled over and sitting *above* much of the base.
That is the post-parabolic distribution shape, not a rounded base. The 0.18
volume ratio is an extreme dry-up rather than a healthy one, and at **₹6.2cr/day
it barely cleared the ₹5cr liquidity floor** — the thinnest survivor.

**REDINGTON** (RRR 2.01) — multi-week decline from 358 to 325, then a V recovery
to 378. Same failure mode as HINDZINC and it passed for the same reason: the
recovery high happens to be the 60-day high. The base is 29 bars of wide,
choppy, two-legged movement — 378 down to 350, up to 373, back to 366 — with no
rounding at any point. A V-bottom recovery into the top of the prior range is a
different trade with different odds.

## 5. Risk reality check — the stop-inside-base problem

**All 10 of 10 names have a 3% stop landing inside the base.** Not most — all.
A 3% stop on any of these sits mid-cup and gets taken out by ordinary chop
*without the pattern having failed at all*. The base low is the only stop the
structure supports.

| Symbol | Entry (lip) | 3% stop | Base low (real stop) | Structural risk | 3% stop compatible? |
|---|---|---|---|---|---|
| MCX | 3362.00 | 3261.14 | 3245.00 | **3.48%** | No — but by only 0.48pp, the closest in the batch |
| HINDZINC | 631.20 | 612.26 | 608.25 | **3.64%** | No — 3% stop sits 4.01 above the base low |
| IDBI | 96.23 | 93.34 | 91.50 | **4.92%** | No — 3% stop is mid-base |
| PARADEEP | 168.00 | 162.96 | 159.61 | **4.99%** | No — real risk is 1.7× the assumed |
| TIMEX | 657.00 | 637.29 | 620.25 | **5.59%** | No — real risk is 1.9× |
| KRBL | 452.70 | 439.12 | 427.00 | **5.68%** | No — real risk is 1.9× |
| FCL | 51.03 | 49.50 | 47.88 | **6.17%** | No — real risk is 2.1× |
| SOLARA | 644.40 | 625.07 | 601.55 | **6.65%** | No — real risk is 2.2× |
| REDINGTON | 378.45 | 367.10 | 350.15 | **7.48%** | No — real risk is 2.5× |
| PTCIL | 22200.00 | 21534.00 | 20480.00 | **7.75%** | No — real risk is 2.6× |

**What this does to sizing:** honoring the structure on PTCIL means 7.75% risk,
not 3% — which cuts position size to roughly 39% of what a 3% assumption would
give, and changes the whole reward/risk arithmetic. On FCL it is 6.17% vs 3%,
so roughly half the size.

No name in this batch has `base_low_is_wick = true`, so the base lows above are
not artifacts of a single outlier bar and the dual-stop caveat does not apply
today. For context, the closing-basis floors are meaningfully tighter on a few:
MCX 2.65% (vs 3.48%), KRBL 4.79% (vs 5.68%), SOLARA 5.62% (vs 6.65%), FCL 5.25%
(vs 6.17%). The wick-inclusive figure remains the conservative stop and is what
the table and the ranking use.

## 6. Regime

Bases near highs resolve upward far more often in a trending index than a choppy
one, and the same screener on the same universe has a very different hit rate in
the two. That a pattern is present today is a different question from whether it
is worth trading today, and only a backtest split by index trend state answers
the second. This run does not attempt that.

---

## Method notes

- **No threshold was loosened.** Every parameter is at its default:
  `min_curvature 0.015`, `min_r2 0.45`, `vertex_window 0.65`, `min_rally 0.10`,
  `base_max_depth 0.10`, `max_dist_from_high 0.04`, `min_turnover ₹5cr`,
  `min_pct_60d_high 97`, `max_bar_share 0.5`, target 15%.
- Funnel ratio 2,182 → 38 → 10 is in the healthy band the skill describes
  (~40 raw, 10–15 clean). Nothing suggests miscalibration in either direction.
- The 15:15 bar was kept because the market was closed at run time. A
  mid-session run of this same screen would drop it.
