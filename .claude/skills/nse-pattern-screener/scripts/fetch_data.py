"""Resumable batched OHLCV fetch from yfinance for NSE symbols.

Writes one parquet per batch into --out-dir and SKIPS batches already on disk,
so re-running the same command continues where a timeout left off. A full
~2300-symbol hourly pull takes 15-40 minutes serially and will not finish in
one command invocation -- that is expected, just run it again.

Because parts are written per BATCH, a batch that returns only some of its
symbols (rate limiting does exactly this) still leaves a part file and would be
skipped forever by the resume check. After the batch pass, a gap-fill stage
therefore works at SYMBOL granularity: it recomputes who is missing, backs off
to let the rate limiter drain, and refetches just those symbols into g*.parquet
files. --gap-rounds controls how many times (0 disables). Without it, transient
429s get permanently mislabelled "no data".

yfinance intraday history limits: 1h and below -> ~60 days; 1m -> 7 days.

Speed: yfinance issues one Yahoo chart request PER SYMBOL (there is no batched
OHLCV endpoint); a symbol list is just parallelised by yfinance's own thread
pool. --workers N sets that pool (threads=N). Default 1 == serial. MEASURED on
2026-08-20 with the proxy-required requests.Session: workers=6 gave 15.8s vs
19.0s serial on 200 symbols (~17%), and workers=10 vs 1 at batch=200 gave
14.96s vs 15.56s (indistinguishable). The custom Session's per-host connection
pool lock serialises what threads=N tries to parallelise, so on this transport
the lever is mostly dead. Kept anyway: it does no harm, auto-degrades to serial
after 2 consecutive bad batches, and becomes useful if the transport ever
changes (e.g. curl_cffi works through the proxy again).

Observability: every dropped symbol is counted and categorised, every caught
exception is logged with type + message + the batch it hit, and each stage ends
with a reconciliation line (universe N -> data M -> dropped by reason) that logs
at WARNING/ERROR when anything is lost. A machine-readable fetch_report.json is
written next to the parts dir. Nothing a symbol's absence could hide stays
silent. Export SCREENER_LOG=DEBUG for per-drop examples and tracebacks.

Usage:
    python fetch_data.py --universe universe.txt --period 60d --interval 1h --out-dir parts
    python fetch_data.py --universe universe.txt --workers 6 --out-dir parts
    python fetch_data.py --merge parts --out all.parquet
"""

from __future__ import annotations

import argparse
import glob
import os
import time
import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import requests
import yfinance as yf

import obs

COLS = ["symbol", "ts", "open", "high", "low", "close", "volume"]
LOG = obs.get_logger("fetch")

# yfinance defaults to curl_cffi, which impersonates a browser TLS fingerprint.
# Behind an HTTPS-inspecting egress proxy that handshake is reset (curl error 35
# / SSLError), so every ticker fails and the run merges zero parts. A plain
# requests session traverses the proxy, but Yahoo answers a cold session with
# HTTP 429 -- it wants the cookies a browser picks up first. Priming one quote
# page yields cookies that make the chart endpoint return 200.
# Kept in step with fetch_universe.py's UA. Yahoo does not currently gate on
# Chrome major version the way NSE does (Chrome/126 was fetching fine), but a
# stale UA is a cheap thing to get wrong and an expensive one to diagnose --
# see the version table in fetch_universe.py.
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36")


