# P(racha de >=k perdidas seguidas en n trades), q=0.48, por DP exacta
def p_streak(n,k,q):
    st=[0.0]*k; st[0]=1.0; hit=0.0
    for _ in range(n):
        new=[0.0]*k
        for j,pr in enumerate(st):
            new[0]+=pr*(1-q)
            if j+1>=k: hit+=pr*q
            else: new[j+1]+=pr*q
        st=new
    return hit
for n in [40,280]:
    print(n,{k:round(p_streak(n,k,0.48),3) for k in [4,5,6,7,8,10]})
