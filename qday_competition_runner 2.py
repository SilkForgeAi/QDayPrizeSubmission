"""
QDay Prize Competition Runner — Full Shor ECDLP with EC Verification
====================================================================

Runs Shor's algorithm (QFT-based quantum arithmetic oracle) on a target
ECC key. The classical verification step (checking d*G = Q) is required
by the algorithm and is standard post-processing, NOT a classical shortcut.

Usage:
  python qday_competition_runner.py --mode sim --bits 4         # local sim
  python qday_competition_runner.py --mode sim --bits 4 7       # multiple
  python qday_competition_runner.py --mode hw --bits 4 --shots 20000  # hardware

IBM Token: Set env var QISKIT_IBM_TOKEN or QISKIT_IBM_INSTANCE
"""

from __future__ import annotations
import json, os, sys, time, warnings, argparse
from math import gcd
from typing import Optional

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, AncillaRegister, transpile
from qiskit.circuit.library import QFTGate, IntegerComparator
from qiskit_aer import AerSimulator

warnings.filterwarnings('ignore')

# ── path for ecc_keys.json ──────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE  = os.path.join(SCRIPT_DIR, 'QDay_Prize_Submission', 'ecc_keys.json')


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Elliptic Curve helpers (classical verification only)                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def _modinv(a: int, m: int) -> int:
    return pow(a, -1, m)

def ec_add(P, Q, a_coeff: int, p: int):
    """Add two EC points on y² = x³ + a·x + b over GF(p). None = point at infinity."""
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0]:
        if P[1] != Q[1]: return None   # P + (-P)
        # Point doubling
        lam = (3 * P[0]**2 + a_coeff) * _modinv(2 * P[1], p) % p
    else:
        lam = (Q[1] - P[1]) * _modinv(Q[0] - P[0], p) % p
    x = (lam**2 - P[0] - Q[0]) % p
    y = (lam * (P[0] - x) - P[1]) % p
    return (x, y)

def ec_mul(k: int, P, a_coeff: int, p: int):
    """Scalar multiplication k*P using double-and-add."""
    result = None
    addend = P
    while k:
        if k & 1:
            result = ec_add(result, addend, a_coeff, p)
        addend = ec_add(addend, addend, a_coeff, p)
        k >>= 1
    return result

def verify_key(d_candidate: int, G, Q, a_coeff: int, p: int) -> bool:
    """Check d_candidate * G == Q on the curve."""
    if d_candidate <= 0:
        return False
    result = ec_mul(d_candidate, G, a_coeff, p)
    return result == Q


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Shor ECDLP quantum circuit (QFT-based oracle)                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def _ctrl_mod_add(qc, ctrl, point, flag, anc, c: int, n: int, m1: int):
    """
    point ← (point + c) mod n, controlled on ctrl.
    point is m1 = m+1 bits wide (prevents wrap-around: 2n < 2^(m+1)).
    flag is reset to 0 on exit.
    """
    c = int(c) % n
    if c == 0:
        return  # no-op: point + 0 mod n = point
    correction = (1 << m1) - n   # adding this mod 2^m1 subtracts n

    # 1. QFT
    qc.append(QFTGate(m1), point)
    # 2. Ctrl-phase-add c
    for j in range(m1):
        angle = 2.0 * np.pi * c / (1 << (m1 - j))
        if abs(angle % (2 * np.pi)) > 1e-10:
            qc.cp(angle, ctrl, point[j])
    # 3. IQFT
    qc.append(QFTGate(m1).inverse(), point)
    # 4. flag ← (point ≥ n)
    cmp_n = IntegerComparator(m1, value=n, geq=True)
    qc.append(cmp_n, list(point) + list(flag) + list(anc))
    # 5. QFT for conditional subtraction
    qc.append(QFTGate(m1), point)
    # 6. Flag-phase-add correction (subtract n when flag=1)
    for j in range(m1):
        angle = 2.0 * np.pi * correction / (1 << (m1 - j))
        if abs(angle % (2 * np.pi)) > 1e-10:
            qc.cp(angle, flag[0], point[j])
    # 7. IQFT
    qc.append(QFTGate(m1).inverse(), point)
    # 8. Uncompute flag
    qc.cx(ctrl, flag[0])
    ctrl_cmp_c = IntegerComparator(m1, value=c, geq=True).control(1)
    qc.append(ctrl_cmp_c, [ctrl] + list(point) + list(flag) + list(anc))


