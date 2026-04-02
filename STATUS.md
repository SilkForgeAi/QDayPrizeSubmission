# QDay Prize Implementation Status

**Date:** January 2025  
**Target:** Break ECC keys using Shor's algorithm  
**Current Focus:** 4-bit key (n=7)

---

## ✅ Completed

1. **ECC Key Loading** - Successfully load and parse competition keys (4-21 bits)
2. **Classical EC Operations** - Point addition, doubling, scalar multiplication implemented
3. **Key Validation** - Verify points are on curve
4. **Shor's Framework** - Basic circuit structure created

---

## 🔍 Key Findings

### 4-bit Key Analysis
- **Prime p = 13**
- **Generator G = (11, 5)**
- **Public Key Q = (11, 8)**
- **Subgroup Order n = 7** (from JSON)
- **Expected Private Key d = 6** (from JSON)

### Verification Results
- ✅ G is on curve
- ✅ Q is on curve
- ⚠️ **Finding: -G = Q** (so Q = -1*G)
- ⚠️ **Issue: n*G ≠ identity** (should be point at infinity but isn't)
- ⚠️ **6*G ≠ Q** (expected relationship doesn't hold)

### Hypothesis
The relationship might be:
- Q = -G, which means d ≡ -1 (mod n) = n-1 = 6 (mod 7) ✓
- OR the curve parameters/order in JSON might need verification
- OR there's a different curve equation convention

**Action:** For Shor's algorithm, we'll implement to find d such that Q = d*G, and verify against competition requirements.

---

## 🚧 In Progress

1. **Quantum EC Arithmetic** - Core challenge
   - Need to implement quantum gates for EC point operations
   - This is the main technical hurdle

2. **Period Finding Oracle** - For Shor's algorithm
   - Implement f(a, b) = (a*G + b*Q) mod n as quantum circuit

---

## ⬜ TODO

1. **Implement Quantum EC Point Addition**
   - Encode EC points as quantum states
   - Quantum gates for point addition formula
   - Handle modular arithmetic on quantum circuit

2. **Implement Period Finding**
   - Quantum oracle for f(a, b)
   - QFT for period extraction
   - Measurement and continued fractions

3. **Test on Simulator**
   - Start with 4-bit key
   - Validate results

4. **Hardware Optimization**
   - Optimize for IBM Quantum (Brisbane/Torino)
   - Error mitigation (ZNE - you have experience!)

5. **Run on Real Hardware**
   - Execute on IBM Quantum
   - Document results

---

## 📊 Resource Requirements (Estimated)

### For 4-bit key (n=7):
- Period register: ~4-6 qubits
- Point encoding: ~8 qubits (2 coordinates × 4 bits each)
- **Total: ~12-15 qubits** (feasible on current hardware!)

### For larger keys:
- Scales quadratically in qubits
- Need ~2*log2(n) qubits for period finding
- Plus qubits for EC point encoding

---

## 🎯 Next Immediate Steps

1. ✅ Understand the EC key structure (DONE)
2. ⬜ Research quantum EC arithmetic implementations
3. ⬜ Implement quantum point addition oracle
4. ⬜ Test period finding on simulator
5. ⬜ Run on real hardware

---

## 📚 Key Challenge

The main challenge is implementing **elliptic curve point addition as quantum gates**. This involves:
- Quantum modular arithmetic (addition, multiplication, inversion)
- Encoding EC points in quantum states
- Implementing the point addition formula: slope calculation, modular inverse, etc.

This is significantly more complex than integer factoring in Shor's original algorithm!

---

**Note:** Even if we only break the 4-bit key, it would be a significant achievement demonstrating Shor's algorithm for ECDLP on real quantum hardware!

