#!/bin/bash
# #699 run, part 2 (started 2026-10-24): w699_v3 = w699_v2 + one certificate line per segment of 10^6 n.
# Usage: run_v3.sh X0   -- searches [X0, 10^12), then re-runs [10^7, X0) to backfill certificate lines
# (that range was already searched by w699_v2; see results/run_1e7_1e12.txt).
cd "$(dirname "$0")"
X0=$1
CERTFILE=results/cert_v3.txt SEG=1000000 LOGSEC=300 ./w699_v3 "$X0" 1000000000000 > results/run_v3_main.txt 2> results/run_v3_main.err
echo "main exit=$?" >> results/run_v3_main.txt
CERTFILE=results/cert_v3_backfill.txt SEG=1000000 LOGSEC=300 ./w699_v3 10000000 "$X0" > results/run_v3_backfill.txt 2> results/run_v3_backfill.err
echo "backfill exit=$?" >> results/run_v3_backfill.txt
