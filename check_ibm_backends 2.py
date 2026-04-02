"""
Check IBM Quantum backends for 6-bit ECDLP
"""

from qiskit_ibm_runtime import QiskitRuntimeService
import sys

try:
    service = QiskitRuntimeService()
    print("=" * 70)
    print("Available IBM Quantum Backends")
    print("=" * 70)
    
    # Get all operational backends
    backends = service.backends(simulator=False, operational=True)
    
    target_backends = ['ibm_kyiv', 'ibm_sherbrooke', 'ibm_torino', 'ibm_brisbane']
    
    print("\nTarget Backends (for 6-bit ECDLP):")
    print("-" * 70)
    
    backend_info = {}
    
    for backend_name in target_backends:
        try:
            backend = service.backend(backend_name)
            status = backend.status()
            
            # Get properties
            props = backend.properties()
            
            # Calculate average gate errors
            gate_errors = []
            for gate in props.gates:
                for param in gate.parameters:
                    if param.name == 'gate_error':
                        gate_errors.append(param.value)
            
            avg_gate_error = sum(gate_errors) / len(gate_errors) if gate_errors else 0
            
            # Average readout errors
            readout_errors = []
            for qubit in props.qubits:
                for param in qubit:
                    if param.name == 'readout_error':
                        readout_errors.append(param.value)
            
            avg_readout_error = sum(readout_errors) / len(readout_errors) if readout_errors else 0
            
            backend_info[backend_name] = {
                'available': True,
                'qubits': backend.num_qubits,
                'status': status.status_msg,
                'pending_jobs': status.pending_jobs,
                'avg_gate_error': avg_gate_error,
                'avg_readout_error': avg_readout_error,
                'total_error': avg_gate_error + avg_readout_error
            }
            
            print(f"\n{backend_name}:")
            print(f"  Qubits: {backend.num_qubits}")
            print(f"  Status: {status.status_msg}")
            print(f"  Queue: {status.pending_jobs} jobs")
            print(f"  Avg gate error: {avg_gate_error:.4f}")
            print(f"  Avg readout error: {avg_readout_error:.4f}")
            print(f"  Total error (lower is better): {avg_gate_error + avg_readout_error:.4f}")
            
        except Exception as e:
            backend_info[backend_name] = {'available': False, 'error': str(e)}
            print(f"\n{backend_name}: Not available ({e})")
    
    # Recommendation
    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    
    available = {k: v for k, v in backend_info.items() if v.get('available', False)}
    
    if available:
        # Sort by total error (lower is better)
        sorted_backends = sorted(available.items(), key=lambda x: x[1].get('total_error', 100))
        
        print("\nBackend ranking (by error rate):")
        for i, (name, info) in enumerate(sorted_backends, 1):
            error = info.get('total_error', 0)
            queue = info.get('pending_jobs', 0)
            print(f"  {i}. {name}: error={error:.4f}, queue={queue}")
        
        best = sorted_backends[0][0]
        best_info = sorted_backends[0][1]
        
        print(f"\n✅ Recommended: {best}")
        print(f"   Lowest total error: {best_info.get('total_error', 0):.4f}")
        print(f"   Queue: {best_info.get('pending_jobs', 0)} jobs")
        print(f"   Good for 6-bit ECDLP (~25 qubits needed)")
    else:
        print("\n⚠️  No target backends available")
        print("   Will use least busy backend with ≥25 qubits")
    
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

