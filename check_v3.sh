#!/bin/bash
# Validate w699_v3 against w699_v2 before switching: identical totals, and per-10^6-block counts independent of SEG.
cd "$(dirname "$0")"
/usr/bin/clang -O3 -mcpu=native -Wall -o w699_v3 w699_v3.c -lpthread 2>&1 | head -5
LOGSEC=1e9 ./w699_v2 10000000000 10010000000 | tail -1 | sed 's/elapsed=[0-9.]*s//' > results/chk_v2.txt
rm -f results/chk_cert_a.txt results/chk_cert_b.txt
CERTFILE=results/chk_cert_a.txt SEG=1000000 LOGSEC=1e9 ./w699_v3 10000000000 10010000000 | tail -1 | sed 's/elapsed=[0-9.]*s//' > results/chk_v3a.txt
CERTFILE=results/chk_cert_b.txt SEG=250000 LOGSEC=1e9 ./w699_v3 10000000000 10010000000 | tail -1 | sed 's/elapsed=[0-9.]*s//' > results/chk_v3b.txt
diff results/chk_v2.txt results/chk_v3a.txt && diff results/chk_v2.txt results/chk_v3b.txt && echo TOTALS_MATCH
agg() { awk '{b=int($2/1000000); c[b]+=$4; d[b]+=$5; s[b]+=$6; f[b]+=$7} END {for (k in c) print k, c[k], d[k], s[k], f[k]}' "$1" | sort -n; }
diff <(agg results/chk_cert_a.txt) <(agg results/chk_cert_b.txt) && echo BLOCKS_MATCH
awk '{c+=$5} END {print "cert cand sum", c}' results/chk_cert_a.txt; cat results/chk_v3a.txt
echo CHECK_DONE
