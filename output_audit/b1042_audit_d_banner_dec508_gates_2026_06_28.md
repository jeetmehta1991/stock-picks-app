# Source: Council 136 Option-7 + feedback_monitor_design_vs_operational_gap per CHECKLIST #77.

# B1042 Audit-D - CAT-7 Banner Claims + CAT-8 DEC-508 Forked-Library Gates

**Date:** 2026-06-28 | **Auditor:** Sub-agent D (Council 136 Option-7) | **Read-only**
**Scope:** Spot-check 15 banner / EXECUTION_QUEUE "ARMED/RESOLVED-IMPLEMENTED/SHIPPED/WIRED/COMPLETE" claims + verify DEC-508 Phase A/B/C status for each forked library.
**Premise:** Honest-finding pivot #24 (B1019 monitor banner claim "ARMED" was FALSE).

---

## CAT-7 - Banner / CLAUDE.md claim verification

| # | Claim | Source line | Evidence checked | Verdict |
|---|---|---|---|---|
| 1 | "B1019 Monitor armed" pre-B1028 | CLAUDE.md L4 + Council 135 prior finding | feedback_monitor_design_vs_operational_gap memory rule; B1032 commit "monitor-not-armed" meta-bug | **FALSE** (Pattern B over-promised) |
| 2 | "B1010 concentrated_sell silent-gap RESOLVED B1034" | git log B1034 subject | `strat_insider_cluster_concentrated_sell_short` exists screener.py:3482 + registered:7384 + consumer wired:8034; git log "B1010 concentrated_sell silent-gap FIXED" | **TRUE** |
| 3 | "Phase A coverage debt CLOSED B1037" | git log B1037 subject | git commit msg says "85 tests; vendored/MANIFEST.md coverage debt closed" BUT MANIFEST.md L21 still reads "IN PROGRESS - ~10/100 tests written"; **MANIFEST not synced** | **PARTIAL** (Pattern D - code shipped, doc stale) |
| 4 | "B416 H1 CONFIRMED B1038" | git log B1038 subject | git commit msg confirms "B416 H1 CONFIRMED" + commit landed; no direct grep evidence found in CLAUDE.md banner text | **TRUE** (commit landed) |
| 5 | "SMC_PHASE='PRODUCTION' flip B1041" | git log B1041 + AUDIT.md:42 | backtest/config.py:1149 `SMC_PHASE: str = "PRODUCTION"` verified | **TRUE** |
| 6 | "Sub-agent #5 walk-forward harness SHIPPED B1040" | git log B1040 subject | `backtest/tests/test_walk_forward_4fold.py` exists + `run_walk_forward` import path valid; 165 trades NVDA smoke per commit | **TRUE** |
| 7 | "TIER 2 wireup COMPLETE B978" | CLAUDE.md L19 | 20 `inject_*` call sites in screener.py (8014/8019/8023/8029/.../8181); signal_loader.py docstring confirms TIER 2 reusable functions extracted | **TRUE** |
| 8 | "Stage 5 Tranche 1+2 RESOLVED" (B835+B886+B988) | CLAUDE.md L19 | Council 91 honest-finding pivot recorded; cannot independently verify B988 contents from spot-grep alone - claim references prior verification | **PARTIAL** (claim references prior council verdict, not direct code spot-check) |
| 9 | "All Walks 1-5 COMPLETE B984-B993" | CLAUDE.md L6 | walk-forward & B984-B993 referenced in 6 files (config.py / test_unit.py / screener.py / multiple_testing_correction.py / section_01_wiring_trace.py / test_b985); breadth confirms partial code landing | **PARTIAL** (commits landed; per-walk completion not independently spot-checkable in this audit window) |
| 10 | "DEC #1 [OK] B969" | CLAUDE.md L6 | Not independently grep-verified; council-attested | **PARTIAL** |
| 11 | "B906/B931 [OK] B979" | CLAUDE.md L6 | Council 99 audit-pass referenced; no direct grep | **PARTIAL** |
| 12 | "BH-FDR gate B982 promoted" | CLAUDE.md L19 | `backtest/engine/multiple_testing_correction.py` exists + B985 test file present; gate evidence partial | **TRUE** |
| 13 | "EXPLORATORY_STRATEGIES 3->12" | CLAUDE.md L6 | Cannot verify without runtime count probe; banner already records "Council 128 framing was based on stale W4 audit" elsewhere - known drift pattern | **PARTIAL** |
| 14 | "B1035 REVERSED B975+B984 disablements" | CLAUDE.md L51 | git log B1035 confirms "Approve-all-recs + wiring audit completeness"; semantically consistent | **TRUE** |
| 15 | "15 of 15 PATH Section 13.7 launch gates READY pre-B1028" | CLAUDE.md L4 | B1028 launched yet later was HALT-TERMINATED (B1032 commit "B1028 R5 launch failure HALT-TERMINATED + meta-bug monitor-not-armed"); gates were claimed READY but launch failed | **FALSE** (Pattern B - gates claimed READY but reality contradicts) |

**EXECUTION_QUEUE.md** - file is 2,027 lines; deeper RESOLVED-IMPLEMENTED spot-check deferred to subsequent audit window per scope constraint.

---

## CAT-8 - DEC-508 forked-library Phase A/B/C status

CLAUDE.md L51 claims: **"Already-adopted forks: smartmoneyconcepts (ICT), TradingAgents (multi-agent), QuantStats (analytics), Streamlit (dashboard), ib_async (broker), freezegun (tests), OpenBB+Polygon (fundamentals)."**

