# NSE Hourly Pattern Screen — rally → rounded/flat base near highs

**Executed at:** 2026-08-21 01:24 IST (`run_ts_ist`; data snapshot taken at 01:25 IST after the fetch)
**Latest data bar:** 2026-08-20 15:15 IST — the **2026-08-20** session
**Session age:** `session_age_days = 1` — the latest available session is one
day before the run date (this run fired after IST midnight). **This is a scan
of the 2026-08-20 session, not of today.** Levels below are Aug 20 closes.

> **These are candidates matching a geometry, not recommendations.** Every name
> here passed a mechanical rally→base fit plus liquidity/at-high/rally-quality
> filters. Passing the geometry says nothing about the odds of the trade
> working. Nothing here is a buy list. Charts are matplotlib renderings of
> yfinance data — EMA seeding and session handling differ from TradingView/Kite;
> confirm every price on your own platform before acting.

**Chart (all 16 panels):** https://claude.ai/code/artifact/83c6208c-dbf7-48ad-ad6c-d6f5315900eb

---

## Coverage

| | |
|---|---|
| Universe | **EQ** (full NSE equity series, the skill default — ~2,293 symbols) |
| Symbols with usable data | **2,102 / 2,293 = 91.7%** |
| Missing | 191 symbols — recent listings lacking 60d of hourly history + Yahoo rate-limited/unmapped names |
| Interval | 1h, 60-day window (~7 bars/session) |
| Last closed bar | **2026-08-20 15:15 IST** |
| Symbols carrying that bar | 1,984 / 2,102 = **94.4%** of the fetched set (= 86.5% of the full universe) |

Coverage is at the normal ~92% level; this is **not** a full-universe scan — 191
names are absent. Two hits below are priced one bar behind the universe (see
the *Data* column) and are quoted at their own last bar, not at 15:15.

## Funnel — what each stage cut

| Stage | Count | Cut by |
|---|---|---|
| Universe (EQ) | 2,293 | — |
| Fetched with usable data | 2,102 | 191 no/short history (91.7% coverage) |
| Raw detector hits | 38 | rally→parabolic-base fit on the 120-bar window |
| **After context filters** | **16** | 22 cut |

The 22 rejected at the context stage, by reason (a name can trip more than one;
32 flag-hits across 22 names):

- **Illiquid** (`turnover < ₹5 cr/day`) — **16 names**, the single biggest cut.
  Examples: AVTNPL 0.2cr, MATRIMONY 0.7cr, TNPETRO 1.4cr. Thin names dominate
  the raw geometry hits.
- **Gap-driven** (`max_bar_share > 0.5`, i.e. one bar > 50% of the whole rally)
  — **13 names**. Examples: WSTCSTPAPR (1.36), ANDHRSUGAR (0.91), LUMAXTECH
  (0.72), OBEROIRLTY (0.51). The "rally" was a single candle, not a sustained
  advance.
- **Not-at-high** (`base_high < 97% of 60d high`) — **3 names**: ZEEL (92.4%,
  liquid but too far below its high), AXISCADES (80.4%), DHRUV (83.4%).

**Rounding-artifact pass — JUBLFOOD.** Its raw `max_bar_share` is **0.502**,
above the 0.5 cut, but `postfilter.py` rounds to two decimals *before*
comparing, so 0.50 > 0.50 is false and it passes. The three nearest rejects
sit at 0.508 (OBEROIRLTY), 0.511 (AXISCADES), 0.516 (DCI) — JUBLFOOD is on the
same side of the true threshold as all of them. Treat its rally-quality as
mechanically-passed-but-borderline, not clean.

## Ranked candidates (by structural RRR = 15% target off the lip ÷ risk to base low)

RRR ranks the *geometry's* payoff if it works; it is silent on how often it
works. Do not read the ordering as a probability ranking or a buy list.

