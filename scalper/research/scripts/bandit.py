# Thompson sampling gaussiano (sigma conocida=1.1) vs descontado, 4 estrategias, regimen cambia en t=1500
import numpy as np
rng=np.random.default_rng(7); S=1.1; T=3000; R=300
mus1=np.array([0.10,0.05,0.0,-0.10]); mus2=np.array([-0.10,0.05,0.0,0.10])
def run(gamma,prior_n=10,prior_mu=0.0):
    share=np.zeros((R,T),bool); cum=np.zeros(R)
    for r in range(R):
        n=np.full(4,float(prior_n)); s=np.full(4,prior_mu*prior_n)
        for t in range(T):
            mus=mus1 if t<1500 else mus2
            draw=rng.normal(s/n, S/np.sqrt(n))
            a=draw.argmax(); x=rng.normal(mus[a],S)
            if gamma<1: n=gamma*n+(1-gamma)*prior_n; s=gamma*s+(1-gamma)*prior_mu*prior_n
            n[a]+=1; s[a]+=x; cum[r]+=x
            share[r,t]= a==mus.argmax()
    return share.mean(0), cum.mean()
for g in [1.0,0.995,0.98]:
    sh,c=run(g)
    print(f"gamma={g}: %mejor brazo t<200={sh[:200].mean():.2f} 200-1500={sh[200:1500].mean():.2f} 1500-1700={sh[1500:1700].mean():.2f} 1700-3000={sh[1700:].mean():.2f} | R total medio={c:.1f} (oraculo={0.10*T:.0f}, uniforme={0.0125*T:.0f})")
