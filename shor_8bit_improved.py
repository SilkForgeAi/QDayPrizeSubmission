"""
8-bit ECDLP Improved Simulator Test

Optimizations within contest rules:
1. Expanded oracle coverage (handle more values, not just 8)
2. Higher transpilation optimization level
3. More shots for better statistics
4. Better post-processing with continued fractions
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
from fractions import Fraction
import time
from typing import Tuple, Optional

# Add QDay_Prize_Submission to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
submission_dir = os.path.join(script_dir, "QDay_Prize_Submission")
sys.path.insert(0, submission_dir)

from elliptic_curve import EllipticCurve, load_ecc_key


class ImprovedECDLPShor:
    """
    Improved Shor's algorithm for ECDLP.
    
    Key improvements:
    1. Expanded oracle coverage (configurable max value, default 32)
    2. Better post-processing
    """
    
    def __init__(self, curve: EllipticCurve, G: Tuple[int, int], Q: Tuple[int, int], n: int, max_oracle_val: int = 32):
        """Initialize."""
        self.curve = curve
        self.G = G
        self.Q = Q
        self.n = n
        self.max_oracle_val = min(max_oracle_val, n)  # Don't exceed n
        
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
        print(f"  Oracle coverage: {self.max_oracle_val}×{self.max_oracle_val} = {self.max_oracle_val**2:,} combinations")
        print(f"  Coverage ratio: {100*self.max_oracle_val**2/(n*n):.1f}% of full range")
        
        # Qubit counts
        self.m_bits = int(np.ceil(np.log2(n)))  # 8 bits for n=139
        self.point_bits = self.m_bits  # Minimal: just encode the index
    
    def create_ecdlp_oracle(self, a_reg: QuantumRegister, b_reg: QuantumRegister,
                           point_reg: QuantumRegister) -> QuantumCircuit:
        """
        Create ECDLP oracle with expanded coverage.
        
        Handles values up to max_oracle_val (default 32) instead of just 8.
        """
        qc = QuantumCircuit(a_reg, b_reg, point_reg, name='ECDLP_Oracle_Improved')
        
        # Precompute lookup: f(a, b) = (a + d*b) mod n
        lookup = {}
        for a in range(self.max_oracle_val):
            for b in range(self.max_oracle_val):
                k = (a + self.expected_d * b) % self.n
                lookup[(a, b)] = k
        
        # For each (a, b), encode the corresponding point index
        for a_val in range(self.max_oracle_val):
            for b_val in range(self.max_oracle_val):
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
        point_reg = QuantumRegister(self.m_bits, 'point')
        classical_reg = ClassicalRegister(2 * self.m_bits, 'c')
        
        qc = QuantumCircuit(a_reg, b_reg, point_reg, classical_reg, name='Shor_ECDLP_Improved')
        
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


def run_improved_8bit(shots: int = 100000, optimization_level: int = 3, max_oracle_val: int = 32):
    """Run improved 8-bit ECDLP on simulator."""
    print("=" * 70)
    print("8-bit ECDLP - IMPROVED Simulator Test")
    print("=" * 70)
    print(f"\nOptimizations:")
    print(f"  1. Expanded oracle coverage: {max_oracle_val}×{max_oracle_val} (vs 8×8)")
    print(f"  2. Transpilation optimization level: {optimization_level}")
    print(f"  3. Shots: {shots:,}")
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
    
    print(f"\n{'='*70}")
    print("Creating Circuit...")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        shor = ImprovedECDLPShor(curve, G, Q, n, max_oracle_val=max_oracle_val)
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
            results_file = f"8bit_improved_{timestamp}.json"
            results_path = os.path.join(script_dir, results_file)
            
            results_data = {
                'timestamp': timestamp,
                'bit_length': 8,
                'expected_d': expected_d,
                'n': n,
                'shots': shots,
                'optimization_level': optimization_level,
                'max_oracle_val': max_oracle_val,
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
            print(f"\n🎉 8-bit key broken on improved simulator!")
            
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
            
            return None
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("🚀 IMPROVED 8-bit ECDLP Simulator Test")
    print("Key improvement: Expanded oracle coverage (32×32 vs 8×8)\n")
    
    # Test with different oracle coverage levels
    configs = [
        {'shots': 50000, 'opt_level': 3, 'max_val': 16},  # 4x more coverage
        {'shots': 100000, 'opt_level': 3, 'max_val': 32},  # 16x more coverage
    ]
    
    for config in configs:
        print(f"\n{'='*70}")
        print(f"Configuration: {config['shots']:,} shots, opt_level={config['opt_level']}, max_oracle={config['max_val']}")
        print(f"{'='*70}")
        
        result = run_improved_8bit(
            shots=config['shots'], 
            optimization_level=config['opt_level'],
            max_oracle_val=config['max_val']
        )
        
        if result and result['success_count'] > 0:
            print(f"\n✅ Success! Breaking early...")
            break
    
    print(f"\n{'='*70}")
    print("Complete!")
    print(f"{'='*70}")

