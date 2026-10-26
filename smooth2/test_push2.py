from sympy import primerange
import sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_push.py")).read().split("# (2) survivors vs brute force")[1].split("# (3)")[0].split("for (N0, J, mode")[0], globals())
import push_j as P
import push_j as P
for (N0, J, mode, imin, imax) in [(30, 40, 'counter', 3, 39), (100, 80, 'counter', 3, 79),
                                  (400, 300, 'counter', 3, 40), (3000, 1500, 'counter', 3, 12),
                                  (20000, 3000, 'counter', 3, 9), (5000, 2000, 'strict', 2, 10)]:
    got = set()
    P.run(N0, J, mode, imax=imax + 1, verbose=False, collect=got, imin=imin)
    exp = brute(N0, J, mode, imin, imax)
    print("(2b) N0=%d J=%d %s i<=%d: generated %d, brute %d, missing %d, extra %d" %
          (N0, J, mode, imax, len(got), len(exp), len(exp - got), len(got - exp)))
    # end-to-end: counterexamples should be none
    if mode == 'counter':
        print("     counterexamples found:", P.run(N0, J, mode, imax=imax + 1, verbose=False, imin=imin))
