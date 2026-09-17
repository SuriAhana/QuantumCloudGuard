# QuantumCloudGuard

*A Quantum-Inspired Hybrid Cryptographic Framework for Secure and Resilient Cloud Data Protection*

QuantumCloudGuard is a reproducible research implementation of a hybrid cloud-security framework that integrates quantum-inspired chaotic key generation, AES-GCM authenticated encryption, post-quantum key encapsulation, hash-based authentication, ciphertext integrity verification, tamper-evident audit logging, and threshold-based fault-tolerant recovery.

The framework is designed as a system-level security architecture rather than a new standalone cryptographic primitive. Its goal is to jointly support confidentiality, authentication, integrity, auditability, post-quantum key protection, and resilience within a unified cloud data-protection workflow.

# 1. Main Features

- Coupled logistic-tent chaotic sequence generation
- Session-specific 256-bit key derivation
- Statistical randomness evaluation
- AES-256-GCM authenticated data encryption
- ML-KEM-768 post-quantum key encapsulation through Open Quantum Safe
- X25519 development fallback when liboqs is unavailable
- Lamport one-time hash signatures
- Merkle-tree-based authentication
- SHA3-256 ciphertext block integrity commitments
- Merkle aggregation of integrity metadata
- Tamper-evident hash-chained audit logging
- Shamir Secret Sharing
- 3-of-5 threshold recovery
- 4-of-7 threshold recovery
- Ciphertext-tampering experiments
- Authentication attack experiments
- Replay-attack simulation
- Audit-log manipulation detection
- Node-failure and recovery experiments
- Baseline comparison
- Component ablation experiments
- Repeated-run statistical evaluation
- Lightweight Python cloud workload simulation
- CloudSim Plus integration
- CSV and JSON result generation

# 2. Framework Architecture

The overall security workflow is:

```text
Input Data
    |
    v
Quantum-Inspired Chaotic Key Generator
    |
    v
Session-Key Derivation
    |
    v
AES-256-GCM Encryption
    |
    v
ML-KEM Post-Quantum Key Protection
    |
    v
Merkle/Hash-Based Authentication
    |
    v
Ciphertext Integrity Metadata
    |
    v
Tamper-Evident Audit Logging
    |
    v
Encrypted Cloud Storage
    |
    +-----------------------------+
    |                             |
    v                             v
Normal Secure Retrieval     Threshold Recovery
                                  |
                                  v
                          Shamir Secret Sharing
                                  |
                                  v
                          Secure Key Restoration
                                  |
                                  v
                          Integrity Revalidation
```

The implementation separates bulk-data encryption from post-quantum key protection. AES-GCM protects large data objects efficiently, while ML-KEM protects key-management material.

# 3. Important Security Interpretation

## 3.1 Quantum-Inspired Key Generation

The chaotic key generator should not be interpreted as an independently proven cryptographically secure random-number generator. The logistic and tent maps are used as an experimental entropy-diversification mechanism.

```text
Chaotic sequence
       +
Operating-system entropy
       |
       v
HKDF-based derivation
       |
       v
256-bit AES session key
```

Therefore, the security of encrypted data does not rely solely on chaotic dynamics.

## 3.2 Post-Quantum Security

When Open Quantum Safe is available, QuantumCloudGuard uses ML-KEM-768 for post-quantum key establishment.

If Open Quantum Safe is unavailable, the implementation can automatically use X25519 to allow development and functional testing.

**Important:** X25519 is not post-quantum secure and results obtained in X25519 development mode must not be reported as ML-KEM or post-quantum experimental results.

For publication-quality PQC experiments, always execute the framework using:

```bash
--require-pqc
```

## 3.3 Integrity Verification

The current reproducible implementation uses ciphertext blocks, SHA3-256 block hashes, and Merkle aggregation to create integrity commitments. This allows encrypted data to be verified without accessing plaintext. The implementation deliberately does not describe ordinary SHA3 hashing as an algebraically homomorphic cryptographic hash.

# 4. Repository Structure

```text
QuantumCloudGuard/
|
├── README.md
├── requirements.txt
├── pyproject.toml
|
├── config/
│   ├── quick.yaml
│   └── paper.yaml
|
├── data/
│   ├── google_trace/
│   ├── alibaba_trace/
│   ├── processed/
│   └── synthetic_files/
|
├── src/
│   └── quantumcloudguard/
│       ├── keygen/
│       ├── crypto/
│       ├── authentication/
│       ├── integrity/
│       ├── audit/
│       ├── recovery/
│       ├── attacks/
│       ├── workloads/
│       ├── metrics/
│       └── pipeline/
|
├── experiments/
├── cloudsim/
├── results/
└── tests/
```