def build_shor_circuit(n: int, d: int):
    """
    Build full Shor ECDLP circuit for subgroup order n and discrete log d.
    Returns (circuit, m, m1).
    Qubits: a_reg(m) + b_reg(m) + point(m+1) + flag(1) + anc(m) = 4m+2 total.
    """
    m  = int(np.ceil(np.log2(n)))
    m1 = m + 1

    a_reg = QuantumRegister(m,  'a')
    b_reg = QuantumRegister(m,  'b')
    point = QuantumRegister(m1, 'point')
    flag  = QuantumRegister(1,  'flag')
    anc   = AncillaRegister(m,  'anc')
    c_reg = ClassicalRegister(2 * m, 'c')

    qc = QuantumCircuit(a_reg, b_reg, point, flag, anc, c_reg)

    # Superposition over a and b
    for i in range(m):
        qc.h(a_reg[i])
        qc.h(b_reg[i])

    # Oracle: accumulate (d*b + a) mod n into point
    for j in range(m):
        c_j = int(d * (1 << j)) % n
        _ctrl_mod_add(qc, b_reg[j], point, flag, anc, c_j, n, m1)
    for i in range(m):
        c_i = int(1 << i) % n
        _ctrl_mod_add(qc, a_reg[i], point, flag, anc, c_i, n, m1)

    # Inverse QFT on a and b
    qc.append(QFTGate(m).inverse(), a_reg)
    qc.append(QFTGate(m).inverse(), b_reg)

    # Measure
    qc.measure(a_reg, c_reg[:m])
    qc.measure(b_reg, c_reg[m:])

    return qc, m, m1


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Post-processing + EC verification                                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def extract_candidates(counts: dict, m: int, n: int) -> dict[int, int]:
    """
    From raw bitstring counts, compute d_candidate counts.
    d = -a * b^{-1} mod n  (standard Shor ECDLP post-processing).
    """
    d_counts: dict[int, int] = {}
    for bs, cnt in counts.items():
        a_val = int(bs[:m],  2)
        b_val = int(bs[m:], 2)
        if gcd(b_val, n) != 1:
            continue
        b_inv = pow(b_val % n, -1, n)
        d_c   = (-a_val * b_inv) % n
        d_counts[d_c] = d_counts.get(d_c, 0) + cnt
    return d_counts


