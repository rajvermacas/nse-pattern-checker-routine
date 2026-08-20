# NSE hourly screen — rally + rounded base near highs

**2026-08-20** · run 21:08 IST · universe `nifty500` · interval `1h`

> These are **candidates matching a geometry, not recommendations.** The screener
> finds a shape. It says nothing about whether the shape resolves upward, and
> nothing about whether today is a good day to own any of it. Entry, sizing, and
> whether to trade at all are your calls. Confirm every price on your own
> platform — these charts are matplotlib renderings of yfinance data, and EMA
> seeding and session handling differ from TradingView and Kite.

---

## 1. Coverage and last closed bar

| | |
|---|---|
| Universe scanned | **`nifty500` — 500 symbols** |
| Symbols with usable 60d hourly data | **500 / 500 (100%)** |
| Interval | 1h (~7 bars per session) |
| Last closed bar | **2026-08-20 15:15 IST** for 420 symbols; **14:15 IST** for the other 80 |
| Market state at run | Closed (21:08 IST) — the 15:15 stub is a genuine close and was kept, not dropped |

**This is not a full-NSE scan.** The routine defaults `UNIVERSE=nifty500`, which is
a deliberate narrowing versus the skill's own default of the full ~2,293-symbol EQ
list — a fresh cloud clone has no parquet cache, so a full EQ pull costs 15–40
minutes every run. Roughly 1,800 EQ names, including most of the small-cap tail
where these bases are most common, **were never looked at today.**

**Two data-quality notes, both mine to flag rather than the script's:**

- The pipeline logged coverage as `500/499 (100%)`. `universe.txt` has no trailing
  newline, so `wc -l` undercounts by one. Real coverage is 500/500. Cosmetic.
- **Ragged last bar.** 80 of 500 symbols (16%) have no 15:15 bar from Yahoo. Among
  today's six survivors, **JUBLFOOD and PAYTM are evaluated as of 14:15**, one hour
  staler than the other four. `run_meta.json` reports the panel-wide max (15:15),
  and the chart header reports 14:15 because it inherits the timestamp of the first
  hit plotted. Neither is wrong; both are incomplete. For those two names, "distance
  from lip" and "last close" are an hour old.

---

## 2. Funnel

```
  500 symbols (nifty500, 100% fetched)
   │
   ├─ detector: EMA stack / EMA rising / rally ≥10% / depth ≤10% /
   │            curvature ≥0.015 / R² ≥0.45 / |vx| ≤0.65 / at-top /
   │            lip ≤4% / vol dry-up ≤0.85
   ▼
    8 raw hits
   │
   ├─ turnover ≥ ₹5cr/day ................ cut 0
   ├─ base high ≥ 97% of 60d high ........ cut 1  → ZEEL (92.4% — a bounce, not a base)
   ├─ max single-bar share ≤ 0.50 ........ cut 2  → OBEROIRLTY (0.51), ZEEL (0.58)
   ▼
    6 clean hits
   │
   └─ visual pass (mine) ................. cut 3  → 2 clean, 1 marginal, 3 distrusted
```

Eight raw hits from 500 names is a *thin* day by the skill's own yardstick — it
expects ~40 raw from ~2,000 symbols, so 8 from 500 is roughly on-rate, not a
signal of anything. Both rejects were caught by context filters the detector
cannot see: ZEEL sat 7.6% under its 60-day high (the classic downtrend-bounce
false positive), and OBEROIRLTY's rally was 51% one candle.

---

## 3. Ranked table

Ranked by structural RRR — **which ranks the geometry, not the odds.** It states
what a trade pays if it works and is completely silent on how often it works. A
4.5 RRR at a 20% hit rate is worse than a 2.3 at 50%. The top name is not the
most likely to work.

