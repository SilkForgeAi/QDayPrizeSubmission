"""
Verify all ECC keys using the correct curve equation: y^2 = x^3 + 7 mod p
"""

from elliptic_curve import EllipticCurve, load_ecc_key
import os


def verify_key(bit_length: int) -> bool:
    """Verify a single key - check that d*G = Q."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_file = os.path.join(script_dir, "ecc_keys.json")
    
    try:
        key_data = load_ecc_key(key_file, bit_length=bit_length)
    except ValueError:
        print(f"Key with bit_length {bit_length} not found")
        return False
    
    p = key_data['prime']
    G = tuple(key_data['generator_point'])
    Q = tuple(key_data['public_key'])
    n = key_data['subgroup_order']
    expected_d = key_data['private_key']
    
    # Create curve with a=0, b=7
    curve = EllipticCurve(p, a=0, b=7)
    
    # Verify points are on curve
    if not curve.is_on_curve(G):
        print(f"  ❌ Generator G is not on curve")
        return False
    if not curve.is_on_curve(Q):
        print(f"  ❌ Public key Q is not on curve")
        return False
    
    # Verify d*G = Q
    dG = curve.scalar_multiply(expected_d, G)
    if dG != Q:
        print(f"  ❌ {expected_d}*G = {dG} ≠ Q = {Q}")
        return False
    
    # Verify order
    nG = curve.scalar_multiply(n, G)
    if nG is not None:
        print(f"  ⚠️  {n}*G = {nG} (should be None/identity)")
        # Don't fail on this, just warn
    
    print(f"  ✅ Verified: {expected_d}*G = Q")
    return True


def verify_all_keys():
    """Verify all available keys."""
    print("Verifying all ECC keys...")
    print("=" * 60)
    
    # Available bit lengths from the JSON
    bit_lengths = [4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    
    success_count = 0
    for bit_length in bit_lengths:
        print(f"\n--- Bit length {bit_length} ---")
        if verify_key(bit_length):
            success_count += 1
        else:
            print(f"  ❌ Verification failed for {bit_length}-bit key")
    
    print("\n" + "=" * 60)
    print(f"Verified {success_count}/{len(bit_lengths)} keys successfully")
    return success_count == len(bit_lengths)


if __name__ == "__main__":
    verify_all_keys()

