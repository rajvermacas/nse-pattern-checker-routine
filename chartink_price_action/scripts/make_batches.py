import json,os
BASE=os.path.dirname(os.path.abspath(__file__))
M=json.load(open(os.path.join(BASE,'metrics.json')))
scr={r['nsecode']:r for r in json.load(open(os.path.join(BASE,'screener_rows.json')))}
syms=sorted(M.keys())
NB=9
os.makedirs(os.path.join(BASE,'batches'),exist_ok=True)
batches=[[] for _ in range(NB)]
for i,s in enumerate(syms): batches[i%NB].append(s)
for bi,b in enumerate(batches,1):
    pack={s:dict(M[s], company=scr.get(s,{}).get('name'), chartink_close=scr.get(s,{}).get('close'), chartink_pct_chg=scr.get(s,{}).get('per_chg')) for s in b}
    p=os.path.join(BASE,'batches',f'batch{bi}.json')
    json.dump(pack,open(p,'w'),indent=1)
    print(bi,len(b),os.path.getsize(p)//1024,'KB',' '.join(b))
