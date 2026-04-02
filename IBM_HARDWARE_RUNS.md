# IBM Quantum Hardware Runs - Recommendations

## 📊 Shot Recommendations

### Simulator Performance
- **Success Rate:** ~2.5% (finds d=6 correctly)
- **Valid Measurements:** ~46% (where b is invertible)
- **At 8192 shots:** Found d=6 in ~217 measurements

### Real Hardware Expectations
- **Expected Success Rate:** 1-2% (due to noise)
- **Recommendation:** 10,000-15,000 shots per run

### Shot Count Strategy

**Option 1: Single Large Run (Recommended)**
- **Shots:** 15,000
- **Expected correct results:** 150-300
- **Cost:** Moderate
- **Time:** ~10-15 minutes

**Option 2: Multiple Medium Runs (More Reliable)**
- **Run 1:** 10,000 shots
- **Run 2:** 10,000 shots
- **Run 3:** 10,000 shots
- **Total:** 30,000 shots, ~300-600 correct results
- **Cost:** Higher but better statistics
- **Time:** ~30-45 minutes total

**Option 3: Multiple Backends (Best for Competition)**
- **ibm_brisbane:** 15,000 shots
- **ibm_torino:** 15,000 shots (if available)
- **Total:** 30,000 shots across backends
- **Benefit:** Validates across different hardware
- **Time:** Queue time dependent

## 🎯 Recommended Configuration

For **competition submission**, I recommend:

1. **Start with 15,000 shots** on one backend (ibm_brisbane recommended)
2. **If successful**, do a second run on different backend for validation
3. **Total:** 2-3 runs with 10,000-15,000 shots each

## 📝 Success Criteria

- **Minimum:** 50+ correct measurements (d=6 found)
- **Good:** 100+ correct measurements
- **Excellent:** 200+ correct measurements

At 1-2% success rate:
- 10,000 shots → ~100-200 correct
- 15,000 shots → ~150-300 correct
- 20,000 shots → ~200-400 correct

## 💰 Cost Considerations

- Free tier: Limited shots per month
- Paid tier: More shots available
- Check your IBM Quantum account limits

## ⏱️ Time Estimates

- **Queue time:** 0-30 minutes (varies by backend)
- **Execution:** ~5-10 minutes per 10,000 shots
- **Total per run:** 10-40 minutes

## 🚀 Quick Start

```bash
cd qday_prize
python3 shor_ibm_hardware.py
```

Defaults: 15,000 shots on least busy backend

## 📊 Monitoring

The script will:
- Save results to JSON file with timestamp
- Show job ID for tracking
- Display top measurements and success rate
- Track d=6 occurrences

