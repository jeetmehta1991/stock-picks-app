# B700 Candle Diagnostics Report (2026-06-11)

# Source: scripts/run_b700_candle_diagnostics.py per CHECKLIST #77

Universe: 30 alphabetical T1a PIT-active tickers (['A', 'AAPL', 'ABBV', 'ABNB', 'ABT'] ...).
Train through 2023-12-31; test 2024-01-01 onward. Barrier race: +2x ATR target, -1x ATR stop, 10-bar horizon.

Reviewer-asked, runnable-NOW diagnostics on the trustworthy candle half of the cluster (technical.compute_candles producer; not affected by chart_patterns harness gap or repaint risk).

## Diagnostic 1: CC-D redundancy hypothesis

**Reviewer's claim:** morning_star + bullish_engulfing + doji_at_support all fire on the same setup (bullish reversal at support after decline). High Jaccard overlap of fire-bar sets -> effective N = 1, not 3.

### Fire counts (across all tickers, train+test combined)

| Strategy | Total fires |
|---|---:|
| morning_star (with location+volume gates) | 437 |
| bullish_engulfing (with location+volume gates) | 170 |
| doji_at_support (with location+volume gates) | 134 |

### Pairwise Jaccard overlap

| Pair | Intersection | Union | Jaccard | n_tickers |
|---|---:|---:|---:|---:|
| morning_star x bullish_engulfing | 6 | 601 | 0.01 | 30 |
| morning_star x doji_at_support | 0 | 571 | 0.0 | 30 |
| bullish_engulfing x doji_at_support | 0 | 304 | 0.0 | 30 |

**Interpretation:**
- Jaccard near 1.0 -> patterns fire on (nearly) the same bars -> 1 effective strategy, not 3
- Jaccard near 0.0 -> patterns are orthogonal -> 3 distinct strategies
- Jaccard in middle -> some overlap but each pattern catches independent bars

## Diagnostic 2: CC-E confronting test

**Reviewer's claim:** "Doc treats 'Nison documented it' as 'it has edge.' Those are different. Run conditional_add_test where existing = location+volume gates only, candidate = the candle pattern. If the pattern doesn't lift conditional follow-through, the strategy's edge is in the location+volume, not the pattern."

### Verdicts

| Strategy | Base FT (location+vol) | With FT (+ pattern) | Kept frac | Verdict |
|---|---:|---:|---:|---|
| morning_star | 0.3636 (n=572) | None (n=0) | 0% | **DEFER** |
|   |   |   |   | n=0 too few |
| bullish_engulfing | 0.3636 (n=572) | None (n=0) | 0% | **DEFER** |
|   |   |   |   | n=0 too few |
| doji_at_support | 0.3636 (n=572) | 0.2258 (n=31) | 5% | **REJECT_HARMFUL** |
|   |   |   |   | pattern LOWERS FT 0.364->0.226 |

**Reviewer's confrontation:**
- ADD -> the candle pattern DOES earn its slot; reviewer's hypothesis REFUTED for that strategy
- REJECT_REDUNDANT -> the candle pattern doesn't lift conditional FT; reviewer's hypothesis CONFIRMED -- strategy's edge is in location+volume not the candle gate
- REJECT_HARMFUL -> the candle pattern actively LOWERS FT (anti-selects); strategy needs structural rethink
- DEFER -> insufficient surviving sample to judge; needs larger universe or longer window

## Caveats

- 30-ticker sample is a hypothesis-generating run, not a deployment verdict. Full-universe post-B660 re-run with measured fire counts will be authoritative.
- Candle pattern proxies are simplified (not the exact strat_* fire logic). Goal is to test the REVIEWER'S HYPOTHESIS not validate the production strategies.
- Train/test split: pre-2024 train, 2024+ test. Held-out FT used for verdict.
- Per `feedback_local_changes_default_global_needs_approval`, these results are EVIDENCE for owner decisions, not autonomous code-change triggers.