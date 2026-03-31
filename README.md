QDay Prize Submission - Breaking ECC Keys with Shor's Algorithm

This repository contains verified IBM Quantum hardware results for ECDLP key recovery using Shor-style period-finding workflows, including scaling evidence from 4-bit through 10-bit subgroup sizes.

Contact: Aaron@vexaai.app

Overview

- Problem: Recover private key d from public key Q = d*G on elliptic curves
- Method: Quantum period-finding workflow with ECDLP oracle/post-processing
- Platform: IBM Quantum Runtime on ibm_torino
- Verification: Each recovered key is classically verified by checking d*G = Q

Keys Broken on Hardware

1) 4-bit key
   - n = 7, d = 6
   - Success rate: 1.92%
   - Shots: 5,000
   - Job ID: d53hle9smlfc739eskn0

2) 6-bit key
   - n = 31, d = 18
   - Success rate: 2.915%
   - Shots: 20,000
   - Job ID: d53i7nfp3tbc73amgl2g

3) 7-bit key
   - n = 79, d = 56
   - Success rate: 1.13%
   - Shots: 50,000
   - Job ID: d53ijmgnsj9s73b0vf60

4) 9-bit key
   - n = 313, d = 135
   - Success rate: 0.255% (verified run artifact in repo)
   - Shots: 20,000
   - Job ID: d762t2u8faus73f0ofe0

5) 10-bit key
   - n = 547, d = 165
   - Success rate: 0.19% (verified run artifact in repo)
   - Shots: 20,000
   - Job ID: d762v3a3qcgc73fsedeg

Largest key broken: 10-bit (n = 547)

Results Summary

Key Size | n   | Private Key d | Success Rate | Shots  | Job ID
-------- | --- | ------------- | ------------ | ------ | --------------------
4-bit    | 7   | 6             | 1.92%        | 5,000  | d53hle9smlfc739eskn0
6-bit    | 31  | 18            | 2.915%       | 20,000 | d53i7nfp3tbc73amgl2g
7-bit    | 79  | 56            | 1.13%        | 50,000 | d53ijmgnsj9s73b0vf60
9-bit    | 313 | 135           | 0.255%       | 20,000 | d762t2u8faus73f0ofe0
10-bit   | 547 | 165           | 0.19%        | 20,000 | d762v3a3qcgc73fsedeg

Additional 9-bit verified run:
- Job ID: d762r7u8faus73f0ode0
- Success rate: 0.375%
- Shots: 20,000

Hardware

- Backend: ibm_torino
- Access: IBM Quantum Runtime (qiskit-ibm-runtime)
- Job verification portal: https://quantum.ibm.com/

Algorithm Notes

- Uses Shor-inspired period-finding adapted to ECDLP structure.
- Candidate keys are extracted from measured (a, b) pairs.
- Final acceptance requires exact classical EC verification.
- For larger instances in this repo, carry-ripple arithmetic path is used in shor_9bit_ripple.py.

Requirements

- Python 3.9+
- qiskit
- qiskit-ibm-runtime
- numpy
- scipy

Install:
  pip install qiskit qiskit-ibm-runtime numpy scipy

IBM setup:
  export QISKIT_IBM_TOKEN="YOUR_TOKEN"
  export QISKIT_IBM_INSTANCE="YOUR_INSTANCE_CRN"

Run Examples

Simulator:
  python3 shor_7bit_full_test.py

Hardware:
  python3 shor_7bit_ibm.py
  python3 shor_9bit_ripple.py --mode hw --bits 9 --shots 20000
  python3 shor_9bit_ripple.py --mode hw --bits 10 --shots 20000

Key Files

Core:
- shor_ecdlp_correct.py
- elliptic_curve.py
- QDay_Prize_Submission/ecc_keys.json
- QDay_Prize_Submission/verify_keys.py

Execution:
- QDay_Prize_Submission/shor_6bit_ibm.py
- QDay_Prize_Submission/shor_7bit_ibm.py
- shor_9bit_ripple.py

Result artifacts:
- QDay_Prize_Submission/ibm_results_4bit_20251220_165304.json
- QDay_Prize_Submission/6bit_ibm_ibm_torino_20251220_173259.json
- QDay_Prize_Submission/7bit_ibm_ibm_torino_20251220_180541.json
- 9bit_ripple_ibm_torino_20260331_162859.json
- 10bit_ripple_ibm_torino_20260331_163318.json

Verification

All hardware outcomes can be checked by:
1) Opening listed job IDs in IBM Quantum console
2) Re-running scripts with repository keys
3) Running:
   python3 QDay_Prize_Submission/verify_keys.py

Limitations

- Success rates are low and require high shots.
- Circuit depth scales quickly with bit-size.
- Cost/time increase substantially at larger sizes.

License

MIT License (see LICENSE). Commercial use requires separate licensing terms.
