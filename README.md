# nse-screener-routine

Runs the `nse-pattern-screener` skill unattended as a Claude Code cloud
routine, on Anthropic's infrastructure, with no machine of yours awake.

```
.claude/skills/nse-pattern-screener/   the skill + its scripts (cloned each run)
run_screener.sh                        the deterministic pipeline
setup.sh                               dependency install (paste into the environment)
ROUTINE_PROMPT.md                      the prompt to paste into the routine
```

## Setup

**1. Push this to a private GitHub repo.** Routines clone a repo from its
default branch on every run; skills committed under `.claude/skills/` are
available to the session. Make sure `run_screener.sh` is executable
(`git update-index --chmod=+x run_screener.sh`).

**2. Create the routine.** Either `/schedule` in the CLI, or
[claude.ai/code/routines](https://claude.ai/code/routines) → **New routine**.
The web form is worth using here because you need to touch the environment.

- **Instructions**: contents of `ROUTINE_PROMPT.md`
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

**5. Trigger**: the **weekdays** preset, at **16:15 IST**. Times are entered in
your local zone. Runs stagger a few minutes after the scheduled time, which is
why 16:15 rather than 16:00 — the 15:15 hourly bar closes at 15:30 and Yahoo
takes a few minutes to settle. Minimum interval is one hour; for a custom cron
use `/schedule update` in the CLI.

**6. Click Run now** and read the transcript before trusting the schedule. A
green status only means the session exited without an infrastructure error — it
does not mean the screen worked.

## Things worth knowing before you rely on it

**Every run is a fresh clone, so there is no parquet cache.** That is the real
cost of the cloud model here: a full ~2,300-symbol EQ pull takes 15–40 minutes
and burns it on every run. `UNIVERSE` therefore defaults to `nifty500`, which
finishes in about five minutes. This is a genuine narrowing versus the skill's
own default, and the report says so. If you want the full universe, set
`UNIVERSE=EQ` as an environment variable and expect long, expensive runs.

**Routines draw down your subscription usage and have a daily run cap.** One
weekday run is comfortable; hourly intraday scanning is not what this is for.

**The partial-bar logic is inverted from the skill's snippet, deliberately.**
The skill drops `max(ts)` unconditionally because it assumes you're running
intraday. `run_screener.sh` drops it only when the market is actually open, so
a 16:15 run keeps the 15:15 close instead of silently reporting 14:15 prices.

**The holiday guard is exit code 20, not a failure.** Cron fires on NSE
holidays and yfinance returns the previous session without complaint. The run
checks that the newest bar is dated today and stops if it isn't.

**Charts are matplotlib renderings of yfinance data.** EMA seeding and session
handling differ from TradingView and Kite. Treat them as shape verification and
confirm prices on your own platform before acting on anything.
