/* w699.c -- exhaustive search for Erdos Problem 699.
 *
 * Problem: is it true that for every 1 <= i < j <= n/2 some prime p >= i divides gcd(C(n,i), C(n,j))?
 * We search for "strict failures": triples (n, i, j), 2 <= i < j <= n/2, such that NO prime p > i divides
 * both C(n,i) and C(n,j). Each strict failure is then tested for the official statement (p = i allowed);
 * a strict failure where also p = i fails would be a counterexample. (i = 1 needs no search: C(n,1) = n and
 * n/gcd(n,j) > 1 divides both n and C(n,j).)
 *
 * Facts used (each proved in README_699.md):
 *  (A) For a prime p > i:  p | C(n,i)  <=>  p divides one of n, n-1, ..., n-i+1.   [v_p(i!) = 0]
 *      So the primes p > i dividing C(n,i) are T_i(n) = { p > i prime : p | n - t for some 0 <= t < i }.
 *  (B) Lucas: p does not divide C(n,j) <=> every base-p digit of j is <= the corresponding digit of n.
 *      In particular, if p | n - t with t < p, the lowest digit of n is t, so j mod p <= t is necessary.
 *  (C) If (n - i, n] contains a prime p (and 2i <= n), then p > n/2 >= j > i and p divides both C(n,i)
 *      and C(n,j) (for p > n/2 and k < p: p | C(n,k) <=> n mod p < k). So a failure needs (n-i, n] prime-free,
 *      i.e. i <= g(n) := n - (largest prime <= n).
 *  Fast path: with q1 = P(n) (largest prime factor of n) and q2 = P(n-1), for every 2 <= i < min(q1, q2)
 *  both q1, q2 lie in T_i(n), so by (B) a failure j must satisfy j == 0 (mod q1) and j mod q2 in {0,1}.
 *  These j are enumerated by CRT; every survivor is checked exactly against all of T_i(n).
 *  When min(q1, q2) <= i the general routine picks other primes of T_i(n) (never empty by Sylvester-Schur).
 *
 * Usage: w699 lo hi      (searches lo <= n < hi; n < 2^63)
 * Env:   THREADS, SEG (segment length, default 1<<22), LOGSEC (default 300)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
typedef unsigned long long u64;
typedef unsigned __int128 u128;

#define OV 8192                       /* overlap: must exceed every prime gap in range */
static u64 *SP; static size_t nSP;    /* primes up to sqrt(hi) (and at least up to 1e5) */
static u64 LO, HI, SEG = 1u << 20;
static double LOGSEC = 300;
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
static u64 next_seg = 0, nsegs = 0, done_segs = 0;
static unsigned char *seg_done;
static u64 n_failures = 0, n_cands = 0, n_exact = 0, n_slow = 0;
static double t0, tlast;
static FILE *OUT;

static double now(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + 1e-9 * ts.tv_nsec; }

/* p | C(n,j) ?  (Lucas / Kummer: some base-p digit of j exceeds that of n) */
static int pdiv_binom(u64 n, u64 j, u64 p) {
    while (j) { if (j % p > n % p) return 1; j /= p; n /= p; }
    return 0;
}
static u64 inv_mod(u64 a, u64 m) {           /* a^{-1} mod m, gcd = 1 */
    long long t = 0, nt = 1; u64 r = m, nr = a % m;
    while (nr) { u64 q = r / nr, tmp; long long tt; tt = t - (long long)q * nt; t = nt; nt = tt; tmp = r - q * nr; r = nr; nr = tmp; }
    if (t < 0) t += (long long)m;
    return (u64)t;
}
static int is_small_prime(u64 x) { if (x < 2) return 0; for (u64 d = 2; d * d <= x; d++) if (x % d == 0) return 0; return 1; }

/* distinct prime factors > lim of x, by trial division with SP (x < SP[last]^2 assumed) */
static int factor_gt(u64 x, u64 lim, u64 *out) {
    int k = 0;
    for (size_t a = 0; a < nSP; a++) { u64 p = SP[a]; if (p * p > x) break;
        if (x % p == 0) { if (p > lim) out[k++] = p; while (x % p == 0) x /= p; } }
    if (x > 1 && x > lim) out[k++] = x;
    return k;
}

#define MAXF 16                       /* distinct primes <= sqrt(hi) per number: < 14 for n < 1e17 */
typedef struct { u64 A; u64 len; u64 *rem; unsigned char *cnt; unsigned *fac; } Buf;   /* covers [A, A+len) */
/* fac[k*MAXF ..] = distinct primes <= sqrt bound dividing A+k, increasing; rem[k] = remaining prime cofactor or 1 */
static inline u64 LP(const Buf *b, u64 m) { u64 k = m - b->A;
    return b->rem[k] > 1 ? b->rem[k] : (b->cnt[k] ? b->fac[k * MAXF + b->cnt[k] - 1] : 1); }
static int XCHECK = 0;

