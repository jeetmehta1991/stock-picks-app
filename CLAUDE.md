# Stock Picks & Automated Trading System
**Stage:** 2 — Strategy Validation | **Phase:** 0A → 1A (launch day 2026-05-15; Pass 53 Day 9+ Batch 178)
**Repo:** jeetmehta1991/stock-picks-app
**Docs:** `PROJECT_PLAN.md` (full detail) | `CHECKLIST.md` (pre-action) | `LEARNINGS.md` (lessons) | `VERIFICATION_MATRIX.md` (engine-consumption ground truth, coverage-driven - replaces the `wired=yes` grep heuristic that produced ~150 false-positive RESOLVED-IMPLEMENTED claims; regenerate via `scripts/build_verification_matrix.py` after a canonical backtest under `coverage run`) | **`STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md`** (Pass 53 Day 9+ 2026-05-19 canonical post-Phase-1A-alpha build plan: summary table + 10-day plan + winners-only Phase 1B-alpha architecture)

**Live dashboards (GitHub Pages):** `https://jeetmehta1991.github.io/stock-picks-app/`
- `/dashboard_sprint0a/` — API endpoint coverage (109 CACHED / 28 ACCESSIBLE_NOT_CACHED / 40 TIER_BLOCKED)
- `/dashboard_stage_2/` — Decisions + Bugs + INVs registry (481 visible DECs / 250 visible BUGs; matrix stable 731)
- `/dashboard_phase_1a/` — 12-tab Phase 1A trade analysis (Sprint 6.5 deliverable, delivered early 2026-05-15 Batch 177)

**Latest pyramid (2026-05-15):** 1882 passed / 14 skipped / 5 xfailed / 0 failed.
**Phase 1A launch status:** 0 strict blockers. Day-8 ritual items 1-5 ✅; items 6-7 (tag + owner sign-off) pending owner.

**Phase 1A-β R4 status (B828 owner sync 2026-06-16):** **R4 EXECUTED + STAGE 4 WALKS COMPLETE.** Owner confirmed 2026-06-16: (1) R4 cube ran and is represented by `output_batch395_final/` (May 31 cube data) + dashboard refreshed from R4 full cube per B564-B566 commits + B566 surfaced 351 atomic rows from R4 for Stage 4 per-change approval; (2) All Stage 4 per-strategy cluster walks (221 strategies across 8 cluster docs) are DONE — `feedback_r5_paused_pending_stage4_completion` gate LIFTED. **Phase 1A-β R5 next status:** R5 EXECUTION GATED BY ENTIRE-EXECUTION-QUEUE RESOLUTION + IMPLEMENTATION per owner directive 2026-06-16. Sequential execution: (i) B828 doc-sync DONE; (ii) Stage 4 per-change approval on 351 R4 atomic rows; (iii) Stage 5 implementation batches (≥5 approvals/batch); (iv) TIER 2 producer wireup completion (smart-money/event-driven/cross-sectional); (v) Strategy-side EVENT rollouts + AA EXPLORATORY 18-strategy sweep + S mean-rev SHORT EXPLORATORY tags + BB news_sentiment vendor SPOF sentinel; (vi) #4 BH-FDR vs Bonferroni methodology decision; (vii) 18 substantive pyramid items (B586/B533/B465 + 15 singletons). R5 launches only after all queue items resolved/implemented. Pre-R4 pause-state (2026-05-26) superseded.

---

## Critical Rules

