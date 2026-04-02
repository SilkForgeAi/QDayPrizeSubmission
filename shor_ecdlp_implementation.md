# Shor's Algorithm for ECDLP - Implementation Plan

Based on competition guidelines and best practices.

## Problem Reduction

**ECDLP:** Given G, Q = d*G, find d.

**Shor's Approach:** Find period of f(a, b) = (a*G + b*Q) mod n

The period reveals: if f(a, b) = f(a', b'), then:
- (a - a')*G = (b' - b)*Q
- Since Q = d*G: (a - a')*G = (b' - b)*d*G
- So: (a - a') ≡ (b' - b)*d (mod n)
- Therefore: d ≡ (a - a') / (b' - b) (mod n)

## Implementation Strategy

### Phase 1: Simplified Oracle (For 4-bit key)

For small keys (n=7), we can use a simplified approach:

1. **Classical Pre-computation** (if allowed by rules)
   - Pre-compute all multiples of G: {G, 2*G, ..., 7*G}
   - Store in lookup table
   - Oracle becomes: f(a, b) = lookup[(a + b*d) mod n]

2. **Quantum Period Finding**
   - Use QFT to find period
   - Extract d from period

### Phase 2: Full Quantum Implementation

For larger keys, need full quantum EC arithmetic:

1. **Quantum Modular Arithmetic**
   - Quantum addition, multiplication, inversion mod p
   - Use Qiskit's arithmetic circuits where possible

2. **Quantum EC Point Operations**
   - Encode points as quantum states
   - Quantum point addition oracle
   - Quantum scalar multiplication

3. **Optimizations**
   - Semi-classical QFT (reduce qubits)
   - Windowed arithmetic (reduce depth)
   - Out-of-place operations (reduce ancilla)

## Circuit Structure

```
Shor ECDLP Circuit:
├── Period Register (n_qubits ≈ 2*log2(n))
│   └── Initialize: |0...0⟩ → Hadamard → superposition
├── Oracle Register (for storing f(a, b) results)
│   └── Oracle: |a, b⟩ → |a, b, f(a, b)⟩
└── Period Finding
    └── Inverse QFT → Measure period
```

## Resource Estimates (4-bit key, n=7)

- Period register: 6 qubits (can represent 0-63, need ~14 for period 7)
- Oracle ancilla: ~8-10 qubits (for point encoding)
- **Total: ~14-16 qubits** ✅ Feasible on IBM Brisbane (127 qubits)

## Next Steps

1. ✅ Classical verification (DONE)
2. ⬜ Implement simplified oracle for 4-bit key
3. ⬜ Test period finding on simulator
4. ⬜ Run on real hardware
5. ⬜ Scale to larger keys

