# Quick Start Guide - QDay Prize

## What We Have

✅ **Classical ECC Operations** - All working  
✅ **Key Verification** - All keys verified  
✅ **Quantum Framework** - Circuit structure ready  
⚠️ **Oracle** - Needs implementation  

## Current Status

**4-bit Key (Target):**
- Prime: 13
- Generator: (11, 5)
- Public Key: (11, 8)
- Private Key: 6 (expected)
- Subgroup Order: 7

**Circuit Stats:**
- Qubits: 11
- Runs on simulator
- Oracle placeholder exists

## What's Needed

**The Oracle** must compute: `f(a, b) = (a + b*d) mod n`

This requires:
- Quantum modular addition
- Quantum modular multiplication  
- Control logic for superposition

## Next Action

1. **Research Qiskit Arithmetic**
   ```python
   from qiskit.circuit.library import ...
   # Check for modular arithmetic circuits
   ```

2. **Implement Oracle**
   - Add quantum modular operations
   - Compute (a + b*d) mod n
   - Test with 4-bit key

3. **Validate**
   - Extract period from measurements
   - Recover d
   - Verify d = 6

## Run Current Code

```bash
cd qday_prize
python3 verify_keys.py          # Verify all keys
python3 shor_oracle_4bit.py     # Run quantum circuit (oracle needs work)
```

## Helpful Resources

- Qiskit Textbook: Shor's Algorithm
- Competition guidelines on oracle requirements
- Open-source quantum ECDLP implementations

---

**You're ready to implement the oracle!** 🎯

