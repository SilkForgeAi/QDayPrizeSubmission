# Scaling Strategy: 4-bit → 6-bit → Larger Keys

## Current Status

**4-bit Key (n=7): ✅ WORKING**
- Successfully broken on IBM Quantum hardware
- 1.92% success rate
- Lookup table: 49 combinations
- Circuit depth: ~4000 (transpiled)

---

## 6-bit Key Challenge (n=31)

### Scaling Analysis

**Parameters:**
- n = 31 (subgroup order)
- Register bits: 5 (log2(31) ≈ 5)
- Lookup table: 31 × 31 = **961 combinations**
- Expected d = 18

**Resource Estimates:**
- Qubits: ~25-30 (vs 15 for 4-bit)
- Circuit depth: ~15,000-20,000 (scales roughly as n²)
- Gates: ~20,000-30,000

**Challenge:**
- Lookup approach still works but circuit becomes large
- Depth may exceed coherence time limits
- Need optimization strategies

---

## Strategy Options

### Option 1: Optimized Lookup (Best for 6-bit)

**Approach:**
- Keep lookup table but optimize implementation
- Use more efficient encoding
- Reduce circuit depth through better gate decomposition
- Apply error mitigation (ZNE) aggressively

**Pros:**
- Can reuse current code structure
- Fastest to implement
- Should work for n=31

**Cons:**
- Doesn't scale well beyond 6-bit
- Circuit depth is high

**Feasibility:** ✅ High - should work on IBM hardware

---

### Option 2: Windowed/Block Lookup (Smart Optimization)

**Approach:**
- Break n into smaller blocks (e.g., 31 = 7 + 8 + 8 + 8)
- Use smaller lookup tables
- Combine results with quantum arithmetic

**Example for n=31:**
- Block 1: values 0-7 (8 values)
- Block 2: values 8-15 (8 values)
- Block 3: values 16-23 (8 values)
- Block 4: values 24-31 (8 values)

**Pros:**
- Reduces lookup table size
- More scalable
- Lower circuit depth

**Cons:**
- More complex implementation
- Need quantum arithmetic for combining

**Feasibility:** ⚠️ Medium - requires more work

---

### Option 3: Quantum Modular Arithmetic (Most Scalable)

**Approach:**
- Implement quantum modular arithmetic operations
- Compute f(a, b) = (a + d*b) mod n directly
- Use Qiskit arithmetic circuits or custom gates

**Pros:**
- Scales to much larger keys (7-bit, 8-bit, etc.)
- General solution
- More "correct" for competition

**Cons:**
- Significant implementation effort
- Higher qubit requirements
- May need error correction/mitigation

**Feasibility:** ⚠️ Medium-High - best long-term solution

---

## Recommendation for 6-bit

**Quick Win:** Option 1 (Optimized Lookup)
- Extend current code to n=31
- Test on simulator first
- Run on IBM hardware with error mitigation
- Should complete in reasonable time

**Then Consider:** Option 3 for larger keys

---

## Scaling Beyond 6-bit

**7-bit (n=79):**
- Lookup: 79² = 6,241 combinations
- Too large for lookup approach
- **Must** use quantum arithmetic (Option 3)

**8-bit+ (n=139+):**
- Definitely need quantum arithmetic
- Consider error correction
- May need multiple runs with post-processing

---

## Competition Strategy

**Goal:** Break the **largest** key possible

**Progressive Approach:**
1. ✅ 4-bit: DONE (proof of concept)
2. 🎯 6-bit: Current target (demonstrates scaling)
3. 🚀 7-bit: Stretch goal (requires quantum arithmetic)
4. 💎 8-bit+: Competition winner territory

**Smart Strategy:**
- Get 6-bit working quickly with lookup (Option 1)
- Document the approach
- Meanwhile develop quantum arithmetic (Option 3)
- Use it to push to 7-bit and beyond

---

## Next Steps

1. **Extend lookup oracle to n=31**
2. **Test on simulator** (validate correctness)
3. **Optimize circuit** (reduce depth)
4. **Run on IBM hardware** (with ZNE)
5. **Document results** (for submission)
6. **Develop quantum arithmetic** (for 7-bit+)

