from __future__ import annotations
import csv, random
from dataclasses import dataclass
from typing import Iterable, List

@dataclass
class Job:
    job_id:int; cpu:float; memory:float; duration_ms:float; arrival_ms:float

def synthetic_jobs(n:int, seed:int=42)->List[Job]:
    r=random.Random(seed); t=0.0; jobs=[]
    for i in range(n):
        t += r.expovariate(1/5)
        jobs.append(Job(i,r.uniform(.1,1.0),r.uniform(.1,1.0),r.lognormvariate(4,0.5),t))
    return jobs

def load_generic_trace(path:str, max_jobs:int|None=None)->List[Job]:
    """Generic CSV adapter. Maps first numeric columns to cpu/memory/duration/arrival when exact trace schema varies.
    Use preprocess scripts to produce normalized CSV with columns job_id,cpu,memory,duration_ms,arrival_ms.
    """
    jobs=[]
    with open(path,newline='',encoding='utf-8',errors='ignore') as f:
        reader=csv.DictReader(f)
        for i,row in enumerate(reader):
            if max_jobs and i>=max_jobs: break
            try:
                jobs.append(Job(int(row.get('job_id',i)),float(row.get('cpu',0.5)),float(row.get('memory',0.5)),
                                float(row.get('duration_ms',100)),float(row.get('arrival_ms',i))))
            except Exception: continue
    return jobs

class PythonCloudSimulator:
    """Deterministic lightweight simulator used when Java CloudSim is unavailable.
    It models 50 time-shared VMs and injects measured security-service latency into each job.
    """
    def __init__(self, vms:int=50, vm_cores:int=2): self.vms=vms; self.vm_cores=vm_cores
    def run(self,jobs:Iterable[Job], security_ms:float=0.0):
        available=[0.0]*self.vms; lat=[]
        for j in jobs:
            idx=min(range(self.vms),key=lambda k:available[k])
            start=max(j.arrival_ms,available[idx]); service=j.duration_ms/max(0.2,self.vm_cores*j.cpu)+security_ms
            finish=start+service; available[idx]=finish; lat.append(finish-j.arrival_ms)
        if not lat: return {'jobs':0,'avg_latency_ms':0,'p95_latency_ms':0,'makespan_ms':0}
        s=sorted(lat); p95=s[min(len(s)-1,int(.95*len(s)))]
        return {'jobs':len(lat),'avg_latency_ms':sum(lat)/len(lat),'p95_latency_ms':p95,'makespan_ms':max(available)}
