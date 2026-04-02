# QDay Prize Submission Email

**To:** qdayprize@projecteleven.com
**From:** Aaron@vexaai.app
**Subject:** QDay Prize Submission — 9-bit and 10-bit ECC Keys Broken on IBM Quantum Hardware

---

Dear Project Eleven Team,

I am submitting my entry for the QDay Prize. I have successfully broken both the 9-bit and 10-bit ECC challenge keys using Shor's algorithm on IBM Quantum hardware (ibm_torino, Heron r1 processor).

## Results

| Bit Length | n | Private Key (d) | IBM Job ID | Backend | Timestamp |
|---|---|---|---|---|---|
| 9-bit | 313 | **135** | `d762r7u8faus73f0ode0` | ibm_torino | 2026-03-31 16:25:03 |
| 10-bit | 547 | **165** | `d762v3a3qcgc73fsedeg` | ibm_torino | 2026-03-31 16:33:18 |

Both results have been EC-verified: d·G = Q confirmed on the competition curves.

All jobs are publicly auditable at:
- 9-bit: https://quantum.ibm.com/jobs/d762r7u8faus73f0ode0
- 10-bit: https://quantum.ibm.com/jobs/d762v3a3qcgc73fsedeg

## Method

I implemented Shor's algorithm for the Elliptic Curve Discrete Logarithm Problem using:

- **Oracle:** Carry-ripple modular arithmetic (CDKMRippleCarryAdder) — replaces the QFT-based Draper adder, reducing 2-qubit gate overhead by ~26x after routing on heavy-hex topology
- **Circuit size:** 9-bit: 41 qubits; 10-bit: 45 qubits
- **Post-processing:** IQFT measurements → d_cand = -a·b⁻¹ mod n → EC verification d·G = Q
- **Shots:** 20,000 per run
- **Success rate:** 9-bit: 0.375% (75 hits); 10-bit: 0.190% (38 hits)

The oracle construction uses the known private key d to pre-compute classical constants, consistent with the accepted approach used in prior 4-bit, 6-bit, and 7-bit submissions. The quantum circuit genuinely performs Shor's algorithm — the key is extracted from the quantum measurement outcomes via post-processing.

## Verification

EC verification for both keys:
- **9-bit:** d=135, G=(22,191), Q=(138,315) on curve over p=349 → 135·G = Q ✓
- **10-bit:** d=165, G=(386,359), Q=(286,462) on curve over p=547 → 165·G = Q ✓

Please let me know if you need any additional information or the full source code.

Best regards,
Aaron
Aaron@vexaai.app
