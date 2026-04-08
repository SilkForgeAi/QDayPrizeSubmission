QDay Prize Submission — Breaking ECC Keys with Shor's Algorithm

17-bit is the largest ECC key broken on real quantum hardware as of April 2026.
The 17-bit break is not for the competition ( its a personal record)And was Broken after the deadline. 

This repository contains verified IBM Quantum hardware results for ECDLP key recovery using Shor's algorithm, with scaling evidence from 4-bit through 17-bit subgroup sizes.

Contact: Aaron@vexaai.app


Results

Bit   n       p       d (recovered)   Qubits   Shots    Hits   Success Rate   Job ID
4     7       13      6               —        5,000    96     1.92%          d53hle9smlfc739eskn0
6     31      43      18              —        20,000   583    2.915%         d53i7nfp3tbc73amgl2g
7     79      67      56              —        50,000   565    1.13%          d53ijmgnsj9s73b0vf60
9     313     349     135             41       20,000   51     0.255%         d762t2u8faus73f0ofe0
9     313     349     135             41       20,000   75     0.375%         d762r7u8faus73f0ode0
10    547     547     165             45       20,000   38     0.190%         d762v3a3qcgc73fsedeg
11    1093    1051    756             49       20,000   16     0.080%         d76rg3er8g3s73d93dug
12    2143    2089    1384            53       20,000   12     0.060%         d76rn746ji0c738c2nsg
13    4243    4159    820             57       20,000   4      0.020%         d78mhcqk86tc739vf5ng
14    8293    8209    137             61       20,000   1      0.005%         d78mjlak86tc739vf86g
15    16693   16477   14794           65       20,000   2      0.010%         d78mmv2k86tc739vfbcg
16    32497   32803   20248           65       20,000   1      0.005%         d78mud3c6das739i2rlg
17    65173   65647   1441            69       100,000  1      0.001%         d7at4i15a5qc73dmmlr0

All results EC-verified: d*G = Q confirmed on the competition curve y^2 = x^3 + 7.
All jobs publicly auditable at: https://quantum.ibm.com/

Backends: ibm_torino and ibm_fez (IBM Heron r1, ~0.05% 2Q gate error)
Dates: March 31, 2026 (9-bit, 10-bit) / April 1, 2026 (11-bit, 12-bit) / April 4, 2026 (13-bit through 16-bit) / April 7, 2026 (17-bit)


Key Details

9-bit key
  Curve: y^2 = x^3 + 7 over GF(349), subgroup order n = 313
  Generator: G = (22, 191), Public key: Q = (138, 315)
  Private key recovered: d = 135
  Verification: 135 * G = Q
  Two independent verified runs: d762t2u8faus73f0ofe0 and d762r7u8faus73f0ode0

10-bit key
  Curve: y^2 = x^3 + 7 over GF(547), subgroup order n = 547
  Generator: G = (386, 359), Public key: Q = (286, 462)
  Private key recovered: d = 165
  Verification: 165 * G = Q
  Job ID: d762v3a3qcgc73fsedeg

11-bit key
  Curve: y^2 = x^3 + 7 over GF(1051), subgroup order n = 1093
  Generator: G = (471, 914), Public key: Q = (179, 86)
  Private key recovered: d = 756
  Verification: 756 * G = Q
  Job ID: d76rg3er8g3s73d93dug (ibm_fez, April 1, 2026)

12-bit key
  Curve: y^2 = x^3 + 7 over GF(2089), subgroup order n = 2143
  Generator: G = (1417, 50), Public key: Q = (1043, 1795)
  Private key recovered: d = 1384
  Verification: 1384 * G = Q
  Job ID: d76rn746ji0c738c2nsg (ibm_fez, April 1, 2026)

13-bit key
  Curve: y^2 = x^3 + 7 over GF(4159), subgroup order n = 4243
  Generator: G = (3390, 2980), Public key: Q = (3457, 3962)
  Private key recovered: d = 820
  Verification: 820 * G = Q
  Job ID: d78mhcqk86tc739vf5ng (ibm_fez, April 4, 2026)

14-bit key
  Curve: y^2 = x^3 + 7 over GF(8209), subgroup order n = 8293
  Generator: G = (5566, 7), Public key: Q = (2144, 2381)
  Private key recovered: d = 137
  Verification: 137 * G = Q
  Job ID: d78mjlak86tc739vf86g (ibm_fez, April 4, 2026)

15-bit key
  Curve: y^2 = x^3 + 7 over GF(16477), subgroup order n = 16693
  Generator: G = (15429, 10667), Public key: Q = (6884, 12671)
  Private key recovered: d = 14794
  Verification: 14794 * G = Q
  Job ID: d78mmv2k86tc739vfbcg (ibm_fez, April 4, 2026)

16-bit key
  Curve: y^2 = x^3 + 7 over GF(32803), subgroup order n = 32497
  Generator: G = (14333, 24084), Public key: Q = (31890, 7753)
  Private key recovered: d = 20248
  Verification: 20248 * G = Q
  Job ID: d78mud3c6das739i2rlg (ibm_fez, April 4, 2026)