- **MANDATORY PRE-FLIGHT CHECKLIST (Pass 52 owner directive — no exceptions):** Every recommendation in every response must be preceded by a visible pre-flight verification block applying the full CHECKLIST.md (currently 55 items). Format:
  - Pre-flight executes BEFORE the recommendation is stated, not after
  - Each applicable checklist item explicitly noted as ✅ / ⚠ / 🔴 with brief evidence (grep output, audit cross-reference, project scope check)
  - Items NOT applicable to a given recommendation must be explicitly marked N/A — silent skipping is not allowed
  - If ANY item fails (returns 🔴), HALT — do not draft the recommendation; report the failure and ask for direction
  - Critical findings surfaced during pre-flight (existing-code violations, scope conflicts, prior-art duplicates, phase-scope errors) must be reported BEFORE the recommendation, with the recommendation revised to incorporate the finding
  - End-of-response compliance statement (per CHECKLIST #45) is the per-response gate; it does NOT replace per-recommendation pre-flight gates
  - Past failures: 6+ consecutive lapses in DEC-422 framework drafting (Pass 52 turns 1-6) where end-of-response self-check missed errors that pre-flight would have caught (sector concentration entry-vs-exit, phase scope, dynamic-vs-static framing, dimensional coverage gaps, hardcoded strategy count, hold-duration-as-input, schema missing R:R/ROI/profit factor, existing-code DEC-353 violation in fixed_3r_2r). Owner caught all 6 with common-sense questions. The pre-flight gate is the systematic fix.
  - Applies to: new recommendations, revisions to prior recommendations, scope expansions, batch reviews, framework proposals, sub-decision logging, schema/field additions
  - Does NOT apply to: pure logging actions (committing already-approved decisions to audit), git operations, simple acknowledgments, owner-direction responses where Claude is asking clarification rather than recommending

- **ALL decisions need explicit owner approval before implementation. No exceptions.**
- **All API runs costing money: small test batch → manual review → owner approval → scale. NEVER jump from "data ready" to "full run". Past mistakes (L86, L95) cost $150 in discarded work — same pattern, different operation, same outcome unless this discipline is mandatory. See CHECKLIST #13, #22, #23, #29.**
- Never change rules, filters, thresholds, or parameters without approval. Recommend only.
- Think through every action completely before suggesting it. Anticipate edge cases.
- Never jump ahead of the current phase. One instruction at a time.
- If something can go wrong, flag it proactively.
- Point-in-time data enforcement is non-negotiable.
- **Never use `git reset --hard` without running `git status` first. This has destroyed data twice (L49, L77).**
- **Run CHECKLIST.md before every suggestion or execution.**
- **MANDATORY (Pass 52): every response must end with a visible CHECKLIST compliance statement enumerating which items applied and were satisfied. No exceptions. If checklist was not consulted before responding, the response itself is non-compliant. Owner has authorized ending conversation if this rule is repeatedly violated.**
- **MANDATORY (Pass 53 owner directive 2026-05-05): every turn that produces meaningful changes ends with a per-turn document sync sweep — see CHECKLIST #67. All forward-looking documents outside `archive/` folder must be updated AND COMMITTED in that same turn. No deferred-doc-sweep debt. **Doc commits are DECOUPLED from pending long-running operations** (CHECKLIST #67.b owner clarification 2026-05-05): if a multi-hour SCREENER / prefetch / API job is in flight, doc updates STILL commit at end of turn; the pending run's output commits separately when complete. If end-of-turn shows stale references in any non-archive doc OR uncommitted forward-looking work, the response is non-compliant. Excludes: `archive/**`, `AUDIT.md` historical narrative entries (per L143), Pass-specific snapshot docs.**
- For every proposed change, always provide a recommendation with clear reasoning and tradeoffs before waiting for approval.
- After every audit, validate by RUNNING CODE — not reading it.
- Run `backtest/tests/test_integration.py` and `backtest/tests/test_unit.py` before every phase run and after every significant code change (all tests must pass; current count grows over time — run `pytest -q` to verify; baseline ~102 tests as of Pass 53). See [CANONICAL_FACTS.md F-007](CANONICAL_FACTS.md).
<!-- canonical-fact-scope: F-002 mention of layered roster as project-unique IP -->
- **Fork-first architecture** — for every new component, identify battle-tested libraries before proposing custom code. Default to forking unless integration cost > rebuild cost OR requirement is genuinely novel to this project. Custom code reserved for what's UNIQUE to our system (signal computation, agent prompts, risk context, earnings_tolerant logic, PIT semantics, validation methodology, the layered strategy roster — Layer 1 baseline 60 + Layer 2 Phase 0.D ICT/Earnings/Calendar + Layer 2D form-derived ICT + Layer 3 Pass 52 RESOLVED chart-pattern/categories + Layer 4 PENDING. **Live count as of 2026-06-12: `len(ALL_STRATEGIES) = 221` total registered (Batch 467 P10 +2 news; Batch 487 SM1 +10 smart-money sleeves; Batch 507 M6 Path-2 +2 YoY-growth PEAD sleeves; Batch 519 P15 +2 squeeze_setup_long + short_borrow_trap_avoid; Batch 531 P17 +2 activist_13d_long + m_and_a_target_long; Batch 572 candle inverse +1 doji_at_resistance_short per Stage 4 cluster walk; Batch 580 Layer 2D ICT first inline-spec +2 turtle_soup_long + turtle_soup_short per Raschke Street Smarts 1996; Batch 581 Layer 2D ICT second batch +6 judas_swing_long/_short + mmbm_long + mmsm_short + week_opening_gap_fill_down/_up per ICT methodology owner inline-spec; Batch 591 +2 donchian_breakout_long + donchian_breakout_retest_long per Stage 4 donchian walk - tight-long mirrors of donchian_breakdown_short/retest_short for symmetry; Batch 599 -1 deleted dual donchian_20_breakout_retest per owner B596 convergence option 2 - explicit pair donchian_breakout_retest_long + donchian_breakdown_retest_short carries the semantics; Batch 603 +2 Class 7 NEW news_momentum_short + news_reversal_long symmetric inverse mirrors per news_momentum_long walk; Batch 605 +1 Class 7 NEW 52wl_break_retest_short per F1 bug fix in 52wh_break_retest walk - new compute_52w_break_retest_signals producer replaced DC20-anchored bug; Batch 607 +1 Class 7 NEW flag_bear_retest_short per F1 bug fix in flag_bull_retest_long walk - new compute_flag_break_retest_signals producer anchors on flag_bull_breakout_level / flag_bear_breakdown_level; Batch 610 +1 Class 7 NEW institutional_breakdown_confirmation_short per institutional_breakout_confirmation_long walk - missing-inverse symmetric mirror using institutional_negative signal; Batch 611 -1 reverted B610's Class 7 NEW per external-AI critique - 13F is long-only data per SEC rule; mechanical symmetry was economically false; Batch 613 -1 strat_52w_low_breakdown_with_smart_money_short F3b deleted + 1 B-twin strat_52w_high_breakout_with_smart_money_vol_below_long added = net 0; Batch 615 +1 B-twin strat_squeeze_setup_event_only_long EVENT-only L1c for A/B vs broader OR composite per squeeze_setup_long re-walk = 222; Batch 620 -1 deleted strat_squeeze_setup_event_only_long per B619 fire-count estimator FAIL_FIRE_STARVED finding ~2.5 fires/yr universe-wide upper bound, below min_trades=30/regime by an order of magnitude - A/B EVENT-only L1c question is answerable post-cube from squeeze_setup_long's trade log filtered by insider_cluster_active=True at fire bar = 221; Batch 636 +1 Class 7 NEW strat_three_black_crows_short per Stage 4 walk of strat_three_white_soldiers - Nison 1991 canonical bearish-reversal mirror = 222; Batch 639 -1 deleted strat_evening_star_short per Stage 4 walk of strat_morning_star (owner option a) - standalone became strict subset of strat_morning_star SHORT after option-2 reconcile-to-reversal removed ema_50_200 trend gates from both directions; same walk also deleted morning_star regime affinity entry (F3 B271 family-bug fix) + queued S5-RSI-DEFAULT-50-FAMILY ticket (F5) + codified CHECKLIST (q) candle-pattern next-bar-open PIT rule (F6) = 221; Batch 641 net 0 strategy count change but RENAMED strat_camarilla_r3_breakout -> strat_camarilla_r4_breakout per Camarilla source-system re-anchor (R3=fade per Slim Khan/Nick Scott; R4=breakout level) -- W10 of B640 walk bundle; same B641 also shipped W3 pin_bar direction-contamination fix via producer-additive bullish_pin_bar/bearish_pin_bar + W4 F3 regime-entry deletion (B271 family-bug pattern) + W8 F1/F1b silent-gap NOT-pattern -> positive symmetric (below_avwap_50low/below_ema_200) + CHECKLIST (r) timeframe-mismatch + (s) EVENT-STATE-wired-finding + Step 1.5 avoid-branch dead-code check restore + 13 new EXECUTION_QUEUE tickets from external-AI audit capture (fire-count measurement pass S5-FIRE-COUNT-MEASURED-RUN built same batch + multiple-testing/marginal-contribution/corporate-action/survivorship/regime-classifier 8-finding queue); Batch 642 net 0 strategy count change but engine-level regime classifier cleanup (removed dead canonical bear line per B640 audit finding #2; added EMA-cross hysteresis band 2pct per audit finding #3); Batch 643 net 0 strategy count change but REDESIGNED strat_pivot_s3_capitulation per owner directive option C from B640 W5 -- new producer compute_capitulation_lookback emits recent_capitulation_at_s3 over 5-bar window; strategy now requires recent_capitulation AND reversal-trigger today (bullish_engulfing OR hammer OR above_prev_high) - buys the TURN not the FALL per Wyckoff Spring/Test sequence; Class 7 NEW pivot_r3_blowoff_short mirror DEFERRED pending W5 measured-fire-count validation; B643 measurement post-redesign 18.3/yr universe-wide FAIL_FIRE_STARVED + owner directive W5-i 2026-06-09 "Keep as exploratory" -> W5 docstring marked EXPLORATORY status pending Stage 5 cube empirical validation (no further pre-cube loosening; rare-but-strong signals can be valid even below n=30 power floor); Batch 645 +1 Class 7 NEW strat_pivot_r3_blowoff_short wired as symmetric mirror of B643-redesigned W5 per owner directive (a) from B643+B644 follow-on - new compute_blowoff_lookback producer + 2-gate structure (recent_blowoff_at_r3 + bearish-reversal trigger today: bearish_engulfing OR shooting_star OR below_prev_low) - sells the TURN not the SPIKE per Wyckoff Buying Climax + Upthrust-Test sequence; EXPECTANCY ASYMMETRY explicitly acknowledged per feedback_structural_symmetry_not_economic_symmetry (equity upward drift + squeeze risk + borrow costs bias against SHORT); BOTH W5 LONG + W5 mirror SHORT marked EXPLORATORY pending Stage 5 cube validation; Batch 648 fix measure_fire_count.py hardcoded-220 universe bug (now uses actual T1a PIT-active count ~503 per owner directive 2026-06-09 post-external-AI critique #1) + added --ticker-sample-strategy {first,random,stratified,all} option; Batch 650 W5 added vol_below_avg AND-required on reversal trigger (Bulkowski/Wyckoff Spring LOW-volume Test bar per external-AI critique #3a -- closes dead-cat-bounce hole); Batch 651 W5 STRATEGY_REGIME_AFFINITY expanded {neutral,bear,crisis} -> all regimes (post-B643-redesign the strategy buys turn up to 5 days later when regime may have transitioned per external-AI critique #3b); Batch 652 W5m stronger EXPLORATORY marker -- explicit DO NOT DEPLOY gate until M10 cost-aware cube + S5-MULTIPLE-TESTING-CORRECTION ship (per external-AI critique #5 -- cube cannot yet evaluate squeeze tail / borrow / selection bias); Batch 654 W8 redundancy-audit option B-local per critique #2 corrected methodology (W8 fires every 4 days/ticker at 34k/yr; cpr_narrow at 0.15 fires 87% of bars = NEAR-NO-OP filter defeating "narrow CPR predicts directional day" thesis) -- NEW producer cpr_narrow_tight (0.05 threshold; B574-style local variant only consumed by W8) + dropped no-op rsi_14>50/<50 gates (jointly resolves S4-W8-RSI-NOOP-GATE + S4-W8-REDUNDANCY-AUDIT); other two cpr_narrow consumers (strat_cpr_narrow_momentum + strat_cpr_narrow_momentum_short) retain 0.15 pending their own walks per feedback_narrow_scope_blast_radius; Batch 655 T10 supertrend_macd redundancy-audit option B per critique #2 (T10 fires every 2.5 days/ticker at 33k/yr; supertrend_bullish at 99.19% True = EXTREME NO-OP on 2022-2024 sample) -- NEW producer-additive supertrend_flip_recent_long_5d / _short_5d (B643/B645-style 5-bar lookback in compute_supertrend; B574-style narrow-scope; other supertrend consumers unchanged) + strategy switched from STATE supertrend_bullish to EVENT-anchored lookback gate; resolves T10 portion of S4-TREND-REDUNDANCY-AUDIT; Batch 656 T3 hull_rsi redundancy-audit option A+C -- different finding from W8/T10: NO extreme NO-OP gate (all 5 gates 38-53% True), honest CONFLUENCE not redundancy (hull_bullish x price_above_hull correlate +0.41 measuring same Hull semantics from distinct angles); option A status-quo on confluence + option C drop rsi_9>50/<50 accidentally-safe no-op (same precedent as B654 W8 RSI); 5 -> 4 distinct gates per direction; SHORT-side (not above_200) NOT-pattern surfaced + queued as S4-T3-NOT-ABOVE-200-EMA-PATTERN; Batch 657 T8 ichimoku_cloud_breakout redundancy-audit option E (A+D) -- same finding as T3 (honest confluence, no extreme NO-OP; 4 marginals 38-51% True) BUT had separate default-True silent-gap on weekly Kumo gates same class as W6/W7/W8 LONG defaults; option A status-quo on 4-gate confluence + option D swap weekly_above/below_cloud defaults True->False (resolves T8 portion of S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY); all 3 originally-flagged trend strategies (T3+T8+T10) now redundancy-audited per their actual pattern; Batch 659 owner-directed AUTONOMOUS implementation of 5 remaining queue items: W6 + W7 + W8 LONG AVWAP defaults True->False symmetric with SHORT side (resolves S4-W6-W7-W8-LONG-DEFAULT-TRUE-UNIFY); T3 SHORT side `(not above_200)` -> positive symmetric `s.get("below_ema_200", False)` (resolves S4-T3-NOT-ABOVE-200-EMA-PATTERN); W5m `vol_below_avg` AND-required on SHORT reversal-trigger (mirror of B650 W5 Spring volume condition; resolves S4-W5M-SYMMETRIC-VOL-GATE); Batch 660 launched S5-FIRE-COUNT-MEASURED-RUN-FULL background job (full T1a x full date range 2020-2026 x all 222 strategies; overnight runtime expected); Batch 682 (2026-06-10 owner-approved deletions per B680 self-critique): -4 strategies = BR-15 strat_volume_spike_breakout_retest DELETED per B620 precedent + B621 0.01/yr WORST FAIL_FIRE_STARVED estimator + EV-3 strat_pead_long_high_yoy_growth_only DELETED per Pattern W deterministic-subset of EV-1 + EV-4 strat_pead_short_negative_yoy_growth DELETED per Pattern W symmetric + EV-7 strat_buyback_8k_recent_long DELETED per CC-B 8-K population-mixing (M&A Item 1.01 SM-4 feasibility-failure carry); plus BR-8 strat_dc20_break_retest swap vol_spike_15x->vol_below_avg (Bulkowski 2005 retest absorption thesis alignment; no count change); 222 -> 218; Batch 685 (2026-06-10 owner-approved Class 7 NEW additions per B683 self-critique missing-inverse audit): +3 strategies = strat_head_and_shoulders_top_short (Edwards-Magee 1948 + Bulkowski 2005 mirror of CP-3) + strat_triangle_descending_short (Bulkowski 2005 mirror of CP-7) + strat_hammer_at_support_long (Nison 1991 mirror of CC-4); plus 2 producer-side fixes (compute_triangle_apex_break_retest_signals + compute_cup_handle_neckline_break_retest_signals B607-pattern new producers re-wiring CP-8+CP-9) + Pattern A WAVE 2 sweep (price_above_ema_50 default-True -> False across 8 strategies symmetric with B663 WAVE 1) + CP-1 cup_and_handle_long EXPLORATORY marker per B660 0-fire confirmation; 218 -> 221; Batch 686 (2026-06-10 owner-approved Class 7 NEW; deferred from B685 pending inverted-cup producer methodology + executed per owner directive 'execute now'): +1 strategy = strat_inverted_cup_and_handle_short (Bulkowski 2005 'rounded top with handle' / 'dump and pop' bearish mirror of CP-1 cup-and-handle long); plus NEW detect_inverted_cup_and_handle producer in chart_patterns.py (symmetric bearish-mirror methodology: left_rim_low + right_rim_low + cup_high + handle_bounce vs detect_cup_and_handle's left_rim + right_rim + cup_low + handle_pullback); 221 -> 222 = 222; Batch 709 (2026-06-12 EMPIRICAL-RESTORE per B702 adversarial review verdict): +2 strategies = strat_pead_long_high_yoy_growth_only + strat_pead_short_negative_yoy_growth RESTORED -- B709 empirical verify measured phi correlation = 0.297 on 29 T1a tickers 2020-2026 (well below the 0.70 revert threshold); 70% of EV-3 fires (1,466 of 2,093) are a distinct "fundamental momentum" population EV-1 misses entirely; B682's "deterministic strict subset" rationale was empirically wrong; 222 -> 224 = 224; Batch 722 (2026-06-12 owner-approved per "approve all recs"): -3 strategies = strat_hull_rsi_short DELETED per B718 Pattern W deterministic-duplicate finding (post-B718 tightening it fires on IDENTICAL gates to strat_hull_rsi SHORT branch) + strat_po3_htf_aligned_long DELETED per B720 HYBRID Pattern F rec (strict subset of strat_po3_bullish on weekly_bias_bull axis) + strat_po3_htf_aligned_short DELETED per same rec; same B722 also applied STATE->EVENT conversion to strat_hull_rsi (LONG: price_above_ema_200 -> price_above_ema_200_break_recent_5d; SHORT: below_ema_200 -> below_ema_200_break_recent_5d) per B655 T10 + B721 below_ema_50_short precedents; same B722 also marked strat_po3_bullish + strat_po3_bearish EXPLORATORY per B652 W5m precedent (cube measurement only, no production deployment regardless of verdict); 224 -> 221 = 221) / `len(DEPRECATED_STRATEGIES) = 0` (Batch 316a empty) / `len(STRATEGIES_DISABLED_MISSING_PRODUCER) = 1` (Batch 372 `dxy_headwind_multinational_short` — foreign_rev_pct producer absent) / 220 active for next cube iteration**. The 108-133 figure in CANONICAL_FACTS.md F-002 is pre-Batch-316a stale.). Per L103: read library source before recommending. Per DEC-045 (RESOLVED Pass 27): use this approach across all phases. Already-adopted forks: smartmoneyconcepts (ICT), TradingAgents (multi-agent), QuantStats (analytics), Streamlit (dashboard), ib_async (broker), freezegun (tests), OpenBB+Polygon (fundamentals).

