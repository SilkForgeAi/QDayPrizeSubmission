#!/usr/bin/env python3
"""
Analyze 8-bit measurements in detail
Check if measurements are being parsed correctly and look for patterns
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'QDay_Prize_Submission'))

from qiskit_ibm_runtime import QiskitRuntimeService
from shor_ecdlp_correct import CorrectECDLPShor
from elliptic_curve import EllipticCurve, load_ecc_key

JOB_ID = "d5p98hgh0i0s73eoutvg"

print("=" * 70)
print("Detailed 8-bit Measurement Analysis")
print("=" * 70)

# Load key
key_file = os.path.join("QDay_Prize_Submission", "ecc_keys.json")
key_data = load_ecc_key(key_file, bit_length=8)
expected_d = key_data['private_key']
n = key_data['subgroup_order']

print(f"\nTarget: 8-bit key")
print(f"  n = {n}")
print(f"  Expected d = {expected_d}")

# Get results
service = QiskitRuntimeService()
job = service.job(JOB_ID)
result = job.result()

# Extract counts
try:
    counts = result[0].data.c.get_counts()
except AttributeError:
    counts = dict(result[0].data.c.array)

print(f"\n📊 Measurement Statistics:")
print(f"  Total shots: {sum(counts.values()):,}")
print(f"  Unique outcomes: {len(counts):,}")
print(f"  Top 10 measurements:")

# Initialize Shor extractor
shor = CorrectECDLPShor(
    EllipticCurve(key_data['prime'], a=0, b=7),
    tuple(key_data['generator_point']),
    tuple(key_data['public_key']),
    n
)

# Analyze top measurements
print(f"\n{'='*70}")
print("Top 20 Measurements Analysis")
print(f"{'='*70}")
print(f"{'Bitstring':<20} {'Count':<8} {'%':<8} {'a':<6} {'b':<6} {'d_candidate':<12} {'Match':<8}")
print("-" * 70)

sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
total_shots = sum(counts.values())
success_count = 0
valid_measurements = 0

for bitstring, count in sorted_counts[:20]:
    # Parse bitstring - need to know how many bits for a and b
    # For 8-bit, n=139, so we need ceil(log2(139)) = 8 bits for each
    total_bits = len(bitstring)
    m_bits = (total_bits + 1) // 2  # Split roughly in half
    
    a_bits = bitstring[:m_bits] if total_bits >= m_bits else bitstring[:total_bits//2]
    b_bits = bitstring[m_bits:] if total_bits >= m_bits else bitstring[total_bits//2:]
    
    a_measured = int(a_bits, 2) if a_bits else 0
    b_measured = int(b_bits, 2) if b_bits else 0
    
    d_candidate = shor.extract_d_from_measurement(a_measured, b_measured)
    
    match = "✅" if d_candidate == expected_d else ""
    if d_candidate == expected_d:
        success_count += count
    
    if d_candidate is not None:
        valid_measurements += count
    
    percentage = (count / total_shots * 100) if total_shots > 0 else 0
    print(f"{bitstring:<20} {count:<8} {percentage:>6.3f}% {a_measured:<6} {b_measured:<6} {str(d_candidate) if d_candidate else 'None':<12} {match}")

print(f"\n{'='*70}")
print("Summary")
print(f"{'='*70}")
print(f"  Total shots: {total_shots:,}")
print(f"  Valid measurements: {valid_measurements:,} ({valid_measurements/total_shots*100:.2f}%)")
print(f"  Success count (d={expected_d}): {success_count}")
print(f"  Success rate: {success_count/total_shots*100:.4f}%")

if success_count == 0:
    print(f"\n⚠️  No correct key found in top 20 measurements")
    print(f"   This is expected with:")
    print(f"   - Very low success rate (0.002% = 1/50k)")
    print(f"   - Only 5,000 shots (expected ~0.1 correct results)")
    print(f"   - Circuit depth: 296,444 (very deep, high noise)")
    print(f"\n💡 Recommendations:")
    print(f"   1. Run with more shots (50k-100k) for better chance")
    print(f"   2. Check if measurements are being parsed correctly")
    print(f"   3. Verify circuit/oracle is correct for 8-bit")
    print(f"   4. Consider if circuit depth is too high for current hardware")

# Check bitstring length distribution
print(f"\n{'='*70}")
print("Bitstring Length Analysis")
print(f"{'='*70}")
length_dist = {}
for bitstring in counts.keys():
    length = len(bitstring)
    length_dist[length] = length_dist.get(length, 0) + 1

for length, count in sorted(length_dist.items()):
    print(f"  Length {length}: {count} unique outcomes")

# Expected: For n=139, we need 8 bits for a and 8 bits for b = 16 bits total
expected_length = 2 * (n.bit_length())
print(f"\n  Expected bitstring length: {expected_length} bits (2 × {n.bit_length()} for a and b)")