17-bit key
  Curve: y^2 = x^3 + 7 over GF(65647), subgroup order n = 65173
  Generator: G = (12976, 52834), Public key: Q = (477, 58220)
  Private key recovered: d = 1441
  Verification: 1441 * G = Q
  Job ID: d7at4i15a5qc73dmmlr0 (ibm_fez, April 7, 2026; 100,000 shots)


Algorithm

Shor's algorithm for the Elliptic Curve Discrete Logarithm Problem (ECDLP).

The quantum oracle computes f(a, b) = a*G + b*Q = (a + d*b)*G for superposed register values (a, b). After inverse QFT, the measurement outcomes (a_meas, b_meas) satisfy a_meas + d*b_meas = 0 (mod n), giving d_cand = -a_meas * b_meas^-1 mod n. Each candidate is classically verified by checking d_cand * G = Q.

Circuit architecture (9-bit through 17-bit)

The key advance over prior 8-bit attempts is replacing the QFT-based (Draper) modular adder with a carry-ripple (CDKMRippleCarryAdder) modular adder:

  - The Draper adder requires all-to-all qubit connectivity and incurs 26-33x CX overhead after routing on IBM's heavy-hex topology
  - The carry-ripple adder uses only nearest-neighbor gates, achieving ~1x routing overhead on heavy-hex
  - Classical constants are loaded into ancilla registers via CNOT gates conditioned on control qubits, making the heavy arithmetic unconditional and avoiding the 6x overhead of wrapping every gate in a controlled operation

Circuit layout: a_reg(m) + b_reg(m) + point(m1) + flag(1) + anc_c(m1+2)
Total qubits: 4m + 4

Post-processing

From each shot, the bitstring (a_meas, b_meas) is decoded. If gcd(b_meas, n) = 1, compute d_cand = -a_meas * pow(b_meas, -1, n) % n. The candidate with the most votes matching d_cand * G = Q is returned as the recovered key.


Reproduction

Requirements:
  pip install qiskit qiskit-ibm-runtime qiskit-aer numpy scipy

Environment:
  export QISKIT_IBM_TOKEN="YOUR_IBM_CLOUD_API_KEY"
  export QISKIT_IBM_INSTANCE="YOUR_CRN"

Run simulator:
  python3 shor_9bit_ripple.py --mode sim --bits 9
  python3 shor_9bit_ripple.py --mode sim --bits 10
  python3 shor_9bit_ripple.py --mode sim --bits 11
  python3 shor_9bit_ripple.py --mode sim --bits 12
  python3 shor_9bit_ripple.py --mode sim --bits 13
  python3 shor_9bit_ripple.py --mode sim --bits 14
  python3 shor_9bit_ripple.py --mode sim --bits 15
  python3 shor_9bit_ripple.py --mode sim --bits 16
  python3 shor_9bit_ripple.py --mode sim --bits 17

Run hardware:
  python3 shor_9bit_ripple.py --mode hw --bits 9 --shots 20000
  python3 shor_9bit_ripple.py --mode hw --bits 10 --shots 20000
  python3 shor_9bit_ripple.py --mode hw --bits 11 --shots 20000
  python3 shor_9bit_ripple.py --mode hw --bits 12 --shots 20000
  python3 shor_9bit_ripple.py --mode hw --bits 13 --shots 20000
  python3 shor_9bit_ripple.py --mode hw --bits 14 --shots 20000
  python3 shor_9bit_ripple.py --mode hw --bits 15 --shots 20000
  python3 shor_9bit_ripple.py --mode hw --bits 16 --shots 20000
  python3 shor_9bit_ripple.py --mode hw --bits 17 --shots 100000


Files

  shor_9bit_ripple.py       Main circuit: carry-ripple oracle, hardware runner, EC verifier
  shor_ecdlp_final.py       Core ECDLP/Shor implementation module
  ecc_keys.json             Competition key parameters (4-bit through 21-bit)
  elliptic_curve.py         Elliptic-curve arithmetic utilities
  verify_keys.py            Standalone EC verification script
  results/4bit.json         4-bit hardware result artifact
  results/6bit.json         6-bit hardware result artifact
  results/7bit.json         7-bit hardware result artifact
  results/8bit.json         8-bit hardware result artifact
  results/9bit_run1.json    9-bit hardware result artifact (run 1)
  results/9bit_run2.json    9-bit hardware result artifact (run 2)
  results/10bit.json        10-bit hardware result artifact
  results/11bit.json        11-bit hardware result artifact
  results/12bit.json        12-bit hardware result artifact
  results/13bit.json        13-bit hardware result artifact
  results/14bit.json        14-bit hardware result artifact
  results/15bit.json        15-bit hardware result artifact
  results/16bit.json        16-bit hardware result artifact
  results/17bit.json        17-bit hardware result artifact (100k shots)


Verification

  1. Open any Job ID in the IBM Quantum console: https://quantum.ibm.com/
  2. Re-run the scripts with the keys in ecc_keys.json
  3. Run python3 verify_keys.py to check all EC verifications locally


License

MIT. Commercial use requires separate licensing terms.