- **MANDATORY (Pass 53 DEC-503 owner directive 2026-05-05): comprehensive test pyramid before every code push.** Every code push (new feature / bug fix / refactor / schema change / data-source migration) must execute and pass ALL applicable test types: Unit + Smoke + Integration + System + Functional + Regression (full `backtest/tests/test_unit.py` + `test_integration.py` — all tests must pass; current count ~102 and growing per [CANONICAL_FACTS.md F-007](CANONICAL_FACTS.md)) + Data integrity + Performance (where applicable) + Acceptance (owner-defined). Partial coverage is non-compliant. If a test type doesn't apply, pre-flight must explicitly mark N/A with reason — silent skipping is non-compliant. See CHECKLIST #69. Past failure: silent-gap finding (BUG-271/272/273) where 3 of 4 Quiver endpoints in `smart_money.py` had been silently broken, undetected because tests focused on the one working endpoint. First application: smart_money silent-gap fix.

- **MANDATORY (Pass 53 DEC-507 owner directive 2026-05-05): Agent toolkit wiring matrix HARD RULE.** Pre-Phase-1B (or any agent-using phase entry), maintain explicit `Agent × Data source × Code path × Verified status` matrix in `TRADINGAGENTS_DATA_AUDIT.md`. Each row must be ✅ end-to-end traced + tested before phase begins. See CHECKLIST #70. Past failure: 1.05M Polygon news articles cached (Pass 53 Batch 3) but `smart_money.get_news_sentiment` reads legacy `cache/av_news/` paths — data DEC (DEC-440) and toolkit DEC (DEC-464) were approved independently without integration deliverable. L146 codifies the lesson; this rule prevents recurrence. Pattern: data DEC + toolkit DEC ≠ integration; wiring is a third explicit deliverable.

