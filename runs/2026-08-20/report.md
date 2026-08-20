# NSE hourly screen — rally + rounded base near highs
**2026-08-20** · run 16:34 IST

These are **candidates matching a geometry, not recommendations.** The screener
finds a shape; it says nothing about whether the shape resolves upward, and
nothing about whether today is a good day to act on it. Entry, sizing, and
whether to trade at all are your calls. Charts are matplotlib renderings of
yfinance data — EMA seeding and session handling differ from TradingView and
Kite, so confirm every price on your own platform before acting.

---

## 1. Coverage and data

| | |
|---|---|
| Universe | **nifty500** — 500 symbols |
| Symbols with usable data | **500 / 500 (100%)** |
| Interval | 1h, 60d lookback |
| Last closed bar | **2026-08-20 15:15 IST** |
| Market state at run | closed (16:34 IST) — 15:15 stub kept as a genuine close |

**This is not a full-universe scan.** `UNIVERSE` defaults to `nifty500`, which
is narrower than the skill's own default of the ~2,293-symbol EQ list. Roughly
1,800 tradable NSE equities were never looked at today. Anything outside the
Nifty 500 could not have appeared here.

Coverage was 100%, which is better than the ~92% the skill warns to expect.
Treat that as today's luck, not a standing property.

**Three names are one bar stale.** Yahoo had not published the 15:15 bar for
JUBLFOOD, PAYTM, or MOTILALOFS at fetch time, so their last bar is 14:15. Their
`close` and `dist_from_lip` are an hour old and each may have moved since. The
chart's title reflects this (it stamps 14:15, the earliest last-bar in the batch).

## 2. Funnel

```
500 symbols in nifty500
  │  detector: EMA stack, EMA rising, depth ≤10%, curvature ≥.015,
  │            R² ≥.45, |vertex| ≤.65, rally ≥10%, at-top, lip ≤4%, vol ≤.85
  ▼
    9 raw hits
  │  context filters: turnover ≥₹5cr/day, base_high ≥97% of 60d high,
  │                   max_bar_share ≤0.5
  ▼
    7 clean hits
  │  visual pass (below)
  ▼
    2 clean · 3 marginal · 2 distrusted
```

**What the context filters cut (2 names):**

- **ZEEL** — failed *both* checks: base high only **92.4%** of the 60-day high,
  and one bar carried **58%** of the rally. This is the exact false positive the
  filter was built for: a stock well below its real high whose bounce reads to a
  120-bar detector as "rally into a base near the high." It is a downtrend
  bounce into overhead supply, not a base. Liquidity was never the issue
  (₹143cr/day).
- **OBEROIRLTY** — 98.8% of its 60-day high and liquid (₹31cr/day), but
  **max_bar_share 0.51**, a hair over the 0.5 limit: one gap candle was half the
  rally. Gap-and-base is a different setup with different odds than
  rally-and-base. It failed by 0.01 and is worth a manual look rather than
  treating the cut as a verdict.

Note that **JUBLFOOD passed at exactly 0.50** — sitting precisely on the
boundary that rejected OBEROIRLTY. See its tier note.

## 3. Ranked table

Ranked by structural reward-to-risk = target 15% ÷ base depth. It reduces to
inverse base depth, because base depth *is* the risk — the base low is the only
stop the structure supports.

| # | Symbol | Entry (lip) | Close | % to lip | Base depth | Risk → base low | Vol ratio | R² | Vertex | Turnover | %60d high | Bar share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | JUBLFOOD | 512.60 | 507.30* | 1.03% | 3.31% | **3.31%** | 0.22 | 0.703 | +0.01 | ₹85cr | 98.5 | 0.50 |
| 2 | NEULANDLAB | 23,845.00 | 23,573.00 | 1.14% | 3.50% | **3.50%** | 0.41 | 0.736 | +0.08 | ₹82cr | 100.0 | 0.17 |
| 3 | PAYTM | 1,626.50 | 1,603.60* | 1.41% | 4.93% | **4.93%** | 0.56 | 0.605 | +0.01 | ₹405cr | 98.2 | 0.27 |
| 4 | DEVYANI | 147.99 | 147.80 | 0.13% | 5.11% | **5.11%** | 0.29 | 0.879 | −0.19 | ₹48cr | 100.0 | 0.32 |
| 5 | BLS | 282.17 | 273.00 | 3.25% | 5.91% | **5.91%** | 0.45 | 0.599 | +0.08 | ₹23cr | 100.0 | 0.25 |
| 6 | MOTILALOFS | 989.00 | 973.40* | 1.58% | 5.95% | **5.95%** | 0.77 | 0.754 | −0.48 | ₹48cr | 99.9 | 0.33 |
| 7 | SAPPHIRE | 245.29 | 241.35 | 1.61% | 6.62% | **6.62%** | 0.18 | 0.877 | −0.25 | ₹25cr | 100.0 | 0.42 |

