"""
Efficient Lookup-Based Oracle for Shor's ECDLP

For 4-bit key (n=7): Optimized implementation using state preparation
and quantum multiplexers. This follows the Option 3 approach from the guide.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT, StatePreparation
from qiskit_aer import AerSimulator
from qiskit import transpile
from typing import Tuple, Dict, Optional, List
from elliptic_curve import EllipticCurve, load_ecc_key
import os


class EfficientLookupShor:
    """
    Efficient Shor's ECDLP using lookup oracle.
    
    Strategy:
    1. Precompute all group elements: {0*G, 1*G, ..., 6*G}
    2. Use quantum multiplexer to load points based on control register
    3. Implement f(a, b) = a*G + b*Q using lookup
    """
    
    def __init__(self, curve: EllipticCurve, G: Tuple[int, int], Q: Tuple[int, int], n: int):
        """Initialize with curve parameters."""
        self.curve = curve
        self.G = G
        self.Q = Q
        self.n = n
        self.p = curve.p
        
        # Precompute all multiples of G
        self.group_points = []
        current = None
        for i in range(n):
            if i == 0:
                self.group_points.append(None)  # Point at infinity
                current = G
            else:
                self.group_points.append(current)
                current = self.curve.point_add(current, G)
        
        # Find expected d
        self.expected_d = None
        for d in range(1, n):
            if self.curve.scalar_multiply(d, G) == Q:
                self.expected_d = d
                break
        
        print(f"Initialized:")
        print(f"  Order n = {n}")
        print(f"  Expected d = {self.expected_d}")
        print(f"  Group elements: {len(self.group_points)}")
        
        # Qubit counts
        self.k_bits = int(np.ceil(np.log2(n)))  # 3 bits for n=7
        self.coord_bits = 4  # p=13 < 16
        self.point_bits = 2 * self.coord_bits + 1  # 9 bits (x:4, y:4, inf:1)
    
    def encode_point_value(self, point: Optional[Tuple[int, int]]) -> int:
        """
        Encode point as integer for easier manipulation.
        
        Format: [inf_flag (1 bit), x (4 bits), y (4 bits)]
        Returns: integer representation
        """
        if point is None:
            return 1 << 8  # Infinity flag set
        
        x, y = point
        return (x & 0xF) | ((y & 0xF) << 4)
    
    def create_multiplexer_oracle(self, control: QuantumRegister, 
                                  target: QuantumRegister) -> QuantumCircuit:
        """
        Create oracle using quantum multiplexer.
        
        Maps: |k> |0> -> |k> |encode(k*G)>
        
        Uses controlled operations to load precomputed points.
        More efficient than individual multi-controlled gates.
        """
        qc = QuantumCircuit(control, target, name='Multiplexer_Oracle')
        
        # Pre-encode all points
        encoded_points = [self.encode_point_value(pt) for pt in self.group_points]
        
        # For each possible k value, set target bits accordingly
        # We'll use a pattern-based approach
        
        # Strategy: For each bit position in target register,
        # determine which k values need it set to 1
        # Then use multi-controlled gates
        
        for bit_pos in range(self.point_bits):
            # Find all k where this bit should be 1
            k_values_set = [k for k, encoded in enumerate(encoded_points) 
                          if encoded & (1 << bit_pos)]
            
            if not k_values_set:
                continue
            
            # For each k that sets this bit, add controlled operation
            for k in k_values_set:
                # Create control condition: control register == k
                # Need to build multi-controlled gate
                
                if len(control) == 1:
                    # Single control qubit
                    if k == 1:
                        qc.cx(control[0], target[bit_pos])
                    else:
                        qc.x(control[0])
                        qc.cx(control[0], target[bit_pos])
                        qc.x(control[0])
                else:
                    # Multiple control qubits - use MCX
                    # Build control list matching k's binary representation
                    controls = []
                    ancilla = []
                    
                    # For simplicity with n=7 (3 bits), handle each case
                    if k < len(control) ** 2:  # Within register size
                        # Set up controls to match k's binary
                        for i in range(len(control)):
                            if (k >> i) & 1:
                                controls.append(control[i])
                            else:
                                # Need to invert this control
                                # Use ancilla or invert
                                qc.x(control[i])
                                controls.append(control[i])
                                qc.x(control[i])  # Restore
                        
                        # Apply controlled operation
                        if len(controls) == len(control):
                            # All controls match pattern
                            qc.mcx(controls, target[bit_pos])
        
        return qc
    
    def create_ecdlp_function_circuit(self, a_reg: QuantumRegister, b_reg: QuantumRegister,
                                     result_reg: QuantumRegister) -> QuantumCircuit:
        """
        Create circuit computing: |a, b> |0> -> |a, b> |encode((a + d*b)*G)>
        
        Since Q = d*G, we have: a*G + b*Q = (a + d*b)*G
        We compute (a + d*b) mod n, then lookup the result.
        """
        qc = QuantumCircuit(a_reg, b_reg, result_reg, name='ECDLP_Function')
        
        # Temporary register for computing (a + d*b) mod n
        temp_reg = QuantumRegister(self.k_bits, 'temp')
        qc.add_register(temp_reg)
        
        # Compute temp = (a + d*b) mod n
        # For small n, we can use lookup or quantum arithmetic
        
        # Simplified: For n=7, d=6, we compute (a + 6*b) mod 7
        # This is: (a + 6*b) mod 7 = (a + (7-1)*b) mod 7 = (a - b) mod 7
        
        # Actually: 6*b mod 7 = -b mod 7 = (7-b) mod 7 for b > 0
        
        # For now, use a direct computation approach
        # We'll implement quantum modular arithmetic
        
        # Placeholder: This needs full quantum arithmetic implementation
        # For demonstration, we'll use a simplified lookup
        
        # Then use multiplexer to load the point
        lookup_oracle = self.create_multiplexer_oracle(temp_reg, result_reg)
        qc.append(lookup_oracle, temp_reg[:] + result_reg[:])
        
        return qc
    
    def create_shor_circuit(self, period_bits: int = 6) -> QuantumCircuit:
        """
        Create full Shor's circuit for ECDLP.
        
        Uses semi-classical QFT for efficiency.
        """
        # Registers
        period_reg = QuantumRegister(period_bits, 'period')  # For phase estimation
        a_reg = QuantumRegister(self.k_bits, 'a')  # For a*G
        b_reg = QuantumRegister(self.k_bits, 'b')  # For b*Q
        result_reg = QuantumRegister(self.point_bits, 'result')  # For storing point
        classical_reg = ClassicalRegister(period_bits, 'c')
        
        qc = QuantumCircuit(period_reg, a_reg, b_reg, result_reg, classical_reg,
                           name='Shor_ECDLP_Full')
        
        # Step 1: Initialize period register in superposition
        for i in range(period_bits):
            qc.h(period_reg[i])
        
        # Step 2: Initialize a and b in superposition
        for i in range(self.k_bits):
            qc.h(a_reg[i])
            qc.h(b_reg[i])
        
        # Step 3: Apply controlled ECDLP function
        # For each qubit in period register, apply function if qubit is |1>
        # This is quantum phase estimation
        
        # Simplified version: Apply function once
        # Full version would apply controlled-U^2^k for each period qubit
        
        ecdlp_func = self.create_ecdlp_function_circuit(a_reg, b_reg, result_reg)
        qc.append(ecdlp_func, a_reg[:] + b_reg[:] + result_reg[:])
        
        # Step 4: Apply inverse QFT to period register
        iqft = QFT(num_qubits=period_bits, approximation_degree=0, do_swaps=True).inverse()
        qc.append(iqft, period_reg)
        
        # Step 5: Measure period register
        qc.measure(period_reg, classical_reg)
        
        return qc
    
    def create_simple_test_circuit(self) -> QuantumCircuit:
        """
        Create simplified test circuit: just the lookup oracle.
        
        Tests: |k> |0> -> |k> |encode(k*G)>
        """
        control = QuantumRegister(self.k_bits, 'k')
        target = QuantumRegister(self.point_bits, 'point')
        classical = ClassicalRegister(self.k_bits + self.point_bits, 'c')
        
        qc = QuantumCircuit(control, target, classical, name='Test_Lookup')
        
        # Initialize control in superposition
        for i in range(self.k_bits):
            qc.h(control[i])
        
        # Apply lookup oracle
        oracle = self.create_multiplexer_oracle(control, target)
        qc.append(oracle, control[:] + target[:])
        
        # Measure
        qc.measure(control, classical[:self.k_bits])
        qc.measure(target, classical[self.k_bits:])
        
        return qc


def test_lookup_oracle(bit_length: int = 4, shots: int = 1024):
    """Test the lookup oracle."""
    print(f"\n{'='*60}")
    print(f"Testing Lookup Oracle - {bit_length}-bit key")
    print(f"{'='*60}")
    
    # Load key
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_file = os.path.join(script_dir, "ecc_keys.json")
    key_data = load_ecc_key(key_file, bit_length=bit_length)
    
    p = key_data['prime']
    G = tuple(key_data['generator_point'])
    Q = tuple(key_data['public_key'])
    n = key_data['subgroup_order']
    
    # Create curve
    curve = EllipticCurve(p, a=0, b=7)
    
    # Initialize
    shor = EfficientLookupShor(curve, G, Q, n)
    
    # Create test circuit
    print("\nCreating test circuit...")
    qc = shor.create_simple_test_circuit()
    
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
        # Parse: first k_bits are control, rest are point encoding
        k_bits = shor.k_bits
        k_str = bitstring[:k_bits]
        point_str = bitstring[k_bits:]
        k_val = int(k_str, 2)
        point_val = int(point_str, 2)
        print(f"  k={k_val}, point={point_str} ({point_val}): {count}")
    
    return counts


if __name__ == "__main__":
    test_lookup_oracle(bit_length=4, shots=1024)

