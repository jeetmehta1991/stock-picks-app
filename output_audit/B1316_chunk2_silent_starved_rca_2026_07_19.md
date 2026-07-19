<!-- Source: per CHECKLIST #77 canonical-source; B1316 2026-07-19 owner directive "show list of strategies and root cause analysis of each" (chunk-2 cube analysis follow-up to B1315) -->

# Chunk 2 — Silent / Starved Strategy Root-Cause Analysis (per strategy)

**Batch:** B1316 (2026-07-19, Council 348) · **Data:** `chunk2/artifacts.tar` (379 traded tickers, C-K alphabetical slice, 1002 NYSE days 2022-05-05→2026-05-05, 17,569 closed trades) · **Follow-up to:** B1315 (fanout + anomaly summary).

## Critical caveat (read first)
Chunk 2 is a **C-K alphabetical ticker slice (379 tickers)**, not the full universe. Many "silent/starved" cases are **chunk-local** (sector mix, news coverage, event rarity) and will fire in other chunks. **Only code-level causes are cube-wide** and thus final: Mechanism 1 (SMC_PHASE), Mechanism 2 (portfolio gate), Mechanism 3 (exit anomaly), Mechanism 4 (avoid-gate). The **merged full cube is authoritative** for the rarity-driven cases (Mechanism 5).

Definitions: **raw_fires** = strategy function returned True (intrinsic signal frequency, pre-portfolio). **trades** = positions actually opened (post-portfolio-competition). A large raw→0 gap = the signal is NOT rare; it lost a downstream gate.

---

## 🔴 Mechanism 2 (headline) — cross-strategy one-position-per-ticker gate contaminates per-strategy counts

**Evidence:** `portfolio.py:384` `if ticker in self.positions: return False, "ticker_already_in_portfolio"`. This is the single largest skip reason: **266,212 of 401,240 skips (66%)**. `--no-portfolio-cap` removed the *position-count* cap (no `max_open_positions` skips appear) but left this **cross-strategy ticker-uniqueness** gate active.

**Why it matters:** the cube is meant to give each strategy an **independent** verdict, but a strategy can't open a ticker another strategy already holds. So per-strategy **trade counts (and therefore silent/starved verdicts) depend on which strategy grabbed the ticker first** — order/priority contamination, not intrinsic signal quality. Poster child: `insider_cluster_with_director_long` fires **849 raw signals → 0 trades** (every one of its tickers was already held).

**Contradiction:** CLAUDE.md Approved Rules says *"One trade per ticker — Removed — all strategies fire independently"* and *"Open position cap — Removed."* The one-per-ticker rule is **not actually removed** in the portfolio path.

**Decision needed:** is the R5 cube a **single shared portfolio** (realistic, but cross-strategy contamination) or **per-strategy isolated portfolios** (independent verdict, matches CLAUDE.md intent)? This changes ~all starvation counts. → **Ticket S6-B1316-PORTFOLIO-GATE-CUBE-INDEPENDENCE.**

Other notable skip reasons: `no_next_bar` 79.5K (last-bar entries, benign), `ticker_already_open_same_strategy_bug61` 15.3K (same-strategy re-entry block, defensible), `required_macro_regime_mismatch` 8.2K, `stopout_cooldown_5d` 4.6K, `avoid_tier_blocked` 4.4K, `max_loss_cap_breach` 4.5K.

---

## 🟡 Mechanism 1 — SMC_PHASE B-CANARY (22 strategies, truly silent, cube-wide, BY DESIGN)

**Root cause (shared):** `smc_ict.py:126` `from backtest.config import SMC_PHASE; if SMC_PHASE != "PRODUCTION": return {}`. All SMC producer signals (`smc_liquidity_swept_dn/up`, `smc_fvg_*`, `smc_ob_*`, …) return empty → every strategy consuming them fires 0 raw signals. Deliberate B-CANARY per **B1038 / Council 131 / DEC-508** (SMC deferred pending Phase-C 8-item sign-off). Config flag → **identical local + cloud → NOT a merge inconsistency.**

**Consequence:** the entire R5 cube has **zero SMC/ICT-sweep coverage** until `SMC_PHASE` is promoted. → **Ticket S6-B1316-SMC-PHASE-DECISION.**

| Strategy | raw | RCA |
|---|---|---|
| smc_bos_continuation, smc_bos_retest_entry, smc_breaker_block_long/short, smc_choch_reversal, smc_discount_long, smc_equal_highs_sweep_short, smc_equal_lows_sweep_long, smc_fvg_retest_long/short, smc_inverse_fvg, smc_liquidity_sweep_reversal, smc_mitigation_block_long/short, smc_order_block_bounce, smc_ote_long/short, smc_premium_short **(18)** | 0 | SMC producers gated off by SMC_PHASE≠PRODUCTION |
| turtle_soup_long, turtle_soup_short **(2)** | 0 | consume `smc_liquidity_swept_dn/up` → same SMC_PHASE gate (NOT "daily-bar inapplicable" — corrected from B1315) |
| judas_swing_long, judas_swing_short **(2)** | 0 | consume `smc_liquidity_swept_dn/up` + `near_pivot` → same SMC_PHASE gate |

---

## 🟠 Mechanism 3 — `hybrid_50pct_target` exit anomaly (cube-wide)