- **MANDATORY (Pass 53 DEC-508 owner directive 2026-05-05): External library fork integration mandate — 15-category test plan + 3-phase A/B/C gate.** Any external library forked under DEC-045 must complete Tier 1 correctness (unit + canonical + PIT regression + edge cases + version pin) + Tier 2 integration (cache pipeline + composition + survivorship + performance) + Tier 3 empirical (statistical sanity + adversarial random-walk + cross-validation + lookahead detection) + Tier 4 visual+manual (Dashboard 2 + owner spot-check) — before strategies consume signals. 3-phase gate: Phase A (PRE-MERGE; library in `vendored/` not main; tests pass + ≥90% coverage); Phase B (CANARY; signals computed but strategies disabled; Dashboard validates 20-50 signals + statistical sanity + PIT regression); Phase C (PRODUCTION; strategies enabled + A/B vs baseline + DEC-084 red-flag check + walk-forward DEC-505). Each phase has explicit owner-approval gate. See CHECKLIST #71 + L147. First application: smartmoneyconcepts library Phase A starts Pass 53 Sprint 0A.

- **Sprint 0A (Pass 53 DEC-497 active sprint):** "Sprint 1" was renamed → Sprint 0A with materially expanded scope: multi-API prefetch (Polygon Stocks Starter, Quiver Trader, FRED, ALFRED, AAII, CNN F&G + 7 sub-components, CFTC COT, SEC EDGAR, Apewisdom, pytrends) + 5-tier universe build (DONE 2026-05-05 — T1a 614 + T1c 161 + T1 ETFs 27 + T2 347 + T3 1923 + Master 1,937) + 18-classifier sector taxonomy (DEC-499) + Stage 2 NO-LIVE-API HARD CUT refactor + Polygon ticker events integration (DEC-500) + DEC-504 T3-over-T1 multi-tier precedence resolver (RESOLVED-IMPLEMENTED 2026-05-05). Sprint 0A.0-0A.10 sub-phases per DETAILED_PROJECT_PLAN.md §3.16. Owner-gated per CHECKLIST #68 smoke→demo→full protocol + #69 test pyramid.

