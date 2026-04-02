QDay Prize Submission Package
=============================

Submission focus:
- Practical ECDLP key recovery on IBM Quantum hardware
- Verified scaling from 4-bit to 10-bit keys
- Reproducible artifacts with job IDs and JSON outputs

Primary claims
--------------
1) Hardware-verified key recovery at:
   - 4-bit (n=7)
   - 6-bit (n=31)
   - 7-bit (n=79)
   - 9-bit (n=313)
   - 10-bit (n=547)

2) Largest key broken in this package:
   - 10-bit, n=547, d=165
   - IBM Job ID: d762v3a3qcgc73fsedeg

3) Independent verification path:
   - IBM job IDs can be inspected in IBM Quantum console
   - Local classical verification via verify_keys.py

Included files
--------------
Required core:
- README.md
- brief.pdf
- QDay_Prize_Submission/ecc_keys.json
- QDay_Prize_Submission/elliptic_curve.py
- QDay_Prize_Submission/verify_keys.py
- QDay_Prize_Submission/shor_6bit_ibm.py
- QDay_Prize_Submission/shor_7bit_ibm.py

Result artifacts:
- QDay_Prize_Submission/ibm_results_4bit_20251220_165304.json
- QDay_Prize_Submission/6bit_ibm_ibm_torino_20251220_173259.json
- QDay_Prize_Submission/7bit_ibm_ibm_torino_20251220_180541.json
- 9bit_ripple_ibm_torino_20260331_162859.json
- 10bit_ripple_ibm_torino_20260331_163318.json

Supporting docs:
- HARDWARE_VS_SIMULATOR_ANALYSIS.md
- ACHIEVEMENTS_SUMMARY.md

Verification job IDs
--------------------
4-bit:  d53hle9smlfc739eskn0
6-bit:  d53i7nfp3tbc73amgl2g
7-bit:  d53ijmgnsj9s73b0vf60
9-bit:  d762r7u8faus73f0ode0
10-bit: d762v3a3qcgc73fsedeg

Additional 9-bit verified run:
9-bit:  d762t2u8faus73f0ofe0

Contact
-------
Aaron@vexaai.app
