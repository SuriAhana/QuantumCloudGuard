import os
from quantumcloudguard.pipeline import QuantumCloudGuard
from quantumcloudguard.recovery import Shamir
from quantumcloudguard.audit import AuditChain
from quantumcloudguard.integrity import IntegrityVerifier


def test_end_to_end():
    q=QuantumCloudGuard()
    data=b'hello quantum cloud guard'*100
    q.store('x',data)
    assert q.retrieve('x')==data


def test_tamper_detected():
    q=QuantumCloudGuard(); q.store('x',b'abc'*1000); q.tamper_ciphertext('x')
    try:
        q.retrieve('x')
        assert False
    except (ValueError, PermissionError):
        assert True


def test_shamir():
    key=os.urandom(32); shares=Shamir.split(key,3,5)
    assert Shamir.combine([shares[0],shares[2],shares[4]],32)==key


def test_audit():
    a=AuditChain(); a.append('STORE','u','o','PASS'); a.append('READ','u','o','PASS')
    assert a.validate(); a.records[0]['result']='FAIL'; assert not a.validate()


def test_integrity():
    v=IntegrityVerifier(16); d=b'abcdef'*100; m=v.metadata(d)
    assert v.verify(d,m); assert not v.verify(d+b'x',m)
