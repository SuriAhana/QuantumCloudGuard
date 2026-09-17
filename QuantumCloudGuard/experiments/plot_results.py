import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main(results='results'):
    p=Path(results); p.mkdir(exist_ok=True)
    f=p/'crypto_scaling.csv'
    if f.exists():
        df=pd.read_csv(f); g=df.groupby('size_mb')[['store_ms','retrieve_ms']].mean().reset_index()
        plt.figure(); plt.plot(g.size_mb,g.store_ms,marker='o',label='Store'); plt.plot(g.size_mb,g.retrieve_ms,marker='s',label='Retrieve');
        plt.xlabel('File Size (MB)'); plt.ylabel('Latency (ms)'); plt.legend(); plt.tight_layout(); plt.savefig(p/'crypto_scaling.png',dpi=300); plt.close()
    f=p/'workload_scaling.csv'
    if f.exists():
        df=pd.read_csv(f); plt.figure(); plt.plot(df.jobs,df.avg_latency_ms,marker='o'); plt.xlabel('Number of Jobs'); plt.ylabel('Average Latency (ms)'); plt.tight_layout(); plt.savefig(p/'workload_scaling.png',dpi=300); plt.close()
if __name__=='__main__': main()
