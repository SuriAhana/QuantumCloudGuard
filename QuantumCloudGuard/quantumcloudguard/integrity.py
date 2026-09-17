from __future__ import annotations
from .utils import sha3
from .auth import build_tree

class IntegrityVerifier:
    def __init__(self, block_size:int=4096): self.block_size=block_size
    def metadata(self, protected:bytes):
        blocks=[protected[i:i+self.block_size] for i in range(0,len(protected),self.block_size)] or [b'']
        hashes=[sha3(b) for b in blocks]
        root=build_tree(hashes)[-1][0]
        return {'block_size':self.block_size,'block_hashes':hashes,'root':root,'count':len(blocks)}
    def verify(self, protected:bytes, meta:dict)->bool:
        m=self.metadata(protected)
        return m['root']==meta['root'] and m['count']==meta['count']
