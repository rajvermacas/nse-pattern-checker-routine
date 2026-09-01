# NSE hourly pattern screen — rally + rounded base near highs

| | |
|---|---|
| **Executed at** | **2026-09-01 17:08 IST** (`run_ts_ist`) |
| **Latest data bar** | **2026-09-01 15:15 IST** — the **2026-09-01** session (`session_age_days = 0`) |
| Data snapshot | 2026-09-01 17:15 IST |
| Interval | 1h (NSE hourly, 7 bars/session) |
| Market open at run | No — the 15:15 bar is the final closed candle of the session |
| **Chart — all 7 panels** | **https://claude.ai/code/artifact/6e3275fa-a14b-49ac-a988-c628248aa006** |

The latest closed bar is from today's session, so this report covers **1 Sep
2026** and nothing about it is stale. 95.0% of the symbols with data (2,126 of
2,237) are priced at that same 15:15 bar, and **every one of the 7 hits below
has `bars_behind_universe = 0`** — each is quoted at the 1 Sep 15:15 close, not
at an older bar.

> **These are candidates matching a geometry, not recommendations.** The
> detector finds a rally followed by a parabolic-fitting base near the highs.
> It knows nothing about earnings, news, sector, or whether the pattern
> resolves up. Charts are matplotlib renderings of yfinance data; EMA seeding
> and session handling differ from TradingView and Kite. Confirm every price
> on your own platform before acting.

---

## 1. Coverage

| | |
|---|---|
| Universe | `EQ` — the full NSE equity list (skill default, **not** a narrowed slice) |
| Symbols in universe | 2,302 |
| Symbols with usable data | **2,237 → 97.2% coverage** |
| Missing | 65 symbols |
| Coverage floor | 80% (`MIN_COVERAGE`) — cleared with margin |
| Fetch | 58/58 batches, 0 failed, 2 gap-fill rounds (round 1 recovered 93 symbols) |

97.2% is a normal figure for this pipeline, not a full-universe scan. The 65
missing names are mostly recent listings without 60 days of hourly history and
small-caps that do not map to `SYMBOL.NS` on Yahoo (ABMKNO, ADDIND, ALFREDHE,
ANSALBU, APOORVA, ARCL, ARYAMAN, ASSAMENT, ASTAR, AUGMONT, BENARAS, BRIGHTBR,
CRAVATEX, GAJA, GKB, GRAVISSHO, HBESD, HORIZONIND, HRYNSHP, INDPRUD, KANCOTEA,
KJMCFIN, LADDERUP, LAHOTIOV, LAKSHMIMIL, …). **If a name you care about is not
in this report, check it is not in the missing 2.8% before concluding it did
not match.**

Yahoo rate-limited this fetch repeatedly through the P–V range (roughly ten
batches hit `YFRateLimitError`). The fetcher re-primed its session and two
gap-fill rounds recovered the shortfall, so the 97.2% figure is a real recovered
number, not a rate-limited hole reported as success. Round 2 recovered 0 — the
remaining 65 are genuinely absent from Yahoo, not throttled.

## 2. Funnel — what each filter cut

| Stage | Count | What it removes |
|---|---|---|
| Symbols in universe | 2,302 | — |
| Symbols with hourly data | 2,237 | no Yahoo mapping / <60d history |
| **Raw geometric hits** | **26** | rally + parabola-fitting base near highs |
| → cut: `turnover_cr < 5.0` | −16 names | illiquid; a base you cannot exit |
| → cut: `pct_of_60d_high < 97.0` | −6 names | fell hard and bounced — the "rally" is a dead-cat, the "base" is a pause in a downtrend |
| → cut: `max_bar_share > 0.50` | −11 names | one gap candle *is* the rally — no accumulation, just a repricing |
| **Clean hits** | **7** | (reject reasons overlap; 19 distinct names cut) |

All 19 rejects with reasons: TTML, EPIGRAL, ARIHANTCAP, INDOCO, GUJALKALI,
LANCORHOL, CENTEXT, SHRADDHA, UMIYA-MRO, GFLLIMITED, MARATHON, IGPL, SPORTKING,
BEPL, ACMESOLAR, VTMLTD, MEDICAPQ, WELCORP, KAMATHOTEL.

