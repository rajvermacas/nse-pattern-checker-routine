Run the daily NSE hourly pattern screen.

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
   the funnel counts. There is no holiday/staleness exit: the run always
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

4. **Open `work/hits.png` with the Read tool and actually look at every panel.**
   This step is not optional and cannot be replaced by reading the JSON. A
   V-shaped bounce fits a parabola better than a real rounded base, so the
   highest-R² name in a batch is often the worst candidate. For each panel ask:
   - Is the rally *sustained*, or one gap candle plus drift?
   - Does the base **round**, or is it a V, a descending wedge, or a flat shelf?
   - Do the fast EMAs run under the base and rise through it?
   - Is there overhead supply to the left?

   Sort the names into: clean structural match / marginal / distrust-despite-
   passing. Say why for anything in the last two buckets.

5. Write `work/report.md` following step 7 of the `nse-pattern-screener` skill:
   coverage and last closed bar; the funnel with what each filter cut; the
   ranked table; the tiers from your visual pass; and the stop-inside-base
   check — for every name, print `risk_pct_to_base_low` next to a 3% stop and
   say plainly when the two are incompatible, which they usually are.

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
   - Upload `work/report.md` and `work/hits_clean.csv` to the Google Drive
     folder `NSE Screener` (create it if missing). Because several runs can
     land on one date, put the run time in the filename, not just the date:
     name them `YYYY-MM-DD-HHMM-nse-screen.md` and
     `YYYY-MM-DD-HHMM-nse-screen.csv`, where `YYYY-MM-DD` is the
     `session_date` from `run_meta.json` (the last-closed-bar date, i.e. the
     session the report actually covers) and `HHMM` is the IST hour+minute
     of `run_ts_ist` (the run's wall-clock start). This is the same key the
     archive slot uses, so the Drive copy, the archive slot and the report's
     top-line dating all agree: an intraday re-run of the same session gets
     a new `HHMM` under the same `YYYY-MM-DD`, and a scan of yesterday's
     session (post-midnight fire, holiday, etc.) still files under the
     session's date rather than today's. Both files are text and go through
     the Google Drive connector without issue.
   - The chart (`work/hits.png`) cannot go through the connector at
     legible quality — its base64 encoding is prohibitively large for a
     tool call. Instead: publish it as an Artifact (that upload takes a
     path and works), and include the Artifact URL near the top of the
     Google Drive report so the Drive copy has a one-click route to the
     chart.
   - Then archive to `claude/screener-runs`. Run `bash archive_run.sh` — it
     stages `report.md`, `hits.png`, `hits_clean.csv`, `run_meta.json` and
     `hits_clean.json` into `runs/YYYY-MM-DD/HHMM-<universe>/`, clearing
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
- If zero names survive, say zero and attach the diagnostic output from
  `work/diagnose.txt`. A quiet day and a mis-calibrated threshold look
  identical in the output and are not the same thing.
- Never loosen a threshold and re-run to manufacture hits. If you think one
  needs tuning, say so in the report and leave it alone.
