from __future__ import annotations
import argparse, json, os, csv, time
from pathlib import Path
from .pipeline import QuantumCloudGuard
from .workloads import synthetic_jobs, PythonCloudSimulator
from .metrics import summary


def demo(args):
    q=QuantumCloudGuard(require_pqc=args.require_pqc)
    data=(b'QuantumCloudGuard demo payload. '*4096)
    obj=q.store('demo-object',data,k=3,n=5)
    out=q.retrieve('demo-object')
    assert out==data
    print(json.dumps({'status':'PASS','kem_backend':q.kem.backend,'key_report':obj.key_report,'timings_ms':obj.timings,'audit_valid':q.audit.validate()},indent=2,default=str))

def experiments(args):
    outdir=Path(args.out); outdir.mkdir(parents=True,exist_ok=True)
    sizes=[1,4,8] if args.profile=='quick' else [10,50,100,250,500]
    runs=3 if args.profile=='quick' else 10
    rows=[]
    for mb in sizes:
        payload=os.urandom(mb*1024*1024)
        for r in range(runs):
            q=QuantumCloudGuard(require_pqc=args.require_pqc)
            t=time.perf_counter(); obj=q.store(f'o-{mb}-{r}',payload); store_ms=(time.perf_counter()-t)*1000
            t=time.perf_counter(); got=q.retrieve(f'o-{mb}-{r}'); retrieve_ms=(time.perf_counter()-t)*1000
            assert got==payload
            rows.append({'size_mb':mb,'run':r,'store_ms':store_ms,'retrieve_ms':retrieve_ms,'kem_backend':q.kem.backend,
                         'entropy':obj.key_report['entropy'],**obj.timings})
    with open(outdir/'crypto_scaling.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    summaries=[]
    for mb in sizes:
        rr=[x for x in rows if x['size_mb']==mb]
        summaries.append({'size_mb':mb,'store':summary(x['store_ms'] for x in rr),'retrieve':summary(x['retrieve_ms'] for x in rr)})
    (outdir/'summary.json').write_text(json.dumps(summaries,indent=2))
    # workload scalability using measured median security cost
    sec=summary(x['store_ms'] for x in rows)['median']
    job_sizes=[1000,5000] if args.profile=='quick' else [1000,5000,10000,25000,50000]
    sim=PythonCloudSimulator(50,2); wr=[]
    for n in job_sizes:
        res=sim.run(synthetic_jobs(n),security_ms=sec); res['security_ms']=sec; wr.append(res)
    with open(outdir/'workload_scaling.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=wr[0].keys()); w.writeheader(); w.writerows(wr)
    print(f'Wrote results to {outdir}')


def main():
    p=argparse.ArgumentParser(prog='quantumcloudguard')
    sub=p.add_subparsers(dest='cmd',required=True)
    d=sub.add_parser('demo'); d.add_argument('--require-pqc',action='store_true'); d.set_defaults(func=demo)
    e=sub.add_parser('experiment'); e.add_argument('--profile',choices=['quick','paper'],default='quick'); e.add_argument('--out',default='results'); e.add_argument('--require-pqc',action='store_true'); e.set_defaults(func=experiments)
    a=p.parse_args(); a.func(a)
if __name__=='__main__': main()