| # | Symbol | RRR | R² | Base (bars / depth) | Dist to lip | Rally | Turnover ₹cr | Data | Tier |
|--:|--------|----:|----:|---|---:|---:|---:|---|---|
| 1 | JUBLFOOD | 4.53 | 0.70 | 21 / 3.3% | 1.0% | 10.0% | 85.3 | **14:15 (−1 bar)** | Marginal |
| 2 | NEULANDLAB | 4.29 | 0.74 | 26 / 3.5% | 1.1% | 10.2% | 83.3 | 15:15 | **Clean** |
| 3 | TI | 3.85 | 0.64 | 21 / 3.9% | 1.3% | 20.3% | 40.7 | 15:15 | Marginal |
| 4 | PAYTM | 3.04 | 0.61 | 30 / 4.9% | 1.4% | 15.9% | 405.4 | **14:15 (−1 bar)** | Marginal |
| 5 | DEVYANI | 2.94 | 0.88 | 29 / 5.1% | 0.1% | 17.3% | 48.2 | 15:15 | **Clean** |
| 6 | QPOWER | 2.72 | 0.47 | 16 / 5.5% | 1.8% | 15.0% | 8.0 | 15:15 | Distrust |
| 7 | BLS | 2.54 | 0.60 | 30 / 5.9% | 3.2% | 10.4% | 22.7 | 15:15 | Marginal |
| 8 | KSHINTL | 2.50 | 0.66 | 29 / 6.0% | 3.2% | 18.3% | 13.6 | 15:15 | Marginal |
| 9 | LASERPOWER | 2.35 | 0.47 | 14 / 6.4% | 4.0% | 19.8% | 41.9 | 15:15 | Distrust |
| 10 | ASIANENE | 2.33 | 0.54 | 12 / 6.5% | 1.2% | 28.5% | 11.0 | 15:15 | Distrust |
| 11 | SAPPHIRE | 2.27 | 0.88 | 27 / 6.6% | 1.6% | 21.0% | 24.6 | 15:15 | **Clean** |
| 12 | COMSYN | 2.22 | 0.69 | 30 / 6.8% | 2.5% | 39.4% | 6.2 | 15:15 | Marginal |
| 13 | ROLEXRINGS | 2.03 | 0.93 | 20 / 7.4% | 0.6% | 18.1% | 19.1 | 15:15 | **Clean** |
| 14 | INDSWFTLAB | 1.95 | 0.61 | 14 / 7.7% | 3.9% | 46.5% | 10.5 | 15:15 | Distrust |
| 15 | RBA | 1.91 | 0.72 | 15 / 7.8% | 2.5% | 20.3% | 57.9 | 15:15 | Marginal |
| 16 | RATNAVEER | 1.88 | 0.87 | 19 / 8.0% | 0.6% | 24.4% | 63.5 | 15:15 | Marginal |

Tier tally: **Clean 4, Marginal 8, Distrust 4** (=16). Sections below match the
Tier column exactly.

## Visual pass — I looked at all 16 panels

The highest-R² name in a batch is often the worst candidate, because a V-shaped
bounce fits a parabola better than a real rounded base does. Tiers below are my
read of the *shape*, not the fit number.

### Clean structural match (4)
- **DEVYANI** (R²0.88, 48cr) — genuine rounded advance, base coils right under
  the lip (0.1% away), fast EMA rising through the base, breaking to a new high
  on the last bars. The cleanest of the batch.
- **SAPPHIRE** (R²0.88, 25cr) — rounded/flat base near highs after a steady
  climb; EMAs stacked and rising under it; volume dry-up in the base
  (vol_ratio 0.18). Textbook shape.
- **ROLEXRINGS** (R²0.93, 19cr) — smooth rounded climb into a tight base at
  highs. Highest fit in the batch and, unusually, the shape backs it up. Base
  depth 7.4% is on the deeper side (see stops).
- **NEULANDLAB** (R²0.74, 83cr) — steady uptrend, tight 3.5% base pressed
  against the highs, very liquid. Shallow, near the lip, sustained.

### Marginal (8) — structure acceptable, one real caveat each
- **JUBLFOOD** (85cr, most liquid name here) — shallow flat base right under
  the lip. Structurally the base itself is fine, but its rally trips the
  gap-quality metric at the true value (0.502) and passes only because of
  rounding to 0.50, and it is priced one bar stale. Best-of-marginals, not clean.
- **TI** (R²0.64) — clean enough rounded base near highs; modest fit, nothing
  wrong, just not distinctive.
- **PAYTM** (405cr) — rounded rollover after a near-vertical gap run; the base
  itself rounds and is very liquid, but the advance into it was a gap, and it
  is priced one bar stale (14:15). Treat the level as approximate.
- **BLS** (R²0.60) — rounded base but 3.2% below the lip — more overhead to
  clear than the leaders.
- **KSHINTL** (R²0.66) — a huge single-bar spike sits inside the rally
  (max_bar_share 0.35) and base volume is very thin (vol_ratio 0.16). Structure
  near highs is okay; provenance of the move is not clean.
- **COMSYN** (39.4% rally) — long *flat* base near highs (constructive), but
  the rally is essentially one gap (max_bar_share 0.43) and the name is thin
  (6.2cr, just over the ₹5cr floor). Flat-base bulls only.
- **RBA** (58cr) — steady advance, base near highs, but 7.8% deep — a wide-stop
  name.
