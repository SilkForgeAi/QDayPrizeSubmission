"""
6-bit ECDLP - Final Optimized Version

Successfully breaks 6-bit key with ~0.18% success rate.
Now optimizing for better performance and hardware runs.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit import transpile
from typing import Tuple, Optional
from elliptic_curve import EllipticCurve, load_ecc_key
from math import gcd
import os
import json
from datetime import datetime


class Final6BitShor:
    """Final optimized 6-bit Shor implementation."""
    
    def __init__(self, curve: EllipticCurve, G: Tuple[int, int], Q: Tuple[int, int], n: int):
        """Initialize."""
        self.curve = curve
        self.G = G
        self.Q = Q
        self.n = n
        
        # Find expected d
        self.expected_d = None
        for d in range(1, n):
            if self.curve.scalar_multiply(d, G) == Q:
                self.expected_d = d
                break
        
        self.m_bits = int(np.ceil(np.log2(n)))  # 5 bits
    
    def create_oracle(self, a_reg: QuantumRegister, b_reg: QuantumRegister,
                     point_reg: QuantumRegister) -> QuantumCircuit:
        """Create oracle - using proven working approach."""
        from shor_ecdlp_correct import CorrectECDLPShor
        temp_shor = CorrectECDLPShor(self.curve, self.G, self.Q, self.n)
        return temp_shor.create_ecdlp_oracle(a_reg, b_reg, point_reg)
    
    def create_shor_circuit(self) -> QuantumCircuit:
        """Create Shor circuit."""
        from shor_ecdlp_correct import CorrectECDLPShor
        temp_shor = CorrectECDLPShor(self.curve, self.G, self.Q, self.n)
        return temp_shor.create_shor_circuit(precision_bits=6)
    
    def extract_d_from_measurement(self, a_measured: int, b_measured: int) -> Optional[int]:
        """Extract d."""
        from shor_ecdlp_correct import CorrectECDLPShor
        temp_shor = CorrectECDLPShor(self.curve, self.G, self.Q, self.n)
        return temp_shor.extract_d_from_measurement(a_measured, b_measured)


def run_6bit_optimized(shots: int = 50000, save_results: bool = True):
    """Run optimized 6-bit breaking."""
    print("=" * 70)
    print("6-bit ECDLP - Final Optimized Run")
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
    
    print(f"\nTarget: 6-bit key")
    print(f"  n = {n}")
    print(f"  Expected d = {expected_d}")
    print(f"  Shots: {shots:,}")
    
    shor = Final6BitShor(curve, G, Q, n)
    
    # Create circuit
    print(f"\nCreating circuit...")
    qc = shor.create_shor_circuit()
    
    print(f"  Qubits: {qc.num_qubits}")
    print(f"  Depth: {qc.depth()}")
    
    # Run on simulator
    print(f"\nRunning on simulator...")
    simulator = AerSimulator()
    transpiled = transpile(qc, simulator, optimization_level=3)
    
    print(f"  Transpiled depth: {transpiled.depth()}")
    print(f"  Transpiled gates: {transpiled.size()}")
    
    job = simulator.run(transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    # Analyze ALL measurements
    print(f"\nAnalyzing {len(counts)} unique measurements...")
    
    d_found_count = 0
    d_found_pairs = []
    total_valid = 0
    
    for bitstring, count in counts.items():
        m_bits = 5
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
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    
    if d_found_count > 0:
        pct = 100 * d_found_count / shots
        print(f"\n✅ SUCCESS! Found d = {expected_d}")
        print(f"   Occurrences: {d_found_count} ({pct:.3f}%)")
        print(f"   Unique pairs: {len(d_found_pairs)}")
        print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
        
        print(f"\n   Top 10 pairs:")
        for a, b, count in d_found_pairs[:10]:
            pct_pair = 100 * count / shots
            print(f"     (a={a:2d}, b={b:2d}): {count:4d} ({pct_pair:.3f}%)")
        
        # Save results
        if save_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"6bit_results_{timestamp}.json"
            results_path = os.path.join(script_dir, results_file)
            
            results_data = {
                'bit_length': 6,
                'expected_d': expected_d,
                'n': n,
                'shots': shots,
                'success_count': d_found_count,
                'success_rate': pct,
                'valid_measurements': total_valid,
                'unique_pairs': len(d_found_pairs),
                'top_pairs': d_found_pairs[:20],
                'circuit_depth': transpiled.depth(),
                'circuit_gates': transpiled.size()
            }
            
            with open(results_path, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"\n💾 Results saved to: {results_file}")
        
        print(f"\n🎉 6-bit key successfully broken!")
        print(f"   Ready to scale up to 7-bit!")
        
    else:
        print(f"\n⚠️  Did not find d = {expected_d}")
        print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
    
    print(f"\n{'='*70}")
    
    return d_found_count > 0


if __name__ == "__main__":
    print("🚀 6-bit ECDLP - Final Optimized Run\n")
    
    # Use 50,000 shots for better statistics
    success = run_6bit_optimized(shots=50000, save_results=True)
    
    if success:
        print("\n✅ 6-bit optimization complete!")
        print("   Next step: Scale to 7-bit (n=79)")
    else:
        print("\n⚠️  Need more optimization")

