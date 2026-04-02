"""Debug script to verify curve operations"""

import sys
sys.path.append('/Users/brixxbeat/Desktop/ibm-quantum/qday_prize')

from elliptic_curve import EllipticCurve, load_ecc_key
import os

# Load 4-bit key
script_dir = os.path.dirname(os.path.abspath(__file__))
key_file = os.path.join(script_dir, "ecc_keys.json")
key_data = load_ecc_key(key_file, bit_length=4)

p = key_data['prime']
G = tuple(key_data['generator_point'])
Q = tuple(key_data['public_key'])
n = key_data['subgroup_order']
expected_d = key_data['private_key']

print(f"Prime p = {p}")
print(f"Generator G = {G}")
print(f"Public key Q = {Q}")
print(f"Subgroup order n = {n}")
print(f"Expected private key d = {expected_d}\n")

# Create curve
curve = EllipticCurve(p, generator=G)
print(f"Curve: y^2 = x^3 + {curve.a}x + {curve.b} (mod {p})")
print(f"G on curve: {curve.is_on_curve(G)}")
print(f"Q on curve: {curve.is_on_curve(Q)}\n")

# Test scalar multiplication step by step
print("Testing scalar multiplication step by step:")
print(f"1*G = {curve.scalar_multiply(1, G)}")
print(f"2*G = {curve.scalar_multiply(2, G)}")
print(f"3*G = {curve.scalar_multiply(3, G)}")
print(f"4*G = {curve.scalar_multiply(4, G)}")
print(f"5*G = {curve.scalar_multiply(5, G)}")
print(f"6*G = {curve.scalar_multiply(6, G)}")
print(f"7*G = {curve.scalar_multiply(7, G)} (should be point at infinity)\n")

print(f"Expected Q = {Q}")
print(f"6*G = {curve.scalar_multiply(6, G)}")
print(f"Match: {curve.scalar_multiply(6, G) == Q}\n")

# Verify the curve equation for Q
x_q, y_q = Q
lhs = (y_q**2) % p
rhs = (x_q**3 + curve.a * x_q + curve.b) % p
print(f"Verify Q is on curve:")
print(f"  y^2 mod p = {lhs}")
print(f"  x^3 + ax + b mod p = {rhs}")
print(f"  Match: {lhs == rhs}\n")

# Try all scalars to find which one gives Q
print("Brute force search:")
for k in range(1, n + 1):
    kG = curve.scalar_multiply(k, G)
    if kG == Q:
        print(f"  Found: {k}*G = {Q}")
    print(f"  {k}*G = {kG}")

