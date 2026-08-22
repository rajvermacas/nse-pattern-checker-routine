#!/usr/bin/env bash
# Deterministic archive of one screener run into runs/YYYY-MM-DD/HHMM-UNIVERSE/
# on the current branch. Usage:
#
#     bash archive_run.sh
#
# Reads from $WORK (default: work) and expects the deliverables run_screener.sh
# produced there. Writes a clean, self-contained directory:
#
#     report.md run_meta.json
#     hits.png hits_clean.csv hits_clean.json            (rally_cup)
#     dip_hits.png dip_hits_clean.csv dip_hits_clean.json (momentum_dip)
#     shape_rejects.json                                  (rally_cup, if any)
#
# Which of those are REQUIRED depends on which screens ran: the file set is
# derived from `patterns_run` in run_meta.json rather than hardcoded, so
# archiving a single-pattern run does not fail on the other pattern's missing
# files, and a two-pattern run cannot quietly archive half of itself.
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
read -r DATE HHMM UNIVERSE PATTERNS < <(python - <<PY
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
# Older run_meta files predate multi-pattern runs; they are rally_cup only.
pats = m.get("patterns_run") or ["rally_cup"]
pats = [p for p in pats if p in ("rally_cup", "momentum_dip")]
print(date, f"{hh}{mm}", uni, ",".join(pats) or "rally_cup")
PY
)

DEST="runs/$DATE/$HHMM-$UNIVERSE"
echo "archive: -> $DEST"

# Clear the slot before writing. rm -rf is safe here because the path is
# fully derived from run_meta above and always begins with runs/, and the
# subsequent writes recreate every expected file.
rm -rf "$DEST"
mkdir -p "$DEST"

# Required and optional file sets, per pattern that actually ran. A pattern's
# clean json+csv are hard requirements (their absence means the stage did not
# finish); its PNG is optional, because a zero-hit pattern legitimately has no
# chart to draw.
REQUIRED=(report.md run_meta.json)
OPTIONAL=()
case ",$PATTERNS," in
  *,rally_cup,*)
    REQUIRED+=(hits_clean.csv hits_clean.json)
    OPTIONAL+=(hits.png hits.json shape_rejects.json diagnose.txt)
    ;;
esac
case ",$PATTERNS," in
  *,momentum_dip,*)
    REQUIRED+=(dip_hits_clean.csv dip_hits_clean.json)
    OPTIONAL+=(dip_hits.png dip_hits.json dip_diagnose.txt)
    ;;
esac
echo "archive: patterns $PATTERNS"

hard_missing=()
for f in "${REQUIRED[@]}"; do
  if [ -f "$WORK/$f" ]; then
    cp "$WORK/$f" "$DEST/$f"
  else
    hard_missing+=("$f")
  fi
done
missing=()
for f in "${OPTIONAL[@]}"; do
  if [ -f "$WORK/$f" ]; then
    cp "$WORK/$f" "$DEST/$f"
  else
    missing+=("$f")
  fi
done

if [ "${#hard_missing[@]}" -gt 0 ]; then
  echo "archive: missing required files ${hard_missing[*]}" >&2
  exit 1
fi
if [ "${#missing[@]}" -gt 0 ]; then
  echo "archive: note -- optional files absent (zero-hit pattern?): ${missing[*]}"
fi

echo "archive: wrote $(ls "$DEST" | wc -l) files to $DEST"
echo "         commit and push $DEST on the claude/screener-runs branch."
