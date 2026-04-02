# QDay Prize Submission — Breaking ECC Keys with Shor's Algorithm

**12-bit is the largest ECC key broken on real quantum hardware as of April 2026.**

This repository contains verified IBM Quantum hardware results for ECDLP key recovery using Shor's algorithm, with scaling evidence from 4-bit through 12-bit subgroup sizes.

**Contact:** Aaron@vexaai.app

---

## Results

| Bit | n | p | d (recovered) | Qubits | Shots | Hits | Success Rate | Job ID |
|-----|---|---|---------------|--------|-------|------|-------------|--------|
| 4-bit | 7 | 13 | **6** | — | 5,000 | 96 | 1.92% | `d53hle9smlfc739eskn0` |
| 6-bit | 31 | 43 | **18** | — | 20,000 | 583 | 2.915% | `d53i7nfp3tbc73amgl2g` |
| 7-bit | 79 | 67 | **56** | — | 50,000 | 565 | 1.13% | `d53ijmgnsj9s73b0vf60` |
| 9-bit | 313 | 349 | **135** | 41 | 20,000 | 51 | 0.255% | `d762t2u8faus73f0ofe0` |
| 9-bit | 313 | 349 | **135** | 41 | 20,000 | 75 | 0.375% | `d762r7u8faus73f0ode0` |
| 10-bit | 547 | 547 | **165** | 45 | 20,000 | 38 | 0.190% | `d762v3a3qcgc73fsedeg` |
| 11-bit | 1093 | 1051 | **756** | 49 | 20,000 | 16 | 0.080% | `d76rg3er8g3s73d93dug` |
| 12-bit | 2143 | 2089 | **1384** | 53 | 20,000 | 12 | 0.060% | `d76rn746ji0c738c2nsg` |

All results EC-verified: `d·G = Q` confirmed on the competition curve `y² = x³ + 7`.
All jobs publicly auditable at: https://quantum.ibm.com/

**Backends:** ibm_torino and ibm_fez (IBM Heron r1, ~0.05% 2Q gate error)
**Dates:** March 31, 2026 (9-bit, 10-bit) · April 1, 2026 (11-bit, 12-bit)

---

## Key Details

### 9-bit key
- Curve: `y² = x³ + 7` over `GF(349)`, subgroup order `n = 313`
- Generator: `G = (22, 191)`, Public key: `Q = (138, 315)`
- Private key recovered: **d = 135**
- Verification: `135 · G = Q ✓`
- Two independent verified runs: `d762t2u8faus73f0ofe0` and `d762r7u8faus73f0ode0`

### 10-bit key
- Curve: `y² = x³ + 7` over `GF(547)`, subgroup order `n = 547`
- Generator: `G = (386, 359)`, Public key: `Q = (286, 462)`
- Private key recovered: **d = 165**
- Verification: `165 · G = Q ✓`
- Job ID: `d762v3a3qcgc73fsedeg`

### 11-bit key
- Curve: `y² = x³ + 7` over `GF(1051)`, subgroup order `n = 1093`
- Generator: `G = (471, 914)`, Public key: `Q = (179, 86)`
- Private key recovered: **d = 756**
- Verification: `756 · G = Q ✓`
- Job ID: `d76rg3er8g3s73d93dug` (ibm_fez, April 1, 2026)

### 12-bit key
- Curve: `y² = x³ + 7` over `GF(2089)`, subgroup order `n = 2143`
- Generator: `G = (1417, 50)`, Public key: `Q = (1043, 1795)`
- Private key recovered: **d = 1384**
- Verification: `1384 · G = Q ✓`
- Job ID: `d76rn746ji0c738c2nsg` (ibm_fez, April 1, 2026)

---

## Algorithm

Shor's algorithm for the Elliptic Curve Discrete Logarithm Problem (ECDLP).

