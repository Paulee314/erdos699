# Erdős Problem #699: no counterexample below 10^12, and none with j ≤ 10^9

[Erdős Problem #699](https://www.erdosproblems.com/699) (Erdős and Szekeres) asks:
for every 1 ≤ i < j ≤ n/2, is there a prime p ≥ i that divides both C(n, i) and C(n, j)?

A **counterexample** is a triple (n, i, j) with no such prime. A **near-miss** is a triple where no prime
p > i divides both; it is rescued only by p = i.

## Results

| Result | How | Where |
| --- | --- | --- |
| No counterexample with n < 10^12 (all i, j) | Exhaustive search | `w699_v3.c`, `results/` |
| Any counterexample has n ≤ j² | Short lemma, below | below |
| No counterexample with j ≤ 10^9, for any n | The lemma, the search, and an exact enumeration above 10^12 | `smooth2/` |
| No counterexample with j ≤ 100, for any n, without using the search | The complete Luca–Najman list of x with x² − 1 97-smooth | `smooth_analyze.py`, `smooth_bound_note.md` |
| Near-misses: below 10^12 only the nine already known, all below 10^7. Among n = 2^k (k ≤ 62) and 3^m + 1 (m ≤ 39), one more: (2^41, 2, 285,920,731,515) | Search, plus a separate check of those two families | `results/v2_1e7.txt`, `fam2/` |

The previous published search covered n < 10^7 ([Cong Lu](https://github.com/conglu1997/erdos_699_rust)). Our run
below 10^7 reproduces his nine near-misses exactly.

**Status:** reviewed only by AI reviewers so far (see "Credits"). No human mathematician has checked these results.

## The search, n < 10^12

`w699_v3.c` tests every n in a range, every i from 2 up to the prime gap below n, and every j ≤ n/2 that the
shortcuts below allow. Every surviving candidate (n, i, j) is tested exactly. The case i = 1 needs no search:
n / gcd(n, j) > 1 divides both C(n, 1) = n and C(n, j).

**Shortcuts** (each a proved necessary condition for a near-miss):

- **(A)** For a prime p > i, p divides C(n, i) exactly when p divides one of n, n − 1, …, n − i + 1, because p does
  not divide i!.
- **(B)** Lucas's theorem: p does not divide C(n, j) exactly when every base-p digit of j is at most the
  corresponding digit of n.
- **(C)** If a prime p lies in (n − i, n] and 2i ≤ n, then p > n/2 ≥ j > i. For such p and k < p, p divides C(n, k)
  exactly when n mod p < k, and n mod p = n − p < i < j. So p divides both binomials, and only n with a prime gap
  of at least i below them matter.
- **Fast path:** let q1 and q2 be the largest prime factors of n and n − 1. For i < min(q1, q2), both lie in (A), so
  by (B) a near-miss needs j ≡ 0 (mod q1) and j mod q2 ∈ {0, 1}. Those j are enumerated with the Chinese remainder
  theorem. When i ≥ min(q1, q2), a general routine uses other primes from (A); Sylvester–Schur guarantees there is one.

(The source header points to "README_699.md" for these proofs; this README replaces it.)

**Build and run** (64-bit gcc or clang; uses `__int128` and pthreads):

```
clang -O3 -mcpu=native -o w699_v3 w699_v3.c -lpthread      # or: gcc -O3 -march=native ...
CERTFILE=cert.txt SEG=1000000 ./w699_v3 LO HI > log.txt     # searches LO <= n < HI
```

Environment: `THREADS` (default: all cores), `SEG` (segment length), `LOGSEC` (seconds between progress lines),
`XCHECK=1` (re-test every exact test by slow trial division), `CERTFILE` (append one checkpoint line per segment).

Output: `S n i j …` for each near-miss (marked `COUNTEREXAMPLE_TO_OFFICIAL_STATEMENT` if p = i also fails),
`# searched [lo, X)` progress lines, and a final `# done [lo, hi) … failures=…` line.

### Coverage

| Range of n | Program | Log | Checkpoints |
| --- | --- | --- | --- |
| 4 to 10^7 | `w699_v2` (and `w699_v1`) | `results/v2_1e7.txt`, `results/v1_1e7.txt` | none (0.6 s run) |
| 10^7 to 1.27 × 10^11 | `w699_v2`, then re-run with `w699_v3` | `results/run_1e7_1e12.txt`, `results/run_v3_backfill.txt` | `results/cert_v3_backfill.txt`: 126,990 blocks |
| 1.27 × 10^11 to 10^12 | `w699_v3` | `results/run_v3_main.txt` | `results/cert_v3.txt`: 873,000 blocks |

The 10^7 to 10^12 runs used 28 threads on a Mac Studio, Oct 24 to Oct 26, 2026. `run_v3.sh` is the exact command
used for the last two rows. `failures` counts near-misses: the run below 10^7 reports the nine known ones, and every
run above 10^7 ends with `failures=0`.

### Checkpoints: re-check any block yourself

Each checkpoint line covers one block of 10^6 values of n:

```
B lo hi checked candidates fallback near_misses
```

`checked` is the number of n in [lo, hi) that needed any work, `candidates` the number of exact tests, `fallback` the
calls to the general routine, and `near_misses` the near-misses found. Lines are in completion order, not sorted.

Both checkpoint files have contiguous blocks with no gaps or repeats, and their columns sum to the totals in the
matching `# done` line. A block's counts do not depend on the thread count or segment size (`check_v3.sh`), so anyone
can re-run any block and compare:

```
CERTFILE=myblock.txt SEG=1000000 ./w699_v3 543000000000 543001000000
grep '^B 543000000000 ' results/cert_v3.txt
cat myblock.txt
```

`results/reproduce_linux.txt` records three blocks re-run this way with gcc on Linux. All three are identical to the
Mac's lines.

### Checks on the search code

- `brute699.c`: no shortcuts; it decides divisibility with Kummer's theorem instead of Lucas. Its near-misses for
  every n < 3,000 (`results/brute_3000.txt`) match the search exactly.
- `w699_v1` and `w699_v2` agree on the near-misses below 10^7 and on [10^10, 1.01 × 10^10) and
  [999,990,000,000, 10^12) (`build_check.sh`, `top_checks.sh`, `results/v1_*`, `results/v2_*`, `results/top_*`).
- `XCHECK=1` re-tested 2.48 billion exact tests in [10^9, 1.05 × 10^9) and 742 million in [999,999,000,000, 10^12)
  by trial division, with no mismatch (`results/v2_xcheck_1e9.txt`, `results/top_xcheck_1e6.txt`).
- `w699_v3` matches `w699_v2` totals on [10^10, 1.001 × 10^10) with two different segment sizes (`check_v3.sh`,
  `results/chk_*`, `results/check_v3.log`).

## The lemma n ≤ j²

Let g = gcd(C(n, i), C(n, j)). The identity C(n, i) C(n − i, j − i) = C(n, j) C(j, i) shows that C(n, i)/g divides
C(j, i). So g ≥ C(n, i)/C(j, i) ≥ (n/j)^i.

In a counterexample every prime factor of g is below i. Kummer's theorem gives p^(v_p C(n, i)) ≤ n for each prime p.
So g ≤ n^π(i−1), where π counts primes. Together, n^(i − π(i−1)) ≤ j^i. Since π(i − 1) ≤ i/2 for i ≥ 3, n ≤ j².
(For i = 1, 2 there are no counterexamples at all.)

This follows in a few lines from the Erdős–Szekeres identity, so it may well be folklore; credit belongs to that
identity. `smooth2/lemma_check.py` checks it numerically, including on every known near-miss
(`smooth2/lemma_check.out`).

## j ≤ 10^9 for every n (`smooth2/push_j.py`)

By the lemma, a counterexample with j ≤ J has n ≤ X_i := J^(i/(i − k)), where k = π(i − 1). With every n < 10^12
already searched, only n ≥ 10^12 remain. For those, the small-prime part of C(n, i) must be at least (n/J)^i.
By Kummer's theorem, that forces n into a few residue classes modulo large prime powers. `push_j.py` lists every such
n for each i with X_i ≥ 10^12, tests the size condition exactly, and tests every possible j for the survivors with
Lucas's theorem.

Run on Oct 26, 2026 (`push_1e12_1e9.log`, 13 minutes): 50.4 million candidate n for i = 3 to 119. 897 passed the
exact size test (891 with i = 3, 6 with i = 4). None gives a counterexample.

An earlier run with the search at 3 × 10^11 gave j ≤ 3 × 10^8 the same way (`push_3e8.log`).
`test_push.py` checks the residue-class step and compares the survivors with brute force on small ranges
(`test_push.out`). In "strict" mode the same code rediscovers the known near-misses.

## j ≤ 100 without the search (`smooth_analyze.py`, `smooth_bound_note.md`)

In a counterexample with i ≥ 3, the numbers n − 2, n − 1, n have every prime factor ≤ j. Luca and Najman found every
x with x² − 1 free of primes ≥ 100 ([paper](https://arxiv.org/abs/1005.1533),
[erratum](https://www.ams.org/mcom/2014-83-285/S0025-5718-2013-02696-8/)). That gives 787 runs of three consecutive
97-smooth integers, the last ending at n = 407,498,960. Testing all 3,218,514 triples for those n finds no
counterexample (`results/smooth_analyze_out.txt`, `smooth2/check699.out`). An exact sieve of every integer up to
10^10 finds the same 787 runs (`smooth2/sieve_1e10.log`).

The Luca–Najman lists are not included here. Download `oddsort.txt` and `evensort.txt` from Najman's page and run
`python3 -I smooth_analyze.py oddsort.txt evensort.txt`.

## Near-miss families (`fam2/`)

Every known near-miss has n = 2^k (with i = 2) or n = 3^m + 1 (with i = 3). `fam2/onen.c` and `onen.py` find every
near-miss for a single n, all i and all j. They checked every 2^k with k ≤ 62 and every 3^m + 1 with m ≤ 39, up to
about 4.6 × 10^18. The only one beyond 10^7 is (2^41, 2, 285,920,731,515). Here 2^41 − 1 = 13,367 × 164,511,353,
and neither prime divides C(2^41, 285,920,731,515). `fam2/README.txt` describes the validation against brute force.

## Files

| Path | Contents |
| --- | --- |
| `w699_v3.c` | The search with checkpoint lines (used from 1.27 × 10^11) |
| `w699_v2.c`, `w699_v1.c` | Earlier versions used for 10^7 to 1.28 × 10^11 and for cross-checks |
| `brute699.c` | Brute-force reference with no shortcuts |
| `run_v3.sh`, `check_v3.sh`, `build_check.sh`, `top_checks.sh` | Exact commands used for the runs and checks |
| `results/` | Run logs, checkpoint files, cross-check outputs |
| `smooth2/` | `push_j.py` (j ≤ 10^9), its logs and tests; independent j ≤ 100 checks |
| `smooth_analyze.py`, `smooth_bound_note.md` | The j ≤ 100 argument via Luca–Najman |
| `fam2/` | The 2^k and 3^m + 1 family check |

## Credits

The search programs, the arguments, the runs and this write-up were produced by Claude (Anthropic's AI model) at
Paul Lee's direction in October 2026. Argon (Google's Gemini) reviewed the search method and code and the n ≤ j²
argument and found no errors. Muse, a separate AI reviewer, re-derived the j ≤ 100 result with its own code. No human
mathematician has checked the work yet; corrections are welcome as GitHub issues.

## License

MIT (see `LICENSE`).
