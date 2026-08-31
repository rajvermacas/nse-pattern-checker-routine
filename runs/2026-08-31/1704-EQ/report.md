# NSE hourly pattern screen — rally + rounded base near highs

| | |
|---|---|
| **Executed at** | **2026-08-31 17:04 IST** (`run_ts_ist`) |
| **Latest data bar** | **2026-08-31 15:15 IST** — the **2026-08-31** session (`session_age_days = 0`) |
| Data snapshot | 2026-08-31 17:10 IST |
| Interval | 1h (NSE hourly, 7 bars/session) |
| Market open at run | No — the 15:15 bar is the final closed candle of the session |
| **Chart — all 18 panels** | **https://claude.ai/code/artifact/ccc4e545-4193-4d9c-b63e-4e8abad428c3** |

The latest closed bar is from today's session, so this report covers **31 Aug
2026** and nothing about it is stale. 97.3% of the universe (2,165 of 2,226
symbols with data) is priced at that same 15:15 bar, and **every one of the 18
hits below has `bars_behind_universe = 0`** — each is quoted at the 31 Aug
15:15 close, not at an older bar.

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
| Symbols in universe | 2,301 |
| Symbols with usable data | **2,226 → 96.7% coverage** |
| Missing | 75 symbols |
| Coverage floor | 80% (`MIN_COVERAGE`) — cleared with margin |
| Fetch | 58/58 batches, 0 failed, 2 gap-fill rounds |

96.7% is a normal figure for this pipeline, not a full-universe scan. The 75
missing names are mostly recent listings without 60 days of hourly history and
small-caps that do not map to `SYMBOL.NS` on Yahoo (ABMKNO, ADDIND, ALFREDHE,
AMARJOTHI, ANSALBU, APOORVA, ARCL, ARYAMAN, ASSAMENT, ASTAR, AUGMONT, AUSTENG,
BENARAS, BNAGROCHEM, BRIGHTBR, CRAVATEX, GAJA, GKB, GRAVISSHO, HBESD, HBPOR,
HORIZONIND, HRYNSHP, INDPRUD, ISTLTD, …). **If a name you care about is not in
this report, check it is not in the missing 3.3% before concluding it did not
match.**

## 2. Funnel — what each filter cut

| Stage | Count | What it removes |
|---|---|---|
| Symbols in universe | 2,301 | — |
| Symbols with hourly data | 2,226 | no Yahoo mapping / <60d history |
| **Raw geometric hits** | **42** | rally + parabola-fitting base near highs |
| → cut: `turnover_cr < 5.0` | −18 names | illiquid; a base you cannot exit |
| → cut: `pct_of_60d_high < 97.0` | −13 names | fell hard and bounced — the "rally" is a dead-cat, the "base" is a pause in a downtrend |
| → cut: `max_bar_share > 0.50` | −10 names | one gap candle *is* the rally — no accumulation, just a repricing |
| **Clean hits** | **18** | (reject reasons overlap; 24 distinct names cut) |

All 24 rejects with reasons: SPORTKING, GVT&D, GARFIBRES, RADIANTCMS, HNDFDS,
LAMBODHARA, AJOONI, LUMAXIND, GLOBECIVIL, NITINSPIN, RBZJEWEL, STAR, CONFIPET,
PROZONER, GUJTHEM, MANORG, QUESS, YUKEN, BANG, ABCOTS, ATLANTAELE, TARMAT,
SHREEPUSHK, RANASUG.

**Two hits passed on a boundary, not a margin:**

- **GSPCROP** — `max_bar_share` 0.49 against a 0.50 cut. One more tick of gap
  concentration and it would have been rejected as gap-driven.
- **INDOBORAX** — turnover ₹5.5cr against a ₹5.0cr floor. Thin.

A boundary pass is not the same evidence as a margin pass. Both names also land
in my distrust tier below, independently, on the chart.

## 3. Ranked table

Ranked by `rrr_structural` — reward to the +15% target against risk to the base
low. **RRR ranks the geometry, not the odds.** It says what the trade pays if it
works, never how often it works. Do not read the top row as the best trade.

