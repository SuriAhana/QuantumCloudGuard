import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from quantumcloudguard.pipeline import QuantumCloudGuard


def run():
    results=[]
    q=QuantumCloudGuard(); q.store('tamper',b'A'*10000); q.tamper_ciphertext('tamper')
    try: q.retrieve('tamper'); detected=False
    except Exception: detected=True
    results.append(('ciphertext_tamper',detected))

    q=QuantumCloudGuard(); q.store('audit',b'A'*1000); q.tamper_audit(0)
    results.append(('audit_tamper',not q.audit.validate()))

    q=QuantumCloudGuard(); obj=q.store('recovery',b'A'*1000,k=3,n=5)
    obj.recovery.nodes[0].available=False; obj.recovery.nodes[1].available=False
    results.append(('3_of_5_with_2_failures', q.retrieve('recovery',force_recovery=True)==b'A'*1000))
    for name,ok in results: print(f'{name}: {"PASS" if ok else "FAIL"}')

if __name__=='__main__': run()
