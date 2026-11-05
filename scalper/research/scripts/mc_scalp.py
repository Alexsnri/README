# Monte Carlo de crecimiento con riesgo fijo fraccional (porcentaje del capital ACTUAL por trade).
# Resultado por trade en R: gana +W con prob p; pierde -1R (97%) o -2.5R (3%, slippage/gap).
# W se calibra para que la expectativa E (ya neta de costos) sea la deseada.
import numpy as np
rng=np.random.default_rng(12345)
START=100.0; RUIN=20.0; TARGET=10000.0
def W_for(E,p,tail=0.03,big=2.5):
    lossmean=(1-tail)*1+tail*big
    return (E+(1-p)*lossmean)/p
def sim(E,p,f,ntr,npaths=20000,tail=0.03,big=2.5):
    W=W_for(E,p,tail,big)
    eq=np.full(npaths,START); alive=np.ones(npaths,bool); peak_hit=np.zeros(npaths,bool)
    minq=np.full(npaths,START)
    for t in range(ntr):
        u=rng.random(npaths); v=rng.random(npaths)
        r=np.where(u<p,W,np.where(v<tail,-big,-1.0))
        mult=np.maximum(1+f*r,0.0)
        eq=np.where(alive,eq*mult,eq)
        peak_hit|=eq>=TARGET
        minq=np.minimum(minq,eq)
        alive&=eq>=RUIN
    return eq,alive,peak_hit,minq,W
fs=[0.005,0.01,0.02,0.03,0.05,0.10,0.20,0.50,1.00]
Es=[-0.05,0.0,0.05,0.10,0.15]
p=0.52
horizons=[('1 noche (40 tr)',40),('1 semana 7d (280 tr)',280),('1 mes 30d (1200 tr)',1200)]
import sys
mode=sys.argv[1] if len(sys.argv)>1 else 'main'
if mode=='main':
  for E in Es:
    print(f"\n### E = {E:+.2f}R/trade (p={p}, W={W_for(E,p):.3f}R)")
    print("riesgo | horizonte | mediana $ | p10 | p90 | P(>=10k al final) | P(toco 10k) | P(-50% al final) | P(ruina <$20)")
    for f in fs:
        for hn,n in horizons:
            eq,alive,hit,minq,W=sim(E,p,f,n,npaths=10000 if n>300 else 20000)
            print(f"{f*100:5.1f}% | {hn} | {np.median(eq):.2f} | {np.percentile(eq,10):.2f} | {np.percentile(eq,90):.2f} | {np.mean(eq>=TARGET):.4f} | {np.mean(hit):.4f} | {np.mean(eq<=50):.3f} | {np.mean(~alive):.3f}")
elif mode=='night':
  # P(tocar 10k en una noche) con 20/40/60 trades y riesgos altos
  for E in [0.10,0.15]:
    for n in [20,40,60]:
      for f in [0.05,0.10,0.20,0.50,1.0]:
        eq,alive,hit,minq,W=sim(E,p,f,n,npaths=200000)
        print(f"E={E} n={n} f={f}: P(toca 10k)={np.mean(hit):.5f} P(ruina)={np.mean(~alive):.3f} mediana={np.median(eq):.2f}")