| # | Symbol | Close | Entry | Base low | Rally % | Base (sess) | Depth % | R² | Turnover ₹cr | % of 60d high | RRR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | DCBBANK | 218.00 | 218.70 | 211.19 | 21.7 | 2.2 | 3.43 | 0.679 | 17.8 | 99.4 | 4.37 |
| 2 | GODREJAGRO | 615.30 | 628.80 | 604.25 | 11.5 | 3.5 | 3.90 | 0.714 | 7.2 | 99.1 | 3.85 |
| 3 | MCX | 3400.00 | 3400.00 | 3245.00 | 13.4 | 3.6 | 4.56 | 0.610 | 565.9 | 100.0 | 3.29 |
| 4 | YATHARTH | 1004.85 | 1010.55 | 960.30 | 20.9 | 1.7 | 4.97 | 0.705 | 20.3 | 98.6 | 3.02 |
| 5 | WELENT | 688.80 | 697.50 | 662.00 | 22.8 | 3.3 | 5.09 | 0.785 | 11.3 | 100.0 | 2.95 |
| 6 | GSPCROP | 639.50 | 655.95 | 622.00 | 13.2 | 3.3 | 5.18 | 0.570 | 9.0 | 98.4 | 2.90 |
| 7 | ENTERO | 1809.90 | 1840.60 | 1744.70 | 30.9 | 1.7 | 5.21 | 0.509 | 18.1 | 100.0 | 2.88 |
| 8 | KTKBANK | 336.00 | 342.50 | 324.50 | 10.7 | 3.5 | 5.26 | 0.798 | 55.7 | 100.0 | 2.85 |
| 9 | KABRAEXTRU | 600.30 | 612.50 | 579.30 | 24.8 | 3.6 | 5.42 | 0.569 | 8.8 | 98.0 | 2.77 |
| 10 | TBZ | 305.70 | 311.25 | 292.85 | 26.1 | 2.0 | 5.91 | 0.679 | 17.9 | 99.6 | 2.54 |
| 11 | SOLARA | 635.00 | 640.90 | 601.55 | 29.1 | 4.4 | 6.14 | 0.698 | 6.5 | 98.0 | 2.44 |
| 12 | MSTCLTD | 751.10 | 762.10 | 709.55 | 15.8 | 3.9 | 6.90 | 0.789 | 14.9 | 100.0 | 2.17 |
| 13 | INDOBORAX | 508.45 | 524.50 | 487.05 | 25.3 | 3.9 | 7.14 | 0.607 | 5.5 | 100.0 | 2.10 |
| 14 | PARAGMILK | 256.50 | 256.59 | 237.10 | 22.3 | 3.6 | 7.60 | 0.743 | 8.4 | 100.0 | 1.97 |
| 15 | TVSSRICHAK | 5519.60 | 5585.00 | 5155.30 | 14.9 | 3.2 | 7.69 | 0.820 | 8.4 | 100.0 | 1.95 |
| 16 | FCL | 50.91 | 52.20 | 47.88 | 20.3 | 3.3 | 8.28 | 0.692 | 31.9 | 100.0 | 1.81 |
| 17 | SUVEN | 392.05 | 394.95 | 361.50 | 20.0 | 3.5 | 8.47 | 0.851 | 12.4 | 100.0 | 1.77 |
| 18 | AVADHSUGAR | 852.10 | 871.85 | 790.05 | 24.4 | 4.1 | 9.38 | 0.788 | 9.8 | 98.6 | 1.60 |

No `base_low` in this batch is set by a single wick — `base_low_is_wick` is
`False` for all 18, and the largest wick-to-close gap is 0.82% (SOLARA). The
structural lows are real closes, not one stray print.

## 4. Visual pass — I looked at all 18 panels

**R² is not quality.** A V-shaped bounce fits a parabola better than a real
rounded base does, which is why the two weakest structures here (ENTERO 0.509,
GSPCROP 0.570) sit at ranks 7 and 6, while the highest R² in the batch (SUVEN
0.851) has an entry problem the number cannot see.

### Clean structural match (5)

