# Oracle Implementation Guide - Current Status & Next Steps

Based on the comprehensive implementation guide provided.

---

## ✅ What We Have Working

1. **Classical Verification** - All keys verified (4-21 bits)
2. **Curve Operations** - Point addition, scalar multiplication working
3. **Precomputed Group Elements** - All multiples of G computed
4. **Circuit Framework** - QFT, registers, structure in place
5. **Simulator Integration** - Runs on AerSimulator

---

## ⚠️ Current Challenge: Oracle Implementation

The oracle needs to implement the controlled operation for period finding:
**U |x> = |f(x)>** where f is related to ECDLP

For Shor's algorithm, we need:
1. Function U: computes a*G + b*Q
2. Controlled operations: U^2^k for each qubit in period register
3. Phase kickback: reveals period information

---

## 📋 Implementation Options (From Guide)

### Option 3: Simplified Lookup (Best for n=7) ⭐ **RECOMMENDED START**

**Status:** Partially implemented, needs refinement

**What's Needed:**
- Cleaner lookup table encoding
- Proper controlled operations based on period register
- Phase kickback mechanism

**Steps:**
1. ✅ Precompute all group elements (DONE)
2. ⚠️ Encode lookup table as quantum gates (IN PROGRESS)
3. ⬜ Implement controlled-U^2^k operations
4. ⬜ Add phase kickback for period finding
5. ⬜ Test and extract period

**Qubit Estimate:** ~12-15 qubits total

**Resources:**
- GitHub: `mhinkie/ShorDiscreteLog` for DLP lookup adaptations
- Use Qiskit's `MCXGate` for multi-controlled operations

---

### Option 1: Qiskit Arithmetic Circuits (For Scaling)

**Status:** Not started

**For:** 6-10 bit keys later

**What's Needed:**
- `RGQFTMultiplier` for mod p multiplication
- `ModularAdderGate` for mod p addition
- ExactReciprocalGate for modular inversion
- Custom point addition circuit

**Resources:**
- Qiskit circuit library: `qiskit.circuit.library`
- Tutorial: https://p51lee.github.io/quantum-computing/qiskit-ecdlp/
- They recovered 3-bit equiv key on simulator

**Qubit Estimate:** ~20-30 qubits for 4-bit key

---

### Option 2: Custom Gates (Advanced)

**Status:** Not started

**For:** Optimization, lowest resources

**What's Needed:**
- Custom modular arithmetic gates
- Montgomery form for efficiency
- Out-of-place operations

**Resources:**
- arXiv 2506.03318 - 6-step circuit design
- Qualtran (Google's library)
- Q# from Microsoft paper

**Qubit Estimate:** ~25 qubits with optimizations

---

## 🎯 Immediate Next Steps

### 1. Fix Lookup Oracle (Priority 1)

**Problem:** Current oracle doesn't create proper phase relationships for period finding.

**Solution:** Implement controlled-U operations correctly:

```python
# For each qubit j in period register:
# Apply controlled-U^(2^j) where U|x> = |a*G + b*Q>
# This creates phase kickback proportional to the period
```

**Implementation:**
- Use precomputed lookup table
- For each period register qubit, apply controlled operations
- The control should enable U^(2^j) power of the function

### 2. Test Period Extraction

**Goal:** Extract period from measurements using continued fractions

**Check:**
- Measurements show periodic patterns
- Continued fraction expansion finds correct period
- Period relates to discrete logarithm d

### 3. Extract Discrete Logarithm

**Goal:** Recover d from period information

**Method:** Use relationship between period and d:
- If period r found in f(a, b) = a*G + b*Q
- Extract d from the period relationship

---

## 📚 Key Resources to Use

### Code References
1. **GitHub:** `mhinkie/ShorDiscreteLog` - DLP lookup implementations
2. **Tutorial:** https://p51lee.github.io/quantum-computing/qiskit-ecdlp/
3. **Qiskit Examples:** Shor's algorithm tutorials

### Papers
1. Recent work on practical quantum cryptanalysis
2. arXiv 2506.03318 - Efficient EC circuits
3. Semi-classical QFT implementations

### Qiskit Libraries
```python
from qiskit.circuit.library import (
    QFT,
    MCXGate,  # Multi-controlled X
    # Check for:
    # - ModularAdderGate
    # - RGQFTMultiplier
    # - ExactReciprocalGate
)
```

---

## 🔧 Debug Checklist

If oracle isn't working:

- [ ] Verify group elements precomputed correctly
- [ ] Check encoding of points into qubits
- [ ] Verify controlled operations match intended k values
- [ ] Ensure phase kickback is happening
- [ ] Check measurement results show periodicity
- [ ] Validate continued fraction extraction

---

## 📊 Target Specifications (4-bit key)

**Goal:** Recover d = 6 for n=7

**Circuit Requirements:**
- Period register: ~6 qubits
- Group encoding: ~3 qubits (for k: 0-6)
- Point encoding: ~9 qubits (x:4, y:4, inf:1)
- **Total: ~18 qubits** (with ancillas)

**Success Criteria:**
- Circuit runs on simulator
- Measurements show period r
- Extract d from period
- Verify d = 6

---

## 🚀 Timeline

**This Week:**
1. Fix lookup oracle implementation
2. Implement controlled-U operations
3. Test period finding

**Next Week:**
1. Run on real hardware (IBM Quantum)
2. Apply error mitigation
3. Document results

**Following:**
1. Scale to 6-bit key
2. Optimize circuit
3. Prepare submission

---

## 💡 Key Insight

The **lookup approach is the right starting point** for n=7. Once we get it working and understand the period finding mechanism, we can:
- Optimize the circuit
- Scale to larger keys
- Move to full quantum arithmetic if needed

**Current Status:** Foundation is solid, oracle implementation needs refinement! 🎯