static void report(u64 n, u64 i, u64 j) {
    int ip = is_small_prime(i);
    int both = ip && pdiv_binom(n, i, i) && pdiv_binom(n, j, i);
    pthread_mutex_lock(&mu);
    n_failures++;
    fprintf(OUT, "S %llu %llu %llu %s\n", n, i, j, both ? "p=i_divides_both(official_ok)" : "COUNTEREXAMPLE_TO_OFFICIAL_STATEMENT");
    fflush(OUT);
    pthread_mutex_unlock(&mu);
}

/* exact strict test for (n,i,j): returns 1 if some prime p > i divides both C(n,i) and C(n,j) */
static int strict_ok_slow(u64 n, u64 i, u64 j) {        /* independent: trial-division factoring */
    u64 f[64];
    for (u64 t = 0; t < i; t++) { int k = factor_gt(n - t, i, f);
        for (int a = 0; a < k; a++) if (pdiv_binom(n, j, f[a])) return 1; }
    return 0;
}
static int strict_ok_exact(const Buf *b, u64 n, u64 i, u64 j, u64 *cnt_exact) {
    (*cnt_exact)++;
    int res = 0;
    for (u64 t = 0; t < i && !res; t++) { u64 k = n - t - b->A;
        u64 r = b->rem[k]; if (r > i && pdiv_binom(n, j, r)) { res = 1; break; }
        for (int a = b->cnt[k] - 1; a >= 0; a--) { u64 p = b->fac[k * MAXF + a]; if (p <= i) break;
            if (pdiv_binom(n, j, p)) { res = 1; break; } } }
    if (XCHECK && res != strict_ok_slow(n, i, j)) { fprintf(stderr, "XCHECK MISMATCH n=%llu i=%llu j=%llu\n", n, i, j); exit(7); }
    return res;
}

/* general routine for one (n, i): enumerate all j in (i, n/2] that avoid two chosen primes of T_i */
static void general(const Buf *b, u64 n, u64 i, u64 *cands, u64 *cnt_exact) {
    u64 tq[2], qq[2]; int k = 0;
    for (u64 t = 0; t < i && k < 2; t++) { u64 q = LP(b, n - t); if (q > i) { tq[k] = t; qq[k] = q; k++; } }
    u64 half = n / 2;
    if (k == 0) { fprintf(stderr, "ASSERT: T_i empty at n=%llu i=%llu\n", n, i); exit(5); }
    if (k == 1) {
        u64 q = qq[0];
        for (u64 d = 0; d <= tq[0]; d++) for (u64 j = d; j <= half; j += q) {
            if (j <= i) continue;
            if (pdiv_binom(n, j, q)) continue;
            (*cands)++;
            if (!strict_ok_exact(b, n, i, j, cnt_exact)) report(n, i, j);
        }
        return;
    }
    u128 M = (u128)qq[0] * qq[1]; u64 inv = inv_mod(qq[0] % qq[1], qq[1]);
    for (u64 d1 = 0; d1 <= tq[0]; d1++) for (u64 d2 = 0; d2 <= tq[1]; d2++) {
        u64 dd = (d2 + qq[1] - d1 % qq[1]) % qq[1];
        u128 x = (u128)d1 + (u128)qq[0] * (u64)((u128)dd * inv % qq[1]);
        for (u128 j = x; j <= half; j += M) {
            if (j <= i) continue;
            if (pdiv_binom(n, (u64)j, qq[0]) || pdiv_binom(n, (u64)j, qq[1])) continue;
            (*cands)++;
            if (!strict_ok_exact(b, n, i, (u64)j, cnt_exact)) report(n, i, (u64)j);
        }
    }
}

