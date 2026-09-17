# QuantumCloudGuard — Reproducible Research Implementation

This repository implements the manuscript architecture as an executable research prototype:

- coupled logistic–tent chaotic session-key generation;
- entropy/randomness testing;
- AES-256-GCM authenticated bulk encryption;
- ML-KEM-768 through Open Quantum Safe when `oqs` is installed;
- automatic X25519 development fallback when liboqs is unavailable;
- Lamport one-time hash signatures authenticated by a Merkle tree;
- ciphertext block-integrity commitments;
- tamper-evident hash-chained audit logging;
- Shamir 3-of-5 and 4-of-7 threshold recovery;
- controlled tamper, audit, node-failure and recovery experiments;
- lightweight Python cloud workload simulator;
- CloudSim Plus Java runner using the manuscript's 20-host/50-VM configuration;
- repeated-run statistics and CSV/JSON outputs.

## Important security interpretation

The chaotic generator is an experimental entropy-diversification source, not an independently proven cryptographic RNG. The default key-generation path mixes its output with operating-system entropy before deriving the 256-bit session key.

If Open Quantum Safe is available, the KEM layer uses **ML-KEM-768**. If it is not available, the code automatically uses **X25519 development mode** so the complete workflow remains runnable. X25519 mode is **not post-quantum secure and must not be reported as ML-KEM/PQC results**. Use `--require-pqc` to make the program fail instead of falling back.

The manuscript leaves the exact algebraic homomorphic-hash realization implementation-specific. This repository therefore implements reproducible block SHA3-256 commitments aggregated with a Merkle root. It verifies protected ciphertext without plaintext access, but the code does not mislabel ordinary SHA3 as an algebraically homomorphic hash.

## 1. Installation

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
# .venv\\Scripts\\activate
pip install -r requirements.txt
pip install -e .
```

For real ML-KEM-768, install Open Quantum Safe `liboqs` and its Python binding, then confirm:

```bash
python -c "import oqs; print('ML-KEM-768' in oqs.get_enabled_kem_mechanisms())"
```

## 2. Run end-to-end demo

```bash
python -m quantumcloudguard demo
```

Require real PQC:

```bash
python -m quantumcloudguard demo --require-pqc
```

## 3. Run automated tests

```bash
pytest -q
```

## 4. Run experiments

Quick smoke-test profile:

```bash
python -m quantumcloudguard experiment --profile quick --out results/quick
```

Manuscript-scale profile (10 independent runs; 10/50/100/250/500 MB):

```bash
python -m quantumcloudguard experiment --profile paper --out results/paper --require-pqc
```

The paper profile can be computationally expensive and should be run on the manuscript workstation or an equivalent Linux machine.

## 5. Attack/resilience suite

```bash
python experiments/attack_suite.py
```

## 6. Ablation example

```bash
python experiments/ablation.py
```

## 7. CloudSim Plus

The Java project is under `cloudsim/`. Maven downloads CloudSim Plus on first run.

```bash
cd cloudsim
mvn -q compile exec:java -Dexec.args="2.5 1000"
```

Arguments are `security_overhead_ms` and `job_count`. The runner instantiates 20 hosts and 50 VMs with time-shared scheduling. For publication experiments, feed measured median/mean cryptographic latency from the Python output into this runner.

## 8. Google Cluster Trace / Alibaba Cluster Trace

The large public traces are not bundled in the ZIP. They should be downloaded from their official repositories. Normalize selected events to CSV columns:

```text
job_id,cpu,memory,duration_ms,arrival_ms
```

Then `quantumcloudguard.workloads.load_generic_trace()` can ingest the normalized trace. The trace is used to drive arrival/resource patterns; it is not treated as the encrypted payload itself.



