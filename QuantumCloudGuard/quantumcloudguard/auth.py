from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List, Tuple
from .utils import sha3

# Compact Lamport one-time signature + Merkle authentication.
def _msg_digest(message: bytes) -> bytes: return sha3(message)

class LamportOTS:
    @staticmethod
    def keygen():
        sk=[(os.urandom(32),os.urandom(32)) for _ in range(256)]
        pk=[(sha3(a),sha3(b)) for a,b in sk]
        return sk,pk
    @staticmethod
    def pk_bytes(pk):
        return b''.join(a+b for a,b in pk)
    @staticmethod
    def sign(sk,message:bytes):
        d=_msg_digest(message); bits=[(d[i//8]>>(7-i%8))&1 for i in range(256)]
        return [sk[i][bits[i]] for i in range(256)]
    @staticmethod
    def verify(pk,message:bytes,sig):
        if len(sig)!=256: return False
        d=_msg_digest(message); bits=[(d[i//8]>>(7-i%8))&1 for i in range(256)]
        return all(sha3(sig[i])==pk[i][bits[i]] for i in range(256))


def merkle_parent(a:bytes,b:bytes)->bytes: return sha3(a+b)

def build_tree(leaves: List[bytes]):
    if not leaves: raise ValueError('no leaves')
    levels=[leaves]
    cur=leaves
    while len(cur)>1:
        if len(cur)%2: cur=cur+[cur[-1]]
        cur=[merkle_parent(cur[i],cur[i+1]) for i in range(0,len(cur),2)]
        levels.append(cur)
    return levels

def auth_path(levels,index:int):
    path=[]; idx=index
    for level in levels[:-1]:
        sib=idx^1
        if sib>=len(level): sib=idx
        path.append((level[sib], sib<idx))
        idx//=2
    return path

def verify_path(leaf:bytes,index:int,path,root:bytes):
    h=leaf
    for sibling,is_left in path:
        h=merkle_parent(sibling,h) if is_left else merkle_parent(h,sibling)
    return h==root

class MerkleAuthenticator:
    def __init__(self, leaf_count:int=8):
        n=1
        while n<leaf_count: n*=2
        self.keys=[]; leaves=[]
        for _ in range(n):
            sk,pk=LamportOTS.keygen(); self.keys.append([sk,pk,False]); leaves.append(sha3(LamportOTS.pk_bytes(pk)))
        self.levels=build_tree(leaves); self.root=self.levels[-1][0]
    def sign(self,message:bytes):
        for i,(sk,pk,used) in enumerate(self.keys):
            if not used:
                self.keys[i][2]=True
                return {'index':i,'signature':LamportOTS.sign(sk,message),'public_key':pk,'path':auth_path(self.levels,i)}
        raise RuntimeError('all one-time keys exhausted')
    @staticmethod
    def verify(root:bytes,message:bytes,bundle:dict)->bool:
        pk=bundle['public_key']
        if not LamportOTS.verify(pk,message,bundle['signature']): return False
        leaf=sha3(LamportOTS.pk_bytes(pk))
        return verify_path(leaf,bundle['index'],bundle['path'],root)
