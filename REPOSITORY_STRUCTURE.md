Recommended GitHub Repository Structure

Repository Name: qday-prize-ecdlp-submission

Directory Layout:

qday-prize-ecdlp-submission/
│
├── README.md                    (Main submission document)
├── brief.pdf                    (2-page brief, converted from brief.txt)
│
├── Core Code/
│   ├── shor_ecdlp_correct.py   (Main Shor's algorithm implementation)
│   ├── elliptic_curve.py       (Classical EC operations)
│   ├── ecc_keys.json           (Competition keys)
│   └── verify_keys.py          (Key verification script)
│
├── Execution Scripts/
│   ├── shor_4bit_ibm.py        (4-bit key breaking)
│   ├── shor_6bit_ibm.py        (6-bit key breaking)
│   └── shor_7bit_ibm.py        (7-bit key breaking)
│
├── Results/
│   ├── ibm_results_4bit_20251220_165304.json
│   ├── 6bit_ibm_ibm_torino_20251220_173259.json
│   └── 7bit_ibm_ibm_torino_20251220_180541.json
│
└── Documentation/
    ├── COMPETITION_RULES_COMPLIANCE.md
    ├── HARDWARE_VS_SIMULATOR_ANALYSIS.md
    └── SUBMISSION_PACKAGE.md

OR simpler flat structure:

qday-prize-ecdlp-submission/
│
├── README.md
├── brief.pdf
│
├── shor_ecdlp_correct.py
├── elliptic_curve.py
├── ecc_keys.json
├── verify_keys.py
│
├── shor_4bit_ibm.py
├── shor_6bit_ibm.py
├── shor_7bit_ibm.py
│
├── ibm_results_4bit_20251220_165304.json
├── 6bit_ibm_ibm_torino_20251220_173259.json
├── 7bit_ibm_ibm_torino_20251220_180541.json
│
└── (optional documentation files)

Recommendation: Use the simpler flat structure unless you have many files.

Key Files to Include (Required):

Required by competition:
- README.md
- brief.pdf
- All code necessary to run the algorithm
- Results/logfiles (JSON files)

Recommended to include:
- Core implementation files
- Execution scripts
- Results JSON files
- Additional documentation (optional but helpful)

Files to Exclude:

- Test files (shor_7bit_full_test.py, etc.) - optional, can include if helpful
- Development scripts - only include if they add value
- Temporary/debug files
- Large log files (keep JSON results, skip verbose logs)

GitHub Repository Settings:

- Name: qday-prize-ecdlp-submission
- Visibility: PUBLIC (required by competition)
- Description: "QDay Prize submission: Breaking 4-bit, 6-bit, and 7-bit ECC keys using Shor's algorithm on IBM Quantum hardware"
- Topics: quantum-computing, shor-algorithm, ecdlp, qiskit, ibm-quantum, cryptanalysis
- License: MIT (as specified in README)

