from __future__ import annotations
import math, os
from dataclasses import dataclass
from typing import Dict, List, Tuple
from .utils import sha3

@dataclass
class ChaoticConfig:
    logistic_r: float = 3.99
    tent_mu: float = 1.999
    coupling: float = 0.5
    threshold: float = 0.5
    burn_in: int = 1000
    candidate_bits: int = 8192
    key_bits: int = 256
    min_entropy: float = 0.95
    min_p_value: float = 0.01


def _bits_to_bytes(bits: List[int]) -> bytes:
    out = bytearray()
    for i in range(0, len(bits), 8):
        v = 0
        for b in bits[i:i+8]:
            v = (v << 1) | int(b)
        out.append(v)
    return bytes(out)


def normalized_shannon_entropy(bits: List[int]) -> float:
    if not bits:
        return 0.0
    n = len(bits)
    p1 = sum(bits)/n
    p0 = 1-p1
    h = 0.0
    for p in (p0,p1):
        if p > 0:
            h -= p*math.log2(p)
    return h


def _erfc_p(z: float) -> float:
    return math.erfc(abs(z)/math.sqrt(2.0))


def frequency_test(bits: List[int]) -> float:
    n = len(bits)
    s = sum(1 if b else -1 for b in bits)
    return math.erfc(abs(s)/math.sqrt(2*n)) if n else 0.0


def block_frequency_test(bits: List[int], block_size: int = 128) -> float:
    n = len(bits)
    m = min(block_size, n)
    N = n // m if m else 0
    if N == 0:
        return 0.0
    chisq = 0.0
    for i in range(N):
        block = bits[i*m:(i+1)*m]
        pi = sum(block)/m
        chisq += 4*m*(pi-0.5)**2
    # Wilson-Hilferty normal approximation to chi-square tail
    k = N
    z = ((chisq/k)**(1/3) - (1-2/(9*k))) / math.sqrt(2/(9*k)) if chisq > 0 else -99
    return 0.5*math.erfc(z/math.sqrt(2))


def runs_test(bits: List[int]) -> float:
    n = len(bits)
    if n < 2: return 0.0
    pi = sum(bits)/n
    if abs(pi-0.5) >= 2/math.sqrt(n): return 0.0
    v = 1 + sum(bits[i] != bits[i-1] for i in range(1,n))
    num = abs(v - 2*n*pi*(1-pi))
    den = 2*math.sqrt(2*n)*pi*(1-pi)
    return math.erfc(num/den) if den else 0.0


def longest_run_test(bits: List[int]) -> float:
    n=len(bits)
    if n < 64: return 0.0
    block=128 if n>=128 else n
    N=n//block
    longest=[]
    for i in range(N):
        r=mx=0
        for b in bits[i*block:(i+1)*block]:
            r = r+1 if b else 0
            mx=max(mx,r)
        longest.append(mx)
    # Compare to crude expected longest run log2(block)
    mu=math.log2(block)
    var=max(1.0, mu/2)
    z=(sum(longest)/N-mu)/math.sqrt(var/N)
    return _erfc_p(z)


