"""Layer 1 (screen baseline) + Layer 2 (mechanical setup filters).

Statistics note: screen entries cluster heavily on market-wide up days, so
trades are NOT independent draws. A naive per-trade t-stat treats 4,000
overlapping trades as 4,000 observations and will call almost anything
significant. Everything below is therefore clustered BY SIGNAL DATE: reduce to
one mean excess return per date, then test across dates. That is the number
that survives contact with reality.
"""
import os, sys, json, datetime
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E

B = os.path.dirname(os.path.abspath(__file__))
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
COST_RT = 0.30          # % round trip: STT 0.2 + brokerage/charges ~0.05 + slippage
SETUPS = ['flat_base_breakout', 'tight_flag', 'pullback_ema50', 'coil_near_high', 'any_setup']

# ------------------------------------------------------------------ benchmark
z = np.load(os.path.join(B, 'BENCH.npz'))
BT = z['t'].astype(np.int64); BO = z['o'].astype(float); BC = z['c'].astype(float)
BDATE = np.array([datetime.datetime.fromtimestamp(int(t), IST).date() for t in BT])
B_FIRST = {}
for i in range(len(BDATE) - 1, -1, -1):
    B_FIRST[BDATE[i]] = i

def bench_ret(entry_date, nbars):
    j = B_FIRST.get(entry_date)
    if j is None: return None
    k = min(j + nbars, len(BC) - 1)
    if k <= j: return None
    return float(BC[k] / BO[j] - 1) * 100

# ------------------------------------------------------------------ collect
def main():
    shares = json.load(open(os.path.join(B, 'shares.json')))
    syms = sorted(f[:-4] for f in os.listdir(os.path.join(B, 'bars')) if f.endswith('.npz')
                  and f != 'BENCH.npz')
    trades, skipped = [], 0
    for s in syms:
        try:
            S = E.load(s)
        except Exception:
            skipped += 1; continue
        rec = shares.get(s) or {}
        m = E.screen_mask(S, rec.get('shares'), always_eligible=not rec.get('shares'))
        if m is None:
            skipped += 1; continue
        trades.extend(E.build_trades(s, S, m))
    print(f'{len(syms)} symbols, {skipped} skipped, {len(trades)} trades', flush=True)

    for t in trades:
        for name, nb in E.HORIZONS.items():
            b = bench_ret(datetime.date.fromisoformat(t['entry_date']), nb)
            t[f'bench_{name}'] = b
            r = t.get(f'ret_{name}')
            t[f'exc_{name}'] = (r - b) if (r is not None and b is not None) else None
    json.dump(trades, open(os.path.join(B, 'trades.json'), 'w'))
    return trades

def clustered_t(by_date):
    """t-stat across per-date means (each date = one observation)."""
    v = np.array([x for x in by_date if x is not None and np.isfinite(x)])
    if len(v) < 5: return None, None, len(v)
    se = v.std(ddof=1) / np.sqrt(len(v))
    return (float(v.mean()), float(v.mean() / se) if se > 0 else None, len(v))

def stats(trades, horizon, key_ret='ret', label=''):
    rk, ek = f'{key_ret}_{horizon}', f'exc_{horizon}'
    rows = [t for t in trades if t.get(rk) is not None]
    if not rows: return None
    r = np.array([t[rk] for t in rows])
    exc = np.array([t[ek] for t in rows if t.get(ek) is not None])
    net = r - COST_RT
    bydate = {}
    for t in rows:
        if t.get(ek) is not None:
            bydate.setdefault(t['signal_date'], []).append(t[ek])
    dmeans = [float(np.mean(v)) for v in bydate.values()]
    m, tstat, ndates = clustered_t(dmeans)
    mae = np.array([t[f'mae_{horizon}'] for t in rows if t.get(f'mae_{horizon}') is not None])
    mfe = np.array([t[f'mfe_{horizon}'] for t in rows if t.get(f'mfe_{horizon}') is not None])
    return dict(label=label, horizon=horizon, n=len(rows), n_dates=ndates,
        mean=float(r.mean()), median=float(np.median(r)),
        hit=float((r > 0).mean() * 100),
        net_mean=float(net.mean()), net_hit=float((net > 0).mean() * 100),
        bench_mean=float(np.mean([t[f'bench_{horizon}'] for t in rows
                                  if t.get(f'bench_{horizon}') is not None])),
        excess_mean=float(exc.mean()) if len(exc) else None,
        excess_hit=float((exc > 0).mean() * 100) if len(exc) else None,
        excess_t_clustered=tstat,
        mae_p50=float(np.percentile(mae, 50)) if len(mae) else None,
        mae_p25=float(np.percentile(mae, 25)) if len(mae) else None,
        mae_p10=float(np.percentile(mae, 10)) if len(mae) else None,
        mfe_p50=float(np.percentile(mfe, 50)) if len(mfe) else None,
        mfe_p90=float(np.percentile(mfe, 90)) if len(mfe) else None)

if __name__ == '__main__':
    trades = main()
    out = {'cost_round_trip_pct': COST_RT, 'layer1': [], 'layer2': []}
    for h in E.HORIZONS:
        s = stats(trades, h, label='ALL screen entries')
        if s: out['layer1'].append(s)
    for su in SETUPS:
        sub = [t for t in trades if t.get(f'su_{su}')]
        for h in E.HORIZONS:
            s = stats(sub, h, label=su)
            if s: out['layer2'].append(s)
    json.dump(out, open(os.path.join(B, 'results.json'), 'w'), indent=1)

    def line(s):
        ex = f"{s['excess_mean']:+6.2f}" if s['excess_mean'] is not None else '   n/a'
        tt = f"{s['excess_t_clustered']:+5.2f}" if s['excess_t_clustered'] is not None else '  n/a'
        return (f"{s['label'][:22]:22s} {s['horizon']:>4s} n={s['n']:>5d} "
                f"gross={s['mean']:+6.2f}% net={s['net_mean']:+6.2f}% hit={s['hit']:5.1f}% "
                f"bench={s['bench_mean']:+6.2f}% excess={ex}% t={tt} "
                f"MAEp50={s['mae_p50']:+6.2f}%")
    print('\n=== LAYER 1: buy every fresh screen entry ===')
    for s in out['layer1']: print(line(s))
    print('\n=== LAYER 2: screen AND mechanical setup ===')
    for s in out['layer2']: print(line(s))
