#!/usr/bin/env python3
"""Independent check of the j <= 100 claim for Erdos #699.

Input: Najman's corrected list of x >= 2 with P(x^2-1) < 100 (odd and even files).
Step 1: verify the list's internal consistency (every entry really has P(x^2-1) <= 97,
        and contains every x in [2, 98], which is forced).
Step 2: runs of three consecutive 97-smooth integers (x-1, x, x+1) <=> x in list and x 97-smooth.
        Set n = x+1 (largest of the three).
Step 3: for every such n and every 3 <= i < j <= min(100, n//2), decide directly whether
        some prime p >= i divides gcd(C(n,i), C(n,j)) (Lucas: p | C(n,k) iff some base-p
        digit of k exceeds the corresponding digit of n), and whether some prime p > i does.
Primes > 100: since i < j <= 100 < p, p | C(n,k) iff n mod p < k, so p divides both iff
p | n-t for some t < i.
"""
import sys
from sympy import primerange, factorint

import os
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ext_najman") + "/"  # oddsort.txt + evensort.txt from Najman's page (not included)
PR = list(primerange(2, 101))  # primes <= 97


def smooth97(m):
    for p in PR:
        while m % p == 0:
            m //= p
    return m == 1


def load():
    xs = []
    for f in ("oddsort.txt", "evensort.txt"):
        with open(DIR + f) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    xs.append(int(line))
    return xs


def digits(n, p):
    d = []
    while n:
        d.append(n % p)
        n //= p
    return d


def divmask(n, p, K=100):
    """bitmask over k in [0,K]: bit k set iff p | C(n,k) (Lucas/Kummer)."""
    nd = digits(n, p)
    m = 0
    for k in range(K + 1):
        kd = digits(k, p)
        if len(kd) > len(nd):
            # k > n: C(n,k)=0, not relevant (k <= n/2 always here)
            m |= 1 << k
            continue
        if any(kd[t] > nd[t] for t in range(len(kd))):
            m |= 1 << k
    return m


def main():
    xs = load()
    print("entries:", len(xs), "distinct:", len(set(xs)))
    S = set(xs)
    # consistency: every listed x has x^2-1 97-smooth
    bad = [x for x in xs if not smooth97(x * x - 1)]
    print("entries failing P(x^2-1)<100:", len(bad), bad[:5])
    missing_small = [x for x in range(2, 99) if x not in S]
    print("x in [2,98] missing from list:", missing_small)
    print("min x:", min(xs), "max x:", max(xs))

    centers = sorted(x for x in S if smooth97(x))
    print("centers x with x-1,x,x+1 all 97-smooth:", len(centers))
    print("largest centers:", centers[-5:])
    ns = [x + 1 for x in centers]
    # maximal runs of consecutive centers -> maximal runs of >=3 consecutive smooth ints
    runs = []
    for x in centers:
        if runs and runs[-1][1] == x - 1:
            runs[-1][1] = x
        else:
            runs.append([x, x])
    print("maximal runs of >=3 consecutive 97-smooth ints:", len(runs),
          "; longest:", max(r[1] - r[0] + 3 for r in runs))
    ns_eligible = [n for n in ns if n // 2 >= 4]
    print("n values (=x+1) total:", len(ns), " with n//2 >= 4:", len(ns_eligible))

    total = 0
    counterex = []
    strict = []
    rescued_only_by_i = []
    for n in ns_eligible:
        J = min(100, n // 2)
        masks = {p: divmask(n, p) for p in PR if p <= n}
        # first t such that n-t has a prime factor > 100 (those primes divide both iff t < i)
        first_big = None
        for t in range(0, 100):
            if n - t < 2:
                break
            f = factorint(n - t)
            if max(f) > 100:
                first_big = t
                break
        for i in range(3, J):
            big = first_big is not None and first_big < i
            for j in range(i + 1, J + 1):
                total += 1
                ps = [p for p in PR if p >= i and (masks.get(p, 0) >> i) & 1 and (masks.get(p, 0) >> j) & 1]
                # primes between 100 and j: none (j<=100). primes > 100: 'big'
                ok_ge = big or len(ps) > 0
                ok_gt = big or any(p > i for p in ps)
                if not ok_ge:
                    counterex.append((n, i, j))
                if not ok_gt:
                    strict.append((n, i, j, ps))
    print("triples tested:", total)
    print("counterexamples (no prime >= i):", counterex)
    print("strict near-misses (no prime > i):", strict)


if __name__ == "__main__":
    main()
