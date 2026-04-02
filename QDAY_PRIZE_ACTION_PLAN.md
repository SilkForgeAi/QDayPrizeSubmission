# QDay Prize Competition - Action Plan

**Competition:** Break ECC with Shor's Algorithm  
**Prize:** 1 Bitcoin  
**Deadline:** April 5, 2026  
**Status:** ✅ Registered

---

## 🎯 COMPETITION GOAL

Break the **largest ECC key possible** using Shor's algorithm on a quantum computer.

**Key Requirements:**
- ✅ Pure quantum solution (no classical shortcuts or hybrid tricks)
- ✅ Must use Shor's algorithm for ECDLP (Elliptic Curve Discrete Logarithm Problem)
- ✅ General and robust approach that scales
- ✅ No impractical classical computation requirements
- ✅ ECC keys provided: security levels 1-25 bits
- ✅ **Even a 3-bit key would be big news!**

---

## 📋 IMMEDIATE NEXT STEPS

### Step 1: Get the Competition ECC Keys
**Action Required:**
- Contact competition organizers to obtain the provided ECC keys (1-25 bit security levels)
- Understand the key format and curve parameters
- Test keys should be provided after registration

### Step 2: Understand ECDLP vs Standard Shor's
**Critical Understanding:**
- Standard Shor's algorithm: Factors integers (RSA-like)
- **ECDLP Shor's:** Solves discrete logarithm on elliptic curves (different problem!)
- Need to adapt Shor's algorithm for elliptic curve operations

**Key Differences:**
```
Standard Shor's:        ECDLP Shor's:
- Factor N = p × q      - Find k where Q = kP on curve
- Uses period finding   - Uses period finding on EC group
- Quantum Fourier       - Quantum Fourier Transform
  Transform               on elliptic curve
```

### Step 3: Review Your Current Capabilities

**✅ You Have:**
- Qiskit installed (v2.1.2) - ✅
- IBM Quantum access (ibm_brisbane, Torino experience) - ✅
- AWS Braket access - ✅
- Quantum circuit experience - ✅
- Error mitigation techniques (ZNE) - ✅

**❌ You Need:**
- Shor's algorithm implementation for ECDLP
- Elliptic curve arithmetic on quantum circuits
- Period finding for elliptic curve groups
- Testing framework for ECC key breaking

---

## 🔬 TECHNICAL IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1-2)

1. **Implement Basic Shor's Components**
   - Quantum Fourier Transform (QFT) - you have some QFT code
   - Modular exponentiation for EC operations
   - Period finding oracle for elliptic curves

2. **Elliptic Curve Arithmetic**
   - Classical: Point addition, scalar multiplication
   - Quantum: Encode EC operations as quantum gates
   - Implement EC group operations on qubits

3. **Small-Scale Testing**
   - Start with 1-bit key (should be feasible immediately)
   - Test on quantum simulator first
   - Validate against known solutions

### Phase 2: Hardware Optimization (Week 3-4)

4. **Error Mitigation**
   - Apply ZNE (you have experience with this!)
   - Optimize qubit mapping for IBM/IBMQ hardware
   - Handle 99-99.9% gate fidelity limitations

5. **Circuit Optimization**
   - Minimize circuit depth (critical for noisy hardware)
   - Optimize gate count
   - Use hardware-native gates (IBM: CNOT, single-qubit gates)

6. **Backend Selection**
   - Test on IBM Brisbane (127 qubits)
   - Test on IBM Torino
   - Compare with AWS Braket options (IonQ, Rigetti)

### Phase 3: Scaling (Week 5+)

7. **Progressive Key Breaking**
   - 1-bit key → proof of concept
   - 2-bit key → basic validation
   - 3-bit key → **significant milestone** (competition goal)
   - 4-bit+ keys → stretch goals

8. **Performance Documentation**
   - Record gate counts, circuit depth
   - Document error rates and mitigation strategies
   - Measure success probability vs key size

---

## 🛠️ IMPLEMENTATION CHECKLIST

### Core Components Needed

- [ ] **Shor's Algorithm for ECDLP**
  - [ ] Quantum period finding subroutine
  - [ ] Elliptic curve point addition oracle
  - [ ] Scalar multiplication on quantum circuit
  - [ ] QFT for period extraction

- [ ] **Elliptic Curve Quantum Gates**
  - [ ] Encode EC points as quantum states
  - [ ] Implement EC group operations
  - [ ] Handle curve parameters (a, b, p)

- [ ] **Testing Framework**
  - [ ] Load competition-provided ECC keys
  - [ ] Verify solutions classically
  - [ ] Compare quantum results

- [ ] **Hardware Integration**
  - [ ] IBM Quantum backend integration
  - [ ] Circuit transpilation optimization
  - [ ] Error mitigation pipeline

- [ ] **Documentation**
  - [ ] Gate-level code documentation
  - [ ] Approach description
  - [ ] Hardware specifications used

