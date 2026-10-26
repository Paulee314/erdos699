"""List-free proof of the j<=100 case: a counterexample has n < j^2 <= 10^4, so test every
n < 10^4 and every 3 <= i < j <= min(100, n//2) directly (Lucas for p <= 97; for p > 100,
p | C(n,i), C(n,j) iff n mod p < i)."""
from sympy import primerange, factorint
K = 100
PR = list(primerange(2, K + 1))
def mask(n, p):
    m = 0
    for k in range(K + 1):
        kk, nn, bad = k, n, False
        while kk:
            if kk % p > nn % p: bad = True; break
            kk //= p; nn //= p
        if bad: m |= 1 << k
    return m
ce, strict, tested = [], [], 0
for n in range(8, 10**4):
    J = min(K, n // 2)
    masks = {p: mask(n, p) for p in PR if p <= n}
    first_big = next((t for t in range(min(K, n - 1)) if max(factorint(n - t)) > K), None)
    for i in range(3, J):
        if first_big is not None and first_big < i:
            tested += J - i; continue
        U = 0; Us = 0
        for p, m in masks.items():
            if p >= i and (m >> i) & 1:
                U |= m
                if p > i: Us |= m
        for j in range(i + 1, J + 1):
            tested += 1
            if not (U >> j) & 1: ce.append((n, i, j))
            if not (Us >> j) & 1: strict.append((n, i, j))
print("triples tested:", tested, "counterexamples:", ce, "strict near-misses:", strict)