# 5. Requirements

Recommended environment:

- Python 3.10+
- Java 17+
- Maven 3.8+
- Linux / Ubuntu recommended

Major Python dependencies include:

```text
cryptography
numpy
pandas
scipy
matplotlib
PyYAML
pytest
```

Optional post-quantum dependency: Open Quantum Safe liboqs and oqs-python.

# 6. Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/QuantumCloudGuard.git
cd QuantumCloudGuard
```

Create and activate a Python virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

On Windows, activate the environment using:

```text
.venv\Scripts\activate
```

# 7. Open Quantum Safe / ML-KEM Setup

For actual post-quantum experiments, install Open Quantum Safe liboqs and its Python bindings. After installation, verify that ML-KEM-768 is available:

```bash
python -c "import oqs; print('ML-KEM-768' in oqs.get_enabled_kem_mechanisms())"
```

Expected output:

```text
True
```

If `False` is returned, verify the liboqs installation and enabled algorithms.

# 8. Quick End-to-End Demo

```bash
python -m quantumcloudguard demo
```

This executes the principal pipeline from input data through key generation, encryption, key protection, authentication, integrity metadata, audit logging, storage, retrieval, verification, and decryption.

# 9. Require Real Post-Quantum Cryptography

```bash
python -m quantumcloudguard demo --require-pqc
```

If ML-KEM-768 is unavailable, execution terminates rather than silently using a non-PQC fallback. This mode should be used for manuscript experiments.

# 10. Automated Testing

```bash
pytest -q
```

The tests cover AES-GCM encryption/decryption, modified-ciphertext rejection, audit-chain validation, integrity-verification logic, Shamir share generation, threshold reconstruction, threshold recovery, and secure retrieval workflow.

# 11. Quick Experimental Run

```bash
python -m quantumcloudguard experiment \
  --profile quick \
  --out results/quick
```

The quick profile is intended for debugging, CI testing, workflow validation, and code demonstration. It should not replace the complete manuscript-scale evaluation.

# 12. Manuscript-Scale Experimental Run

```bash
python -m quantumcloudguard experiment \
  --profile paper \
  --out results/paper \
  --require-pqc
```

The paper profile uses the manuscript-aligned experimental configuration.

| Category | Values |
|---|---|
| Data object sizes | 10, 50, 100, 250, 500 MB |
| Workload sizes | 1,000; 5,000; 10,000; 25,000; 50,000 jobs |
| Concurrent requests | 50; 120; 250; 500; 900 |
| Repetitions | 10 independent runs per configuration |

# 13. Complete Quick Workflow

```bash
python run_all_quick.py
```

Use this convenience runner to verify that the principal experimental components operate correctly before launching manuscript-scale experiments.

# 14. Chaotic Session-Key Generation

The key-generation module combines logistic and tent maps. The generated states undergo transient-state removal, coupled-sequence generation, normalization, threshold quantization, bias filtering, statistical validation, entropy mixing, and 256-bit key derivation.

# 15. Randomness Evaluation

- Normalized Shannon entropy
- Frequency test
- Block Frequency test
- Runs test
- Longest Run test
- Binary Matrix Rank test
- FFT test
- Serial test
- Approximate Entropy test

A typical statistical acceptance threshold is `p >= 0.01`. Passing statistical randomness tests should not be interpreted as a formal proof of cryptographic unpredictability.

# 16. AES-256-GCM Encryption

Bulk cloud data are encrypted using AES-256-GCM, providing confidentiality, ciphertext authentication, and tamper detection. Each encryption operation uses a session-specific 256-bit key, a fresh nonce, and an authentication tag.

# 17. ML-KEM Key Protection

ML-KEM operates as a key-encapsulation mechanism rather than conventional arbitrary-message encryption. The implementation therefore derives a key-encryption key from the KEM shared secret and uses it to protect the AES session key.

```text
ML-KEM Encapsulation
        |
        v
Shared Secret
        |
        v
HKDF
        |
        v
Key Encryption Key
        |
        v
