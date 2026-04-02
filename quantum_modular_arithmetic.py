"""
Quantum modular arithmetic building blocks for scalable ECDLP oracles.

This module provides reversible circuits for:
- Adding a constant modulo 2^n (via ModularAdderGate)
- Comparing a register to a constant (IntegerComparator)
- Adding a constant modulo N (conditional subtraction)
- Multiplying a register by a constant modulo N (double-and-add)

These are intended as primitives for a future full ECDLP oracle
that avoids classical lookup tables and scales to 9/10-bit and beyond.
"""

from __future__ import annotations

from typing import Tuple

from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from qiskit.circuit.library import ModularAdderGate, IntegerComparator


def _prepare_constant(qc: QuantumCircuit, const_reg: QuantumRegister, value: int) -> None:
    """Prepare a constant value into const_reg using X gates."""
    for i in range(const_reg.size):
        if (value >> i) & 1:
            qc.x(const_reg[i])


def build_add_const_mod_2n(n_bits: int, const: int, name: str | None = None) -> QuantumCircuit:
    """
    Build a circuit that adds a constant to a target register modulo 2^n.

    Registers:
    - const (n_bits): prepared to |const>
    - target (n_bits): target register (updated in place)

    The const register remains unchanged, so it can be reused.
    """
    const_reg = QuantumRegister(n_bits, "const")
    target = QuantumRegister(n_bits, "x")
    qc = QuantumCircuit(const_reg, target, name=name or f"add_{const}_mod_2n")

    _prepare_constant(qc, const_reg, const)
    qc.append(ModularAdderGate(n_bits), const_reg[:] + target[:])

    return qc


def build_compare_geq_const(n_bits: int, const: int, name: str | None = None) -> QuantumCircuit:
    """
    Build a comparator circuit that sets flag if state >= const.

    Registers:
    - state (n_bits)
    - flag (1)
    - ancilla (n_bits - 1)
    """
    state = QuantumRegister(n_bits, "state")
    flag = QuantumRegister(1, "flag")
    anc = AncillaRegister(max(0, n_bits - 1), "anc")
    qc = QuantumCircuit(state, flag, anc, name=name or f"geq_{const}")

    cmp_gate = IntegerComparator(n_bits, value=const, geq=True)
    qc.append(cmp_gate, state[:] + flag[:] + anc[:])

    return qc


def build_add_const_mod_n(n_bits: int, modulus: int, const: int, name: str | None = None) -> QuantumCircuit:
    """
    Build a circuit that adds a constant modulo an arbitrary modulus N.

    This computes: x <- (x + const) mod N, assuming 0 <= x < N.

    Strategy:
    1) x <- x + const (mod 2^n)
    2) flag <- [x >= N]
    3) if flag: x <- x - N  (add 2^n - N mod 2^n)
    4) uncompute flag

    Registers:
    - x (n_bits): target register
    - flag (1)
    - anc (n_bits - 1)
    - const_add (n_bits): prepared to |const>
    - const_sub (n_bits): prepared to |(2^n - N)>
    """
    if modulus <= 0 or modulus >= (1 << n_bits):
        raise ValueError("modulus must satisfy 0 < modulus < 2^n")

    x = QuantumRegister(n_bits, "x")
    flag = QuantumRegister(1, "flag")
    anc = AncillaRegister(max(0, n_bits - 1), "anc")
    const_add = QuantumRegister(n_bits, "c_add")
    const_sub = QuantumRegister(n_bits, "c_sub")

    qc = QuantumCircuit(x, flag, anc, const_add, const_sub, name=name or f"add_{const}_mod_{modulus}")

    # Prepare constants
    _prepare_constant(qc, const_add, const)
    _prepare_constant(qc, const_sub, (1 << n_bits) - modulus)

    # Step 1: x <- x + const (mod 2^n)
    qc.append(ModularAdderGate(n_bits), const_add[:] + x[:])

    # Step 2: flag <- [x >= modulus]
    cmp_gate = IntegerComparator(n_bits, value=modulus, geq=True)
    qc.append(cmp_gate, x[:] + flag[:] + anc[:])

    # Step 3: if flag: x <- x - modulus  (add 2^n - modulus mod 2^n)
    sub_gate = ModularAdderGate(n_bits).control(1)
    qc.append(sub_gate, flag[:] + const_sub[:] + x[:])

    # Step 4: uncompute comparator
    qc.append(cmp_gate.inverse(), x[:] + flag[:] + anc[:])

    return qc


def build_mul_const_mod_n(n_bits: int, modulus: int, const: int, name: str | None = None) -> QuantumCircuit:
    """
    Build a circuit that multiplies a register by a constant modulo N.

    Computes: out <- (in * const) mod N

    Registers:
    - inp (n_bits)
    - out (n_bits) (initialized to |0>)
    - flag (1)
    - anc (n_bits - 1)
    - const_add_i (n_bits) for each bit i
    - const_sub_i (n_bits) for each bit i

    This uses a double-and-add approach with modular addition by constants.
    """
    if modulus <= 0 or modulus >= (1 << n_bits):
        raise ValueError("modulus must satisfy 0 < modulus < 2^n")

    inp = QuantumRegister(n_bits, "inp")
    out = QuantumRegister(n_bits, "out")
    flag = QuantumRegister(1, "flag")
    anc = AncillaRegister(max(0, n_bits - 1), "anc")

    const_add_regs = [QuantumRegister(n_bits, f"c_add_{i}") for i in range(n_bits)]
    const_sub_regs = [QuantumRegister(n_bits, f"c_sub_{i}") for i in range(n_bits)]

    qc = QuantumCircuit(inp, out, flag, anc, *const_add_regs, *const_sub_regs,
                        name=name or f"mul_{const}_mod_{modulus}")

    # Precompute constant for each bit position (const * 2^i mod N)
    add_values = [(const * (1 << i)) % modulus for i in range(n_bits)]

    for i, add_const in enumerate(add_values):
        const_add = const_add_regs[i]
        const_sub = const_sub_regs[i]

        _prepare_constant(qc, const_add, add_const)
        _prepare_constant(qc, const_sub, (1 << n_bits) - modulus)

        # Controlled add to out if inp[i] is 1
        add_gate = ModularAdderGate(n_bits).control(1)
        qc.append(add_gate, [inp[i]] + const_add[:] + out[:])

        # Compare and conditionally subtract modulus to keep in range
        cmp_gate = IntegerComparator(n_bits, value=modulus, geq=True)
        qc.append(cmp_gate, out[:] + flag[:] + anc[:])
        sub_gate = ModularAdderGate(n_bits).control(1)
        qc.append(sub_gate, flag[:] + const_sub[:] + out[:])
        qc.append(cmp_gate.inverse(), out[:] + flag[:] + anc[:])

    return qc


if __name__ == "__main__":
    # Smoke build only (no simulation)
    for n_bits, modulus, const in [(4, 13, 3), (5, 17, 7)]:
        add_circ = build_add_const_mod_n(n_bits, modulus, const)
        mul_circ = build_mul_const_mod_n(n_bits, modulus, const)
        print(f"add_mod_n({n_bits}, {modulus}, {const}): qubits={add_circ.num_qubits}, depth={add_circ.depth()}")
        print(f"mul_mod_n({n_bits}, {modulus}, {const}): qubits={mul_circ.num_qubits}, depth={mul_circ.depth()}")
