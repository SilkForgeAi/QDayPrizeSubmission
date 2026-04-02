"""
Quick IBM Quantum Run - Optimized for time limit
5,000 shots to complete in ~3-4 minutes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shor_ibm_hardware import run_on_ibm

if __name__ == "__main__":
    print("⚡ QUICK RUN - Optimized for time limit")
    print("=" * 70)
    print("Configuration:")
    print("  Shots: 5,000 (optimized for ~5 minute runtime)")
    print("  Expected: ~50-100 correct results (1-2% success)")
    print("=" * 70)
    print()
    
    result = run_on_ibm(
        bit_length=4,
        shots=5000,  # Reduced for time limit
        backend_name=None,  # Use least busy
        save_results=True
    )
    
    if result:
        print("\n✅ Quick run complete!")
        if result.get('d_found'):
            print(f"🎉 Found d={result['expected_d']} on IBM Quantum hardware!")
    else:
        print("\n❌ Run failed - check connection/credentials")

