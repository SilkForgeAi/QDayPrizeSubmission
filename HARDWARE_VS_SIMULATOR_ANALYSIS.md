Hardware vs Simulator Analysis
==============================

Summary
-------
This repository focuses on hardware-verified ECDLP recovery. Simulator runs remain useful for sanity-checking, but submission credibility is based on IBM job IDs and classical key verification.

Observed hardware outcomes
--------------------------
- 4-bit: 1.92%
- 6-bit: 2.915%
- 7-bit: 1.13%
- 9-bit: 0.255% (verified artifact in repo)
- 10-bit: 0.19% (verified artifact in repo)

Why hardware-first evidence matters
-----------------------------------
1) NISQ effects and backend-specific behavior are not fully captured by idealized simulation.
2) Competition validation is strongest when claims are tied to publicly verifiable IBM job IDs.
3) End-to-end reproducibility includes queueing, transpilation, runtime constraints, and measurement noise.

Interpretation
--------------
- Success rates decrease with scale, consistent with deeper circuits and accumulated error.
- Despite lower rates, 9-bit and 10-bit recoveries are achieved and classically verified.
- This establishes practical scaling evidence beyond earlier low-bit demonstrations.

Caveats
-------
- Low hit rates require high shot counts.
- Resource cost grows significantly with bit-size.
- Further depth and error mitigation optimization is needed for larger keys.
