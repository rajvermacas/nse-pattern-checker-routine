import requests, time, json, os
B=os.path.dirname(os.path.abspath(__file__))
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
s=requests.Session(); s.headers.update({'User-Agent':UA,'Accept':'*/*'})
try: s.get('https://fc.yahoo.com',timeout=15)
except Exception: pass
crumb=s.get('https://query2.finance.yahoo.com/v1/test/getcrumb',timeout=15).text.strip()
syms=open(f'{B}/universe.txt').read().split()
out={}
for i in range(0,len(syms),50):
    chunk=syms[i:i+50]
    q=','.join(x+'.NS' for x in chunk)
    for attempt in range(4):
        try:
            r=s.get('https://query1.finance.yahoo.com/v7/finance/quote',params={'symbols':q,'crumb':crumb},timeout=40)
            if r.status_code==200:
                for x in r.json()['quoteResponse']['result']:
                    out[x['symbol'].replace('.NS','')]={'mktcap':x.get('marketCap'),'shares':x.get('sharesOutstanding'),'price':x.get('regularMarketPrice')}
                break
            time.sleep(3+2*attempt)
        except Exception:
            time.sleep(3+2*attempt)
    time.sleep(1.0)
    print(f'{min(i+50,len(syms))}/{len(syms)} -> {len(out)} resolved', flush=True)
json.dump(out,open(f'{B}/shares.json','w'))
miss=[x for x in syms if x not in out or not out[x].get('shares')]
print('resolved',len(out),'missing shares',len(miss)); print(' '.join(miss[:40]))
