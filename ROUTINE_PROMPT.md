Run the daily NSE hourly pattern screen.

The run produces TWO independent shortlists from the same bars:

- **rally_cup** — a rally into a rounded base near the highs. You buy the
  breakout above the lip of a base that has already formed.
- **momentum_dip** — a shallow, orderly pullback inside an ongoing advance.
  You buy inside a move that has NOT finished, with a stop 1-3% away.

They are different trades. Report them as two sections with two tables, and
never merge them or compare their RRR numbers (see step 5).

1. Execute `bash run_screener.sh` from the repository root. It may take 5–30
   minutes depending on `UNIVERSE`. If a single invocation times out, run it
   again — the data fetch is resumable and skips batches already on disk.

2. Handle the exit code before anything else:
   - **30** — fetch coverage below the floor. Report the coverage number and
     that the scan is not trustworthy today. Do not publish a shortlist.
   - **40** — a stage failed. `fetch_universe.py` reports the actual HTTP
     status and a snippet of the response body on a terminal failure — read
     it before diagnosing. If the failure is environmental (TLS/proxy/
     network/dependencies) and fixable **without touching any detector
     threshold, filter parameter, or ranking logic**: fix it, re-run once,
     and state exactly what you changed. Otherwise say which stage failed
     and stop. The guardrail — never loosen a threshold to manufacture
     hits — still holds.
   - **41** — fetch reached zero batches. A transport failure, not a quiet
     market. Diagnose the network path (curl_cffi vs the egress proxy, the
     nsearchives.nseindia.com / *.finance.yahoo.com allowlist). Do not
     report it as a holiday.
   - **0** — continue.

3. Read `work/run_meta.json` for coverage, the last closed bar timestamp, and
   the funnel counts. `funnel` holds one entry per pattern; `patterns_run`
   says which screens actually ran. `raw_hits`/`clean_hits` are the rally_cup
   numbers (kept under those names for continuity); the dip's are
   `dip_raw_hits`/`dip_clean_hits`. There is no holiday/staleness exit: the run always
   screens the latest available session. Check `session_age_days` — when it is
   nonzero the latest session predates today (NSE holiday, weekend, the run
   fired before 09:15 IST or after midnight IST, or the feed has not yet
   published). That is not an error; screen it anyway, but label everything as
   the `session_date` session, never as today's. If `session_age_days` is
   large (roughly `> 4`, i.e. more than a long weekend), the feed is likely
   stale on Yahoo's side rather than an off-hour timing artifact — say so
   prominently at the top of the report and flag the whole scan as suspect
   rather than presenting it as a normal run. Also check `pct_at_last_bar`:
   if it is well below 100 the
   universe's `last_closed_bar` is *not* the price time for every symbol. Per-hit
   staleness lives in `bars_behind_universe` inside `hits_clean.json`; when it
   is nonzero, quote that hit at its own `last_ts`, not at the universe last
   bar. The pipeline prints a WARN line when this matters.

4. **Open BOTH `work/hits.png` and `work/dip_hits.png` with the Read tool and
   actually look at every panel.** This step is not optional and cannot be
   replaced by reading the JSON. Whichever chart is missing because that
   pattern found nothing, say so rather than skipping quietly.

   For `hits.png` (rally_cup) — a V-shaped bounce fits a parabola better than a
   real rounded base, so the highest-R² name in a batch is often the worst
   candidate. Each panel draws both fits: a solid curve (parabola) and a dashed
   line (best two-segment V). Per panel ask:
   - Is the rally *sustained*, or one gap candle plus drift?
   - Does the base **round**, or is it a V, a descending wedge, or a flat shelf?
     Where the dashed V hugs the candles more tightly than the curve, distrust
     the name even though it passed.
   - Do the fast EMAs run under the base and rise through it?
   - Is there overhead supply to the left?

   For `dip_hits.png` (momentum_dip) — the questions are different, because the
   entry is inside a move that has not finished:
   - Is the advance a real trend, or one gap and a drift?
   - Is the dip *orderly* — stair-steps down — or a cliff?
   - Were the highs before the swing high already rolling over? A pullback
     inside a topping pattern passes every numeric gate.
   - Does the last bar genuinely turn, or is the trigger one small up-close?
   - Is the dip low a stop you could carry? At 1-3% it will be tested by noise.

   Sort each list separately into: clean structural match / marginal /
   distrust-despite-passing. Say why for anything in the last two buckets.

   Also read `work/shape_rejects.json` — the rally_cup candidates that cleared
   every other gate and died only on the saucer-vs-V test. If any sat within
   about 0.02 of the `vee_gain` threshold, name it in the report as a boundary
   call. If that file is long and the clean list is empty, say that the shape
   gates are what emptied the screen; that is not the same statement as "the
   market was quiet".

