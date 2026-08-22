#!/usr/bin/env bash
# Deterministic half of the nse-pattern-screener pipeline: universe -> fetch ->
# drop-partial-bar -> detect -> context filter -> plot.
#
# Produces, in $WORK:
#   run_meta.json    coverage, last closed bar, universe, per-pattern funnels
#
#   rally_cup (the breakout screen -- buy the lip of a finished base):
#     hits.json / hits_clean.json / hits_clean.csv / hits.png
#     shape_rejects.json  cleared every legacy gate, failed the saucer-vs-V test
#
#   momentum_dip (the pullback screen -- buy inside an unfinished dip):
#     dip_hits.json / dip_hits_clean.json / dip_hits_clean.csv / dip_hits.png
#
# Both charts still have to be LOOKED at. Neither detector's numbers are the
# deliverable; the shortlist that survives the visual pass is.
#
# PATTERNS selects which screens run (default: both). The two are complements,
# not variants: one buys a completed base breaking out, the other buys a live
# pullback. They will rarely name the same stock, and their RRRs are not
# directly comparable -- the dip's stop is tighter AND likelier to be hit.
#
# Exit codes:
#   0   pipeline completed (hits may be zero; check run_meta.json)
#   30  fetch coverage too low to trust the scan
#   40  a pipeline stage failed
#   41  fetch reached zero batches (transport failure, not a quiet market)
#
# There is deliberately no "stale data" exit any more. The run screens the
# latest available session whatever its date; `session_date` and
# `session_age_days` in run_meta.json carry the dating that the report must
# quote.
set -uo pipefail

SKILL="${SKILL:-.claude/skills/nse-pattern-screener}"
WORK="${WORK:-work}"
UNIVERSE="${UNIVERSE:-EQ}"         # EQ | nifty500 | nifty200 | midcap150 | ...
PERIOD="${PERIOD:-60d}"
INTERVAL="${INTERVAL:-1h}"
BATCH="${BATCH:-40}"
WORKERS="${WORKERS:-1}"             # yfinance threads; 1 = serial (safe default)
MAX_FETCH_PASSES="${MAX_FETCH_PASSES:-6}"
MIN_COVERAGE="${MIN_COVERAGE:-80}"   # percent of universe with usable data
MIN_TURNOVER="${MIN_TURNOVER:-5}"    # rupees crore/day
TARGET_PCT="${TARGET_PCT:-15}"
PATTERNS="${PATTERNS:-rally_cup momentum_dip}"

# True start-of-run wall clock, captured before the 10-30 minute fetch. The
# dating step used to stamp run_ts_ist with its own `now`, which is post-fetch
# -- so a 16:15 run advertised itself as ~16:40 in the report, the Drive
# filename and the archive slot, all three of which document it as the run's
# start time. Capture it once, here, and let the dating step record its own
# (genuinely later) clock separately as data_snapshot_ist.
RUN_STARTED_IST="$(TZ=Asia/Kolkata date +%Y-%m-%dT%H:%M:%S%:z)"
export RUN_STARTED_IST

die() { echo "FAIL: $*" >&2; exit 40; }

