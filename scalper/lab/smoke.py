import sys, time
sys.path.insert(0, "lab"); sys.path.insert(0, ".")
from data import load_1m
from sim import Market, simulate
from bot import strategies as S
from bot.stops import POLICIES
for name in ["US500", "BTCUSD"]:
    t=time.time(); df=load_1m(name); mk=Market(name, df); print(name, len(df), df.index[0], df.index[-1], "prep %.1fs"%(time.time()-t))
    for cls in S.ALL:
        if name not in cls.instruments: continue
        st=next(cls.configs()); t=time.time(); sig=st.signals(mk.df5, mk.inst.family); ts=time.time()-t
        tr=simulate(mk, sig, POLICIES["fijo"], ignore_schedule=getattr(cls,"ignore_schedule",False))
        print(f"  {st.key:40s} n={len(tr):5d} E={tr.R.mean():+.3f}R cost={tr.cost_R.mean():.3f}R win={(tr.R>0).mean():.2f} sig {ts:.1f}s sim {time.time()-t-ts:.1f}s", tr.reason.value_counts().to_dict())