- **KTKBANK** — the best structure on the page. A 45-bar orderly staircase from
  ₹300 to ₹342, then a genuine rounded pullback: down to 324.5, a flat curl,
  and the last candles reclaiming 336–341. The fast EMA dips *through* the base
  and turns up under price; the slow EMA rises underneath the whole time.
  ₹55.7cr/day is real liquidity. `max_bar_share` 0.33 — no single candle carried
  it.
- **MSTCLTD** — a stepwise advance ₹578 → ₹750 with a genuine intermediate
  consolidation around 690–700 (a base that already worked once), then an
  orderly 3.9-session rounded pullback to 709 and a clean reclaim of the high.
  Textbook shape.
- **DCBBANK** — sustained six-session rally 183 → 220 with no dominant candle
  (`max_bar_share` 0.27), then the tightest base in the batch: a 3.43% dip that
  rounds and pushes back to the lip on the final bar. EMAs rising through it.
- **MCX** — the cleanest *advance* here: a two-week orderly grind 2,900 → 3,400
  with the most evenly distributed rally in the batch (`max_bar_share` 0.16) and
  ₹566cr/day of turnover, an order of magnitude beyond anything else. Caveat
  that has nothing to do with the shape: `dist_from_lip_pct` is **0.00** — the
  close *is* the entry. There is no pullback left to buy.
- **WELENT** — a long flat launch pad through 20 Aug, then a real multi-session
  advance. There *is* one large thrust candle on 22 Aug, but price kept
  advancing for three sessions after it (`max_bar_share` 0.25), so it is not a
  gap-and-drift. The base rounds and the final candle reclaims the 697 lip.

### Marginal (9)

- **FCL** — the pullback genuinely rounds and ₹31.9cr/day is the second-best
  liquidity here, but the base is 8.28% deep. You are asked to risk 8% on a ₹51
  stock.
- **TBZ** — the rally is real and sustained (250 → 311 across six sessions with
  intermediate pullbacks), but the base is only **2.0 sessions** and is a V-dip
  to 293 and back, not a rounded base. The geometry passed on a rally the
  detector correctly liked and a base it should have called immature.
- **SUVEN** — highest R² in the batch (0.851) and the base does round properly
  from 358 to 372 over 3.5 sessions. Then the final bars fire vertically ~7% to
  394, straight into the lip. Good shape, bad moment: you would be buying an
  extended breakout candle with the structural stop 8.47% below.
- **GODREJAGRO** — the advance leg is one near-vertical two-session thrust
  (575 → 632 on 25–26 Aug), not a sustained rally. The base steps *down* to a
  605–618 shelf rather than rounding, and there is overhead supply at 600 from
  the 18 Aug peak sitting just underneath.
- **KABRAEXTRU** — a two-day vertical thrust 508 → 625, then a wide, choppy
  30-point range that only loosely rounds. R² 0.569. Price at 600 is still below
  the 612.5 lip.
- **SOLARA** — the advance is dominated by one enormous 20 Aug candle; the rest
  is follow-through. The base drifts sideways-down more than it rounds, price is
  below the lip, and ₹6.5cr/day is thin.
- **TVSSRICHAK** — the staircase from 3,950 to 5,300 is genuinely good. But the
  final bars are a vertical thrust to a new high, so the entry at 5,585 sits
  7.69% above the base low — you are chasing. ₹8.4cr/day is thin for a ₹5,500
  stock.
- **PARAGMILK** — `dist_from_lip_pct` 0.04: it is breaking out *on the last
  bar*. The "base" is a descending drift from 256 to 237 followed by a vertical
  snap-back, which is a shakeout-and-recover, not a rounded base. 7.6% deep.
- **AVADHSUGAR** — a long **flat shelf** at 800–830, not a round, and the
  deepest base in the batch at 9.38%. Worst risk profile on the page.

### Distrust despite passing every filter (4)

These four cleared turnover, at-the-high and gap-share. I do not believe the
pattern.

- **YATHARTH** (rank 4) — the "20.9% rally" is a single near-vertical
  two-session spike off ten flat days at ₹850, and the "base" is **12 bars —
  1.7 sessions** at the very top of it. That is a pause inside a parabolic move,
  not accumulation. The parabola fit (R² 0.705) is describing the spike.
