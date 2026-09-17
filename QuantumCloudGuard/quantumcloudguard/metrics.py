from __future__ import annotations
import math
from typing import Iterable

def summary(values:Iterable[float]):
    v=list(values); n=len(v)
    if not n: return {'n':0,'mean':0,'sd':0,'ci95_low':0,'ci95_high':0,'median':0,'p95':0}
    mean=sum(v)/n
    sd=math.sqrt(sum((x-mean)**2 for x in v)/(n-1)) if n>1 else 0
    try:
        from scipy.stats import t
        crit=float(t.ppf(.975,n-1)) if n>1 else 0
    except Exception: crit=1.96
    half=crit*sd/math.sqrt(n) if n>1 else 0
    s=sorted(v); med=s[n//2] if n%2 else .5*(s[n//2-1]+s[n//2]); p95=s[min(n-1,int(.95*n))]
    return {'n':n,'mean':mean,'sd':sd,'ci95_low':mean-half,'ci95_high':mean+half,'median':med,'p95':p95}

def classification(tp,tn,fp,fn):
    total=tp+tn+fp+fn
    acc=(tp+tn)/total if total else 0
    tpr=tp/(tp+fn) if tp+fn else 0; tnr=tn/(tn+fp) if tn+fp else 0
    return {'accuracy':acc,'tpr':tpr,'tnr':tnr,'fpr':1-tnr,'fnr':1-tpr}
