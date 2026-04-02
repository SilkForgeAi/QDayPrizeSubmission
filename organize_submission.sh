#!/bin/bash
# Script to list files for GitHub submission

echo "=== FILES TO INCLUDE IN GITHUB SUBMISSION ==="
echo ""
echo "Required Core Files:"
echo "-------------------"
for file in README.md brief.txt shor_ecdlp_correct.py elliptic_curve.py ecc_keys.json verify_keys.py; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (MISSING!)"
    fi
done

echo ""
echo "Execution Scripts:"
echo "------------------"
for file in shor_4bit_ibm.py shor_6bit_ibm.py shor_7bit_ibm.py; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (MISSING!)"
    fi
done

echo ""
echo "Results Files:"
echo "--------------"
for file in ibm_results_4bit_20251220_165304.json 6bit_ibm_ibm_torino_20251220_173259.json 7bit_ibm_ibm_torino_20251220_180541.json; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (MISSING!)"
    fi
done

echo ""
echo "Recommended Documentation:"
echo "-------------------------"
for file in brief.txt COMPETITION_RULES_COMPLIANCE.md HARDWARE_VS_SIMULATOR_ANALYSIS.md; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (MISSING!)"
    fi
done

echo ""
echo "=== SUMMARY ==="
echo "Total files to upload: ~15-17 files"
echo "Remember to convert brief.txt to brief.pdf before uploading!"
