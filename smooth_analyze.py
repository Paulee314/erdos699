"""Erdos #699, j <= 100: use the complete list of x with P(x^2-1) < 100 (Luca-Najman, corrected list from Najman's page:
oddsort.txt + evensort.txt, 16223 numbers) to find every n with n-2, n-1, n all 97-smooth, then test every such n directly.
Usage: python3 -I analyze.py oddsort.txt evensort.txt"""
import sys
PR = [p for p in range(2, 100) if all(p % q for q in range(2, int(p ** .5) + 1))]   # primes < 100
def smooth(m):
    for p in PR:
        while m % p == 0: m //= p
    return m == 1
xs = []
for f in sys.argv[1:]:
    xs += [int(l) for l in open(f) if l.strip()]
print("numbers:", len(xs), "distinct:", len(set(xs)), "max:", max(xs))
bad = [x for x in xs if not smooth(x * x - 1)]
print("entries with P(x^2-1) >= 100:", len(bad))
# Every x with P(x^2-1)<100 and x itself 97-smooth gives the run x-1, x, x+1. n = x+1 is the top of the run.
runs = sorted(x + 1 for x in xs if x >= 2 and smooth(x))
print("runs of three consecutive 97-smooth integers (top n):", len(runs), " largest n:", runs[-1])
# sanity: brute force for small range must give exactly the same runs
B = 2 * 10 ** 6
sm = [False, True] + [smooth(m) for m in range(2, B + 2)]
brute = [n for n in range(3, B + 1) if sm[n] and sm[n - 1] and sm[n - 2]]
print("brute-force runs up to", B, ":", len(brute), " match list:", brute == [n for n in runs if n <= B])
open("runs_top_n.txt", "w").write("\n".join(map(str, runs)) + "\n")

# Direct test of #699 for every such n and all 3 <= i < j <= min(100, n/2) (i = 1, 2 are always fine).
def kummer(n, k, p):                    # p | C(n,k) iff adding k and n-k in base p carries
    a, b, c = k, n - k, 0
    while a or b or c:
        s = a % p + b % p + c; c = s >= p
        if c: return True
        a //= p; b //= p
    return False
def primes_of(m):
    out, d = set(), 2
    while d * d <= m:
        while m % d == 0: out.add(d); m //= d
        d += 1
    if m > 1: out.add(m)
    return out
counter, strict, checked = [], [], 0
for n in runs:
    J = min(100, n // 2)
    fac = {}                             # prime factors of n - t, t < J
    for t in range(J):
        fac[t] = primes_of(n - t)
    for i in range(3, J):
        big = set().union(*(fac[t] for t in range(i)))            # primes dividing n(n-1)...(n-i+1)
        Pi = sorted(p for p in big if p > i and kummer(n, i, p))  # all primes > i dividing C(n,i) (all of them do)
        for j in range(i + 1, J + 1):
            checked += 1
            if any(kummer(n, j, p) for p in Pi): continue
            strict.append((n, i, j))
            if not (len(primes_of(i)) == 1 and i in primes_of(i) and kummer(n, i, i) and kummer(n, j, i)):
                counter.append((n, i, j))
print("triples checked:", checked)
print("strict near-misses (no prime > i shared), j <= 100:", strict)
print("COUNTEREXAMPLES:", counter)
