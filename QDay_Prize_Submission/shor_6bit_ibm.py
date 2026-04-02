"""
6-bit ECDLP on IBM Quantum Hardware

Tests multiple backends to find best performance.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFT
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from typing import Tuple, Optional
from elliptic_curve import EllipticCurve, load_ecc_key
from math import gcd
import os
import json
from datetime import datetime
from shor_ecdlp_correct import CorrectECDLPShor


def run_6bit_on_ibm(backend_name: str = None, shots: int = 20000, 
                    save_results: bool = True):
    """
    Run 6-bit ECDLP on IBM Quantum hardware.
    
    Args:
        backend_name: Specific backend (None = best available)
        shots: Number of shots (20k recommended for 0.19% success)
        save_results: Save results to file
    """
    print("=" * 70)
    print("6-bit ECDLP on IBM Quantum Hardware")
    print("=" * 70)
    
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
    
    print(f"\nTarget: 6-bit key (n={n}, d={expected_d})")
    print(f"Shots: {shots:,}")
    print(f"Expected success rate: ~0.19% ({int(shots*0.0019)} expected correct)")
    
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
        return None
    
    # Select backend
    if backend_name:
        try:
            backend = service.backend(backend_name)
            print(f"  Using specified backend: {backend_name}")
        except:
            print(f"  ⚠️  {backend_name} not available, finding best...")
            backend = service.least_busy(min_num_qubits=qc.num_qubits, operational=True)
    else:
        # Find best backend
        print(f"  Finding best backend (≥{qc.num_qubits} qubits)...")
        
        # Try preferred backends first
        preferred = ['ibm_sherbrooke', 'ibm_kyiv', 'ibm_torino', 'ibm_brisbane']
        backend = None
        
        for name in preferred:
            try:
                candidate = service.backend(name)
                if candidate.status().operational:
                    backend = candidate
                    print(f"  ✅ Found: {name}")
                    break
            except:
                continue
        
        if not backend:
            backend = service.least_busy(min_num_qubits=qc.num_qubits, operational=True)
            print(f"  Using least busy: {backend.name}")
    
    status = backend.status()
    print(f"\nBackend: {backend.name}")
    print(f"  Qubits: {backend.num_qubits}")
    print(f"  Status: {status.status_msg}")
    print(f"  Queue: {status.pending_jobs} jobs")
    
    # Transpile
    print(f"\n⚙️  Transpiling for {backend.name}...")
    transpiled = transpile(qc, backend, optimization_level=3)
    
    print(f"  Transpiled qubits: {transpiled.num_qubits}")
    print(f"  Transpiled depth: {transpiled.depth()}")
    print(f"  Transpiled gates: {transpiled.size()}")
    
    # Run
    print(f"\n🚀 Submitting job...")
    print(f"   Estimated time: ~{shots//2000 * 2-3} minutes")
    
    try:
        sampler = Sampler(mode=backend)
        job = sampler.run([transpiled], shots=shots)
        
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
        m_bits = 5
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
            
            pct = 100 * count / shots
            d_str = str(d_candidate) if d_candidate is not None else "N/A"
            
            print(f"{a_val:<6} {b_val:<6} {count:<8} {pct:<7.2f}% {d_str:<12} {match:<8}")
        
        # Summary
        print(f"\n{'='*70}")
        print("🎯 SUMMARY")
        print(f"{'='*70}")
        
        if d_found_count > 0:
            pct = 100 * d_found_count / shots
            print(f"\n✅ SUCCESS! Found d = {expected_d}")
            print(f"   Occurrences: {d_found_count} ({pct:.3f}%)")
            print(f"   Unique pairs: {len(d_found_pairs)}")
            print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
            print(f"\n   Top pairs:")
            for a, b, count in d_found_pairs[:10]:
                print(f"     (a={a:2d}, b={b:2d}): {count} times")
            
            print(f"\n🎉 6-bit key broken on {backend.name}!")
        else:
            print(f"\n⚠️  Did not find d = {expected_d}")
            print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
            print(f"   May need more shots (current: {shots:,})")
        
        # Save results
        if save_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"6bit_ibm_{backend.name}_{timestamp}.json"
            results_path = os.path.join(script_dir, results_file)
            
            results_data = {
                'timestamp': timestamp,
                'bit_length': 6,
                'expected_d': expected_d,
                'n': n,
                'backend': backend.name,
                'job_id': job_id,
                'shots': shots,
                'success_count': d_found_count,
                'success_rate': 100 * d_found_count / shots if shots > 0 else 0,
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
        
        return {
            'backend': backend.name,
            'job_id': job_id,
            'success': d_found_count > 0,
            'success_count': d_found_count,
            'success_rate': 100 * d_found_count / shots if shots > 0 else 0
        }
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import sys
    
    # Configuration
    BACKEND = None  # None = auto-select, or specify: "ibm_sherbrooke", "ibm_kyiv", etc.
    SHOTS = 20000   # 20k shots: expect ~38 correct results (0.19% success)
    
    # Can specify backend from command line
    if len(sys.argv) > 1:
        BACKEND = sys.argv[1]
    
    if len(sys.argv) > 2:
        SHOTS = int(sys.argv[2])
    
    print("🚀 6-bit ECDLP on IBM Quantum")
    print(f"Backend: {BACKEND if BACKEND else 'Auto-select (best available)'}")
    print(f"Shots: {SHOTS:,}\n")
    
    result = run_6bit_on_ibm(backend_name=BACKEND, shots=SHOTS)
    
    if result and result['success']:
        print("\n✅ SUCCESS! 6-bit key broken on IBM Quantum!")
    elif result:
        print("\n⚠️  Job completed but did not find d (may need more shots)")

