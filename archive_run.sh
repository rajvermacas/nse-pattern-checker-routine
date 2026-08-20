#!/usr/bin/env bash
# Deterministic archive of one screener run into runs/YYYY-MM-DD/HHMM-UNIVERSE/
# on the current branch. Usage:
#
#     bash archive_run.sh
#
# Reads from $WORK (default: work) and expects the deliverables run_screener.sh
# produced there. Writes a clean, self-contained directory:
#
#     report.md hits.png hits_clean.csv run_meta.json hits_clean.json
#
# The subdirectory keys on the run's actual start time and its universe, so
# multiple runs on the same date coexist instead of silently overwriting each
# other -- the earlier failure mode was a nifty200 run replacing a nifty500 run
# for 2026-08-20, recoverable only via git history and only if someone thought
# to look.
#
# The target directory is cleared before writing, so a stale file from a prior
# run in the same slot (which happened when the archived file set drifted from
# ROUTINE_PROMPT.md's list) cannot masquerade as part of this run.
#
# Committing and pushing are the caller's job -- this script only stages files.
set -euo pipefail

WORK="${WORK:-work}"

command -v python >/dev/null || { echo "archive: python required" >&2; exit 1; }
[ -f "$WORK/run_meta.json" ] || { echo "archive: $WORK/run_meta.json missing -- run run_screener.sh first" >&2; exit 1; }

# Slot key comes from run_meta.json so it matches what the report says, not
# from `date` (which would drift by seconds and, on a retry, disagree with
# what the run actually thinks it is).
#
# Date is `session_date` (the last-closed-bar date), not the run's calendar
# date. Otherwise an intraday screen at 01:24 IST -- which reports on the
# previous session -- would archive under tomorrow's folder, splitting the
# same session's runs across two date directories and misleading anyone
# scanning `ls runs/`. Every file the slot holds describes that session.
# HHMM stays run-start-time, so multiple intraday screens of one session
# still get distinct slots underneath it.
read -r DATE HHMM UNIVERSE < <(python - <<PY
import json, re, sys
m = json.load(open("$WORK/run_meta.json"))
date = m.get("session_date")
if not date:
    # Legacy runs before session_date existed used the run_ts_ist date;
    # keep parsing it as a fallback so old work/ dirs still archive.
    ts = m["run_ts_ist"]  # e.g. 2026-08-20T23:25:45.594610+05:30
    mo = re.match(r"(\d{4}-\d{2}-\d{2})", ts)
    if not mo:
        sys.exit(f"archive: cannot parse run_ts_ist {ts!r}")
    date = mo.group(1)
ts = m["run_ts_ist"]
mo = re.match(r"\d{4}-\d{2}-\d{2}T(\d{2}):(\d{2})", ts)
if not mo:
    sys.exit(f"archive: cannot parse run_ts_ist {ts!r} for HHMM")
hh, mm = mo.group(1), mo.group(2)
uni = re.sub(r"[^A-Za-z0-9._-]+", "-", str(m.get("universe", "unknown")))
print(date, f"{hh}{mm}", uni)
PY
)

DEST="runs/$DATE/$HHMM-$UNIVERSE"
echo "archive: -> $DEST"

# Clear the slot before writing. rm -rf is safe here because the path is
# fully derived from run_meta above and always begins with runs/, and the
# subsequent writes recreate every expected file.
rm -rf "$DEST"
mkdir -p "$DEST"

REQUIRED=(report.md hits.png hits_clean.csv run_meta.json hits_clean.json)
missing=()
for f in "${REQUIRED[@]}"; do
  if [ -f "$WORK/$f" ]; then
    cp "$WORK/$f" "$DEST/$f"
  else
    missing+=("$f")
  fi
done

# hits.png and hits.json are conditional -- a zero-hits run legitimately
# has no PNG. Everything else is required for a run to be archivable at
# all. Distinguishing these two cases keeps zero-hit runs archivable while
# still flagging genuine gaps.
required_hard=(report.md run_meta.json hits_clean.csv hits_clean.json)
hard_missing=()
for f in "${REQUIRED[@]}"; do
  case " ${required_hard[*]} " in *" $f "*) [ -f "$WORK/$f" ] || hard_missing+=("$f");; esac
done
if [ "${#hard_missing[@]}" -gt 0 ]; then
  echo "archive: missing required files ${hard_missing[*]}" >&2
  exit 1
fi
if [ "${#missing[@]}" -gt 0 ]; then
  echo "archive: note -- optional files missing (zero-hits run?): ${missing[*]}"
fi

echo "archive: wrote $(ls "$DEST" | wc -l) files to $DEST"
echo "         commit and push $DEST on the claude/screener-runs branch."
