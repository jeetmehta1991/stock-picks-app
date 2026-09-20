# Table A - smc_order_block_bounce

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit f55b7c1e7 at 2026-09-19 23:26:39 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** smc | **status:** STALLED-CAMPAIGN | **R5 fires:** 1340 | **surviving fires (T1): 0** (survives_pct 0.0)

**T1 VERDICT: 0 of the R5 fires survive the CURRENT gate - no offline band level is measurable from this cube. Per the workflow's T1 gate the campaign RE-LANES TO W-L (engine): the producer bands below are the resim inventory it prices.**

## Formula (Section 1 of the SS6/#183 locked artifact)

```python
fl = s.get('smc_ob_bullish_tap_recent_5d', False) and s.get('rsi_14', 50) < 45 and s.get('price_above_ema_200', False)
fs = s.get('smc_ob_bearish_tap_recent_5d', False) and s.get('rsi_14', 50) > 55 and s.get('below_ema_200', False) and (not _short_borrow_trap_active(s))
```

## Producer bands (resim inventory for the W-L campaign)

The gate's parameters and their defined bands are those of the shared producers - see the smc SPECS family (producer_variant_table) and table_a_bands.py entries for: below_ema_200, price_above_ema_200, smc_ob_bearish_tap_recent_5d, smc_ob_bullish_tap_recent_5d.
