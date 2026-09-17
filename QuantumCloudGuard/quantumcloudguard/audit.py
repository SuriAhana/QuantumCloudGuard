from __future__ import annotations
import time
from .utils import sha3, canonical_json, b64e

class AuditChain:
    def __init__(self): self.records=[]
    def append(self, event:str, user_id:str, object_id:str, result:str, details:dict|None=None):
        prev=self.records[-1]['entry_hash'] if self.records else 'GENESIS'
        core={'seq':len(self.records),'timestamp_ns':time.time_ns(),'event':event,'user_id':user_id,
              'object_id':object_id,'result':result,'details':details or {},'previous_hash':prev}
        core['entry_hash']=b64e(sha3(canonical_json(core)))
        self.records.append(core); return core
    def validate(self)->bool:
        prev='GENESIS'
        for i,r in enumerate(self.records):
            if r.get('seq')!=i or r.get('previous_hash')!=prev: return False
            core={k:v for k,v in r.items() if k!='entry_hash'}
            if b64e(sha3(canonical_json(core)))!=r.get('entry_hash'): return False
            prev=r['entry_hash']
        return True
