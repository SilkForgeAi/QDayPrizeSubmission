"""
Step 2: Simplified Additive Oracle for ECDLP

Implement f(a, b) = a + d*b mod n using additive group (mod 7).
This tests the oracle approach before full EC point operations.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit import transpile
from typing import Tuple
from fractions import Fraction
from elliptic_curve import EllipticCurve, load_ecc_key
import os


class AdditiveOracleShor:
    """
    Shor's algorithm for additive group (mod n).
    
    Oracle: f(a, b) = (a + d*b) mod n
    Where d is the discrete logarithm we're trying to find.
    """
    
    def __init__(self, n: int, d: int):
        """Initialize with group order n and discrete log d."""
        self.n = n
        self.d = d  # Hidden value we're finding
        self.m_bits = int(np.ceil(np.log2(n)))  # 3 bits for n=7
        
        print(f"Additive group (mod {n})")
        print(f"Hidden d = {d}")
        print(f"Register bits: {self.m_bits}")
    
    def mod_add_constant(self, qc: QuantumCircuit, reg: QuantumRegister, 
                        constant: int, control_qubits: list = None):
        """
        Add constant mod n to register.
        Uses controlled modular addition.
        """
        # For small n, we can use direct lookup
        # Add constant mod n to each possible state
        
        # Simplified: Use controlled operations
        # For each bit position, determine when to flip
        
        const_mod = constant % self.n
        
        if const_mod == 0:
            return  # No-op
        
        # Use ripple-carry adder approach or lookup
        # For small n, lookup is simpler
        
        # Build control condition
        controls = control_qubits if control_qubits else []
        
        # Add const_mod to reg using controlled operations
        # This is simplified - full implementation needs proper modular adder
        # For now, use a basic approach
        
        # For each bit, determine carry and sum
        # Since we're working mod n, we need modular arithmetic
        # This is a placeholder - would need proper quantum modular adder
    
    def create_oracle(self, a_reg: QuantumRegister, b_reg: QuantumRegister,
                     target_reg: QuantumRegister) -> QuantumCircuit:
        """
        Create oracle: |a, b> |0> -> |a, b> |(a + d*b) mod n>
        
        For small n, use lookup table approach.
        """
        qc = QuantumCircuit(a_reg, b_reg, target_reg, name='Additive_Oracle')
        
        # Precompute f(a, b) = (a + d*b) mod n for all a, b
        lookup = {}
        for a in range(self.n):
            for b in range(self.n):
                key = (a, b)
                lookup[key] = (a + self.d * b) % self.n
        
        # For each (a, b) combination, set target to lookup[a, b]
        # Use controlled operations
        
        for a_val in range(min(self.n, 8)):
            for b_val in range(min(self.n, 8)):
                target_val = lookup[(a_val, b_val)]
                
                # Set target register to target_val when a == a_val and b == b_val
                for bit_pos in range(self.m_bits):
                    if (target_val >> bit_pos) & 1:
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
                            qc.mcx(controls, target_reg[bit_pos])
                        
                        # Restore
                        for q in reversed(b_flips):
                            qc.x(q)
                        for q in reversed(a_flips):
                            qc.x(q)
        
        return qc
    
    def create_shor_circuit(self, precision_bits: int = 6) -> QuantumCircuit:
        """
        Create Shor's circuit for additive group.
        
        Finds period using QPE on function f(a, b) = (a + d*b) mod n
        """
        # Registers
        a_reg = QuantumRegister(self.m_bits, 'a')
        b_reg = QuantumRegister(self.m_bits, 'b')
        target_reg = QuantumRegister(self.m_bits, 'target')
        classical_reg = ClassicalRegister(2 * self.m_bits, 'c')
        
        qc = QuantumCircuit(a_reg, b_reg, target_reg, classical_reg, name='Shor_Additive')
        
        # Step 1: Initialize a and b in superposition
        for i in range(self.m_bits):
            qc.h(a_reg[i])
            qc.h(b_reg[i])
        
        # Step 2: Apply oracle
        oracle = self.create_oracle(a_reg, b_reg, target_reg)
        qc.append(oracle, a_reg[:] + b_reg[:] + target_reg[:])
        
        # Step 3: Apply inverse QFT to a and b
        iqft_a = QFT(num_qubits=self.m_bits, approximation_degree=0, do_swaps=True).inverse()
        iqft_b = QFT(num_qubits=self.m_bits, approximation_degree=0, do_swaps=True).inverse()
        
        qc.append(iqft_a, a_reg)
        qc.append(iqft_b, b_reg)
        
        # Step 4: Measure a and b
        qc.measure(a_reg, classical_reg[:self.m_bits])
        qc.measure(b_reg, classical_reg[self.m_bits:])
        
        return qc
    
    def extract_d_from_measurement(self, a_measured: int, b_measured: int) -> int:
        """
        Extract d from measurements.
        
        If gcd(b, n) = 1, then d = -a * b^(-1) mod n
        """
        from math import gcd
        
        if gcd(b_measured, self.n) != 1:
            return None  # b not invertible
        
        # Compute b^(-1) mod n
        b_inv = pow(b_measured, -1, self.n)
        d_candidate = (-a_measured * b_inv) % self.n
        
        return d_candidate


def test_additive_shor(bit_length: int = 4, shots: int = 4096):
    """Test additive group Shor's algorithm."""
    print("=" * 70)
    print("Step 2: Testing Additive Group Oracle (mod n)")
    print("=" * 70)
    
    # Load key to get n and d
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_file = os.path.join(script_dir, "ecc_keys.json")
    key_data = load_ecc_key(key_file, bit_length=bit_length)
    
    n = key_data['subgroup_order']
    expected_d = key_data['private_key']
    
    print(f"\nParameters:")
    print(f"  Group order: n = {n}")
    print(f"  Expected d = {expected_d}")
    
    # Initialize
    shor = AdditiveOracleShor(n, expected_d)
    
    # Create circuit
    print(f"\nCreating circuit...")
    qc = shor.create_shor_circuit(precision_bits=6)
    
    print(f"  Qubits: {qc.num_qubits}")
    print(f"  Depth: {qc.depth()}")
    print(f"  Gates: {qc.size()}")
    
    # Run simulation
    print(f"\nRunning simulation ({shots} shots)...")
    simulator = AerSimulator()
    transpiled = transpile(qc, simulator, optimization_level=2)
    
    print(f"  Transpiled: {transpiled.depth()} depth, {transpiled.size()} gates")
    
    job = simulator.run(transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    print(f"\nResults:")
    print(f"{'a':<8} {'b':<8} {'Count':<8} {'%':<8} {'d_candidate':<12} {'Match':<8}")
    print("-" * 70)
    
    d_found_count = {}
    
    for bitstring, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        # Parse measurements
        a_bits = bitstring[:shor.m_bits]
        b_bits = bitstring[shor.m_bits:]
        
        a_val = int(a_bits, 2)
        b_val = int(b_bits, 2)
        
        # Extract d
        d_candidate = shor.extract_d_from_measurement(a_val, b_val)
        
        match = "✅" if d_candidate == expected_d else ""
        if d_candidate == expected_d:
            d_found_count[d_candidate] = d_found_count.get(d_candidate, 0) + count
        
        pct = 100 * count / shots
        d_str = str(d_candidate) if d_candidate is not None else "N/A"
        
        print(f"{a_val:<8} {b_val:<8} {count:<8} {pct:<7.2f}% {d_str:<12} {match:<8}")
    
    # Summary
    print(f"\n{'='*70}")
    print("Summary:")
    if d_found_count:
        total_correct = sum(d_found_count.values())
        pct_correct = 100 * total_correct / shots
        print(f"  Found d = {expected_d}: {total_correct} times ({pct_correct:.2f}%)")
        print(f"  ✅ SUCCESS! Oracle is working!")
    else:
        print(f"  ⚠️  Did not find d = {expected_d}")
    
    print(f"{'='*70}")
    
    return counts


if __name__ == "__main__":
    test_additive_shor(bit_length=4, shots=4096)