- **ENTERO** (rank 7) — the same failure, worse. +30.9% vertical in roughly two
  sessions, base of **12 bars / 1.7 sessions**, and **R² 0.509 — the weakest fit
  in the batch**. The detector is fitting a curve to the top of a rocket.
- **GSPCROP** (rank 6) — spiked to 667 on a long upper wick on 24–25 Aug, was
  rejected immediately back to 630, and has gone sideways on a flat shelf for
  3.3 sessions underneath it. R² 0.570. That wick is overhead supply directly
  above the entry. It also passed `max_bar_share` at 0.49 against a 0.50 cut.
- **INDOBORAX** (rank 13) — +22% vertical thrust in two sessions, then a wide
  choppy 488–518 range that does not round at all. R² 0.607, and it passed
  liquidity at ₹5.5cr against the ₹5.0cr floor. Two boundary passes and a
  structure I would not trade.

## 5. Stop-inside-base check — read this before sizing anything

**All 18 of 18 names have a conventional 3% stop sitting INSIDE the base.** A 3%
stop would be taken out by ordinary noise within the consolidation on every
single candidate — not by the pattern failing, just by it breathing.

`risk_pct_to_base_low` is the real structural risk. Where the two numbers are
incompatible, the honest options are to size for the structural stop or to skip
the name — not to use the tighter stop and call it risk management.

| Symbol | 3% stop | Structural risk to base low | Compatible? |
|---|---|---|---|
| DCBBANK | 3.00% | **3.43%** | Closest in the batch — still inside, but only by 0.4pt |
| GODREJAGRO | 3.00% | **3.90%** | No — 3% stop sits inside the base |
| MCX | 3.00% | **4.56%** | No |
| YATHARTH | 3.00% | **4.97%** | No |
| WELENT | 3.00% | **5.09%** | No |
| GSPCROP | 3.00% | **5.18%** | No |
| ENTERO | 3.00% | **5.21%** | No |
| KTKBANK | 3.00% | **5.26%** | No |
| KABRAEXTRU | 3.00% | **5.42%** | No |
| TBZ | 3.00% | **5.91%** | No |
| SOLARA | 3.00% | **6.14%** | No — 2x the fixed stop |
| MSTCLTD | 3.00% | **6.90%** | No — 2.3x |
| INDOBORAX | 3.00% | **7.14%** | No — 2.4x |
| PARAGMILK | 3.00% | **7.60%** | No — 2.5x |
| TVSSRICHAK | 3.00% | **7.69%** | No — 2.6x |
| FCL | 3.00% | **8.28%** | No — 2.8x |
| SUVEN | 3.00% | **8.47%** | No — 2.8x |
| AVADHSUGAR | 3.00% | **9.38%** | No — 3.1x, worst on the page |

Closing prices are close enough to the closing-basis lows that this does not
change: `risk_pct_to_base_low_close` runs only 0.1–1.0pt tighter than the wick
basis, so no name becomes 3%-compatible on a closing stop either.

## 6. Notes and things I did not do

- **I did not touch a single threshold.** Turnover floor ₹5cr, at-the-high floor
  97% of the 60-day high, gap-share cap 0.50 and the coverage floor 80% are all
  at their defaults. Nothing was loosened, and nothing was re-run to produce a
  better-looking list.
- **One threshold I think is worth discussing — and left alone:** there is no
  minimum base length. ENTERO and YATHARTH both passed with 12-bar (1.7-session)
  bases that are pauses inside vertical moves, and TBZ with 2.0 sessions. A
  floor of roughly 2.5–3 sessions would have removed the two names I distrust
  most without touching anything I rated clean. **I did not change it.** It is a
  recommendation for the next tuning pass, not something to apply mid-run.
- The `pct_of_60d_high ≥ 97` filter did the most useful work of the three,
  cutting 13 dead-cat bounces (GVT&D at 78.7% of its 60-day high is the clearest
  example of what it is for).
- Coverage, timestamps and per-hit staleness all agree today: `session_age_days`
  0, `pct_at_last_bar` 97.3, and `bars_behind_universe` 0 for every hit. No hit
  needed to be quoted at an older bar.
