# Phase 1A-beta strategy wiring + bug audit (Batch 392)

**Source (per CHECKLIST #77):** owner directive 2026-05-26 - deep audit of wiring and per-strategy bugs. Identify silent gaps, engine consumption gaps, errors. Generator: `scripts/strategy_wiring_audit.py`.

## Summary

- Active strategies audited: 185
- Producer-key index: 1243 keys across all signal modules
- Strategies clean (0 findings): 159
- Strategies with findings: 26

### Findings by bug class

| Class | Count | Severity |
|---|---:|---|
| `SYNTHESIZE_NEVER_FIRES` | 25 | HIGH (logic bug; cannot fire even with best inputs) |
| `SYNTHESIZE_ALWAYS_FIRES` | 1 | MEDIUM (no real gating with worst inputs) |

## Bug class: `SYNTHESIZE_NEVER_FIRES` (25 findings)

| Strategy | Clause / key | Issue |
|---|---|---|
| avwap_20high_rejection_short | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| camarilla_rsi_obv | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| camarilla_rsi_obv_short | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| camarilla_s3_bounce | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| classification_change_from_tech_short | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| classification_change_to_defensive_short | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| cpr_narrow_bullish | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| cpr_narrow_momentum | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| cpr_narrow_momentum_short | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| donchian_breakdown_retest_short | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| donchian_breakdown_short | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| evening_star_short | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| institutional_capitulation_short | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| institutional_distribution_short | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| morning_star | `?` | strategy did NOT fire even with best-case synthetic inputs (tried both long and short directions); possible logic bug or |
| ... | ... | +10 more (see JSON) |

## Bug class: `SYNTHESIZE_ALWAYS_FIRES` (1 findings)

| Strategy | Clause / key | Issue |
|---|---|---|
| hull_rsi_short | `?` | strategy fires with all-False signals AND is not dual-direction; no real gating |
