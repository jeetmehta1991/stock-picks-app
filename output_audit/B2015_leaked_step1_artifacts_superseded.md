# THE 11 PRE-B1718 STEP-1 ARTIFACTS AND THEIR HONEST SUCCESSORS (B2015 / I2, owner-approved 2026-08-22)

These 11 grid artifacts were produced before B1718 closed the P0-2 selection
leak: their STEP-1 rankings sorted on the HOLDOUT Sharpe. Their per-row
statistics are real measurements; their RANKING ORDER is the leak. None is
deleted - each is an incident record - and none needs a re-run, because an
honest successor already exists for every one:

| leaked artifact (ranking = holdout, LEAKED) | honest successor (ranks in-sample) |
|---|---|
| b1608_cfg2_grid.json | b1817_cfg2_grid_minn10.json |
| b1611_cfg1_grid.json | b1817_cfg1_grid_minn10.json |
| b1611_cfg2_grid.json | b1817_cfg2_grid_minn10.json |
| b1615_cfg1_grid.json | b1817_cfg1_grid_minn10.json |
| b1615_cfg2_grid.json | b1817_cfg2_grid_minn10.json (b1819_cfg2_verify.json confirms) |
| b1678_w1_span21_grid.json | b1718_p0fix_span21.json |
| b1678_w1_span50_grid.json | b1718_p0fix_span50.json |
| b1714_regrade_span21.json | b1718_p0fix_span21.json |
| b1714_regrade_span50.json | b1718_p0fix_span50.json |
| b1715_leak_span21.json | b1718_p0fix_span21.json (b1715 is the LEAK MEASUREMENT itself - kept as the incident record; also the B1770/B1991 rho input, where its is_sharpe/holdout PAIRS are the data and the ranking order is irrelevant) |
| b1715_leak_span50.json | b1718_p0fix_span50.json (same) |

**Why no re-computation:** 9 of the 11 never recorded IS-side statistics, so
an offline re-rank on the honest key is impossible from the artifact - and a
re-grade would only reproduce what the successor files already are. The two
that do carry `is_sharpe` (the b1715 pair) exist precisely to PRESERVE the
leaked ordering beside the honest key for the rho analyses.

**Rule for readers:** never quote a top-N from the left column; quote the
right column. Field census by executed probe at B2015 (rows/keys inventoried
per file); the successor identities follow the S6-B1923b measurement that
only these 11 of the 17 key-lacking artifacts carry the leak.