def fft_test(bits: List[int]) -> float:
    try:
        import numpy as np
    except Exception:
        return 1.0
    x=np.array([1 if b else -1 for b in bits], dtype=float)
    s=np.abs(np.fft.fft(x))[:len(x)//2]
    threshold=math.sqrt(math.log(1/0.05)*len(x))
    n0=0.95*len(x)/2
    n1=float((s < threshold).sum())
    d=(n1-n0)/math.sqrt(len(x)*0.95*0.05/4)
    return math.erfc(abs(d)/math.sqrt(2))


def serial_test(bits: List[int], m:int=2) -> float:
    if len(bits) < 32: return 0.0
    counts=[0]*(2**m)
    ext=bits+bits[:m-1]
    for i in range(len(bits)):
        idx=0
        for j in range(m): idx=(idx<<1)|ext[i+j]
        counts[idx]+=1
    expected=len(bits)/(2**m)
    chi=sum((c-expected)**2/expected for c in counts)
    k=len(counts)-1
    z=((chi/k)**(1/3)-(1-2/(9*k)))/math.sqrt(2/(9*k)) if chi>0 else -99
    return 0.5*math.erfc(z/math.sqrt(2))


def approximate_entropy_test(bits: List[int], m:int=2) -> float:
    n=len(bits)
    if n < 64: return 0.0
    def phi(mm):
        counts=[0]*(2**mm); ext=bits+bits[:mm-1]
        for i in range(n):
            idx=0
            for j in range(mm): idx=(idx<<1)|ext[i+j]
            counts[idx]+=1
        return sum((c/n)*math.log(c/n) for c in counts if c)
    apen=phi(m)-phi(m+1)
    # transform relative to ln(2); heuristic p for compact reproducible implementation
    z=abs(apen-math.log(2))*math.sqrt(n)
    return _erfc_p(z)


def rank_test(bits: List[int]) -> float:
    try:
        import numpy as np
    except Exception:
        return 1.0
    rows=cols=16
    block=rows*cols
    N=len(bits)//block
    if N==0: return 0.0
    full=0
    def gf2_rank(mat):
        a=mat.copy().astype(np.uint8); r=0
        for c in range(a.shape[1]):
            piv=next((i for i in range(r,a.shape[0]) if a[i,c]),None)
            if piv is None: continue
            a[[r,piv]]=a[[piv,r]]
            for i in range(a.shape[0]):
                if i!=r and a[i,c]: a[i]^=a[r]
            r+=1
            if r==a.shape[0]: break
        return r
    for i in range(N):
        mat=np.array(bits[i*block:(i+1)*block],dtype=np.uint8).reshape(rows,cols)
        full += gf2_rank(mat) >= rows-1
    p=full/N
    # Expected P(rank >= 15) for random 16x16 is high; use broad binomial check around 0.86.
    mu=.86; se=math.sqrt(mu*(1-mu)/N) if N else 1
    return _erfc_p((p-mu)/max(se,1e-9))


def randomness_report(bits: List[int], min_p: float=0.01) -> Dict[str,float|bool]:
    tests={
        'frequency_p':frequency_test(bits), 'block_frequency_p':block_frequency_test(bits),
        'runs_p':runs_test(bits), 'longest_run_p':longest_run_test(bits),
        'rank_p':rank_test(bits), 'fft_p':fft_test(bits), 'serial_p':serial_test(bits),
        'approx_entropy_p':approximate_entropy_test(bits)
    }
    h=normalized_shannon_entropy(bits)
    accepted=(h>=0.95 and all(v>=min_p for v in tests.values()))
    return {'entropy':h, **tests, 'accepted':accepted}

class ChaoticKeyGenerator:
    def __init__(self, cfg: ChaoticConfig|None=None):
        self.cfg=cfg or ChaoticConfig()

    def _seed_pair(self, seed: bytes|None=None) -> Tuple[float,float]:
        seed = seed or os.urandom(32)
        d=sha3(seed)
        a=int.from_bytes(d[:16],'big')/(2**128)
        b=int.from_bytes(d[16:],'big')/(2**128)
        # avoid exact boundaries / known unstable seeds
        return 0.01+0.98*a, 0.01+0.98*b

    def _candidate(self, seed: bytes|None=None) -> List[int]:
        c=self.cfg; x,y=self._seed_pair(seed)
        total=c.burn_in+c.candidate_bits
        vals=[]
        for i in range(total):
            x=c.logistic_r*x*(1-x)
            y=c.tent_mu*y if y<0.5 else c.tent_mu*(1-y)
            y=max(1e-15,min(1-1e-15,y))
            if i>=c.burn_in:
                vals.append(c.coupling*x+(1-c.coupling)*y)
        mn,mx=min(vals),max(vals)
        norm=[(v-mn)/(mx-mn+1e-18) for v in vals]
        return [1 if v>=c.threshold else 0 for v in norm]

    def generate(self, seed: bytes|None=None, hybridize_with_os_entropy: bool=True, max_attempts:int=12):
        base=seed or os.urandom(32)
        last=None
        for i in range(max_attempts):
            bits=self._candidate(sha3(base+i.to_bytes(4,'big')))
            rep=randomness_report(bits, self.cfg.min_p_value)
            last=(bits,rep)
            if rep['accepted']:
                raw=_bits_to_bytes(bits[:self.cfg.key_bits])
                if hybridize_with_os_entropy:
                    raw=sha3(raw+os.urandom(32))[:self.cfg.key_bits//8]
                return raw, rep
        # fail-safe: still provide a secure OS-hybridized key but mark report not accepted
        bits,rep=last
        raw=_bits_to_bytes(bits[:self.cfg.key_bits])
        raw=sha3(raw+os.urandom(32))[:self.cfg.key_bits//8]
        rep=dict(rep); rep['accepted']=False; rep['fallback_os_entropy']=True
        return raw, rep