- **MANDATORY (Pass 53 DEC-504 owner directive 2026-05-05): T3-over-T1 multi-tier precedence rule.** When a ticker is PIT-active in multiple tiers, the most-specific tier wins for runtime rules application: T3 > T2 > T1c > T1a > T1ETF. Resolver: `backtest.data.universe.resolve_tier_precedence(ticker, as_of)` returns most-specific tier name; `get_tier_params(ticker, as_of)` returns tier-specific dict (liquidity floor, history minimum, position sizing, refresh cadence). Scope (a)-(e) all apply: liquidity, history, sizing, strategy roster, refresh cadence. Canonical example: VST joined S&P 500 2024-05-08 + T3 added 2024-05-01; for as_of=2024-06-01 both active → resolves T3. Master Dedup CSV has new `resolved_tier` column per DEC-504. 10 new unit tests in `backtest/tests/test_unit.py` (test_dec504_*).

---

## Repo Structure

```
Backtesting universe/    # Top-level folder for ALL universe CSVs (Pass 53 owner directive — single visible folder). ALL files use standardized B++ schema: `Symbol, Company, Sector, added_date, removed_date` + tier-specific extension columns (Pass 53 schema standardization).
  Current Snapshot_SP500 Tickers_May 2026.csv          # T1a current snapshot — Wiki Table 0 ground truth (503 rows, B++ schema; Pass 53 sync replaced 481 stale slickcharts)
  Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv  # T1a B++ canonical PIT file (DEC-477) RESOLVED-IMPLEMENTED Pass 53 — 614 rows (503 active + 111 historical removed-during-window); 124 events 2020-01-01 → 2026-04-09 from Wikipedia Table 1 under L88 exception (4/4 high-impact spot-check verified vs S&P DJI press releases); CDAY→DAY rename map applied; renamed Pass 53 from `historical_membership.csv` per owner directive 2026-05-05; FILENAME DATE-RANGE: rename to extend range on next monthly refresh.
  Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv             # Tier 1 ETFs (27) — DEC-118 / DEC-494; B++ schema + Category extension column (Pass 53 standardized; ETFs are reference instruments — added/removed_date NULL = always-active)
  Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv  # T1c — 161 rows B++ schema (DEC-303); 101 currently active = Nasdaq official 101 (Pass 53 CAVEAT RESOLVED 2026-05-05 — 3-way cross-check Slickcharts + Wikipedia + Nasdaq IR all match exactly); 60 historical removed-during-window; GICS sectors; multi-period rows (CSGP/TTWO/WDC/SPLK)
  Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv      # T2 — DEC-103; populate Sprint 1 post-Polygon-prefetch via DEC-380 corp actions screener (per Pass 53 SCREENER-FIRST correction)
  Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv     # T3 — DEC-104/364; populate Sprint 1 post-Polygon-prefetch via DEC-496 J-T 12-1 broad-market screener (per Pass 53 SCREENER-FIRST correction)
  # FUTURE:
  # russell_1000_membership.csv    # T1b — DEFERRED TO STAGE 3 (Pass 53 owner-decided 2026-05-05 — LSEG free tier inadequate; T1a 503 + T1c 101 + ETFs 27 = ~632 instruments already 9× Phase 1A v3 archive baseline; T1b expansion premature for Stage 2 backtest validity. Revisit at Stage 3 papertrading.)
  # archived_watchlist.csv         # DEC-495 RESOLVED-DECIDED Stage 3+ — tickers rotating out of all 5 buckets
  # index_rebalance_events.parquet # DEC-370 — Sprint 5 day-grain effective dates for index rebalance strategies
backtest/
  config.py              # universe, regimes, thresholds, position sizing
  run_phase1a.py         # entry point — --phase, --tickers, --no-news, --no-git flags
  data/
    cache.py             # Parquet cache + filelock for parallel writes
    universe.py          # 5-bucket universe loader (T1a/T1b/T1c/T2/T3 + ETFs); reads from "Backtesting universe/" via UNIVERSE_DIR
    fetcher.py           # yfinance OHLCV + fundamentals (Wikipedia REMOVED — L88)
    macro.py             # FRED yield curve, VIX (from OHLCV cache), DXY (UUP proxy)
    sentiment.py         # AAII, CNN Fear & Greed
    smart_money.py       # congressional, insider, 13F
  signals/
    technical.py         # ~220 technical signal fields (Category 1); see CANONICAL_FACTS.md F-003 for ~270-280 total signals across 6 categories
    screener.py          # 198 strategy classes registered live `len(ALL_STRATEGIES)` 2026-05-30 (was 186 through Batch 372; Batch 467 P10 +2 news; Batch 487 SM1 +10 smart-money sleeves). 0 in DEPRECATED_STRATEGIES (Batch 316a empty). 1 in STRATEGIES_DISABLED_MISSING_PRODUCER (Batch 372 `dxy_headwind_multinational_short` — foreign_rev_pct producer absent). 197 active for Phase 1A-β cube; Batch 487 SM2 added 26th exit method `smart_money_reversal`; cube cells 197 × 26 = 5,122.
  engine/
    backtest.py          # main loop, incremental checkpoints every 100 days
    exit_manager.py      # trailing stop + 5 circuit breakers
    exit_strategies.py   # 25 exit methods (live `len(EXIT_STRATEGIES)` 2026-05-25; was 12 pre-Batches 282-285; cube replay tests every method per entry per Phase 1A-β scope)
    regime_filter.py     # classify_regime: bull/neutral/bear/crisis
    improvements.py      # walk-forward, transaction costs, slippage, survivorship
  agents/pipeline.py     # 11-active-agent pipeline per DEC-057 (3 analysts + Bull/Bear/RM + Trader + 3 Risk Debaters + Portfolio Manager + Reflection post-decision); Haiku Phase 1B (~$116 CAD), Sonnet Phase 1C+. Note: prior CLAUDE.md docstring of "6 agents" was a simplification of the conceptual roles before TradingAgents Pattern 2 integration; actual node count is 11+ per L94/Pass 26 lesson.
  util/
    structured_logger.py # Batch 374 DEC-230: JSON-lines logger helper (opt-in; emits to logs/structured_<DATE>.jsonl with DEC-230 canonical context fields ticker/strategy/regime/...).
  results/
    metrics.py           # 9 passing criteria + per-regime verdict matrix
    writer.py            # trade_log, backtest_results, strategy_regime_matrix.json
    site_generator.py    # daily site_picks JSON
scripts/
  generate_batch_splits.py     # prints 5-batch commands + 1-ticker test commands
  merge_batch_outputs.py       # merge 5 outputs, re-compute metrics, validate
  build_ticker_lifecycle_events.py  # Batch 374 DEC-234+380: Polygon corp-actions -> ticker_lifecycle_events.parquet
  build_t1a_correlation_matrix.py   # Batch 374 B-3: T1a pair-wise OHLCV log-return correlation precompute
  build_t5b_pairs_precompute.py     # Batch 326: cointegrated-pairs precompute (5 annual snapshots in cache)
  profile_process_day_lever_c.py    # Batch 371: cProfile harness for Speedup Lever C investigation
  run_live_end_of_day.py            # Batch 373 C-1: Stage 4 LIVE EOD reconciliation (IB fills + slippage)
  prepopulate_cache_index.py   # pre-fill index.json before parallel runs
  refresh_sp500_universe.py    # quarterly S&P 500 refresh (laptop only, slickcharts.com)
  refresh_extended_universe.py # monthly Tier 2 refresh (laptop only)
  build_momentum_watchlist.py  # monthly Tier 3 refresh (laptop only)
  validate_phase1b_data.py     # pre-run data completeness check
PROJECT_PLAN.md   # comprehensive reference — read first
CHECKLIST.md      # pre-action checklist — 21 items including universe refresh
LEARNINGS.md      # 89 lessons — L88: no Wikipedia, L89: universe staleness
```

