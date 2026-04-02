#!/usr/bin/env python3
"""
IBM Connect & Run — QDay Prize One-Shot Script
===============================================

Run this AFTER setting your IBM credentials (see instructions below).

STEP 1 — Get credentials (pick ONE option):

  Option A — IBM Quantum Platform token (regenerate yours):
    1. Go to https://quantum.ibm.com/
    2. Click your account icon → "Copy token"
    3. Run:
       export QISKIT_IBM_TOKEN="paste_token_here"

  Option B — IBM Cloud API key (for cloud instances like ELifeDevise):
    1. Go to https://cloud.ibm.com/iam/apikeys
    2. Create new API key → copy it
    3. Run:
       export QISKIT_IBM_TOKEN="paste_api_key_here"
       export QISKIT_IBM_INSTANCE="crn:v1:bluemix:public:quantum-computing:us-east:a/9912f0e851b64e13a483727c70edb288:c4a5d7c2-0429-4e8d-bb6b-f942a9dd85a1::"

STEP 2 — Run this script:
  python connect_and_run.py

It will:
  • Connect to IBM and list available backends
  • Run 9-bit (and 8-bit) jobs on ibm_torino
  • Save results with Job IDs for competition submission
"""
import os, sys, json, time
import numpy as np

TOKEN    = os.environ.get('QISKIT_IBM_TOKEN', '')
INSTANCE = os.environ.get('QISKIT_IBM_INSTANCE',
           'crn:v1:bluemix:public:quantum-computing:us-east:a/'
           '9912f0e851b64e13a483727c70edb288:'
           'c4a5d7c2-0429-4e8d-bb6b-f942a9dd85a1::')

if not TOKEN:
    print("❌  No token found. Set QISKIT_IBM_TOKEN env var.")
    print("    See instructions at the top of this file.")
    sys.exit(1)

print(f"Token (first 20 chars): {TOKEN[:20]}...")

# ── Connect ──────────────────────────────────────────────────────────────────
from qiskit_ibm_runtime import QiskitRuntimeService

service = None
for channel, inst in [
    ('ibm_cloud',             INSTANCE),
    ('ibm_quantum_platform',  INSTANCE),
    ('ibm_quantum_platform',  'ibm-q/open/main'),
    ('ibm_cloud',             None),
]:
    try:
        kwargs = dict(channel=channel, token=TOKEN)
        if inst: kwargs['instance'] = inst
        QiskitRuntimeService.save_account(overwrite=True, **kwargs)
        service = QiskitRuntimeService(**kwargs)
        print(f"✅ Connected: channel={channel}")
        break
    except Exception as e:
        print(f"  ✗ {channel} / {str(inst)[:40]}: {str(e)[:70]}")

if service is None:
    print("\n❌ Could not connect with any channel.")
    print("   • If using IBM Quantum Platform: regenerate token at https://quantum.ibm.com/")
    print("   • If using IBM Cloud: create API key at https://cloud.ibm.com/iam/apikeys")
    sys.exit(1)

# ── List backends ─────────────────────────────────────────────────────────────
print("\nAvailable operational backends:")
try:
    backends = service.backends(operational=True)
    for b in backends:
        try:
            s = b.status()
            print(f"  {b.name:25s}  qubits={b.num_qubits:3d}  queue={s.pending_jobs}")
        except Exception:
            print(f"  {b.name}")
except Exception as e:
    print(f"  (could not list backends: {e})")

# ── Pick backend ──────────────────────────────────────────────────────────────
preferred = ['ibm_torino', 'ibm_fez', 'ibm_marrakesh', 'ibm_kyiv', 'ibm_brisbane']
backend = None
for name in preferred:
    try:
        b = service.backend(name)
        if b.status().operational:
            backend = b
            print(f"\nUsing backend: {backend.name} ({backend.num_qubits} qubits)")
            break
    except Exception:
        continue

if backend is None:
    backend = service.least_busy(min_num_qubits=41, operational=True)
    print(f"\nUsing least-busy backend: {backend.name}")

# ── Run jobs ──────────────────────────────────────────────────────────────────
import subprocess, sys
SCRIPT = os.path.join(os.path.dirname(__file__), 'shor_9bit_ripple.py')

# Save credentials to environment for child script
env = os.environ.copy()
env['QISKIT_IBM_TOKEN']    = TOKEN
env['QISKIT_IBM_INSTANCE'] = INSTANCE

print("\n" + "="*62)
print("Launching 9-bit job (and 8-bit for comparison)...")
print("="*62)

# Run 9-bit (then 8-bit if time allows)
for bits in [9, 8]:
    print(f"\n▶  Submitting {bits}-bit job...")
    cmd = [sys.executable, SCRIPT, '--mode', 'hw',
           '--bits', str(bits), '--shots', '20000', '--backend', backend.name]
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        print(f"  Job exited with code {result.returncode}")
