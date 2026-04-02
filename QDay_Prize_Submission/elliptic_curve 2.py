"""
Classical Elliptic Curve Operations for ECDLP
Used for validation and understanding the problem structure.
"""

from typing import Tuple, Optional, List
import json


class EllipticCurve:
    """
    Elliptic curve over finite field F_p: y^2 = x^3 + ax + b (mod p)
    For QDay competition, curves use standard form with a=0, b=7 (y^2 = x^3 + 7)
    """
    
    def __init__(self, p: int, a: int = 0, b: int = 7, generator: Optional[Tuple[int, int]] = None):
        """
        Initialize elliptic curve.
        
        Args:
            p: Prime field modulus
            a: Curve parameter a (default 0 for competition curves)
            b: Curve parameter b (default 7 for competition curves)
            generator: Generator point [x, y] (optional, for verification)
        """
        self.p = p
        self.a = a
        self.b = b
            
        # Verify generator is on curve if provided
        if generator:
            if not self.is_on_curve(generator):
                raise ValueError(f"Generator {generator} is not on curve y^2 = x^3 + {a}x + {b} (mod {p})")
    
    def is_on_curve(self, point: Tuple[int, int]) -> bool:
        """Check if point (x, y) is on the curve."""
        if point is None:
            return True  # Point at infinity
        x, y = point
        lhs = (y**2) % self.p
        rhs = (x**3 + self.a * x + self.b) % self.p
        return lhs == rhs
    
    def point_add(self, P: Optional[Tuple[int, int]], Q: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        Add two points on the elliptic curve.
        Returns point at infinity (None) if result is identity.
        """
        # Point at infinity is identity
        if P is None:
            return Q
        if Q is None:
            return P
        
        x1, y1 = P
        x2, y2 = Q
        
        # Same point: use point doubling
        if P == Q:
            return self.point_double(P)
        
        # Vertical line: result is point at infinity
        if x1 == x2:
            return None
        
        # Calculate slope
        delta_x = (x2 - x1) % self.p
        delta_y = (y2 - y1) % self.p
        inv_delta_x = self.mod_inverse(delta_x, self.p)
        s = (delta_y * inv_delta_x) % self.p
        
        # Calculate result point
        x3 = (s**2 - x1 - x2) % self.p
        y3 = (s * (x1 - x3) - y1) % self.p
        
        return (x3, y3)
    
    def point_double(self, P: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Double a point on the elliptic curve (2P = P + P)."""
        if P is None:
            return None
        
        x, y = P
        
        # Vertical tangent: result is point at infinity
        if y == 0:
            return None
        
        # Calculate slope
        numerator = (3 * x**2 + self.a) % self.p
        denominator = (2 * y) % self.p
        inv_denom = self.mod_inverse(denominator, self.p)
        s = (numerator * inv_denom) % self.p
        
        # Calculate result point
        x3 = (s**2 - 2 * x) % self.p
        y3 = (s * (x - x3) - y) % self.p
        
        return (x3, y3)
    
    def scalar_multiply(self, k: int, P: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Compute k * P using binary method.
        Returns point at infinity if k = 0 mod order.
        """
        if k == 0:
            return None
        
        # Handle negative k
        if k < 0:
            k = -k
            P = self.point_negate(P)
        
        result = None
        addend = P
        
        while k > 0:
            if k & 1:
                result = self.point_add(result, addend)
            addend = self.point_double(addend)
            k >>= 1
        
        return result
    
    def point_negate(self, P: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """Negate a point: -P = (x, -y mod p)."""
        if P is None:
            return None
        x, y = P
        return (x, (-y) % self.p)
    
    @staticmethod
    def mod_inverse(a: int, m: int) -> int:
        """Compute modular inverse using extended Euclidean algorithm."""
        if a == 0:
            raise ValueError("Cannot compute inverse of 0")
        
        def ext_gcd(a: int, b: int) -> Tuple[int, int, int]:
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = ext_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, _ = ext_gcd(a % m, m)
        if gcd != 1:
            raise ValueError(f"Inverse of {a} mod {m} does not exist")
        return (x % m + m) % m


def load_ecc_key(filename: str = "ecc_keys.json", bit_length: Optional[int] = None) -> dict:
    """
    Load ECC key from JSON file.
    
    Args:
        filename: Path to ECC keys file
        bit_length: Specific bit length to load (if None, returns all)
    
    Returns:
        Dictionary with key parameters or list of all keys
    """
    with open(filename, 'r') as f:
        keys = json.load(f)
    
    if bit_length:
        for key in keys:
            if key['bit_length'] == bit_length:
                return key
        raise ValueError(f"Key with bit_length {bit_length} not found")
    
    return keys


def solve_ecdlp_classical(curve: EllipticCurve, G: Tuple[int, int], Q: Tuple[int, int], n: int) -> Optional[int]:
    """
    Solve ECDLP classically using brute force: find k such that Q = k*G.
    Only works for small orders n.
    
    Args:
        curve: Elliptic curve
        G: Generator point
        Q: Public key point
        n: Subgroup order (maximum possible k)
    
    Returns:
        Private key k if found, None otherwise
    """
    # Verify Q is on curve
    if not curve.is_on_curve(Q):
        raise ValueError("Q is not on the curve")
    
    # Try all possible k values
    for k in range(1, min(n, 10000)):  # Limit for safety
        kG = curve.scalar_multiply(k, G)
        if kG == Q:
            return k
        if kG is None:
            continue
    
    return None


def verify_key_solution(curve: EllipticCurve, G: Tuple[int, int], Q: Tuple[int, int], k: int) -> bool:
    """Verify that k*G = Q."""
    kG = curve.scalar_multiply(k, G)
    return kG == Q


if __name__ == "__main__":
    # Test with 4-bit key
    print("Testing classical ECC operations with 4-bit key...")
    
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_file = os.path.join(script_dir, "ecc_keys.json")
    key_data = load_ecc_key(key_file, bit_length=4)
    print(f"\nKey data: {key_data}")
    
    p = key_data['prime']
    G = tuple(key_data['generator_point'])
    Q = tuple(key_data['public_key'])
    n = key_data['subgroup_order']
    expected_k = key_data['private_key']
    
    # Create curve
    curve = EllipticCurve(p, generator=G)
    print(f"\nCurve: y^2 = x^3 + {curve.a}x + {curve.b} (mod {p})")
    print(f"Generator G = {G}")
    print(f"Public key Q = {Q}")
    print(f"Subgroup order n = {n}")
    print(f"Expected private key k = {expected_k}")
    
    # Verify generator is on curve
    print(f"G on curve: {curve.is_on_curve(G)}")
    print(f"Q on curve: {curve.is_on_curve(Q)}")
    
    # Test scalar multiplication
    test_kG = curve.scalar_multiply(expected_k, G)
    print(f"\nk*G = {test_kG}")
    print(f"Q == k*G: {test_kG == Q}")
    
    # Solve ECDLP classically
    print("\nSolving ECDLP classically (brute force)...")
    found_k = solve_ecdlp_classical(curve, G, Q, n)
    print(f"Found k = {found_k}")
    print(f"Correct: {found_k == expected_k}")

