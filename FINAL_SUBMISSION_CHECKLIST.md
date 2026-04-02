Final Submission Checklist

Before submitting to GitHub, verify the following:

Code Verification:

□ All code runs successfully without errors
□ Test at least one key (e.g., run shor_7bit_full_test.py on simulator)
□ All imports work correctly
□ File paths are correct in all scripts

File Presence:

□ shor_ecdlp_correct.py - Main implementation
□ elliptic_curve.py - Classical operations
□ ecc_keys.json - Competition keys
□ verify_keys.py - Verification script
□ shor_4bit_ibm.py - 4-bit execution
□ shor_6bit_ibm.py - 6-bit execution
□ shor_7bit_ibm.py - 7-bit execution

Results Files:

□ ibm_results_4bit_20251220_165304.json
□ 6bit_ibm_ibm_torino_20251220_173259.json
□ 7bit_ibm_ibm_torino_20251220_180541.json

Documentation:

□ README.md - Complete and updated
□ brief.txt - Ready to convert to PDF
□ brief.pdf - Converted from brief.txt (max 2 pages)

Job ID Verification:

□ 4-bit: d53hle9smlfc739eskn0 - Verify on IBM Quantum Cloud
□ 6-bit: d53i7nfp3tbc73amgl2g - Verify on IBM Quantum Cloud
□ 7-bit: d53ijmgnsj9s73b0vf60 - Verify on IBM Quantum Cloud

README.md Checks:

□ Contact email: Aaron@vexaai.app (correct)
□ All file names match actual files
□ All paths are correct
□ Job IDs match results JSON files
□ No typos or formatting errors
□ Code examples are correct
□ Installation instructions are accurate

Brief.pdf Checks:

□ Under 2 pages
□ Explains approach clearly
□ Describes techniques used
□ Includes requirements
□ Mentions drawbacks/limitations
□ Suitable for quantum algorithms audience

GitHub Repository:

□ Repository is created
□ All files are uploaded
□ Repository is set to PUBLIC
□ README.md displays correctly
□ brief.pdf is uploaded
□ Code files are properly formatted

Final Verification:

□ Can someone else clone and run the code?
□ Are instructions clear and complete?
□ Do results JSON files contain valid data?
□ Are all claims supported by evidence?

Pre-Submission Test:

1. Clone repository in fresh directory
2. Follow README.md instructions from scratch
3. Run verification: python3 verify_keys.py
4. Run simulator test: python3 shor_7bit_full_test.py
5. Verify all outputs match expected results

Email Submission:

□ Email address: qdayprize@projecteleven.com
□ Include GitHub repository URL
□ Brief description of keys broken (4-bit, 6-bit, 7-bit)
□ Largest key: 7-bit (n=79)
□ Mention hardware-beats-simulator finding

Final Review:

□ README.md is professional and complete
□ Code is clean and well-commented
□ Results are verifiable
□ Submission follows all competition requirements
□ Everything is ready for public review

