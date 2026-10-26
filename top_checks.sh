#!/bin/bash
# Argon's suggested extra test: exercise the top of the range (largest sieving primes, 40-bit values).
cd "$(dirname "$0")"
LOGSEC=1e9 ./w699_v1 999990000000 1000000000000 > results/top_v1_1e7.txt
LOGSEC=1e9 ./w699_v2 999990000000 1000000000000 > results/top_v2_1e7.txt
diff <(grep ^S results/top_v1_1e7.txt) <(grep ^S results/top_v2_1e7.txt) && echo V1V2_MATCH_TOP
SEG=16384 XCHECK=1 LOGSEC=1e9 ./w699_v2 999999000000 1000000000000 > results/top_xcheck_1e6.txt; echo xcheck_exit=$?
echo ALL_DONE
