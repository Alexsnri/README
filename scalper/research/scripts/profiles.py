# Perfiles con stop diario (en R desde equity de inicio del dia) y breaker de rachas (pausa resto del dia)
import numpy as np
rng=np.random.default_rng(99); p=0.52; tail=0.03; big=2.5
def W_for(E): return (E+(1-p)*((1-tail)+tail*big))/p
def run(E,f,D,K,days,ntr=40,P=10000):
    W=W_for(E); eq=np.full(P,100.0); alive=np.ones(P,bool); stopped_days=0
    out={}
    for d in range(days):
        start=eq.copy(); active=alive.copy(); streak=np.zeros(P,int); dayR=np.zeros(P)
        for t in range(ntr):
            u=rng.random(P); v=rng.random(P)
            r=np.where(u<p,W,np.where(v<tail,-big,-1.0))
            r=np.where(active,r,0.0)
            eq=eq*np.maximum(1+f*r,0); dayR+=r
            streak=np.where(r<0,streak+1,np.where(r>0,0,streak))
            hit=active&((dayR<=-D)|(streak>=K)); stopped_days+=hit.sum(); active&=~hit
            alive&=eq>=20; active&=alive
        if d+1 in (1,7,30): out[d+1]=eq.copy()
    return out,alive,stopped_days/(P*days)
for name,f,D,K in [("NORMAL 1%/trade, stop dia -6R(-6%), breaker 7",0.01,6,7),("AGRESIVO 2%/trade, stop dia -6R(-12%), breaker 7",0.02,6,7),("CONSERVADOR-ARRANQUE 0.5%, stop -6R(-3%), breaker 7",0.005,6,7),("SIN FRENOS 2%",0.02,1e9,10**9),("SIN FRENOS 1%",0.01,1e9,10**9)]:
    print("\n##",name)
    for E in [-0.05,0.0,0.05,0.10]:
        o,alive,sd=run(E,f,D,K,30)
        s=" | ".join(f"{k}d: med {np.median(v):.1f} [{np.percentile(v,10):.1f}-{np.percentile(v,90):.1f}] P(-50%) {np.mean(v<=50):.3f}" for k,v in o.items())
        print(f" E={E:+.2f}: {s} | ruina30d {np.mean(~alive):.3f} | %dias frenados {sd:.2f}")
