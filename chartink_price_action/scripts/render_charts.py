import json,os,datetime,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

BASE=os.path.dirname(os.path.abspath(__file__))
D=os.path.join(BASE,'data'); C=os.path.join(BASE,'charts'); os.makedirs(C,exist_ok=True)
IST=datetime.timezone(datetime.timedelta(hours=5,minutes=30))

def ema(a,n):
    a=np.asarray(a,float); k=2/(n+1); o=np.empty_like(a); o[0]=a[0]
    for i in range(1,len(a)): o[i]=a[i]*k+o[i-1]*(1-k)
    return o

def candles(ax,bars,ema_periods=(20,50,200),title='',xlabels=None):
    o=np.array([b[1] for b in bars]); h=np.array([b[2] for b in bars])
    l=np.array([b[3] for b in bars]); c=np.array([b[4] for b in bars])
    x=np.arange(len(bars))
    for i in range(len(bars)):
        up = c[i]>=o[i]
        col='#0b8a3e' if up else '#c62828'
        ax.vlines(x[i],l[i],h[i],color=col,linewidth=0.8,zorder=2)
        lo,hi=min(o[i],c[i]),max(o[i],c[i])
        ax.add_patch(Rectangle((x[i]-0.36,lo),0.72,max(hi-lo,(h.max()-l.min())*0.0008),
                     facecolor=col,edgecolor=col,linewidth=0.5,zorder=3))
    return x,c

def plot_symbol(sym):
    r=json.load(open(os.path.join(D,f'{sym}.json')))
    H=r['hourly']; DD=r['daily']
    if not H or len(H)<60: return None
    NH=180
    fullc=np.array([b[4] for b in H],float)
    e20f,e50f,e200f=ema(fullc,20),ema(fullc,50),ema(fullc,200)
    hb=H[-NH:]; off=len(H)-len(hb)
    fig=plt.figure(figsize=(16,10),dpi=100)
    gs=fig.add_gridspec(3,2,height_ratios=[3,1,2.4],hspace=0.28,wspace=0.14)
    ax=fig.add_subplot(gs[0,:]); axv=fig.add_subplot(gs[1,:],sharex=ax); axd=fig.add_subplot(gs[2,:])

    x,c=candles(ax,hb)
    ax.plot(x,e20f[off:],color='#1565c0',lw=1.2,label='EMA20')
    ax.plot(x,e50f[off:],color='#ef6c00',lw=1.2,label='EMA50')
    ax.plot(x,e200f[off:],color='#6a1b9a',lw=1.3,label='EMA200')
    hi=max(b[2] for b in hb); lo=min(b[3] for b in hb)
    ax.axhline(hi,color='#555',ls='--',lw=0.7); ax.axhline(lo,color='#555',ls='--',lw=0.7)
    ax.text(len(hb)*0.995,hi,f' {hi:.1f}',va='bottom',ha='right',fontsize=8,color='#555')
    ax.text(len(hb)*0.995,lo,f' {lo:.1f}',va='top',ha='right',fontsize=8,color='#555')
    ax.axhline(hb[-1][4],color='#000',ls=':',lw=0.9)
    ax.text(len(hb)-1,hb[-1][4],f'  {hb[-1][4]:.1f}',va='center',fontsize=9,fontweight='bold')
    lab=[datetime.datetime.fromtimestamp(b[0],IST) for b in hb]
    ticks=[i for i in range(len(hb)) if i%14==0]
    ax.set_xticks(ticks); ax.set_xticklabels([lab[i].strftime('%d-%b') for i in ticks],fontsize=8)
    ax.set_xlim(-1,len(hb)); ax.grid(alpha=0.18); ax.legend(fontsize=8,loc='upper left')
    ax.set_title(f'{sym} — 1 HOUR candles (last {len(hb)} bars, to {lab[-1]:%d-%b-%Y %H:%M} IST)',fontsize=12,fontweight='bold')

    vv=np.array([b[5] for b in hb],float)
    cols=['#0b8a3e' if hb[i][4]>=hb[i][1] else '#c62828' for i in range(len(hb))]
    axv.bar(x,vv,color=cols,width=0.72)
    axv.plot(x,np.convolve(vv,np.ones(20)/20,mode='same'),color='#333',lw=1)
    axv.set_ylabel('Vol',fontsize=9); axv.grid(alpha=0.18); axv.tick_params(labelbottom=False)

    ND=140; db=DD[-ND:]
    dc=np.array([b[4] for b in DD],float)
    d20,d50,d200=ema(dc,20),ema(dc,50),ema(dc,min(200,len(dc)))
    doff=len(DD)-len(db)
    xd,_=candles(axd,db)
    axd.plot(xd,d20[doff:],color='#1565c0',lw=1.1,label='D-EMA20')
    axd.plot(xd,d50[doff:],color='#ef6c00',lw=1.1,label='D-EMA50')
    axd.plot(xd,d200[doff:],color='#6a1b9a',lw=1.2,label='D-EMA200')
    dl=[datetime.datetime.fromtimestamp(b[0],IST) for b in db]
    dt=[i for i in range(len(db)) if i%14==0]
    axd.set_xticks(dt); axd.set_xticklabels([dl[i].strftime('%d-%b') for i in dt],fontsize=8)
    axd.set_xlim(-1,len(db)); axd.grid(alpha=0.18); axd.legend(fontsize=8,loc='upper left')
    axd.set_title(f'{sym} — DAILY candles (context, last {len(db)} sessions)',fontsize=11)

    p=os.path.join(C,f'{sym}.png')
    fig.savefig(p,bbox_inches='tight'); plt.close(fig)
    return p

syms=[f[:-5] for f in sorted(os.listdir(D)) if f.endswith('.json')]
if len(sys.argv)>1: syms=sys.argv[1:]
done=0;fail=[]
for s in syms:
    try:
        if plot_symbol(s): done+=1
    except Exception as e: fail.append((s,repr(e)[:90]))
print('charts',done,'fail',len(fail),fail[:5])
