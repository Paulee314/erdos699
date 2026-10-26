#!/usr/bin/env python3
"""List-independent check: find all x <= LIMIT with x-1, x, x+1 all 97-smooth by an exact
segmented sieve (divide out every prime power p^k, p <= 97, at its multiples)."""
import sys, time
import numpy as np

LIMIT = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10**9
CH = 1 << 24
PR = [p for p in range(2, 98) if all(p % q for q in range(2, int(p**0.5) + 1))]

t0 = time.time()
centers = []
prev_tail = None  # smooth flags of last 2 numbers of previous chunk
lo = 1
while lo <= LIMIT + 1:
    hi = min(lo + CH, LIMIT + 2)  # numbers lo..hi-1
    r = np.arange(lo, hi, dtype=np.int64)
    for p in PR:
        pk = p
        while pk < hi:
            s = (-lo) % pk
            r[s::pk] //= p
            pk *= p
    sm = (r == 1)
    if prev_tail is not None:
        sm = np.concatenate([prev_tail, sm])
        base = lo - 2
    else:
        base = lo
    trip = sm[:-2] & sm[1:-1] & sm[2:]
    idx = np.nonzero(trip)[0]
    for k in idx:
        x = base + int(k) + 1  # center
        if 2 <= x <= LIMIT:
            centers.append(x)
    prev_tail = sm[-2:]
    lo = hi
print("LIMIT", LIMIT, "centers found:", len(centers), "time %.1fs" % (time.time() - t0))
print("largest:", centers[-6:])
with open(sys.argv[2] if len(sys.argv) > 2 else "/dev/null", "w") as fh:
    fh.write("\n".join(map(str, centers)))