# Resolve the scripts directory BEFORE cd-ing into $WORK. It used to be
# "../$SKILL/scripts", which silently assumed $WORK was exactly one level below
# the repo root -- so any absolute or nested WORK (a scratch dir, a test run)
# failed at step 1 with "universe fetch", pointing the diagnosis at the network.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "$SKILL" in
  /*) S="$SKILL/scripts" ;;
  *)  S="$REPO_ROOT/$SKILL/scripts" ;;
esac
[ -d "$S" ] || die "skill scripts not found at $S (set SKILL= to the skill dir)"

mkdir -p "$WORK"
cd "$WORK" || die "cannot enter work dir $WORK"

# ------------------------------------------------------------ 0. dependencies
# The environment's setup-script cache is not always warm (a rebuilt container,
# a fresh session, a routine firing right after an image change). Without this
# preflight, missing deps show up as `FAIL: universe fetch` at step 1 -- a
# misleading message that sends the diagnosis down the wrong path.
# Show the real ImportError instead of hiding it: a broken install (ABI
# mismatch, half-written wheel) is not the same as "not installed", and
# 2>/dev/null made the two look identical.
if ! import_err=$(python -c "import yfinance, polars, pandas, pyarrow, numpy, matplotlib, requests" 2>&1); then
  echo "== dependencies not importable: ${import_err##*$'\n'}"
  echo "== installing pipeline dependencies"
  pip install --break-system-packages -q \
    yfinance polars pandas pyarrow numpy matplotlib requests \
    || die "dependency install"
  python -c "import yfinance, polars, pandas, pyarrow, numpy, matplotlib, requests" \
    || die "dependencies still not importable after install"
fi

# ---------------------------------------------------------------- 1. universe
echo "== universe: $UNIVERSE"
if [ "$UNIVERSE" = "EQ" ]; then
  python "$S/fetch_universe.py" --series EQ --out universe.txt || die "universe fetch"
else
  python "$S/fetch_universe.py" --index "$UNIVERSE" --out universe.txt || die "universe fetch"
fi
# Count non-empty lines. `wc -l` misses the final entry when the file has no
# trailing newline (which it does not), producing `500/499 (100%)` cosmetics
# and, more seriously, an inflated coverage percentage that would let a
# partial scan slip past the MIN_COVERAGE floor.
N_SYMBOLS=$(grep -c . universe.txt)
echo "   $N_SYMBOLS symbols"
[ "$N_SYMBOLS" -gt 10 ] || die "universe looks empty ($N_SYMBOLS)"

# ------------------------------------------------------------------- 2. fetch
# fetch_data.py is resumable: it writes one parquet per batch and skips batches
# already on disk. A full EQ pull exceeds a single command timeout, so call it
# repeatedly until the part count stops growing.
EXPECTED_PARTS=$(( (N_SYMBOLS + BATCH - 1) / BATCH ))
echo "== fetch: expecting ~$EXPECTED_PARTS parts (workers=$WORKERS)"
PREV=-1
for pass in $(seq 1 "$MAX_FETCH_PASSES"); do
  # A non-zero exit from fetch_data used to be swallowed by `|| true`, so a
  # crash on pass 1 looked identical to "some batches remain". Capture the
  # code and log it -- but keep going, because a partial pass is still useful
  # progress on the resumable parts dir.
  python "$S/fetch_data.py" --universe universe.txt --period "$PERIOD" \
    --interval "$INTERVAL" --out-dir parts --batch "$BATCH" \
    --workers "$WORKERS"
  rc=$?
  # Count SYMBOLS on disk, not part FILES. A batch that returned 25 of 40
  # symbols still writes its p*.parquet, so a file count hits 58/58 and breaks
  # this loop while ~300 symbols are missing -- which is exactly how 107
  # rate-limited names were silently written off on the 2026-08-20 EQ run.
  HAVE_FILES=$(ls parts/*.parquet 2>/dev/null | wc -l)
  HAVE=$(python -c "
import glob, sys
try:
    import pandas as pd
    got=set()
    for f in glob.glob('parts/*.parquet'):
        got |= set(pd.read_parquet(f, columns=['symbol'])['symbol'].unique())
    print(len(got))
except Exception:
    print(0)
" 2>/dev/null || echo 0)
  if [ "$rc" -ne 0 ]; then
    echo "   pass $pass: fetch_data exited $rc ($HAVE/$N_SYMBOLS symbols, $HAVE_FILES/$EXPECTED_PARTS parts)"
  else
    echo "   pass $pass: $HAVE/$N_SYMBOLS symbols ($HAVE_FILES/$EXPECTED_PARTS parts)"
  fi
  # Yahoo genuinely lacks 60d of hourly history for a tail of recent listings,
  # so requiring 100% would loop forever. Stop once we clear the coverage floor
  # the run would accept anyway.
  NEED=$(( N_SYMBOLS * MIN_COVERAGE / 100 ))
  [ "$HAVE" -ge "$NEED" ] && { echo "   symbol coverage above floor (${MIN_COVERAGE}%), stopping"; break; }
  # Pass 1 producing zero parts is a terminal transport failure -- retrying
  # walks over every batch again for another guaranteed failure. Stop now and
  # let the zero-batch guard below give the right diagnostic.
  [ "$pass" -eq 1 ] && [ "$HAVE" -eq 0 ] && { echo "   pass 1 produced nothing"; break; }
  [ "$HAVE" -eq "$PREV" ] && { echo "   no progress, stopping retries"; break; }
  PREV=$HAVE
done

# Fetch reached nothing -> exit 41. A distinct code so the routine prompt can
# distinguish "the network path to Yahoo is broken" from "a pipeline stage
# died" (40). Merge would otherwise fail with the wrong stage name in the error.
if [ "$(ls parts/*.parquet 2>/dev/null | wc -l)" -eq 0 ]; then
  {
    echo "fetch produced zero parquet batches - no data reached disk."
    echo "This is a transport failure, not a market or holiday condition."
    echo "Check the TLS path to Yahoo (curl_cffi vs the egress proxy) and"
    echo "the presence of nsearchives.nseindia.com / *.finance.yahoo.com in"
    echo "the environment's network allowlist before treating as a data issue."
  } >&2
  exit 41
fi

python "$S/fetch_data.py" --merge parts --out all.parquet || die "merge"

COVERED=$(python -c "
import polars as pl
print(pl.read_parquet('all.parquet')['symbol'].n_unique())
")
COV_PCT=$(( 100 * COVERED / N_SYMBOLS ))
echo "   coverage: $COVERED/$N_SYMBOLS (${COV_PCT}%)"
if [ "$COV_PCT" -lt "$MIN_COVERAGE" ]; then
  echo "coverage ${COV_PCT}% below floor ${MIN_COVERAGE}% - refusing to report a partial scan as a scan" >&2
  exit 30
fi

# ------------------------------------------- 3. drop the in-progress bar (only
# if the market is actually open). The skill's snippet drops max(ts)
# unconditionally because it assumes an intraday run. Post-close the 15:15 stub
# is a genuine close, and dropping it silently ages every "distance from lip"
# by an hour.
# The `rc=$?` dispatch below turns any non-zero status from this heredoc into a
# stage failure (40). (An earlier version wrote `python - <<'PY' || exit 40`,
# which preempted a then-live multi-code dispatch and made it dead code; the
# dispatch is the surviving, correct form.)
python - <<'PY'
import json, os
from datetime import datetime, time
from zoneinfo import ZoneInfo
import polars as pl

IST = ZoneInfo("Asia/Kolkata")
# run_ts_ist is the run's START, captured in the shell before the multi-minute
# fetch (RUN_STARTED_IST). `now` here is the later dating-step clock, recorded
# separately as data_snapshot_ist. "today" for staleness keys off the run
# start, so the report's "Executed at" and its session-age reasoning agree.
now = datetime.now(IST)
run_started = datetime.fromisoformat(os.environ["RUN_STARTED_IST"])
today = run_started.date()
market_open = (now.weekday() < 5 and time(9, 15) <= now.time() < time(15, 30))

df = pl.read_parquet("all.parquet")
mx = df["ts"].max()
if market_open:
    df = df.filter(pl.col("ts") < mx)
    print(f"market OPEN at {now:%H:%M} IST - dropped in-progress bar {mx}")
else:
    print(f"market CLOSED at {now:%H:%M} IST - keeping final bar {mx}")
df.write_parquet("all_closed.parquet")

last = df["ts"].max()
print("last closed bar:", last)

# Recency-aware coverage. The plain "symbols_with_data" count treated a symbol
# whose newest bar was hours ago the same as one that had the current bar,
# which let run_meta advertise coverage_pct=100 while 38% of the universe was
# behind the reported last_closed_bar. That timestamp then rode into the
# report as the price time for hits that were actually an hour stale. The
# guard here is the missing dimension: how many symbols carry the newest bar,
# and what the modal last bar looks like across the universe.
per_sym_last = df.group_by("symbol").agg(pl.col("ts").max().alias("last"))
n_total = per_sym_last.height
at_last = per_sym_last.filter(pl.col("last") == last).height
pct_at_last = round(at_last / n_total * 100, 1) if n_total else 0.0
consensus = (per_sym_last.group_by("last").len()
             .sort("len", descending=True).head(1))
consensus_ts = str(consensus["last"][0])
consensus_n = int(consensus["len"][0])

# Session dating. This used to be a hard guard that exited 20 whenever the
# newest bar was not dated today; it now only records what it sees. The run
# screens whatever the latest available session is -- an NSE holiday, a
# not-yet-published feed and a post-midnight-IST firing all just mean "the
# latest session is older than the wall clock", which is a fact to report,
# not a reason to refuse.
#
# The dating still has to survive into the report: a scan of a three-day-old
# session is a legitimate scan of that session and an illegitimate scan of
# today. `session_date` and `session_age_days` are what downstream prose must
# quote so the two can never be confused.
session_age = (today - last.date()).days
json.dump({
    "run_ts_ist": run_started.isoformat(),
    "data_snapshot_ist": now.isoformat(),
    "last_closed_bar": str(last),
    "session_date": str(last.date()),
    "session_age_days": session_age,
    "symbols_at_last_bar": at_last,
    "pct_at_last_bar": pct_at_last,
    "consensus_last_bar": consensus_ts,
    "consensus_last_bar_symbols": consensus_n,
    "market_open_at_run": market_open,
}, open("bar_meta.json", "w"), indent=2)
print(f"symbols carrying {last}: {at_last}/{n_total} ({pct_at_last}%); "
      f"universe consensus last bar: {consensus_ts} ({consensus_n} symbols)")
if session_age != 0:
    print(f"NOTE: latest available session is {last.date()}, {session_age} day(s) "
          f"before the run date ({today}). Screening it anyway, as configured. "
          f"Report it as the {last.date()} session, NOT as today's. "
          f"A large age (roughly >4 days) means the feed is likely stale -- "
          f"say so prominently rather than publishing it as a normal scan.")
PY
rc=$?
[ "$rc" -ne 0 ] && exit 40

# ------------------------------------------- 4-6. detect, filter, plot
# One block per pattern. Each writes its own hits/clean/csv/png so the two
# screens can never be read as one list -- they are different trades with
# different entries, different stops and different failure modes.
RAW=0; CLEAN=0; DIP_RAW=0; DIP_CLEAN=0; SHAPE_REJ=0

count_json() {  # count_json FILE -- 0 for a missing file, hard fail on bad JSON
  [ -f "$1" ] || { echo 0; return 0; }
  python -c "import json,sys;print(len(json.load(open(sys.argv[1]))))" "$1"
}

# Stale outputs from an earlier run in the same work/ dir must not survive into
# this one: a pattern that finds nothing today would otherwise ship yesterday's
# chart and CSV under today's run_meta.
rm -f hits.json hits_clean.json hits_clean.csv hits.png shape_rejects.json \
      dip_hits.json dip_hits_clean.json dip_hits_clean.csv dip_hits.png \
      diagnose.txt dip_diagnose.txt

for pat in $PATTERNS; do
  case "$pat" in
    rally_cup)
      echo "== detect: rally_cup (rally into a rounded base)"
      python "$S/screener.py" --parquet all_closed.parquet --json hits.json \
        --shape-rejects shape_rejects.json || die "screener"
      RAW=$(count_json hits.json) || die "raw hit count"
      SHAPE_REJ=$(count_json shape_rejects.json) || die "shape reject count"
      echo "   raw hits: $RAW   (shape-rejected: $SHAPE_REJ)"

      if [ "$RAW" -eq 0 ]; then
        echo "== zero raw hits - running diagnostics before anyone says 'quiet market'"
        python "$S/screener.py" --parquet all_closed.parquet --diagnose | tee diagnose.txt
      fi

      echo "== context filters: rally_cup"
      python "$S/postfilter.py" --hits hits.json --parquet all_closed.parquet \
        --out hits_clean.json --csv hits_clean.csv \
        --min-turnover "$MIN_TURNOVER" \
        --target-pct "$TARGET_PCT" || die "postfilter"
      CLEAN=$(count_json hits_clean.json) || die "clean hit count"
      echo "   clean hits: $CLEAN"

      if [ "$CLEAN" -gt 0 ]; then
        echo "== plot: rally_cup"
        python "$S/plot_hits.py" --hits hits_clean.json \
          --parquet all_closed.parquet --out hits.png || die "plot"
      fi
      ;;
    momentum_dip)
      echo "== detect: momentum_dip (pullback in a strong name)"
      python "$S/momentum_dip.py" --parquet all_closed.parquet \
        --json dip_hits.json --target-pct "$TARGET_PCT" || die "momentum_dip"
      DIP_RAW=$(count_json dip_hits.json) || die "dip raw count"
      echo "   raw dip hits: $DIP_RAW"

      if [ "$DIP_RAW" -eq 0 ]; then
        echo "== zero dip hits - diagnosing before calling it a quiet market"
        python "$S/momentum_dip.py" --parquet all_closed.parquet --diagnose \
          | tee dip_diagnose.txt
      fi

      echo "== context filters: momentum_dip"
      python "$S/postfilter.py" --hits dip_hits.json --parquet all_closed.parquet \
        --out dip_hits_clean.json --csv dip_hits_clean.csv \
        --min-turnover "$MIN_TURNOVER" \
        --target-pct "$TARGET_PCT" || die "postfilter (dip)"
      DIP_CLEAN=$(count_json dip_hits_clean.json) || die "dip clean count"
      echo "   clean dip hits: $DIP_CLEAN"

      if [ "$DIP_CLEAN" -gt 0 ]; then
        echo "== plot: momentum_dip"
        python "$S/plot_hits.py" --hits dip_hits_clean.json \
          --parquet all_closed.parquet --out dip_hits.png || die "plot (dip)"
      fi
      ;;
    *)
      die "unknown pattern '$pat' in PATTERNS (expected rally_cup, momentum_dip)"
      ;;
  esac
done

# `work/` persists across runs (the fetch is resumable), so an unguarded
# failure here is the one path that ships a silently wrong report: the script
# would exit 0 while run_meta.json still held the PREVIOUS run's timestamps,
# coverage and funnel counts, paired with this run's hits and chart. The Drive
# filename and the archive slot both key off run_ts_ist, so a stale one also
# overwrites the earlier run's archive. Since run_meta.json is now the only
# durable carrier of session_date/session_age_days, that must be a hard fail.
# Remove the stale file first so a crash can never leave a plausible one.
rm -f run_meta.json
python - <<PY || die "run_meta"
import json
meta = json.load(open("bar_meta.json"))
meta.update({
    "universe": "$UNIVERSE",
    "symbols_in_universe": $N_SYMBOLS,
    "symbols_with_data": $COVERED,
    "coverage_pct": $COV_PCT,
    "interval": "$INTERVAL",
    "patterns_run": "$PATTERNS".split(),
    # raw_hits/clean_hits stay the rally_cup funnel: they predate the second
    # pattern and downstream prose keys off them. Per-pattern counts below.
    "raw_hits": $RAW,
    "clean_hits": $CLEAN,
    "shape_rejects": $SHAPE_REJ,
    "chart": "hits.png" if $CLEAN > 0 else None,
    "dip_raw_hits": $DIP_RAW,
    "dip_clean_hits": $DIP_CLEAN,
    "dip_chart": "dip_hits.png" if $DIP_CLEAN > 0 else None,
    "funnel": {
        "rally_cup": {"raw": $RAW, "clean": $CLEAN, "shape_rejects": $SHAPE_REJ},
        "momentum_dip": {"raw": $DIP_RAW, "clean": $DIP_CLEAN},
    },
})
json.dump(meta, open("run_meta.json", "w"), indent=2)
print(json.dumps(meta, indent=2))

# Loud, machine-readable staleness warning: if a meaningful chunk of the
# universe is behind the reported last_closed_bar, every downstream reader
# needs to know before they quote those levels as current. The threshold is
# deliberately soft (>=5% behind) -- a couple of stragglers on Yahoo is
# normal; a third of the universe being an hour behind is not.
if meta["pct_at_last_bar"] < 95:
    print(f"WARN: only {meta['symbols_at_last_bar']}/{meta['symbols_in_universe']} "
          f"symbols carry the reported last bar {meta['last_closed_bar']}. "
          f"Universe consensus is {meta['consensus_last_bar']} "
          f"({meta['consensus_last_bar_symbols']} symbols). "
          f"Individual hits may be priced earlier -- check bars_behind_universe "
          f"in hits_clean.json before quoting levels.")

# A long shape-reject list next to zero survivors is the signature of a
# mis-calibrated saucer-vs-V threshold, which is indistinguishable from a
# quiet market in the hit count alone. Name it here so nobody has to guess.
if $SHAPE_REJ > 0 and $RAW == 0:
    print(f"WARN: every rally_cup candidate ($SHAPE_REJ of them) cleared the "
          f"legacy gates and died on the shape test. Read shape_rejects.json "
          f"before reporting a quiet market -- this is what a too-tight "
          f"max_vee_gain / min_bottom_frac looks like.")
PY

echo "== done. NOTHING here has been visually verified yet."
echo "   view hits.png (rally_cup) and dip_hits.png (momentum_dip) before reporting."
