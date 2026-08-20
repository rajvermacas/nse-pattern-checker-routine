# Routine prompt

Paste everything below the line into the routine's **Instructions** box. It has
to be self-contained: the run is autonomous, there is no one to ask, and each
run starts from a fresh clone with zero prior context.

---

Run the daily NSE hourly pattern screen.

1. Execute `bash run_screener.sh` from the repository root. It may take 5–30
   minutes depending on `UNIVERSE`. If a single invocation times out, run it
   again — the data fetch is resumable and skips batches already on disk.

2. Handle the exit code before anything else:
   - **20** — no fresh session data (NSE holiday, or Yahoo hasn't published
     yet). Post a one-line note saying the market didn't trade today and stop.
     Do not report yesterday's charts as today's scan.
   - **30** — fetch coverage below the floor. Report the coverage number and
     that the scan is not trustworthy today. Do not publish a shortlist.
   - **40** — a stage failed. If the failure is environmental (TLS/proxy/
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
   the funnel counts.

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

6. Deliver it:
   - Upload `work/report.md` and `work/hits_clean.csv` to the Google Drive
     folder `NSE Screener` (create it if missing). Name them
     `YYYY-MM-DD-nse-screen.md` and `YYYY-MM-DD-nse-screen.csv`. Both are
     text and go through the Google Drive connector without issue.
   - The chart (`work/hits.png`) cannot go through the connector at
     legible quality — its base64 encoding is prohibitively large for a
     tool call. Instead: publish it as an Artifact (that upload takes a
     path and works), and include the Artifact URL near the top of the
     Google Drive report so the Drive copy has a one-click route to the
     chart.
   - Then commit `report.md`, `hits.png`, `hits_clean.csv`, `run_meta.json`
     and `hits_clean.json` to `runs/YYYY-MM-DD/` on the
     `claude/screener-runs` branch as a durable archive, and push it. Do
     NOT merge that branch into `master` — routines re-clone `master` on
     every run, so archived runs must stay on their own branch.

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
