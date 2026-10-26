#!/bin/bash
# Build both versions natively and check they agree (v2 also cross-checks every exact test by trial division).
cd "$(dirname "$0")"
for v in v1 v2; do /usr/bin/clang -O3 -mcpu=native -Wall -o w699_$v w699_$v.c -lpthread 2>&1 | head -3; done
mkdir -p results
LOGSEC=1e9 ./w699_v1 4 10000000 > results/v1_1e7.txt
XCHECK=1 LOGSEC=1e9 ./w699_v2 4 10000000 > results/v2_1e7.txt
diff <(grep ^S results/v1_1e7.txt) <(grep ^S results/v2_1e7.txt) && echo V1V2_MATCH_1e7
XCHECK=1 LOGSEC=1e9 ./w699_v2 1000000000 1050000000 > results/v2_xcheck_1e9.txt; echo "xcheck exit=$?"
LOGSEC=1e9 ./w699_v1 10000000000 10100000000 > results/v1_1e10.txt
LOGSEC=1e9 ./w699_v2 10000000000 10100000000 > results/v2_1e10.txt
diff <(grep ^S results/v1_1e10.txt) <(grep ^S results/v2_1e10.txt) && echo V1V2_MATCH_1e10
grep -c ^S results/v2_1e7.txt; tail -1 results/v1_1e7.txt; tail -1 results/v2_1e7.txt; tail -1 results/v2_xcheck_1e9.txt; tail -1 results/v1_1e10.txt; tail -1 results/v2_1e10.txt
