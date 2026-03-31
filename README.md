# Q-Day Prize Submission: Hardware Execution of Shor-Based ECDLP with Verified Results

## 1. Claim

We demonstrate **hardware-executed Shor-based period finding for the Elliptic Curve Discrete Logarithm Problem (ECDLP)** on IBM Quantum systems, with **verified key recovery up to 10-bit subgroup sizes**.

We additionally observe **hardware-over-simulator performance gains (up to 56.5× in these runs)**, consistent with backend-specific noise and interference effects in NISQ systems.

---

## 2. Problem

Recover the private key d from a public key:

dG = Q

on an elliptic curve.

This is the **Elliptic Curve Discrete Logarithm Problem (ECDLP)**, the security foundation of modern elliptic curve cryptography.

---

## 3. Method Overview

We implement a **Shor-based period-finding workflow** adapted for ECDLP.

The oracle computes:

f(a,b) = aG + bQ = (a + db)G

which reduces to:

f(a,b) = (a + db) mod n

where n is the subgroup order.

Quantum phase estimation is used to extract periodic structure, from which candidate values of d are derived and classically verified.

---

## 4. Implementation Regimes

### 4.1 Small Subgroup Regime (4–7 bit)

* Oracle implemented via **compiled lookup-table encoding**
* All group elements precomputed classically
* Quantum circuit performs period-finding and measurement

This follows standard compiled-oracle techniques used in early demonstrations of Shor-based algorithms for small problem sizes.

---

### 4.2 Extended Regime (9–10 bit)

* Oracle implemented using **quantum ripple-carry arithmetic**
* No full lookup table
* Same period-finding workflow preserved

---

## 5. Results (Hardware Verified)

All results were obtained on IBM Quantum hardware and are publicly verifiable.

| Key Size | n   | Private Key d | Success Rate | Shots  | Job ID               |
| -------- | --- | ------------- | ------------ | ------ | -------------------- |
| 4-bit    | 7   | 6             | 1.92%        | 5,000  | d53hle9smlfc739eskn0 |
| 6-bit    | 31  | 18            | 2.915%       | 20,000 | d53i7nfp3tbc73amgl2g |
| 7-bit    | 79  | 56            | 1.13%        | 50,000 | d53ijmgnsj9s73b0vf60 |
| 9-bit    | 313 | 135           | 0.375%       | 20,000 | d762r7u8faus73f0ode0 |
| 10-bit   | 547 | 165           | 0.19%        | 20,000 | d762v3a3qcgc73fsedeg |

Additional verified 9-bit run:

* Job ID: d762t2u8faus73f0ofe0
* Success rate: 0.255%
* Valid hits: 51

All recovered keys are verified via:

dG = Q

---

## 6. Hardware vs Simulation Observations

Observed comparisons:

* 6-bit: 2.915% (hardware) vs 0.19% (simulation) → 15.3× improvement
* 7-bit: 1.13% (hardware) vs 0.02% (simulation) → 56.5× improvement

These results suggest that **hardware-specific noise and interference patterns may, in some cases, improve effective period detection** relative to idealized simulation.

We present this as an empirical observation from these runs rather than a general claim.

---

## 7. Validity of Quantum Approach

* The **period-finding step is quantum**, including superposition, interference, and measurement
* This holds **in the compiled-oracle setting used here for small-n**
* Classical preprocessing is limited to oracle construction in small-n regimes
* No classical algorithm is used to directly solve ECDLP
* Final key recovery depends on quantum measurement outputs

This is consistent with accepted compiled-oracle approaches used in early experimental implementations of Shor-based algorithms.

---

## 8. Verification

All results can be independently verified by:

1. Checking job IDs on IBM Quantum Cloud Console
2. Re-running provided scripts
3. Executing:

```bash
python3 QDay_Prize_Submission/verify_keys.py
```

---

## 9. Reproduction

### Requirements

* Python 3.9+
* qiskit
* qiskit-ibm-runtime
* numpy
* scipy

### Installation

```bash
pip install qiskit qiskit-ibm-runtime numpy scipy
```

### Running (from repository root)

Simulator:

```bash
python3 shor_7bit_full_test.py
```

Hardware:

```bash
python3 QDay_Prize_Submission/shor_7bit_ibm.py
python3 shor_9bit_ripple.py --mode hw --bits 9 --shots 20000
python3 shor_9bit_ripple.py --mode hw --bits 10 --shots 20000
```

---

## 10. Limitations

* Low success probability (0.2%–3%) requires high shot counts
* Circuit depth increases significantly with key size
* Lookup-table oracle does not scale beyond small n
* Larger instances require fully quantum arithmetic

---

## 11. Scalability

Scaling proceeds along two axes:

1. **Algorithmic**

   * Transition from lookup tables → quantum arithmetic

2. **Execution**

   * Hardware-aware optimization
   * Noise-sensitive circuit tuning

Observed hardware effects appear independent of oracle construction method and may extend to larger-scale implementations.

---

## 12. Conclusion

This submission provides:

* Verified hardware execution of **Shor-based ECDLP workflows**
* Demonstrated key recovery up to **10-bit subgroup size**
* Empirical evidence of **hardware-specific performance effects in NISQ systems**

These results contribute to both:

* Practical quantum cryptanalysis
* Experimental understanding of quantum algorithm behavior on real hardware

---

## Contact

Aaron Dennis
Founder, VexaAI
[Aaron@vexaai.app](mailto:Aaron@vexaai.app)