---

## Passing Criteria (11 tiered overall/per-regime + per-regime verdict)

All overall thresholds must pass for a strategy to advance overall. Additionally, each strategy gets a per-regime verdict (PASS/FAIL/INSUFFICIENT_DATA) for each of the 7 historical regimes evaluated against the per-regime thresholds. A strategy valid in crisis but not bull is deployed only during crisis — this is intentional. Per-regime thresholds are lower than overall thresholds because per-regime trade samples are smaller (statistical-power tradeoff codified in Pass 53 owner decisions 2026-05-12 via BUG-31/32/33).

| # | Criterion | Per-regime threshold | Overall threshold | Source |
|---|---|---|---|---|
| 1 | Win rate | ≥55% (high-vol: ≥50%) | same | original |
| 2 | Profit factor | >1.3 (high-vol: >1.2) | >1.5 (literature canonical) | BUG-32 Batch 111 |
| 3 | Expected value | >0 | same | original |
| 4 | Win/loss ratio | >1.0 | same | original |
| 5 | Max drawdown | <20 pct-points (high-vol: <25) | same | original |
| 6 | Total ROI | >0% | same | original |
| 7 | Smart money lift | ≥3pp win rate improvement | same | original |
| 8 | Macro correlation | ≥5pp win rate diff | same | original |
| 9 | Min trades | ≥30 | ≥100 | BUG-31 Batch 112 (codified existing) |
| 10 | Sharpe ratio | ≥0.7 | ≥1.0 | BUG-33 Batch 110 |
| 11 | Per-regime verdict | PASS in ≥1 regime (not universal pass required) | -- | original |

Config: `PASSING_CRITERIA` dict in `backtest/config.py` carries all keys (`min_*`, `min_*_overall`, `min_*_per_regime`). Caller-side verdict functions read these to gate overall vs per-regime PASS evaluation.

---

## Key Design Decisions

- **Risk profile:** medium-high risk, high return. Buy dips including in crisis.
- **Regime classification (real-time):** bull/neutral/bear/crisis via 20-day realised vol + SPY vs 200 EMA
- **Per-regime strategy library:** different strategies for different regimes — not universal strategies
- **Position sizing:** EXCEPTIONAL 5%, VERY HIGH 4%, HIGH 3%, MEDIUM-HIGH 1.5%, MEDIUM 0.75%, LOW skip
- **Exit:** atr_trail_1x (1× ATR trailing stop, checked against intraday low) — won 20/29 in Phase 1A v3 archive
- **Phase 1A restored Pass 53:** rules + smart money baseline (no agents) precedes Phase 1B agent overlay. Phase 1A → 1A-α (rules-only cube) → 1A-β (full-scale dry-run) → 1B (agents added) → 1B-α (combined cube). Owner gate at 1A-α (rules-only Sharpe ≥ 0.7 OOS) before $300 1B-α budget commits. See PROJECT_PLAN §3.6-3.10 + DETAILED_PROJECT_PLAN Parts 7.5/7.6/7.7.
- **Email** (not Telegram) for all trade approvals in Stage 4
- **Intraday trading:** completely separate future project — out of scope
- **Agent pipeline:** 11 active agents per DEC-057 + DETAILED_PROJECT_PLAN.md §2.6 (3 analysts: Market / Fundamentals / News; 3 research: Bull / Bear / Research Manager; Trader; 3 Risk Debaters: Aggressive / Conservative / Neutral; Portfolio Manager; +1 Reflection post-decision). Pass 53 correction: prior "6 agents" reference (Technical / Fundamental / Sentiment / Risk / Bull-Bear Debate / Decision) was conceptual simplification — actual count is 11 active LLM nodes per propagate() (L94 / Pass 26 lesson). Temperature=0. Haiku for Phase 1B (~$116 CAD). Sonnet for Phase 1C+.
- **News sentiment:** not_available at free tier. Proceed Phase 1B without news. Add Unusual Whales in Phase 1C instead.

---

## Approved Rules

| Rule | Value |
|---|---|
| Open position cap | Removed from backtest |
| Daily loss limit | Removed from backtest |
| Correlation filter | Removed from backtest |
| Regime hard blocks | Removed — crisis flagged but longs allowed (buy-the-dip) |
| One trade per ticker | Removed — all strategies fire independently |
| Crisis regime longs | Allowed at 50% size — flagged as `regime=crisis_CRISIS_FLAG` |
| Max candidates/day | 30 (Batch 314 Cat-5 A 2026-05-24; was 10) |
| Position sizing | Tiered: 5/4/3/1.5/0.75% by confidence tier |
| Agent tier upgrade | score ≥75 upgrades one tier |
| Agent tier downgrade | score ≤40 downgrades one tier |

