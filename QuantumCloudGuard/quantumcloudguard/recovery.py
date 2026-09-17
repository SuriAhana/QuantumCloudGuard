from __future__ import annotations
import secrets
from dataclasses import dataclass
from typing import List,Tuple

P=(1<<521)-1

def _inv(a,p=P): return pow(a,p-2,p)

class Shamir:
    @staticmethod
    def split(secret:bytes,k:int,n:int):
        if not (2<=k<=n): raise ValueError('require 2 <= k <= n')
        s=int.from_bytes(secret,'big')
        coeff=[s]+[secrets.randbelow(P) for _ in range(k-1)]
        shares=[]
        for x in range(1,n+1):
            y=0
            for c in reversed(coeff): y=(y*x+c)%P
            shares.append((x,y))
        return shares
    @staticmethod
    def combine(shares:List[Tuple[int,int]], out_len:int=32):
        if not shares: raise ValueError('no shares')
        s=0
        for j,(xj,yj) in enumerate(shares):
            num=den=1
            for m,(xm,_) in enumerate(shares):
                if m==j: continue
                num=(num*(-xm))%P; den=(den*(xj-xm))%P
            s=(s+yj*num*_inv(den))%P
        return s.to_bytes(out_len,'big')

@dataclass
class RecoveryNode:
    node_id:int
    share:tuple
    available:bool=True
    corrupted:bool=False
    def get_share(self):
        if not self.available: return None
        x,y=self.share
        return (x,(y+1)%P) if self.corrupted else self.share

class RecoveryManager:
    def __init__(self,key:bytes,k:int=3,n:int=5):
        self.k=k; self.n=n
        shares=Shamir.split(key,k,n)
        self.nodes=[RecoveryNode(i+1,s) for i,s in enumerate(shares)]
    def recover(self,validator=None):
        valid=[]
        for node in self.nodes:
            s=node.get_share()
            if s is None: continue
            if validator and not validator(node,s): continue
            valid.append(s)
            if len(valid)>=self.k: break
        if len(valid)<self.k: raise RuntimeError('threshold unavailable')
        return Shamir.combine(valid,self_key_len(self))

def self_key_len(manager): return 32
