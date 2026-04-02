# Step-by-Step Plan: 6-bit → 7-bit → Larger Keys

## ✅ Current Status

### Completed
- ✅ **4-bit key (n=7)**: Broken on IBM hardware (1.92% success)
- ✅ **6-bit key (n=31)**: Broken on IBM hardware (2.915% success)
- ✅ **Oracle implementation**: f(a,b) = a*G + b*Q working correctly
- ✅ **Hardware validation**: ibm_torino working well

---

## 📋 Step-by-Step Plan for 7-bit

### **Step 1: Analyze 7-bit Requirements** ⏳ NEXT

**Goal:** Understand what's needed for n=79

**Tasks:**
- [ ] Check 7-bit key parameters (n=79, p=67, etc.)
- [ ] Calculate resource requirements
  - Qubits needed: ~?
  - Lookup table size: 79² = 6,241 combinations
  - Circuit depth estimate
- [ ] Compare with current approach limitations

**Output:** Requirements document

---

### **Step 2: Test Lookup Approach Limit** 

**Goal:** See if lookup table still works for 7-bit

**Tasks:**
- [ ] Extend current lookup oracle to n=79
- [ ] Test on simulator with 7-bit key
- [ ] Measure success rate and performance
- [ ] Check if circuit depth/gates are manageable

**Decision Point:**
- ✅ If lookup works → Continue with lookup
- ❌ If lookup fails → Move to quantum arithmetic

**Expected:** Lookup may be too large, need quantum arithmetic

---

### **Step 3: Implement Quantum Modular Arithmetic** (If needed)

**Goal:** Build scalable oracle using quantum arithmetic

**Tasks:**
- [ ] Research Qiskit arithmetic circuits
  - Check for ModularAdder, RGQFTMultiplier
  - Understand how to use them
- [ ] Implement quantum modular addition mod p
- [ ] Implement quantum modular multiplication mod p
- [ ] Implement quantum modular inversion (Fermat's Little Theorem)
- [ ] Combine into oracle: f(a,b) = (a + d*b) mod n

**Resources:**
- Qiskit circuit library documentation
- Tutorial: https://p51lee.github.io/quantum-computing/qiskit-ecdlp/
- GitHub examples

**Time Estimate:** 1-2 weeks

---

### **Step 4: Test 7-bit on Simulator**

**Goal:** Validate 7-bit implementation works

**Tasks:**
- [ ] Create 7-bit circuit
- [ ] Run on AerSimulator
- [ ] Measure success rate
- [ ] Optimize if needed
- [ ] Validate we can extract d correctly

**Success Criteria:**
- Successfully find d for 7-bit key
- Success rate > 0.1% (reasonable for larger key)
- Circuit completes in reasonable time

---

### **Step 5: Optimize for Hardware**

**Goal:** Make 7-bit circuit runnable on IBM hardware

**Tasks:**
- [ ] Reduce circuit depth (if possible)
- [ ] Optimize gate count
- [ ] Test transpilation to ibm_torino
- [ ] Check qubit requirements vs available
- [ ] Apply error mitigation strategies

**Target:**
- Circuit depth < 100,000 (current 6-bit: ~65k)
- Qubits < 133 (ibm_torino limit)
- Manageable execution time

---

### **Step 6: Run 7-bit on IBM Hardware**

**Goal:** Break 7-bit key on real hardware

**Tasks:**
- [ ] Submit job to ibm_torino
- [ ] Use appropriate shot count (50k+ shots)
- [ ] Monitor job progress
- [ ] Analyze results
- [ ] Extract d and verify

**Success Criteria:**
- Find correct d for 7-bit key
- Document results
- Save for competition submission

---

### **Step 7: Scale to 8-bit+ (If successful)**

**Goal:** Push to even larger keys

**Tasks:**
- [ ] Analyze 8-bit requirements (n=139)
- [ ] Further optimize quantum arithmetic
- [ ] Test on simulator
- [ ] Run on hardware if feasible

**Note:** 8-bit may be near current hardware limits

---

## 🎯 Immediate Next Steps (This Week)

### Today/Tomorrow:
1. **Analyze 7-bit requirements** (Step 1)
2. **Test lookup approach limit** (Step 2)
3. **Decide on approach** (lookup vs quantum arithmetic)

### This Week:
4. **Start quantum arithmetic implementation** (if needed)
5. **Test on simulator** (Step 4)

### Next Week:
6. **Optimize for hardware** (Step 5)
7. **Run on IBM** (Step 6)

---

## 📊 Key Metrics to Track

For each step, track:
- **Success rate**: % of measurements giving correct d
- **Circuit depth**: After transpilation
- **Gate count**: After transpilation  
- **Qubit count**: Total qubits needed
- **Execution time**: On simulator and hardware
- **Valid measurements**: % where b is invertible

---

## ⚠️ Potential Challenges

1. **Lookup table too large** (7-bit: 6,241 combinations)
   - Solution: Use quantum arithmetic

2. **Circuit depth too high**
   - Solution: Optimize gates, use better arithmetic circuits

3. **Low success rate**
   - Solution: More shots, better error mitigation

4. **Hardware limitations**
   - Solution: Optimize circuit, use multiple runs

---

## 📁 Files to Create

- `shor_7bit_analysis.py` - Analyze 7-bit requirements
- `shor_7bit_lookup_test.py` - Test lookup approach
- `quantum_modular_arithmetic.py` - Quantum arithmetic implementation
- `shor_7bit_quantum_arithmetic.py` - 7-bit with quantum arithmetic
- `shor_7bit_ibm.py` - Run on IBM hardware

---

**Status:** Ready to start Step 1 - Analyze 7-bit requirements!

