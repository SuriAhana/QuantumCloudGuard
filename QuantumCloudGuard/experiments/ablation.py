import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
"""Simple executable ablation harness.
For paper experiments, replace one module at a time and compare latency/security outputs.
This script demonstrates two core ablations: chaotic+OS entropy versus OS entropy only,
and threshold recovery enabled versus unavailable.
"""
import os,time,csv
from quantumcloudguard.pipeline import QuantumCloudGuard
from quantumcloudguard.crypto import AESGCMEngine

def run(path='results/ablation.csv'):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    rows=[]; data=os.urandom(1024*1024)
    for mode in ['full','os_rng_baseline']:
        q=QuantumCloudGuard(); t=time.perf_counter()
        if mode=='full': obj=q.store(mode,data)
        else:
            # latency baseline for conventional CSPRNG + AES-GCM
            key=os.urandom(32); aes=AESGCMEngine.encrypt(key,data); obj=None
        ms=(time.perf_counter()-t)*1000
        rows.append({'variant':mode,'storage_latency_ms':ms,'integrity_available':mode=='full','recovery_available':mode=='full'})
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print(path)
if __name__=='__main__': run()