5. Write `work/report.md` following step 7 of the `nse-pattern-screener` skill:
   coverage and last closed bar; the per-pattern funnel with what each filter
   cut; **one ranked table per pattern**; the tiers from your visual pass; and
   the risk check.

   The risk check differs by pattern and both halves must appear:
   - **rally_cup** — print `risk_pct_to_base_low` next to a 3% stop and say
     plainly when the two are incompatible, which they usually are: bases run
     4-8% deep, so a fixed 3% stop sits mid-cup and dies to ordinary chop.
   - **momentum_dip** — the mirror image. Its structural stop is 1-3% away, so
     the danger is that the stop is too TIGHT, not too wide: the dip low is the
     most-tested price in the setup. Quote `risk_pct_buffered` (half an ATR
     below the dip low) as the risk a real position carries, and state the RRR
     that implies, not just the headline one.

   **Never merge the two tables or rank across them.** A dip's RRR of 11 and a
   cup's of 3.4 are not on the same scale — the dip's denominator is a 1.3%
   stop inside an unfinished move. Say this once, explicitly, in the report.

   This screen runs on intraday hourly candles and may fire several times a
   day, so the report must make its two timestamps unambiguous, both from
   `run_meta.json`:
   - **Executed at** — `run_ts_ist` (IST), the wall-clock time this run ran.
   - **Latest data bar** — `last_closed_bar` / `session_date`, the newest
     candle screened. When `session_age_days` is nonzero, say so explicitly
     and label the whole report as the `session_date` session, not today's.
   Put both at the very top of the report so two runs an hour apart can never
   be confused for each other.

6. Deliver it:
   - Upload `work/report.md`, `work/hits_clean.csv` and
     `work/dip_hits_clean.csv` to the Google Drive
     folder `NSE Screener` (create it if missing). Because several runs can
     land on one date, put the run time in the filename, not just the date:
     name them `YYYY-MM-DD-HHMM-nse-screen.md`,
     `YYYY-MM-DD-HHMM-nse-screen-cup.csv` and
     `YYYY-MM-DD-HHMM-nse-screen-dip.csv`, where `YYYY-MM-DD` is the
     `session_date` from `run_meta.json` (the last-closed-bar date, i.e. the
     session the report actually covers) and `HHMM` is the IST hour+minute
     of `run_ts_ist` (the run's wall-clock start). This is the same key the
     archive slot uses, so the Drive copy, the archive slot and the report's
     top-line dating all agree: an intraday re-run of the same session gets
     a new `HHMM` under the same `YYYY-MM-DD`, and a scan of yesterday's
     session (post-midnight fire, holiday, etc.) still files under the
     session's date rather than today's. All three files are text and go
     through the Google Drive connector without issue. Skip the CSV of a
     pattern that found nothing, and say in the report that it found nothing.
   - The charts (`work/hits.png`, `work/dip_hits.png`) cannot go through the
     connector at legible quality — their base64 encoding is prohibitively
     large for a tool call. Instead: publish each as an Artifact (that upload
     takes a path and works), and include both Artifact URLs near the top of
     the Google Drive report, labelled by pattern, so the Drive copy has a
     one-click route to each chart.
   - Then archive to `claude/screener-runs`. Run `bash archive_run.sh` — it
     stages `report.md` and `run_meta.json` plus, for each pattern that ran,
     that pattern's clean JSON/CSV, chart and diagnostics, into
     `runs/YYYY-MM-DD/HHMM-<universe>/`, clearing
     the slot first so a stale file from an earlier run in the same slot
     cannot masquerade as part of this one. The per-run subdirectory keeps
     multiple runs on the same date from silently overwriting each other.
     After it stages, commit and push on `claude/screener-runs`. Do NOT
     merge that branch into `master` — routines re-clone `master` on every
     run, so archived runs must stay on their own branch.

Honesty requirements, which override any instinct to produce a tidy result:
- These are **candidates matching a geometry, not recommendations**. Say so.
- Report actual coverage. The default universe is EQ (~2,293 symbols) with
  coverage typically ~92%; state the actual numerator/denominator and do
  not imply a full-universe scan when a chunk is missing. If `UNIVERSE`
  was overridden on the routine to a narrower slice, name the slice and
  say it is narrower than the skill's default.
- Name the ones you distrust even though they passed every filter. Disagreeing
  with the numbers is the entire point of step 4.
- If zero names survive on a pattern, say zero for that pattern and attach its
  diagnostic output (`work/diagnose.txt` for rally_cup,
  `work/dip_diagnose.txt` for momentum_dip). A quiet day and a mis-calibrated
  threshold look identical in the output and are not the same thing. For
  rally_cup, check `work/shape_rejects.json` first: a long reject list beside
  zero survivors means the shape gates were the constraint, and the report must
  say that instead of "quiet market".
- The momentum_dip list buys into moves that have not finished. Say so plainly:
  there is no breakout confirmation, the stop is tight enough to be hit by
  ordinary noise, and "the trend is intact" is a statement about the past.
- Never loosen a threshold and re-run to manufacture hits. If you think one
  needs tuning, say so in the report and leave it alone.
