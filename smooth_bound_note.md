# #699: no counterexample with j <= 100, for any n (working note, 2026-10-24, Claude)

Status: computed and cross-checked; Argon review pending. The erdosproblems.com #699 forum thread (4 comments, read
2026-10-24) does not mention this reduction. Not yet checked against the wider literature.

## Claim
For every n and every 1 <= i < j <= min(n/2, 100), some prime p >= i divides both C(n,i) and C(n,j).

## Argument
Let (n, i, j) be a counterexample (no prime p >= i divides both).
1. i >= 3. For i = 1, 2 any common prime factor works, and gcd(C(n,i), C(n,j)) > 1 for 1 <= i < j < n
   (Erdős–Szekeres: C(n,i)/gcd divides C(j,i) < C(n,i)).
2. If a prime p > j divides n - t for some 0 <= t < i, then p | C(n,i) (p > i so v_p(i!) = 0), and n mod p = t < i < j with
   j < p a single base-p digit, so p | C(n,j) by Lucas. That p >= i would divide both. So n, n-1, ..., n-i+1 have all prime
   factors <= j.
3. With i >= 3 and j <= 100: n-2, n-1, n are three consecutive integers with all prime factors <= 97. Put x = n-1: then
   x^2 - 1 = (n-2) n and x are both 97-smooth.
4. Luca–Najman (Math. Comp. 80 (2011) 429–435; erratum Math. Comp. 83 (2014) 337) determine all x with P(x^2-1) < 100.
   Najman's page gives the corrected list as oddsort.txt + evensort.txt (16,223 numbers; sha256 035f2e73... / 05dd3086...,
   downloaded 2026-10-24 to Erdos/e699/ext_najman/).
5. smooth_analyze.py: every listed x really has P(x^2-1) < 100; the x that are themselves 97-smooth give 787 runs of three
   consecutive 97-smooth integers, the largest ending at n = 407,498,960 (agrees with the paper's Corollary 6, so the erratum
   did not change it). Cross-check: brute force over n <= 2,000,000 finds the same 772 runs.
6. For each of those 787 n, all 3,218,514 triples with 3 <= i < j <= min(100, n/2) were tested directly (Kummer carries;
   primes > i of C(n,i) from the factorization of n(n-1)...(n-i+1)). Strict near-misses (no prime > i shared): only
   (10,3,5), (28,3,14), (28,5,14), all rescued by p = i. Counterexamples: none.
   (Independently, the exhaustive w699 search covers every n <= 1.27e11, which contains all 787 n.)

## Rests on
The completeness of the corrected Luca–Najman list (a published, refereed computation), plus the short argument above.

## Extensions
- Larger j needs complete lists of consecutive y-smooth triples for y > 100; Conrey–Holmstrom–McLaughlin "Smooth neighbors"
  (arXiv:1212.5161) lists are heuristic (not proven complete), so they would give only a conditional statement.
- Weaker but proof-light: Lehmer (1964) consecutive 41-smooth pairs end at 63,927,525,376, giving j <= 42 from pairs alone.

## Corrections to the Argon note Paul shared
- "13,325 solutions, errata to 16,167": the paper already says 16,167; the corrected list on Najman's page has 16,223.
- "n <= 814,997,918": 814,997,917 = 2027 x 402071, so that is not a smooth triple; the true bound is 407,498,960.
- "166,055,401,586,083,680": that is the largest consecutive 89-smooth pair (OEIS A002072), not the 97 bound.
