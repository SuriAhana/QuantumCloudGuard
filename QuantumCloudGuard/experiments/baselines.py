import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import csv, os, time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from quantumcloudguard.crypto import AESGCMEngine, KEMProvider
from quantumcloudguard.pipeline import QuantumCloudGuard


def bench(size_mb=1, runs=3, out='results/baselines.csv'):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    data=os.urandom(size_mb*1024*1024); rows=[]
    rsa_sk=rsa.generate_private_key(public_exponent=65537,key_size=3072); rsa_pk=rsa_sk.public_key()
    kem=KEMProvider(); pk,sk=kem.generate_keypair()
    for r in range(runs):
        key=os.urandom(32)
        t=time.perf_counter(); aes=AESGCMEngine.encrypt(key,data); AESGCMEngine.decrypt(key,aes); ms=(time.perf_counter()-t)*1000
        rows.append({'baseline':'AES-GCM only','run':r,'size_mb':size_mb,'latency_ms':ms,'pqc':False,'recovery':False,'audit':False})

        t=time.perf_counter(); wrapped=rsa_pk.encrypt(key,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None));
        key2=rsa_sk.decrypt(wrapped,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None)); aes=AESGCMEngine.encrypt(key2,data); AESGCMEngine.decrypt(key2,aes); ms=(time.perf_counter()-t)*1000
        rows.append({'baseline':'AES-GCM + RSA-OAEP','run':r,'size_mb':size_mb,'latency_ms':ms,'pqc':False,'recovery':False,'audit':False})

        t=time.perf_counter(); pack=kem.wrap_session_key(pk,key); key2=kem.unwrap_session_key(sk,pack); aes=AESGCMEngine.encrypt(key2,data); AESGCMEngine.decrypt(key2,aes); ms=(time.perf_counter()-t)*1000
        rows.append({'baseline':'AES-GCM + KEM','run':r,'size_mb':size_mb,'latency_ms':ms,'pqc':kem.backend.startswith('liboqs'),'recovery':False,'audit':False})

        q=QuantumCloudGuard(); t=time.perf_counter(); q.store(f'x{r}',data); q.retrieve(f'x{r}'); ms=(time.perf_counter()-t)*1000
        rows.append({'baseline':'Full QuantumCloudGuard','run':r,'size_mb':size_mb,'latency_ms':ms,'pqc':q.kem.backend.startswith('liboqs'),'recovery':True,'audit':True})
    with open(out,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print(out)
if __name__=='__main__': bench()
