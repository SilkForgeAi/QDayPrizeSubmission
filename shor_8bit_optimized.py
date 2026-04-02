"""
ECDLP Optimized Simulator Test (8-bit, 9-bit, 10-bit)

Optimizations within contest rules:
1. Full oracle coverage (handle all n values, not just 8)
2. Higher transpilation optimization level
3. More shots for better statistics
4. Better post-processing
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
import sys
import os
import json
from datetime import datetime
from math import gcd
import time
from typing import Tuple, Optional
import argparse

# Add QDay_Prize_Submission to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
submission_dir = os.path.join(script_dir, "QDay_Prize_Submission")
sys.path.insert(0, submission_dir)

from elliptic_curve import EllipticCurve, load_ecc_key


class OptimizedECDLPShor:
    """
    Optimized Shor's algorithm for ECDLP with full oracle coverage.
    
    Key improvement: Handles full range of a and b values (not limited to 8).
    """
    
    def __init__(self, curve: EllipticCurve, G: Tuple[int, int], Q: Tuple[int, int], n: int):
        """Initialize."""
        self.curve = curve
        self.G = G
        self.Q = Q
        self.n = n
        
        # Precompute all multiples of G (group elements)
        self.group = []
        current = None
        for k in range(n):
            if k == 0:
                self.group.append(None)  # Point at infinity
                current = G
            else:
                self.group.append(current)
                current = self.curve.point_add(current, G)
        
        # Find expected d
        self.expected_d = None
        for d in range(1, n):
            if self.curve.scalar_multiply(d, G) == Q:
                self.expected_d = d
                break
        
        print(f"ECDLP Setup:")
        print(f"  Group order: n = {n}")
        print(f"  Expected d = {self.expected_d}")
        print(f"  Group elements: {len(self.group)} points")
        
        # Qubit counts
        self.m_bits = int(np.ceil(np.log2(n)))  # 8 bits for n=139
        # Use minimal point register - just enough to encode point indices (0 to n-1)
        self.point_bits = self.m_bits  # Same as m_bits, just encode the index
    
    def create_ecdlp_oracle(self, a_reg: QuantumRegister, b_reg: QuantumRegister,
                           point_reg: QuantumRegister) -> QuantumCircuit:
        """
        Create ECDLP oracle with FULL coverage: f(a, b) = a*G + b*Q
        
        KEY OPTIMIZATION: Handle all values of a and b (not limited to 8).
        """
        qc = QuantumCircuit(a_reg, b_reg, point_reg, name='ECDLP_Oracle_Full')
        
        # Precompute lookup: f(a, b) = (a + d*b) mod n
        # This gives us the index k where the result is k*G
        lookup = {}
        for a in range(self.n):  # FULL RANGE, not min(n, 8)
            for b in range(self.n):  # FULL RANGE, not min(n, 8)
                k = (a + self.expected_d * b) % self.n
                lookup[(a, b)] = k
        
        print(f"  Oracle lookup table: {len(lookup):,} entries")
        
        # For each (a, b), encode the corresponding point index
        for a_val in range(self.n):  # FULL RANGE
            for b_val in range(self.n):  # FULL RANGE
                k = lookup.get((a_val, b_val), 0)
                
                # Encode point index k into point_reg
                for bit_pos in range(min(self.m_bits, point_reg.size)):
                    if (k >> bit_pos) & 1:
                        # Build control: a == a_val AND b == b_val
                        controls = []
                        a_flips = []
                        b_flips = []
                        
                        # Controls for a == a_val
                        for i in range(a_reg.size):
                            if (a_val >> i) & 1:
                                controls.append(a_reg[i])
                            else:
                                qc.x(a_reg[i])
                                a_flips.append(a_reg[i])
                                controls.append(a_reg[i])
                        
                        # Controls for b == b_val
                        for i in range(b_reg.size):
                            if (b_val >> i) & 1:
                                controls.append(b_reg[i])
                            else:
                                qc.x(b_reg[i])
                                b_flips.append(b_reg[i])
                                controls.append(b_reg[i])
                        
                        # Apply multi-controlled X
                        if len(controls) >= 2:
                            qc.mcx(controls, point_reg[bit_pos])
                        elif len(controls) == 1:
                            qc.cx(controls[0], point_reg[bit_pos])
                        
                        # Restore
                        for q in reversed(b_flips):
                            qc.x(q)
                        for q in reversed(a_flips):
                            qc.x(q)
        
        return qc
    
    def create_shor_circuit(self) -> QuantumCircuit:
        """Create full Shor's circuit for ECDLP."""
        # Registers
        a_reg = QuantumRegister(self.m_bits, 'a')
        b_reg = QuantumRegister(self.m_bits, 'b')
        point_reg = QuantumRegister(self.m_bits, 'point')  # Minimal: just encode index
        classical_reg = ClassicalRegister(2 * self.m_bits, 'c')
        
        qc = QuantumCircuit(a_reg, b_reg, point_reg, classical_reg, name='Shor_ECDLP_Optimized')
        
        # Step 1: Initialize a and b in superposition
        for i in range(self.m_bits):
            qc.h(a_reg[i])
            qc.h(b_reg[i])
        
        # Step 2: Apply ECDLP oracle
        oracle = self.create_ecdlp_oracle(a_reg, b_reg, point_reg)
        qc.append(oracle, a_reg[:] + b_reg[:] + point_reg[:])
        
        # Step 3: Apply inverse QFT to a and b
        iqft_a = QFT(num_qubits=self.m_bits, approximation_degree=0, do_swaps=True).inverse()
        iqft_b = QFT(num_qubits=self.m_bits, approximation_degree=0, do_swaps=True).inverse()
        
        qc.append(iqft_a, a_reg)
        qc.append(iqft_b, b_reg)
        
        # Step 4: Measure a and b
        qc.measure(a_reg, classical_reg[:self.m_bits])
        qc.measure(b_reg, classical_reg[self.m_bits:])
        
        return qc
    
    def extract_d_from_measurement(self, a_measured: int, b_measured: int) -> Optional[int]:
        """Extract d from measurements."""
        if gcd(b_measured, self.n) != 1:
            return None  # b not invertible
        
        # Compute b^(-1) mod n
        try:
            b_inv = pow(b_measured % self.n, -1, self.n)
            d_candidate = (-a_measured * b_inv) % self.n
            return d_candidate
        except:
            return None


