"""
Debug 6-bit oracle - Check if it's encoding correctly
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit import transpile
from elliptic_curve import EllipticCurve, load_ecc_key
import os

# Load key
script_dir = os.path.dirname(os.path.abspath(__file__))
key_file = os.path.join(script_dir, "ecc_keys.json")
key_data = load_ecc_key(key_file, bit_length=6)

n = key_data['subgroup_order']
expected_d = key_data['private_key']

print("=" * 70)
print("Debugging 6-bit Oracle")
print("=" * 70)
print(f"n = {n}, Expected d = {expected_d}")
print()

# Test oracle on specific inputs
print("Testing oracle function f(a, b) = (a + d*b) mod n:")
print()

test_cases = [
    (0, 1),   # Should give: (0 + 18*1) mod 31 = 18
    (13, 1),  # Should give: (13 + 18*1) mod 31 = 0
    (26, 2),  # Should give: (26 + 18*2) mod 31 = 0
    (5, 3),   # Should give: (5 + 18*3) mod 31 = 59 mod 31 = 28
]

for a, b in test_cases:
    k = (a + expected_d * b) % n
    print(f"  f({a}, {b}) = ({a} + {expected_d}*{b}) mod {n} = {k}")

print()
print("Expected measurements that give d=18:")
print("  d = -a * b^(-1) mod 31")
print()

# Find some (a,b) pairs that should give d=18
good_pairs = []
for b in range(1, min(n, 10)):
    try:
        b_inv = pow(b, -1, n)
        # We want: -a * b_inv ≡ 18 mod n
        # So: a ≡ -18 * b mod n
        a = (-18 * b) % n
        good_pairs.append((a, b))
        print(f"  (a={a}, b={b}): d = -{a} * {b}^(-1) = -{a} * {b_inv} = {(-a * b_inv) % n} ✓")
    except:
        pass

print()
print(f"Looking for these pairs in measurements: {good_pairs[:5]}")

# Now test a simple oracle circuit
print()
print("=" * 70)
print("Testing simple oracle circuit...")
print("=" * 70)

m_bits = 5
a_reg = QuantumRegister(m_bits, 'a')
b_reg = QuantumRegister(m_bits, 'b')
point_reg = QuantumRegister(m_bits, 'point')
cr = ClassicalRegister(2 * m_bits, 'c')

qc = QuantumCircuit(a_reg, b_reg, point_reg, cr)

# Initialize specific state: |a=13, b=1>
# Binary: 13 = 01101, 1 = 00001
qc.x(a_reg[0])  # bit 0 = 1
qc.x(a_reg[2])  # bit 2 = 1
qc.x(a_reg[3])  # bit 3 = 1
# b = 1: bit 0 = 1
qc.x(b_reg[0])

# Apply oracle: should compute f(13, 1) = (13 + 18*1) mod 31 = 0
# So point_reg should be 0 (all zeros)

# For now, just measure to see what we get
qc.measure(a_reg, cr[:m_bits])
qc.measure(b_reg, cr[m_bits:])

simulator = AerSimulator()
transpiled = transpile(qc, simulator)
job = simulator.run(transpiled, shots=100)
result = job.result()
counts = result.get_counts()

print("\nMeasurement results:")
for bitstring, count in counts.items():
    a_bits = bitstring[:m_bits]
    b_bits = bitstring[m_bits:]
    a_val = int(a_bits, 2)
    b_val = int(b_bits, 2)
    print(f"  (a={a_val}, b={b_val}): {count}")

print("\n✅ Debug complete")