`*` last bar 14:15, not 15:15 — price is an hour stale.

**RRR is not shown, because the pipeline's number is wrong.** `postfilter.py`
computes `rrr_structural = target_pct * 100 / base_depth_pct`, which assumes
`target_pct` arrives as a fraction (0.15), but `run_screener.sh` passes `15`.
Every `rrr_structural` in `hits_clean.json` is therefore **100× too large**
(JUBLFOOD shows 453.17; the real reward-to-risk is **4.53**). Ranking is
unaffected — the error is a constant multiplier — but the magnitude is
meaningless. The true values are 4.53 / 4.29 / 3.04 / 2.94 / 2.54 / 2.52 / 2.27
in table order. **I have not changed the code**; it is flagged here for a
deliberate fix.

**RRR ranks the geometry, not the odds.** It states what a trade pays if it
works and is silent on how often it does. JUBLFOOD ranks first only because its
base is shallowest — which is also why its stop is tightest and easiest to hit.
Do not read the ordering as a preference list.

## 4. Visual pass — what the charts actually show

I opened `hits.png` and read all seven panels. The numbers and my eyes disagree
on three of them; where they do, the eyes are the point of this step.

### Clean structural match (2)

**DEVYANI** — the best structure in the batch and the only one where every check
agrees. Sustained 17.3% rally over 43 bars with no single dominant candle
(0.32), then a genuinely *rounded* 29-bar saucer: price dishes down to 140.4 and
curves back up, rather than snapping. Fast EMAs run under the base the whole way
and rise through it. At 100% of its 60-day high with **zero** prior volume above
the lip — no overhead supply at all. Volume dries up to 0.29 through the base.
R² 0.879 here is measuring a real curve, not a V. Caveat: it is already *at* the
lip (0.13% away), so there is no waiting room left — it either goes or it fails
from here.

**NEULANDLAB** — at its 60-day high, tight 26-bar base, lowest bar-share in the
batch (0.17), EMAs rising underneath, no overhead supply, and a genuine 15:15
bar. The honest qualification: at 3.5% the base is more of a tight sideways
drift than a pronounced saucer, so "rounded base" is generous — it is a shallow
consolidation that happens to fit a parabola. It is clean, but it is clean
because nothing is wrong with it, not because the geometry is striking. Also
note the ₹23,573 price: position sizing is lumpy.

### Marginal (3)

**PAYTM** — the rounded pullback is real (1,650 → 1,546 → 1,604) and it is by
far the most liquid name here at ₹405cr/day. What holds it back is the one thing
no other name has: **actual overhead supply.** 9.4% of prior volume traded
*above* the lip, and there is a swing high at 1,656 sitting 1.8% over the entry.
Anyone trapped at 1,650 gets their exit right where this is supposed to break
out. Add the lowest R² of the group (0.605) and a stale 14:15 print. Real
pattern, worst location.

**SAPPHIRE** — numerically the most attractive: R² 0.877, the best volume dry-up
in the batch (0.18), 100% of 60-day high, biggest rally (21%). Two things pull
it down. First, **the lip is a single print** — only 1 of 27 base bars trades
within 0.5% of 245.29, so the "entry level" is one bar's high, not a
consolidation ceiling that the market has agreed on. Second, max_bar_share 0.42
means one candle carried 42% of the rally. And at 6.62% it has the deepest base,
so it demands the widest stop of any name here.

**JUBLFOOD** — ranks first on RRR purely because its 3.31% base is the
shallowest. But the rally into it is dominated by one vertical candle (477 → 520
in a single bar), and **max_bar_share is exactly 0.50 — it passed by sitting
precisely on the boundary that rejected OBEROIRLTY at 0.51.** That is not a
margin, it is a coin landing on its edge. The base itself reads as a shelf with
a shallow dip rather than a saucer. Volume dry-up (0.22) and a well-defined lip
(6 of 21 bars) are genuinely good. Stale 14:15 print. Treat the top ranking as
an artifact of shallow depth, not as quality.

### Distrust despite passing every filter (2)

