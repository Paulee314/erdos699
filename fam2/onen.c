// Single-n strict near-miss finder for Erdos #699.
// stdin lines: n i k p_1 ... p_k   where {p} = every prime p > i dividing C(n,i)
// For each line: enumerate every j in (i, n/2] whose base-p digits are all <= n's digits for the
// prime p with the fewest such j (Lucas: exactly the j with p not dividing C(n,j)), then require the
// same for every other p. Survivors are strict near-misses (no prime > i divides both binomials).
// stdout: n i chosen_p candidates survivors [j ...]
#include <stdio.h>
#include <stdlib.h>
typedef unsigned long long u64;
#define MAXP 4096
static u64 N, LIM, I;
static int K, best;
static u64 P[MAXP];
static int L; static u64 d[70], pw[70];
static u64 cands, nsurv, surv[1000];

static int ok_other(u64 j) {               // 1 if no other prime divides C(N,j)
    for (int s = 0; s < K; s++) {
        if (s == best) continue;
        u64 q = P[s], jj = j, nn = N;
        while (jj) { if (jj % q > nn % q) return 0; jj /= q; nn /= q; }
    }
    return 1;
}
static void dfs(int k, u64 s) {
    if (k < 0) {
        if (s <= I) return;
        cands++;
        if (ok_other(s)) { if (nsurv < 1000) surv[nsurv] = s; nsurv++; }
        return;
    }
    for (u64 e = 0; e <= d[k]; e++) {
        u64 v = s + e * pw[k];
        if (v > LIM) break;
        dfs(k - 1, v);
    }
}
int main(void) {
    while (scanf("%llu %llu %d", &N, &I, &K) == 3) {
        for (int s = 0; s < K; s++) scanf("%llu", &P[s]);
        LIM = N / 2;
        if (K == 0) {   // no prime > i divides C(n,i): every j survives; report without enumerating
            printf("%llu %llu 0 %llu %llu ALL\n", N, I, LIM - I, LIM - I); continue;
        }
        long double bc = 1e300L; best = 0;
        for (int s = 0; s < K; s++) {        // count of digit-dominated j <= n (upper bound for <= n/2)
            long double c = 1; u64 nn = N;
            while (nn) { c *= (long double)(nn % P[s] + 1); nn /= P[s]; }
            if (c < bc) { bc = c; best = s; }
        }
        u64 p = P[best], nn = N; L = 0; u64 w = 1;
        while (nn) { d[L] = nn % p; pw[L] = w; L++; nn /= p; if (nn) w *= p; }
        cands = nsurv = 0;
        dfs(L - 1, 0);
        printf("%llu %llu %llu %llu %llu", N, I, p, cands, nsurv);
        for (u64 s = 0; s < nsurv && s < 1000; s++) printf(" %llu", surv[s]);
        printf("\n"); fflush(stdout);
    }
    return 0;
}
