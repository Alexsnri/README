# ATR(14) en velas de 5 min: mediana y p75, todas las horas y "horas activas" (13-20 UTC)
import json, numpy as np, csv, sys
S='/tmp/claude-0/-home-user-README/82cdbbb4-ddee-5e71-af10-eeafa19fca7d/scratchpad/'
def atr(ts,h,l,c,n=14):
    pc=np.r_[c[0],c[:-1]]
    tr=np.maximum(h-l,np.maximum(abs(h-pc),abs(l-pc)))
    a=np.convolve(tr,np.ones(n)/n,'valid'); return ts[n-1:],a,c[n-1:]
def rep(name,ts,h,l,c):
    t,a,cc=atr(ts,h,l,c)
    hr=(t//3600)%24
    act=(hr>=13)&(hr<20)
    print(f"{name:8s} precio~{np.median(cc):10.5g} ATR5m mediana={np.median(a):.5g} p75={np.percentile(a,75):.5g} | 13-20UTC mediana={np.median(a[act]):.5g} n={len(a)}")
for sym in ['BTCUSDT','ETHUSDT','PAXGUSDT']:
    rows=[]
    for m in ['2026-08','2026-09','2026-10']:
        with open(S+f'data/binance/{sym}-1m-{m}.csv') as f:
            for r in csv.reader(f):
                if not r[0].isdigit(): continue
                rows.append((int(r[0]),float(r[2]),float(r[3]),float(r[4])))
    a=np.array(rows); ts=a[:,0]; ts=ts/1e6 if ts[0]>1e14 else ts/1e3
    b=(ts//300).astype(np.int64); u,idx=np.unique(b,return_index=True)
    H=np.maximum.reduceat(a[:,1],idx); L=np.minimum.reduceat(a[:,2],idx); C=a[np.r_[idx[1:]-1,len(a)-1],3]
    rep(sym,u*300,H,L,C)
for s in ['EURUSDX','GBPUSDX','NQF','ESF','GCF']:
    d=json.load(open(S+f'dl/yahoo/y_{s}.json'))['chart']['result'][0]
    q=d['indicators']['quote'][0]; ts=np.array(d['timestamp'],float)
    h,l,c=[np.array([np.nan if v is None else v for v in q[k]],float) for k in ('high','low','close')]
    ok=~(np.isnan(h)|np.isnan(l)|np.isnan(c)); rep(s,ts[ok],h[ok],l[ok],c[ok])
