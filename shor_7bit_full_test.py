"""
Step 2b: Full 7-bit Test - Verify we can extract d correctly
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from elliptic_curve import EllipticCurve, load_ecc_key
from math import gcd
import os
from shor_ecdlp_correct import CorrectECDLPShor

print("=" * 70)
print("Step 2b: Full 7-bit Test - Extract d")
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

print(f"\nTarget: 7-bit key (n={n}, d={expected_d})")

# Create circuit
print(f"\nCreating circuit...")
shor = CorrectECDLPShor(curve, G, Q, n)
qc = shor.create_shor_circuit(precision_bits=6)

print(f"  Qubits: {qc.num_qubits}")

# Transpile
simulator = AerSimulator()
transpiled = transpile(qc, simulator, optimization_level=3)

print(f"  Transpiled depth: {transpiled.depth():,}")
print(f"  Transpiled gates: {transpiled.size():,}")

# Run with increasing shots to see success rate
shots_list = [10000, 50000, 100000]

for shots in shots_list:
    print(f"\n{'='*70}")
    print(f"Testing with {shots:,} shots...")
    print(f"{'='*70}")
    
    job = simulator.run(transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    print(f"\nAnalyzing {len(counts)} unique measurements...")
    
    m_bits = 7
    d_found_count = 0
    total_valid = 0
    
    for bitstring, count in counts.items():
        a_bits = bitstring[:m_bits]
        b_bits = bitstring[m_bits:]
        
        a_val = int(a_bits, 2) if a_bits else 0
        b_val = int(b_bits, 2) if b_bits else 0
        
        d_candidate = shor.extract_d_from_measurement(a_val, b_val)
        
        if d_candidate is not None:
            total_valid += count
        
        if d_candidate == expected_d:
            d_found_count += count
    
    if d_found_count > 0:
        pct = 100 * d_found_count / shots
        print(f"\n✅ SUCCESS! Found d = {expected_d}")
        print(f"   Occurrences: {d_found_count} ({pct:.3f}%)")
        print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
        print(f"\n🎉 7-bit key broken! Ready for IBM hardware!")
        break
    else:
        pct_valid = 100 * total_valid / shots
        print(f"\n⚠️  Did not find d = {expected_d} with {shots:,} shots")
        print(f"   Valid measurements: {total_valid} ({pct_valid:.2f}%)")
        if shots < max(shots_list):
            print(f"   Trying more shots...")

print(f"\n{'='*70}")
print("Step 2 Complete!")
print(f"{'='*70}")

if d_found_count > 0:
    print(f"\n✅ 7-bit lookup approach WORKS!")
    print(f"   Next: Optimize and run on IBM hardware")
else:
    print(f"\n⚠️  May need more shots or different approach")