AES Session-Key Protection
```

# 18. Authentication

QuantumCloudGuard uses Lamport One-Time Signatures together with Merkle Tree Authentication. The Merkle root acts as a compact trust anchor for many one-time verification keys.

An access request may include a user ID, object ID, operation, timestamp, nonce, one-time signature, OTS public key, and Merkle authentication path.

# 19. Integrity Verification

Protected cloud objects are split into fixed-size blocks, each block is hashed using SHA3-256, and the block commitments are aggregated through a Merkle structure. During retrieval, the stored integrity commitment is compared with a recomputed commitment.

# 20. Tamper-Evident Audit Logging

QuantumCloudGuard uses blockchain-inspired hash chaining without implementing a public blockchain consensus mechanism. Each audit record contains a sequence number, timestamp, user identifier, object identifier, security event, result, previous record hash, and current record hash.

# 21. Threshold Recovery

QuantumCloudGuard implements Shamir Secret Sharing with 3-of-5 and 4-of-7 configurations. At least `k` valid shares are required for reconstruction using Lagrange interpolation. After key recovery, the data are decrypted and subjected to post-recovery integrity verification before release.

# 22. Attack and Resilience Experiments

```bash
python experiments/attack_suite.py
```

The experiments include:

- Ciphertext modification
- Authentication failure
- Invalid signature attempts
- Replay attempts
- Integrity-metadata corruption
- Audit-chain manipulation
- Unavailable recovery nodes
- Corrupted recovery shares
- Threshold failure
- Malformed cryptographic material

These modules are designed for controlled defensive evaluation of the framework.

# 23. Ablation Study

```bash
python experiments/ablation.py
```

The ablation study evaluates the contribution of individual components. Example configurations include the full framework and variants with the chaotic entropy module, ML-KEM layer, Merkle authentication, integrity-verification layer, audit chaining, or threshold recovery removed.

# 24. CloudSim Plus Integration

The Java cloud-simulation project is located in `cloudsim/`. Compile and run it using:

```bash
cd cloudsim
mvn -q compile exec:java -Dexec.args="2.5 1000"
```

The arguments correspond to `security_overhead_ms` and `job_count`.

# 25. Manuscript-Aligned Cloud Configuration

| Parameter | Value |
|---|---:|
| Hosts | 20 |
| Processing elements per host | 8 |
| RAM per host | 16 GB |
| Host storage | 1 TB |
| Host bandwidth | 10 Gbps |
| Virtual machines | 50 |
| vCPUs per VM | 2 |
| RAM per VM | 4 GB |
| VM storage | 100 GB |
| VM bandwidth | 1 Gbps |
| VM scheduling | Time-shared |

# 26. Python-CloudSim Experimental Workflow

```text
Python cryptographic experiments
            |
            v
Measure actual security-operation latency
            |
            v
Generate CSV/JSON statistics
            |
            v
Feed measured security overhead to CloudSim
            |
            v
Execute workload-scaling experiments
            |
            v
Analyze end-to-end cloud behaviour
```

This avoids using arbitrary cryptographic delay assumptions inside the cloud simulator.

# 27. Google Cluster Trace and Alibaba Cluster Trace

The large public cloud traces are not bundled with this repository. They should be obtained separately from their official sources because of their size.

They are used to model job arrival patterns, execution durations, CPU demand, memory demand, workload intensity, and concurrent activity. They are not used directly as encrypted application files.

Example processed structure:

```text
job_id,cpu,memory,duration_ms,arrival_ms
```

# 28. Result Files

Experiment outputs are written under `results/`.

Typical CSV outputs may include:

- `key_randomness.csv`
- `encryption_scaling.csv`
- `retrieval_scaling.csv`
- `workload_scaling.csv`
- `authentication.csv`
- `integrity.csv`
- `recovery.csv`
- `attack_results.csv`
- `ablation.csv`
- `baseline_comparison.csv`

# 29. Performance Metrics

- Key-generation latency
- AES encryption/decryption time
- KEM encapsulation/decapsulation time
- Authentication generation/verification time
- Integrity generation/verification time
- Audit-write latency
- Recovery latency
- End-to-end storage/retrieval latency
- Throughput
- CPU utilization
- Memory utilization
- Storage overhead
- P95 latency

# 30. Security Metrics

**Key quality:** normalized Shannon entropy and statistical randomness-test outcomes.

**Authentication:** accuracy, precision, recall, F1-score, False Acceptance Rate, and False Rejection Rate.

**Integrity verification:** accuracy, TPR, TNR, FPR, FNR, and tamper detection rate.

**Auditability:** audit manipulation detection rate.

**Recovery:** recovery success rate, failure rate, recovery latency, and threshold availability.

# 31. Statistical Reporting

For the manuscript profile, each configuration should be independently executed 10 times. Report mean, standard deviation, 95% confidence interval, median, and P95 latency where applicable.

```text
CI95 = mean ± t × SD / sqrt(n)
```

where `n = 10`.

# 32. Baseline Evaluation

- **B1:** AES-GCM only
- **B2:** AES-GCM + classical asymmetric key protection
- **B3:** AES-GCM + ML-KEM
- **B4:** Full QuantumCloudGuard

Additional resilience-oriented comparisons can remove threshold recovery, audit chaining, or integrity verification to determine their individual system-level contributions.



