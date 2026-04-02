"""
Step 1: Test Quantum Phase Estimation with Known Unitary

Test QPE on a simple phase gate U = R_z(2π/r) with known period r=4.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT, RZGate
from qiskit_aer import AerSimulator
from qiskit import transpile
from fractions import Fraction


def create_qpe_test_circuit(period: int = 4, precision_bits: int = 4) -> QuantumCircuit:
    """
    Create QPE circuit to estimate phase of R_z(2π/r).
    
    Should find phase = 1/r = 1/4 = 0.25
    """
    # Registers
    control_reg = QuantumRegister(precision_bits, 'control')
    target_reg = QuantumRegister(1, 'target')
    classical_reg = ClassicalRegister(precision_bits, 'c')
    
    qc = QuantumCircuit(control_reg, target_reg, classical_reg, name='QPE_Test')
    
    # Initialize target to eigenstate |1⟩ (eigenvector of R_z)
    qc.x(target_reg[0])
    
    # Step 1: Initialize control register in superposition
    for i in range(precision_bits):
        qc.h(control_reg[i])
    
    # Step 2: Apply controlled-U^2^j for each control qubit
    # U = R_z(2π/r), so U^2^j = R_z(2^j * 2π/r)
    phase = 2 * np.pi / period
    
    for j in range(precision_bits):
        power = 2 ** j
        controlled_phase = RZGate(power * phase)
        qc.append(controlled_phase.control(1), [control_reg[j], target_reg[0]])
    
    # Step 3: Apply inverse QFT to control register
    iqft = QFT(num_qubits=precision_bits, approximation_degree=0, do_swaps=True).inverse()
    qc.append(iqft, control_reg)
    
    # Step 4: Measure control register
    qc.measure(control_reg, classical_reg)
    
    return qc


def extract_phase(measured: int, n_bits: int) -> float:
    """Extract phase from measurement."""
    return measured / (2 ** n_bits)


def test_qpe():
    """Test QPE with known period."""
    print("=" * 70)
    print("Step 1: Testing Quantum Phase Estimation")
    print("=" * 70)
    
    period = 4
    precision_bits = 6
    shots = 2048
    
    print(f"\nTest setup:")
    print(f"  Known period: r = {period}")
    print(f"  Expected phase: θ = 1/{period} = {1/period}")
    print(f"  Precision bits: {precision_bits}")
    
    # Create circuit
    qc = create_qpe_test_circuit(period, precision_bits)
    
    print(f"\nCircuit:")
    print(f"  Qubits: {qc.num_qubits}")
    print(f"  Depth: {qc.depth()}")
    
    # Run simulation
    print(f"\nRunning simulation ({shots} shots)...")
    simulator = AerSimulator()
    transpiled = transpile(qc, simulator, optimization_level=1)
    job = simulator.run(transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    print(f"\nResults:")
    print(f"{'Bitstring':<12} {'Count':<8} {'%':<8} {'Value':<8} {'Phase':<12} {'k/r':<12}")
    print("-" * 70)
    
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    phase_stats = {}
    
    for bitstring, count in sorted_counts[:10]:
        measured = int(bitstring, 2)
        phase = extract_phase(measured, precision_bits)
        pct = 100 * count / shots
        
        # Use continued fractions to find k/r
        if measured > 0:
            frac = Fraction(measured, 2 ** precision_bits).limit_denominator(period * 2)
            period_str = f"{frac.numerator}/{frac.denominator}"
            key = f"{frac.numerator}/{frac.denominator}"
            phase_stats[key] = phase_stats.get(key, 0) + count
        else:
            period_str = "-"
        
        print(f"{bitstring:<12} {count:<8} {pct:<7.2f}% {measured:<8} {phase:<12.6f} {period_str:<12}")
    
    # Check if we found the correct period
    print(f"\nPhase fractions found:")
    for key, count in sorted(phase_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
        pct = 100 * count / shots
        print(f"  {key}: {count} ({pct:.2f}%)")
        # Check if denominator matches expected period
        if "/" in key:
            _, denom = map(int, key.split("/"))
            if denom == period:
                print(f"    ✅ Found expected period r = {period}!")
    
    print(f"\n{'='*70}")
    return counts


if __name__ == "__main__":
    test_qpe()

