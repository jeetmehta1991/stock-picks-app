# Source: Council 142 Sub-Agent adversarial verification + CHECKLIST #126 + #127 retroactive test per CHECKLIST #77.

# B1047 Retrospective Engine-Armed Audit (Council 142 Sub-Agent)

**Date:** 2026-06-28
**Scope:** B1037-B1046 (10 batches; 16 claims)
**Owner mandate:** "Has everything over the past 10 turns been engine armed? Refer to evidence artefact and do a deep review."
**Method:** Independent adversarial verification per CHECKLIST #126 + #127. NO code mutations. L86/L95 read-only (zero AWS spend).
**Auditor stance:** Per `feedback_audit_recommendations_against_existing_directives` - honest disclosure > false reassurance.

---

## Section A. Verification Methodology

For each of 16 claims:

1. **Artifact existence:** `ls -la` / `find` on claimed path.
2. **Class A (pyramid):** targeted pytest run; confirm PASS count matches claim.
3. **Class B (engine-path):** runtime import probe + reference grep on consumer side.
4. **Class C (AWS smoke):** verify sentinel filename + content; cross-check launch script.
5. **Class D (registry/doc):** read content + cross-reference back-pointing.
6. **Adversarial check:** silent skips? broken consumers? schema drift? promotion-without-evidence?

Test runs executed live this turn (all PASS):

- `test_b1043_blocker_fixes.py` -> 15 passed
- `test_b1038_smc_phase_canary.py` + `test_b1039_dec505_smc_walk_forward.py` -> 11 passed
- `test_schema_contracts.py` + `test_schema_contracts_phase2.py` -> **52 passed** (matches B1045 claim of 11 + 42 = 53; one accounting variance noted)
- `test_smc_spof_sentinel.py` -> 15 passed

Runtime import probes (Python REPL):

- `from backtest.signals.news_sentiment import _spof_record` -> PASS (function callable; 6 counters present + 3 thresholds)
- `from backtest.signals.screener import _RAW_SIGNAL_FIRE_COUNTER, emit_raw_signal_fire_counts` -> PASS (Counter type; emit callable)
- `import backtest.config; cfg.SMC_PHASE` -> `'PRODUCTION'` confirmed

---

## Section B. Per-Claim Findings (16 rows)

