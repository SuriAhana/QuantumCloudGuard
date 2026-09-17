import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import csv, os, time
from quantumcloudguard.pipeline import QuantumCloudGuard

def run(out='results/recovery_matrix.csv'):
    os.makedirs(os.path.dirname(out),exist_ok=True); rows=[]
    for k,n in [(3,5),(4,7)]:
        for failures in range(n+1):
            q=QuantumCloudGuard(); obj=q.store(f'r-{k}-{n}-{failures}',b'R'*8192,k=k,n=n)
            for node in obj.recovery.nodes[:failures]: node.available=False
            t=time.perf_counter(); ok=True
            try: q.retrieve(obj.object_id,force_recovery=True)
            except Exception: ok=False
            ms=(time.perf_counter()-t)*1000
            rows.append({'k':k,'n':n,'failed_nodes':failures,'available_nodes':n-failures,'success':ok,'recovery_latency_ms':ms})
    with open(out,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print(out)
if __name__=='__main__': run()
