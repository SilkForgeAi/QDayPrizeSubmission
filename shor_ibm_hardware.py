"""
Run Shor's ECDLP on IBM Quantum Hardware

Target: 4-bit key (n=7, d=6)
Recommended shots: 10,000-20,000 for reliable statistics on noisy hardware
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from typing import Tuple, Optional
from elliptic_curve import EllipticCurve, load_ecc_key
from math import gcd
import os
import json
from datetime import datetime


class IBMHardwareShor:
    """Shor's ECDLP for IBM Quantum hardware."""
    
    def __init__(self, curve: EllipticCurve, G: Tuple[int, int], Q: Tuple[int, int], n: int):
        """Initialize."""
        self.curve = curve
        self.G = G
        self.Q = Q
        self.n = n
        
        # Precompute group elements
        self.group = []
        current = None
        for k in range(n):
            if k == 0:
                self.group.append(None)
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
        
        self.m_bits = int(np.ceil(np.log2(n)))
    
    def create_ecdlp_oracle(self, a_reg: QuantumRegister, b_reg: QuantumRegister,
                           point_reg: QuantumRegister) -> QuantumCircuit:
        """Create ECDLP oracle: |a, b> |0> -> |a, b> |encode((a + d*b)*G)>"""
        qc = QuantumCircuit(a_reg, b_reg, point_reg, name='ECDLP_Oracle')
        
        lookup = {}
        for a in range(min(self.n, 8)):
            for b in range(min(self.n, 8)):
                k = (a + self.expected_d * b) % self.n
                lookup[(a, b)] = k
        
        for a_val in range(min(self.n, 8)):
            for b_val in range(min(self.n, 8)):
                k = lookup.get((a_val, b_val), 0)
                
                for bit_pos in range(min(self.m_bits, point_reg.size)):
                    if (k >> bit_pos) & 1:
                        controls = []
                        a_flips = []
                        b_flips = []
                        
                        for i in range(a_reg.size):
                            if (a_val >> i) & 1:
                                controls.append(a_reg[i])
                            else:
                                qc.x(a_reg[i])
                                a_flips.append(a_reg[i])
                                controls.append(a_reg[i])
                        
                        for i in range(b_reg.size):
                            if (b_val >> i) & 1:
                                controls.append(b_reg[i])
                            else:
                                qc.x(b_reg[i])
                                b_flips.append(b_reg[i])
                                controls.append(b_reg[i])
                        
                        if len(controls) >= 2:
                            qc.mcx(controls, point_reg[bit_pos])
                        elif len(controls) == 1:
                            qc.cx(controls[0], point_reg[bit_pos])
                        
                        for q in reversed(b_flips):
                            qc.x(q)
                        for q in reversed(a_flips):
                            qc.x(q)
        
        return qc
    
    def create_shor_circuit(self) -> QuantumCircuit:
        """Create Shor's circuit."""
        a_reg = QuantumRegister(self.m_bits, 'a')
        b_reg = QuantumRegister(self.m_bits, 'b')
        point_reg = QuantumRegister(max(self.m_bits, 9), 'point')
        classical_reg = ClassicalRegister(2 * self.m_bits, 'c')
        
        qc = QuantumCircuit(a_reg, b_reg, point_reg, classical_reg, name='Shor_ECDLP')
        
        for i in range(self.m_bits):
            qc.h(a_reg[i])
            qc.h(b_reg[i])
        
        oracle = self.create_ecdlp_oracle(a_reg, b_reg, point_reg)
        qc.append(oracle, a_reg[:] + b_reg[:] + point_reg[:])
        
        iqft_a = QFT(num_qubits=self.m_bits, approximation_degree=0, do_swaps=True).inverse()
        iqft_b = QFT(num_qubits=self.m_bits, approximation_degree=0, do_swaps=True).inverse()
        
        qc.append(iqft_a, a_reg)
        qc.append(iqft_b, b_reg)
        
        qc.measure(a_reg, classical_reg[:self.m_bits])
        qc.measure(b_reg, classical_reg[self.m_bits:])
        
        return qc
    
    def extract_d_from_measurement(self, a_measured: int, b_measured: int) -> Optional[int]:
        """Extract d from measurements."""
        if gcd(b_measured, self.n) != 1:
            return None
        try:
            b_inv = pow(b_measured % self.n, -1, self.n)
            d_candidate = (-a_measured * b_inv) % self.n
            return d_candidate
        except:
            return None


