#!/usr/bin/env python3
"""Rigorous extension: given that all n < N0 have been searched exhaustively, show there is no
counterexample (n,i,j) to Erdos #699 with j <= J (any n), or list the (n,i,j) that must be
checked by hand.

mode 'counter': counterexample  = no prime p >= i divides g = gcd(C(n,i),C(n,j)).
mode 'strict' : strict near-miss = no prime p >  i divides g.
Let SMALL = primes < i (counter) or primes <= i (strict), k = |SMALL|.

Lemma (Erdos-Szekeres identity C(n,i)C(n-i,j-i) = C(n,j)C(j,i)):  g >= C(n,i)/C(j,i) >= (n/j)^i.
In a counterexample / near-miss all primes of g lie in SMALL, so
    g <= A(n,i) := prod_{p in SMALL} p^{v_p C(n,i)} <= n^k        (p^{v_p C(n,k)} <= n).
Hence (n/J)^i <= A(n,i), so n <= X_i := J^{i/(i-k)}, and on a dyadic block [N,2N):
    max_{p in SMALL} p^{v_p C(n,i)} >= G := (N/J)^{i/k}.
Kummer: v_p C(n,i) = #borrows in n - i (base p).  With m = #digits of i in base p and r = n mod p^m,
    v_p C(n,i) = b(r) + beta(r) * z,   z = number of zero digits of n from position m upward,
so v_p C(n,i) >= c  <=>  b(r) >= c  or  (beta(r) = 1 and n == r mod p^{m+c-b(r)}).
Enumerate those residue classes for c = c_min(p) (least c with p^c >= G), test A(n,i) >= (n/J)^i
exactly, then for survivors find every j <= J that could work and test it exactly via Lucas.
"""
import sys, math, time
from sympy import primerange, factorint, isprime


def digits(n, p):
    d = []
    while n:
        d.append(n % p)
        n //= p
    return d


def ssum(n, p):
    s = 0
    while n:
        s += n % p
        n //= p
    return s


def vbin(n, k, p):
    return (ssum(k, p) + ssum(n - k, p) - ssum(n, p)) // (p - 1)


def divides_binom(p, n, k):
    """p | C(n,k) iff some base-p digit of k exceeds that of n (Lucas)."""
    while k:
        if k % p > n % p:
            return True
        k //= p
        n //= p
    return False


def iroot_floor(x, r):
    """largest y with y^r <= x"""
    y = int(round(x ** (1.0 / r))) if x < 1 << 1000 else int(math.exp(math.log(x) / r))
    y = max(y, 1)
    while y ** r > x:
        y -= 1
    while (y + 1) ** r <= x:
        y += 1
    return y


def low_classes(i, p):
    idig = digits(i, p)
    m = len(idig)
    out = []
    for r in range(p ** m):
        rr = r
        borrow = 0
        b = 0
        for kk in range(m):
            d = rr % p - idig[kk] - borrow
            rr //= p
            if d < 0:
                borrow = 1
                b += 1
            else:
                borrow = 0
        out.append((r, b, borrow))
    return m, out


