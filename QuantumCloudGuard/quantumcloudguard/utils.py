import base64, hashlib, json, os, time
from dataclasses import dataclass
from typing import Any, Dict


def sha3(data: bytes) -> bytes:
    return hashlib.sha3_256(data).digest()


def b64e(b: bytes) -> str:
    return base64.b64encode(b).decode('ascii')


def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode('ascii'))


def canonical_json(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def now_ns() -> int:
    return time.perf_counter_ns()


def elapsed_ms(start_ns: int) -> float:
    return (time.perf_counter_ns() - start_ns) / 1e6


def secure_random(n: int) -> bytes:
    return os.urandom(n)

@dataclass
class TimerResult:
    value: Any
    ms: float