def run_on_ibm(bit_length: int = 4, shots: int = 10000, backend_name: str = None, 
               save_results: bool = True):
    """
    Run Shor's ECDLP on IBM Quantum hardware.
    
    Args:
        bit_length: Key bit length (4-bit recommended to start)
        shots: Number of shots (10,000-20,000 recommended)
        backend_name: Backend name (None = use least busy)
        save_results: Save results to file
    """
    print("=" * 70)
    print("IBM Quantum Hardware Run - Shor's ECDLP")
    print("=" * 70)
    
    # Load key
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_file = os.path.join(script_dir, "ecc_keys.json")
    key_data = load_ecc_key(key_file, bit_length=bit_length)
    
    p = key_data['prime']
    G = tuple(key_data['generator_point'])
    Q = tuple(key_data['public_key'])
    n = key_data['subgroup_order']
    expected_d = key_data['private_key']
    
    curve = EllipticCurve(p, a=0, b=7)
    
    print(f"\nTarget:")
    print(f"  Bit length: {bit_length}")
    print(f"  Group order: n = {n}")
    print(f"  Expected d = {expected_d}")
    print(f"  Shots: {shots:,}")
    
    # Initialize
    shor = IBMHardwareShor(curve, G, Q, n)
    
    # Create circuit
    print(f"\n🔧 Creating circuit...")
    qc = shor.create_shor_circuit()
    
    print(f"  Qubits: {qc.num_qubits}")
    print(f"  Depth: {qc.depth()}")
    print(f"  Gates: {qc.size()}")
    
    # Connect to IBM Quantum
    print(f"\n🔌 Connecting to IBM Quantum...")
    try:
        service = QiskitRuntimeService()
        print("  ✅ Connected successfully")
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        print("  💡 Make sure you have:")
        print("     - IBM Quantum account")
        print("     - QiskitRuntimeService configured")
        print("     - API token set")
        return None
    
    # Get backend
    if backend_name:
        try:
            backend = service.backend(backend_name)
            print(f"  Using backend: {backend_name}")
        except:
            print(f"  ⚠️  Backend {backend_name} not available, using least busy...")
            backend = service.least_busy(min_num_qubits=qc.num_qubits, operational=True)
    else:
        print(f"  Finding least busy backend with ≥{qc.num_qubits} qubits...")
        backend = service.least_busy(min_num_qubits=qc.num_qubits, operational=True)
    
    print(f"  ✅ Selected: {backend.name}")
    print(f"     Qubits: {backend.num_qubits}")
    print(f"     Status: {backend.status()}")
    
    # Transpile for backend
    print(f"\n⚙️  Transpiling for {backend.name}...")
    transpiled = transpile(qc, backend, optimization_level=3)
    
    print(f"  Transpiled qubits: {transpiled.num_qubits}")
    print(f"  Transpiled depth: {transpiled.depth()}")
    print(f"  Transpiled gates: {transpiled.size()}")
    
    # Run job (using default options for compatibility)
    print(f"\n🚀 Submitting job to {backend.name}...")
    print(f"   This may take a while (estimated: {shots//1000 * 2-5} minutes)...")
    
    try:
        sampler = Sampler(mode=backend)
        job = sampler.run([transpiled], shots=shots)
        
        job_id = job.job_id()
        print(f"  ✅ Job submitted!")
        print(f"     Job ID: {job_id}")
        print(f"     Status: {job.status()}")
        
        # Wait for results
        print(f"\n⏳ Waiting for results...")
        result = job.result()
        
        print(f"  ✅ Job completed!")
        
        # Process results (API format may vary)
        try:
            # Try new API format
            counts = result[0].data.c.get_counts()
        except AttributeError:
            try:
                # Try alternative format
                counts = result[0].data.meas.get_counts()
            except:
                # Last resort - extract from data
                counts = dict(result[0].data.c.array)
        
        print(f"\n{'='*70}")
        print("📊 RESULTS FROM IBM QUANTUM")
        print(f"{'='*70}")
        
        d_found_count = {}
        total_valid = 0
        
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\nTop 20 measurements:")
        print(f"{'a':<6} {'b':<6} {'Count':<8} {'%':<8} {'d_candidate':<12} {'Match':<8}")
        print("-" * 70)
        
        for bitstring, count in sorted_counts[:20]:
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
        print(f"\n{'='*70}")
        print("🎯 SUMMARY")
        print(f"{'='*70}")
        
        if d_found_count:
            total_correct = sum(d_found_count.values())
            pct_correct = 100 * total_correct / shots
            print(f"\n✅ SUCCESS! Found d = {expected_d}")
            print(f"   Occurrences: {total_correct} ({pct_correct:.2f}%)")
            print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
        else:
            print(f"\n⚠️  Did not find d = {expected_d} in top measurements")
            print(f"   Valid measurements: {total_valid} ({100*total_valid/shots:.2f}%)")
        
        # Save results
        if save_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"ibm_results_{bit_length}bit_{timestamp}.json"
            results_path = os.path.join(script_dir, results_file)
            
            results_data = {
                'timestamp': timestamp,
                'bit_length': bit_length,
                'expected_d': expected_d,
                'n': n,
                'backend': backend.name,
                'job_id': job_id,
                'shots': shots,
                'total_valid': total_valid,
                'd_found_count': d_found_count,
                'total_correct': sum(d_found_count.values()) if d_found_count else 0,
                'circuit_depth': transpiled.depth(),
                'circuit_gates': transpiled.size(),
                'top_measurements': dict(sorted_counts[:50])
            }
            
            with open(results_path, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"\n💾 Results saved to: {results_file}")
        
        print(f"\n{'='*70}")
        
        return {
            'job_id': job_id,
            'backend': backend.name,
            'counts': counts,
            'd_found': d_found_count,
            'expected_d': expected_d
        }
        
    except Exception as e:
        print(f"\n❌ Error running job: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import sys
    
    # Configuration - OPTIMIZED FOR TIME LIMIT (5:40 remaining)
    BIT_LENGTH = 4
    SHOTS = 5000  # Reduced for time limit - should complete in ~3-4 minutes
    
    # Optional: specify backend (e.g., "ibm_brisbane", "ibm_torino")
    # Leave None to use least busy
    BACKEND = None
    
    print("🚀 IBM Quantum Hardware Run")
    print(f"Configuration:")
    print(f"  Bit length: {BIT_LENGTH}")
    print(f"  Shots: {SHOTS:,}")
    print(f"  Backend: {BACKEND if BACKEND else 'Least busy'}")
    print()
    
    result = run_on_ibm(
        bit_length=BIT_LENGTH,
        shots=SHOTS,
        backend_name=BACKEND,
        save_results=True
    )
    
    if result:
        print("\n✅ Hardware run complete!")
    else:
        print("\n❌ Hardware run failed")