static void process_segment(u64 s, Buf *b, u64 *loc) {
    u64 S0 = LO + s * SEG, S1 = S0 + SEG; if (S1 > HI) S1 = HI;
    u64 A = S0 > OV + 2 ? S0 - OV : 2;
    b->A = A; b->len = S1 - A;
    for (u64 k = 0; k < b->len; k++) { b->rem[k] = A + k; b->cnt[k] = 0; }
    for (size_t a = 0; a < nSP; a++) {
        u64 p = SP[a]; if (p * p >= S1) break;
        u64 st = (A + p - 1) / p * p;
        for (u64 m = st; m < S1; m += p) { u64 k = m - A; u64 r = b->rem[k];
            do r /= p; while (r % p == 0);
            b->rem[k] = r;
            if (b->cnt[k] >= MAXF) { fprintf(stderr, "ASSERT: MAXF\n"); exit(8); }
            b->fac[k * MAXF + b->cnt[k]++] = (unsigned)p; }
    }
    /* walk: find last prime before S0 */
    u64 last = 0;
    for (u64 m = A; m < S0; m++) if (LP(b, m) == m) last = m;
    if (S0 > 3 && last == 0) { fprintf(stderr, "ASSERT: no prime in overlap before %llu\n", S0); exit(6); }
    u64 cands = 0, cnt_exact = 0, slow = 0;
    for (u64 n = S0; n < S1; n++) {
        if (n >= 2 && LP(b, n) == n) { last = n; continue; }
        if (n < 4) continue;
        u64 g = n - last, imax = g < n / 2 ? g : n / 2;
        if (imax < 2) continue;
        u64 q1 = LP(b, n), q2 = LP(b, n - 1), mq = q1 < q2 ? q1 : q2;
        u64 ifast = imax < mq - 1 ? imax : mq - 1;      /* fast path covers 2 <= i <= ifast */
        if (ifast >= 2) {
            u64 half = n / 2; u128 M = (u128)q1 * q2;
            u64 inv = inv_mod(q1 % q2, q2);
            for (u64 d2 = 0; d2 <= 1; d2++) {
                /* j == 0 mod q1, j == d2 mod q2 */
                u128 x = (u128)q1 * (u64)((u128)d2 * inv % q2);
                for (u128 j = x; j <= half; j += M) {
                    if (j == 0) continue;
                    if (pdiv_binom(n, (u64)j, q1) || pdiv_binom(n, (u64)j, q2)) continue;
                    for (u64 i = 2; i <= ifast && i < j; i++) {
                        cands++;
                        if (!strict_ok_exact(b, n, i, (u64)j, &cnt_exact)) report(n, i, (u64)j);
                    }
                }
            }
        }
        for (u64 i = (ifast >= 2 ? ifast + 1 : 2); i <= imax; i++) { slow++; general(b, n, i, &cands, &cnt_exact); }
    }
    loc[0] += cands; loc[1] += cnt_exact; loc[2] += slow;
}

static void *worker(void *arg) {
    (void)arg;
    Buf b; b.rem = malloc((SEG + OV + 8) * sizeof(u64)); b.cnt = malloc(SEG + OV + 8);
    b.fac = malloc((SEG + OV + 8) * MAXF * sizeof(unsigned));
    for (;;) {
        pthread_mutex_lock(&mu); u64 s = next_seg++; pthread_mutex_unlock(&mu);
        if (s >= nsegs) break;
        u64 loc[3] = {0, 0, 0};
        process_segment(s, &b, loc);
        pthread_mutex_lock(&mu);
        n_cands += loc[0]; n_exact += loc[1]; n_slow += loc[2];
        seg_done[s] = 1; done_segs++;
        double tn = now();
        if (tn - tlast >= LOGSEC) {
            u64 c = 0; while (c < nsegs && seg_done[c]) c++;
            u64 through = LO + c * SEG; if (through > HI) through = HI;
            fprintf(OUT, "# searched [%llu, %llu) elapsed=%.0fs failures=%llu cand=%llu exact=%llu slow=%llu\n",
                    LO, through, tn - t0, n_failures, n_cands, n_exact, n_slow);
            fflush(OUT); tlast = tn;
        }
        pthread_mutex_unlock(&mu);
    }
    free(b.rem); free(b.cnt); free(b.fac);
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s lo hi\n", argv[0]); return 1; }
    LO = strtoull(argv[1], 0, 10); HI = strtoull(argv[2], 0, 10);
    if (LO < 4) LO = 4;
    if (getenv("SEG")) SEG = strtoull(getenv("SEG"), 0, 10);
    if (getenv("LOGSEC")) LOGSEC = atof(getenv("LOGSEC"));
    if (getenv("XCHECK")) XCHECK = atoi(getenv("XCHECK"));
    int T = getenv("THREADS") ? atoi(getenv("THREADS")) : (int)sysconf(_SC_NPROCESSORS_ONLN);
    OUT = stdout;
    /* primes up to max(sqrt(HI)+1, 1e5) -- also used for exact factoring (n < SP[last]^2) */
    u64 lim = 100000; while ((u128)lim * lim < (u128)HI) lim *= 2;
    char *c = calloc(lim + 1, 1); nSP = 0;
    for (u64 x = 2; x <= lim; x++) if (!c[x]) { nSP++; for (u64 y = x * x; y <= lim; y += x) c[y] = 1; }
    SP = malloc(nSP * sizeof(u64)); size_t z = 0;
    for (u64 x = 2; x <= lim; x++) if (!c[x]) SP[z++] = x;
    free(c);
    nsegs = (HI - LO + SEG - 1) / SEG; seg_done = calloc(nsegs + 1, 1);
    t0 = tlast = now();
    fprintf(OUT, "# w699 lo=%llu hi=%llu threads=%d seg=%llu primes<=%llu\n", LO, HI, T, SEG, lim); fflush(OUT);
    pthread_t th[256]; if (T > 256) T = 256;
    for (int a = 0; a < T; a++) pthread_create(&th[a], NULL, worker, NULL);
    for (int a = 0; a < T; a++) pthread_join(th[a], NULL);
    fprintf(OUT, "# done [%llu, %llu) elapsed=%.1fs failures=%llu cand=%llu exact=%llu slow=%llu\n",
            LO, HI, now() - t0, n_failures, n_cands, n_exact, n_slow);
    return 0;
}
