# Quick Guide: Retrieve 8-Bit Results

**Job ID:** `d5p98hgh0i0s73eoutvg`  
**Status:** ✅ DONE  
**Backend:** ibm_torino  
**Shots:** 5,000

## Run This Command:

```bash
cd 02_QDAY_PRIZE_COMPETITION
python3 retrieve_8bit_results.py
```

The script will:
1. ✅ Connect to IBM Quantum
2. ✅ Retrieve job results
3. ✅ Process measurements
4. ✅ Extract the key (d=103)
5. ✅ Save results to JSON file

## Expected Output:

- Success count (how many times d=103 was found)
- Success rate percentage
- Top 20 measurements
- Results saved to: `8bit_ibm_d5p98hgh0i0s73eoutvg_YYYYMMDD_HHMMSS.json`

## If You Get Errors:

The result format from Sampler uses `quasi_dists` (probability distributions). The script now handles this correctly by converting probabilities to counts.

**Note:** The job completed successfully - you just need to retrieve and process the results!