**Liquidity did the heavy lifting today** — 16 of the 19 cuts, against 6 for
at-the-high and 11 for gap-share. That is the opposite of the 31 Aug run, where
`pct_of_60d_high` was the dominant filter. Today's raw crop skewed micro-cap:
MEDICAPQ at ₹0.0cr, UMIYA-MRO and SHRADDHA at ₹0.03cr, VTMLTD at ₹0.07cr. The
geometry was there; the ability to get filled was not.

**Two hits passed on a boundary, not a margin:**

- **WAKEFIT** — `pct_of_60d_high` 97.3% against a 97.0 floor.
- **KENNAMET** — `pct_of_60d_high` 97.2% against a 97.0 floor.

A boundary pass is not the same evidence as a margin pass. Both mean there is
overhead supply from a higher print earlier in the 60-day window that the
panel's left edge does not show. KENNAMET also lands in my distrust tier below,
independently, on the chart.

**This was a narrow day.** 26 raw hits and 7 clean, against 42 and 18 on 31 Aug
— the crop roughly halved in one session with no threshold touched. Worth
knowing when comparing the two reports side by side.

## 3. Ranked table

Ranked by `rrr_structural` — reward to the +15% target against risk to the base
low. **RRR ranks the geometry, not the odds.** It says what the trade pays if it
works, never how often it works. Do not read the top row as the best trade —
today the top row is the name I trust least.

| # | Symbol | Close | Entry | Base low | Rally % | Base (sess) | Depth % | R² | Turnover ₹cr | % of 60d high | Dist from lip % | RRR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | SBFC | 99.95 | 103.24 | 97.54 | 10.5 | 4.2 | 5.52 | 0.746 | 6.4 | 100.0 | 3.19 | 2.72 |
| 2 | DCBBANK | 224.25 | 225.47 | 211.19 | 21.7 | 3.2 | 6.33 | 0.894 | 17.6 | 100.0 | 0.54 | 2.37 |
| 3 | BALAMINES | 2409.70 | 2454.80 | 2295.80 | 18.9 | 3.5 | 6.48 | 0.655 | 17.7 | 99.8 | 1.84 | 2.31 |
| 4 | WELENT | 705.55 | 712.00 | 661.60 | 22.8 | 4.4 | 7.08 | 0.839 | 9.9 | 100.0 | 0.91 | 2.12 |
| 5 | WAKEFIT | 152.92 | 154.46 | 143.45 | 12.0 | 3.1 | 7.13 | 0.630 | 7.7 | 97.3 | 1.00 | 2.10 |
| 6 | KENNAMET | 4558.20 | 4721.10 | 4352.00 | 34.5 | 2.9 | 7.82 | 0.625 | 13.4 | 97.2 | 3.45 | 1.92 |
| 7 | PARAGMILK | 259.10 | 262.30 | 237.10 | 22.3 | 4.4 | 9.61 | 0.780 | 8.1 | 100.0 | 1.22 | 1.56 |

No `base_low` in this batch is set by a single wick — `base_low_is_wick` is
`False` for all 7, and the largest wick-to-close gap is 0.47% (BALAMINES). The
structural lows are real closes, not one stray print, so the RRR ordering is not
being distorted by an outlier bar.

### Three names carried over from 31 Aug — and all three got worse

DCBBANK, WELENT and PARAGMILK also appeared in yesterday's report. In every case
the base low is **unchanged** while price has advanced, so the lip moved up and
the structural risk widened:

| Symbol | Entry 31 Aug → 1 Sep | Base low | Depth 31 Aug → 1 Sep | Risk widened by |
|---|---|---|---|---|
| DCBBANK | 218.70 → 225.47 | 211.19 (same) | 3.43% → **6.33%** | +2.90 pt |
| WELENT | 697.50 → 712.00 | 662.00 → 661.60 | 5.09% → **7.08%** | +1.99 pt |
| PARAGMILK | 256.59 → 262.30 | 237.10 (same) | 7.60% → **9.61%** | +2.01 pt |