---

## HARD RULES — Never Violate

### Git Safety
- **NEVER run `git reset --hard` without `git status` first.** Has destroyed data twice (L49, L77).
- **NEVER run any git destructive command during or after parallel batch runs without checking status.**
- All code goes to `claude-updates` branch, merged to main via push.

### Push & PAT Pattern (Pass 52 owner-approved Option 3)
- Repo URL: `https://github.com/jeetmehta1991/stock-picks-app.git`
- **Authentication:** Personal Access Token (PAT) cached in sandbox session.
- **Lifecycle (Option 3 per Pass 52 owner directive):**
  1. Owner issues a long-lived PAT (30-90 day expiration) at session start
  2. Claude caches PAT to `~/.git-credentials` for in-session reuse
  3. Sandbox is ephemeral — `/home/claude` resets between work sessions
  4. Owner re-pastes PAT at start of each new session
  5. Owner revokes PAT when project is paused or done
- **PAT settings (recommended):**
  - Name: `claude-sandbox-YYYY-MM-DD` or similar timestamp
  - Expiration: 30 days (re-issuable; long enough to avoid re-prompting per session, short enough to limit blast radius if leaked)
  - Type: Fine-grained PAT preferred over classic
  - Scope: Repository = `jeetmehta1991/stock-picks-app` only
  - Permissions: Repository → Contents = Read and write; Metadata = Read-only (auto-set)
- **Hard rules — NEVER violate:**
  - **NEVER commit the PAT to any tracked file.** PAT lives only in `~/.git-credentials` (untracked) or in the active session's `git remote set-url` config.
  - **NEVER write the PAT to any file under `/home/claude/stock-picks-app/`** (the repo working tree). That file would get caught by `git add` someday and pushed publicly.
  - **NEVER paste the PAT into AUDIT.md, LEARNINGS.md, CLAUDE.md, or any other repo file.** The pattern is documented here; the secret never is.
  - After each push, immediately reset the remote URL to remove the PAT from `.git/config` (which `git remote set-url <PAT-URL>` may have written): `git remote set-url origin https://github.com/jeetmehta1991/stock-picks-app.git`
- **Push cadence:** at meaningful checkpoints (theme closures, significant work milestones), not after every commit. Reduces re-issuance friction.
- **If push is rejected (remote ahead):** `git fetch origin main` → review remote commits → `git rebase origin/main` if file-change sets disjoint → push again. NEVER force-push without explicit owner approval.
- **Recovery if PAT compromised:** owner revokes PAT at github.com/settings/personal-access-tokens. Issues new one. Repaste in new session.

### Sprint Structure (Pass 53 Sprint 0A active per DEC-497)

**Active Sprint:** Sprint 0A — Full multi-API prefetch + universe build + Stage 2 NO-LIVE-API refactor.
- Universe build: T1a (614) + T1c (161) + T1 ETFs (27) + T2 (347 — full SCREENER 297 + PIT graduated-name backfill 50 per BUG-274; 0 blank sectors post BUG-275 fix) + T3 (1923 period rows / 1220 unique; 0 NULL post BUG-276 fix) — IMPLEMENTED Pass 53. Master Dedup 1,937 unique tickers w/ resolved_tier per DEC-504 (T3=993, T1a=501, T2=282, T1c=134, T1ETF=27).
- Sector normalization: 18-classifier set per DEC-499 (GICS-11 + Fixed Income, Commodities, Volatility, Broad Market, International, Emerging Markets, Small Cap)
- Polygon Stocks Starter prefetch: 1,821 OHLCV cached (extension to news/indicators/financials/events/NBBO pending)
- API scope (8 APIs): Polygon, Quiver Trader, FRED, ALFRED, AAII, CNN F&G (composite + 7 sub-components), CFTC COT, SEC EDGAR (structured per DEC-456)
- HARD CUT — NO LIVE API CALLS in Stage 2 backtest (owner directive 2026-05-05). yfinance permitted for one-time SETUP only.
- Folder: `data_prefetch/<api_name>/<endpoint>/...` (Polygon cache to be moved from `backtest/data/cache/polygon/` post-universe-validation)
- Smoke + demo tests per API (separate test files)

**Sprint 1 RENAMED → Sprint 0A** Pass 53 owner directive 2026-05-05. Prior Sprint 1 work absorbed into Sprint 0A naming.

**Sprint 2** — Engine bug fixes (DEC-491-493 trade_log Parquet + signals_at_entry filter + trade_id schema). Unchanged.
**Sprint 5** — Index rebalance + archived watchlist + monthly automation. Unchanged.
**Sprint 9** — Cube Explorer dashboard. Unchanged.

### Data Sources
- **NEVER use Wikipedia.** Historically blocked in Codespaces; not point-in-time; fragile (L88). Same fragility applies on local VS Code.
  - S&P 500 → `Backtesting universe/Current Snapshot_SP500 Tickers_May 2026.csv` (Pass 53 folder move per `c7f5580f`) refreshed quarterly via `scripts/refresh_sp500_universe.py` on LAPTOP using slickcharts.com
  - Never propose `pd.read_html('https://en.wikipedia.org/...')` for any purpose.
  - **One-time historical scrape exception (Pass 53 owner-granted, scoped):** Wikipedia + general internet browsing is permitted for ONE-TIME assembly of historical universe membership files (`historical_membership.csv`, `russell_1000_membership.csv`, `Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv`, `index_rebalance_events.parquet`) under these conditions: (i) laptop-local execution only, (ii) fallback source — primary is S&P DJI press releases / FTSE Russell / Nasdaq, (iii) manual verification before commit, (iv) not runtime — these scrapes happen pre-Sprint-1 to assemble static CSV inputs, never inside the backtest hot path. See AUDIT.md Pass 53 entries for exception scope details.