Mean `max_drawdown_pct` by exit: **hybrid_50pct_target = −803 pp** (2× next-worst `trailing_15pct` −341). Extreme cells −11,941 pp (`xs_momentum_bottom_decile_short`: 73% WR, avg −32.7%/trade, PF 0.32). Two parts: (a) `max_drawdown_pct` is **additive pnl-point units** (Σ trade %), so it can exceed −100% — the "DD < 20 pp" gate measures additive DD (confirm intended); (b) hybrid_50pct_target likely **does not cap short losses** (unbounded squeeze). → **Ticket S6-B1315-HYBRID-EXIT-LOSS-AUDIT** (opened B1315).

---

## ⚪ Mechanism 4 — by-design non-trade-producer

| Strategy | raw | trades | RCA |
|---|---|---|---|
| short_borrow_trap_avoid | 67,619 | 0 | It is an **avoid-side GATE** (fires `avoid` when days_to_cover>8) consulted by every SHORT via `_short_borrow_trap_active()`; it does **not** generate entries. 0 trades is correct — **exclude from starvation analysis.** |

---

## 🟢 Mechanism 5 — genuinely rare / EXPLORATORY / chunk-local (confirm on merged cube)

| Strategy | raw | RCA |
|---|---|---|
| rsi_overbought_short | 0 | Gates `rsi_14>65 AND below_sma_50` are near-contradictory (overbought while below mid-term MA is rare). EXPLORATORY (B803 short-side anti-edge). |
| rsi21_slow (short branch) | 12 | EXPLORATORY dual-direction; SHORT structural anti-edge per B768. |
| classification_change_to_tech_long | 0 | Rare event: reclassification INTO tech (sector_history.csv). EXPLORATORY Pattern AA. |
| classification_change_* (breakout/oversold/recent/volume/with_insider/with_institutional/from_tech_short) **(7)** | 3–230 | Rare GICS reclassification events + extra confirmation gates; many raw fires (recent 230, from_tech_short 201, with_institutional 190) that then lose the **portfolio gate** (Mechanism 2) → 0 trades. |
| gold_silver_risk_off_long | 0 | Producer exists (`cross_asset.py:273`); needs gold/silver-ratio risk-off state AND defensive-sector ticker — rare macro state × chunk-2 (C-K) sector mix. |
| sector_rotation_defensive_long | 0 | Producer exists (`cross_asset.py:255` `defensive_leadership`); needs defensive-leadership regime AND defensive-quartet sector — rare × chunk-local. |
| news_momentum_short (108 raw), news_reversal_long (5 raw) | 5–108 | News coverage sparse for chunk-2 tickers (B1211: 84% effective universe, C-K names heavily represented in the 15.8% zero-coverage list) + EVENT confirmation gates + portfolio gate. |
| squeeze_setup_long | 2 | 3-layer composite (SI + DTC + institutional + news catalyst); intrinsically very selective / FIRE_STARVED (known). |
| weekly_bias_pullback_short | 2 | Weekly-timeframe bias signal → slow/rare on daily bars; SHORT anti-edge. |
| post_inclusion_drift_long (195), post_deletion_drift_short (399), pre_rebalance_long (187) | 187–399 | Rare index-membership events; substantial raw fires but lose the **portfolio gate** / `no_next_bar` → 0 trades. |
| insider_cluster_with_director_long | 849 | NOT rare — 849 raw fires; **100% lost to the portfolio gate (Mechanism 2)**. |

---

## Starved (fired, but below the 100-trade overall gate at full-universe estimate)
~64 strategies estimated below 100 trades at full scale (chunk2 count ×4). Dominant causes: (1) **portfolio-gate crowding** (Mechanism 2) — the biggest lever; (2) event-rarity (index/reclassification/insider); (3) EXPLORATORY short-side anti-edge; (4) chunk-2 ticker-mix. **Re-assess on the merged full cube** — per-chunk counts understate because each chunk is ¼ of the universe AND portfolio-gated. Direction skew overall: 11,849 long vs 5,720 short (~2:1).

## Fanout & cube health (from B1315, confirmed)
Fanout **clean**: 3,978 cells = 153 strategies × 26 exits, 0 defects, trade-count constant across exits. 0 NaN in win_rate/PF/composite/DD. Strategies with <5 trades excluded from the cube by threshold (23). No crisis regime in window → crisis verdicts INSUFFICIENT_DATA.

## Tickets opened
- **S6-B1316-PORTFOLIO-GATE-CUBE-INDEPENDENCE** (🔴 design): decide shared-portfolio vs per-strategy-isolated cube; resolve the CLAUDE.md "one-trade-per-ticker removed" contradiction.
- **S6-B1316-SMC-PHASE-DECISION** (🟡): promote SMC_PHASE=PRODUCTION (needs Phase-C sign-off) or accept 22-strategy SMC/ICT exclusion from the cube.
- **S6-B1315-HYBRID-EXIT-LOSS-AUDIT** (🟠): audit hybrid_50pct_target loss-capping + confirm additive-pp DD gate intent.
- **S6-B1316-8-SILENT-INVESTIGATE**: the 4 non-SMC truly-silent (rsi_overbought_short, classification_change_to_tech_long, gold_silver_risk_off_long, sector_rotation_defensive_long) — confirm rare-vs-broken on merged cube.
