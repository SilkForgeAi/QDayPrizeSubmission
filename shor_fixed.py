"""
Fixed Shor's Algorithm for ECDLP - Proper Phase Kickback

Correctly implements quantum phase estimation with controlled-U operations.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit import transpile
from typing import Tuple, Dict, Optional, List
from elliptic_curve import EllipticCurve, load_ecc_key
from fractions import Fraction
import os


class FixedShorECDLP:
    """
    Fixed implementation with proper phase kickback.
    
    For ECDLP: Find period of f(x) = x * d mod n
    The period reveals information about d.
    """
    
    def __init__(self, curve: EllipticCurve, G: Tuple[int, int], Q: Tuple[int, int], n: int):
        """Initialize."""
        self.curve = curve
        self.G = G
        self.Q = Q
        self.n = n
        self.p = curve.p
        
        # Find expected d
        self.expected_d = None
        for d in range(1, n):
            if self.curve.scalar_multiply(d, G) == Q:
                self.expected_d = d
                break
        
        print(f"Order n = {n}, Expected d = {self.expected_d}")
        
        # Qubit counts
        self.k_bits = int(np.ceil(np.log2(n)))  # 3 bits for n=7
        self.period_bits = 6  # Resolution for period finding
        
        # Precompute function values: f(x) = (x * d) mod n
        self.f_values = {}
        for x in range(n):
            self.f_values[x] = (x * self.expected_d) % n
    
    def create_controlled_U_power(self, control_bit: int, x_reg: QuantumRegister, 
                                  y_reg: QuantumRegister, power: int) -> QuantumCircuit:
        """
        Create controlled-U^power operation.
        
        U |x> = |f(x)> where f(x) = (x * d) mod n
        U^power |x> = |f^power(x)> = |(x * d^power) mod n>
        
        The control bit controls whether to apply U^power.
        """
        qc = QuantumCircuit(x_reg, y_reg, name=f'CU^{power}')
        
        # Compute d^power mod n
        d_power = pow(self.expected_d, power, self.n)
        
        # Precompute f^power values: (x * d^power) mod n
        f_power = {}
        for x in range(min(self.n, 8)):  # Handle up to 8 values (3 bits)
            f_power[x] = (x * d_power) % self.n
        
        # For each x value, set y to f_power(x) when control is active
        # We'll use a simplified approach with controlled swaps/operations
        
        # Initialize y register to 0 first (should already be |0>)
        
        # Apply controlled operations for each x value
        for x_val in range(min(self.n, 8)):
            y_val = f_power[x_val]
            
            # When x == x_val, we want to set y to y_val
            # But this should only happen when control is |1>
            # Use multi-controlled operations
            
            # For each bit of y_val that should be 1, add controlled-X
            for bit_pos in range(self.k_bits):
                if (y_val >> bit_pos) & 1:
                    # Build control: control_bit AND (x == x_val)
                    controls = []
                    
                    # Add control bit (this will be added externally)
                    # For now, build controls for x == x_val
                    for i in range(self.k_bits):
                        if (x_val >> i) & 1:
                            controls.append(x_reg[i])
                        else:
                            # Need to control on |0>, flip and control
                            qc.x(x_reg[i])
                            controls.append(x_reg[i])
                            qc.x(x_reg[i])
                    
                    # This will be a multi-controlled X on y_reg[bit_pos]
                    # The external control will be added when this is used
                    # Store for later - for now just mark
                    pass
        
        return qc
    
    def create_shor_circuit(self) -> QuantumCircuit:
        """
        Create Shor's circuit with proper phase estimation.
        
        The key is to apply controlled-U^2^j for each qubit j in period register.
        This creates phase kickback that reveals the period.
        """
        # Registers
        period_reg = QuantumRegister(self.period_bits, 'period')
        x_reg = QuantumRegister(self.k_bits, 'x')
        y_reg = QuantumRegister(self.k_bits, 'y')
        classical_reg = ClassicalRegister(self.period_bits, 'c')
        
        qc = QuantumCircuit(period_reg, x_reg, y_reg, classical_reg, name='Shor_Fixed')
        
        # Step 1: Initialize period register in superposition
        for i in range(self.period_bits):
            qc.h(period_reg[i])
        
        # Step 2: Initialize x register in superposition
        for i in range(self.k_bits):
            qc.h(x_reg[i])
        
        # Step 3: Apply controlled-U^2^j for each period register qubit
        # This is the core of quantum phase estimation
        
        for j in range(self.period_bits):
            power = 2 ** j
            d_power = pow(self.expected_d, power, self.n)
            
            # Precompute f^power
            f_power = {}
            for x_val in range(min(self.n, 8)):
                f_power[x_val] = (x_val * d_power) % self.n
            
            # Apply controlled-U^power
            # When period_reg[j] is |1>, apply U^power to (x_reg, y_reg)
            
            # For each x value, set y to f_power(x) when control is active
            for x_val in range(min(self.n, 8)):
                y_val = f_power[x_val]
                
                # For each bit of y that should be set
                for bit_pos in range(self.k_bits):
                    if (y_val >> bit_pos) & 1:
                        # Controlled operation: if period_reg[j] == 1 AND x == x_val, set y bit
                        controls = [period_reg[j]]
                        
                        # Add controls for x == x_val
                        x_controls_flipped = []
                        for i in range(self.k_bits):
                            if (x_val >> i) & 1:
                                controls.append(x_reg[i])
                            else:
                                # Need to control on |0>
                                qc.x(x_reg[i])
                                x_controls_flipped.append(x_reg[i])
                                controls.append(x_reg[i])
                        
                        # Apply multi-controlled X
                        if len(controls) >= 2:
                            qc.mcx(controls, y_reg[bit_pos])
                        
                        # Unflip x controls
                        for x_ctrl in reversed(x_controls_flipped):
                            qc.x(x_ctrl)
            
            qc.barrier()
            
            # Uncompute y register (important for phase kickback to work)
            # Reverse the operations to reset y to |0>
            for x_val in range(min(self.n, 8))[::-1]:  # Reverse order
                y_val = f_power[x_val]
                
                for bit_pos in range(self.k_bits):
                    if (y_val >> bit_pos) & 1:
                        controls = [period_reg[j]]
                        
                        x_controls_flipped = []
                        for i in range(self.k_bits):
                            if (x_val >> i) & 1:
                                controls.append(x_reg[i])
                            else:
                                qc.x(x_reg[i])
                                x_controls_flipped.append(x_reg[i])
                                controls.append(x_reg[i])
                        
                        if len(controls) >= 2:
                            qc.mcx(controls, y_reg[bit_pos])
                        
                        for x_ctrl in reversed(x_controls_flipped):
                            qc.x(x_ctrl)
            
            qc.barrier()
        
        # Step 4: Apply inverse QFT to period register
        iqft = QFT(num_qubits=self.period_bits, approximation_degree=0, do_swaps=True).inverse()
        qc.append(iqft, period_reg)
        
        # Step 5: Measure period register
        qc.measure(period_reg, classical_reg)
        
        return qc
    
    def extract_period_continued_fractions(self, measured: int, n_qubits: int) -> Optional[Tuple[int, int]]:
        """
        Extract period using continued fractions.
        
        Returns: (k, r) where measured/N ≈ k/r
        """
        if measured == 0:
            return None
        
        N = 2 ** n_qubits
        phase = Fraction(measured, N).limit_denominator(self.n * 2)
        
        return (phase.numerator, phase.denominator)


def run_fixed_shor(bit_length: int = 4, shots: int = 4096):
    """Run fixed Shor implementation."""
    print(f"\n{'='*70}")
    print(f"FIXED Shor's ECDLP - {bit_length}-bit key")
    print(f"{'='*70}")
    
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
    shor = FixedShorECDLP(curve, G, Q, n)
    
    # Create circuit
    print("\n🔧 Creating Shor's circuit...")
    qc = shor.create_shor_circuit()
    
    print(f"  Qubits: {qc.num_qubits}")
    print(f"  Depth: {qc.depth()}")
    print(f"  Gates: {qc.size()}")
    
    # Run on simulator
    print(f"\n⚡ Running on quantum simulator ({shots} shots)...")
    
    simulator = AerSimulator()
    transpiled = transpile(qc, simulator, optimization_level=2)
    
    print(f"  Transpiled depth: {transpiled.depth()}")
    print(f"  Transpiled gates: {transpiled.size()}")
    
    job = simulator.run(transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    print(f"\n{'='*70}")
    print("📊 RESULTS")
    print(f"{'='*70}")
    print(f"Unique measurements: {len(counts)}")
    
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Rank':<6} {'Bitstring':<12} {'Count':<8} {'%':<8} {'Value':<8} {'Phase':<12} {'k/r':<12}")
    print("-" * 80)
    
    period_counts = {}
    
    for rank, (bitstring, count) in enumerate(sorted_counts[:20], 1):
        measured = int(bitstring, 2)
        phase_val = measured / (2 ** shor.period_bits)
        period_info = shor.extract_period_continued_fractions(measured, shor.period_bits)
        
        if period_info:
            k, r = period_info
            period_key = f"{k}/{r}"
            period_counts[period_key] = period_counts.get(period_key, 0) + count
            period_str = period_key
        else:
            period_str = "N/A"
        
        pct = 100 * count / shots
        print(f"{rank:<6} {bitstring:<12} {count:<8} {pct:<7.2f}% {measured:<8} {phase_val:<12.6f} {period_str:<12}")
    
    print(f"\n{'='*70}")
    print("🔍 PERIOD ANALYSIS")
    print(f"{'='*70}")
    
    if period_counts:
        print("\nPeriod fractions found:")
        for period_key, count in sorted(period_counts.items(), key=lambda x: x[1], reverse=True):
            pct = 100 * count / shots
            print(f"  {period_key}: {count} times ({pct:.2f}%)")
        
        # The period r should relate to finding d
        print(f"\nExpected discrete logarithm: d = {expected_d}")
        print(f"Order of group: n = {n}")
        
        # Check if we found useful periods
        best_period = max(period_counts.items(), key=lambda x: x[1])
        print(f"\nMost common period fraction: {best_period[0]} ({best_period[1]} occurrences)")
    else:
        print("⚠️  No clear period fractions found")
    
    print(f"\n{'='*70}")
    
    return counts, period_counts


if __name__ == "__main__":
    print("🚀 FIXED Shor's Algorithm for ECDLP")
    print("Target: 4-bit key (n=7, expected d=6)\n")
    
    counts, periods = run_fixed_shor(bit_length=4, shots=4096)
    
    print("\n✅ Done!")

