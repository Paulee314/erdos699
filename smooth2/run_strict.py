import sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import push_j as P
N0 = int(float(sys.argv[1])); J = int(float(sys.argv[2]))
print(P.run(N0, J, 'strict', imin=2))
