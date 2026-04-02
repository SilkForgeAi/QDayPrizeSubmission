"""
Basic Oracle Test - Verify controlled operations work correctly
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit import transpile

# Test: Simple oracle |x> |0> -> |x> |f(x)>
# f(x) = x mod 4 for x in [0, 3]

def create_test_oracle():
    """Create a simple test oracle."""
    x_reg = QuantumRegister(2, 'x')  # 2 qubits for 0-3
    y_reg = QuantumRegister(2, 'y')  # 2 qubits for output
    cr = ClassicalRegister(4, 'c')
    
    qc = QuantumCircuit(x_reg, y_reg, cr)
    
    # Initialize x in superposition
    qc.h(x_reg[0])
    qc.h(x_reg[1])
    
    # Oracle: f(x) = x (identity for testing)
    # When x == 0, set y = 0
    # When x == 1, set y = 1
    # When x == 2, set y = 2
    # When x == 3, set y = 3
    
    # For x == 1 (binary 01), set y = 1
    qc.x(x_reg[0])  # Flip to control on |0>
    qc.ccx(x_reg[0], x_reg[1], y_reg[0])  # If x == 01, set y[0]
    qc.x(x_reg[0])  # Restore
    
    # For x == 2 (binary 10), set y = 2
    qc.x(x_reg[1])
    qc.ccx(x_reg[0], x_reg[1], y_reg[1])  # If x == 10, set y[1]
    qc.x(x_reg[1])
    
    # For x == 3 (binary 11), set y = 3
    qc.ccx(x_reg[0], x_reg[1], y_reg[0])  # Set y[0]
    qc.ccx(x_reg[0], x_reg[1], y_reg[1])  # Set y[1]
    
    # Measure
    qc.measure(x_reg, cr[:2])
    qc.measure(y_reg, cr[2:])
    
    return qc

print("Testing basic oracle...")
qc = create_test_oracle()

simulator = AerSimulator()
transpiled = transpile(qc, simulator)
job = simulator.run(transpiled, shots=1024)
result = job.result()
counts = result.get_counts()

print("\nResults:")
for bitstring, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    x_str = bitstring[:2]
    y_str = bitstring[2:]
    x_val = int(x_str, 2)
    y_val = int(y_str, 2)
    print(f"  x={x_val:2d} (binary {x_str}) -> y={y_val:2d} (binary {y_str}): {count}")

print("\n✅ Basic oracle test complete!")