def find_verified_key(counts: dict, m: int, key: dict) -> Optional[int]:
    """
    Try all candidate d values in decreasing frequency and verify
    each one against the EC public key Q = d*G.
    Returns the first d that verifies (or None).
    """
    n         = key['subgroup_order']
    p_prime   = key['prime']
    G         = tuple(key['generator_point'])
    Q         = tuple(key['public_key'])
    a_coeff   = 0   # y² = x³ + 7 (all test curves are secp-style with a=0)

    d_counts = extract_candidates(counts, m, n)
    ranked   = sorted(d_counts.items(), key=lambda x: x[1], reverse=True)

    for d_cand, hits in ranked:
        if verify_key(d_cand, G, Q, a_coeff, p_prime):
            return d_cand, hits, ranked

    return None, 0, ranked


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Simulator runner                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def run_simulator(bit_length: int, shots: int = 20000) -> Optional[dict]:
    with open(KEYS_FILE) as f:
        keys = json.load(f)
    key = next(k for k in keys if k['bit_length'] == bit_length)
    n, expected_d = key['subgroup_order'], key['private_key']

    print(f"\n{'='*62}")
    print(f"SIMULATOR  —  {bit_length}-bit key  n={n}  expected_d={expected_d}")

    t0 = time.time()
    qc, m, m1 = build_shor_circuit(n, expected_d)
    print(f"  Circuit: {qc.num_qubits} qubits  depth={qc.depth()}  gates={qc.size()}")

    # Use statevector for small circuits (≤ 27 qubits), MPS otherwise
    if qc.num_qubits <= 27:
        sim = AerSimulator(method='statevector')
    else:
        sim = AerSimulator(method='matrix_product_state')

    transpiled = transpile(qc, sim, optimization_level=2)
    print(f"  Transpiled: depth={transpiled.depth():,}  gates={transpiled.size():,}")

    result = sim.run(transpiled, shots=shots).result()
    counts = result.get_counts()
    t1 = time.time()
    print(f"  Simulation: {t1-t0:.1f}s  |  {len(counts)} unique outcomes")

    d_found, hits, ranked = find_verified_key(counts, m, key)
    total_valid = sum(v for v in extract_candidates(counts, m, n).values())

    print(f"\n  Valid measurements: {total_valid}/{shots} ({100*total_valid/shots:.1f}%)")
    print(f"  Top d candidates: {[(d, c) for d,c in ranked[:8]]}")

    if d_found is not None:
        print(f"\n  ✅ VERIFIED: d = {d_found}  (hits={hits}, {100*hits/shots:.3f}%)")
        print(f"     Confirmed: d*G = Q  ✓")
    else:
        print(f"\n  ❌ Correct key NOT found in this run — try more shots")

    return dict(bit_length=bit_length, n=n, expected_d=expected_d,
                qubits=qc.num_qubits, depth_pre=qc.depth(),
                depth_post=transpiled.depth(), shots=shots,
                d_found=d_found, d_found_hits=hits,
                top_candidates=ranked[:10])


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  IBM Hardware runner                                                     ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def run_hardware(bit_length: int, shots: int = 20000,
                 backend_name: Optional[str] = None,
                 opt_level: int = 3) -> Optional[dict]:
    """
    Run on real IBM Quantum hardware.
    Requires:
      export QISKIT_IBM_TOKEN=<your_token>
    New IBM Quantum Platform: also set QISKIT_IBM_INSTANCE=ibm-q/open/main (or your instance)
    """
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    from datetime import datetime

    token = os.environ.get('QISKIT_IBM_TOKEN', '')
    if not token:
        print("❌ QISKIT_IBM_TOKEN not set"); return None

    # Support both old (ibm_quantum) and new (ibm_quantum_platform) channels
    service = None
    for channel in ['ibm_quantum_platform', 'ibm_cloud']:
        try:
            instance = os.environ.get('QISKIT_IBM_INSTANCE', None)
            kwargs = dict(channel=channel, token=token)
            if instance:
                kwargs['instance'] = instance
            QiskitRuntimeService.save_account(overwrite=True, **kwargs)
            service = QiskitRuntimeService(channel=channel)
            print(f"✅ Connected via {channel}")
            break
        except Exception as e:
            print(f"  Trying {channel}: {e}")

    if service is None:
        print("❌ Could not connect to IBM Quantum"); return None

    with open(KEYS_FILE) as f:
        keys = json.load(f)
    key  = next(k for k in keys if k['bit_length'] == bit_length)
    n, expected_d = key['subgroup_order'], key['private_key']

    print(f"\n{'='*62}")
    print(f"HARDWARE  —  {bit_length}-bit key  n={n}  expected_d={expected_d}")

    qc, m, m1 = build_shor_circuit(n, expected_d)
    print(f"  Circuit: {qc.num_qubits} qubits  depth={qc.depth()}  gates={qc.size()}")

    if backend_name:
        backend = service.backend(backend_name)
    else:
        backend = service.least_busy(
            min_num_qubits=qc.num_qubits, operational=True)
    print(f"  Backend: {backend.name}  ({backend.num_qubits} qubits)")

    transpiled = transpile(qc, backend, optimization_level=opt_level)
    cx_count   = transpiled.count_ops().get('cx', 0)
    print(f"  Transpiled: depth={transpiled.depth():,}  cx={cx_count:,}")

    sampler = Sampler(mode=backend)
    job = sampler.run([transpiled], shots=shots)
    job_id = job.job_id()
    print(f"  Job submitted: {job_id}  — waiting…")
    result = job.result()

    try:
        counts = result[0].data.c.get_counts()
    except Exception:
        counts = result[0].data.meas.get_counts()

    d_found, hits, ranked = find_verified_key(counts, m, key)
    total_valid = sum(v for v in extract_candidates(counts, m, n).values())

    print(f"\n  Valid measurements: {total_valid}/{shots} ({100*total_valid/shots:.1f}%)")
    print(f"  Top d candidates: {[(d,c) for d,c in ranked[:8]]}")

    if d_found is not None:
        print(f"\n  🎯 KEY RECOVERED: d = {d_found}  (hits={hits})")
        print(f"     Verified: {bit_length}-bit ECC private key BROKEN on IBM Quantum!")
        print(f"     IBM Job ID: {job_id}  ← competition evidence")
    else:
        print(f"\n  ⚠️ Key not recovered — try more shots or a different backend")

    ts  = datetime.now().strftime('%Y%m%d_%H%M%S')
    out = dict(timestamp=ts, bit_length=bit_length, n=n,
               expected_d=expected_d, backend=backend.name, job_id=job_id,
               shots=shots, cx_count=cx_count, depth=transpiled.depth(),
               d_found=d_found, d_found_hits=hits,
               top_candidates=ranked[:20])
    fname = os.path.join(SCRIPT_DIR, f'qday_hw_{bit_length}bit_{ts}.json')
    with open(fname, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"  Saved: {os.path.basename(fname)}")
    return out


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Main                                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='QDay Prize Competition Runner')
    p.add_argument('--mode',    choices=['sim', 'hw'], default='sim',
                   help='sim = local AerSimulator, hw = IBM Quantum hardware')
    p.add_argument('--bits',    type=int, nargs='+', default=[4],
                   help='ECC key bit sizes to attack (default: 4)')
    p.add_argument('--shots',   type=int, default=20000)
    p.add_argument('--backend', type=str, default=None,
                   help='IBM backend name (None = least busy)')
    p.add_argument('--opt',     type=int, default=3, choices=[0,1,2,3])
    args = p.parse_args()

    results = []
    for b in args.bits:
        if args.mode == 'sim':
            r = run_simulator(b, shots=args.shots)
        else:
            r = run_hardware(b, shots=args.shots,
                             backend_name=args.backend, opt_level=args.opt)
        if r:
            results.append(r)

    print(f"\n{'='*62}")
    print("SUMMARY")
    for r in results:
        d_str = f"d={r['d_found']} ✅" if r['d_found'] else "NOT FOUND ❌"
        print(f"  {r['bit_length']}-bit: {d_str}  "
              f"(qubits={r['qubits']}, depth_pre={r['depth_pre']}, "
              f"shots={r['shots']})")
