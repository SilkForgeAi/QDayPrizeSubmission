FINAL GITHUB UPLOAD LIST

Repository Name: qday-prize-ecdlp-submission

FILES TO UPLOAD (17 files total):

Required Files (11):
--------------------
1. README.md
2. brief.pdf (convert from brief.txt - MUST BE PDF)
3. shor_ecdlp_correct.py
4. elliptic_curve.py
5. ecc_keys.json
6. verify_keys.py
7. shor_6bit_ibm.py
8. shor_7bit_ibm.py
9. ibm_results_4bit_20251220_165304.json
10. 6bit_ibm_ibm_torino_20251220_173259.json
11. 7bit_ibm_ibm_torino_20251220_180541.json

Note: shor_4bit_ibm.py is not required since 4-bit was run using shor_ibm_hardware.py
The 4-bit results are in ibm_results_4bit_20251220_165304.json

Recommended Documentation (3):
-------------------------------
12. brief.txt (source file for reference)
13. COMPETITION_RULES_COMPLIANCE.md
14. HARDWARE_VS_SIMULATOR_ANALYSIS.md

Optional Documentation (3):
----------------------------
15. SUBMISSION_PACKAGE.md (comprehensive doc)
16. ACHIEVEMENTS_SUMMARY.md (summary)
17. .gitignore (Git ignore file)

TOTAL: 17 files maximum

FILES TO EXCLUDE (DO NOT UPLOAD):

Development/Test Scripts:
- All *_test.py files
- All debug_*.py files
- All shor_*bit_*.py except shor_6bit_ibm.py and shor_7bit_ibm.py
- Old implementations (shor_ecdlp.py, shor_ecdlp_final.py, etc.)
- shor_ibm_hardware.py (generic wrapper, not needed)
- check_ibm_backends.py (utility script)

Simulator-Only Results:
- 6bit_results_20251220_172559.json
- 8bit_simulator_20251220_202339.json
- Any *_simulator_*.json files

Internal Documentation:
- All planning docs (STEP_BY_STEP_PLAN.md, FUTURE_SCALING_ROADMAP.md, etc.)
- All checklist files (GITHUB_*, FINAL_*, etc.)
- All status files (STATUS.md, DEBUG_STATUS.md, etc.)
- REPOSITORY_STRUCTURE.md
- SUBMISSION_FILES_LIST.txt
- organize_submission.sh

QUICK CHECKLIST:

Before Upload:
□ Convert brief.txt to brief.pdf (max 2 pages)
□ Verify all 11 required files exist
□ Test that code runs (at least verify_keys.py)
□ Check that README.md has correct email
□ Verify all job IDs are correct

After Upload:
□ Repository is PUBLIC
□ README.md displays correctly
□ brief.pdf is visible
□ All code files are present
□ Results JSON files are included
□ Code can be cloned

Email Submission:
□ Send to: qdayprize@projecteleven.com
□ Include GitHub repository URL
□ Mention keys broken: 4-bit, 6-bit, 7-bit
□ Mention largest key: 7-bit (n=79)

