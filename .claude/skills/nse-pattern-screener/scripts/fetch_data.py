"""Resumable batched OHLCV fetch from yfinance for NSE symbols.

Writes one parquet per batch into --out-dir and SKIPS batches already on disk,
so re-running the same command continues where a timeout left off. A full
~2300-symbol hourly pull takes 15-40 minutes and will not finish in one
command invocation -- that is expected, just run it again.

yfinance intraday history limits: 1h and below -> ~60 days; 1m -> 7 days.

Usage:
    python fetch_data.py --universe universe.txt --period 60d --interval 1h --out-dir parts
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
import yfinance as yf

COLS = ["symbol", "ts", "open", "high", "low", "close", "volume"]


def fetch(universe: str, period: str, interval: str, out_dir: str,
          batch: int, suffix: str, min_bars: int) -> None:
    syms = [s.strip() for s in open(universe) if s.strip()]
    tickers = [s + suffix for s in syms]
    os.makedirs(out_dir, exist_ok=True)

    done = 0
    for i in range(0, len(tickers), batch):
        part = os.path.join(out_dir, f"p{i:05d}.parquet")
        if os.path.exists(part):
            done += 1
            continue

        chunk = tickers[i:i + batch]
        d = None
        for _ in range(2):
            try:
                d = yf.download(chunk, period=period, interval=interval,
                                group_by="ticker", threads=True,
                                progress=False, auto_adjust=False)
                break
            except Exception:
                time.sleep(3)
        if d is None:
            print(f"FAIL batch {i}", flush=True)
            continue

        rows = []
        for t in chunk:
            try:
                sub = d[t].dropna(subset=["Close"])
            except Exception:
                continue
            if len(sub) < min_bars:
                continue
            sub = sub.reset_index()
            sub.columns = [str(c).lower() for c in sub.columns]
            tc = "datetime" if "datetime" in sub.columns else sub.columns[0]
            rows.append(pd.DataFrame({
                "symbol": t[: -len(suffix)], "ts": sub[tc],
                "open": sub["open"], "high": sub["high"], "low": sub["low"],
                "close": sub["close"], "volume": sub["volume"]}))

        if rows:
            pd.concat(rows, ignore_index=True).to_parquet(part, index=False)
        print(f"{min(i + batch, len(tickers))}/{len(tickers)}", flush=True)
        time.sleep(0.4)

    n_parts = len(glob.glob(os.path.join(out_dir, "*.parquet")))
    print(f"DONE ({n_parts} batch files in {out_dir}; {done} were already present)")


def merge(parts_dir: str, out: str, tz: str) -> None:
    files = sorted(glob.glob(os.path.join(parts_dir, "*.parquet")))
    if not files:
        raise SystemExit(f"no parquet files in {parts_dir}")
    d = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    d["ts"] = (pd.to_datetime(d["ts"], utc=True)
               .dt.tz_convert(tz).dt.tz_localize(None))
    d = d[COLS].sort_values(["symbol", "ts"]).reset_index(drop=True)
    d.to_parquet(out, index=False)
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
    ap.add_argument("--merge", default=None, help="merge this parts dir instead of fetching")
    ap.add_argument("--out", default="all.parquet")
    ap.add_argument("--tz", default="Asia/Kolkata")
    args = ap.parse_args()

    if args.merge:
        merge(args.merge, args.out, args.tz)
    else:
        if not args.universe:
            raise SystemExit("--universe required when fetching")
        fetch(args.universe, args.period, args.interval, args.out_dir,
              args.batch, args.suffix, args.min_bars)


if __name__ == "__main__":
    main()
