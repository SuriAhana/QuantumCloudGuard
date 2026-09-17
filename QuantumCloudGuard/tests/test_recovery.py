from quantumcloudguard.pipeline import QuantumCloudGuard

def test_threshold_recovery_success():
    q=QuantumCloudGuard(); obj=q.store('x',b'data'*100,k=3,n=5)
    obj.recovery.nodes[0].available=False
    obj.recovery.nodes[1].available=False
    assert q.retrieve('x',force_recovery=True)==b'data'*100

def test_threshold_recovery_failure():
    q=QuantumCloudGuard(); obj=q.store('x',b'data'*100,k=3,n=5)
    for node in obj.recovery.nodes[:3]: node.available=False
    try:
        q.retrieve('x',force_recovery=True)
        assert False
    except RuntimeError:
        assert True
