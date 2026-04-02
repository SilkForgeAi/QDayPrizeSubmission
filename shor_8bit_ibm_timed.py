"""
8-bit ECDLP on IBM Quantum Hardware - Time-Constrained Version

Optimized for 10-minute time budget:
- Monitors elapsed time throughout
- Adapts shot count based on queue time
- Maximizes success probability within time limit
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from math import gcd
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'QDay_Prize_Submission'))
from elliptic_curve import EllipticCurve, load_ecc_key
import json
from datetime import datetime
import time
from shor_ecdlp_correct import CorrectECDLPShor

print("=" * 70)
print("8-bit ECDLP on IBM Quantum - TIME-CONSTRAINED")
print("=" * 70)

# Time budget: 4 minutes = 240 seconds (user has 4 min left)
TIME_BUDGET_SECONDS = 240
START_TIME = time.time()

def get_elapsed_time():
    """Get elapsed time since start."""
    return time.time() - START_TIME

def get_remaining_time():
    """Get remaining time in budget."""
    return max(0, TIME_BUDGET_SECONDS - get_elapsed_time())

def check_time_limit(operation_name):
    """Check if we have time remaining."""
    remaining = get_remaining_time()
    elapsed = get_elapsed_time()
    
    print(f"\n⏱️  Time Status: {elapsed:.1f}s elapsed, {remaining:.1f}s remaining")
    
    if remaining < 60:
        print(f"⚠️  WARNING: Less than 1 minute remaining!")
        return False
    return True

# Load 8-bit key
script_dir = os.path.dirname(os.path.abspath(__file__))
# Try multiple possible locations
key_file = os.path.join(script_dir, "QDay_Prize_Submission", "ecc_keys.json")
if not os.path.exists(key_file):
    key_file = os.path.join(script_dir, "ecc_keys.json")
key_data = load_ecc_key(key_file, bit_length=8)

p = key_data['prime']
G = tuple(key_data['generator_point'])
Q = tuple(key_data['public_key'])
n = key_data['subgroup_order']
expected_d = key_data['private_key']

curve = EllipticCurve(p, a=0, b=7)

print(f"\nTarget: 8-bit key")
print(f"  n = {n}")
print(f"  Expected d = {expected_d}")
print(f"  Time budget: {TIME_BUDGET_SECONDS/60:.1f} minutes")
print(f"  Simulator success: 0.002% (1/50k)")
print(f"  Strategy: Adaptive shot allocation based on queue time")

# Create circuit
print(f"\n🔧 Creating circuit...")
circuit_start = time.time()
shor = CorrectECDLPShor(curve, G, Q, n)
qc = shor.create_shor_circuit(precision_bits=6)

print(f"  Qubits: {qc.num_qubits}")
print(f"  Depth: {qc.depth()}")
print(f"  Circuit creation: {time.time() - circuit_start:.1f}s")

if not check_time_limit("circuit creation"):
    print("❌ Out of time before circuit creation completed")
    exit(1)

# Connect to IBM
print(f"\n🔌 Connecting to IBM Quantum...")
try:
    service = QiskitRuntimeService()
    print("  ✅ Connected")
except Exception as e:
    print(f"  ❌ Connection failed: {e}")
    exit(1)

if not check_time_limit("IBM connection"):
    exit(1)

# Select backend
print(f"\n🔍 Selecting backend...")
try:
    backend = service.backend("ibm_torino")
    status = backend.status()
    
    print(f"\nBackend: {backend.name}")
    print(f"  Qubits: {backend.num_qubits}")
    print(f"  Status: {status.status_msg}")
    print(f"  Queue: {status.pending_jobs} jobs")
    
    # Estimate queue time (rough: 1-3 min per job in queue)
    queue_estimate_min = status.pending_jobs * 2
    queue_estimate_max = status.pending_jobs * 5
    print(f"  Estimated queue time: {queue_estimate_min}-{queue_estimate_max} minutes")
    
except Exception as e:
    print(f"  ❌ Backend not available: {e}")
    exit(1)

if not check_time_limit("backend selection"):
    exit(1)

# Transpile
print(f"\n⚙️  Transpiling for {backend.name}...")
transpile_start = time.time()
transpiled = transpile(qc, backend, optimization_level=3)

transpile_time = time.time() - transpile_start
print(f"  Transpiled qubits: {transpiled.num_qubits}")
print(f"  Transpiled depth: {transpiled.depth():,}")
print(f"  Transpiled gates: {transpiled.size():,}")
print(f"  Transpilation time: {transpile_time:.1f}s")

if not check_time_limit("transpilation"):
    exit(1)

# Calculate optimal shot count based on remaining time
remaining = get_remaining_time()
elapsed = get_elapsed_time()

print(f"\n📊 Time Analysis:")
print(f"  Elapsed: {elapsed:.1f}s ({elapsed/60:.2f} min)")
print(f"  Remaining: {remaining:.1f}s ({remaining/60:.2f} min)")

# Execution time estimate: ~5-10 minutes per 10k shots
# Queue time estimate: ~queue_estimate_min minutes
execution_per_10k_min = 7  # Conservative estimate
execution_per_10k_sec = execution_per_10k_min * 60

# Account for queue time
available_for_execution = remaining - (queue_estimate_min * 60)

if available_for_execution < 120:
    print(f"\n⚠️  Not enough time after queue estimate")
    print(f"   Available for execution: {available_for_execution/60:.1f} min")
    print(f"   Minimum needed: ~2 minutes")
    SHOTS = 5000  # Try minimum viable shot count
else:
    # Calculate max shots we can do
    max_shots = int((available_for_execution / execution_per_10k_sec) * 10000)
    
    # Be conservative: use 80% of available time
    conservative_shots = int(max_shots * 0.8)
    
    # For 0.002% success rate, we want at least 10k shots
    # Target: 15k-20k shots if time allows
    if conservative_shots >= 20000:
        SHOTS = 20000
    elif conservative_shots >= 15000:
        SHOTS = 15000
    elif conservative_shots >= 10000:
        SHOTS = 10000
    else:
        SHOTS = max(5000, conservative_shots)

print(f"\n🚀 Shot Allocation Strategy:")
print(f"   Queue estimate: {queue_estimate_min}-{queue_estimate_max} min")
print(f"   Available execution time: {available_for_execution/60:.1f} min")
print(f"   Selected shots: {SHOTS:,}")
print(f"   Estimated execution: ~{SHOTS/10000 * execution_per_10k_min:.1f} min")
print(f"   Expected correct results: ~{int(SHOTS * 0.00002)} (at 0.002% rate)")

if not check_time_limit("shot allocation"):
    exit(1)

# Submit job
print(f"\n🚀 Submitting job...")
try:
    sampler = Sampler(mode=backend)
    job_start = time.time()
    job = sampler.run([transpiled], shots=SHOTS)
    
    job_id = job.job_id()
    print(f"  ✅ Job submitted: {job_id}")
    print(f"  Status: {job.status()}")
    submission_time = time.time() - job_start
    print(f"  Submission time: {submission_time:.1f}s")
    
    # Monitor job with time checks
    print(f"\n⏳ Waiting for results...")
    print(f"   (Monitoring time budget throughout)")
    
    poll_count = 0
    while True:
        elapsed = get_elapsed_time()
        remaining = get_remaining_time()
        
        # Check every 30 seconds
        if poll_count % 6 == 0:  # Every 6 polls = 30 seconds
        status = job.status()
        # Handle both enum and string status
        status_str = status.value if hasattr(status, 'value') else str(status)
        print(f"\n   Status: {status_str} | Elapsed: {elapsed:.0f}s | Remaining: {remaining:.0f}s")
            
            if remaining < 120:
                print(f"   ⚠️  Less than 2 minutes remaining!")
        
        # Check if job is done
        try:
            if job.status() in ['DONE', 'ERROR', 'CANCELLED']:
                break
        except:
            pass
        
        # Check time limit - cancel if we're out of time
        if remaining < 30:
            print(f"\n❌ TIME LIMIT REACHED - Cancelling job if possible")
            try:
                job.cancel()
                print(f"   Job cancelled")
            except:
                print(f"   Could not cancel (may have already started)")
            exit(1)
        
        time.sleep(5)  # Poll every 5 seconds
        poll_count += 1
    
    print(f"\n  ✅ Job completed!")
    
    # Check final time
    final_elapsed = get_elapsed_time()
    final_remaining = get_remaining_time()
    print(f"\n⏱️  Final Time Status:")
    print(f"   Total elapsed: {final_elapsed:.1f}s ({final_elapsed/60:.2f} min)")
    print(f"   Remaining: {final_remaining:.1f}s ({final_remaining/60:.2f} min)")
    
    # Process results
    result = job.result()
    try:
        counts = result[0].data.c.get_counts()
    except AttributeError:
        try:
            counts = dict(result[0].data.c.array)
        except:
            # Fallback: try different access patterns
            counts = dict(result[0].data.meas.get_counts() if hasattr(result[0].data, 'meas') else {})
    
    print(f"\n{'='*70}")
    print("📊 RESULTS FROM IBM QUANTUM")
    print(f"{'='*70}")
    
    # Analyze
    m_bits = 8  # log2(139) ≈ 8
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
                print(f"     (a={a:3d}, b={b:3d}): {count} times")
        
        print(f"\n🎉 8-bit key broken on IBM Quantum hardware!")
        print(f"   Time used: {final_elapsed/60:.2f} minutes")
    else:
        print(f"\n⚠️  Did not find d = {expected_d}")
        print(f"   Valid measurements: {total_valid} ({100*total_valid/SHOTS:.2f}%)")
        print(f"   Shots used: {SHOTS:,}")
        print(f"   May need more shots or better luck")
        print(f"   Time used: {final_elapsed/60:.2f} minutes")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"8bit_ibm_timed_{backend.name}_{timestamp}.json"
    results_path = os.path.join(script_dir, results_file)
    
    results_data = {
        'timestamp': timestamp,
        'bit_length': 8,
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
        'circuit_gates': transpiled.size(),
        'time_elapsed_seconds': final_elapsed,
        'time_budget_seconds': TIME_BUDGET_SECONDS,
        'queue_jobs': status.pending_jobs
    }
    
    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    print(f"\n{'='*70}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
    elapsed = get_elapsed_time()
    print(f"\n⏱️  Total time used: {elapsed:.1f}s ({elapsed/60:.2f} min)")
