# Next Steps for QDay Prize

## Immediate Action Items

### 1. Research Phase (This Week)
- [ ] Find papers on "quantum elliptic curve discrete logarithm"
- [ ] Review Shor's algorithm adaptations for ECDLP
- [ ] Study quantum modular arithmetic implementations
- [ ] Understand existing quantum EC point addition approaches

**Key Questions to Answer:**
- How are EC points encoded in quantum states?
- Can we avoid full point encoding by using group structure?
- Are there simplified versions for small keys?

### 2. Implementation Strategy

#### Option A: Full Quantum EC Arithmetic
- Implement complete quantum modular arithmetic
- Quantum EC point addition gates
- Most general but complex

#### Option B: Simplified for Small Keys
- Use specific properties of small curves
- Pre-compute some classical parts (if allowed)
- Faster to implement, may not scale

#### Option C: Hybrid Approach
- Quantum period finding + classical verification
- Most practical for NISQ era
- Need to check competition rules

### 3. Quick Win Path

For the **4-bit key (n=7)**:
- Only need 3 bits to represent numbers 0-7
- Period register: ~6 qubits
- Point coordinates: ~4 bits each × 2 = 8 qubits
- **Total: ~14 qubits** - very feasible!

**Strategy:**
1. Start with simplified oracle (maybe classical helper)
2. Implement quantum period finding
3. Validate on simulator
4. Run on IBM Brisbane (127 qubits available!)

### 4. Recommended Next File to Create

Create `quantum_ec_simplified.py`:
- Simplified EC operations for small keys
- Test with 4-bit key first
- Validate approach before full implementation

### 5. Timeline

**Week 1:**
- Research quantum ECDLP implementations
- Understand what's feasible on current hardware
- Design simplified approach for 4-bit key

**Week 2:**
- Implement period finding oracle (simplified)
- Test on quantum simulator
- Debug and optimize

**Week 3:**
- Run on IBM Quantum hardware
- Apply error mitigation (ZNE)
- Document results

**Week 4+:**
- Scale to larger keys (6-bit, 7-bit)
- Full implementation if needed
- Optimize for competition submission

---

## Resources to Check

1. **Qiskit Textbook** - Shor's Algorithm chapter
2. **Papers:**
   - "Quantum Algorithms for Elliptic Curves" (various)
   - Recent work on practical quantum cryptanalysis
3. **Competition Guidelines:**
   - Review rubric for scoring criteria
   - Understand what "pure quantum" means
   - Check if classical pre-processing is allowed

---

## Key Insight

The **4-bit key** is our proof-of-concept target:
- Small enough to be feasible on current hardware
- Large enough to be significant
- Will validate our approach before scaling

**Goal:** Break 4-bit key by end of Week 3, then scale up!

