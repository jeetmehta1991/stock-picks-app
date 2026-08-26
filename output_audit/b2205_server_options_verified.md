# VERIFIED server options under $500 CAD (B2205, 2026-08-26)

**Provenance:** every price below was pulled THIS SESSION from deltaserverstore.com's live
WooCommerce Store API at variation level (`/wp-json/wc/store/v1/products/<variation_id>`),
not from a price range or a phone quote. All configs are "All Caddies, No HDD" (no boot
drive included). Currency CAD, minor units converted (e.g. price "49000" = $490.00).

## The sub-$500 space (verified)

| # | Model | CPUs | Cores/Threads | RAM | Price | variation id |
|---|---|---|---|---|---|---|
| A | Dell R720 (2U) | 2 x E5-2697 v2 @2.7GHz | 24 / 48 | 64GB DDR3 | **$490** | 748127 |
| B | Dell R620 (1U) | 2 x E5-2697 v2 @2.7GHz | 24 / 48 | 64GB DDR3 | **$490** | 748002 |
| C | Dell R720 (2U) | 2 x E5-2690 v2 @3.0GHz | 20 / 40 | 64GB DDR3 | **$440** | 747986 |
| D | Dell R720 (2U) | 2 x E5-2680 @2.7GHz | 16 / 32 | 128GB DDR3 | **$440** | 748010 |
| E | Dell R720 (2U) | 2 x E5-2680 @2.7GHz | 16 / 32 | 96GB DDR3 | **$400** | 748040 |

## Just over budget (for reference, same verification method)

| Model | CPUs | Cores | RAM | Price | id |
|---|---|---|---|---|---|
| R720 | 2 x E5-2690 v2 | 20 | 128GB | $540 | 747962 |
| R620 | 2 x E5-2697 v2 | 24 | 96GB | $550 | 748008 |
| R720 | 2 x E5-2697 v2 | 24 | 96GB | $550 | 748133 |
| R720 | 2 x E5-2697 v2 | 24 | 128GB | $590 | 748043 |
| R630 (DDR4) | 2 x E5-2660 v3 | 20 | 64GB | $650 | 770061 |
| R630 (DDR4) | 2 x E5-2650 v4 | 24 | 64GB | $700 | 770236 |
| R630 (DDR4) | 2 x E5-2697 v3 | 28 | 64GB | $700 | 770113 |
| R630 (DDR4) | 2 x E5-2699 v3 | 36 | 64GB | $750 | 770139 |
| R630 (DDR4) | 2 x E5-2696 v4 | 44 | 128GB | $1,300 | 770379 |
| DL380 G9 12LFF | - | - | base | from $500 | 269361 |
| T430 tower | v3/v4 | up to 28 | base | from $700 | 6271 |

**Finding: the DDR4 generation (R630/R730, Haswell/Broadwell v3-v4) does not enter the
budget at all** - its cheapest useful config is $650. Everything under $500 is
Sandy/Ivy Bridge (v1/v2) on DDR3.

## 3-parallel-config feasibility (the owner's requirement)

Measured basis, from this project's own artifacts:
- one config = a 10-worker pool; **12.04 GB peak working-set sum per config** (B2204b,
  live 18-process measurement of a running config)
- 3 configs = ~36GB + ~6GB OS = **~42GB** -> 64GB clears it with 22GB headroom

| Option | 3 configs at pool-8 (24 workers) | RAM headroom at 3 configs | verdict |
|---|---|---|---|
| A (24c/48t) | fits on physical cores exactly | 22GB spare | **YES, cleanest** |
| B (24c/48t) | same as A | 22GB spare | YES (but 1U noise) |
| C (20c/40t) | 4 workers oversubscribed (HT absorbs) | 22GB spare | YES |
| D (16c/32t) | 8 workers oversubscribed | 86GB spare | YES, slower per config |
| E (16c/32t) | 8 workers oversubscribed | 54GB spare | YES, slower per config |

**All five deliver 3 parallel configs.** They differ in per-config speed, not in whether
3 fit. Two caveats, both real:
1. **The shared-ledger race is unfixed**: run_postconfig writes postconfig_ledger.json
   without a lock; two configs landing simultaneously can corrupt it. A file lock is a
   PREREQUISITE of any parallel program, on any hardware. Not yet built.
2. **Per-core speed vs the laptop is UNVERIFIED on this engine** (external benchmark
   tables suggest ~0.45-0.65x for these Xeons; our engine's pandas/BLAS profile is not
   what those tables measure). The decisive test is one config on the box.

## Two probes run this session that change the picture

**(a) The laptop's own RAM ceiling: 64GB max, 2 slots, currently 2x8GB DDR4-3200**
(Win32_PhysicalMemoryArray MaxCapacityEx). So the measured crash class (RAM commit
exhaustion at 2 parallel) is fixable for the price of memory. BUT the laptop CPU is an
**i7-1355U** - a 15W mobile part, 2 performance + 8 efficiency cores. More RAM removes
the crash; it does not add cores, so 3 parallel configs on the laptop would each run
~3x slower for roughly unchanged total throughput. **The server's real product is cores,
not RAM.**

**(b) The 5-hour local cap is real and mechanically enforced**
(prelaunch_gate.py:153 OWNER_LOCAL_CAP_HOURS = 5.0; CLAUDE.md B2107 banner). A slower
per-config wall clock does NOT breach it, because run_wave chunks runs into legs
(leg_cap_hours 4.5, max_legs 3) and resumes - the cost is more resume boundaries, each
dropping open trades (B1076 disclosed artifact), not a refused launch.

## Not included in any price above

- **Boot drive: mandatory.** These ship with caddies and no disk; nothing boots. Store
  sells SSD options as a separate configurable product (ids 119991 / 717444). Budget
  $50-80 for a 500GB SATA SSD.
- Rails ~$100 if rack-mounting (not needed on a shelf/floor).
- Electricity: a dual-130W-TDP box under sustained 3-config load draws materially more
  than idle; the earlier $20-25/month figure was an IDLE-class estimate and is
  UNMEASURED for loaded operation.