def make_session(suffix: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": _UA, "Accept-Language": "en-US,en;q=0.9"})
    try:
        r = s.get(f"https://finance.yahoo.com/quote/RELIANCE{suffix}/", timeout=25)
        LOG.debug("primed session: HTTP %s, %d cookies",
                  r.status_code, len(s.cookies))
    except requests.RequestException as e:
        # Not fatal -- an uncookied session may still work or get re-primed on
        # the first empty batch -- but it is a leading indicator of 429s, so it
        # must be visible rather than a bare one-liner.
        obs.log_exception(LOG, "session prime failed (continuing uncookied)", e)
    return s


def _extract(d: pd.DataFrame, chunk: list[str], suffix: str, min_bars: int,
             drops: obs.Drops) -> list[pd.DataFrame]:
    """Pull each ticker out of a multi-ticker frame, categorising every drop."""
    rows = []
    for t in chunk:
        try:
            sub = d[t].dropna(subset=["Close"])
        except KeyError:
            # Ticker absent from the response entirely -- usually Yahoo has no
            # data for it (delisted, wrong .NS mapping). Expected but counted.
            drops.add("missing_from_response", t)
            continue
        except Exception as e:
            # A parse/shape error is NOT expected and must not read as "no data".
            obs.log_exception(LOG, f"extract {t}", e)
            drops.add("parse_error", t)
            continue
        if len(sub) == 0:
            # The column exists but every Close is NaN. yfinance materialises
            # the ticker even when its download FAILED (rate limit, transport),
            # so this is a fetch failure wearing the costume of "no data" --
            # and it is RECOVERABLE, unlike a genuinely short history. Counting
            # it as too_few_bars is what let 107 rate-limited symbols (incl.
            # SHRIRAMFIN, a Nifty 50 name) get written off as unavailable.
            drops.add("no_data_returned", t)
            continue
        if len(sub) < min_bars:
            drops.add("too_few_bars", f"{t}:{len(sub)}<{min_bars}")
            continue
        sub = sub.reset_index()
        sub.columns = [str(c).lower() for c in sub.columns]
        tc = "datetime" if "datetime" in sub.columns else sub.columns[0]
        rows.append(pd.DataFrame({
            "symbol": t[: -len(suffix)], "ts": sub[tc],
            "open": sub["open"], "high": sub["high"], "low": sub["low"],
            "close": sub["close"], "volume": sub["volume"]}))
    return rows


def fetch(universe: str, period: str, interval: str, out_dir: str,
          batch: int, suffix: str, min_bars: int, workers: int,
          gap_rounds: int = 2) -> dict:
    syms = [s.strip() for s in open(universe) if s.strip()]
    tickers = [s + suffix for s in syms]
    os.makedirs(out_dir, exist_ok=True)
    session = make_session(suffix)

    drops = obs.Drops(LOG, "fetch")     # per-symbol drops, this invocation
    n_batches = (len(tickers) + batch - 1) // batch
    LOG.info("fetch start: %d symbols, %d batches of %d, workers=%d",
             len(tickers), n_batches, batch, workers)

    active_workers = workers
    consecutive_bad = 0
    done = failed_batches = kept = 0

    for bi, i in enumerate(range(0, len(tickers), batch)):
        part = os.path.join(out_dir, f"p{i:05d}.parquet")
        if os.path.exists(part):
            done += 1
            continue

        chunk = tickers[i:i + batch]
        span = f"batch {bi + 1}/{n_batches} [{chunk[0]}..{chunk[-1]}]"
        d = None
        last_reason = "unknown"
        for attempt in range(2):
            try:
                # threads=int -> yfinance's own pool (thread-safe within one
                # download call; guarded by its ctx.lock). 1 == serial.
                d = yf.download(chunk, period=period, interval=interval,
                                group_by="ticker", threads=active_workers,
                                progress=False, auto_adjust=False,
                                session=session)
                if d is not None and not d.dropna(how="all").empty:
                    break
                # All-empty frame == Yahoo returned nothing, usually stale
                # cookies / 429. Re-prime and retry once.
                last_reason = "empty_frame(429?)"
                LOG.warning("%s: empty frame (attempt %d), re-priming session",
                            span, attempt + 1)
                session = make_session(suffix)
                d = None
            except Exception as e:
                last_reason = obs.exc_line(e)
                obs.log_exception(LOG, f"{span} download (attempt {attempt + 1})", e)
                session = make_session(suffix)
                time.sleep(3)

        if d is None:
            failed_batches += 1
            consecutive_bad += 1
            drops.add("batch_failed", f"{span} ({last_reason})")
            LOG.error("%s FAILED after 2 attempts: %s (%d symbols lost)",
                      span, last_reason, len(chunk))
            # A run of bad batches under concurrency == we are being rate
            # limited. Fall back to serial for the rest rather than shipping a
            # thin scan; make the decision loud.
            if active_workers > 1 and consecutive_bad >= 2:
                LOG.error("2 consecutive bad batches at workers=%d -> "
                          "DEGRADING to serial for the remainder", active_workers)
                active_workers = 1
            continue

        consecutive_bad = 0
        rows = _extract(d, chunk, suffix, min_bars, drops)
        if rows:
            merged = pd.concat(rows, ignore_index=True)
            merged.to_parquet(part, index=False)
            kept += merged["symbol"].nunique()
        else:
            LOG.warning("%s: 0 usable symbols after extract", span)
        LOG.info("%s: wrote %d/%d symbols (%d/%d)", span, len(rows), len(chunk),
                 min(i + batch, len(tickers)), len(tickers))
        time.sleep(0.4)

    if failed_batches:
        LOG.error("%d/%d batches failed outright this pass", failed_batches, n_batches)

    # ---------------------------------------------------------- gap-fill
    # The part files are written per BATCH, so a batch that returned 25 of 40
    # symbols still leaves a p*.parquet on disk and is skipped forever by the
    # resume check -- the outer retry loop can never reach those 15 symbols.
    # Rate limiting produces exactly that shape. So after the main pass, work
    # at SYMBOL granularity: recompute who is actually missing, back off to let
    # the rate limiter drain, and refetch just them into their own part files.
    kept += _gap_fill(syms, suffix, out_dir, period, interval, batch, min_bars,
                      gap_rounds, drops)

    # Reconciliation across everything on disk -- the real coverage number, not
    # just this invocation's. This is what turns "a symbol vanished" into a
    # counted, named gap.
    on_disk = _symbols_on_disk(out_dir)
    universe = {s for s in syms}
    missing = sorted(universe - on_disk)
    report = {
        "universe": len(universe),
        "symbols_on_disk": len(on_disk),
        "coverage_pct": round(100 * len(on_disk) / max(len(universe), 1), 1),
        "missing_count": len(missing),
        "missing_sample": missing[:25],
        "batches_total": n_batches,
        "batches_skipped_present": done,
        "batches_failed_this_pass": failed_batches,
        "workers_requested": workers,
        "workers_ended": active_workers,
        "degraded_to_serial": active_workers != workers,
        "gap_fill_rounds": gap_rounds,
        "drops_this_pass": drops.report(kept, len(tickers)),
    }
    report_path = os.path.join(os.path.dirname(out_dir) or ".", "fetch_report.json")
    obs.write_report(report_path, report)

    lvl = LOG.warning if missing else LOG.info
    lvl("coverage: %d/%d on disk (%.1f%%), %d missing%s",
        len(on_disk), len(universe), report["coverage_pct"], len(missing),
        f" e.g. {missing[:10]}" if missing else "")
    n_parts = len(glob.glob(os.path.join(out_dir, "*.parquet")))
    LOG.info("DONE (%d batch files in %s; %d already present; report -> %s)",
             n_parts, out_dir, done, report_path)
    return report


def _gap_fill(syms: list[str], suffix: str, out_dir: str, period: str,
              interval: str, batch: int, min_bars: int, rounds: int,
              drops: obs.Drops) -> int:
    """Refetch symbols still missing after the batch pass, at symbol granularity.

    Rate limiting is transient, so the fix is to wait and ask again for exactly
    the symbols we lack -- not to re-walk batches that are already complete.
    Backoff grows per round because a rate limiter that just fired needs longer
    than a network blip. Returns the number of symbols recovered.
    """
    recovered = 0
    for rnd in range(1, rounds + 1):
        missing = sorted(set(syms) - _symbols_on_disk(out_dir))
        if not missing:
            LOG.info("gap-fill: nothing missing, universe complete")
            return recovered
        wait = 30 * rnd
        LOG.warning("gap-fill round %d/%d: %d symbols still missing; "
                    "waiting %ds for the rate limiter to drain",
                    rnd, rounds, len(missing), wait)
        time.sleep(wait)

        session = make_session(suffix)
        before = len(_symbols_on_disk(out_dir))
        for j in range(0, len(missing), batch):
            part = os.path.join(out_dir, f"g{rnd:02d}_{j:05d}.parquet")
            if os.path.exists(part):
                continue
            chunk = [s + suffix for s in missing[j:j + batch]]
            try:
                d = yf.download(chunk, period=period, interval=interval,
                                group_by="ticker", threads=1, progress=False,
                                auto_adjust=False, session=session)
            except Exception as e:
                obs.log_exception(LOG, f"gap-fill round {rnd} chunk {j}", e)
                session = make_session(suffix)
                time.sleep(5)
                continue
            if d is None or d.dropna(how="all").empty:
                LOG.warning("gap-fill round %d chunk %d: still empty", rnd, j)
                session = make_session(suffix)
                continue
            # Drops here are counted separately: a symbol missing after a
            # dedicated retry is far more likely to be genuinely absent from
            # Yahoo than transiently throttled.
            rows = _extract(d, chunk, suffix, min_bars, obs.Drops(LOG, f"gapfill-r{rnd}"))
            if rows:
                pd.concat(rows, ignore_index=True).to_parquet(part, index=False)
            time.sleep(1.0)

        gained = len(_symbols_on_disk(out_dir)) - before
        recovered += gained
        LOG.warning("gap-fill round %d recovered %d symbols", rnd, gained)
        if gained == 0:
            LOG.warning("gap-fill round %d recovered nothing -- remaining "
                        "symbols are probably genuinely absent from Yahoo, "
                        "not throttled; stopping early", rnd)
            break
    return recovered


def _symbols_on_disk(out_dir: str) -> set[str]:
    got: set[str] = set()
    for f in glob.glob(os.path.join(out_dir, "*.parquet")):
        try:
            got |= set(pd.read_parquet(f, columns=["symbol"])["symbol"].unique())
        except Exception as e:
            obs.log_exception(LOG, f"reading {f} for reconciliation", e)
    return got


def merge(parts_dir: str, out: str, tz: str) -> None:
    files = sorted(glob.glob(os.path.join(parts_dir, "*.parquet")))
    if not files:
        raise SystemExit(f"no parquet files in {parts_dir}")
    frames, bad = [], 0
    for f in files:
        try:
            frames.append(pd.read_parquet(f))
        except Exception as e:
            bad += 1
            obs.log_exception(LOG, f"merge: skipping unreadable {f}", e)
    if not frames:
        raise SystemExit(f"every parquet in {parts_dir} was unreadable")
    if bad:
        LOG.error("merge: %d/%d part files were unreadable and skipped",
                  bad, len(files))
    d = pd.concat(frames, ignore_index=True)
    d["ts"] = (pd.to_datetime(d["ts"], utc=True)
               .dt.tz_convert(tz).dt.tz_localize(None))
    d = d[COLS].sort_values(["symbol", "ts"]).reset_index(drop=True)
    d.to_parquet(out, index=False)
    LOG.info("merged rows %d  symbols %d  last ts %s -> %s",
             len(d), d.symbol.nunique(), d.ts.max(), out)
    print(f"rows {len(d)}  symbols {d.symbol.nunique()}  last ts {d.ts.max()}")
    print(f"-> {out}")
    print("NOTE: drop the in-progress bar before screening if the market is open.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--universe")
    ap.add_argument("--period", default="60d")
    ap.add_argument("--interval", default="1h")
    ap.add_argument("--out-dir", default="parts")
    ap.add_argument("--batch", type=int, default=40)
    ap.add_argument("--suffix", default=".NS", help=".NS for NSE, .BO for BSE")
    ap.add_argument("--min-bars", type=int, default=60)
    ap.add_argument("--workers", type=int, default=1,
                    help="yfinance thread pool size; 1 = serial (safe default). "
                         "Auto-degrades to 1 on repeated rate-limit failures.")
    ap.add_argument("--gap-rounds", type=int, default=2,
                    help="retry rounds for symbols still missing after the "
                         "batch pass (rate-limit recovery); 0 disables")
    ap.add_argument("--merge", default=None, help="merge this parts dir instead of fetching")
    ap.add_argument("--out", default="all.parquet")
    ap.add_argument("--tz", default="Asia/Kolkata")
    args = ap.parse_args()

    if args.workers < 1:
        raise SystemExit("--workers must be >= 1")

    if args.merge:
        merge(args.merge, args.out, args.tz)
    else:
        if not args.universe:
            raise SystemExit("--universe required when fetching")
        fetch(args.universe, args.period, args.interval, args.out_dir,
              args.batch, args.suffix, args.min_bars, args.workers,
              args.gap_rounds)


if __name__ == "__main__":
    main()