DCBBANK in particular was the cleanest and tightest name on yesterday's page at
3.43% risk. It has since broken out; the structure is still good, but the entry
is now 6.33% above the only stop the pattern supports. **Anyone acting on
yesterday's report today is taking roughly double the risk for the same
target.** The other 15 names from 31 Aug no longer qualify at all.

## 4. Visual pass — I looked at all 7 panels

**R² is not quality, and RRR is not conviction.** The top-ranked name (SBFC,
2.72) is the one I distrust most, and the two names I rate cleanest sit at ranks
2 and 4. The two weakest fits in the batch (KENNAMET 0.625, WAKEFIT 0.630) are
also the two boundary passes — the numbers and the pictures agree on those.

### Clean structural match (2)

- **DCBBANK** — the best structure on the page. A 44-bar staircase from ₹182 to
  ₹220 built out of several distinct legs with real pullbacks between them
  (`max_bar_share` 0.27 — no candle carried it), then a genuine rounded
  pullback to 211, a curl, and a reclaim to a new high on the final bar. The
  fast EMA dips *through* the base and turns up under price; the slow EMA rises
  underneath the whole time. ₹17.6cr/day is real liquidity. R² 0.894 is the
  highest in the batch and here the number agrees with the picture. The caveat
  is entry, not shape: `dist_from_lip_pct` 0.54 means there is essentially no
  pullback left to buy, and see the carry-over table above.
- **WELENT** — a long flat launch pad through 20 Aug, then a real five-session
  advance to 697 with the most evenly distributed rally in the batch
  (`max_bar_share` 0.25). The base rounds properly from 697 down to 662 and the
  last candles push to a new high. EMAs behave as they should. ₹9.9cr/day is
  adequate rather than deep for a ₹700 stock.

### Marginal (3)

- **BALAMINES** (rank 3) — the advance is real and multi-session, but it
  launches off one very large 22 Aug candle: `max_bar_share` 0.41 is the closest
  to the 0.50 gap-share cut of anything that passed. The base is a **wide,
  choppy 2,300–2,420 range** rather than a smooth round — R² 0.655 — and the
  2,454 lip is exactly where price was rejected on 27 Aug, so the entry sits
  directly under known supply.
- **WAKEFIT** (rank 5) — the rally is the honest part: a steady 42-bar staircase
  from 120 to 152 with a genuine intermediate pullback around 25–27 Aug. The
  base is the weak part — a fairly **V-shaped dip** to 143 and back rather than
  a round, R² 0.630, second-weakest fit here. Combined with the boundary pass on
  at-the-high (97.3% vs 97.0), there is supply above that these 60 days do not
  show.
- **PARAGMILK** (rank 7) — the base does round (252 → 237 → curl → back up) and
  R² 0.78 is respectable, which is an improvement on how this name read on 31
  Aug. The problem is the recovery leg and the size of the hole: the last push
  is **near-vertical, roughly 9% in a day and a half**, straight into the lip,
  on the **deepest base in the batch at 9.61%**. You would be buying an extended
  candle and accepting the widest structural stop on the page.

### Distrust despite passing every filter (2)

Both cleared turnover, at-the-high and gap-share. I do not believe the pattern.

- **SBFC** (rank 1 — top of the ranking, and the one I trust least). The "10.5%
  rally" is a single near-vertical repricing over **12 bars — 1.7 sessions** off
  a two-week flat shelf at 93. `max_bar_share` 0.36 keeps it under the
  gap-driven cut on a technicality; visually it is two or three candles doing
  all the work, which is a news repricing, not accumulation. What follows is not
  a base curling up but a **step down from 102 to a flat 98–100 shelf** over 4.2
  sessions, and at `dist_from_lip_pct` 3.19 it is the furthest from entry of
  anything here. The fast EMA has flattened and price is chopping across it
  rather than riding it. The parabola is fitting post-spike drift.
