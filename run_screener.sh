#!/usr/bin/env bash
# Deterministic half of the nse-pattern-screener pipeline: universe -> fetch ->
# drop-partial-bar -> detect -> context filter -> plot.
#
# Produces, in $WORK:
#   run_meta.json    coverage, last closed bar, universe, funnel counts
#   hits.json        raw detector hits
#   hits_clean.json  after context filters, ranked by structural RRR
#   hits.png         chart grid  <- a human or a model still has to LOOK at this
#
# Exit codes:
#   0   pipeline completed (hits may be zero; check run_meta.json)
#   20  no fresh session data (NSE holiday, or data not published yet) - not an error
#   30  fetch coverage too low to trust the scan
#   40  a pipeline stage failed
set -uo pipefail

SKILL="${SKILL:-.claude/skills/nse-pattern-screener}"
WORK="${WORK:-work}"
UNIVERSE="${UNIVERSE:-EQ}"         # EQ | nifty500 | nifty200 | midcap150 | ...
PERIOD="${PERIOD:-60d}"
INTERVAL="${INTERVAL:-1h}"
BATCH="${BATCH:-40}"
MAX_FETCH_PASSES="${MAX_FETCH_PASSES:-6}"
MIN_COVERAGE="${MIN_COVERAGE:-80}"   # percent of universe with usable data
MIN_TURNOVER="${MIN_TURNOVER:-5}"    # rupees crore/day
TARGET_PCT="${TARGET_PCT:-15}"

mkdir -p "$WORK"
cd "$WORK"
S="../$SKILL/scripts"

die() { echo "FAIL: $*" >&2; exit 40; }

# ------------------------------------------------------------ 0. dependencies
# The environment's setup-script cache is not always warm (a rebuilt container,
# a fresh session, a routine firing right after an image change). Without this
# preflight, missing deps show up as `FAIL: universe fetch` at step 1 -- a
# misleading message that sends the diagnosis down the wrong path.
if ! python -c "import yfinance, polars, pandas, pyarrow, numpy, matplotlib, requests" 2>/dev/null; then
  echo "== installing pipeline dependencies"
  pip install --break-system-packages -q \
    yfinance polars pandas pyarrow numpy matplotlib requests \
    || die "dependency install"
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
echo "== fetch: expecting ~$EXPECTED_PARTS parts"
PREV=-1
for pass in $(seq 1 "$MAX_FETCH_PASSES"); do
  python "$S/fetch_data.py" --universe universe.txt --period "$PERIOD" \
    --interval "$INTERVAL" --out-dir parts --batch "$BATCH" || true
  HAVE=$(ls parts/*.parquet 2>/dev/null | wc -l)
  echo "   pass $pass: $HAVE/$EXPECTED_PARTS parts"
  [ "$HAVE" -ge "$EXPECTED_PARTS" ] && break
  # Pass 1 producing zero parts is a terminal transport failure -- retrying
  # walks over every batch again for another guaranteed failure. Stop now and
  # let the zero-batch guard below give the right diagnostic.
  [ "$pass" -eq 1 ] && [ "$HAVE" -eq 0 ] && { echo "   pass 1 produced nothing"; break; }
  [ "$HAVE" -eq "$PREV" ] && { echo "   no progress, stopping retries"; break; }
  PREV=$HAVE
done

# Fetch reached nothing -> exit 41. A distinct code so the routine prompt can
# distinguish "the network path to Yahoo is broken" from "a pipeline stage
# died" (40), from "no market data today" (20). Merge would otherwise fail
# with the wrong stage name in the error.
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
python - <<'PY' || exit 40
import json, sys
from datetime import datetime, time
from zoneinfo import ZoneInfo
import polars as pl

IST = ZoneInfo("Asia/Kolkata")
now = datetime.now(IST)
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

# Holiday / stale-data guard: cron fires on NSE holidays too, and yfinance will
# happily hand back the previous session. Reporting that as today's scan is the
# failure mode worth spending an exit code on.
stale = last.date() != now.date()
json.dump({
    "run_ts_ist": now.isoformat(),
    "last_closed_bar": str(last),
    "market_open_at_run": market_open,
    "stale": stale,
}, open("bar_meta.json", "w"), indent=2)
if stale:
    print(f"STALE: newest bar is {last.date()}, today is {now.date()} "
          "(NSE holiday, or data not published yet)")
    sys.exit(20)
PY
rc=$?
[ "$rc" -eq 20 ] && exit 20
[ "$rc" -ne 0 ] && exit 40

# ------------------------------------------------------------------ 4. detect
echo "== detect"
python "$S/screener.py" --parquet all_closed.parquet --json hits.json || die "screener"
RAW=$(python -c "import json;print(len(json.load(open('hits.json'))))")
echo "   raw hits: $RAW"

if [ "$RAW" -eq 0 ]; then
  echo "== zero raw hits - running diagnostics before anyone says 'quiet market'"
  python "$S/screener.py" --parquet all_closed.parquet --diagnose | tee diagnose.txt
fi

# ---------------------------------------------------------- 5. context filters
echo "== context filters"
python "$S/postfilter.py" --hits hits.json --parquet all_closed.parquet \
  --out hits_clean.json --csv hits_clean.csv \
  --min-turnover "$MIN_TURNOVER" \
  --target-pct "$TARGET_PCT" || die "postfilter"
CLEAN=$(python -c "import json;print(len(json.load(open('hits_clean.json'))))")
echo "   clean hits: $CLEAN"

# -------------------------------------------------------------------- 6. plot
if [ "$CLEAN" -gt 0 ]; then
  echo "== plot"
  python "$S/plot_hits.py" --hits hits_clean.json --parquet all_closed.parquet \
    --out hits.png || die "plot"
fi

python - <<PY
import json
meta = json.load(open("bar_meta.json"))
meta.update({
    "universe": "$UNIVERSE",
    "symbols_in_universe": $N_SYMBOLS,
    "symbols_with_data": $COVERED,
    "coverage_pct": $COV_PCT,
    "interval": "$INTERVAL",
    "raw_hits": $RAW,
    "clean_hits": $CLEAN,
    "chart": "hits.png" if $CLEAN > 0 else None,
})
json.dump(meta, open("run_meta.json", "w"), indent=2)
print(json.dumps(meta, indent=2))
PY

echo "== done. NOTHING here has been visually verified yet."
