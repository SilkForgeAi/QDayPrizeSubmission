#!/usr/bin/env python3
"""
Retrieve a specific IBM job result and diagnose issues.
Usage:
  QISKIT_IBM_TOKEN=... python3 retrieve_job.py <job_id>
  QISKIT_IBM_TOKEN=... python3 retrieve_job.py d762evm8faus73f0nukg
"""
import sys, os, json
from qiskit_ibm_runtime import QiskitRuntimeService

INSTANCE = "crn:v1:bluemix:public:quantum-computing:us-east:a/9912f0e851b64e13a483727c70edb288:c4a5d7c2-0429-4e8d-bb6b-f942a9dd85a1::"
KEYS_FILE = os.path.join(os.path.dirname(__file__), 'QDay_Prize_Submission', 'ecc_keys.json')

job_id = sys.argv[1] if len(sys.argv) > 1 else 'd762evm8faus73f0nukg'

token = os.environ.get('QISKIT_IBM_TOKEN', '')
if not token:
    print("Set QISKIT_IBM_TOKEN env var"); sys.exit(1)

print(f"Connecting...")
service = None
for channel in ['ibm_cloud', 'ibm_quantum_platform']:
    try:
        service = QiskitRuntimeService(channel=channel, token=token, instance=INSTANCE)
        print(f"Connected via {channel}")
        break
    except Exception as e:
        print(f"  {channel}: {e}")

if service is None:
    print("Could not connect"); sys.exit(1)

print(f"\nFetching job {job_id}...")
job = service.job(job_id)

print(f"  Status : {job.status()}")
print(f"  Backend: {job.backend().name}")

status = str(job.status())
if 'DONE' in status or 'done' in status.lower():
    print("\nJob DONE — retrieving results...")
    try:
        result = job.result()
        print(f"  Result type: {type(result)}")

        # Try various ways to get counts
        try:
            counts = result[0].data.c.get_counts()
            print(f"  ✅ Got counts — {len(counts)} unique outcomes")

            # Load key and post-process
            with open(KEYS_FILE) as f:
                keys = json.load(f)
            key = next(k for k in keys if k['bit_length'] == 8)
            n = key['subgroup_order']
            m = 8

            from math import gcd
            d_counts = {}
            for bs, cnt in counts.items():
                try:
                    a_val = int(bs[:m], 2)
                    b_val = int(bs[m:], 2)
                    if gcd(b_val, n) != 1: continue
                    b_inv = pow(b_val % n, -1, n)
                    d_c = (-a_val * b_inv) % n
                    d_counts[d_c] = d_counts.get(d_c, 0) + cnt
                except: pass

            ranked = sorted(d_counts.items(), key=lambda x: -x[1])
            print(f"  Top candidates: {ranked[:10]}")

            expected_d = key['private_key']
            if expected_d in d_counts:
                hits = d_counts[expected_d]
                print(f"\n  ✅ d={expected_d} FOUND with {hits} hits!")
                print(f"  Job ID for submission: {job_id}")
            else:
                print(f"\n  ⚠️  d={expected_d} not in top candidates")

        except Exception as e:
            print(f"  Count parsing error: {e}")
            print(f"  Raw result[0]: {result[0]}")

    except Exception as e:
        print(f"\n  ❌ result() failed: {e}")
        print("\n  Job likely failed on IBM side. Check:")
        print(f"  https://quantum.ibm.com/jobs/{job_id}")

elif 'FAIL' in status.upper() or 'ERROR' in status.upper() or 'CANCEL' in status.upper():
    print(f"\n  ❌ Job failed/cancelled: {status}")
    print(f"  Error info: {job.error_message() if hasattr(job, 'error_message') else 'N/A'}")
    print(f"  Check: https://quantum.ibm.com/jobs/{job_id}")
    print(f"\n  → Run shor_9bit_ripple.py --mode hw --bits 8 to resubmit")
else:
    print(f"\n  Job still running: {status}")
    print(f"  Check: https://quantum.ibm.com/jobs/{job_id}")
    print(f"  Re-run this script when done")