- **RATNAVEER** (R²0.87, 64cr) — reads more like a stock still *advancing* into
  the shaded window than one basing; the "base" is where it is making new
  highs. Deepest base in the batch (8.0%).

### Distrust despite passing every filter (4)
- **ASIANENE** — the textbook false positive the screen is built to catch: a
  flat shelf, a sharp V-dip, then a near-vertical launch to new highs. The
  parabola fits the V, not a base. 12-bar "base" at the very top of a vertical
  move. Avoid.
- **INDSWFTLAB** — 46.5% parabolic rally, 14-bar pause at the top. Extended,
  not based; high mean-reversion risk. Avoid.
- **LASERPOWER** (R²0.47) — long choppy shelf, dip, then a V-recovery into the
  highs. Poor fit, furthest from the lip (4.0%). This is a recovery, not a
  rounded base.
- **QPOWER** (R²0.47, 8cr) — spiky, illiquid-adjacent left side, erratic path
  into the base; lowest fit in the batch. Distrust the whole shape.

## Stop-inside-base check — a 3% stop is incompatible with almost every name

For all 16, `stop_inside_base = True`: a fixed 3% stop lands **inside** the
base's own range, where it will be shaken out by normal base noise. Honoring
the structure means stopping below the base low, which is
`risk_pct_to_base_low`:

| Symbol | Risk to base low | 3% stop | Real risk vs 3% | Verdict |
|--------|--:|--:|--:|---|
| JUBLFOOD | 3.3% | 3.0% | 1.1× | Almost compatible; still slightly tight |
| NEULANDLAB | 3.5% | 3.0% | 1.2× | 3% sits inside the base |
| TI | 3.9% | 3.0% | 1.3× | 3% sits inside the base |
| PAYTM | 4.9% | 3.0% | 1.6× | 3% ≈ 0.6× the real risk |
| DEVYANI | 5.1% | 3.0% | 1.7× | 3% ≈ 0.6× the real risk |
| QPOWER | 5.5% | 3.0% | 1.8× | 3% ≈ 0.55× the real risk |
| BLS | 5.9% | 3.0% | 2.0× | 3% ≈ 0.5× the real risk |
| KSHINTL | 6.0% | 3.0% | 2.0× | 3% ≈ 0.5× the real risk |
| LASERPOWER | 6.4% | 3.0% | 2.1× | 3% ≈ 0.47× the real risk |
| ASIANENE | 6.5% | 3.0% | 2.2× | 3% ≈ 0.46× the real risk |
| SAPPHIRE | 6.6% | 3.0% | 2.2× | 3% ≈ 0.45× the real risk |
| COMSYN | 6.8% | 3.0% | 2.3× | 3% ≈ 0.44× the real risk |
| ROLEXRINGS | 7.4% | 3.0% | 2.5× | 3% ≈ 0.4× the real risk |
| INDSWFTLAB | 7.7% | 3.0% | 2.6× | 3% ≈ 0.4× the real risk |
| RBA | 7.8% | 3.0% | 2.6× | 3% ≈ 0.4× the real risk |
| RATNAVEER | 8.0% | 3.0% | 2.7× | 3% ≈ 0.4× the real risk |

**Read this plainly:** on 15 of 16 a 3% stop does not honor the pattern —
JUBLFOOD (3.3%) is the only near-compatible name. Everywhere else, a 3% stop is
whipsaw bait inside the base; the structural stop is 3.5–8.0% away, roughly
1.2×–2.7× the fixed 3%. Sizing at 3%-equivalent risk therefore needs to shrink
by that factor to hold the same rupee risk. The RRR column already uses the
structural (base-low) risk, so the ranking is honest about this — but do not
size these as if 3% were the risk. The deeper-base names (ROLEXRINGS, RBA,
RATNAVEER at 7.4–8.0%) are the most affected.

## Bottom line

- 4 names read as clean rounded/flat bases near highs: **DEVYANI, SAPPHIRE,
  ROLEXRINGS, NEULANDLAB**.
- JUBLFOOD leads the marginals — shallow base right under the lip, but the
  rally passes the gap-quality filter only because 0.502 rounds to 0.50, and
  it's priced one bar stale. Structurally close to clean, mechanically borderline.
- 4 names — **ASIANENE, INDSWFTLAB, LASERPOWER, QPOWER** — passed every
  mechanical filter but are V-bounces / parabolic extensions / spiky
  illiquid-adjacent messes the numbers can't distinguish from real bases. This
  disagreement with the numbers is the point of the visual pass.
- Every name needs a wider-than-3% stop to respect its base (JUBLFOOD barely,
  the rest materially).
- This is the **2026-08-20** session, screened after midnight IST — not today's.
