/* brute699.c -- brute-force reference for Erdos 699 (no pruning).
 * For every 4 <= n < N and 2 <= i < j <= n/2, prints "S n i j" when no prime p > i divides both
 * C(n,i) and C(n,j). Divisibility p | C(n,k) is decided by Kummer's theorem (count of carries
 * when adding k and n-k in base p), independently of w699's Lucas routine. */
#include <stdio.h>
#include <stdlib.h>
static int carries(long n, long k, long p) {   /* number of carries adding k and n-k in base p */
    long a = k, b = n - k, c = 0, cnt = 0;
    while (a || b || c) { long s = a % p + b % p + c; c = s >= p; cnt += c; a /= p; b /= p; }
    return cnt;
}
int main(int argc, char **argv) {
    long N = argc > 1 ? atol(argv[1]) : 1000;
    char *comp = calloc(N + 1, 1); long *pr = malloc(sizeof(long) * (N + 1)); long np = 0;
    for (long x = 2; x <= N; x++) if (!comp[x]) { pr[np++] = x; for (long y = 2 * x; y <= N; y += x) comp[y] = 1; }
    long *T = malloc(sizeof(long) * (N + 1));
    for (long n = 4; n < N; n++)
        for (long i = 2; 2 * i <= n; i++) {
            long nt = 0;
            for (long a = 0; a < np && pr[a] <= n; a++) if (pr[a] > i && carries(n, i, pr[a]) > 0) T[nt++] = pr[a];
            for (long j = i + 1; 2 * j <= n; j++) {
                int ok = 0;
                for (long a = 0; a < nt && !ok; a++) if (carries(n, j, T[a]) > 0) ok = 1;
                if (!ok) printf("S %ld %ld %ld\n", n, i, j);
            }
        }
    return 0;
}
