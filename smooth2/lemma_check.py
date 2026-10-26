#!/usr/bin/env python3
"""Numerical sanity checks of the valuation lemma behind the bound n <= j^2.

Lemma (from C(n,i) C(n-i,j-i) = C(n,j) C(j,i)):
  for every prime p:  v_p(C(n,i)) <= v_p(C(n,j)) + v_p(C(j,i)).
Hence if p does not divide C(n,j), then v_p(C(n,i)) <= v_p(C(j,i)).

Consequences:
  counterexample (no prime p >= i divides both):  prod_{p>=i} p^{v_p C(n,i)} | C(j,i)
     => (n/j)^i <= C(n,i)/C(j,i) <= prod_{p<i} p^{v_p C(n,i)} <= n^{pi(i-1)}
     => n^{i-pi(i-1)} <= j^i  => n <= j^2   (i >= 3)
  strict near-miss (no prime p > i divides both):  n^{i-pi(i)} <= j^i.
"""
import random
from math import comb
from sympy import primerange, primepi


def vp(m, p):
    c = 0
    while m % p == 0:
        m //= p
        c += 1
    return c


def vp_binom(n, k, p):
    # Legendre / Kummer: (s_p(k) + s_p(n-k) - s_p(n)) / (p-1)
    def s(m):
        t = 0
        while m:
            t += m % p
            m //= p
        return t
    return (s(k) + s(n - k) - s(n)) // (p - 1)


# (a) exhaustive small-n check of the valuation inequality and of p^{v_p C(n,k)} <= n
bad = 0
N = 300
for n in range(2, N + 1):
    ps = list(primerange(2, n + 1))
    for i in range(1, n // 2):
        for j in range(i + 1, n // 2 + 1):
            for p in ps:
                a = vp_binom(n, i, p)
                if p ** a > n:
                    bad += 1
                if a > vp_binom(n, j, p) + vp_binom(j, i, p):
                    bad += 1
print("(a) violations for n<=%d:" % N, bad)

# (b) random large checks with exact binomials
random.seed(1)
bad = 0
for _ in range(3000):
    n = random.randint(10, 10**6)
    j = random.randint(2, n // 2)
    i = random.randint(1, min(j - 1, 40))
    Cni, Cnj, Cji = comb(n, i), comb(n, j) if j < 2000 else None, comb(j, i)
    for p in primerange(2, 200):
        a = vp_binom(n, i, p)
        assert a == vp(Cni, p)
        if a > vp_binom(n, j, p) + vp(Cji, p):
            bad += 1
print("(b) random violations:", bad)

# (c) the strict near-misses found by the exhaustive search satisfy n^{i-pi(i)} <= j^i
near = [(10, 3, 5), (16, 2, 6), (28, 3, 14), (28, 5, 14), (244, 3, 122), (512, 2, 147),
        (2048, 2, 713), (2188, 3, 1094), (1594324, 3, 797162), (2**41, 2, 285920731515)]
for n, i, j in near:
    e = i - int(primepi(i))
    # also the sharper product form: prod_{p>i} p^{v_p C(n,i)} divides C(j,i)
    Cji = comb(j, i)
    big = 1
    for p in primerange(i + 1, n + 1) if n < 10**7 else []:
        a = vp_binom(n, i, p)
        if a:
            big *= p ** a
    div = (Cji % big == 0) if n < 10**7 else None
    print("(c)", (n, i, j), "n^(i-pi(i)) <= j^i:", n ** e <= j ** i,
          " (>i)-part of C(n,i) | C(j,i):", div)

# (d) exponent table i/(i - pi(i-1)) and i/(i - pi(i))
print("(d) i, e_counterex=i/(i-pi(i-1)), e_strict=i/(i-pi(i))")
mx = 0
for i in range(3, 200):
    e1 = i / (i - int(primepi(i - 1)))
    e2 = i / (i - int(primepi(i)))
    mx = max(mx, e1)
    if i <= 16:
        print("   ", i, round(e1, 4), round(e2, 4))
print("    max over 3<=i<200 of counterexample exponent:", mx)
