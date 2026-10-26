#!/usr/bin/env python3
"""Tests for push_j.py: (1) residue-class characterisation of v_p C(n,i) >= c,
(2) survivor generation == brute force on small ranges, (3) strict mode recovers known near-misses."""
import random, math, sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import push_j as P
from sympy import primerange, primepi

random.seed(7)
# (1)
bad = 0
for _ in range(20000):
    i = random.randint(2, 60)
    p = random.choice(list(primerange(2, i + 1)))
    n = random.randint(2 * i + 2, 10**9)
    if random.random() < 0.5:  # bias toward many borrows
        n = (n // p**random.randint(1, 8)) * p**random.randint(1, 8) + random.randint(0, i)
        if n < 2 * i + 2:
            continue
    c = random.randint(0, 12)
    m, lst = P.low_classes(i, p)
    r0 = n % p**m
    _, b, beta = lst[r0]
    if b >= c:
        inclass = True
    elif beta:
        inclass = (n % p**(m + c - b) == r0)
    else:
        inclass = False
    if inclass != (P.vbin(n, i, p) >= c):
        bad += 1
print("(1) class characterisation mismatches:", bad)

# (2) survivors vs brute force
def brute(N0, J, mode, imin, imax):
    out = set()
    for i in range(imin, imax + 1):
        small = list(primerange(2, i + (1 if mode == 'strict' else 0)))
        k = len(small)
        if k >= i:
            continue
        X = P.iroot_floor(J**i, i - k)
        for n in range(max(N0, 2 * (i + 1)), X + 1):
            A = 1
            for q in small:
                A *= q ** P.vbin(n, i, q)
            if A * J**i >= n**i:
                out.add((n, i))
    return out

for (N0, J, mode, imin, imax) in [(200, 40, 'counter', 3, 39), (500, 60, 'counter', 3, 59),
                                  (300, 50, 'strict', 2, 49), (1000, 120, 'strict', 3, 20),
                                  (5000, 300, 'counter', 3, 12)]:
    got = set()
    P.run(N0, J, mode, imax=imax + 1, verbose=False, collect=got, imin=imin)
    exp = brute(N0, J, mode, imin, imax)
    print("(2) N0=%d J=%d %s: generated %d, brute %d, missing %d, extra %d" %
          (N0, J, mode, len(got), len(exp), len(exp - got), len(got - exp)))

# (3) end-to-end strict mode: known strict near-misses
print("(3) strict, N0=21, J=200, i<=20:", P.run(21, 200, 'strict', imax=21, verbose=False))
print("(3) strict, N0=21, J=1200, i in {3,4,5}:", P.run(21, 1200, 'strict', verbose=False, only_i={3, 4, 5}))
print("(3) strict, N0=21, J=1200, i=2:", P.run(21, 1200, 'strict', verbose=False, only_i={2}, imin=2))
