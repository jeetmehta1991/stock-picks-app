# Table A - smc_order_block_bounce

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6d884d139 | commit 6d884d139 at 2026-10-27 10:10:00 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** smc | **status:** STALLED-CAMPAIGN | **R5 fires:** 1340 (closed fires in the exit cube: 1340 of 1340, S6-B3258) | **surviving fires (T1): 0** (survives_pct UNMEASURED)

**T1 VERDICT: UNMEASURED (S6-B3239) - the CURRENT gate's long side reads smc_ob_bullish_tap_recent_5d; short side reads smc_ob_bearish_tap_recent_5d, absent from every R5 fire of that side, so the replay would read a default and no survival, and no offline band level, is measurable from this cube. Per the workflow's T1 gate the campaign RE-LANES TO W-L (engine): a run at the current gate produces fires carrying the key, and the producer bands below are the resim inventory it prices.**

## Formula (Section 1 of the SS6/#183 locked artifact)

```python
fl = s.get('smc_ob_bullish_tap_recent_5d', False) and s.get('rsi_14', 50) < 45 and s.get('price_above_ema_200', False)
fs = s.get('smc_ob_bearish_tap_recent_5d', False) and s.get('rsi_14', 50) > 55 and s.get('below_ema_200', False) and (not _short_borrow_trap_active(s))
```

## Producer bands (resim inventory for the W-L campaign)

The gate's parameters and their defined bands are those of the shared producers - see the smc SPECS family (producer_variant_table) and table_a_bands.py entries for: below_ema_200, price_above_ema_200, smc_ob_bearish_tap_recent_5d, smc_ob_bullish_tap_recent_5d.
