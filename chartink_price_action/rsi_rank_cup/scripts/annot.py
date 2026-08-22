import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np, sys, os
sys.path.insert(0,'rsi15')
from daily_series import load_all, ema, rsi_series
UP='#1a9850'; DN='#d73027'

def candles(ax,o,h,l,c,w=0.62):
    for i in range(len(o)):
        col=UP if c[i]>=o[i] else DN
        ax.vlines(i,l[i],h[i],color=col,lw=0.85,zorder=2)
        lo,hi=min(o[i],c[i]),max(o[i],c[i])
        ax.add_patch(Rectangle((i-w/2,lo),w,max(hi-lo,(h[i]-l[i])*0.004 or 1e-9),
                     facecolor=col,edgecolor=col,lw=0.5,zorder=3))

SETUPS = {
 'APLAPOLLO': dict(rank=4, rsi=77.0, rally=(5,119), rim=2301.40, low_i=192, low=1736.00,
    lines=[(2301.40,'#7b3294','true rim / Feb high  2301'),
           (2173.00,'#4575b4','110-bar high  2173'),
           (1980.00,'#d73027','invalidation  1980'),
           (1736.00,'#888888','base low  1736')],
    note='rally +45.8% (114 bars)  ->  cup -24.6% deep, 73 bars down / 58 bars up  ->  right side, 7.1% below rim'),
 'BLISSGVS': dict(rank=8, rsi=75.9, rally=(145,212), rim=553.00, low_i=228, low=447.20,
    lines=[(602.45,'#4575b4','20-Aug spike high  602.45'),
           (553.00,'#7b3294','rim / 30-Jun high  553'),
           (447.20,'#d73027','base low & invalidation  447'),],
    note='rally +212% (104 bars)  ->  base -19.1% deep, 38 bars  ->  broken out, 4.7% above the 553 rim'),
}

for sym,S in SETUPS.items():
    g=load_all()[sym] if 'ALL' not in globals() else None
for_all = load_all()

for sym,S in SETUPS.items():
    g=for_all[sym]
    o,h,l,c,v=[g[k].values.astype(float) for k in ('open','high','low','close','volume')]
    d=g['d'].values; n=len(c)
    e20,e50,e200=ema(c,20),ema(c,50),ema(c,200); rs=rsi_series(c)

    fig=plt.figure(figsize=(18,13))
    gs=fig.add_gridspec(4,1,height_ratios=[3.4,1.0,3.0,1.0],hspace=0.30)

    ax=fig.add_subplot(gs[0]); candles(ax,o,h,l,c)
    ax.plot(e20,color='#4575b4',lw=1.1,label='EMA20')
    ax.plot(e50,color='#f46d43',lw=1.1,label='EMA50')
    ax.plot(e200,color='#7b3294',lw=1.2,label='EMA200')
    r0,r1=S['rally']
    ax.axvspan(r0,r1,color='#1a9850',alpha=0.07,zorder=0)
    ax.axvspan(r1,n-1,color='#4575b4',alpha=0.07,zorder=0)
    ymin,ymax=l.min(),h.max(); pad=(ymax-ymin)*0.04
    ax.text((r0+r1)/2,ymin-pad*0.2,'RALLY',ha='center',fontsize=12,weight='bold',color='#1a9850')
    ax.text((r1+n-1)/2,ymin-pad*0.2,'CUP / BASE',ha='center',fontsize=12,weight='bold',color='#2b5f9e')
    for y,col,lab in S['lines']:
        ax.axhline(y,color=col,lw=1.3,ls='--',zorder=4)
        ax.text(n*1.005,y,lab,fontsize=10,color=col,va='center',weight='bold')
    ax.scatter([S['low_i']],[S['low']],s=120,marker='v',color='#111',zorder=6)
    ax.scatter([r1],[S['rim']],s=120,marker='^',color='#111',zorder=6)
    ax.scatter([n-1],[c[-1]],s=150,marker='o',facecolor='none',edgecolor='#111',lw=2,zorder=6)
    ax.annotate(f'now {c[-1]:.2f}',(n-1,c[-1]),xytext=(-72,-26),textcoords='offset points',
                fontsize=11,weight='bold',arrowprops=dict(arrowstyle='->',color='#111'))
    ax.set_xlim(-2,n*1.0); ax.set_ylim(ymin-pad,ymax+pad)
    ax.legend(loc='upper left',fontsize=9,ncol=3)
    ax.set_title(f"#{S['rank']}  {sym}   daily RSI(14)={S['rsi']}   close={c[-1]:.2f}   [{d[0]} .. {d[-1]}]\n{S['note']}",
                 fontsize=13,weight='bold')
    ax.grid(alpha=0.16); ax.set_ylabel('price')
    tk=range(0,n,15); ax.set_xticks(list(tk)); ax.set_xticklabels([d[i][2:] for i in tk],fontsize=7,rotation=45)

    axr=fig.add_subplot(gs[1],sharex=ax); axr.plot(rs,color='#111',lw=1.0)
    axr.axhline(70,color='#d73027',lw=0.7,ls='--'); axr.axhline(60,color='#888',lw=0.7,ls=':')
    axr.axvspan(r0,r1,color='#1a9850',alpha=0.07); axr.axvspan(r1,n-1,color='#4575b4',alpha=0.07)
    axr.set_ylim(10,95); axr.set_ylabel('RSI14'); axr.grid(alpha=0.16)
    plt.setp(ax.get_xticklabels(),visible=False)

    k=min(120,n); s=n-k
    ax2=fig.add_subplot(gs[2]); candles(ax2,o[s:],h[s:],l[s:],c[s:])
    ax2.plot(e20[s:],color='#4575b4',lw=1.2); ax2.plot(e50[s:],color='#f46d43',lw=1.2); ax2.plot(e200[s:],color='#7b3294',lw=1.3)
    for y,col,lab in S['lines']:
        if l[s:].min()*0.97 < y < h[s:].max()*1.03:
            ax2.axhline(y,color=col,lw=1.3,ls='--')
            ax2.text(k*1.004,y,lab,fontsize=10,color=col,va='center',weight='bold')
    if S['low_i']>=s: ax2.scatter([S['low_i']-s],[S['low']],s=130,marker='v',color='#111',zorder=6)
    ax2.set_xlim(-1,k); ax2.grid(alpha=0.16); ax2.set_ylabel('price')
    ax2.set_title(f'{sym} — zoom, last {k} daily bars',fontsize=11)
    tk2=range(0,k,5); ax2.set_xticks(list(tk2)); ax2.set_xticklabels([d[s+i][5:] for i in tk2],fontsize=7,rotation=45)

    axv=fig.add_subplot(gs[3],sharex=ax2)
    avg=np.convolve(v,np.ones(20)/20,mode='same')
    axv.bar(range(k),v[s:],color=[UP if c[s+i]>=o[s+i] else DN for i in range(k)],width=0.62)
    axv.plot(avg[s:],color='#333',lw=1.0); axv.set_ylabel('vol'); axv.grid(alpha=0.16)
    plt.setp(ax2.get_xticklabels(),visible=False)

    out=f'rsi15/selected_{sym}.png'
    fig.savefig(out,dpi=105,bbox_inches='tight',facecolor='white'); plt.close(fig); print('saved',out)