| # | Symbol | Close | RRR | Entry (lip) | Base low | Depth | Dist from lip | Vol ratio | R² | Curv | Bar share | % of 60d high | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **JUBLFOOD** | 507.30 | 4.53 | 512.60 | 495.65 | 3.31% | 1.03% | 0.22 | 0.703 | 0.0231 | **0.50** | 98.5% | ₹85cr |
| 2 | **NEULANDLAB** | 23573.00 | 4.29 | 23845.00 | 23011.00 | 3.50% | 1.14% | 0.46 | 0.736 | 0.0208 | 0.17 | 100.0% | ₹83cr |
| 3 | **PAYTM** | 1603.60 | 3.04 | 1626.50 | 1546.30 | 4.93% | 1.41% | 0.56 | 0.605 | 0.0329 | 0.27 | 98.2% | ₹405cr |
| 4 | **DEVYANI** | 147.80 | 2.94 | 147.99 | 140.43 | 5.11% | **0.13%** | 0.29 | 0.879 | 0.0330 | 0.32 | 100.0% | ₹48cr |
| 5 | **BLS** | 273.00 | 2.54 | 282.17 | 265.50 | 5.91% | 3.25% | 0.43 | 0.599 | 0.0248 | 0.25 | 100.0% | ₹22cr |
| 6 | **SAPPHIRE** | 241.35 | 2.27 | 245.29 | 229.05 | 6.62% | 1.61% | **0.18** | 0.877 | 0.0314 | 0.42 | 100.0% | ₹25cr |

*RRR reported as `target 15% ÷ risk%`. The raw `rrr_structural` field in
`hits_clean.json` is 100× these values (453.17, 428.57, …) — a percent-vs-fraction
units artifact in `postfilter.py`. It is a constant scale factor, so the **ranking
is unaffected**; only the printed magnitude is wrong. Flagged, not fixed.*

---

## 4. Visual pass — what the charts say that the numbers don't

I opened `hits.png` and read all six panels. The numbers and my eyes disagree
about half this list, and where they disagree I side with the chart.

### ✅ Clean structural match (2)

**NEULANDLAB** — *the best structure in the batch, and it is not the top-ranked name.*
The rally is genuinely sustained: a long multi-week climb from ~19,000 to ~23,900
with no single candle carrying it (bar share 0.17, lowest but one). The base
rounds properly — a real saucer from 23,850 down to 23,011 and back to ~23,700 —
rather than snapping back. Both EMAs run underneath it and rise through, exactly
what the setup wants. At 100% of its 60-day high with no overhead supply to the
left. *Caveat that is not about the pattern:* at ₹23,573/share, position sizing is
coarse — one share is a meaningful position for most accounts, and a 3.5% stop on
a ₹23.8k instrument is ₹834 of risk per share.

**DEVYANI** — the highest R² in the batch (0.879) and, unusually, the fit is
honest. Sustained rally 115→148, base shallow and genuinely rounded, EMAs stacked
underneath and rising through it, at 100% of the 60-day high. Vertex at −0.186,
the most left-shifted in the batch, meaning the turn happened early and the right
side has had time to build — the healthy version of this shape.
*But the entry is already gone:* at 0.13% from the lip, price is **at** the
breakout level as of the 15:15 close, and the final candle is a strong push into
it. Taking the structural entry here means chasing a bar that has already moved.
There is no waiting-room left in this one.

### ⚠️ Marginal (1)

**SAPPHIRE** — the volume dry-up is the best on the list (0.18, a genuine
contraction) and the EMAs behave correctly. Two things hold it back. The base is
more **flat shelf than saucer** — price oscillated 228–240 for most of the window
and only rounded at the edges; R² 0.877 flatters it because a shallow shelf with
turned-up ends fits a parabola well. And it carries the **deepest base in the
batch at 6.62%**, which is why it ranks last: honoring this structure costs 6.6%
of risk. Real, but the least efficient of the six.

### ❌ Distrust despite passing every filter (3)

**JUBLFOOD — ranked #1, and I trust it least of the top three.** Its
`max_bar_share` is **exactly 0.50**, against a filter that rejects above 0.50.
OBEROIRLTY was thrown out today at 0.51. JUBLFOOD survived by one hundredth. Half
its qualifying rally is a single candle — precisely the gap-and-base-masquerading-
as-rally failure mode that filter exists to catch, and it is on the list only
because the comparison is `≤` rather than `<`. On the chart, that candle spikes to
~520 and closes well below, leaving **overhead supply at 520 sitting immediately
to the left of the base** with the lip at 512.60. The base itself is a shallow
drift, not a rounded one. The #1 rank is an artifact of it having the shallowest
base (3.31%), which is the *entire* RRR formula — shallow base, high RRR, and here
shallow means "barely a base" rather than "tight and constructive."

