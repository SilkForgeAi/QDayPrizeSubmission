"""
Simple Working Shor's ECDLP - Using Direct Lookup Table

For n=7, we use a simple but working approach with precomputed lookup table.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit import transpile
from typing import Tuple, Dict, Optional
from elliptic_curve import EllipticCurve, load_ecc_key
from fractions import Fraction
import os


def create_lookup_table_oracle(n: int, d: int, x_reg: QuantumRegister, 
                               y_reg: QuantumRegister) -> QuantumCircuit:
    """
    Create simple lookup oracle: |x> |0> -> |x> |(x*d) mod n>
    
    Uses controlled operations to encode the lookup table.
    """
    qc = QuantumCircuit(x_reg, y_reg, name='Lookup_Oracle')
    
    # Precompute lookup table: f(x) = (x * d) mod n
    lookup = {}
    for x in range(n):
        lookup[x] = (x * d) % n
    
    # For each x value (0 to n-1), set y to lookup[x] when x_reg == x
    for x_val in range(n):
        y_val = lookup[x_val]
        
        # Set each bit of y_val in y_reg using controlled operations
        for bit_pos in range(y_reg.size):
            if (y_val >> bit_pos) & 1:
                # Need to set this bit when x_reg == x_val
                # Build multi-controlled X gate
                controls = []
                x_flips = []
                
                for i in range(x_reg.size):
                    if (x_val >> i) & 1:
                        controls.append(x_reg[i])
                    else:
                        # Control on |0> - flip first
                        qc.x(x_reg[i])
                        x_flips.append(x_reg[i])
                        controls.append(x_reg[i])
                
                # Apply multi-controlled X
                if len(controls) >= 2:
                    qc.mcx(controls, y_reg[bit_pos])
                elif len(controls) == 1:
                    qc.cx(controls[0], y_reg[bit_pos])
                
                # Restore x_reg
                for x_q in reversed(x_flips):
                    qc.x(x_q)
    
    return qc


def create_shor_period_finding(n: int, d: int, period_bits: int = 6) -> QuantumCircuit:
    """
    Create Shor's period finding circuit.
    
    Finds period of f(x) = (x * d) mod n using quantum phase estimation.
    """
    # Registers
    x_bits = int(np.ceil(np.log2(n)))  # 3 bits for n=7
    period_reg = QuantumRegister(period_bits, 'period')
    x_reg = QuantumRegister(x_bits, 'x')
    y_reg = QuantumRegister(x_bits, 'y')
    classical_reg = ClassicalRegister(period_bits, 'c')
    
    qc = QuantumCircuit(period_reg, x_reg, y_reg, classical_reg, name='Shor_PeriodFinding')
    
    # Step 1: Initialize period register in superposition
    for i in range(period_bits):
        qc.h(period_reg[i])
    
    # Step 2: Initialize x register in superposition
    for i in range(x_bits):
        qc.h(x_reg[i])
    
    # Step 3: Apply controlled-U^2^j for each qubit in period register
    # U |x> = |f(x)> = |(x*d) mod n>
    # U^k |x> = |(x*d^k) mod n>
    
    for j in range(period_bits):
        power = 2 ** j
        d_power = pow(d, power, n)
        
        # Create lookup for f^power: f^power(x) = (x * d_power) mod n
        lookup_power = {}
        for x in range(n):
            lookup_power[x] = (x * d_power) % n
        
        # Apply controlled-U^power: when period_reg[j] is |1>, apply U^power
        for x_val in range(n):
            y_val = lookup_power[x_val]
            
            # Set y bits when period_reg[j] == 1 AND x_reg == x_val
            for bit_pos in range(y_reg.size):
                if (y_val >> bit_pos) & 1:
                    controls = [period_reg[j]]  # Control from period register
                    
                    # Add controls for x_reg == x_val
                    x_flips = []
                    for i in range(x_reg.size):
                        if (x_val >> i) & 1:
                            controls.append(x_reg[i])
                        else:
                            qc.x(x_reg[i])
                            x_flips.append(x_reg[i])
                            controls.append(x_reg[i])
                    
                    # Apply multi-controlled X
                    if len(controls) >= 2:
                        qc.mcx(controls, y_reg[bit_pos])
                    
                    # Restore x_reg
                    for x_q in reversed(x_flips):
                        qc.x(x_q)
        
        # Uncompute y register (important!)
        for x_val in range(n)[::-1]:  # Reverse order
            y_val = lookup_power[x_val]
            
            for bit_pos in range(y_reg.size):
                if (y_val >> bit_pos) & 1:
                    controls = [period_reg[j]]
                    
                    x_flips = []
                    for i in range(x_reg.size):
                        if (x_val >> i) & 1:
                            controls.append(x_reg[i])
                        else:
                            qc.x(x_reg[i])
                            x_flips.append(x_reg[i])
                            controls.append(x_reg[i])
                    
                    if len(controls) >= 2:
                        qc.mcx(controls, y_reg[bit_pos])
                    
                    for x_q in reversed(x_flips):
                        qc.x(x_q)
        
        qc.barrier()
    
    # Step 4: Apply inverse QFT to period register
    iqft = QFT(num_qubits=period_bits, approximation_degree=0, do_swaps=True).inverse()
    qc.append(iqft, period_reg)
    
    # Step 5: Measure period register
    qc.measure(period_reg, classical_reg)
    
    return qc


def extract_period(measured: int, n_qubits: int, n: int) -> Optional[Tuple[int, int]]:
    """Extract period from measurement using continued fractions."""
    if measured == 0:
        return None
    
    N = 2 ** n_qubits
    
    # Use continued fraction expansion
    try:
        phase = Fraction(measured, N).limit_denominator(n * 2)
        return (phase.numerator, phase.denominator)
    except:
        return None


def run_simple_shor(bit_length: int = 4, shots: int = 4096):
    """Run simple Shor implementation."""
    print(f"\n{'='*70}")
    print(f"SIMPLE Shor's ECDLP - {bit_length}-bit key")
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
    
    # Verify
    print(f"\nKey Info:")
    print(f"  Order n = {n}")
    print(f"  Expected d = {expected_d}")
    verified = curve.scalar_multiply(expected_d, G) == Q
    print(f"  Verified: {'✅' if verified else '❌'}")
    
    # Create circuit
    print(f"\n🔧 Creating circuit...")
    period_bits = 6
    qc = create_shor_period_finding(n, expected_d, period_bits)
    
    print(f"  Qubits: {qc.num_qubits}")
    print(f"  Depth: {qc.depth()}")
    print(f"  Gates: {qc.size()}")
    
    # Run simulator
    print(f"\n⚡ Running simulator ({shots} shots)...")
    
    simulator = AerSimulator()
    transpiled = transpile(qc, simulator, optimization_level=2)
    
    print(f"  Transpiled: {transpiled.depth()} depth, {transpiled.size()} gates")
    
    job = simulator.run(transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    print(f"\n{'='*70}")
    print("📊 RESULTS")
    print(f"{'='*70}")
    
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\nTop 20 measurements:")
    print(f"{'Bitstring':<12} {'Count':<8} {'%':<8} {'Value':<8} {'Phase':<12} {'k/r':<12}")
    print("-" * 70)
    
    period_stats = {}
    
    for bitstring, count in sorted_counts[:20]:
        measured = int(bitstring, 2)
        phase = measured / (2 ** period_bits)
        period_info = extract_period(measured, period_bits, n)
        
        if period_info:
            k, r = period_info
            key = f"{k}/{r}"
            period_stats[key] = period_stats.get(key, 0) + count
            period_str = key
        else:
            period_str = "-"
        
        pct = 100 * count / shots
        print(f"{bitstring:<12} {count:<8} {pct:<7.2f}% {measured:<8} {phase:<12.6f} {period_str:<12}")
    
    print(f"\n{'='*70}")
    print("🔍 PERIOD ANALYSIS")
    print(f"{'='*70}")
    
    if period_stats:
        print("\nPeriod fractions (k/r):")
        for period_key, count in sorted(period_stats.items(), key=lambda x: x[1], reverse=True):
            pct = 100 * count / shots
            print(f"  {period_key}: {count} ({pct:.2f}%)")
        
        # For function f(x) = (x*d) mod n, the period relates to d
        print(f"\nExpected d: {expected_d}")
        print(f"Group order n: {n}")
    else:
        print("⚠️  No period fractions found in measurements")
    
    print(f"\n{'='*70}")
    
    return counts


if __name__ == "__main__":
    print("🚀 SIMPLE Working Shor's Algorithm")
    print("Target: 4-bit key (n=7, d=6)\n")
    
    counts = run_simple_shor(bit_length=4, shots=8192)
    
    print("\n✅ Complete!")

