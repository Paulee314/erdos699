#!/usr/bin/env python3
"""Driver for onen.c: every strict near-miss (n, i, j) of Erdos #699 for the given n, all i and j.
Usage: onen.py n [n ...]   (n may be an expression such as 2**48 or 3**31+1)
i runs from 2 to n - (largest prime <= n): a prime in (n - i, n] divides both binomials, so larger i are rescued.
Each survivor is re-checked with exact integer arithmetic: gcd(C(n,i), C(n,j)) with every prime <= i stripped must be 1
(only feasible for small n), else by Kummer carry counts; then p = i is tested to separate near-miss from counterexample."""
import sys, subprocess
from sympy import factorint, prevprime, isprime
from math import comb, gcd

HERE = sys.path[0]

def carries(a, b, p):          # number of carries adding a and b in base p = v_p(C(a+b, a)) (Kummer)
    c = k = 0
    while a or b or c:
        s = a % p + b % p + c
        c = 1 if s >= p else 0; k += c; a //= p; b //= p
    return k

def run(n):
    q0 = prevprime(n + 1) if n > 2 else 2
    imax = min(n - q0, n // 2 - 1)
    if imax < 2: return []
    fac = [factorint(n - t) for t in range(imax)]
    lines = []
    for i in range(2, imax + 1):
        S = sorted({p for t in range(i) for p in fac[t] if p > i})
        lines.append(f"{n} {i} {len(S)} {' '.join(map(str, S))}")
    out = subprocess.run([f"{HERE}/onen"], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True).stdout
    res = []
    for line in out.split("\n"):
        if not line: continue
        f = line.split()
        if f[-1] == "ALL": raise SystemExit(f"unexpected: no prime > i in C(n,i): {line}")
        nn, i, p, cand, ns = map(int, f[:5])
        js = list(map(int, f[5:]))
        assert len(js) == ns, "more than 1000 survivors"
        for j in js:
            # independent re-check of the survivor
            if n <= 5000:
                g = gcd(comb(n, i), comb(n, j))
                for r in range(2, i + 1):
                    while g % r == 0: g //= r
                assert g == 1, (n, i, j, "shares a prime > i")
            else:
                S = {p for t in range(i) for p in fac[t] if p > i}
                for p in S:
                    assert carries(i, n - i, p) > 0 and carries(j, n - j, p) == 0, (n, i, j, p)
            ce = not (isprime(i) and carries(i, n - i, i) > 0 and carries(j, n - j, i) > 0)
            res.append((n, i, j, "COUNTEREXAMPLE" if ce else "p=i rescues"))
        res_c = cand
    return res

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        n = eval(arg, {"__builtins__": {}})
        r = run(n)
        print(arg, n, "none" if not r else " ; ".join(f"S {a} {b} {c} {d}" for a, b, c, d in r), flush=True)