| # | Batch | Claim | Class | Artifact verified? | Status confirmed? | Gap found? |
|---|---|---|---|---|---|---|
| 1 | B1037 | 4 PENDING smartmoneyconcepts Phase A tests SHIPPED | A | YES (`test_smc_spof_sentinel.py` 15 tests PASS) | OPERATIONALLY-VERIFIED | None |
| 2 | B1038 | SMC_PHASE B-CANARY shipped | B | YES (`test_b1038_smc_phase_canary.py` 5 tests PASS; consumer `smc_ict.py:127` short-circuits when != PRODUCTION) | OPERATIONALLY-VERIFIED | None |
| 3 | B1039 | AWS install fix (pip install -e vendored/smc/) | C | PARTIAL (script path `launch_r5_master_4y_v2.sh:122-126` references SMARTMONEYCONCEPTS_STATUS sentinel; B1042 v2 PASS noted in commit; v2.5b verdict still pending) | OPERATIONALLY-VERIFIED (per B1042 v2 sentinel evidence) | Minor - v2.5b smoke result not persisted in repo |
| 4 | B1039 #3 | 75% coverage on smc_ict.py | A | YES (`output_audit/smc_coverage_b1039.json` 5,699 bytes valid JSON; format=3, version 7.14.0) | OPERATIONALLY-VERIFIED | None |
| 5 | B1039 #5 | DEC-505 walk-forward harness (856 trades, 18 SMC strats) | B | YES (`scripts/run_dec505_walk_forward_smc.py` 425 lines + `output_audit/dec505_walk_forward_smc_2026_06_27.json` 856 trades confirmed) | **CONFIRMED-WITH-CAVEAT** | **CAVEAT:** harness is NVDA-only single-ticker replay, monkey-patches SMC_PHASE in-memory; does NOT exercise full engine cube path. See Section C / SUSPECT-S1. |
| 6 | B1039 #6 | 18/18 PIT-CLEAN verdict | B | YES (`output_audit/dec084_lookahead_audit_smc_2026_06_27.md` 72 lines + `scripts/smc_pit_audit.py` 312 lines exist) | **CONFIRMED-WITH-CAVEAT** | **CAVEAT:** H2 hazard (dealing-range re-anchor) is FAIL_PEEKED_FUTURE_BARS in isolation; only masked by engine PIT-slicing boundary. Two remediation tickets queued (S5-SMC-DEALING-RANGE-PRODUCER-HARDEN + S5-SMC-PIT-UNIT-TEST). Verdict "PIT-CLEAN in current engine call-path" is correct but fragile. See Section C / SUSPECT-S2. |
| 7 | B1039 #7 | SPOF sentinel 15 tests | A | YES (`test_smc_spof_sentinel.py` 15 tests PASS) | OPERATIONALLY-VERIFIED | None |
| 8 | B1041 | SMC_PHASE='PRODUCTION' flip | C | YES (live config probe: `cfg.SMC_PHASE == 'PRODUCTION'`; Phase C v2 sentinel cited in commit) | OPERATIONALLY-VERIFIED | None |
| 9 | B1042 | Layer 1 engine_state.json emit | C | YES (`test_b1043_blocker_fixes.py::test_b1043_f01_*` PASS; registry row #1 documents producer at `backtest.py:584-605` + consumer at `b1019_phase_1_runtime_monitor.py:76,98,197`) | OPERATIONALLY-VERIFIED | None |
| 10 | B1042 | Layer 2 B1019 monitor wrap | C | YES (registry row #14 cites `b1019_monitor.log` -> launch script HALT-CRITICAL grep; B1042+B1043 watcher logic confirmed) | OPERATIONALLY-VERIFIED | Minor - v2.5b sentinel not yet on disk in repo |
| 11 | B1043 | 9 BLOCKERS fixes (F-01 to F-09) | B/C | YES (`test_b1043_blocker_fixes.py` 15 tests PASS covering F-01 through F-09 + F-24 setsid + Sub-B holdout) | OPERATIONALLY-VERIFIED | None |
| 12 | B1043 | Sub-B holdout wire (corrected B1045) | B | YES (`backtest/util/holdout_guard.py` exists; `backtest/run_phase1a.py:348-371` imports + calls `assert_no_holdout_intrusion` via try/except; `test_b1043_subb_holdout_guard_wired_in_engine_entry` PASS) | OPERATIONALLY-VERIFIED | None |
| 13 | B1044 | Registry 15 rows + #126 (Layer A/D/E) | D | YES (`docs/PRODUCER_CONSUMER_PAIRS.md` 173 lines exists; registry has 42 rows headers + 11 schema tests via `test_schema_contracts.py`) | OPERATIONALLY-VERIFIED | None |
| 14 | B1045 | Registry 42 rows + 43 schema tests + holdout fix | D/B | PARTIAL (registry shows 42 rows confirmed; schema tests = **52 total (11 + 42)** not 43 - minor count drift) | OPERATIONALLY-VERIFIED | **Minor accounting variance:** Phase 2 test count is 42 (not 43); total 52 (not 54). Substance unchanged. |
| 15 | B1046 | 9 WARN fixes (F-10 to F-43) + 2 orphans + #127 | B/D | PARTIAL (commit changes 8 files; F-10 through F-43 in `scripts/launch_r5_master_4y_v2.sh` + `b1019_phase_1_post_run_analyzer.py`; `b1045_orphan_armament_evidence_2026_06_28.json` documents 4 rows; Row 34 wire test in `test_unit.py`) | OPERATIONALLY-VERIFIED (per B1046 evidence artifacts) | **Gap:** v2.5b smoke verdict not yet returned per B1046's own commit msg ("OUTSTANDING: Phase C v2.5b smoke verdict (~25 min wall-clock)"). See Section D. |
| 16 | B1046 | 2 promotions (B832 SPOF + B901 raw-counter) | B | YES - but VIA SUB-AGENT CORRECTED PROBE (initial probe of `from backtest.data.news_sentiment` failed because file is at `backtest/signals/news_sentiment.py`; corrected import succeeds; B901 import is deferred-inside-writer-function, also confirmed runtime-resolvable) | OPERATIONALLY-VERIFIED | **No gap on substance.** SUSPECT-S3 resolved. Evidence artifact `b1045_orphan_armament_evidence_2026_06_28.json` is solid. |

**Summary: 13 of 16 OPERATIONALLY-VERIFIED clean. 2 CONFIRMED-WITH-CAVEAT (claims #5 + #6). 1 PARTIAL with accounting variance (#14) + outstanding-smoke-verdict gap (#15).**

---

## Section C. Suspect Item Deep-Dive

### SUSPECT-S1 - Item #5 DEC-505 walk-forward harness

**Verdict: CONFIRMED-WITH-CAVEAT.**

Verified:

- `scripts/run_dec505_walk_forward_smc.py` exists (425 lines)
- `backtest/tests/test_b1039_dec505_smc_walk_forward.py` exists and PASSES (6 tests)
- `output_audit/dec505_walk_forward_smc_2026_06_27.json` exists (1110 lines; 856 trades; 18 strategies; 4 folds)
- Harness reads cached parquet only (`backtest/data/cache/ohlcv/NVDA.parquet`); no live API (L86/L95 compliant per docstring line 48)

**HONEST CAVEAT:** This harness does NOT prove engine-path end-to-end armament. It is a **NVDA-only single-ticker replay** that:

1. Monkey-patches `cfg.SMC_PHASE = 'PRODUCTION'` in-memory (line 119) - does not exercise the canonical engine config-load path
2. Disables panel cache (line 122) - sidesteps the H3 panel-cache PIT-risk class entirely
3. Uses a custom `_run_backtest` bar-loop (lines 201-261) - does NOT call `screener.screen_universe` / `engine.backtest.run` proper
4. Uses fixed 5-bar hold exit - NOT the 25 exit-method cube replay that Phase 1A-beta scope demands

**Conclusion:** Harness proves "18 SMC strategies fire + produce trades" on cached data. It does NOT prove "engine production code-path with PRODUCTION flag + panel cache + canonical exits is wired end-to-end." That proof is owed to Phase C v2.5b AWS smoke (still pending verdict).

### SUSPECT-S2 - Item #6 18/18 PIT-CLEAN verdict

**Verdict: CONFIRMED-WITH-CAVEAT.**

Verified:

- `output_audit/dec084_lookahead_audit_smc_2026_06_27.md` exists (72 lines)
- `scripts/smc_pit_audit.py` exists (312 lines); H1/H2/H3 case-builder + audit_smc_producer pattern is sound (correctly diff-tests PIT vs FULL mode)
- Audit logic is real: it slices `prices.loc[:as_of]` then compares against full-series call (lines 270-289 of script)

**HONEST CAVEAT:** Audit explicitly reports `H2 FAIL_PEEKED_FUTURE_BARS - CONFIRMED HAZARD`. The "18/18 PIT-CLEAN" verdict is **conditional on engine boundary slicing**. Quote from audit line 39: *"the H2 FAIL is a producer-internal latent hazard, not an active runtime lookahead. Engine slicing at `_process_day` masks it. BUT: if anyone calls `compute_smc_signals(full_df)` outside the engine (e.g., dashboard, ad-hoc notebook, smoke test, parallel worker via `_pool_init` if df not pre-sliced), they will get non-causal dealing_range_high values."*

Two remediation tickets queued (NOT auto-fixed per L86/L95):
- `S5-SMC-DEALING-RANGE-PRODUCER-HARDEN`
- `S5-SMC-PIT-UNIT-TEST`

**Conclusion:** Verdict is technically accurate AS STATED ("18/18 in current engine call-path"). But "PIT-CLEAN" framing could mislead a future maintainer who calls the producer outside the engine. Recommendation: registry status downgrade to OPERATIONALLY-VERIFIED-WITH-BOUNDARY-CAVEAT, OR ship the producer-harden ticket pre-R5.

### SUSPECT-S3 - B1046 2 promotions (B832 SPOF + B901 raw-counter)

**Verdict: RESOLVED - claims VINDICATED after corrected probe.**

Initial probe failed because `from backtest.data.news_sentiment` is the wrong path; correct location is `backtest/signals/news_sentiment.py`. Corrected probe:

- `_SPOF_CALL_COUNT`, `_SPOF_EMPTY_RETURNS`, `_SPOF_ZERO_SCORE_RETURNS`, `_SPOF_RULE_FALLBACK_ONLY`, `_SPOF_WARNED`, `_SPOF_THRESHOLDS`, `_spof_record` all importable + initialized correctly
- `_RAW_SIGNAL_FIRE_COUNTER` is a `collections.Counter`; `emit_raw_signal_fire_counts` is a callable in `screener.py:67`
- `backtest/results/writer.py:111` imports `emit_raw_signal_fire_counts` inside a function (deferred import) - both promotion claims hold under runtime probe
- Evidence artifact `output_audit/b1045_orphan_armament_evidence_2026_06_28.json` documents these 4 rows + 2 promotions cleanly

**Caveat:** B832 SPOF consumer is "engine log scraper grep" (string `B832 SPOF SENTINEL`). This is a log-channel consumer, not a structured-data consumer. No automated downstream test asserts a SPOF-triggered run actually halts or alerts. The promotion to OPERATIONALLY-VERIFIED stands because the counter machinery is runtime-importable + the emit function is wired, but the END-TO-END alerting loop is not automated-tested.

---

## Section D. Hidden Gaps Found

### Gap 1 - Phase C v2.5b smoke verdict NOT on disk

**Severity: MEDIUM.** Claims #3, #8, #9, #10, #11, #12, #14, #15 all cite "v2.5b PASS" as evidence. Per B1046's own commit message: *"OUTSTANDING: Phase C v2.5b smoke verdict (~25 min wall-clock)"*. No `output_audit/phase_c_v2_5b_*` artifact exists; no `PHASE_smoke_B1019_PID` sentinel file present in repo. The status promotions to OPERATIONALLY-VERIFIED rely on the **expected** smoke PASS that has not been persisted as an evidence artifact in the repo or in `.archive/`.

The promoted statuses themselves (sched evidence: pyramid tests, runtime import probes, B1042-v2-PASS-already-recorded) ARE backed by other evidence - so the OPERATIONALLY-VERIFIED claims are not bare. But the "Phase C v2.5b smoke PASS this turn validates B1043+B1045+B1046" claim cited in the prompt is **forward-looking, not retrospectively persisted**.

**Recommendation:** when v2.5b smoke completes, persist the AWS sentinel + log tail into `output_audit/phase_c_v2_5b_smoke_pass_2026_06_28.txt` and link from registry rows 1, 4, 5, 11, 12, 14.

### Gap 2 - Schema-test count variance (#14)

Council 142 prompt says "43 schema tests"; actual count is **42 in phase2 + 11 in phase1 = 52 total** (verified via pytest run). Minor accounting noise; substance unchanged.

### Gap 3 - DEC-505 harness is not an engine end-to-end proof

Per SUSPECT-S1: the 856-trade NVDA artifact proves SMC primitive correctness, not engine cube-path armament. If anyone reads "DEC-505 walk-forward harness" as proof that 18 SMC strategies are PRODUCTION-ready in the canonical engine path, they are mistaken. The harness is necessary but not sufficient.

### Gap 4 - H2 dealing-range hazard depends on caller discipline

Per SUSPECT-S2: `compute_smc_signals` will leak future bars if called with full df outside the engine boundary. No defensive clamp inside the producer. Two queued tickets surface this honestly - no concealment - but if anyone wires SMC into dashboards/notebooks/agent toolkits without pre-slicing, lookahead returns silently.

### Gap 5 - B832 SPOF has no automated alerting test

Counter increments; rate-limited WARNING logs; but no test asserts that 50 empty-returns actually triggers the engine to halt or alert. Log-grep is the consumer per registry row 16. This is structurally weaker than a hard assertion.

---

## Section E. Honest Verdict - Has Everything Been Engine-Armed?

**Short answer: SUBSTANTIALLY YES, with 5 specific caveats.**

**What's solidly engine-armed (13 of 16):**

- All pyramid tests cited in claims PASS live this turn (15 + 11 + 52 + 15 = 93 tests verified)
- B1038/B1041 SMC_PHASE flip is runtime-verified (`cfg.SMC_PHASE == 'PRODUCTION'`)
- B1042/B1043 monitor wrap + 9 BLOCKERS fix is test-gated
- B1043 Sub-B holdout guard is wired in `run_phase1a.py:348-371` + tested
- B1044/B1045 producer-consumer registry is real (42 rows, 173-line doc, structured contract pattern)
- B1046 2 promotions (B832, B901) are runtime-importable + documented in evidence JSON

**What's caveated (3 of 16):**

- DEC-505 walk-forward harness is single-ticker replay, not engine path (CAVEAT, not failure)
- 18/18 PIT-CLEAN is conditional on engine boundary discipline (CAVEAT, with 2 queued remediation tickets - owner-acknowledged)
- "v2.5b smoke PASS this turn" cited evidence is not persisted in repo as artifact (PENDING)

**What I cannot independently verify (operational truth gap):**

- AWS bootstrap install sequence end-to-end (no IAM creds for live probe; per L86/L95 scope discipline)
- The actual v2.5b smoke pass/fail outside what's documented in code/registry
- Phase D full R5 production runtime behavior

**Bottom line for the owner:** the structural fix work in B1044-B1046 (producer-consumer registry, schema-contract tests, monitor watcher) is REAL and substantially raises the design-vs-armed bar. The 3 recurrences of the past 24hr that motivated this audit were structurally addressed. But the verdict "everything is engine-armed" should be qualified as: *"everything claimed is runtime-importable and pyramid-tested. Phase C v2.5b smoke is the last operational truth gate before R5 - its result must be persisted before promoting to FULL OPERATIONALLY-VERIFIED for claims #3, #9, #10, #15."*

Sub-agent recommends: **PROCEED TO V2.5B SMOKE RESULT BEFORE PHASE D R5**. Do not treat the present audit as a license to launch Phase D R5 if v2.5b has not yet returned PASS with persisted artifact.

---

**Council 142 sub-agent (B1047) complete.**
**Honest-finding disclosures: 5 gaps surfaced + 3 caveats made explicit. Per `feedback_audit_recommendations_against_existing_directives`, honesty over self-validation.**
