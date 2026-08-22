# nse-screener-routine

Runs the `nse-pattern-screener` skill unattended as a Claude Code cloud
routine, on Anthropic's infrastructure, with no machine of yours awake.

```
.claude/skills/nse-pattern-screener/   the skill + its scripts (cloned each run)
run_screener.sh                        the deterministic pipeline
setup.sh                               dependency install (paste into the environment)
ROUTINE_PROMPT.md                      the instructions the routine reads each run
```

Each run screens for **two patterns** over the same bars:

| | `rally_cup` | `momentum_dip` |
|---|---|---|
| the setup | rally into a rounded base near the highs | shallow, orderly pullback inside an advance |
| you buy | the breakout above the lip of a finished base | inside a move that has not finished |
| the stop | base low, typically 4–8% away | dip low, typically 1–3% away |
| outputs | `hits.png` `hits_clean.csv` `hits_clean.json` | `dip_hits.png` `dip_hits_clean.csv` `dip_hits_clean.json` |

They are different trades and the report keeps them in separate tables. Set
`PATTERNS` on the routine (default `rally_cup momentum_dip`) to run only one.

## Setup

**1. Push this to a private GitHub repo.** Routines clone a repo from its
default branch on every run; skills committed under `.claude/skills/` are
available to the session. Make sure `run_screener.sh` is executable
(`git update-index --chmod=+x run_screener.sh`).

**2. Create the routine.** Either `/schedule` in the CLI, or
[claude.ai/code/routines](https://claude.ai/code/routines) → **New routine**.
The web form is worth using here because you need to touch the environment.

- **Instructions**: a thin pointer, not a copy — the routine reads the real
  instructions from the repo on every run, so `ROUTINE_PROMPT.md` and the
  code it depends on stay in one commit and cannot drift apart:

  ```
  Run the daily NSE hourly pattern screen.

  Read ROUTINE_PROMPT.md at the repository root and follow it exactly.
  That file is the authoritative instruction set; this message only
  points at it.

  If ROUTINE_PROMPT.md is missing or unreadable, stop immediately and
  report that — do not attempt the screen from memory.
  ```
- **Repositories**: this repo
- **Connectors**: keep Google Drive. Remove Asana, Sentry, and Gmail —
  a routine can call every tool on an included connector, including writes,
  with no approval prompt.

**3. Fix the network policy — this is the step that will otherwise bite you.**
The Default environment uses *Trusted* access, which only allows a package-manager
allowlist. Yahoo and NSE are not on it, and the fetch will fail with `403` and
`x-deny-reason: host_not_allowed`. Edit the environment → **Network access** →
**Custom**, tick *include default list of common package managers*, and add:

```
nsearchives.nseindia.com
query1.finance.yahoo.com
query2.finance.yahoo.com
fc.yahoo.com
finance.yahoo.com
```

**4. Setup script**: contents of `setup.sh`. It's cached, so it won't re-run
every session.

**5. Trigger**: the **weekdays** preset, at **16:15 IST**, is the baseline
end-of-day run. Times are entered in your local zone. Runs stagger a few
minutes after the scheduled time, which is why 16:15 rather than 16:00 — the
15:15 hourly bar closes at 15:30 and Yahoo takes a few minutes to settle.
Minimum interval is one hour; for a custom cron use `/schedule update` in the
CLI. The screen works on intraday hourly candles, so you can add mid-session
triggers (e.g. hourly through the day) to catch bases as they form — each run
records both its execution time and the bar it screened, and the Drive files
and archive slots are keyed by `YYYY-MM-DD-HHMM`, so intraday re-runs coexist
instead of overwriting each other. Mind the usage note below.

**6. Click Run now** and read the transcript before trusting the schedule. A
green status only means the session exited without an infrastructure error — it
does not mean the screen worked.

## Things worth knowing before you rely on it

**Every run is a fresh clone, so there is no parquet cache.** `UNIVERSE`
defaults to `EQ` — the full ~2,300-symbol NSE equity list, matching the skill's
own default. The fetch is serial (Yahoo rate-limits parallel sessions) and
runs 10–20 minutes on cold caches; the resumable batch loop survives single
command timeouts. Coverage typically lands near 92% — recent listings lack 60
days of history and some symbols don't map to `SYMBOL.NS` on Yahoo. The
`MIN_COVERAGE=80` floor rejects anything worse than that with exit 30. To
scan a narrower slice for testing, set `UNIVERSE=nifty500` (or `nifty200`,
`midcap150`, …) as an environment variable on the routine.

**Routines draw down your subscription usage and have a daily run cap.** Each
run does a full serial fetch of the universe (10–20 min, no cross-run cache),
so cost scales with how many times a day you fire it. A handful of intraday
runs is fine; a run every hour on the full EQ universe will eat usage and can
bump the daily cap. If you want frequent intraday scans, point `UNIVERSE` at a
narrower slice (`nifty500`, `nifty200`, …) to keep each run cheap, or set
`PATTERNS` to a single screen.

**The partial-bar logic is inverted from the skill's snippet, deliberately.**
The skill drops `max(ts)` unconditionally because it assumes you're running
intraday. `run_screener.sh` drops it only when the market is actually open, so
a 16:15 run keeps the 15:15 close instead of silently reporting 14:15 prices.

**There is no holiday/staleness guard — the run screens the latest available
session, whatever its date.** Cron fires on NSE holidays too, and a run can
fire after IST midnight, so the newest bar is often not dated "today". The run
does not stop for this; it records `session_date` and `session_age_days` in
`run_meta.json` so the report labels the scan by the session it actually
covers instead of implying it is today's.

**The cup screen is much stricter than it used to be, on purpose.** Curvature
and R² cannot tell a rounded base from a V-bounce — the V usually fits the
parabola *better*. Two shape metrics now do: `vee_gain` (does a two-segment
straight-line V fit the base better than the curve?) and `bottom_frac` (does
price loiter at the base's low, or pass straight through it?). On a measured
live nifty500 session they cut 5 of 6 raw hits, and the charts confirmed four
were plainly V-bounces or one-gap "rallies". Expect single-digit raw hits on the
full EQ universe where the old thresholds gave 30–50, and expect genuine
zero-hit days. Everything the shape test cuts is written to
`work/shape_rejects.json`, so a too-tight threshold shows up as a long reject
list rather than as a silently quiet market.

**The dip screen buys into an unfinished move**, which is a better price and a
worse confirmation. Its failure mode is a falling knife, so it requires the last
bar to close up and off its low, the pullback to retrace no more than half the
advance, no single candle to account for most of the fall, and the entry bar to
close back above a rising EMA50. Its RRR numbers look far better than the cup's
(5–15 vs 2–5) purely because its stop is tighter — which also means likelier to
be hit. The two rankings are not on one scale and the report must not merge them.

**Verify detector changes without waiting for a market.** `python
.claude/skills/nse-pattern-screener/scripts/selftest_patterns.py` builds
synthetic bars with known shapes — a rounded base, a V-bounce, an orderly dip, a
falling knife, a one-candle gap-down — runs the real detectors over them and
asserts on the result. Deterministic, no network, a few seconds.

**Charts are matplotlib renderings of yfinance data.** EMA seeding and session
handling differ from TradingView and Kite. Treat them as shape verification and
confirm prices on your own platform before acting on anything.