**MOTILALOFS** — **this is the V-bounce the skill warns about, and it passed.**
Vertex at −0.48 is nearly at the ±0.65 limit, meaning the "base" turns almost
immediately and then runs — the shape is a checkmark, not a cup. The panel
confirms it: shortest base in the batch (19 bars), a drop to 930, then two
near-vertical candles from 935 to 989 into the right edge. Volume ratio 0.77 is
the highest here — there is **no dry-up at all**, which is the opposite of what
a genuine base does. R² 0.754 is high precisely *because* a sharp reversal fits
a parabola well. Curvature cannot tell rounded from sharp; this panel can. Also
stale at 14:15. I would not treat this as a base.

**BLS** — the entry level is not real. Only **1 of 30 base bars** trades within
0.5% of the 282.17 lip: that number comes from a single spike candle, and the
market has never accepted it as a ceiling. Everything downstream of it — entry,
the 3.25% distance-to-lip (worst in the batch), the stop — is anchored to one
bar's high. It also carries the lowest R² (0.599), and the panel shows the base
*descending* off the spike and flattening at 268–274 rather than rounding back
up. Lowest turnover of the batch at ₹23cr/day. The geometry passed; the
structure isn't there.

## 5. Stop-inside-base check

**All seven names flag `stop_inside_base = true`. A 3% stop is incompatible with
six of the seven, and marginal on the seventh.**

| Symbol | Entry | 3% stop | Base low | Real risk | Verdict |
|---|---|---|---|---|---|
| JUBLFOOD | 512.60 | 497.22 | 495.65 | 3.31% | 3% stop lands ₹1.57 above the base low — inside, but barely. The only near-miss. |
| NEULANDLAB | 23,845.00 | 23,129.65 | 23,011.00 | 3.50% | Stop sits ₹119 inside the base. Ordinary chop takes it out. |
| PAYTM | 1,626.50 | 1,577.70 | 1,546.30 | 4.93% | Stop lands mid-cup, ₹31 above the low. Incompatible. |
| DEVYANI | 147.99 | 143.55 | 140.43 | 5.11% | Stop lands mid-cup. Incompatible. |
| BLS | 282.17 | 273.70 | 265.50 | 5.91% | Stop lands mid-cup, and the entry itself is a single print. Doubly unusable. |
| MOTILALOFS | 989.00 | 959.33 | 930.15 | 5.95% | Stop lands mid-cup — and there is no real base under it anyway. |
| SAPPHIRE | 245.29 | 237.93 | 229.05 | 6.62% | Worst case: the 3% stop sits ₹8.88 above the base low, squarely mid-cup. |

The point, plainly: **on six of seven, a 3% stop gets taken out by ordinary
movement inside the base without the pattern having failed at all.** Honoring
the structure means risking to the base low — 3.3% to 6.6% depending on the
name. On SAPPHIRE that is 6.6% rather than 3%, which cuts position size by
roughly half versus the 3% assumption and changes the whole reward/risk
arithmetic. The `sl` field in `hits_clean.json` is a mechanical `entry × 0.97`
and should not be used as-is on any of these.

## 6. Regime

Bases near highs resolve upward far more often in a trending index than a choppy
one; the same screener over the same universe has a very different hit rate in
the two. That a pattern exists today is a separate question from whether it is
worth trading today, and only a backtest split by index trend state answers the
second. Nothing here measures that.

## 7. Run notes

**No threshold was loosened, and nothing was re-run to manufacture hits.** The
detector and filter parameters are exactly the committed defaults. Two issues
were found and are reported rather than silently patched:

1. `rrr_structural` is 100× inflated (units mismatch between `run_screener.sh`'s
   `TARGET_PCT=15` and `postfilter.py`'s fractional expectation). Ranking is
   unaffected.
2. `max_bar_share` at exactly 0.50 admits JUBLFOOD while 0.51 rejects
   OBEROIRLTY. That boundary is doing more work than a hard cutoff should. Worth
   deciding deliberately; left alone here.

**One fix was required to make the run possible at all.** The first invocation
exited **40 (`FAIL: merge`)** with 0 of 13 fetch batches written — every ticker
failed with `curl: (35) Recv failure`. Cause: yfinance defaults to `curl_cffi`,
which impersonates a browser TLS fingerprint that this environment's inspecting
egress proxy resets. `fetch_data.py` now passes yfinance a plain `requests`
session primed with Yahoo cookies (a cold session gets HTTP 429). This is a
transport fix in the fetch layer; it touches no threshold, no detector
parameter, and no filter. The rerun fetched 500/500 symbols with zero ticker
failures.
