# QDay Prize Submission - Breaking ECC Keys with Shor's Algorithm

This repository submits verified ECDLP breaks on IBM Quantum hardware using Shor’s algorithm for the Elliptic Curve Discrete Logarithm Problem (ECDLP), including scaling from 4-bit through 10-bit keys.

Contact: Aaron@vexaai.app

---

## Background

This work applies production quantum execution and error mitigation practice to cryptanalysis:

- 160+ production runs across IBM Quantum and AWS Braket
- Hardware-focused error mitigation and reliability tuning
- Practical Shor ECDLP pipeline with classical verification (`d * G = Q`)

---

## Keys Broken (Hardware Verified)

I successfully broke five ECC keys on IBM hardware:

- 4-bit key (`n=7`, `d=6`) - success rate: **1.92%**
- 6-bit key (`n=31`, `d=18`) - success rate: **2.915%**
- 7-bit key (`n=79`, `d=56`) - success rate: **1.13%**
- 9-bit key (`n=313`, `d=135`) - success rate: **0.255%** (verified run)
- 10-bit key (`n=547`, `d=165`) - success rate: **0.19%** (verified run)

Largest key broken: **10-bit** (`n=547`).

---

## Results Summary

| Key Size | n   | Private Key d | Success Rate | Shots  | Hardware | Job ID |
|----------|-----|---------------|--------------|--------|----------|--------|
| 4-bit    | 7   | 6             | 1.92%        | 5,000  | ibm_torino | d53hle9smlfc739eskn0 |
| 6-bit    | 31  | 18            | 2.915%       | 20,000 | ibm_torino | d53i7nfp3tbc73amgl2g |
| 7-bit    | 79  | 56            | 1.13%        | 50,000 | ibm_torino | d53ijmgnsj9s73b0vf60 |
| 9-bit    | 313 | 135           | 0.255%       | 20,000 | ibm_torino | d762t2u8faus73f0ofe0 |
| 10-bit   | 547 | 165           | 0.19%        | 20,000 | ibm_torino | d762v3a3qcgc73fsedeg |

Additional 9-bit verified run:
- Job ID: `d762r7u8faus73f0ode0`  
- Hits: 75 / 20,000  
- Success: 0.375%

---

## Quantum Hardware Used

- Backend: **IBM Torino** (Heron generation)
- Access: IBM Quantum Cloud via `qiskit-ibm-runtime`

All job IDs are verifiable in IBM Quantum job console:  
[https://quantum.ibm.com/](https://quantum.ibm.com/)

---

## Algorithm Overview

This implementation uses Shor’s algorithm adapted for ECDLP:

- Given generator point `G` and public key `Q = d * G`, recover `d`.
- Oracle relation:
  - `f(a, b) = aG + bQ = (a + d*b)G`
  - reduced to `(a + d*b) mod n` for subgroup order `n`.
- Includes post-processing from measured `(a, b)` pairs to candidate `d`, then exact EC verification (`d * G = Q`).

For the 9/10-bit scaling runs, the repository uses a carry-ripple arithmetic path in `shor_9bit_ripple.py` with IBM Runtime compatibility fallback for serialization.

---

## Installation

## Prerequisites

- Python 3.9+
- Qiskit 2.1.2+
- qiskit-ibm-runtime 0.41.1+
- NumPy, SciPy
- IBM Quantum account with access to `ibm_torino`

## Install

```bash
pip install qiskit qiskit-ibm-runtime numpy scipy
