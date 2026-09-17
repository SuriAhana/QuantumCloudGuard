import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import csv, os, copy, time
from quantumcloudguard.pipeline import QuantumCloudGuard
from quantumcloudguard.auth import MerkleAuthenticator
from quantumcloudguard.metrics import classification


def run(out='results/security_metrics.csv'):
    os.makedirs(os.path.dirname(out),exist_ok=True)
    q=QuantumCloudGuard(auth_leaves=64); payload=b'Z'*32768; obj=q.store('secure',payload)
    protected=obj.aes_pack['ciphertext']+obj.aes_pack['tag']; msg=__import__('hashlib').sha3_256(protected).digest()+b'secure'
    tp=tn=fp=fn=0
    # legitimate signature should verify
    for _ in range(20):
        ok=MerkleAuthenticator.verify(obj.auth_root,msg,obj.auth_bundle)
        if ok: tn+=1
        else: fp+=1
    # mutated signatures should fail
    for i in range(20):
        b=copy.deepcopy(obj.auth_bundle); sig=list(b['signature']); x=bytearray(sig[0]); x[0]^=1; sig[0]=bytes(x); b['signature']=sig
        ok=MerkleAuthenticator.verify(obj.auth_root,msg,b)
        if not ok: tp+=1
        else: fn+=1
    auth=classification(tp,tn,fp,fn)

    # integrity classification
    tp=tn=fp=fn=0
    for i in range(20):
        if q.integrity.verify(protected,obj.integrity): tn+=1
        else: fp+=1
    for i in range(20):
        t=bytearray(protected); t[i%len(t)]^=1
        if not q.integrity.verify(bytes(t),obj.integrity): tp+=1
        else: fn+=1
    integ=classification(tp,tn,fp,fn)

    rows=[]
    for k,v in auth.items(): rows.append({'metric_group':'authentication','metric':k,'value':v})
    for k,v in integ.items(): rows.append({'metric_group':'integrity','metric':k,'value':v})
    rows.append({'metric_group':'keygen','metric':'entropy','value':obj.key_report['entropy']})
    rows.append({'metric_group':'audit','metric':'chain_valid','value':1.0 if q.audit.validate() else 0.0})
    with open(out,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print(out)
if __name__=='__main__': run()