- **KENNAMET** (rank 6) — the 34.5% "rally" is two step-jumps (21 Aug and 28
  Aug) with flat shelves between, not a staircase. The second jump **spiked to
  ~4,870 on 28 Aug and was rejected the same session**; that print now sits as
  overhead supply directly above the 4,721 entry — the same failure mode GSPCROP
  showed on 31 Aug. The base is a choppy 4,400–4,650 range over just **2.9
  sessions**, R² 0.625 is the weakest fit in the batch, and it cleared
  at-the-high on a boundary (97.2% vs 97.0). Nothing about it holds up.

## 5. Stop-inside-base check — read this before sizing anything

**All 7 of 7 names have a conventional 3% stop sitting INSIDE the base.** A 3%
stop would be taken out by ordinary noise within the consolidation on every
single candidate — not by the pattern failing, just by it breathing.

`risk_pct_to_base_low` is the real structural risk. Where the two numbers are
incompatible, the honest options are to size for the structural stop or to skip
the name — not to use the tighter stop and call it risk management.

| Symbol | Entry | 3% stop | Structural stop (base low) | Structural risk | Compatible? |
|---|---|---|---|---|---|
| SBFC | 103.24 | 100.14 | 97.54 | **5.52%** | No — 1.8x the fixed stop |
| DCBBANK | 225.47 | 218.71 | 211.19 | **6.33%** | No — 2.1x |
| BALAMINES | 2454.80 | 2381.16 | 2295.80 | **6.48%** | No — 2.2x |
| WELENT | 712.00 | 690.64 | 661.60 | **7.08%** | No — 2.4x |
| WAKEFIT | 154.46 | 149.83 | 143.45 | **7.13%** | No — 2.4x |
| KENNAMET | 4721.10 | 4579.47 | 4352.00 | **7.82%** | No — 2.6x |
| PARAGMILK | 262.30 | 254.43 | 237.10 | **9.61%** | No — 3.2x, worst on the page |

There is no near-miss today. The shallowest base in the batch is 5.52% — nearly
double the fixed stop — so unlike 31 Aug (where DCBBANK's 3.43% came within
0.4pt) there is not a single name where a 3% stop is even arguably defensible.

Closing prices sit close enough to the closing-basis lows that this does not
change on a closing stop either: `risk_pct_to_base_low_close` runs only 0.2–0.9
pt tighter than the wick basis (SBFC 5.12%, DCBBANK 6.11%, BALAMINES 5.55%,
WELENT 6.71%, WAKEFIT 6.32%, KENNAMET 6.88%, PARAGMILK 9.40%). No name becomes
3%-compatible.

## 6. Notes and things I did not do

- **I did not touch a single threshold.** Turnover floor ₹5cr, at-the-high floor
  97% of the 60-day high, gap-share cap 0.50, curvature 0.015, R² 0.45 and the
  coverage floor 80% are all at their defaults. Nothing was loosened, and
  nothing was re-run to produce a longer list. 7 clean hits is what a strict
  screener returned today.
- **The tuning gap I flagged on 31 Aug is still open, and still cost something
  today.** There is no minimum base length. SBFC's *rally* is 12 bars (1.7
  sessions) of vertical repricing, and KENNAMET's *base* is 2.9 sessions of
  chop — the two names I distrust most. A minimum rally length (not just base
  length) would have caught SBFC specifically, since the detector currently
  treats a 12-bar spike and a 44-bar staircase as the same "rally". **I did not
  change it.** It is a recommendation for the next tuning pass, not something to
  apply mid-run.
- `max_bar_share` at 0.50 let SBFC through at 0.36 even though the move is
  visually two or three candles off a flat shelf. The metric measures the single
  largest bar; it has no notion of "the largest three bars". That is a second
  candidate for the tuning pass, and it is also left alone.
- Coverage, timestamps and per-hit staleness all agree today: `session_age_days`
  0, `pct_at_last_bar` 95.0, and `bars_behind_universe` 0 for every hit. No hit
  needed to be quoted at an older bar. The pipeline printed no staleness WARN.
- **Regime dependence, stated once:** bases near highs resolve upward far more
  often in a trending index than a choppy one. The same screener on the same
  universe has a very different hit rate in the two. The presence of a pattern
  today is a different question from whether it is worth trading today, and only
  a backtest split by index trend state answers the second. Nothing in this
  report addresses hit rate.
