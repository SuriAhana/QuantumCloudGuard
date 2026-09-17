from __future__ import annotations
import os,time
from dataclasses import dataclass,field
from typing import Dict
from .keygen import ChaoticKeyGenerator
from .crypto import AESGCMEngine,KEMProvider
from .auth import MerkleAuthenticator
from .integrity import IntegrityVerifier
from .audit import AuditChain
from .recovery import RecoveryManager
from .utils import canonical_json, sha3

@dataclass
class ProtectedObject:
    object_id:str
    aes_pack:dict
    kem_pack:dict
    integrity:dict
    auth_bundle:dict
    auth_root:bytes
    recovery:RecoveryManager
    key_report:dict
    timings:dict=field(default_factory=dict)

class QuantumCloudGuard:
    def __init__(self, require_pqc:bool=False, auth_leaves:int=16):
        self.keygen=ChaoticKeyGenerator(); self.kem=KEMProvider(require_pqc=require_pqc)
        self.pk,self.sk=self.kem.generate_keypair()
        self.auth=MerkleAuthenticator(auth_leaves); self.integrity=IntegrityVerifier(); self.audit=AuditChain()
        self.storage: Dict[str,ProtectedObject]={}

    def store(self, object_id:str, plaintext:bytes, user_id='owner', k:int=3,n:int=5):
        timings={}; t=time.perf_counter_ns(); key,rep=self.keygen.generate(); timings['keygen_ms']=(time.perf_counter_ns()-t)/1e6
        aad=canonical_json({'object_id':object_id,'user_id':user_id})
        t=time.perf_counter_ns(); aes=self._enc(key,plaintext,aad); timings['aes_encrypt_ms']=(time.perf_counter_ns()-t)/1e6
        t=time.perf_counter_ns(); kem=self.kem.wrap_session_key(self.pk,key); timings['kem_wrap_ms']=(time.perf_counter_ns()-t)/1e6
        protected=aes['ciphertext']+aes['tag']
        t=time.perf_counter_ns(); meta=self.integrity.metadata(protected); timings['integrity_ms']=(time.perf_counter_ns()-t)/1e6
        message=sha3(protected)+object_id.encode()
        t=time.perf_counter_ns(); sig=self.auth.sign(message); timings['auth_sign_ms']=(time.perf_counter_ns()-t)/1e6
        recovery=RecoveryManager(key,k,n)
        obj=ProtectedObject(object_id,aes,kem,meta,sig,self.auth.root,recovery,rep,timings)
        self.storage[object_id]=obj
        self.audit.append('STORE',user_id,object_id,'PASS',{'kem_backend':self.kem.backend,'threshold':f'{k}-of-{n}'})
        return obj

    def _enc(self,key,plaintext,aad): return AESGCMEngine.encrypt(key,plaintext,aad)

    def retrieve(self, object_id:str, user_id='owner', force_recovery:bool=False):
        obj=self.storage[object_id]; protected=obj.aes_pack['ciphertext']+obj.aes_pack['tag']
        msg=sha3(protected)+object_id.encode()
        if not MerkleAuthenticator.verify(obj.auth_root,msg,obj.auth_bundle):
            self.audit.append('RETRIEVE',user_id,object_id,'REJECT','auth failed'); raise PermissionError('authentication failed')
        if not self.integrity.verify(protected,obj.integrity):
            self.audit.append('RETRIEVE',user_id,object_id,'REJECT',{'reason':'integrity'}); raise ValueError('integrity verification failed')
        if not self.audit.validate(): raise ValueError('audit chain invalid')
        if not force_recovery:
            try: key=self.kem.unwrap_session_key(self.sk,obj.kem_pack)
            except Exception: key=obj.recovery.recover()
        else: key=obj.recovery.recover()
        plaintext=AESGCMEngine.decrypt(key,obj.aes_pack)
        self.audit.append('RETRIEVE',user_id,object_id,'PASS',{'recovery':force_recovery})
        return plaintext

    def tamper_ciphertext(self, object_id:str, offset:int=0):
        obj=self.storage[object_id]; c=bytearray(obj.aes_pack['ciphertext'])
        if not c: return
        c[offset%len(c)]^=1; obj.aes_pack['ciphertext']=bytes(c)

    def tamper_audit(self,index:int=0):
        if self.audit.records: self.audit.records[index]['result']='ALTERED'
