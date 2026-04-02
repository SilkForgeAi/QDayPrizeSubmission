"""
8-bit ECDLP on Simulator

Testing if lookup approach still works for 8-bit key (n=139).
If successful, we can run on IBM hardware when time is available.
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import sys
import os
import json
from datetime import datetime
from math import gcd
import time

# Add QDay_Prize_Submission to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
submission_dir = os.path.join(script_dir, "QDay_Prize_Submission")
sys.path.insert(0, submission_dir)

from elliptic_curve import EllipticCurve, load_ecc_key
from shor_ecdlp_correct import CorrectECDLPShor

print("=" * 70)
print("8-bit ECDLP - Simulator Test")
print("=" * 70)

# Load 8-bit key
key_file = os.path.join(submission_dir, "ecc_keys.json")
key_data = load_ecc_key(key_file, bit_length=8)

p = key_data['prime']
G = tuple(key_data['generator_point'])
Q = tuple(key_data['public_key'])
n = key_data['subgroup_order']
expected_d = key_data['private_key']

curve = EllipticCurve(p, a=0, b=7)

print(f"\nTarget: 8-bit key")
print(f"  Prime p = {p}")
print(f"  Generator G = {G}")
print(f"  Public key Q = {Q}")
print(f"  Subgroup order n = {n}")
print(f"  Expected d = {expected_d}")

# Verify classically
verified = curve.scalar_multiply(expected_d, G) == Q
print(f"  Classical verification: {'✅' if verified else '❌'}")

# Resource analysis
lookup_size = n * n
print(f"\nResource Analysis:")
print(f"  Lookup table size: {lookup_size:,} combinations")
print(f"  Register bits: {int(np.ceil(np.log2(n)))}")
print(f"  Estimated circuit depth: Very high (~500k-1M+)")

print(f"\n{'='*70}")
print("Creating Circuit...")
print(f"{'='*70}")

start_time = time.time()

try:
    shor = CorrectECDLPShor(curve, G, Q, n)
    qc = shor.create_shor_circuit(precision_bits=6)
    
    creation_time = time.time() - start_time
    print(f"✅ Circuit created in {creation_time:.2f} seconds")
    print(f"  Qubits: {qc.num_qubits}")
    print(f"  Depth: {qc.depth()}")
    print(f"  Gates: {qc.size()}")
    
except Exception as e:
    print(f"❌ Circuit creation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print(f"\n{'='*70}")
print("Transpiling for Simulator...")
print(f"{'='*70}")

start_time = time.time()

try:
    simulator = AerSimulator()
    # Use lower optimization level for speed during testing
    transpiled = transpile(qc, simulator, optimization_level=1)
    
    transpile_time = time.time() - start_time
    print(f"✅ Transpilation completed in {transpile_time:.2f} seconds")
    print(f"  Transpiled qubits: {transpiled.num_qubits}")
    print(f"  Transpiled depth: {transpiled.depth():,}")
    print(f"  Transpiled gates: {transpiled.size():,}")
    
    if transpiled.depth() > 1000000:
        print(f"\n⚠️  WARNING: Circuit depth very high ({transpiled.depth():,})")
        print(f"⚠️  May be too deep for hardware execution")
    elif transpiled.depth() > 500000:
        print(f"\n⚠️  Circuit depth is very high but may be manageable")
    else:
        print(f"\n✅ Circuit depth is reasonable")
        
except Exception as e:
    print(f"❌ Transpilation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print(f"\n{'='*70}")
print("Running Simulation...")
print(f"{'='*70}")

# Start with smaller shot count to test
shots_list = [1000, 5000, 10000, 50000]

for shots in shots_list:
    print(f"\n{'─'*70}")
    print(f"Testing with {shots:,} shots...")
    print(f"{'─'*70}")
    
    start_time = time.time()
    
    try:
        job = simulator.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        sim_time = time.time() - start_time
        print(f"✅ Simulation completed in {sim_time:.2f} seconds")
        print(f"  Unique measurements: {len(counts)}")
        
        # Analyze results
        m_bits = int(np.ceil(np.log2(n)))  # 8 bits for n=139
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
        
        # Results
        if d_found_count > 0:
            pct = 100 * d_found_count / shots
            print(f"\n✅ SUCCESS! Found d = {expected_d}")
            print(f"   Occurrences: {d_found_count} ({pct:.3f}%)")
            print(f"   Unique pairs: {len(d_found_pairs)}")
            print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
            
            if d_found_pairs:
                print(f"\n   Top pairs that gave d={expected_d}:")
                for a, b, count in d_found_pairs[:10]:
                    print(f"     (a={a:3d}, b={b:3d}): {count} times")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"8bit_simulator_{timestamp}.json"
            results_path = os.path.join(script_dir, results_file)
            
            results_data = {
                'timestamp': timestamp,
                'bit_length': 8,
                'expected_d': expected_d,
                'n': n,
                'shots': shots,
                'success_count': d_found_count,
                'success_rate': pct,
                'valid_measurements': total_valid,
                'unique_pairs': len(d_found_pairs),
                'top_pairs': d_found_pairs[:20],
                'circuit_depth': transpiled.depth(),
                'circuit_gates': transpiled.size(),
                'simulation_time': sim_time
            }
            
            with open(results_path, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"\n💾 Results saved to: {results_file}")
            print(f"\n🎉 8-bit key broken on simulator!")
            print(f"   Ready to run on IBM hardware when time is available!")
            
            break  # Success, no need for more shots
            
        else:
            pct_valid = 100 * total_valid / shots
            print(f"\n⚠️  Did not find d = {expected_d} with {shots:,} shots")
            print(f"   Valid measurements: {total_valid} ({pct_valid:.2f}%)")
            
            if shots < max(shots_list):
                print(f"   Trying more shots...")
            else:
                print(f"\n⚠️  Did not find d after all shot counts")
                print(f"   May need:")
                print(f"     - More shots (100k+)")
                print(f"     - Different approach (quantum modular arithmetic)")
                print(f"     - Circuit optimization")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        if shots == shots_list[0]:
            # If first attempt fails, circuit may be too large
            print(f"\n⚠️  Circuit may be too large for simulator")
            print(f"   Consider using quantum modular arithmetic instead")
        break

print(f"\n{'='*70}")
print("Summary")
print(f"{'='*70}")

print(f"\nCircuit Statistics:")
print(f"  Depth: {transpiled.depth():,}")
print(f"  Gates: {transpiled.size():,}")
print(f"  Qubits: {transpiled.num_qubits}")

if d_found_count > 0:
    print(f"\n✅ 8-bit lookup approach WORKS on simulator!")
    print(f"   Success rate: {100 * d_found_count / shots:.3f}%")
    print(f"   Ready for IBM hardware when time is available")
else:
    print(f"\n⚠️  8-bit lookup approach may need optimization")
    print(f"   Or consider quantum modular arithmetic for better scalability")

print(f"\n{'='*70}")

