"""
Step 2: Test Lookup Approach for 7-bit

Quick test to see if lookup table approach still works for n=79.
If too slow/deep, we'll move to quantum arithmetic.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from typing import Tuple
from elliptic_curve import EllipticCurve, load_ecc_key
from math import gcd
import os
import time
from shor_ecdlp_correct import CorrectECDLPShor

print("=" * 70)
print("Step 2: Testing Lookup Approach for 7-bit (n=79)")
print("=" * 70)

# Load 7-bit key
script_dir = os.path.dirname(os.path.abspath(__file__))
key_file = os.path.join(script_dir, "ecc_keys.json")
key_data = load_ecc_key(key_file, bit_length=7)

p = key_data['prime']
G = tuple(key_data['generator_point'])
Q = tuple(key_data['public_key'])
n = key_data['subgroup_order']
expected_d = key_data['private_key']

curve = EllipticCurve(p, a=0, b=7)

print(f"\nTarget: 7-bit key")
print(f"  n = {n}")
print(f"  Expected d = {expected_d}")

# Test 1: Create circuit
print(f"\n{'='*70}")
print("Test 1: Circuit Creation")
print(f"{'='*70}")

print(f"\nCreating circuit...")
start_time = time.time()

try:
    shor = CorrectECDLPShor(curve, G, Q, n)
    qc = shor.create_shor_circuit(precision_bits=6)
    
    creation_time = time.time() - start_time
    print(f"  ✅ Circuit created in {creation_time:.2f} seconds")
    print(f"  Qubits: {qc.num_qubits}")
    print(f"  Depth: {qc.depth()}")
    print(f"  Gates: {qc.size()}")
    
except Exception as e:
    print(f"  ❌ Circuit creation failed: {e}")
    print(f"  This suggests lookup approach may be too large")
    exit(1)

# Test 2: Transpilation
print(f"\n{'='*70}")
print("Test 2: Transpilation")
print(f"{'='*70}")

print(f"\nTranspiling for simulator...")
start_time = time.time()

try:
    simulator = AerSimulator()
    transpiled = transpile(qc, simulator, optimization_level=1)  # Lower optimization for speed
    
    transpile_time = time.time() - start_time
    print(f"  ✅ Transpilation completed in {transpile_time:.2f} seconds")
    print(f"  Transpiled qubits: {transpiled.num_qubits}")
    print(f"  Transpiled depth: {transpiled.depth():,}")
    print(f"  Transpiled gates: {transpiled.size():,}")
    
    # Check if depth is reasonable
    depth = transpiled.depth()
    if depth > 200000:
        print(f"\n  ⚠️  WARNING: Circuit depth very high ({depth:,})")
        print(f"  ⚠️  May be too deep for hardware execution")
        print(f"  ⚠️  Consider quantum arithmetic approach")
    elif depth > 100000:
        print(f"\n  ⚠️  Circuit depth is high ({depth:,}) but may be manageable")
    else:
        print(f"\n  ✅ Circuit depth is reasonable")
        
except Exception as e:
    print(f"  ❌ Transpilation failed: {e}")
    print(f"  This suggests lookup approach is too complex")
    exit(1)

# Test 3: Small test run
print(f"\n{'='*70}")
print("Test 3: Small Simulation Test")
print(f"{'='*70}")

print(f"\nRunning small test (1000 shots)...")
print(f"  Note: Full run would need 50k+ shots for reliable results")

start_time = time.time()

try:
    job = simulator.run(transpiled, shots=1000)
    result = job.result()
    counts = result.get_counts()
    
    test_time = time.time() - start_time
    print(f"  ✅ Simulation completed in {test_time:.2f} seconds")
    print(f"  Unique measurements: {len(counts)}")
    
    # Quick check if we see any valid measurements
    m_bits = 7  # log2(79) ≈ 7
    valid_count = 0
    
    for bitstring in list(counts.keys())[:10]:  # Check first 10
        a_bits = bitstring[:m_bits]
        b_bits = bitstring[m_bits:]
        
        a_val = int(a_bits, 2) if a_bits else 0
        b_val = int(b_bits, 2) if b_bits else 0
        
        if gcd(b_val, n) == 1:
            valid_count += 1
    
    print(f"  Valid measurements found: {valid_count}/10 checked")
    
    if valid_count > 0:
        print(f"\n  ✅ Circuit appears to work (found valid measurements)")
    else:
        print(f"\n  ⚠️  No valid measurements in sample (may need more shots)")
    
    # Estimate full run time
    estimated_full_time = (test_time / 1000) * 50000  # For 50k shots
    print(f"\n  Estimated time for 50k shots: {estimated_full_time/60:.1f} minutes")
    
except Exception as e:
    print(f"  ❌ Simulation failed: {e}")
    print(f"  This suggests circuit may be too complex")
    exit(1)

# Summary
print(f"\n{'='*70}")
print("Summary & Recommendation")
print(f"{'='*70}")

depth = transpiled.depth()
print(f"\nCircuit Statistics:")
print(f"  Depth: {depth:,}")
print(f"  Gates: {transpiled.size():,}")
print(f"  Qubits: {transpiled.num_qubits}")

print(f"\nAssessment:")
if depth > 200000:
    print(f"  ❌ Circuit too deep for practical use")
    print(f"  ❌ Lookup approach not feasible for 7-bit")
    print(f"\n  ✅ RECOMMENDATION: Implement quantum modular arithmetic")
    print(f"     - More scalable solution")
    print(f"     - Better for 7-bit and larger keys")
elif depth > 100000:
    print(f"  ⚠️  Circuit depth is very high but may be manageable")
    print(f"  ⚠️  Consider testing on simulator with more shots")
    print(f"  ⚠️  May want to implement quantum arithmetic for better scalability")
else:
    print(f"  ✅ Circuit depth is manageable")
    print(f"  ✅ Lookup approach can work for 7-bit")
    print(f"  ✅ Can proceed to full test")

print(f"\nNext Steps:")
if depth > 200000:
    print(f"  1. Implement quantum modular arithmetic (Step 3)")
    print(f"  2. Build 7-bit oracle using quantum arithmetic")
    print(f"  3. Test on simulator")
else:
    print(f"  1. Run full simulation test (50k+ shots)")
    print(f"  2. Check if we can extract d correctly")
    print(f"  3. If successful, optimize and run on IBM hardware")

print(f"\n{'='*70}")

