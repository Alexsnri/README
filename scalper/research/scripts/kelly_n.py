import numpy as np, math
from statistics import NormalDist
N=NormalDist()
p=0.52; tail=0.03; big=2.5
def dist(E):
    lm=(1-tail)+tail*big; W=(E+(1-p)*lm)/p
    vals=np.array([W,-1,-big]); pr=np.array([p,(1-p)*(1-tail),(1-p)*tail]); return vals,pr
print("== Kelly exacto (max E[log(1+f r)]) vs aproximacion mu/sigma^2")
for E in [0.02,0.05,0.10,0.15,0.30]:
    v,pr=dist(E); mu=(v*pr).sum(); var=((v-mu)**2*pr).sum()
    fs=np.linspace(0.0005,0.39,4000); g=np.array([(pr*np.log1p(f*v)).sum() for f in fs])
    i=g.argmax(); fk=fs[i]; gk=g[i]
    def gf(f): return (pr*np.log1p(f*v)).sum()
    print(f"E={E:.2f} sigma={math.sqrt(var):.3f} f*exacto={fk*100:.1f}% aprox={mu/var*100:.1f}% g*/trade={gk:.5f} | g(1/2K)={gf(fk/2):.5f} g(1/4K)={gf(fk/4):.5f} g(2K)={gf(min(2*fk,0.39)):.5f} | x/noche(40tr) fullK={math.exp(40*gk):.3f} halfK={math.exp(40*gf(fk/2)):.3f}")
print("\n== Riesgo de ruina asintotico (horizonte infinito, aprox difusion): P(tocar b*inicial)=b^(2m/s^2), b=0.2 ($20) y b=0.5")
for E in [0.0,0.05,0.10]:
    v,pr=dist(E); mu=(v*pr).sum(); var=((v-mu)**2*pr).sum()
    for f in [0.005,0.01,0.02,0.03,0.05,0.10,0.20]:
        m=(pr*np.log1p(f*v)).sum(); s2=(pr*np.log1p(f*v)**2).sum()-m*m
        if m<=0: print(f" E={E} f={f*100:.1f}%: g<=0 -> ruina ~1 (seguro a largo plazo)"); continue
        a=2*m/s2
        print(f" E={E} f={f*100:.1f}%: P(-80%)={0.2**a:.2e} P(-50%)={0.5**a:.3f}")
print("\n== Ventaja necesaria para mediana 100x en una noche (log-crecimiento 4.605) a Kelly completo, sigma=1R")
for n in [20,40,60,100,200]:
    g=math.log(100)/n
    # g*= mu^2/(2 sigma^2) aprox -> mu = sqrt(2g)
    mu=math.sqrt(2*g)
    print(f" n={n}: g/trade={g:.4f} -> mu/sigma por trade>={mu:.3f}  (f*~{mu*100:.0f}% por trade) ; Sharpe anualizado si se repite 252 dias = {mu*math.sqrt(n*252):.0f}")
print("\n== Tamanos de muestra n=(z*sigma/mu)^2, sigma=1R")
for mu in [0.05,0.10,0.20,0.30]:
    n2=(1.96/mu)**2; n1=(1.645/mu)**2; npow=((1.645+0.8416)/mu)**2; ndiff=2*((1.96+0.8416)/mu)**2
    print(f" mu={mu}: 2colas95={n2:.0f} 1cola95={n1:.0f} 1cola95+poder80={npow:.0f} comparar 2 variantes (dif=mu, poder80) por brazo={ndiff:.0f}; noches@40tr(1cola)={n1/40:.1f}")
print("\n== Regla de corte: media observada por debajo de la cual se rechaza mu=mu_bt (1 cola 95%), sigma=1.1")
for mu_bt in [0.05,0.10,0.15]:
    print(" mu_bt",mu_bt, [ (n, round(mu_bt-1.645*1.1/math.sqrt(n),3), round(n*(mu_bt-1.645*1.1/math.sqrt(n)),1)) for n in [30,50,100,200,400]])
print("\n== Error de estimacion: crecimiento real si apuestas Kelly del mu estimado; mu_real=0.05, sigma=1.1")
rng=np.random.default_rng(1)
for ntr in [50,100,200,500,1000]:
    mu_hat=0.05+1.1/math.sqrt(ntr)*rng.standard_normal(200000)
    for frac in [1.0,0.5,0.25]:
        f=np.clip(frac*mu_hat/1.21,0,1)
        g=0.05*f-0.5*1.21*f**2   # crecimiento esperado con mu real
        print(f" n={ntr} frac={frac}: g medio={g.mean():.5f} (optimo {0.05**2/(2*1.21):.5f}) P(f>2f*)={np.mean(f>2*0.05/1.21):.2f}")
