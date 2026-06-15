# CHECKLIST-106 CLUSTER A PRODUCER-DATA AUDIT -- B767 VERDICT

<!--
# Source: scripts/checklist_106_cluster_a_producer_audit.py (B757 build) + B766 EXECUTION_QUEUE.md ticket #32
# Source: output_audit/checklist_106_cluster_a_producer_audit_smoke.json (B757 smoke output)
# Source: backtest/signals/technical.py compute_all_signals producer (emission probe)
# per CHECKLIST #77 + #44(b) + #106 + #107
# per memory: feedback_data_consumption_audit_must_apply_checklist_44b.md
-->

**Ticket executed:** `S4-B766-COUNCIL-CLUSTER-A-PRODUCER-DATA-AUDIT-PRE-FLIGHT` (TIER 0)
**Source:** B766 council chairman directive ("THE ONE THING TO DO FIRST")
**Batch:** B767 (Stage 4, executed 2026-06-15)
**Pre-flight:** CHECKLIST #44(b) data-consumption + #67 doc-sweep + #94 queue-mandatory + #105 walk-step3 + #106 producer-audit + #107 reconciliation
**Per memory:** `feedback_data_consumption_audit_must_apply_checklist_44b.md`

---

## Question council asked

> "If even 2-3 of the 30 Cluster A strategies are silently default-returning at runtime due to producer / signals_used key mismatch (B748c precedent), the entire effective-N debate is contaminated and every downstream council/reviewer recommendation is built on bad counts. Verify the producer-data audit pre-flight."

---

## Empirical result (smoke 3 tickers x 1yr + producer source spot-check)

### Step 1 -- Raw audit output (B757 smoke, source `output_audit/checklist_106_cluster_a_producer_audit_smoke.json`)

- 30 Cluster A strategies probed
- 93 unique declared signals across signals_used fields
- 49 Pattern F candidates RAW (declared but never emitted OR emitted but always False)

### Step 2 -- Council-filter classification (B757 ticket #25 lesson: signals_used can contain semantic shorthand, not all keys are real producer-key references)

| Class | n_candidates | Description |
|---|---|---|
| CONVENTION MARKERS | 1 | `borrow_ok` (sleeve semantic marker, not producer key) |
| SEMANTIC DESCRIPTIONS | 26 | `rsi_2<5_or_rsi_14<35` (docstring threshold shorthand) |
| **REAL PRODUCER KEYS** | **22** | **Genuine signal-name references to investigate** |

### Step 3 -- Real-producer-key issue breakdown

| Issue type | n | Investigation gate |
|---|---|---|
| declared_but_never_emitted | 8 | Producer source grep -- **CRITICAL pre-flight gate** |
| emitted_but_always_False | 14 | Demo (50 tickers x 2yr) -- deferred to B768 |

### Step 4 -- Producer source emission probe (`compute_all_signals` output)

| Declared key | Producer emission | n_strats | Verdict |
|---|---|---|---|
| `above_ema_200` | MISSING (`price_above_ema_200` emitted instead) | 3 | METADATA-mismatch only |
| `price_below_ema_200` | MISSING (`below_ema_200` emitted instead) | 22 | METADATA-mismatch only |
| `macd_bullish` | MISSING (`macd_12_26_9_bullish` emitted instead) | 7 | METADATA-mismatch only |
| `macd_bearish` | MISSING (`macd_12_26_9_bearish` emitted instead) | 9 | METADATA-mismatch only |
| `vol_spike_1.5x` | MISSING (only 12x/15x/17x/2x/3x emitted) | 10 | METADATA-mismatch only |
| `bb_touch_lower_tight` | MISSING (neither variant emitted) | 1 | METADATA-mismatch only |
| `bearish_signal` | MISSING (generic name not emitted) | 1 | METADATA-mismatch only |
| **TOTAL declarations** | | **53** | |

### Step 5 -- The critical distinction: runtime fires logic vs metadata `signals_used` field

For each of the 53 declarations across the 8 mismatched keys, classified by usage location:

| Key | RUNTIME `s.get(key)` in fires logic (silent-no-op bug) | METADATA-only in `signals_used` field |
|---|---|---|
| `above_ema_200` | **0** | 3 |
| `price_below_ema_200` | **0** | 22 |
| `macd_bullish` | **0** | 7 |
| `macd_bearish` | **0** | 9 |
| `vol_spike_1.5x` | **0** | 10 |
| `bb_touch_lower_tight` | **0** | 1 |
| `bearish_signal` | **0** | 1 |
| **TOTAL** | **0** | **53** |

### Step 6 -- Spot-check validation (3 samples)

Inspected runtime fires logic for representative affected strategies:

- `williams_r_oversold` (declares `above_ema_200` in metadata) -- runtime uses `s.get("price_above_ema_200", False)` -- **CORRECT producer key**
- `supertrend_macd` (declares `macd_bullish` / `macd_bearish` in metadata) -- runtime uses `s.get("macd_12_26_9_bullish")` / `s.get("macd_12_26_9_bearish")` -- **CORRECT producer key**
- `bollinger_tight` (declares `above_ema_200` / `bb_touch_lower_tight` in metadata) -- runtime uses `s.get("price_above_ema_200", False)` / `s.get("below_ema_200", False)` -- **CORRECT producer key**

Confirmed: `signals_used` field is a DOCUMENTATION SHORTHAND list (used by dashboard + STRATEGY_ROSTER.md generation). The runtime fires-logic uses the actual producer keys.

---

## Verdict (council TIER 0 question answered)

| Council TIER 0 concern | Empirical result |
|---|---|
| Are silent-no-op runtime gates contaminating effective-N debate? | **NO -- ZERO runtime silent-no-op gates detected on 8 mismatched keys** |
| Is the cluster's empirical fire-count data trustworthy? | **YES** -- runtime is using correct producer keys |
| Does the B748c precedent apply to Cluster A? | **NO** -- only metadata shorthand mismatches, not runtime contract gaps |

**CONTAMINATION: NOT CONFIRMED.** Cluster A effective-N debate proceeds without producer-contamination concern.

**Caveat:** 14 "emitted but always False" candidates pending demo (50 tickers x 2yr larger sample). Smoke (3 tickers x 1yr) is too small for rare-event signals (shooting_star / hammer / Camarilla R4 breakout). Demo audit launched in B767 background; results parsed in B768.

---

## Follow-up tickets surfaced

| # | Ticket | Type | Reason |
|---|---|---|---|
| 50 | `S4-B767-METADATA-SIGNALS-USED-FIELD-SHORTHAND-NORMALIZATION` | Class 1 DOC-DISCIPLINE / P3 polish | 53 declarations across 8 keys use shorthand that doesn't match real producer key names. Dashboard signal-coverage stats + STRATEGY_ROSTER.md accuracy affected; runtime firing NOT affected. Normalize metadata to use canonical producer keys. |
| (queued for B768) | Demo audit parse | Existing infrastructure | Background bh15ewc9v will resolve the 14 "emitted but always False" candidates on a larger sample |

---

## Downstream council ticket unblocking

This audit completion enables progress on B766 council TIER 1 (#33 phi-correlation latent-collapse) and TIER 2 (#34 post-Q fire-count projection) tickets -- they were gated on TIER 0 producer-data audit verdict.

**#33 (phi-correlation)** unblocked: can proceed against existing demo fire-bar matrix (B760 output) + full when it lands (biu7dcrbi running).

**#34 (fire-count projection)** unblocked: same demo fire-bar matrix data is the input.

---

## CHECKLIST #107 reconciliation (this batch)

- **Findings surfaced:** 1 primary (METADATA-mismatch confirmed at 53 declarations across 8 keys) + 1 deferred-to-B768 (emitted-but-always-False on 14 candidates pending demo)
- **Tickets filed:** 1 NEW (#50 metadata normalization) + 1 ANNOTATION (#32 COMPLETED-EMPIRICAL)
- **Audit-clean:** YES

---

## Pyramid + commit

- Pyramid: existing 842/842 unit + integration green (no code changes; audit is read-only inspection)
- Commit: B767 with this verdict report + EXECUTION_QUEUE.md ticket #32 annotation + ticket #50 filing
