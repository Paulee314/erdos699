# independent brute force: every (n,i,j), 2<=i<j<=n/2, gcd with all primes <= i stripped; no Lucas/Kummer, no window rule
import sys
from math import comb, gcd
lo, hi = int(sys.argv[1]), int(sys.argv[2])
for n in range(lo, hi + 1):
    C = [comb(n, k) for k in range(n // 2 + 1)]
    for i in range(2, n // 2):
        for j in range(i + 1, n // 2 + 1):
            g = gcd(C[i], C[j])
            for r in range(2, i + 1):
                while g % r == 0: g //= r
            if g == 1: print(n, i, j)
