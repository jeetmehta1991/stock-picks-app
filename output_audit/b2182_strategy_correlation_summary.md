# Strategy-return correlation and effective breadth (B2182, zero engine runs)

- IS trades analyzed: 136622 across 183 strategies (>= 30 trades each)
- average pairwise rho: 0.087
- cross-sectional annualized Sharpe: mean -2.437, median -1.970

| scenario | s_bar (shrunk) | rho_bar | implied portfolio Sharpe |
|---|---|---|---|
| N=10 | -2.4373 | 0.0866 | -5.777 |
| N=20 | -2.4373 | 0.0866 | -6.7 |
| N=40 | -2.4373 | 0.0866 | -7.366 |
| greedy_subset | -0.165 | 0.1835 | -0.348 |

Caveats: IS-only estimates of mostly UNVALIDATED strategies - winner's curse compounds at portfolio level (S6-B2178c carries this) / pairwise rho is regime-unstable; the crisis rho is the one that matters and one window cannot measure it / zero-filled non-exit days deflate single-strategy vol; correct grain for combination arithmetic, wrong grain for standalone Sharpe claims
