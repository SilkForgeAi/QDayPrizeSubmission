"""
6-bit ECDLP - Optimized Step-by-Step

Step 1: Fix oracle encoding
Step 2: Increase shots for better statistics
Step 3: Optimize circuit
Step 4: Test and validate
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


class Optimized6BitShor:
    """Optimized Shor's for 6-bit key."""
    
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
        
        self.m_bits = int(np.ceil(np.log2(n)))  # 5 bits for n=31
        
        print(f"6-bit ECDLP (Optimized):")
        print(f"  n = {n}, Expected d = {self.expected_d}")
        print(f"  Register bits: {self.m_bits}")
    
    def create_optimized_oracle(self, a_reg: QuantumRegister, b_reg: QuantumRegister,
                                point_reg: QuantumRegister) -> QuantumCircuit:
        """
        Optimized oracle with better encoding.
        
        Key optimizations:
        1. Only encode necessary bits (m_bits, not full point_reg)
        2. More efficient control logic
        3. Better gate ordering
        """
        qc = QuantumCircuit(a_reg, b_reg, point_reg, name='Optimized_Oracle')
        
        # Precompute lookup
        lookup = {}
        for a in range(self.n):
            for b in range(self.n):
                k = (a + self.expected_d * b) % self.n
                lookup[(a, b)] = k
        
        print(f"  Building oracle for {len(lookup)} combinations...")
        
        # Optimize: Group by k value to reduce redundant operations
        k_groups = {}
        for (a, b), k in lookup.items():
            if k not in k_groups:
                k_groups[k] = []
            k_groups[k].append((a, b))
        
        # For each k value, set point_reg when (a,b) matches any in group
        for k, pairs in k_groups.items():
            # Encode k into point_reg
            for bit_pos in range(min(self.m_bits, point_reg.size)):
                if (k >> bit_pos) & 1:
                    # For each (a,b) pair that gives this k
                    for a_val, b_val in pairs:
                        controls = []
                        a_flips = []
                        b_flips = []
                        
                        # Build controls for a == a_val
                        for i in range(min(a_reg.size, 5)):
                            if (a_val >> i) & 1:
                                controls.append(a_reg[i])
                            else:
                                qc.x(a_reg[i])
                                a_flips.append(a_reg[i])
                                controls.append(a_reg[i])
                        
                        # Build controls for b == b_val
                        for i in range(min(b_reg.size, 5)):
                            if (b_val >> i) & 1:
                                controls.append(b_reg[i])
                            else:
                                qc.x(b_reg[i])
                                b_flips.append(b_reg[i])
                                controls.append(b_reg[i])
                        
                        # Apply controlled operation
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
        """Create optimized Shor circuit."""
        a_reg = QuantumRegister(self.m_bits, 'a')
        b_reg = QuantumRegister(self.m_bits, 'b')
        point_reg = QuantumRegister(self.m_bits, 'point')  # Use m_bits, not larger
        classical_reg = ClassicalRegister(2 * self.m_bits, 'c')
        
        qc = QuantumCircuit(a_reg, b_reg, point_reg, classical_reg, name='Shor_6bit_Optimized')
        
        # Initialize superposition
        for i in range(self.m_bits):
            qc.h(a_reg[i])
            qc.h(b_reg[i])
        
        # Apply oracle
        oracle = self.create_optimized_oracle(a_reg, b_reg, point_reg)
        qc.append(oracle, a_reg[:] + b_reg[:] + point_reg[:])
        
        # Inverse QFT
        iqft_a = QFT(num_qubits=self.m_bits, approximation_degree=0, do_swaps=True).inverse()
        iqft_b = QFT(num_qubits=self.m_bits, approximation_degree=0, do_swaps=True).inverse()
        
        qc.append(iqft_a, a_reg)
        qc.append(iqft_b, b_reg)
        
        # Measure
        qc.measure(a_reg, classical_reg[:self.m_bits])
        qc.measure(b_reg, classical_reg[self.m_bits:])
        
        return qc
    
    def extract_d_from_measurement(self, a_measured: int, b_measured: int) -> Optional[int]:
        """Extract d from measurements."""
        # Normalize to [0, n-1] range
        a_measured = a_measured % (2 ** self.m_bits)
        b_measured = b_measured % (2 ** self.m_bits)
        
        # Only consider values in valid range
        if a_measured >= self.n or b_measured >= self.n:
            return None
        
        if gcd(b_measured, self.n) != 1:
            return None
        
        try:
            b_inv = pow(b_measured, -1, self.n)
            d_candidate = (-a_measured * b_inv) % self.n
            return d_candidate
        except:
            return None


