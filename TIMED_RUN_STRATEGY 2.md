# 10-Minute IBM Quantum Time Strategy

## Overview
This script (`shor_8bit_ibm_timed.py`) is optimized for a **10-minute time budget** on IBM Quantum hardware.

## Time Allocation Strategy

### Budget: 10 minutes = 600 seconds

**Estimated breakdown:**
- Circuit creation: ~5-10 seconds
- IBM connection: ~2-5 seconds
- Backend selection: ~2-5 seconds
- Transpilation: ~10-30 seconds
- Queue time: **Variable (1-5 minutes)** ← Biggest uncertainty
- Execution: ~5-10 minutes per 10k shots
- Result processing: ~5-10 seconds

### Adaptive Shot Allocation

The script automatically adjusts shot count based on:
1. **Queue time** - Checks pending jobs and estimates wait time
2. **Remaining time** - Calculates available execution window
3. **Conservative buffer** - Uses only 80% of available time

**Shot allocation logic:**
- **If queue is short** (1-2 min) → 15k-20k shots (best chance)
- **If queue is medium** (3-4 min) → 10k-15k shots
- **If queue is long** (5+ min) → 5k-10k shots (minimum viable)

### Time Monitoring

- **Continuous monitoring** - Checks remaining time every 5 seconds
- **Early warnings** - Alerts when < 2 minutes remain
- **Automatic cancellation** - Cancels job if time runs out before completion
- **Status updates** - Shows elapsed/remaining time throughout

## Success Probability

With 0.002% success rate:
- **5k shots** → Expected ~0.1 correct results (very low)
- **10k shots** → Expected ~0.2 correct results (low)
- **15k shots** → Expected ~0.3 correct results (better)
- **20k shots** → Expected ~0.4 correct results (best within budget)

**Note:** These are expected values - actual results vary. One success is all we need!

## How to Run

```bash
cd qday_prize
python3 shor_8bit_ibm_timed.py
```

The script will:
1. ✅ Create circuit
2. ✅ Connect to IBM
3. ✅ Check queue status
4. ✅ Calculate optimal shot count
5. ✅ Submit job
6. ✅ Monitor time throughout
7. ✅ Process and display results

## Expected Outcomes

### Best Case (Fast Queue)
- Queue: ~1 minute
- Execution: ~10-12 minutes worth of shots (15k-20k)
- Time used: ~8-10 minutes
- **Good chance of success**

### Typical Case (Medium Queue)
- Queue: ~3 minutes  
- Execution: ~7 minutes worth of shots (10k-15k)
- Time used: ~10 minutes (full budget)
- **Moderate chance of success**

### Worst Case (Long Queue)
- Queue: ~5+ minutes
- Execution: ~5 minutes worth of shots (5k-10k)
- Time used: ~10 minutes
- **Lower chance of success** (but still possible!)

## Time Safety Features

1. **Pre-execution checks** - Verifies time remaining before each major step
2. **Job monitoring** - Continuously checks time during execution
3. **Automatic cancellation** - Stops job if time limit reached
4. **Graceful exit** - Saves partial results if interrupted

## Tips for Maximum Success

1. **Run during off-peak hours** - Shorter queue times = more shots
2. **Monitor the run** - Watch for early completion
3. **Be patient** - Queue time is the biggest variable
4. **Check results file** - Saved automatically even if not fully successful

## Output Files

Results are automatically saved to:
```
8bit_ibm_timed_{backend}_{timestamp}.json
```

Includes:
- Job ID (for verification on IBM dashboard)
- Shot count used
- Success count (if any)
- Time statistics
- All measurement data
