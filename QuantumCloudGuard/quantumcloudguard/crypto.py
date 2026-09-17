from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import x25519
from .utils import sha3

class AESGCMEngine:
    @staticmethod
    def encrypt(key: bytes, plaintext: bytes, aad: bytes=b'') -> dict:
        nonce=os.urandom(12)
        data=AESGCM(key).encrypt(nonce, plaintext, aad)
        return {'nonce':nonce, 'ciphertext':data[:-16], 'tag':data[-16:], 'aad':aad}
    @staticmethod
    def decrypt(key: bytes, package: dict) -> bytes:
        return AESGCM(key).decrypt(package['nonce'], package['ciphertext']+package['tag'], package.get('aad',b''))


def hkdf32(shared: bytes, info: bytes=b'QuantumCloudGuard-KEK') -> bytes:
    return HKDF(algorithm=hashes.SHA3_256(), length=32, salt=None, info=info).derive(shared)

class KEMProvider:
    """Auto-selects real ML-KEM-768 via oqs when available; otherwise uses an X25519 development KEM.
    The fallback preserves workflow functionality but MUST NOT be reported as post-quantum secure.
    """
    def __init__(self, algorithm='ML-KEM-768', require_pqc: bool=False):
        self.algorithm=algorithm
        self.backend='x25519-dev'
        self._oqs=None
        try:
            import oqs
            if algorithm in oqs.get_enabled_kem_mechanisms():
                self._oqs=oqs
                self.backend='liboqs-'+algorithm
        except Exception:
            pass
        if require_pqc and self._oqs is None:
            raise RuntimeError('Real ML-KEM requested but oqs/liboqs-python is not available.')

    def generate_keypair(self):
        if self._oqs:
            kem=self._oqs.KeyEncapsulation(self.algorithm)
            pk=kem.generate_keypair()
            sk=kem.export_secret_key()
            kem.free()
            return pk,sk
        sk=x25519.X25519PrivateKey.generate(); pk=sk.public_key()
        return (pk.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw),
                sk.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption()))

    def encapsulate(self, public_key: bytes):
        if self._oqs:
            kem=self._oqs.KeyEncapsulation(self.algorithm)
            ct,ss=kem.encap_secret(public_key); kem.free(); return ct,ss
        peer=x25519.X25519PublicKey.from_public_bytes(public_key)
        eph=x25519.X25519PrivateKey.generate(); shared=eph.exchange(peer)
        ct=eph.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return ct,sha3(shared)

    def decapsulate(self, secret_key: bytes, ciphertext: bytes):
        if self._oqs:
            kem=self._oqs.KeyEncapsulation(self.algorithm, secret_key)
            ss=kem.decap_secret(ciphertext); kem.free(); return ss
        sk=x25519.X25519PrivateKey.from_private_bytes(secret_key)
        eph=x25519.X25519PublicKey.from_public_bytes(ciphertext)
        return sha3(sk.exchange(eph))

    def wrap_session_key(self, public_key: bytes, session_key: bytes):
        kem_ct,ss=self.encapsulate(public_key); kek=hkdf32(ss)
        wrapped=AESGCM(kek).encrypt(b'\x00'*12, session_key, kem_ct)
        return {'kem_ciphertext':kem_ct,'wrapped_key':wrapped,'backend':self.backend}

    def unwrap_session_key(self, secret_key: bytes, pack: dict):
        ss=self.decapsulate(secret_key, pack['kem_ciphertext']); kek=hkdf32(ss)
        return AESGCM(kek).decrypt(b'\x00'*12, pack['wrapped_key'], pack['kem_ciphertext'])
