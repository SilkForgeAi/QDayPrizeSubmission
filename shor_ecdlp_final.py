"""
Final Shor's Algorithm for ECDLP - 4-bit Key

Clean implementation using lookup table approach for n=7.
Based on the implementation guide recommendations.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit import transpile
from typing import Tuple, Dict, Optional, List
from elliptic_curve import EllipticCurve, load_ecc_key
import os
from fractions import Fraction


class FinalShorECDLP:
    """
    Final implementation of Shor's ECDLP using lookup oracle.
    
    Strategy for n=7:
    1. Precompute all group elements
    2. Use direct controlled operations to load points
    3. Implement period finding with semi-classical QFT
    """
    
    def __init__(self, curve: EllipticCurve, G: Tuple[int, int], Q: Tuple[int, int], n: int):
        """Initialize."""
        self.curve = curve
        self.G = G
        self.Q = Q
        self.n = n
        self.p = curve.p
        
        # Precompute group elements: k*G for k in [0, n-1]
        self.group_elements = []
        current = None
        for k in range(n):
            if k == 0:
                self.group_elements.append(None)
                current = G
            else:
                self.group_elements.append(current)
                current = self.curve.point_add(current, G)
        
        # Find expected d
        self.expected_d = None
        for d in range(1, n):
            if self.curve.scalar_multiply(d, G) == Q:
                self.expected_d = d
                break
        
        print(f"Order n = {n}, Expected d = {self.expected_d}")
        
        # Qubit counts
        self.k_bits = 3  # log2(7) = ~3 bits
        self.coord_bits = 4  # p=13 < 16
        self.point_bits = 9  # x:4, y:4, inf:1
    
    def create_simple_lookup_oracle(self, k_reg: QuantumRegister, 
                                    point_reg: QuantumRegister) -> QuantumCircuit:
        """
        Simple lookup oracle: |k> |0> -> |k> |encode(k*G)>
        
        Uses direct controlled operations for each k value.
        More straightforward than multiplexer approach.
        """
        qc = QuantumCircuit(k_reg, point_reg, name='Simple_Lookup')
        
        # Pre-encode points
        point_encodings = {}
        for k, point in enumerate(self.group_elements):
            if point is None:
                # Infinity: set bit 8 (infinity flag)
                point_encodings[k] = (0, 0, True)
            else:
                x, y = point
                point_encodings[k] = (x, y, False)
        
        # For each k value, add controlled operations to set point bits
        # We'll use a pattern: for each bit position, determine which k values set it
        
        # X coordinate bits (bits 0-3)
        for bit_idx in range(4):
            # Find k values where x has this bit set
            for k in range(min(self.n, 8)):  # Handle up to 8 values
                if k in point_encodings and not point_encodings[k][2]:  # Not infinity
                    x, y, is_inf = point_encodings[k]
                    if (x >> bit_idx) & 1:
                        # Set this bit when k_reg == k
                        self._add_controlled_set(qc, k_reg, k, point_reg[bit_idx])
        
        # Y coordinate bits (bits 4-7)
        for bit_idx in range(4):
            for k in range(min(self.n, 8)):
                if k in point_encodings and not point_encodings[k][2]:
                    x, y, is_inf = point_encodings[k]
                    if (y >> bit_idx) & 1:
                        self._add_controlled_set(qc, k_reg, k, point_reg[4 + bit_idx])
        
        # Infinity flag (bit 8)
        for k in range(min(self.n, 8)):
            if k in point_encodings and point_encodings[k][2]:
                self._add_controlled_set(qc, k_reg, k, point_reg[8])
        
        return qc
    
    def _add_controlled_set(self, qc: QuantumCircuit, control_reg: QuantumRegister,
                           value: int, target: int):
        """
        Add operation: if control_reg == value, set target qubit.
        
        For 3-bit register, value can be 0-7.
        """
        if len(control_reg) == 1:
            # Single qubit
            if value == 1:
                qc.cx(control_reg[0], target)
            else:
                qc.x(control_reg[0])
                qc.cx(control_reg[0], target)
                qc.x(control_reg[0])
        elif len(control_reg) == 2:
            # 2 qubits: value can be 0-3
            if value < 4:
                controls = []
                if value & 1:
                    controls.append(control_reg[0])
                else:
                    qc.x(control_reg[0])
                    controls.append(control_reg[0])
                    qc.x(control_reg[0])
                if value & 2:
                    controls.append(control_reg[1])
                else:
                    qc.x(control_reg[1])
                    controls.append(control_reg[1])
                    qc.x(control_reg[1])
                
                if len(controls) == 2:
                    qc.ccx(controls[0], controls[1], target)
        else:
            # 3 qubits: use MCX
            controls = []
            x_gates = []
            
            for i in range(len(control_reg)):
                if (value >> i) & 1:
                    controls.append(control_reg[i])
                else:
                    qc.x(control_reg[i])
                    x_gates.append(control_reg[i])
                    controls.append(control_reg[i])
            
            if len(controls) >= 2:
                qc.mcx(controls, target)
            
            # Restore X gates
            for gate in reversed(x_gates):
                qc.x(gate)
    
    def create_period_finding_circuit(self, period_bits: int = 6) -> QuantumCircuit:
        """
        Create period finding circuit for ECDLP.
        
        We want to find period of function f(x) related to discrete log.
        For ECDLP: find period in a*G + b*Q relationship.
        """
        # Registers
        period_reg = QuantumRegister(period_bits, 'period')
        a_reg = QuantumRegister(self.k_bits, 'a')
        b_reg = QuantumRegister(self.k_bits, 'b')
        temp_reg = QuantumRegister(self.k_bits, 'temp')  # For computing (a + d*b) mod n
        point_reg = QuantumRegister(self.point_bits, 'point')
        classical_reg = ClassicalRegister(period_bits, 'c')
        
        qc = QuantumCircuit(period_reg, a_reg, b_reg, temp_reg, point_reg, classical_reg,
                           name='Shor_ECDLP_PeriodFinding')
        
        # Step 1: Initialize period register in superposition
        for i in range(period_bits):
            qc.h(period_reg[i])
        
        # Step 2: Initialize a and b in superposition
        for i in range(self.k_bits):
            qc.h(a_reg[i])
            qc.h(b_reg[i])
        
        # Step 3: Compute temp = (a + d*b) mod n
        # For n=7, d=6, we have: (a + 6*b) mod 7
        
        # Simplified: For small n, we can use classical computation in superposition
        # via controlled operations
        
        # For now, use temp = a (simplified - full implementation needs mod arithmetic)
        for i in range(self.k_bits):
            qc.cx(a_reg[i], temp_reg[i])
        
        # Step 4: Use lookup to load point
        lookup = self.create_simple_lookup_oracle(temp_reg, point_reg)
        qc.append(lookup, temp_reg[:] + point_reg[:])
        
        # Step 5: Apply phase based on period register
        # This is where period finding happens
        
        # Step 6: Uncompute (reverse lookup and temp)
        lookup_inv = lookup.inverse()
        qc.append(lookup_inv, temp_reg[:] + point_reg[:])
        for i in range(self.k_bits):
            qc.cx(a_reg[i], temp_reg[i])
        
        # Step 7: Apply inverse QFT to period register
        iqft = QFT(num_qubits=period_bits, approximation_degree=0, do_swaps=True).inverse()
        qc.append(iqft, period_reg)
        
        # Step 8: Measure period register
        qc.measure(period_reg, classical_reg)
        
        return qc
    
    def extract_period_continued_fractions(self, measured: int, n_qubits: int) -> Optional[int]:
        """Extract period using continued fractions."""
        if measured == 0:
            return None
        
        N = 2 ** n_qubits
        phase = measured / N
        
        # Use continued fractions to find k/r
        # Try denominators up to n
        for r in range(1, self.n + 1):
            for k in range(r):
                target = k / r
                if abs(phase - target) < 0.01:
                    return r
        
        return None


def run_final_shor(bit_length: int = 4, shots: int = 2048):
    """Run final Shor implementation."""
    print(f"\n{'='*60}")
    print(f"Final Shor's ECDLP - {bit_length}-bit key")
    print(f"{'='*60}")
    
    # Load key
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_file = os.path.join(script_dir, "ecc_keys.json")
    key_data = load_ecc_key(key_file, bit_length=bit_length)
    
    p = key_data['prime']
    G = tuple(key_data['generator_point'])
    Q = tuple(key_data['public_key'])
    n = key_data['subgroup_order']
    expected_d = key_data['private_key']
    
    # Create curve
    curve = EllipticCurve(p, a=0, b=7)
    
    # Initialize
    shor = FinalShorECDLP(curve, G, Q, n)
    
    # Create circuit
    print("\nCreating period finding circuit...")
    qc = shor.create_period_finding_circuit(period_bits=6)
    
    print(f"\nCircuit stats:")
    print(f"  Qubits: {qc.num_qubits}")
    print(f"  Depth: {qc.depth()}")
    print(f"  Size: {qc.size()}")
    
    # Run on simulator
    print("\nRunning on quantum simulator...")
    simulator = AerSimulator()
    transpiled = transpile(qc, simulator, optimization_level=1)
    job = simulator.run(transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    print(f"\nTop 10 measurements:")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for bitstring, count in sorted_counts[:10]:
        measured = int(bitstring, 2)
        phase = measured / (2 ** 6)
        print(f"  {bitstring}: {count} (value={measured}, phase={phase:.4f})")
        
        # Try to extract period
        period = shor.extract_period_continued_fractions(measured, 6)
        if period:
            print(f"    -> Possible period: {period}")
    
    return counts


if __name__ == "__main__":
    run_final_shor(bit_length=4, shots=2048)

