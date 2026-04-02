#!/usr/bin/env python3
"""
Simple 8-bit result retrieval - tries all access methods
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'QDay_Prize_Submission'))

from qiskit_ibm_runtime import QiskitRuntimeService

JOB_ID = "d5p98hgh0i0s73eoutvg"

print("Retrieving job results...")
service = QiskitRuntimeService()
job = service.job(JOB_ID)

print(f"Status: {job.status()}")
result = job.result()

print(f"\nResult type: {type(result)}")
print(f"Result[0] type: {type(result[0])}")
print(f"Result[0] has data: {hasattr(result[0], 'data')}")

data_bin = result[0].data
print(f"\nDataBin type: {type(data_bin)}")
print(f"DataBin attributes: {[x for x in dir(data_bin) if not x.startswith('_')]}")

if hasattr(data_bin, 'c'):
    c_data = data_bin.c
    print(f"\nc type: {type(c_data)}")
    print(f"c attributes: {[x for x in dir(c_data) if not x.startswith('_')][:15]}")
    
    # Try get_counts
    if hasattr(c_data, 'get_counts'):
        print("\n✅ Trying get_counts()...")
        counts = c_data.get_counts()
        print(f"Counts type: {type(counts)}")
        print(f"Counts sample: {list(counts.items())[:5] if isinstance(counts, dict) else counts[:5] if hasattr(counts, '__getitem__') else 'N/A'}")
    else:
        print("\n⚠️  No get_counts() method")
        print(f"c_data value type: {type(c_data)}")
        if isinstance(c_data, dict):
            print(f"✅ It's a dict! Sample: {list(c_data.items())[:5]}")
        elif hasattr(c_data, '__iter__'):
            print(f"✅ It's iterable! First 5: {list(c_data)[:5] if hasattr(c_data, '__len__') else 'Cannot get length'}")
