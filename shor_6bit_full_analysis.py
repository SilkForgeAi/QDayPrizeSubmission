"""
6-bit Full Analysis - Check ALL measurements for d=18
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit import transpile
from elliptic_curve import EllipticCurve, load_ecc_key
from math import gcd
import os

# Load key
script_dir = os.path.dirname(os.path.abspath(__file__))
key_file = os.path.join(script_dir, "ecc_keys.json")
key_data = load_ecc_key(key_file, bit_length=6)

p = key_data['prime']
G = tuple(key_data['generator_point'])
Q = tuple(key_data['public_key'])
n = key_data['subgroup_order']
expected_d = key_data['private_key']

curve = EllipticCurve(p, a=0, b=7)

m_bits = 5

# Expected pairs that give d=18
expected_pairs = []
for b in range(1, n):
    try:
        b_inv = pow(b, -1, n)
        a = (-expected_d * b) % n
        expected_pairs.append((a, b))
    except:
        pass

print("=" * 70)
print("6-bit Full Analysis - Checking ALL measurements")
print("=" * 70)
print(f"Expected d = {expected_d}")
print(f"Expected pairs (first 10): {expected_pairs[:10]}")
print()

# Use the working 4-bit code structure but for 6-bit
from shor_ecdlp_correct import CorrectECDLPShor

shor = CorrectECDLPShor(curve, G, Q, n)

# Create circuit
print("Creating circuit...")
qc = shor.create_shor_circuit(precision_bits=6)

print(f"  Qubits: {qc.num_qubits}")
print(f"  Depth: {qc.depth()}")

# Run with many shots
shots = 32768
print(f"\nRunning with {shots:,} shots...")

simulator = AerSimulator()
transpiled = transpile(qc, simulator, optimization_level=2)

job = simulator.run(transpiled, shots=shots)
result = job.result()
counts = result.get_counts()

print(f"\nAnalyzing ALL {len(counts)} unique measurements...")

# Check ALL measurements for d=18
d_found_count = 0
d_found_pairs = []
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
        d_found_pairs.append((a_val, b_val, count))

# Sort by count
d_found_pairs.sort(key=lambda x: x[2], reverse=True)

print(f"\n{'='*70}")
print("RESULTS")
print(f"{'='*70}")

if d_found_count > 0:
    pct = 100 * d_found_count / shots
    print(f"\n✅ FOUND d = {expected_d}!")
    print(f"   Total occurrences: {d_found_count} ({pct:.2f}%)")
    print(f"   Unique pairs: {len(d_found_pairs)}")
    print(f"\n   Top pairs that gave d={expected_d}:")
    for a, b, count in d_found_pairs[:10]:
        pct_pair = 100 * count / shots
        print(f"     (a={a:2d}, b={b:2d}): {count:4d} times ({pct_pair:.2f}%)")
    
    print(f"\n   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
    print(f"\n🎉 6-bit key broken! Success rate: {pct:.2f}%")
else:
    print(f"\n⚠️  Did NOT find d = {expected_d} in any measurement")
    print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
    print(f"\n   Checking if expected pairs appear at all...")
    
    # Check if any expected pairs appear
    found_expected = []
    for bitstring, count in counts.items():
        a_bits = bitstring[:m_bits]
        b_bits = bitstring[m_bits:]
        a_val = int(a_bits, 2) if a_bits else 0
        b_val = int(b_bits, 2) if b_bits else 0
        
        if (a_val, b_val) in expected_pairs:
            found_expected.append((a_val, b_val, count))
    
    if found_expected:
        found_expected.sort(key=lambda x: x[2], reverse=True)
        print(f"   Found {len(found_expected)} expected pairs (but d extraction failed):")
        for a, b, count in found_expected[:5]:
            print(f"     (a={a}, b={b}): {count} times")
    else:
        print(f"   ⚠️  None of the expected pairs appeared in measurements")
        print(f"   This suggests the oracle may not be working correctly")

print(f"\n{'='*70}")

