# QDay Prize Implementation Status

**Last Updated:** January 2025  
**Current Focus:** 4-bit ECC key (n=7, d=6)

---

## ✅ Completed

1. **Classical Verification**
   - ✅ All keys verified (4-21 bits)
   - ✅ Curve equation: y² = x³ + 7 (mod p)
   - ✅ Confirmed d*G = Q for all keys
   - ✅ Point addition, scalar multiplication working

2. **Quantum Framework**
   - ✅ QFT circuit implemented
   - ✅ Period finding circuit structure created
   - ✅ Simulator integration working
   - ✅ Circuit runs on AerSimulator (11 qubits, depth 11)

3. **Project Structure**
   - ✅ ECC key loading and parsing
   - ✅ Classical EC operations
   - ✅ Quantum circuit framework
   - ✅ Verification scripts

---

## 🚧 Current Challenge

**Oracle Implementation** - The core piece needed:

The oracle needs to compute: **f(a, b) = (a + b*d) mod n**

Where:
- a, b are in superposition
- d is the private key we're finding
- n is the subgroup order

**Current Status:** Simplified placeholder exists, but doesn't implement the actual ECDLP computation.

---

## 📋 Next Steps

### Immediate (This Week)

1. **Implement Proper Oracle**
   - Quantum modular arithmetic: addition, multiplication mod n
   - Compute (a + b*d) mod n in superposition
   - Use Qiskit's arithmetic circuits if available
   - Or implement custom quantum modular operations

2. **Test on Simulator**
   - Verify period finding works correctly
   - Extract d from measurements
   - Validate with 4-bit key

3. **Optimize Circuit**
   - Reduce qubit count
   - Minimize circuit depth
   - Apply optimizations (semi-classical QFT, etc.)

### Short-term (Next 2 Weeks)

4. **Run on Real Hardware**
   - IBM Quantum Brisbane/Torino
   - Apply error mitigation (ZNE)
   - Document results

5. **Scale to Larger Keys**
   - 6-bit key (n=31)
   - 7-bit key (n=79)

---

## 📊 Resource Requirements

### Current (4-bit key, n=7):
- **Qubits:** 11 (period: 8, group: 3)
- **Depth:** 11 gates
- **Status:** ✅ Runs on simulator, oracle needs implementation

### Target (Optimized):
- **Qubits:** ~12-15 (after optimization)
- **Depth:** Minimize for noisy hardware
- **Shots:** 2048+ for good statistics

---

## 🔑 Key Files

- `elliptic_curve.py` - Classical EC operations ✅
- `verify_keys.py` - Key verification ✅
- `shor_ecdlp_practical.py` - Framework ✅
- `shor_oracle_4bit.py` - Working circuit (oracle placeholder) ⚠️
- `ecc_keys.json` - All competition keys ✅

---

## 💡 Implementation Strategy

### Option 1: Full Quantum Modular Arithmetic
- Implement quantum addition/multiplication mod n
- Most general, works for all keys
- More complex, higher qubit count

### Option 2: Lookup-Based Oracle (Small Keys)
- For n=7, pre-compute lookup table
- Use quantum oracle to access table
- Faster to implement, limited to small n

### Option 3: Hybrid Approach
- Classical pre-computation where allowed
- Quantum period finding
- Best for NISQ era validation

**Recommendation:** Start with Option 2 for 4-bit key validation, then move to Option 1 for scalability.

---

## 📚 References Needed

1. **Qiskit Arithmetic Circuits**
   - Check Qiskit circuit library for modular arithmetic
   - Look for `ModularAdder`, `ModularMultiplier`, etc.

2. **Open-Source Implementations**
   - Search GitHub for "quantum shor ecdlp"
   - Qiskit community implementations
   - Academic code repositories

3. **Papers**
   - Recent work on practical quantum cryptanalysis
   - Optimizations for NISQ devices
   - Semi-classical QFT implementations

---

## 🎯 Success Criteria

- [ ] Oracle correctly computes f(a, b) = (a + b*d) mod n
- [ ] Period finding extracts correct period
- [ ] Extract d from period (solve ECDLP)
- [ ] Run on real hardware
- [ ] Document results for submission

---

**Status:** Foundation complete, oracle implementation is the critical next step! 🚀