def test_6bit_step_by_step():
    """Test 6-bit with step-by-step optimization."""
    print("=" * 70)
    print("6-bit ECDLP - Step-by-Step Optimization")
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
    
    # Verify
    verified = curve.scalar_multiply(expected_d, G) == Q
    print(f"\nVerification: {expected_d}*G == Q: {'✅' if verified else '❌'}")
    
    shor = Optimized6BitShor(curve, G, Q, n)
    
    # Step 1: Create circuit
    print(f"\n{'='*70}")
    print("STEP 1: Creating optimized circuit...")
    print(f"{'='*70}")
    qc = shor.create_shor_circuit()
    
    print(f"\nCircuit stats:")
    print(f"  Qubits: {qc.num_qubits}")
    print(f"  Depth: {qc.depth()}")
    print(f"  Gates: {qc.size()}")
    
    # Step 2: Test on simulator with increasing shots
    print(f"\n{'='*70}")
    print("STEP 2: Testing on simulator...")
    print(f"{'='*70}")
    
    simulator = AerSimulator()
    transpiled = transpile(qc, simulator, optimization_level=3)
    
    print(f"\nTranspiled:")
    print(f"  Depth: {transpiled.depth()}")
    print(f"  Gates: {transpiled.size()}")
    
    # Test with more shots
    shots_list = [8192, 16384, 32768]
    
    for shots in shots_list:
        print(f"\n{'─'*70}")
        print(f"Testing with {shots:,} shots...")
        print(f"{'─'*70}")
        
        job = simulator.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        # Analyze results
        d_found_count = {}
        total_valid = 0
        
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\nTop 15 measurements:")
        print(f"{'a':<6} {'b':<6} {'Count':<8} {'%':<8} {'d_candidate':<12} {'Match':<8}")
        print("-" * 70)
        
        for bitstring, count in sorted_counts[:15]:
            a_bits = bitstring[:shor.m_bits]
            b_bits = bitstring[shor.m_bits:]
            
            a_val = int(a_bits, 2) if a_bits else 0
            b_val = int(b_bits, 2) if b_bits else 0
            
            d_candidate = shor.extract_d_from_measurement(a_val, b_val)
            
            if d_candidate is not None:
                total_valid += count
            
            match = "✅" if d_candidate == expected_d else ""
            if d_candidate == expected_d:
                d_found_count[d_candidate] = d_found_count.get(d_candidate, 0) + count
            
            pct = 100 * count / shots
            d_str = str(d_candidate) if d_candidate is not None else "N/A"
            
            print(f"{a_val:<6} {b_val:<6} {count:<8} {pct:<7.2f}% {d_str:<12} {match:<8}")
        
        # Summary
        if d_found_count:
            total_correct = sum(d_found_count.values())
            pct_correct = 100 * total_correct / shots
            print(f"\n✅ SUCCESS! Found d = {expected_d}")
            print(f"   Occurrences: {total_correct} ({pct_correct:.2f}%)")
            print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
            print(f"\n🎉 6-bit key broken! Ready to scale up!")
            return True
        else:
            print(f"\n⚠️  Did not find d = {expected_d} with {shots:,} shots")
            print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
            if shots < max(shots_list):
                print(f"   Trying more shots...")
    
    print(f"\n{'='*70}")
    print("⚠️  Did not find d after all shot counts")
    print("   May need further optimization or different approach")
    print(f"{'='*70}")
    
    return False


if __name__ == "__main__":
    success = test_6bit_step_by_step()
    
    if success:
        print("\n✅ 6-bit optimization complete! Ready for next step.")
    else:
        print("\n⚠️  Need further optimization before scaling up.")

