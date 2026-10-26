Erdos #699 family check, second program (Claude, 2026-10-24, run in the cloud, not on the Mac).
onen.c + onen.py: every strict near-miss (n, i, j) for one n, all i (up to the prime gap below n) and all j <= n/2.
  For each i, the primes p > i dividing C(n,i) are taken from the factorizations of n, n-1, ..., n-i+1; j is enumerated
  over the base-p digit pattern (Lucas) of the most restrictive such p and then tested against every other one.
  Survivors are re-checked with exact gcds (n <= 5000) or Kummer carry counts, and p = i is tested separately.
Validation: brute_small.py (plain gcds, no Lucas/Kummer, no window rule) for every n in [4, 400] -> brute_4_400.txt,
  identical to onen.py; onen.py for n <= 3000 gives only the known near-misses; fam_cloud.txt (all 2^k, k = 4..49, and
  3^m + 1, m = 2..31) matches results/families_2k_3m1.txt exactly and adds 2^48: none.
fam_ext.txt: 2^50..2^62 and 3^32+1..3^39+1 (up to about 4.6e18): none. 676 s on 2 cloud cores.
