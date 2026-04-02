#!/usr/bin/env python3
"""
Retrieve 8-bit IBM Quantum job results
Job ID: d5p98hgh0i0s73eoutvg
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'QDay_Prize_Submission'))

from qiskit_ibm_runtime import QiskitRuntimeService
from shor_ecdlp_correct import CorrectECDLPShor
from elliptic_curve import EllipticCurve, load_ecc_key
import json
from datetime import datetime

JOB_ID = "d5p98hgh0i0s73eoutvg"

print("=" * 70)
print("Retrieving 8-bit ECDLP Results from IBM Quantum")
print("=" * 70)

# Connect to IBM
service = QiskitRuntimeService()
job = service.job(JOB_ID)

print(f"\nJob ID: {job.job_id()}")
print(f"Status: {job.status()}")
print(f"Backend: {job.backend()}")

# Wait for completion if needed
if job.status() not in ['DONE', 'COMPLETED']:
    print(f"\n⏳ Job status: {job.status()}")
    print("   Waiting for completion...")
    try:
        result = job.result()
        print("   ✅ Job completed!")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        print(f"   Job may still be running. Check status later.")
        exit(1)
else:
    result = job.result()

# Load key for verification
key_file = os.path.join("QDay_Prize_Submission", "ecc_keys.json")
key_data = load_ecc_key(key_file, bit_length=8)
expected_d = key_data['private_key']
n = key_data['subgroup_order']

# Process results
print(f"\n📊 Processing Results...")
# Access counts from DataBin structure
# Based on 6-bit script: result[0].data.c.get_counts() or dict(result[0].data.c.array)
try:
    # Method 1: Try get_counts() (preferred)
    counts = result[0].data.c.get_counts()
    print(f"   ✅ Extracted counts using get_counts()")
except AttributeError:
    # Method 2: Try accessing .array attribute
    try:
        counts = dict(result[0].data.c.array)
        print(f"   ✅ Extracted counts from .array")
    except AttributeError:
        # Method 3: Try direct dict conversion
        try:
            counts = dict(result[0].data.c)
            print(f"   ✅ Extracted counts by converting to dict")
        except:
            # Debug output
            print(f"   ❌ Could not extract counts")
            print(f"   data.c type: {type(result[0].data.c)}")
            print(f"   data.c attributes: {[x for x in dir(result[0].data.c) if not x.startswith('_')][:10]}")
            raise
        
    else:
        # Try other methods
        if hasattr(data_bin, 'get_counts'):
            counts = data_bin.get_counts()
        elif hasattr(data_bin, 'items'):
            # DataBin might be dict-like
            counts = dict(data_bin.items())
        else:
            raise AttributeError("DataBin has no 'c' attribute")
            
except (AttributeError, TypeError) as e:
    print(f"   Trying alternative access methods...")
    print(f"   Error: {e}")
    
    # Fallback: try accessing quasi_dists
    try:
        if hasattr(result[0], 'quasi_dists'):
            quasi_dist = result[0].quasi_dists[0]
            total_shots = 5000
            counts = {k: int(v * total_shots) for k, v in quasi_dist.items()}
            print(f"   ✅ Converted quasi_dist to counts")
        else:
            raise AttributeError("No quasi_dists found")
    except:
        # Last resort: debug output
        print(f"   Result[0].data type: {type(result[0].data)}")
        print(f"   Result[0].data attributes: {[x for x in dir(result[0].data) if not x.startswith('_')]}")
        if hasattr(result[0].data, 'c'):
            print(f"   result[0].data.c type: {type(result[0].data.c)}")
            print(f"   result[0].data.c value (first 5): {list(result[0].data.c.items())[:5] if hasattr(result[0].data.c, 'items') else result[0].data.c[:5] if hasattr(result[0].data.c, '__getitem__') else 'N/A'}")
        raise Exception(f"Could not extract counts: {e}")

print(f"\nTotal measurements: {sum(counts.values())}")
print(f"Unique outcomes: {len(counts)}")

# Extract d from measurements
shor = CorrectECDLPShor(
    EllipticCurve(key_data['prime'], a=0, b=7),
    tuple(key_data['generator_point']),
    tuple(key_data['public_key']),
    n
)

success_count = 0
d_found = {}

print(f"\nAnalyzing measurements...")
for bitstring, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:20]:
    # Parse bitstring (a and b measurements)
    total_bits = len(bitstring)
    a_bits = bitstring[:total_bits//2]
    b_bits = bitstring[total_bits//2:]
    
    a_measured = int(a_bits, 2) if a_bits else 0
    b_measured = int(b_bits, 2) if b_bits else 0
    
    d_candidate = shor.extract_d_from_measurement(a_measured, b_measured)
    
    if d_candidate == expected_d:
        success_count += count
        if d_candidate not in d_found:
            d_found[d_candidate] = 0
        d_found[d_candidate] += count

# Save results
results = {
    "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
    "job_id": JOB_ID,
    "bit_length": 8,
    "n": n,
    "expected_d": expected_d,
    "backend": str(job.backend()),
    "shots": sum(counts.values()),
    "success_count": success_count,
    "success_rate": success_count / sum(counts.values()) * 100 if counts else 0,
    "top_20_measurements": [
        {
            "bitstring": bitstring,
            "count": count,
            "percentage": count / sum(counts.values()) * 100
        }
        for bitstring, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:20]
    ],
    "d_found": d_found
}

output_file = f"8bit_ibm_{JOB_ID}_{results['timestamp']}.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*70}")
print("RESULTS SUMMARY")
print(f"{'='*70}")
print(f"\n✅ Job completed successfully!")
print(f"   Job ID: {JOB_ID}")
print(f"   Shots: {results['shots']:,}")
print(f"   Success count: {success_count}")
print(f"   Success rate: {results['success_rate']:.4f}%")
print(f"   Expected d: {expected_d}")
print(f"\n📁 Results saved to: {output_file}")

if success_count > 0:
    print(f"\n🎉 SUCCESS! Found correct key {expected_d} {success_count} times!")
else:
    print(f"\n⚠️  No correct key found in top measurements")
    print(f"   This is expected with low success rate (0.002%)")
    print(f"   May need more shots or check all measurements")
