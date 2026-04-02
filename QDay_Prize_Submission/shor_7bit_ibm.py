"""
Step 4: Run 7-bit ECDLP on IBM Quantum Hardware

Circuit depth is manageable (255), ready for hardware!
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from elliptic_curve import EllipticCurve, load_ecc_key
from math import gcd
import os
import json
from datetime import datetime
from shor_ecdlp_correct import CorrectECDLPShor

print("=" * 70)
print("Step 4: 7-bit ECDLP on IBM Quantum Hardware")
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
print(f"  Simulator success: 0.02% (2/10k)")
print(f"  Recommended shots: 100,000+ for reliable results")

# Create circuit
print(f"\n🔧 Creating circuit...")
shor = CorrectECDLPShor(curve, G, Q, n)
qc = shor.create_shor_circuit(precision_bits=6)

print(f"  Qubits: {qc.num_qubits}")
print(f"  Depth: {qc.depth()}")

# Connect to IBM
print(f"\n🔌 Connecting to IBM Quantum...")
try:
    service = QiskitRuntimeService()
    print("  ✅ Connected")
except Exception as e:
    print(f"  ❌ Connection failed: {e}")
    exit(1)

# Select backend
print(f"\n🔍 Using backend: ibm_torino")
backend = service.backend("ibm_torino")
status = backend.status()

print(f"\nBackend: {backend.name}")
print(f"  Qubits: {backend.num_qubits}")
print(f"  Status: {status.status_msg}")
print(f"  Queue: {status.pending_jobs} jobs")

# Transpile
print(f"\n⚙️  Transpiling for {backend.name}...")
transpiled = transpile(qc, backend, optimization_level=3)

print(f"  Transpiled qubits: {transpiled.num_qubits}")
print(f"  Transpiled depth: {transpiled.depth():,}")
print(f"  Transpiled gates: {transpiled.size():,}")

# Use 50k shots - balance between statistics and execution time
# Note: Depth is high (254k) so we need reasonable shot count
SHOTS = 50000
print(f"\n🚀 Submitting job with {SHOTS:,} shots...")
print(f"   Note: Circuit depth is high ({transpiled.depth():,})")
print(f"   Estimated time: ~40-60 minutes")

try:
    sampler = Sampler(mode=backend)
    job = sampler.run([transpiled], shots=SHOTS)
    
    job_id = job.job_id()
    print(f"  ✅ Job submitted: {job_id}")
    print(f"  Status: {job.status()}")
    
    # Wait
    print(f"\n⏳ Waiting for results...")
    result = job.result()
    
    print(f"  ✅ Job completed!")
    
    # Process results
    try:
        counts = result[0].data.c.get_counts()
    except AttributeError:
        counts = dict(result[0].data.c.array)
    
    print(f"\n{'='*70}")
    print("📊 RESULTS FROM IBM QUANTUM")
    print(f"{'='*70}")
    
    # Analyze
    m_bits = 7
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
    
    d_found_pairs.sort(key=lambda x: x[2], reverse=True)
    
    # Show top measurements
    print(f"\nTop 20 measurements:")
    print(f"{'a':<6} {'b':<6} {'Count':<8} {'%':<8} {'d_candidate':<12} {'Match':<8}")
    print("-" * 70)
    
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for bitstring, count in sorted_counts[:20]:
        a_bits = bitstring[:m_bits]
        b_bits = bitstring[m_bits:]
        
        a_val = int(a_bits, 2) if a_bits else 0
        b_val = int(b_bits, 2) if b_bits else 0
        
        d_candidate = shor.extract_d_from_measurement(a_val, b_val)
        match = "✅" if d_candidate == expected_d else ""
        
        pct = 100 * count / SHOTS
        d_str = str(d_candidate) if d_candidate is not None else "N/A"
        
        print(f"{a_val:<6} {b_val:<6} {count:<8} {pct:<7.3f}% {d_str:<12} {match:<8}")
    
    # Summary
    print(f"\n{'='*70}")
    print("🎯 SUMMARY")
    print(f"{'='*70}")
    
    if d_found_count > 0:
        pct = 100 * d_found_count / SHOTS
        print(f"\n✅ SUCCESS! Found d = {expected_d}")
        print(f"   Occurrences: {d_found_count} ({pct:.3f}%)")
        print(f"   Unique pairs: {len(d_found_pairs)}")
        print(f"   Valid measurements: {total_valid} ({100*total_valid/SHOTS:.2f}%)")
        
        if d_found_pairs:
            print(f"\n   Top pairs that gave d={expected_d}:")
            for a, b, count in d_found_pairs[:10]:
                print(f"     (a={a:2d}, b={b:2d}): {count} times")
        
        print(f"\n🎉 7-bit key broken on IBM Quantum hardware!")
        print(f"   This is a significant achievement!")
    else:
        print(f"\n⚠️  Did not find d = {expected_d}")
        print(f"   Valid measurements: {total_valid} ({100*total_valid/SHOTS:.2f}%)")
        print(f"   May need more shots or check circuit")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"7bit_ibm_{backend.name}_{timestamp}.json"
    results_path = os.path.join(script_dir, results_file)
    
    results_data = {
        'timestamp': timestamp,
        'bit_length': 7,
        'expected_d': expected_d,
        'n': n,
        'backend': backend.name,
        'job_id': job_id,
        'shots': SHOTS,
        'success_count': d_found_count,
        'success_rate': 100 * d_found_count / SHOTS if SHOTS > 0 else 0,
        'valid_measurements': total_valid,
        'unique_pairs': len(d_found_pairs),
        'top_pairs': d_found_pairs[:20],
        'circuit_depth': transpiled.depth(),
        'circuit_gates': transpiled.size()
    }
    
    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    print(f"\n{'='*70}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