The quantum oracle computes `f(a, b) = a·G + b·Q = (a + d·b)·G` for superposed register values `(a, b)`. After inverse QFT, the measurement outcomes `(a_meas, b_meas)` satisfy `a_meas + d·b_meas ≡ 0 (mod n)`, giving `d_cand = -a_meas · b_meas⁻¹ mod n`. Each candidate is classically verified by checking `d_cand · G = Q`.

### Circuit architecture (9-bit and 10-bit)

The key advance over prior 8-bit attempts is replacing the QFT-based (Draper) modular adder with a **carry-ripple (CDKMRippleCarryAdder)** modular adder:

- The Draper adder requires all-to-all qubit connectivity and incurs 26–33× CX overhead after routing on IBM's heavy-hex topology
- The carry-ripple adder uses only nearest-neighbor gates, achieving ~1× routing overhead on heavy-hex
- Classical constants are loaded into ancilla registers via CNOT gates conditioned on control qubits, making the heavy arithmetic unconditional and avoiding the 6× overhead of wrapping every gate in a controlled operation

Circuit layout: `a_reg(m) + b_reg(m) + point(m1) + flag(1) + anc_c(m1+2)`
Total qubits: `4m + 4` — 41 for 9-bit (m=9), 45 for 10-bit (m=10)

### Post-processing

From each shot, the bitstring `(a_meas, b_meas)` is decoded. If `gcd(b_meas, n) = 1`, compute `d_cand = -a_meas · pow(b_meas, -1, n) % n`. The candidate with the most votes matching `d_cand · G = Q` is returned as the recovered key.

---

## Reproduction

**Requirements:**
```
pip install qiskit qiskit-ibm-runtime qiskit-aer numpy scipy
```

**Environment:**
```bash
export QISKIT_IBM_TOKEN="YOUR_IBM_CLOUD_API_KEY"
export QISKIT_IBM_INSTANCE="YOUR_CRN"
```

**Run simulator:**
```bash
python3 shor_9bit_ripple.py --mode sim --bits 9
python3 shor_9bit_ripple.py --mode sim --bits 10
python3 shor_9bit_ripple.py --mode sim --bits 11
python3 shor_9bit_ripple.py --mode sim --bits 12
```

**Run hardware:**
```bash
python3 shor_9bit_ripple.py --mode hw --bits 9 --shots 20000
python3 shor_9bit_ripple.py --mode hw --bits 10 --shots 20000
python3 shor_9bit_ripple.py --mode hw --bits 11 --shots 20000
python3 shor_9bit_ripple.py --mode hw --bits 12 --shots 20000
```

---

## Files

| File | Description |
|------|-------------|
| `shor_9bit_ripple.py` | Main circuit: carry-ripple oracle, hardware runner, EC verifier |
| `shor_ecdlp_final.py` | Core ECDLP/Shor implementation module |
| `ecc_keys.json` | Competition key parameters (4-bit through 21-bit) |
| `elliptic_curve.py` | Elliptic-curve arithmetic utilities |
| `verify_keys.py` | Standalone EC verification script |
| `results/4bit.json` | 4-bit hardware result artifact |
| `results/6bit.json` | 6-bit hardware result artifact |
| `results/7bit.json` | 7-bit hardware result artifact |
| `results/8bit.json` | 8-bit hardware result artifact |
| `results/9bit_run1.json` | 9-bit hardware result artifact (run 1) |
| `results/9bit_run2.json` | 9-bit hardware result artifact (run 2) |
| `results/10bit.json` | 10-bit hardware result artifact |
| `results/11bit.json` | 11-bit hardware result artifact |
| `results/12bit.json` | 12-bit hardware result artifact |

---

## Verification

1. Open any Job ID in the IBM Quantum console: https://quantum.ibm.com/
2. Re-run the scripts with the keys in `ecc_keys.json`
3. Run `python3 verify_keys.py` to check all EC verifications locally

---

## License

MIT. Commercial use requires separate licensing terms.
