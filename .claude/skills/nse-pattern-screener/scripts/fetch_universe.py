"""Fetch the NSE symbol universe from NSE's own archives.

Series meanings:
    EQ - rolling settlement, intraday allowed. The tradable universe.
    BE - trade-to-trade, delivery only. No intraday.
    BZ - surveillance / suspended.

Usage:
    python fetch_universe.py --series EQ --out universe.txt
    python fetch_universe.py --index nifty500 --out universe.txt
"""

from __future__ import annotations

import argparse
import io
import sys

import pandas as pd
import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

EQUITY_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
INDEX_URLS = {
    "nifty50": "https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv",
    "nifty100": "https://nsearchives.nseindia.com/content/indices/ind_nifty100list.csv",
    "nifty200": "https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv",
    "nifty500": "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv",
    "midcap150": "https://nsearchives.nseindia.com/content/indices/ind_niftymidcap150list.csv",
    "smallcap250": "https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap250list.csv",
}


def _get(url: str) -> pd.DataFrame:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = [c.strip() for c in df.columns]
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="EQ",
                    help="comma list: EQ, BE, BZ, or ALL")
    ap.add_argument("--index", default=None, help=f"one of {list(INDEX_URLS)}")
    ap.add_argument("--out", default="universe.txt")
    args = ap.parse_args()

    if args.index:
        key = args.index.lower().replace(" ", "").replace("-", "")
        if key not in INDEX_URLS:
            sys.exit(f"unknown index {args.index}; choose from {list(INDEX_URLS)}")
        df = _get(INDEX_URLS[key])
        syms = sorted(df["Symbol"].astype(str).str.strip().unique())
        label = args.index
    else:
        df = _get(EQUITY_URL)
        df["SERIES"] = df["SERIES"].astype(str).str.strip()
        counts = df["SERIES"].value_counts().to_dict()
        print("series breakdown:", counts)
        if args.series.upper() == "ALL":
            keep = df
        else:
            wanted = [s.strip().upper() for s in args.series.split(",")]
            keep = df[df["SERIES"].isin(wanted)]
        syms = sorted(keep["SYMBOL"].astype(str).str.strip().unique())
        label = args.series

    with open(args.out, "w") as f:
        f.write("\n".join(syms))
    print(f"{len(syms)} symbols ({label}) -> {args.out}")


if __name__ == "__main__":
    main()
