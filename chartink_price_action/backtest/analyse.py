"""Two questions the headline table cannot answer:

1. STOP SURVIVABILITY. The Friday report set stops 2.4-2.5% below entry. If the
   median trade routinely draws down more than that before working, those stops
   are noise-triggered and the stated R:R is fiction.
2. REGIME. A single bull run inside the sample can manufacture an edge that
   looks statistically solid but is really one market, once.
"""
import os, sys, json, datetime
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E

B = os.path.dirname(os.path.abspath(__file__))
trades = json.load(open(os.path.join(B, 'trades.json')))
COST = 0.30

print(f'{len(trades)} trades\n')

# ---------------------------------------------------------- 1. stop survival
print('=== STOP SURVIVABILITY (20-day holding window) ===')
print('For each stop distance: how often price hits the stop at some point,')
print('and how many of those trades would still have FINISHED positive.\n')
print(f"{'stop':>6} {'stopped out':>12} {'of those, +ve at 20d':>22} {'noise-stopped':>15}")
rows = [t for t in trades if t.get('mae_20d') is not None and t.get('ret_20d') is not None]
for stop in (2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0):
    hit = [t for t in rows if t['mae_20d'] <= -stop]
    saved = [t for t in hit if t['ret_20d'] > 0]
    pct = 100 * len(hit) / len(rows)
    rescue = 100 * len(saved) / len(hit) if hit else 0
    print(f'{stop:5.1f}% {pct:11.1f}% {rescue:21.1f}% {100*len(saved)/len(rows):14.1f}%')

print('\n"Noise-stopped" = share of ALL trades that would have been stopped out')
print('yet finished the 20-day window profitable. That is edge the stop destroys.\n')

# ---------------------------------------------------------- 2. MAE detail
print('=== HOW FAR TRADES GO AGAINST YOU (MAE percentiles) ===')
print(f"{'horizon':>8} " + ' '.join(f'{f"p{p}":>7}' for p in (10, 25, 50, 75, 90)))
for h in E.HORIZONS:
    v = np.array([t[f'mae_{h}'] for t in trades if t.get(f'mae_{h}') is not None])
    if not len(v): continue
    print(f'{h:>8} ' + ' '.join(f'{np.percentile(v,p):+7.2f}' for p in (10, 25, 50, 75, 90)))

# ---------------------------------------------------------- 3. regime
print('\n=== 20-DAY EXCESS RETURN BY CALENDAR PERIOD ===')
print(f"{'period':>9} {'n':>6} {'gross':>8} {'bench':>8} {'excess':>8} {'hit%':>7}")
by = {}
for t in trades:
    if t.get('exc_20d') is None: continue
    d = datetime.date.fromisoformat(t['signal_date'])
    by.setdefault(f'{d.year}H{1 if d.month<=6 else 2}', []).append(t)
for k in sorted(by):
    g = by[k]
    r = np.array([x['ret_20d'] for x in g])
    b = np.array([x['bench_20d'] for x in g if x.get('bench_20d') is not None])
    e = np.array([x['exc_20d'] for x in g])
    print(f'{k:>9} {len(g):>6} {r.mean():+7.2f}% {b.mean():+7.2f}% {e.mean():+7.2f}% {100*(r>0).mean():6.1f}%')

# ------------------------------------------------- 4. stop+target expectancy
print('\n=== STOP-AND-TARGET EXPECTANCY (which order they were hit is unknown) ===')
print('Optimistic: if both stop and target were touched, we credit the TARGET.')
print('Pessimistic: we credit the STOP. Truth is between; if the pessimistic')
print('column is negative the setup depends entirely on intrabar sequencing.\n')
print(f"{'stop':>5} {'target':>7} {'n':>6} {'optimistic':>12} {'pessimistic':>13}")
for stop, tgt in ((2.5, 5.0), (3.0, 6.0), (4.0, 8.0), (5.0, 10.0), (2.5, 7.5), (5.0, 15.0)):
    n = opt = pes = 0
    for t in rows:
        mae, mfe, ret = t['mae_20d'], t['mfe_20d'], t['ret_20d']
        if t.get('mfe_20d') is None: continue
        n += 1
        s_hit, t_hit = mae <= -stop, mfe >= tgt
        if t_hit and not s_hit: opt += tgt; pes += tgt
        elif s_hit and not t_hit: opt += -stop; pes += -stop
        elif s_hit and t_hit:     opt += tgt; pes += -stop
        else:                     opt += ret; pes += ret
    if n:
        print(f'{stop:4.1f}% {tgt:6.1f}% {n:>6} {opt/n-COST:+11.2f}% {pes/n-COST:+12.2f}%')