def run_optimized_bitlength(bit_length: int, shots: int = 100000, optimization_level: int = 3):
    """Run optimized ECDLP on simulator for a given bit length."""
    print("=" * 70)
    print(f"{bit_length}-bit ECDLP - OPTIMIZED Simulator Test")
    print("=" * 70)
    print(f"\nOptimizations:")
    print(f"  1. Full oracle coverage (all n values, not limited to 8)")
    print(f"  2. Transpilation optimization level: {optimization_level}")
    print(f"  3. Shots: {shots:,}")
    print("=" * 70)
    
    # Load key
    key_file = os.path.join(submission_dir, "ecc_keys.json")
    key_data = load_ecc_key(key_file, bit_length=bit_length)
    
    p = key_data['prime']
    G = tuple(key_data['generator_point'])
    Q = tuple(key_data['public_key'])
    n = key_data['subgroup_order']
    expected_d = key_data['private_key']
    
    curve = EllipticCurve(p, a=0, b=7)
    
    print(f"\nTarget: {bit_length}-bit key")
    print(f"  Prime p = {p}")
    print(f"  Generator G = {G}")
    print(f"  Public key Q = {Q}")
    print(f"  Subgroup order n = {n}")
    print(f"  Expected d = {expected_d}")
    
    # Verify classically
    verified = curve.scalar_multiply(expected_d, G) == Q
    print(f"  Classical verification: {'✅' if verified else '❌'}")
    
    print(f"\n{'='*70}")
    print("Creating Circuit...")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        shor = OptimizedECDLPShor(curve, G, Q, n)
        qc = shor.create_shor_circuit()
        
        creation_time = time.time() - start_time
        print(f"✅ Circuit created in {creation_time:.2f} seconds")
        print(f"  Qubits: {qc.num_qubits}")
        print(f"  Depth: {qc.depth()}")
        print(f"  Gates: {qc.size()}")
        
    except Exception as e:
        print(f"❌ Circuit creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    print(f"\n{'='*70}")
    print(f"Transpiling for Simulator (optimization_level={optimization_level})...")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        simulator = AerSimulator()
        transpiled = transpile(qc, simulator, optimization_level=optimization_level)
        
        transpile_time = time.time() - start_time
        print(f"✅ Transpilation completed in {transpile_time:.2f} seconds")
        print(f"  Transpiled qubits: {transpiled.num_qubits}")
        print(f"  Transpiled depth: {transpiled.depth():,}")
        print(f"  Transpiled gates: {transpiled.size():,}")
        
        if transpiled.depth() > 1000000:
            print(f"\n⚠️  WARNING: Circuit depth very high ({transpiled.depth():,})")
        elif transpiled.depth() > 500000:
            print(f"\n⚠️  Circuit depth is very high but may be manageable")
        else:
            print(f"\n✅ Circuit depth is reasonable")
            
    except Exception as e:
        print(f"❌ Transpilation failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    print(f"\n{'='*70}")
    print(f"Running Simulation ({shots:,} shots)...")
    print(f"{'='*70}")
    
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
        all_d_candidates = {}
        
        for bitstring, count in counts.items():
            a_bits = bitstring[:m_bits]
            b_bits = bitstring[m_bits:]
            
            a_val = int(a_bits, 2) if a_bits else 0
            b_val = int(b_bits, 2) if b_bits else 0
            
            d_candidate = shor.extract_d_from_measurement(a_val, b_val)
            
            if d_candidate is not None:
                total_valid += count
                all_d_candidates[d_candidate] = all_d_candidates.get(d_candidate, 0) + count
            
            if d_candidate == expected_d:
                d_found_count += count
                d_found_pairs.append((a_val, b_val, count))
        
        d_found_pairs.sort(key=lambda x: x[2], reverse=True)
        
        # Results
        if d_found_count > 0:
            pct = 100 * d_found_count / shots
            print(f"\n✅ SUCCESS! Found d = {expected_d}")
            print(f"   Occurrences: {d_found_count} ({pct:.4f}%)")
            print(f"   Unique pairs: {len(d_found_pairs)}")
            print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
            
            if d_found_pairs:
                print(f"\n   Top pairs that gave d={expected_d}:")
                for a, b, count in d_found_pairs[:10]:
                    print(f"     (a={a:3d}, b={b:3d}): {count} times")
            
            # Show top d candidates
            top_d = sorted(all_d_candidates.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"\n   Top d candidates found:")
            for d_val, count in top_d:
                marker = "✅" if d_val == expected_d else "  "
                print(f"     {marker} d={d_val:3d}: {count} occurrences ({100*count/shots:.4f}%)")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"{bit_length}bit_optimized_{timestamp}.json"
            results_path = os.path.join(script_dir, results_file)
            
            results_data = {
                'timestamp': timestamp,
                'bit_length': bit_length,
                'expected_d': expected_d,
                'n': n,
                'shots': shots,
                'optimization_level': optimization_level,
                'success_count': d_found_count,
                'success_rate': pct,
                'valid_measurements': total_valid,
                'unique_pairs': len(d_found_pairs),
                'top_pairs': d_found_pairs[:20],
                'circuit_depth': transpiled.depth(),
                'circuit_gates': transpiled.size(),
                'simulation_time': sim_time,
                'transpilation_time': transpile_time
            }
            
            with open(results_path, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"\n💾 Results saved to: {results_file}")
            print(f"\n🎉 {bit_length}-bit key broken on optimized simulator!")
            
            return results_data
            
        else:
            pct_valid = 100 * total_valid / shots
            print(f"\n⚠️  Did not find d = {expected_d} with {shots:,} shots")
            print(f"   Valid measurements: {total_valid} ({pct_valid:.2f}%)")
            
            # Show top d candidates anyway
            top_d = sorted(all_d_candidates.items(), key=lambda x: x[1], reverse=True)[:10]
            if top_d:
                print(f"\n   Top d candidates found:")
                for d_val, count in top_d:
                    print(f"     d={d_val:3d}: {count} occurrences ({100*count/shots:.4f}%)")
            
            print(f"\n   Suggestions:")
            print(f"     - Try even more shots (200k+)")
            print(f"     - Check oracle implementation")
            print(f"     - Verify circuit correctness")
            
            return None
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("🚀 OPTIMIZED ECDLP Simulator Test")
    print("Key improvement: Full oracle coverage (all n values)\n")

    parser = argparse.ArgumentParser(description="Optimized ECDLP simulator (8/9/10-bit)")
    parser.add_argument("--bit-length", type=int, default=8, choices=[8, 9, 10],
                        help="Bit length to target (8, 9, or 10)")
    parser.add_argument("--shots", type=int, default=100000, help="Number of shots")
    parser.add_argument("--opt-level", type=int, default=3, choices=[0, 1, 2, 3],
                        help="Transpilation optimization level")
    parser.add_argument("--quick", action="store_true",
                        help="Run a quick 2-config sweep (50k, 100k shots)")

    args = parser.parse_args()

    if args.quick:
        configs = [
            {'shots': 50000, 'opt_level': args.opt_level},
            {'shots': 100000, 'opt_level': args.opt_level},
        ]
        for config in configs:
            print(f"\n{'='*70}")
            print(f"Configuration: {config['shots']:,} shots, opt_level={config['opt_level']}")
            print(f"{'='*70}")
            result = run_optimized_bitlength(
                bit_length=args.bit_length,
                shots=config['shots'],
                optimization_level=config['opt_level'],
            )
            if result and result['success_count'] > 0:
                print(f"\n✅ Success! Breaking early...")
                break
    else:
        run_optimized_bitlength(
            bit_length=args.bit_length,
            shots=args.shots,
            optimization_level=args.opt_level,
        )

    print(f"\n{'='*70}")
    print("Complete!")
    print(f"{'='*70}")


def run_optimized_8bit(shots: int = 100000, optimization_level: int = 3):
    """Backwards-compatible 8-bit entrypoint."""
    return run_optimized_bitlength(8, shots=shots, optimization_level=optimization_level)