---

## 📚 LEARNING RESOURCES

### Key Papers to Review

1. **"Shor's Algorithm for ECDLP"** - Original adaptation papers
2. **"Quantum Elliptic Curve Discrete Logarithm Problem"** - Recent optimizations
3. **"Practical Quantum Cryptanalysis"** - Error mitigation strategies
4. **Competition Rubric** - Review scoring criteria from organizers

### Qiskit Resources
- Qiskit Textbook: Shor's Algorithm chapter
- Qiskit Quantum Circuits for Arithmetic
- Qiskit Optimization for NISQ devices

---

## ⚠️ CRITICAL CONSIDERATIONS

### Hardware Limitations
- **99-99.9% gate fidelity** - Will need error mitigation
- **Limited qubits** - Current: ~100-127 logical qubits
- **Noise** - Decoherence, gate errors, readout errors

### Algorithm Challenges
- **ECDLP is harder than factoring** - More complex group operations
- **Circuit depth** - EC operations are deeper than integer operations
- **Scalability** - Must work without impractical classical pre-computation

### Competition Rules
- **No classical shortcuts** - Pure quantum solution required
- **Must scale** - Can't use tricks that don't work for 256-bit keys
- **Public submission** - Code will be shared publicly

---

## 🎯 SUCCESS METRICS

### Minimum Viable (Still Significant!)
- ✅ Break 1-bit ECC key on real quantum hardware
- ✅ Document complete approach
- ✅ Reproducible results

### Competitive Target
- 🎯 Break 3-bit ECC key (mentioned as "big news")
- 🎯 Robust implementation
- 🎯 Clear documentation

### Stretch Goals
- 🚀 Break 4-5 bit keys
- 🚀 Leading the competition
- 🚀 Publication-quality results

---

## 📝 SUBMISSION REQUIREMENTS

When ready, submission must include:

1. **Gate-Level Code/Instructions**
   - Quantum circuit code (Qiskit, OpenQASM, or equivalent)
   - Clear instructions for execution

2. **Approach Description**
   - How you adapted Shor's for ECDLP
   - Techniques used (error mitigation, optimization, etc.)
   - Scaling strategy

3. **Hardware Specifications**
   - Quantum computer used (IBM Brisbane, etc.)
   - Backend specifications
   - Execution details

4. **Results**
   - Which key size you broke
   - Verification of solution
   - Performance metrics

---

## 🚀 IMMEDIATE ACTIONS (THIS WEEK)

1. **Contact Competition Organizers**
   - Get ECC key files
   - Clarify key format
   - Get access to submission portal

2. **Set Up Project Structure**
   ```
   qday_prize/
   ├── shors_ecdlp/
   │   ├── elliptic_curve.py      # Classical EC operations
   │   ├── quantum_ec_ops.py      # Quantum EC gates
   │   ├── shors_algorithm.py     # Main Shor's implementation
   │   └── period_finding.py      # Quantum period finding
   ├── testing/
   │   ├── test_keys/             # Competition keys
   │   ├── validate_results.py    # Verify solutions
   │   └── benchmarks.py          # Performance testing
   ├── hardware/
   │   ├── ibm_backend.py         # IBM Quantum integration
   │   ├── braket_backend.py      # AWS Braket integration
   │   └── error_mitigation.py    # ZNE and other techniques
   └── submission/
       ├── gate_level_code/       # Final submission code
       ├── approach_description.md
       └── results/
   ```

3. **Start with 1-Bit Key**
   - Implement minimal Shor's for ECDLP
   - Test on simulator
   - Move to real hardware

4. **Literature Review**
   - Find best-known implementations
   - Learn from prior work
   - Identify optimization opportunities

---

## 💡 STRATEGIC ADVANTAGES

**You Have Unique Experience:**
- ✅ Real quantum hardware experience (IBM, Braket)
- ✅ Error mitigation techniques (ZNE from your biosignal work)
- ✅ Circuit optimization experience
- ✅ Multiple backend familiarity

**Competition Edge:**
- Your biosignal work shows you understand NISQ limitations
- You have practical error handling experience
- You know how to optimize for real hardware constraints

---

## 📅 TIMELINE SUGGESTION

- **Week 1-2:** Foundation (ECDLP Shor's, basic implementation)
- **Week 3-4:** Hardware integration (IBM, error mitigation)
- **Week 5-6:** Testing and optimization (1-2 bit keys)
- **Week 7+:** Scaling (3+ bit keys, competition submission)

**You have ~11 months until deadline** - plenty of time for systematic development!

---

## 🔗 NEXT STEPS RIGHT NOW

1. ✅ Read this plan
2. ⬜ Contact competition organizers for ECC keys
3. ⬜ Set up project directory structure
4. ⬜ Start literature review on ECDLP Shor's algorithm
5. ⬜ Begin implementing basic elliptic curve quantum operations

---

**Ready to start building?** Let me know when you want to begin implementation!