### CSV-first data architecture (Pass 53 owner directive — HARD RULE)
- **All input data and output data must live in CSV files (or Parquet for nested/binary data per DEC-491). No data should live exclusively in the codebase.** The code pulls data from CSV files; CSV is the source of truth.
- **Applies to:** universe lists (T1a/T1b/T1c/T2/T3 + ETFs), sector mappings, ticker overrides, calendar events, trade outputs, metrics outputs, regime classifications, strategy registers — anything that is data rather than parameter/logic/threshold.
- **Distinction from configuration:** Numerical thresholds (TRAILING_STOP percent, LIQUIDITY mins, position sizing tiers, slippage bps) and methodological choices (regime classifier formulas, statistical gates) ARE configuration/logic, NOT data — these can stay in code/config files. The line: if it's a *list of items*, *map of attributes*, or *historical record*, it's data → CSV. If it's a *behavior parameter* or *formula*, it's logic → code/config.
- **Past violations being corrected:** `ETFS_FULL` hardcoded in `universe.py` → `Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv` (DEC-494 / commit `e257d160`). `etf_sectors` dict in `universe.py:get_sector_map()` → migrate to read from `Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv` Sector column (queued). `SECTOR_OVERRIDES` dict in `scripts/refresh_sp500_universe.py` → could move to CSV (queued).
- **Apply when:** writing new modules that introduce hardcoded ticker lists / sector dicts / event calendars / known-good outputs; reviewing existing modules during sprint planning; adding new universe tiers or strategy categories. If you find yourself typing a Python list of tickers or a dict of attributes longer than 5 entries, stop and put it in a CSV instead.

### Universe Management
- `Current Snapshot_SP500 Tickers_May 2026.csv` must be refreshed quarterly (CHECKLIST item 19). If last commit >90 days old, flag before any run.
- New spinoffs above $5B market cap → add to Tier 2 immediately, don't wait for S&P 500 inclusion (SNDK waited 9 months — L89).
- **5-bucket architecture (Pass 53):** Tier 1 sub-tiers (T1a S&P 500 / T1b R1000-non-S&P / T1c NDX-non-S&P per DEC-483) + Tier 1 ETFs (per DEC-118 — `Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv` post DEC-494) + Tier 2 (`Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv` — spinoffs + recent IPOs per DEC-103) + Tier 3 (`Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv` — top 100 non-T1 momentum names per DEC-104/364).
- **All universe CSVs use B++ schema** with `added_date` / `removed_date` columns (per DEC-303); PIT loader filters by `(added_date IS NULL OR added_date ≤ as_of) AND (removed_date IS NULL OR removed_date > as_of)`.
- Tier 2 (extended universe — spinoffs >$5B + recent IPOs >$10B): **SCREENER-FIRST two-step flow per DEC-103/DEC-494 Pass 53 owner-corrected.** Step 1 — broad-market screener via Polygon `/v3/reference/dividends|splits|tickers` corporate-actions feed (canonical source, NOT yfinance ticker info which lags new listings per L89 SNDK 9-month example); filter by DEC-103 criteria (>$5B spinoff within 12 months / >$10B IPO with ≥90 days history). Step 2 — OHLCV prefetch for identified universe (~50-150 unique tickers across 2010-2026). **Sprint 1 historical populate** alongside T1 prefetch via DEC-380 corp-actions; **Sprint 5 ongoing automation** per DEC-372/373/374 (GH Actions monthly refresh) + DEC-380 (Polygon corp-actions live).
- Tier 3 (momentum watchlist): **SCREENER-FIRST two-step flow per DEC-496 Pass 53 owner-corrected.** Step 1 — broad-market screener via Polygon `/v2/aggs/grouped/locale/us/market/stocks/{date}` (NOT existing T1 cache — running J-T against T1-only defeats T3's purpose since T3 = top 100 NON-T1 names); apply DEC-321/366 Tier 3 liquidity floor; compute Jegadeesh-Titman 12-1 momentum per DEC-496 (252-day lookback, 21-day skip, risk-adjustment OFF, tie-breakers vol-asc→ADV-desc); exclude T1a/T1b/T1c at as_of D; rank descending; top 100 per DEC-364. Step 2 — OHLCV prefetch for identified non-T1 union (~500-1000 unique tickers across 72 monthly snapshots; Pass 53 owner-approved full historical scope 2020-2026). **Sprint 1 historical populate** alongside T1 prefetch; **Sprint 5 ongoing automation** per DEC-104/375/376/377. Static for backtesting (computed at each monthly snapshot date; not lookahead).
- **Universe construction screener-first principle (Pass 53 HARD RULE — owner Q-D codified):** Any universe-tier construction step that requires identifying tickers OUTSIDE an existing cache (e.g., T2 = non-T1 spinoffs/IPOs, T3 = non-T1 momentum) MUST be a broad-market screener with explicit input source (Polygon endpoints), not a re-rank of an existing tier's cache. Verify input universe ≠ output universe at recommendation time. See CHECKLIST #66.b.
- **Stage 3+ archived watchlist (DEC-495 RESOLVED-DECIDED Pass 53):** When a ticker rotates out of all 5 buckets (T1a/T1b/T1c/T2/T3), it is tracked in `archived_watchlist.csv` (schema: `Symbol, Company, Last_Tier, Last_Active_Date, Removal_Reason, Notes`) for close-out reference + re-entry monitoring + historical reanalysis. Daily reconciliation job (Stage 3+ implementation, Sprint 5 work). Forward-only from Stage 3 start (no Stage 2 retroactive backfill per Pass 53 default).

### Strategy Changes
- No strategy or rule changes without explicit owner approval. Every threshold, filter, and parameter change requires sign-off.
- The per-regime verdict system means a strategy that fails in one regime is NOT discarded — it is tagged for the regimes where it passes.

### Pre-Recommendation Checklist Application (Pass 52 owner-mandated standing rule)
**MANDATORY: Apply the full CHECKLIST.md as a pre-condition gate before stating EVERY recommendation. No exceptions.**

- Before each recommendation in any response, explicitly reference and verify each applicable checklist item.
- Items not applicable to a given recommendation must still be referenced (mark as N/A with reason). The act of referencing each item is what catches errors — skipping the reference is what allows pattern-match-without-verification failures.
- Verification format: per-recommendation pre-flight block showing checklist items + status + evidence (grep output, cross-references, math). NOT deferred to end-of-response compliance statement.
- End-of-response compliance statement (#45) remains required, but it is post-hoc. The pre-flight per-recommendation block is what actually catches errors before they become stated recommendations.
- This rule applies to: recommendations, proposed schemas, threshold values, scope claims, framework designs, dimensional inventories, ANY assertion of "this is what we should do." Does NOT apply to: factual answers to direct questions, verification reports of code state, status updates.
- Pattern lineage: 6 consecutive lapses in DEC-422 framework drafting (Pass 52) caught by owner because end-of-response compliance was post-hoc. Owner mandate: pre-flight per recommendation is the only way to make verification automatic.
- If a checklist item flags an issue, the recommendation must be REVISED before stated. Surfacing findings in pre-flight is success, not failure — it's the system working.