def exact_js(n, i, J, mode):
    """all j in (i, min(J, n//2)] for which (n,i,j) is a counterexample (mode counter) or strict
    near-miss (mode strict). Complete: uses the largest prime P > i dividing C(n,i)."""
    Q = set()
    for t in range(i):
        for p in factorint(n - t):
            if p > i:
                Q.add(p)
    if mode == 'counter' and isprime(i) and divides_binom(i, n, i):
        Q.add(i)
    P = max(q for q in Q if q > i)  # exists by Sylvester-Schur since n >= 2i
    v = vbin(n, i, P)
    t = n % P
    assert t < i
    PV = P ** v
    jmax = min(J, n // 2)
    res = []
    k = 1
    while k * PV <= jmax:
        for s in range(t + 1):
            j = k * PV + s
            if i < j <= jmax:
                if not any(divides_binom(q, n, j) for q in Q):
                    res.append(j)
        k += 1
    return res


def run(N0, J, mode, imax=None, verbose=True, only_i=None, collect=None, imin=3):
    t0 = time.time()
    lnJ, lnN0 = math.log(J), math.log(N0)
    # pi(x) table for i up to J
    LIM = J if imax is None else min(J, imax)
    # Rosser-Schoenfeld: pi(x) < 1.25506 x / ln x (x > 1), so for ln i > 1.25506,
    # e(i) = i/(i-k) <= 1/(1 - 1.25506/ln i), which decreases in i.  Beyond the point where
    # this bound times ln J is < ln N0, no i needs enumeration.
    if lnN0 > lnJ:
        need_ln = 1.25506 / (1.0 - lnJ / lnN0)
        rs = int(math.exp(need_ln)) + 2
        LIM = min(LIM, max(rs, 3))
    sieve = bytearray([1]) * (LIM + 2)
    sieve[0:2] = b'\x00\x00'
    for q in range(2, int((LIM + 1) ** 0.5) + 1):
        if sieve[q]:
            sieve[q * q::q] = bytearray(len(sieve[q * q::q]))
    need = []
    cnt = 0  # pi(i-1) as we go
    for i in range(2, LIM):
        # cnt = pi(i-1)
        k = cnt + (1 if (mode == 'strict' and sieve[i]) else 0)
        if i >= imin and k < i:
            e = i / (i - k)
            if e * lnJ >= lnN0 - 1e-9:  # float screen; exact X computed below
                need.append((i, k))
        if sieve[i]:
            cnt += 1
    if only_i is not None:
        need = [(i, k) for (i, k) in need if i in only_i]
    if verbose:
        print("mode=%s N0=%d J=%d : i values needing enumeration: %d  %s" %
              (mode, N0, J, len(need), [i for i, _ in need][:60]))
    found = []
    total_cand = 0
    for i, k in need:
        X = iroot_floor(J ** i, i - k)
        if X < N0:
            continue
        small = [p for p in primerange(2, i + (1 if mode == 'strict' else 0))]
        assert len(small) == k
        cls = {p: low_classes(i, p) for p in small}
        Ji = J ** i
        cand_i = 0
        surv_i = 0
        N = N0
        while N <= X:
            hi = min(2 * N - 1, X)
            NJ = N ** i  # compare p^(c k) * J^i >= N^i
            seen = set()
            for p in small:
                # least c with p^(c*k) * J^i >= N^i
                c = 0
                pc = 1
                while (pc ** k) * Ji < NJ:
                    c += 1
                    pc *= p
                if pc > hi:
                    continue
                m, lst = cls[p]
                for (r, b, beta) in lst:
                    if b >= c:
                        mu = p ** m
                    elif beta:
                        mu = p ** (m + c - b)
                    else:
                        continue
                    start = N + ((r - N) % mu)
                    for n in range(start, hi + 1, mu):
                        if n in seen or n < 2 * (i + 1):
                            continue
                        seen.add(n)
                        cand_i += 1
                        A = 1
                        for q in small:
                            A *= q ** vbin(n, i, q)
                        if A * Ji >= n ** i:
                            surv_i += 1
                            if collect is not None:
                                collect.add((n, i))
                            else:
                                for j in exact_js(n, i, J, mode):
                                    found.append((n, i, j))
            N *= 2
        total_cand += cand_i
        if verbose and (cand_i or surv_i):
            print("  i=%d k=%d X=%.3g candidates=%d survivors(A-test)=%d" % (i, k, X, cand_i, surv_i))
    if verbose:
        print("total candidates %d, found %s, time %.1fs" % (total_cand, found, time.time() - t0))
    return found


if __name__ == "__main__":
    mode = sys.argv[1]
    N0 = int(float(sys.argv[2]))
    J = int(float(sys.argv[3]))
    run(N0, J, mode)