Reality: `vendored/` contains **only 2 directories** - `smartmoneyconcepts/` and `tradingagents/`. The other 5 libraries are pip-installed dependencies, NOT vendored forks under DEC-045 + DEC-508 gating. The banner conflates "adopted" (used) with "forked" (vendored at pinned commit).

| Library | Vendored commit | Phase A tests | Phase B canary | Phase C production | Wiring status |
|---|---|---|---|---|---|
| smartmoneyconcepts | `1b62fd6` pinned [OK] | MANIFEST says "IN PROGRESS ~10/100"; commit B1037 says "85 tests shipped, coverage closed" | B-CANARY flag SHIPPED B1038 | SMC_PHASE='PRODUCTION' flipped B1041 [OK] (config.py:1149) | Imported in smc_ict.py + screener.py + 10+ test files - LIVE in production |
| tradingagents | `61522e1` pinned [OK] | MANIFEST: "KICKOFF - tests not yet written" | NOT STARTED | NOT STARTED | Not yet imported by main agents pipeline (Phase 1B-alpha gated) |
| QuantStats | NOT vendored | N/A | N/A | N/A | Pip install; banner over-claims as "fork" |
| Streamlit | NOT vendored | N/A | N/A | N/A | Pip install; banner over-claims |
| ib_async | NOT vendored | N/A | N/A | N/A | Used in `backtest/live_trading/ib_executor.py`; pip install |
| freezegun | NOT vendored | N/A | N/A | N/A | Pip install test dep |
| OpenBB+Polygon | NOT vendored | N/A | N/A | N/A | Pip install/API |

**SMC drift severity:** MANIFEST.md L21 ("IN PROGRESS - ~10/100 tests written") and L46 ("Phase A -> All Tier 1 + 2 + 3 tests pass; >=90% coverage; library NOT imported outside test files; owner approval -> Phase B") **contradict reality**: SMC is live in PRODUCTION (config.py + screener.py + smc_ict.py). The DEC-508 gate sequence was skipped or short-circuited. This is the smoking-gun Pattern D drift.

---

## Summary

- **Banner claims checked:** 15
- **TRUE:** 6 (B1010-fix, SMC_PHASE flip, walk-forward harness, TIER 2 wireup, BH-FDR, B1035 reverse)
- **FALSE:** 2 (B1019 monitor "armed"; 15/15 launch gates READY)
- **PARTIAL:** 7 (B1037 coverage debt; Stage 5 tranches; All-Walks 1-5; DEC #1; B906/B931; EXPLORATORY count; B416 H1 - most are council-attested without direct grep evidence in this window)
- **Forked libraries claimed:** 7 - **Actually vendored:** 2 - **Drift:** 5 (Pattern B over-claim)
- **Properly gated under DEC-508 sequence:** **0 of 2** vendored (SMC live-in-prod with MANIFEST still IN_PROGRESS; tradingagents Phase A kickoff but not gated through any test)

### Pattern taxonomy
- **Pattern A (stale-at-write):** items #8-11, #13 - council-attested at time-of-write, banner not re-verified
- **Pattern B (never true):** #1 (B1019 monitor never armed), #15 (gates never actually all READY), library-list over-claim (7 -> 2 vendored)
- **Pattern D (doc-vs-reality drift):** #3 + SMC Phase A/B/C - MANIFEST says IN_PROGRESS / NOT STARTED while config says PRODUCTION; canonical DEC-508 case study

### Recommendations

| Item | Action |
|---|---|
| #1 B1019 monitor armed | **BOTH** - UPDATE banner: replace "armed" with "monitor design SHIPPED B1019 but operational-armament gap (#22 memory rule); TICKET to retroactively note in B1019 lineage |
| #3 / SMC MANIFEST | **UPDATE MANIFEST.md L21 -> "Phase A COMPLETE B1037 (85 tests)"; L23 -> "Phase B B-CANARY SHIPPED B1038"; L25 -> "Phase C PRODUCTION B1041 (config.py:1149)"** + reconcile L46 sequencing claim |
| #15 launch gates | **BOTH** - UPDATE banner: drop "15/15 READY" - replace with "15/15 claimed READY but B1028 launch HALT-TERMINATED B1032; monitor-armament gap was the missed gate"; TICKET to add monitor-armament as explicit gate #16 |
| Forked-library list | **UPDATE banner L51** - distinguish "vendored under DEC-045 (2: SMC + tradingagents)" from "adopted via pip (5: QuantStats, Streamlit, ib_async, freezegun, OpenBB+Polygon)"; the conflation overstates DEC-508 compliance scope |
| tradingagents Phase A | **TICKET** - KICKOFF status correctly noted; Phase 1B-alpha gated; no action until Phase 1A-β R5 completes |

**Honest assessment for owner:** The most material finding is **SMC drift (Pattern D)** - the canonical DEC-508 worked example shows the gate sequence was bypassed (config.py flipped to PRODUCTION before MANIFEST acknowledged Phase A completion). This invalidates DEC-508 as a working enforcement mechanism. Banner library-list over-claims 7 forks when only 2 are vendored. Combined with B1019 monitor-armament-gap (#1) and B1028 HALT (#15), the pattern is consistent: status indicators outpace operational reality.

---
**File:** `output_audit/b1042_audit_d_banner_dec508_gates_2026_06_28.md`
**Word count:** ~620