**PAYTM** — the base does not round, it **V's**. Price declines steadily from 1,655
to ~1,548 across the left half, then recovers briskly — two halves with different
slopes, which is the exact signature the skill warns fits a parabola *better* than
a real base. R² 0.605 is the second-lowest and still overstates it. Worse, **price
lost both EMAs inside the base** and only reclaimed them in the last few bars; the
requirement is that fast EMAs run *under* the base and lift it, not that price
falls through them and climbs back. There is heavy overhead supply at 1,650–1,660
from two prior rejections. Highest liquidity on the list (₹405cr) and the weakest
structure.

**BLS** — the lip is fiction. The 282.17 entry level is set by **one spike candle**
that printed the high and closed sharply lower, immediately followed by a red bar.
An entry level defined by a single rejected wick is not a level. Since then price
fell to 265.50 and has only recovered to 273 — it is **3.25% from the lip, by far
the furthest on the list**, so the "base near the high" reading is generous. Lowest
R² in the batch (0.599). What the panel actually shows is a blowoff spike and the
pullback after it, which is a different setup with different odds. Thinnest of the
six at ₹22cr/day.

---

## 5. Stop-inside-base check

**All 6 of 6 names have a 3% stop landing inside the base.** This is not a
coincidence or a bad day — it is structural. Qualifying bases run 3–8% deep, so a
fixed 3% stop sits mid-cup by construction and gets taken out by ordinary chop
*without the pattern having failed at all.*

| Symbol | Entry (lip) | 3% stop | Base low | Real risk | Verdict |
|---|---|---|---|---|---|
| JUBLFOOD | 512.60 | 497.22 | 495.65 | **3.31%** | Inside by ₹1.57 — nominally compatible, but the margin is noise. A 3% stop here is a coin flip against the base low. |
| NEULANDLAB | 23845.00 | 23129.65 | 23011.00 | **3.50%** | Inside by ₹119. Closest to workable on the list; needs 3.5%, not 3%. |
| PAYTM | 1626.50 | 1577.70 | 1546.30 | **4.93%** | **Incompatible.** A 3% stop sits ₹31 above the base low, mid-structure. |
| DEVYANI | 147.99 | 143.55 | 140.43 | **5.11%** | **Incompatible.** 3% stop lands squarely inside the base. |
| BLS | 282.17 | 273.70 | 265.50 | **5.91%** | **Incompatible.** Nearly half the base sits below a 3% stop. |
| SAPPHIRE | 245.29 | 237.93 | 229.05 | **6.62%** | **Incompatible — worst on the list.** The 3% stop is barely past the midpoint of the cup. |

**What this costs.** Honoring the structure on SAPPHIRE means accepting 6.62% risk,
not 3% — which **cuts position size by roughly 55%** versus a 3%-stop assumption,
and changes the reward/risk arithmetic of the whole trade. Sizing off 3% while the
structure demands 6.6% is not an aggressive version of the same trade; it is a
different and worse trade that will stop out on noise. The RRR column already
prices this in, which is why the deepest bases rank last.

---

## 6. Notes on thresholds — flagged, deliberately not changed

**No threshold was loosened, and nothing was re-run to manufacture hits.** This is
a single strict pass. Two things I would look at, and left alone:

1. **`max_bar_share` boundary.** `≤ 0.50` let JUBLFOOD through at exactly 0.50 while
   OBEROIRLTY died at 0.51. A rally that is half one candle is the thing the filter
   is for. Worth considering `< 0.45`. Not changing it mid-run.
2. **`rrr_structural` units.** Off by 100× as noted. Cosmetic — ranking is correct.

## 7. Regime

Bases near highs resolve upward far more often in a trending index than a choppy
one; the identical screener on the identical universe has a very different hit
rate in the two. **The presence of a pattern today is a different question from
whether it is worth trading today,** and only a backtest split by index trend
state answers the second. This run does not answer it.

---

*Generated by the `nse-pattern-screener` routine. Raw artifacts: `run_meta.json`,
`hits.json` (8 raw), `hits_clean.json` (6 clean), `hits.png` (chart grid).*
