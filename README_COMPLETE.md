# QDay Prize - Complete Implementation Guide

**Competition:** Break ECC with Shor's Algorithm  
**Target:** 4-bit key (n=7, d=6) → Scale to larger keys  
**Prize:** 1 Bitcoin  
**Deadline:** April 5, 2026

---

## 📁 Project Structure

```
qday_prize/
├── ecc_keys.json                 # All competition keys (4-21 bits)
├── elliptic_curve.py             # Classical EC operations ✅
├── verify_keys.py                # Key verification ✅
├── shor_ecdlp_final.py           # Main Shor implementation (oracle in progress)
├── shor_lookup_efficient.py      # Lookup oracle attempts
├── shor_oracle_4bit.py           # Framework/test circuits
├── ORACLE_IMPLEMENTATION_GUIDE.md # Detailed oracle guide
├── IMPLEMENTATION_STATUS.md      # Current status
└── README_COMPLETE.md            # This file
```

---

## ✅ Completed

1. **Classical Infrastructure**
   - ✅ All keys verified (4-21 bits)
   - ✅ Curve: y² = x³ + 7 (mod p)
   - ✅ Point operations working
   - ✅ Confirmed d*G = Q for all keys

2. **Quantum Framework**
   - ✅ Circuit structure created
   - ✅ QFT implemented
   - ✅ Simulator integration
   - ✅ Precomputed group elements

3. **Documentation**
   - ✅ Implementation guides
   - ✅ Status tracking
   - ✅ Next steps documented

---

## ⚠️ In Progress

**Oracle Implementation** - The critical piece

**What's Needed:**
- Implement controlled-U operations for period finding
- Add phase kickback mechanism
- Extract period from measurements
- Recover discrete logarithm d

**Current Status:**
- Lookup table approach started
- Needs refinement for proper phase relationships
- Controlled operations need correct implementation

---

## 🎯 Next Steps (Prioritized)

### 1. Fix Oracle (This Week)
- Implement controlled-U^2^k operations
- Add phase kickback
- Test period extraction

### 2. Validate (Next Week)
- Extract period from measurements
- Recover d = 6
- Verify on simulator

### 3. Hardware (Week 3)
- Run on IBM Quantum
- Apply error mitigation (ZNE)
- Document results

### 4. Scale (Week 4+)
- Move to 6-bit key (n=31)
- Optimize circuit
- Prepare submission

---

## 🚀 Quick Start

### Verify Keys
```bash
cd qday_prize
python3 verify_keys.py
```

### Test Current Circuit
```bash
python3 shor_ecdlp_final.py
```

### Research Resources
- GitHub: `mhinkie/ShorDiscreteLog`
- Tutorial: https://p51lee.github.io/quantum-computing/qiskit-ecdlp/
- Qiskit circuit library documentation

---

## 📊 Resource Requirements

**4-bit Key (Current Target):**
- Qubits: ~18 (with optimizations)
- Depth: Minimize for noisy hardware
- Shots: 2048+ for statistics

**Feasible on:**
- ✅ AerSimulator (unlimited)
- ✅ IBM Brisbane (127 qubits)
- ✅ IBM Torino (various sizes)

---

## 📚 Implementation Strategy

**Phase 1:** Lookup Oracle (Current)
- Best for n=7
- Low qubit count
- Fast to implement

**Phase 2:** Qiskit Arithmetic (Scaling)
- For 6-10 bit keys
- Uses built-in circuits
- More general

**Phase 3:** Custom Gates (Optimization)
- For efficiency
- Lower resources
- Advanced techniques

---

## 🎓 Key Concepts

**Shor's for ECDLP:**
- Find period of function f(a, b) = a*G + b*Q
- Period reveals discrete logarithm d
- Use quantum phase estimation

**Oracle Requirements:**
- Implement U |x> = |f(x)>
- Controlled-U^2^k for period register qubits
- Phase kickback reveals period

**Period Extraction:**
- Continued fraction expansion
- Extract k/r from phase measurements
- Recover d from period

---

## 📝 Competition Submission Requirements

1. **Gate-level code** - Quantum circuit code
2. **Approach description** - Methodology and techniques
3. **Hardware specs** - Quantum computer used
4. **Results** - Key size broken, verification

**Timeline:** ~11 months remaining

---

## 💡 Tips

1. **Start Simple** - Lookup oracle for 4-bit key first
2. **Validate Classically** - Always verify against known d
3. **Test on Simulator** - Before real hardware
4. **Document Everything** - For submission
5. **Optimize Incrementally** - Get working first, then optimize

---

## 🔗 Key Files to Review

- `ORACLE_IMPLEMENTATION_GUIDE.md` - Detailed oracle guide
- `IMPLEMENTATION_STATUS.md` - Current progress
- `shor_ecdlp_final.py` - Main implementation

---

**Status:** Solid foundation, oracle implementation is the critical next step! 🚀

**Goal:** Break 4-bit key → Validate approach → Scale to larger keys → Win competition!

