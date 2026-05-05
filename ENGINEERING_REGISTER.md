# Engineering Register — Implementation Tracking

**Generated:** Pass 52 turn 42
**Purpose:** Per-sub-decision tracking from audit-decided to engineering-implemented
**Status semantics:**
- **RESOLVED-DECIDED:** owner-approved spec; engineering not yet started or in progress
- **RESOLVED-IMPLEMENTED:** engineering complete + tests passing per sub-decision Test Signals + verified
- **BLOCKED_ON_X:** decided but waiting on prerequisite

---

## Cadence

- **1-week sprints**
- **Sprint demo** at end of each week: working code + verified test signals
- **Owner reviews demo** + approves batch status flip RESOLVED-DECIDED → RESOLVED-IMPLEMENTED for completed sub-decisions
- **Engineer:** owner-self with Claude Code pair programming
- **Branch model:** feature branch per sprint; PR to main; merge after owner approval
- **Pyramid layers per sprint:** each sprint declares which test pyramid layers (per PROJECT_PLAN.md §21.1: unit / integration / characterization / property / differential) its tests touch — surfaced in the `**Pyramid layers touched:**` field on each sprint header below (per PROJECT_PLAN.md §22.1)

---

## Sprint Roadmap

### Sprint 1 — Phase 0.A Polygon Foundation (Week 1)

**Entry criteria:**
- Polygon Stocks Starter $29/mo subscription active (DEC-441/478/479 owner-action: subscribe; cost corrected from $30/mo)
- API key in `.env` (local VS Code on Windows laptop)
- main branch in clean state
- Sprint 0 verified: AAII + CNN F&G + SEC EDGAR domains reachable from local VS Code (Codespace allowlist concern moot since running locally Pass 53)

**Universe scope (DEC-483 RESOLVED-DECIDED Pass 53):**
- Tier 1a: S&P 500 (~503 tickers; day-grain PIT via DEC-303 historical_membership.csv per DEC-477)
- Tier 1b: Russell 1000-non-S&P (~497 net new tickers; year-grain PIT via FTSE Russell annual reconstitution)
- Tier 1c: NASDAQ 100-non-S&P (~15 net new tickers; year-grain PIT via Nasdaq annual reconstitution)
- Total: ~1015 unique Tier 1 tickers (was ~509 pre-Pass-53)
- Cache size impact: ~16-24 GB (was ~8-12 GB); prefetch wall ~2 days (was ~1 day)
- Sprint 1 effort: ~25-35d (was 20-28d; +5-7d for sub-tier expansion)

**Walk-forward configuration (DEC-482 RESOLVED-DECIDED Pass 53; SUPERSEDES DEC-109):**
- Expanding window 2y+/6mo OOS × 5 folds within 5y Polygon Stocks Starter window
- Total OOS coverage: 2.5yr across folds
- Implementation deferred to Sprint 7 walk_forward.py refactor

**Sub-decisions in scope:**
| DEC-N | Description | Test signals (verification criteria) | Branch | PR | Status |
|---|---|---|---|---|---|
| DEC-441 | Polygon $29/mo subscription | API key configured; sample fetch returns non-empty | (no code) | (owner action) | RESOLVED-DECIDED |
| DEC-256 | Polygon earnings prefetch | Non-empty parquet ≥95% S&P 500; days_to_earnings computable; PIT loader rejects EPS_actual queries with as_of < report_date | sprint1/dec-256 | - | RESOLVED-DECIDED |
| DEC-257 | Polygon→yfinance fundamentals | All 15 required fields ≥90% S&P 500 × 20 quarters; PIT loader rejects fields with as_of < estimated filing_date. **NOTE Pass 53:** consumer is Phase 1B (OurFundamentalsToolkit), not Phase 1A; full financials deferred to Sprint 4 SEC EDGAR (DEC-484) | sprint1/dec-257 | - | RESOLVED-DECIDED |
| DEC-440 | Polygon news endpoint | Non-empty news cache for sample; sentiment score field populates | absorbed in DEC-256 | - | RESOLVED-DECIDED |
| DEC-261 | ICT/SMC PIT N+1 lag rule | Synthetic FVG forms at bar 100 → strategy entry at bar 101 open | sprint1/dec-261 | - | RESOLVED-DECIDED |
| DEC-260 | Cache freshness assertion | Synthetic stale cache raises CacheStaleError; fresh cache passes; allow-listed stale ticker passes with warning | sprint1/dec-260 | - | RESOLVED-DECIDED |
| DEC-477 | historical_membership.csv canonical universe | Static 482-CSV deprecation warning fires; canonical csv loaded for T1a | sprint1/dec-477 | - | RESOLVED-DECIDED |
| DEC-478 | Polygon Stocks Starter $29/mo selected | Subscription verified; 5y history available | (subscription) | - | RESOLVED-DECIDED |
| DEC-479 | Cost correction $30→$29 | Cost references updated across 6 docs | (doc-only) | - | RESOLVED-DECIDED |
| DEC-483 | Universe sub-tiers T1a/T1b/T1c | T1a returns 503; T1b returns ~497 net new; T1c returns ~15 net new; year-grain PIT correct for any 2023 date returns 2023 R1000 list | sprint1/dec-483 | - | RESOLVED-DECIDED |

**Exit criteria:**
- All sub-decisions' test signals pass
- Sample backtest run uses Polygon as primary source for OHLCV/earnings/fundamentals
- T1a + T1b + T1c universe builds operational with PIT correctness
- All promoted to RESOLVED-IMPLEMENTED on owner approval

**Effort:** ~25-35 engineering days (was ~7-9d pre-Pass-53; +5-7d for sub-tier expansion + universe build PIT correctness)
**Critical-path:** YES
**Pyramid layers touched:** unit + integration. Layers 3-5 (property / characterization / differential) deferred to Sprint 6 retrofit per Option A — framework built in DEC-437/438/439

---

### Sprint 2 — Engine Bug Fixes Tier A (Week 1-2, parallel with Sprint 1)

**Entry criteria:**
- Sprint 1 not blocking Sprint 2 directly (parallel-friendly)
- Cache infrastructure understood

**Sub-decisions in scope (13):**
DEC-381/382/383/384/388/389/390/391/392/394/397/398/399 — all RESOLVED-DECIDED.

| Group | DEC-N | Test signal |
|---|---|---|
| Cache | DEC-381/382/383 | Front-extension fail-fast; min(20,available) flag; zero-volume preserved with is_halted col |
| Stops | DEC-384 | Intraday HIGH/LOW used; trailing stop reflects intraday extreme |
| Regime | DEC-388 | VIX 5-day SMA hysteresis (≥40 enter, <35 exit) |
| Sentiment | DEC-389/390/391 | AAII pub-lag 1-day shift; auto-refresh script + GH Actions; CNN F&G last-published with age_days |
| Universe | DEC-392/394 | Liquidity filter fail-closed with enum reasons; sector_history.csv loaded |
| Methodology | DEC-397 | Rolling 4yr/1yr train/oos windows configurable |
| Costs | DEC-398/399 | Borrow cost path investigated; consolidated to backtest.engine.costs |

**Exit criteria:** all 13 test signals pass; promote to RESOLVED-IMPLEMENTED.
**Effort:** ~9 engineering days
**Critical-path:** YES (cache/stops are foundational)
**Pyramid layers touched:** unit + integration. Layers 3-5 (property / characterization / differential) deferred to Sprint 6 retrofit per Option A — framework built in DEC-437/438/439

---

### Sprint 3 — Phase 0.B Portfolio Class (Week 2-3, sequential after Sprint 2)

**Entry criteria:**
- Sprint 2 cache fixes (DEC-381/382/383) merged
- BUG-095 scope clarified

**Sub-decisions in scope:**
| DEC-N | Description | Test signal |
|---|---|---|
| (no DEC; this implements BUG-095 fix) | Portfolio class with state (open positions, equity curve, peak equity) | All open positions tracked; equity curve continuous; peak_equity monotonic |
| DEC-070 | Portfolio-level exit logic | Drawdown trigger (>30%) flattens portfolio; market-wide breaker integration |
| DEC-076 | Factor exposure breaker | Aggregate exposure threshold halts new entries in that factor |

**Exit criteria:**
- BUG-095 closed via Portfolio class implementation
- DEC-070, DEC-076 promoted PENDING-BLOCKED → RESOLVED-IMPLEMENTED

**Effort:** ~5-7 engineering days
**Critical-path:** YES (blocks Phase 1B-α run)
**Pyramid layers touched:** unit + integration. Layers 3-5 (property / characterization / differential) deferred to Sprint 6 retrofit per Option A — framework built in DEC-437/438/439

---

### Sprint 4 — DEC-410 Audit Findings (Week 2-3, parallel with Sprint 3)

**Sub-decisions in scope (15):** DEC-442/443/444/445/446/447/448/449/450/451/453/454/455/456 + DEC-441 verification.

| Group | DEC-N | Test signal |
|---|---|---|
| yfinance demotion | DEC-442/443/444 | yfinance demoted to fallback; .info replaced; earnings live calls eliminated |
| Polygon expansion | DEC-445/446/447 | Precomputed indicators match our pandas; intraday quotes for slippage; reference PIT |
| FRED expansion | DEC-448/449 | Joint with DEC-407 — see Sprint 7. ALFRED PIT validated. |
| Quiver expansion | DEC-450/451 | All paid endpoints prefetched; gov_contracts date filter works |
| Cleanup | DEC-453/454/455 | Finnhub/OpenBB/AV deprecated and removed |
| EDGAR | DEC-456 | EDGAR vs Polygon fundamentals divergence ≤ tolerance |

**Effort:** ~5-7 engineering days
**Critical-path:** Some items (DEC-443 BUG-218 fix) yes; others parallel-friendly
**Pyramid layers touched:** unit + integration. Layers 3-5 (property / characterization / differential) deferred to Sprint 6 retrofit per Option A — framework built in DEC-437/438/439

---

### Sprint 5 — Universe Management (Week 3-4, parallel)

**Sub-decisions in scope (12):** DEC-363/364/365/372/373/374/375/376/378/379/380/457

| Group | DEC-N | Test signal |
|---|---|---|
| ETFs + Tier 3 size | DEC-363/364 | LIT/DBB/COPX in universe; Tier 3 = 100 |
| Russell 1000 | DEC-365 | Russell 1000 mid-cap add ≈ 500 names with tier liquidity |
| Tier 2 phases | DEC-372/373/374 | GH Actions monthly; --validate mode; historical backfill 2010-2024 |
| Tier 3 phases | DEC-375/376 | MAX_TICKERS=100; GH Actions automation |
| Spinoff detector | DEC-378/379/380 | NASDAQ symbol diff; SEC EDGAR Form 10-12B; Polygon corporate actions |
| Liquidity filter | DEC-457 | Tier-specific thresholds applied; rejection rate < 30% per tier |

**Effort:** ~5-8 engineering days
**Critical-path:** Tier 2 & 3 + Russell 1000 needed for full universe; can defer DEC-374 (historical backfill)
**Pyramid layers touched:** unit + integration. Layers 3-5 (property / characterization / differential) deferred to Sprint 6 retrofit per Option A — framework built in DEC-437/438/439

---

### Sprint 6 — Phase 0.E Catch-Mechanism Defense + Architecture Hygiene (Week 4-5, parallel)

**Sub-decisions in scope (9):** DEC-417/436/437/438/439 (catch mechanisms) + DEC-217/218/219/220 (X33 architecture hygiene)

**Catch-Mechanism Defense (5):**
| DEC-N | Description |
|---|---|
| DEC-417 | Test-run audit gate retroactive validation |
| DEC-436 | CI/CD gate (smoke + property + characterization) |
| DEC-437 | Property-based testing (hypothesis library) |
| DEC-438 | Characterization tests for known-good behaviors |
| DEC-439 | Differential testing (pandas vs numpy + Polygon vs SEC EDGAR) |

**Architecture Hygiene — X33 closure (Pass 52 turn 95) (4):**
| DEC-N | Description | Test signals |
|---|---|---|
| DEC-217 | Dead code audit + removal (engine.py vs engine/backtest.py duplication, vulture or similar tool) | vulture reports zero warnings post-cleanup; coverage ≥90% per DEC-098; golden master tests pass |
| DEC-218 | Documentation audit (per-doc audience + currency + consolidation; deprecated docs → /docs/archive/) | All .md files at repo root have header documenting audience + status; archive/ created; README.md updated |
| DEC-219 | GitHub Actions audit (6 workflows: prefetch_av_news/finnhub/quiver, sync_from_claude, update_stocks, validate_backtest) | Workflow inventory complete; zero hardcoded secrets per `gh secret list`; failure notification tested; idempotency verified |
| DEC-220 | sync_from_claude.yml improvements per Pass 52 turn 95 inspection: (1) add header comment documenting governance model — "trigger ONLY when owner has reviewed and approved claude-updates branch content"; (2) replace `--strategy-option=theirs` with `--no-ff` to prevent silent overwrite of owner-edits to main | Header comment added; merge strategy changed; documentation reflects governance model; resolves Pass 52 parallel-session attribution mystery |

**Effort:** ~14-19 engineering days (catch mechanisms ~7-10d + architecture hygiene ~7-9d)
**Critical-path:** Catch mechanisms required for Phase 1B-α confidence; architecture hygiene parallel-able / non-blocking
**DEC-220 priority within sprint:** HIGH — small effort (~0.5d) but resolves governance clarity + reduces future silent-overwrite risk on main branch
**Pyramid layers touched:** all 5 layers (unit + integration + property + characterization + differential). Sprint 6 BUILDS the framework for layers 3-5 (DEC-437 hypothesis, DEC-438 golden-master, DEC-439 differential) and retrofits Sprints 1-5 tests against it per Option A

---

### Sprint 6.5 — Phase 1A Rules-Only Baseline + 1A-α Cube + 1A-β Scale Validation (NEW Pass 53)

**Sub-decisions in scope:** DEC-486/487/488 PROPOSED (Phase 1A / 1A-α / 1A-β restoration); DEC-018/124/135/332/348/366/450/477 (rules-only baseline dependencies); DEC-199/200 (cube + ICT/SMC dashboards)

**Why this sprint exists Pass 53:** PROJECT_PLAN_ARCHIVE Phase 1A v3 was COMPLETE (67 instruments × 4 years × 6,942 trades, atr_trail_1x confirmed). When Pass 52 turn 119 absorbed DEC-014 Phase 1B passing criteria into DEC-422 + DEC-426, Phase 1A reference was inadvertently dropped from §3 sub-phases. Pass 53 restores Phase 1A as distinct sub-phase preceding Phase 1B agent overlay; 1A-α + 1A-β added symmetric to 1B-α to provide pre-agent owner gate.

**Phase 1A:** Rules-based + smart money baseline (no agents) on full universe; ~6-8d engineering + ~20-25h compute
**Phase 1A-α:** Rules-only cube + dashboards + verdict; owner Sharpe-≥-0.7-OOS gate; ~10-14d engineering
**Phase 1A-β:** Production-scale dry-run on 1B-α infrastructure; $0 API spend; ~3-5d engineering + ~6-8h compute

**Effort:** ~19-27 engineering days total + ~26-33h compute wall time

**Critical-path:** Phase 1A-α gate must pass before Phase 1B agent overlay work begins; Phase 1A-β must pass before Phase 1B-α $300 budget commits
**Pyramid layers touched:** all 5 layers available (post-Sprint-6 framework); specific layer mix TBD per sprint plan

---

### Sprint 7 — Statistical Methodology (Week 5-6, parallel)

**Sub-decisions in scope (16):** DEC-400/401/402/403/404/405/406/407/408/409/412/413/414/415/416/423 (+ DEC-411 blocked on DEC-298)

Implementation per Theme X4 Block 3 sequencing in AUDIT_INDEX.md.

**Effort:** ~17-19 engineering days
**Pyramid layers touched:** all 5 layers available (post-Sprint-6 framework); specific layer mix TBD per sprint plan

---

### Sprint 8 — Strategy Categories (Week 6-7, parallel — NOT critical path)

**Sub-decisions in scope (5):** DEC-367/368/369/370/371

**Effort:** ~14-18 engineering days
**Pyramid layers touched:** all 5 layers available (post-Sprint-6 framework); specific layer mix TBD per sprint plan

---

### Sprint 9 — Phase 1B-α Run (Week 5-6 earliest)

**Entry criteria:**
- Sprints 1-6 RESOLVED-IMPLEMENTED
- Universe stable; cube populating per DEC-422

**Sub-decisions in scope:** DEC-422 (cube driver), DEC-426 (passing criteria), DEC-486/487/488 PROPOSED (post-Phase-1A gates already passed via Sprint 6.5)

**Output:** Phase 1B-α backtest results across 60 strategies × dimensional cube cells

**Test signals:** Cube row count = expected (60 strategies × dimensional cells); each cell has trade_log + metrics + verdict; A/B differential analysis non-empty for cells with both arms

**Exit criteria:** Cube populated; per-strategy × per-cell verdicts produced; owner gate review completed; status flips to RESOLVED-IMPLEMENTED on owner approval

**Effort:** ~3-5 engineering days + ~$300 API spend + ~24-48h compute wall time
**Critical-path:** YES (Phase 1B-α gate determines Phase 1B full-scale go/no-go)
**Pyramid layers touched:** all 5 layers available (post-Sprint-6); execution sprint — primary use is integration + characterization (golden master vs Sprint 6.5 Phase 1A baseline) + property (per-cell verdict invariants); unit minimal (existing tested code paths); differential not in immediate scope

---

## Critical Path Gate

**Phase 1B-α cannot run until:**
- Sprint 1 RESOLVED-IMPLEMENTED (Phase 0.A foundation)
- Sprint 2 RESOLVED-IMPLEMENTED (engine bug fixes Tier A)
- Sprint 3 RESOLVED-IMPLEMENTED (Phase 0.B Portfolio class)
- Sprint 4 partial — at minimum DEC-443 (yfinance .info replacement; resolves BUG-218 CRITICAL)
- Sprint 6 RESOLVED-IMPLEMENTED (Phase 0.E catch mechanisms)

**Estimate: ~21-25 engineering days minimum critical path; ~30-40 days realistic with parallelism.**

---

## Verification gate process (per sprint)

1. Engineer (owner) implements sub-decision per spec text
2. Test signals from sub-decision text pass in CI
3. Owner reviews demo at sprint end
4. Owner approves batch status flip RESOLVED-DECIDED → RESOLVED-IMPLEMENTED for the completed sub-decisions
5. ENGINEERING_REGISTER updated; AUDIT_INDEX status flipped; commit + push

---

*Per CHECKLIST #43/#46/#47/#56/#57. Pass 52 turn 42.*

---

## Phase 2 Batch 1 Additions (Pass 52 turn 101)

Per CHECKLIST #58 — sprint-tracker assignment for RESOLVED-DECIDED decisions previously homeless. Adding 15 engineering decisions to existing sprints + sub-decisions table.

### Sprint 1 / Sprint 2 additions (Phase 0.A foundation / engine bug fixes Tier A)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-040 | PointInTimeLoader structural framework | freezegun-based `loader.fetch(as_of=D)` returns rows with date ≤ D; rejects rows with date > D | ~2-3d (Sprint 1 foundation; consumed by all PIT-aware fetchers) |

### Sprint 4 additions (DEC-410 Audit Findings Sprint)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-072 | Separate WSB from smart money — refactor signal taxonomy | smart_money_composite no longer includes WSB; new social_sentiment_score field | ~1.5d |
| DEC-092 | Slippage model = f(size%ADV, vol) — base model with DEC-122/280 multipliers | trade at 0.5% ADV vol=20% → ~3bps; 5% ADV vol=50% → ~25bps; layered final = base × exit × time-of-day | ~3d post-DEC-446 calibration |

### Sprint 5 additions (Position Sizing — NEW SPRINT block within Universe Management)

Per Pass 52 X5 closure (DEC-086/087/088 + DEC-091 BLOCKED_ON_BUG-095). Position sizing methodology decisions:

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-086 | Fractional Kelly position sizing (PHASED ROLLOUT — Phase A parallel computation) | Synthetic strategy edge=10%, win_rate=55%, avg_win=2× avg_loss → Kelly=0.275; fractional=0.10; both sizes computed | ~2d Phase A |
| DEC-087 | Vol-targeted sizing per-position | High-vol ticker (XOM during oil shock) gets smaller position than low-vol (KO consumer staple) at same edge level | ~1d (joint with DEC-023 SUPERSEDED) |
| DEC-088 | Portfolio vol target 15% annualized | Synthetic backtest produces realized portfolio vol; if 15% systematically missed → REVISIT_AFTER_BACKTEST trigger | ~0.5d |

### Sprint 6 additions (Phase 0.E + Architecture Hygiene)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-067 | Add 9 missing exit methods (chandelier, psar, supertrend, etc.) | All 9 exits compliant with DEC-353 R:R≥2.0; chandelier ATR mult ≥ 2.5; supertrend signals match TradingView reference | ~5-7d |
| DEC-075 | Adverse-excursion-from-peak (AEP) breaker — derived from MFE | Per-strategy `mean_aep_pct` computed; high-AEP trades flagged in retrospective analysis | ~1d (derived-metric, low-risk) |
| DEC-096 | Backtest reproducibility manifest (code SHA + data version + config hash) | Joint with DEC-283 (output schema versioning) + DEC-330 (cache schema versioning); single coordinated reproducibility manifest written per backtest run | ~2d (joint with DEC-330 already RESOLVED) |

### Sprint 7 additions (Statistical Methodology)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-081 | Sharpe + Sortino + transaction cost sensitivity | Both `sharpe_per_trade` and `sharpe_daily = sqrt(252) × mean(daily_returns) / std`; Sortino with same daily mark-to-market; cost sensitivity at 0/5/10/20bps round-trip | ~3d |
| DEC-082 | Stress-test pass requirements (Option A; 2022 Rate-Rise Bear) | Min Sharpe ≥ 0, Max DD ≤ 20%, Min Win Rate threshold per category | ~2d |
| DEC-083 | Min trades floor (TIERED — daily/earnings/calendar=300, regime-gated/crisis-only=100) | Strategies under floor get INSUFFICIENT_OOS_DATA verdict per DEC-426 5-gate validity | ~1d |
| DEC-085 | Define macro correlation precisely (REVISED COMPREHENSIVE — 9 FRED series) | All 9 series (VIX, DGS10, T10Y2Y, FEDFUNDS, UNRATE, CPIAUCSL, T10YIE, BAA10Y, DXY) Pearson + Spearman correlations computed per strategy | ~2d |
| DEC-106 | Regime inputs 2 → 8+ (yield curve, HY spread, ICSA jobless, breadth, sector dispersion, AAII/CNN F&G) | Regime classifier consumes 8+ inputs; transition triggers depend on multiple inputs not just VIX | ~2d post-deps |

### Phase 2 Batch 1 ENG totals

- Sprint 1: +1 decision (DEC-040)
- Sprint 4: +2 decisions (DEC-072, DEC-092)
- Sprint 5: +3 decisions (DEC-086, DEC-087, DEC-088) — NEW dedicated position-sizing block
- Sprint 6: +3 decisions (DEC-067, DEC-075, DEC-096)
- Sprint 7: +5 decisions (DEC-081, DEC-082, DEC-083, DEC-085, DEC-106)
- Total: **+14 ENG decisions assigned to sprints**

(Note: DEC-067 originally proposed Sprint 8 but reassigned Sprint 6 since it's an exit-method engineering task adjacent to architecture hygiene; can move to Sprint 8 if owner prefers strategy-roster grouping.)

(DEC-072 sprint: Sprint 4 selected per owner approval; signal-taxonomy refactor is data-layer work fitting DEC-410 audit findings sprint.)

Sprint 1 effort revised: +2-3d for DEC-040 → ~9-12d total
Sprint 4 effort revised: +4-5d for DEC-072/092 → ~9-12d total (was 5-7d)
Sprint 5 NEW block: ~3.5d (DEC-086/087/088 position sizing parallel implementation)
Sprint 6 effort revised: +8-10d for DEC-067/075/096 → ~22-29d total (was 14-19d)
Sprint 7 effort revised: +10d for DEC-081-085 + DEC-106 → ~27-29d total (was 17-19d)

Total project Stage 2 effort revised: previously ~30-40d realistic → ~50-65d realistic with full register population.

---

## Phase 2 Batch 2 Additions (Pass 52 turn 103)

Per CHECKLIST #58 — sprint-tracker assignment for 9 ENG decisions previously homeless.

### Sprint 6 additions

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-113 (Stage 2 portion) | Research log (every Phase 1B-α run + strategy hypothesis tested) + failure log (system errors + resolution); Stage 3+ trade journal portion in DOCUMENTATION_REGISTER Bucket D | Research log written per backtest run; failure log captures all system errors with resolution | ~0.5d (Stage 2 portion only) |
| DEC-189 | Trade rationale 10-point depth standard (trigger/strategy/setup/smart-money/macro/agent/risk/expectancy/exit-plan/conviction) — schema layer consumed by DEC-213 (both-rationales storage) and DEC-278 (full execution context) | Every trade ledger row has 10-field rationale dict per schema; schema-foundational for trade journal stack | ~1d |

### Sprint 7 additions

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-107 | Regime probability instead of hard label (PHASED ROLLOUT — Phase A backwards-compatible) | Regime classifier emits both `regime_label` and `regime_proba` fields; strategies opt-in to probability-based gating | ~1d Phase A |
| DEC-108 | Regime persistence model (EXPONENTIAL SMOOTHING not HMM): `EMA_regime = 0.9 × prev + 0.1 × new` | Regime transitions don't flicker on single-day VIX spikes; transition takes ≥3 days of confirming signal | ~1d |
| DEC-109 | Rolling 5yr/1yr walk-forward (Option B): Train 2018-2022 → OOS 2023; Train 2019-2023 → OOS 2024 = 2 OOS rolling windows | Joint with DEC-298 PIT cache rebuild (BLOCKED); supersedes DEC-326 4yr/1yr; canonical methodology used by DEC-026/264 supersessions | ~2d post-DEC-298 |
| DEC-110 | Deflated Sharpe (Bailey PSR): PSR formula in metrics.py with SR* ≈ √(2·ln(72)) ≈ 2.92; threshold PSR ≥ 0.95 | Joint with DEC-080 Bonferroni + DEC-413 (5-gate validity per DEC-426) | ~1.5d |
| DEC-111 | Stationarity / structural break tests: (1) ADF on equity curve; (2) Rolling 1-year Sharpe deviation >2σ flag; (3) Chow split-sample (n_trades ≥ 600 only; else INSUFFICIENT_SAMPLE) | `stats.py` produces all 3 test outputs per strategy; Chow respects sample-size gate | ~2d |
| DEC-144 | Stock-vs-sector momentum delta as breakdown variable (cube dimension momentum_delta_band) | Joint with DEC-100/422 — observation-only, not strategy filter | ~1d |
| DEC-152 | Hold-out final test period (never touched during audits) | Train/test split discipline; final 6-12 months reserved as untouched holdout; revealed only at Stage 2→Stage 3 transition | ~1d |

### Sprint 7-8 additions (Phase 1B-α Dimensional Cube + Strategy Categories)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-199 | Dashboard 1 detailed spec (5 sections: Cube Explorer / Per-strategy verdict cards / Regime breakdown / A/B comparison / Live decision lookup) | Joint with DEC-430 Streamlit implementation; owner can navigate to any strategy → see verdict + 5-gate detail + regime breakdown + A/B comparison + drill-down to trades | absorbed in DEC-430 ~3-5d |

### Phase 2 Batch 2 ENG totals

- Sprint 6: +2 decisions (DEC-113 Stage 2 portion, DEC-189)
- Sprint 7: +7 decisions (DEC-107, DEC-108, DEC-109, DEC-110, DEC-111, DEC-144, DEC-152)
- Sprint 7-8: +1 decision (DEC-199 absorbed in DEC-430)
- Total: **+10 ENG decisions assigned to sprints**

Wait — DEC-189 was discussed for Sprint 6 in Batch 2 walkthrough but DEC-199 is a Sprint 7-8 addition. Net 10 entries (DEC-113 Stage 2 portion counts as 1 entry).

Sprint 6 effort revised: +1.5d (DEC-113 + DEC-189) → ~23.5-30.5d total (was 22-29d)
Sprint 7 effort revised: +9.5d (DEC-107/108/109/110/111/144/152) → ~36.5-38.5d total (was 27-29d)
Sprint 7-8 dashboard work absorbed in existing DEC-430 estimate

Total project Stage 2 effort revised: previously ~50-65d → now ~60-75d realistic with full register population.

---

## Phase 2 Batch 3 Additions (Pass 52 turn 105)

Per CHECKLIST #58 — sprint-tracker assignment for 27 ENG decisions previously homeless. **Largest batch yet** — multiple clusters captured.

### Sprint 1 additions (Phase 0.A foundation)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-225 | Cache eviction policy: tag entries cache_class=prefetched/computed/derived; never evict prefetched (expensive refetch); evict computed/derived only on disk pressure | Synthetic disk-pressure scenario evicts computed first; prefetched preserved; eviction logged | ~1d (joint DEC-227) |
| DEC-227 | Cache size monitoring: cache_size_gb metric via du -sh; 80% disk threshold triggers DEC-225 eviction + log warning; Stage 4+ alerting via DEC-095 | Cache size metric correct; 80% threshold triggers eviction + warning | ~0.5d (Stage 2 portion only) |
| DEC-235 | NYSE/NASDAQ calendar handling via pandas_market_calendars (industry-standard library replacing hand-rolled date logic) | Black Friday correctly half-day; DST transitions don't shift bar timestamps; Sept 11 2001 closure handled | ~1d |

### Sprint 4 additions (DEC-410 Audit Findings + cost stack)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-228 | Fetcher reliability audit: per-API standard retry exp backoff (1s/2s/4s/8s/16s) max 5; rate-limit token bucket; idempotency hash | Synthetic 503 → exp backoff retry; 429 → wait until reset; same-range refetch identical hash | ~3-4d |
| DEC-234 | Ticker lifecycle event handler (CUSIP/ISIN tracking across renames/mergers); joint DEC-380 Polygon corporate-actions | Synthetic FB→META rename preserves price continuity; backtest treats single ticker history | ~2-3d post-DEC-380 |
| DEC-252 | IBKR commission model TIERED default: $0.0035/share min $0.35 max 1% trade value + exchange fees; joint DEC-054/092 | Synthetic 100-share trade @ $50 → ~$0.40 IBKR Tiered commission; backtest applies per-trade vs static $1 baseline | ~2-3d (HARD-REVERSIBILITY sandbox-prototype) |

### Sprint 6 additions (Phase 0.E + Architecture Hygiene + new)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-205 | A/B test 4-arm design (rules / full-agents / no-Risk / no-Bull-Bear) — A/B framework foundation | 4-arm config defined; orchestrator (DEC-216) supports arm enumeration | ~1d |
| DEC-206 | Paired A/B design (every trade evaluated by every arm in parallel) | Single trade decision produces 4 verdicts (one per arm); paired comparison enabled | ~1d (joint DEC-205) |
| DEC-222 | Test naming + regression tests for top-20 CRITICAL bugs (BUG-095 Portfolio missing, BUG-218 yfinance .info, BUG-232 trailing stop lookahead, etc.); joint DEC-438 | Each top-20 CRITICAL bug has regression test that would have caught the bug | ~3-4d |
| DEC-229 | Config pydantic upgrade (HARD-REVERSIBILITY sandbox-prototype on 1-2 classes); joint DEC-096/216 | Typed config raises ValidationError on bad input; env override works; config change log | ~3-5d |
| DEC-230 | Logging JSON standard (python-json-logger library, daily rotation, standardized levels DEBUG/INFO/WARNING/ERROR/CRITICAL) | Every log entry parses as valid JSON with required fields; daily rotation at midnight UTC | ~2d |
| DEC-231 | Bare-except audit (WARNING+ logging with context); joint DEC-230/437 | grep -r "except Exception" returns count; each occurrence audited; pre-commit lint warning for new bare except | ~2d |
| DEC-232 | Determinism test (byte-identical regression on 2 identical runs); joint DEC-096/216/417 | 2 identical runs produce byte-identical trade ledgers; CI gate fails on diff | ~1d |
| DEC-233 | Daily data quality monitoring (per-ticker NaN/missing/anomaly detection); joint DEC-260 | Synthetic NaN day → DataQualityWarning; price gap > 50% → anomaly flag | ~1d |
| DEC-241 | Time-in-market metric (% in any position, % long, % short, % cash) — pure additive trade-ledger metric | 100 trades over 252 days, average hold 5d → time_in_market ≈ 2% if non-overlapping | ~0.5d |

### Sprint 7 additions (Statistical Methodology + A/B operational + 3rd cluster)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-207 | Pre-commit minimum sample size 300 paired trades per arm before declaring winner | A/B with n<300 paired returns INSUFFICIENT_SAMPLE_FOR_ARM_COMPARISON | ~0.5d |
| DEC-208 | Multi-metric A/B comparison (Sharpe + Sortino + DD + win_rate + PF + CVaR + cost) | All 7 metrics computed per arm; composite verdict matrix | ~1.5d |
| DEC-209 | Per-regime A/B verdicts (agents pass/fail separately per regime per DEC-422 cube) | Per-regime arm comparison shows different verdicts per regime; documented in cube | ~1d (joint DEC-422 cube) |
| DEC-210 | Net Sharpe contribution accounting (gross lift minus annualized agent cost); joint DEC-131/420 | Synthetic agent run with $1000/mo LLM cost on $100K portfolio → 1.0 Sharpe drag; agent must clear 1.2 gross to meet DEC-131 0.2 net | ~0.5d |
| DEC-212 | Agent-disagreement decomposition (Bull vs Bear, Risk override events) | Synthetic Bull=BUY Bear=HOLD Risk=APPROVE → tagged AGENT_DISAGREEMENT_BULL_BEAR; aggregated per regime/strategy | ~1d |
| DEC-215 | A/B test result registry (versioned JSON/parquet artifacts in repo with timestamp/dataset hash/agent versions); joint DEC-096 | Each A/B run produces ab_results/YYYY-MM-DD_HHMM_runhash.json; queryable across history | ~1d |
| DEC-216 | A/B orchestrator code module backtest/ab_orchestrator.py (HARD-REVERSIBILITY sandbox-prototype on 2-arm before N-arm); joint DEC-211/096 | Same A/B config + seed = bit-identical results; parallel doesn't introduce non-determinism; 4-arm and 7-arm work | ~3-4d |
| DEC-242 | Distribution analysis (skewness, kurtosis, max single-trade contribution); joint DEC-413 PSR | Skewed PnL series produces correct skewness/kurtosis; max_single_trade_contribution = max(trade_pnl) / total_pnl | ~0.5d |

### Sprint 7-8 additions (Phase 1B-α Dashboard + Strategy Categories)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-200 | Dashboard 2 spec (Phase 0.D ICT/SMC signal audit) — 5 sections (signal viz, frequency stats, synthetic tests, PIT validation, library version manifest) | Dashboard launches; all 5 sections populate; synthetic FVG case displays expected pattern | ~3-4d (Streamlit; plotly candlestick + overlay) |
| DEC-201 | Dashboard 3 spec (Stage 2 agent overlay analysis) — 6 sections (A/B summary, disagreement events, per-agent ablation post-DEC-211, both-rationales, cost accounting, quarterly re-validation) | Dashboard launches from DEC-215 versioned artifacts; cost-trend graph reflects DEC-210 calculations | ~4-5d (multi-section Streamlit) |

### Sprint 9 additions (Phase 1B-α run + ongoing)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-211 | Per-agent ablation studies (Option A NARROW SCOPE) — 7-arm runs ONLY post-Phase 1B-α 4-arm completion; sample-bounded top-20% strategies × ~5K trades | 7-arm ablation produces per-agent marginal Sharpe contributions on top-20% strategies sample; cost stays within ~$120 one-time + ~$30-60/month | ~2d post-Phase-1B-α |
| DEC-214 | Quarterly re-validation A/B test (model drift / cost drift); joint DEC-290 quarterly cadence | Quarterly cron re-runs A/B over rolling 90 days; net Sharpe < 0.2 → ALERT_AGENT_DECAY | ~0.5d (script + cron + alerting) |

### Phase 2 Batch 3 ENG totals

- Sprint 1: +3 decisions (DEC-225/227/235)
- Sprint 4: +3 decisions (DEC-228/234/252)
- Sprint 6: +9 decisions (DEC-205/206/222/229/230/231/232/233/241)
- Sprint 7: +8 decisions (DEC-207/208/209/210/212/215/216/242)
- Sprint 7-8: +2 decisions (DEC-200/201)
- Sprint 9: +2 decisions (DEC-211/214)
- Total: **+27 ENG decisions assigned to sprints**

Sprint 1 effort revised: +2.5d → ~11.5-14.5d total (was 9-12d)
Sprint 4 effort revised: +7-10d → ~16-22d total (was 9-12d)
Sprint 6 effort revised: +14-16.5d → ~37.5-47d total (was 23.5-30.5d)
Sprint 7 effort revised: +9d → ~45.5-47.5d total (was 36.5-38.5d)
Sprint 7-8 dashboard work: +7-9d for DEC-200/201 (was DEC-199 only absorbed in DEC-430)
Sprint 9 NEW additions: ~2.5d (DEC-211 + DEC-214 ongoing operational)

Total project Stage 2 effort revised: previously ~60-75d → now ~95-115d realistic with full register population.

---

## Phase 2 Final Sweep Additions (Pass 52 turn 107) — 84 decisions

Per CHECKLIST #58 — sprint-tracker assignment for ALL remaining homeless ENG decisions. **Final Phase 2 sweep complete.**

### Sprint 1 additions (Phase 0.A foundation) — 11 decisions

DEC-300 (yfinance earnings_dates tiered approach), DEC-304 (CPI/NFP/FOMC auto-extend from FRED+BLS), DEC-307 (cache get_ohlcv front-extension), DEC-308 (cache get_ohlcv_bulk min-floor flexibility), DEC-309 (cache ticker collision BRK-B/BRK.B), DEC-310 (cache zero-volume days preserved), DEC-318 (AAII pub-lag N+1 trading day shift), DEC-319 (AAII auto-refresh script in /scripts), DEC-320 (CNN F&G no interpolation), DEC-328 (cache filelock fail-fast), DEC-329 (multi-process safe globals)

Sprint 1 effort revised: +6-9d → ~17.5-23.5d total

### Sprint 2 additions (Engine Bug Fixes Tier A) — 14 decisions

DEC-293 (close_trade days NameError), DEC-294 (duplicate ClosedTrade dataclass), DEC-295 (SHORT_BORROW_COST_PER_DAY units reconciliation), DEC-296 (test_e2e fixture undefined), DEC-297 (close_trade unit test), DEC-305 (PIT guard RAISE not WARNING), DEC-306 (get_news_sentiment path mismatch), DEC-311 (trailing-stop ATR daily refresh), DEC-312 (exit_hybrid_50pct max_days inconsistency), DEC-314 (Circuit breakers Level 3+4 implementation), DEC-315 (Circuit breakers checked sequentially), DEC-327 (short-borrow cost duplication single source), DEC-338 (Conversion logic actual position open Option A), DEC-340 (get_correlation_matrix variable history)

Sprint 2 effort revised: +14-18d → ~23-27d total (was 9d baseline)

### Sprint 3 additions (Phase 0.B Portfolio Class) — 2 decisions

DEC-277 (Per-strategy promotion workflow HARD-REVERSIBILITY ~2-3d), DEC-339 (pnl_dollar dynamic notional via Portfolio class ~1d)

Sprint 3 effort revised: +3-4d → ~8-11d total (was 5-7d)

### Sprint 4 additions (DEC-410 Audit Findings) — 14 decisions

DEC-253 (TSX/US routing rule), DEC-254 (Canadian ETF substitution), DEC-280 (time-of-day slippage layered with DEC-092), DEC-299 (yfinance .info sector snapshot+revisit), DEC-302 (VXX/UUP proxy tracking error quantification), DEC-316 (regime classifier missing-VIX abstain), DEC-317 (VIX SMA hysteresis joint DEC-388), DEC-322 (market_cap_pit joint DEC-393), DEC-323 (sector_history.csv joint DEC-394), DEC-324 (Congressional disclosure_date weighting), DEC-325 (13F filing_date PIT), DEC-332 (smart money composite weights → config), DEC-333 (sentiment thresholds match CNN bands), DEC-344 (slippage threshold ATR/price > 3% REVISIT_AFTER_BACKTEST)

Sprint 4 effort revised: +14-19d → ~30-41d total (was 16-22d) — LARGEST SPRINT

### Sprint 5 additions (Universe Management) — 2 decisions

DEC-303 (S&P 500 historical_membership.csv ~2d), DEC-331 (ETF list fragmentation reconciliation ~1d)

Sprint 5 effort revised: +3d → ~6.5d total (was 3.5d)

### Sprint 6 additions (Phase 0.E + Architecture Hygiene) — 1 decision

DEC-341 (universe.py docstring fix; per Pass 52 X33 architecture hygiene)

Sprint 6 effort revised: +0.25d → ~37.75-47.25d total

### Sprint 7 additions (Statistical Methodology + A/B operational + cluster) — 20 decisions

DEC-262 (conditional candidate cap 10/15/20), DEC-263 (burst-day stress test), DEC-279 (P&L decomposition HARD-REVERSIBILITY ~3-4d), DEC-284 (borderline strategy STRICT-LESS-THAN policy), DEC-334 (composite_score actual ROI not win_rate), DEC-335 (composite_score weights configurable), DEC-348 (event-calendar suppression joint DEC-256/407+448), DEC-349 (asymmetric event window pre=1 post=3), DEC-401 (DEC-080 Phase B Holm-Bonferroni), DEC-402 (DEC-081 Phase A Sharpe canonicalization), DEC-403 (DEC-081 Phase B Sortino), DEC-404 (DEC-081 Phase C transaction cost sensitivity), DEC-405 (DEC-082 stress test runner Option A), DEC-406 (DEC-083 tiered min-trades enforcement), DEC-408 (DEC-085 Phase B macro correlation tags), DEC-409 (DEC-085 Phase C event-window tags), DEC-412 (DEC-109 Phase B walk-forward implementation), DEC-414 (DEC-111 Phase A ADF), DEC-415 (DEC-111 Phase B rolling Sharpe), DEC-416 (DEC-111 Phase C Chow)

Sprint 7 effort revised: +18-22d → ~63.5-69.5d total (was 45.5-47.5d) — MASSIVE — statistical methodology + A/B + cluster work all converge

### Sprint 7-8 additions (Phase 1B-α Dimensional Cube) — 5 decisions

DEC-425 (Phase 1 dim_cube infrastructure HARD-REVERSIBILITY ~5-7d), DEC-427 (Phase 3 marginal heatmap ~2-3d), DEC-428 (Phase 4 3D combined ~3-4d), DEC-429 (Phase 5 live decision lookup ~2d), DEC-431 (Phase 7 validation test suite joint DEC-417 ~2-3d)

Sprint 7-8 effort revised: +14-19d → ~24-33d total (was 10-14d)

### Sprint 8 additions (Strategy Categories + Chart Patterns + Multi-TF) — 15 decisions

DEC-345 (ICT/SMC timeframe scope), DEC-350 (Multi-TF non-ICT strategies extension), DEC-352 (13F price-level mapping), DEC-354 (Chart patterns parent reopened), DEC-355 (Trendline break + retest), DEC-356 (Channel breakout + retest), DEC-357 (Range breakout + retest), DEC-358 (Wedge/triangle/pennant), DEC-359 (H&S / inverse H&S), DEC-360 (Double top / double bottom), DEC-361 (Cup & handle), DEC-362 (Flag / pennant continuation), DEC-432 (DEC-067 Phase A 3 new indicators chandelier/psar/supertrend), DEC-433 (DEC-067 Phase B 6 new exit methods), DEC-435 (DEC-075 AEP implementation)

Sprint 8 effort revised: NEW dedicated block ~30-45d (chart patterns are 8+ strategies × 2-4d each)

### Phase 2 Final Sweep ENG totals

| Sprint | Final Sweep additions |
|---|---|
| Sprint 1 | +11 decisions |
| Sprint 2 | +14 decisions |
| Sprint 3 | +2 decisions |
| Sprint 4 | +14 decisions |
| Sprint 5 | +2 decisions |
| Sprint 6 | +1 decision |
| Sprint 7 | +20 decisions |
| Sprint 7-8 | +5 decisions |
| Sprint 8 | +15 decisions |
| **Total** | **+84 ENG decisions assigned** |

## TOTAL PROJECT EFFORT POST-PHASE-2-FINAL-SWEEP

| Sprint | Effort |
|---|---|
| Sprint 1 (Phase 0.A foundation) | ~17.5-23.5d |
| Sprint 2 (Engine Bug Fixes Tier A) | ~23-27d |
| Sprint 3 (Phase 0.B Portfolio Class) | ~8-11d |
| Sprint 4 (DEC-410 Audit Findings) | ~30-41d |
| Sprint 5 (Universe Management) | ~6.5d |
| Sprint 5 NEW (Position Sizing) | ~3.5d |
| Sprint 6 (Phase 0.E + Hygiene) | ~37.75-47.25d |
| Sprint 7 (Statistical Methodology + A/B) | ~63.5-69.5d |
| Sprint 7-8 (Phase 1B-α Dimensional Cube) | ~24-33d |
| Sprint 8 (Strategy Categories) | ~30-45d |
| Sprint 9 (Phase 1B-α run + ongoing) | ~2.5d |
| **Total Stage 2 realistic** | **~247-313 engineering days** |

CRITICAL PATH revised: ~46-56d → likely **~100-130 days minimum** post-Phase-2-Final-Sweep with full register population (Sprint 4 + Sprint 7 are now both critical-path heavy).

This is a **major reality-check**: previous estimates of ~30-40 days realistic were significantly understating scope. True engineering work for Stage 2 is closer to ~250-300 engineering days.

---

## Phase 2 Cleanup Batch (Pass 52 turn 109) — 22 substantively-homeless decisions added

Per CHECKLIST #58 — these decisions were technically in IMPLEMENTATION_READINESS_DASHBOARD text but lacked proper ENGINEERING_REGISTER sprint slots with test signals + effort estimates. **Substantive homelessness fix.**

### Sprint 1 additions (Phase 0.A foundation) — 5 decisions

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-259 | ICT/SMC signal pre-computation cache (FVG/BOS/CHoCH/order blocks) — joint DEC-045 (smartmoneyconcepts library) + DEC-261 (PIT lag rule); storage `backtest/data/cache/ictsmc/{TICKER}.parquet` | Per-ticker parquet populates with fvg_count/fvg_active_levels/bos_event/choch_event/order_block_levels/liquidity_grab_event; PIT-safe (no future bars referenced) | ~2-3d post-DEC-045 fork verification |
| DEC-382 | DEC-308 implementation — `min(20, available_days)` cache floor + LIMITED_HISTORY result-schema flag; strategy-level (not cache) decides if data sufficient | Synthetic 15-day-history ticker returns LIMITED_HISTORY flag + 15 days of data; strategy can opt-out via flag | ~0.5d |
| DEC-383 | DEC-310 implementation — remove `df = df[df["volume"] > 0]` from cache.py write; add derived `is_halted = (volume == 0) & (close == previous_close)` | Halted day preserved in cache with is_halted=True; existing cache forward-only migration; strategy-level filter respects flag | ~1d |
| DEC-390 | DEC-319 implementation — `scripts/refresh_aaii_sentiment.py` HTML scrape + `.github/workflows/refresh_aaii.yml` Friday 14:00 UTC schedule + auto-PR weekly delta | AAII CSV refreshes weekly; validation gate (DEC-065) checks freshness; PR review precedes merge | ~1d |
| DEC-391 | DEC-320 implementation — `(value, last_published_date, age_days)` tuple replaces interpolation; strategies filter `age_days ≤ 3`; new `scripts/refresh_cnn_fear_greed.py` | CNN F&G returns (value, last_published, age) tuple; historical CSV migrated with is_interpolated=True flag; refresh script populates daily | ~1d |

Sprint 1 effort revised: +5.5d → ~23-29d total

### Sprint 2 additions (Engine Bug Fixes Tier A) — 3 decisions

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-313 | update_trailing_stop intraday HIGH/LOW (PIT-honest stop trigger) — change signature to (trade, today_high, today_low, today_close, vix); use intraday extreme for highest_high/lowest_low; joint DEC-337 + BUG-232 | Synthetic intraday spike to stop level → exit at stop level same day (not close); CAV-038 acknowledged (yfinance high/low outliers) | ~1-2d |
| DEC-321 | Liquidity filter fail-closed — missing/zero market_cap REJECTS ticker (returns False); LIQUIDITY_FILTER_FAIL_REASONS enum; joint BUG-238 + DEC-366 | Synthetic ticker with missing market_cap REJECTED with reason=missing_market_cap; CAV-043 monitoring on rejection rate | ~1d |
| DEC-399 | DEC-327 Phase B — consolidate to shared `backtest.engine.costs.calculate_borrow_cost(trade, hold_days)`; both paths consume single source | Borrow cost charged exactly once per short trade in unit test; historical short-trade backtests rerun + document net PnL delta | ~0.5d |

Sprint 2 effort revised: +2.5-3.5d → ~25.5-30.5d total

### Sprint 4 additions (DEC-410 Audit Findings + cost stack) — 7 decisions

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-301 | FRED data revisions: switch to ALFRED (archival FRED) for vintage data — replaces non-vintage FRED that retroactively revises past values | get_fred_pit(series_id, as_of_date) returns vintage-as-of-date value; differs from current revised value for series with revisions | ~2-3d |
| DEC-444 | Deprecate `days_to_next_earnings()` via yfinance live calls — route all lookups through DEC-256 Polygon earnings cache parquet; remove yfinance.earnings_dates live-call path | Zero yfinance live calls during backtest; resolves BUG-280 (silent None) + BUG-013 (~106K live calls); absorbed into DEC-256 implementation | absorbed in DEC-256 (no separate effort) |
| DEC-447 | Polygon reference tickers PIT consumption — query pattern for `/v3/reference/tickers/{ticker}` with as-of-date semantics for sector + market_cap historical lookup; replaces yfinance .info live calls | PIT-correct sector + market_cap returnable for any (ticker, as_of_date) pair; joint DEC-443 (yfinance .info replacement) + DEC-322 (market_cap_pit) | absorbed in DEC-443 (no separate effort) |
| DEC-449 | Validate DEC-301 ALFRED PIT mitigation produces materially different values — sample test on CPIAUCSL + FEDFUNDS across 2018-2024; if no difference, flag DEC-301 as over-engineered | Non-trivial difference exists between revised and vintage values for at least one series at multiple dates; documented in API_AUDIT.md | ~0.5d |
| DEC-451 | Fix BUG-284 gov_contracts date filter — Quiver `/historical/govcontracts/` returns Date field but cache schema saved only Qtr+Year; re-prefetch with explicit Date preservation OR reconstruct synthetic date from Qtr+Year midpoint with caveat | gov_contracts date filter returns non-empty results for known recent contracts; filter does not silently drop matching rows; resolves BUG-284 MEDIUM OPEN | ~0.5d |
| DEC-454 | Remove OpenBB from project scope — update PROJECT_PLAN section 10 to remove OpenBB row; Polygon DEC-441 + Quiver + FRED collectively cover all OpenBB Stage 0+Stage 2 use cases | PROJECT_PLAN section 10 updated; OpenBB references removed; future Phase 1C+ screener use cases revisitable | ~0.25d documentation |
| DEC-455 | Alpha Vantage deprecation timeline — sequenced cleanup: (a) preserve existing AV cache parquet artifacts; (b) remove AV from active prefetch post-Polygon news prefetch validation; (c) mark ALPHAVANTAGE_API_KEY optional; (d) strip AV references from pipeline.py + smart_money.py post-Polygon stable run | AV code paths inactive; existing cache artifacts preserved; ALPHAVANTAGE_API_KEY no longer required; joint DEC-440 (already approved AV→Polygon supersession) | ~0.5d cleanup spread across migration phases |

Sprint 4 effort revised: +3.75-5.25d (excluding absorbed DEC-444/447) → ~33.75-46.25d total

### Sprint 5 additions (Universe Management) — 4 decisions

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-366 | Liquidity floor for universe inclusion (TIER-SPECIFIC FRAMEWORK) — Tier 1 (S&P 500): min_cap=$0, min_avg_dollar_volume=$10M, min_history=250d; Tier 2 (spinoffs/IPOs): min_cap=$2B, min_avg_dollar_volume=$5M, min_history=20d w/ LIMITED_HISTORY flag; Tier 3 (momentum top-100): min_cap=$300M, min_avg_dollar_volume=$5M, min_history=60d; Russell 1000 add: min_cap=$300M, min_avg_dollar_volume=$3M, min_history=250d | Each tier ticker passes/fails per tier-specific thresholds; joint DEC-321 (fail-closed enforcement); LIMITED_HISTORY flag respected by strategies | ~1-2d |
| DEC-373 | DEC-103 Phase B — `--validate` mode flagging missing-data tickers (yfinance returning empty info) for manual review rather than silent drop | Synthetic SNDK-style edge case (yfinance lag for new listing) flagged for manual review with reason; not silently dropped | ~1d |
| DEC-376 | DEC-104 Phase B — GitHub Actions monthly automation `.github/workflows/refresh_momentum_watchlist.yml` calling `build_momentum_watchlist.py --write` + commit via PR | Workflow runs monthly; produces PR with watchlist diff for owner review/merge; commit lineage preserved | ~1d |
| DEC-379 | DEC-105 Phase 2 — SEC EDGAR Form 10-12B feed scraping for 30-90d spinoff lead time; RSS at sec.gov/cgi-bin/browse-edgar; HTML/PDF text extraction non-trivial; may defer if Phase 1 NASDAQ-diff catches enough | EDGAR feed produces spinoff candidates with 30-90d lead time; PR with proposed Tier 2 additions; may DEFER if Phase 1 sufficient | ~2-3d (or DEFER) |

Sprint 5 effort revised: +5-7d → ~11.5-13.5d total

### Sprint 8 additions (Strategy Categories) — 3 decisions

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-368 | DEC-099-B — Calendar / Seasonal strategies (Sell-in-May, January effect, Santa rally, FOMC drift, end-of-month rebalancing); date-of-year + days-to-event cube dims in DEC-422 already capture these; integration is logging strategies in roster + verifying cube dim populates | Seasonal strategy fires only in date-window-active period; cube dim correctly classifies historical bars by season; 4-5 calendar strategies operational | ~2-3d |
| DEC-370 | DEC-099-D — Index Rebalance strategies — needs S&P/Russell adds-drops calendar; joint DEC-303 (historical_membership.csv) + DEC-394 (sector_history.csv Phase 1) + DEC-378 (NASDAQ symbol-directory weekly diff); Russell rebalance June; S&P quarterly | Historical index add events produce expected price drift in announcement→effective window (~3-7d); strategy entry timing tracks calendar | ~3-5d |
| DEC-371 | DEC-099-E — Within-category gaps catalog (Russell rebalance for momentum, pairs reversion for mean reversion, dark pool prints for smart money [Quiver DEC-450 paid endpoint], gap-fade for breakout) — output: catalog document or appended to PROJECT_PLAN | Catalog covers ≥10 within-category gaps; each gap has explicit data-source path identified; sub-decisions per gap as scoped | ~1d cataloging |

Sprint 8 effort revised: +6-9d → ~36-54d total

### Phase 2 Cleanup Batch ENG totals

| Sprint | Cleanup additions | Effort delta |
|---|---|---|
| Sprint 1 | +5 decisions | +5.5d |
| Sprint 2 | +3 decisions | +2.5-3.5d |
| Sprint 4 | +7 decisions (5 net-new + 2 absorbed) | +3.75-5.25d net-new |
| Sprint 5 | +4 decisions | +5-7d |
| Sprint 8 | +3 decisions | +6-9d |
| **Total** | **+22 ENG decisions** | **+22.75-30.25d net-new effort** |

## TOTAL PROJECT EFFORT POST-CLEANUP-BATCH

| Sprint | Effort |
|---|---|
| Sprint 1 (Phase 0.A foundation) | ~23-29d |
| Sprint 2 (Engine Bug Fixes Tier A) | ~25.5-30.5d |
| Sprint 3 (Phase 0.B Portfolio Class) | ~8-11d |
| Sprint 4 (DEC-410 Audit Findings) | ~33.75-46.25d |
| Sprint 5 (Universe Management) | ~11.5-13.5d |
| Sprint 5 NEW (Position Sizing) | ~3.5d |
| Sprint 6 (Phase 0.E + Hygiene) | ~37.75-47.25d |
| Sprint 7 (Statistical Methodology + A/B) | ~63.5-69.5d |
| Sprint 7-8 (Phase 1B-α Dimensional Cube) | ~24-33d |
| Sprint 8 (Strategy Categories) | ~36-54d |
| Sprint 9 (Phase 1B-α run + ongoing) | ~2.5d |
| **Total Stage 2 realistic** | **~270-340 engineering days** |

CRITICAL PATH revised: ~100-130d → likely **~110-145 days minimum** post-cleanup (Sprint 4 + Sprint 8 grew, both critical-path-relevant).


---

## Walkthrough 4 Additions (Pass 52 turn 113)

Per CHECKLIST #58 — sprint-tracker assignment for Walkthrough 4 (X16 + X43) approved decisions.

### Sprint 6 additions (Phase 0.E + Architecture Hygiene + new)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-138 | Cold-start CI test (`.github/workflows/cold_start.yml` runs weekly + on dependency changes; clone → pip install → smoke test → assert <30min) — joint DEC-219 + DEC-436 | Cold-start workflow runs weekly; full pipeline completes <30min from fresh container; failure → alert via DEC-219 alerting infrastructure | ~1-2d |

Sprint 6 effort revised: +1.5d → ~39.25-48.75d total

### Walkthrough 4 ENG totals

- Sprint 6: +1 decision (DEC-138)
- Total: **+1 ENG decision**

(Other 5 decisions are supersessions/deferrals — 0 net-new ENG sprint-slot effort)

---

## Batch B (Risk Management) Additions (Pass 52 turn 115)

Per CHECKLIST #58 — sprint-tracker assignment for 5 ENG decisions in Batch B.

### Sprint 4 (+1)
- DEC-019 (Liquidity filter timing) — joint DEC-321/366 ~0.5d

### Sprint 6 (+4)
- DEC-018 (Per-ticker stop-out cooldown 5d) ~0.5d
- DEC-134 (USD/CAD FX exposure tracking — Stage 2 portion) ~1d
- DEC-135 (Per-ticker cumulative max-loss cap rolling 30d) ~1d
- DEC-136 (Portfolio rebalancing threshold-based) ~0.5d

Sprint 4 effort: +0.5d → ~34.25-46.75d total
Sprint 6 effort: +3d → ~42.25-51.75d total


---

## Batch C (Code Quality + Defects) Additions (Pass 52 turn 117)

### Sprint 1 (+1)
- DEC-275 (requirements.txt audit) ~0.5d

### Sprint 6 (+5)
- DEC-170 (Type hints + mypy strict) ~3-5d
- DEC-171 (Docstring standard + sphinx) ~2-3d
- DEC-172 (Numerical constants → config; joint DEC-229) ~2d
- DEC-173 (ruff + black + isort + mypy CI gates) ~1d
- (DEC-274 absorbed by DEC-220, already in Sprint 6)

### Sprint 7 (+1)
- DEC-250 (Edge decay 20% default REVISIT_AFTER_BACKTEST) ~0.5d

### Sprint 9 (+1)
- DEC-249 (Strategy decay rolling 6mo Sharpe) ~1d

Sprint 1: +0.5d → ~17.5-23.5d
Sprint 6: +8-11d → ~50.25-62.75d
Sprint 7: +0.5d → ~64-70d
Sprint 9: +1d → ~3.5d


---

## Bulk Sweep Final (Batches D-K + DEC-251) Additions (Pass 52 turn 119)

Per CHECKLIST #58 — comprehensive sprint-tracker assignments for all remaining decisions in bulk sweep.

### Sprint 1 (+2)
- DEC-117 cache checksum + last-validated timestamp ~1d
- DEC-118 cross-asset macro prefetch (VIX/DXY/GLD/oil/sector ETFs/TLT/HYG/SHY) ~1.5d

### Sprint 4 (+5)
- DEC-122 per-exit-method slippage modeling ~1d
- DEC-123 exponential decay smart money weights ~0.5d
- DEC-124 cross-source smart money clusters ~1.5d
- DEC-125 Form 144 prefetch ~1d
- DEC-146 corporate actions handler ~2d
- DEC-159 regulatory event handler ~1.5d

### Sprint 5 (+1)
- DEC-147 delisting registry + survivorship correction ~2d

### Sprint 6 (+10)
- DEC-119 per-trade explainability dict ~1d
- DEC-127 circuit breaker recovery rules ~1d
- DEC-128 dispersion-conditional circuit breaker ~1d
- DEC-177 random seed in backtest output ~0.5d
- DEC-178 signal lookup performance benchmark ~1d
- DEC-179 memory profiling + memory cap ~1d
- DEC-183 memoization LRU cache ~1d
- DEC-251 dependency injection sandbox-prototype HARD-REVERSIBILITY ~5-7d

### Sprint 7 (+8)
- DEC-121 exit comparison report ~1d
- DEC-131 agent value-add two-gate refinement ~0.5d
- DEC-148 stock-specific adaptive momentum ~1d
- DEC-149 regime transition probability matrix ~1.5d
- DEC-150 multi-asset regime detection ~2d
- DEC-151 sector-level regime classification ~1.5d
- DEC-153 regime-stratified train/test splits ~1d
- DEC-155 vs-SPY comparison ~0.5d
- DEC-175 signal persistence weighting ~1d
- DEC-246 quant finance correctness audit ~1d
- DEC-247 stats/ML implementation review ~1.5d

### Sprint 7-8 (+3)
- DEC-062 TradingAgents 5-tier → position_size_modifier ~1d
- DEC-100 17+ categorical breakdown variables (joint DEC-422) absorbed
- DEC-184 parallel backtest execution ~2-3d
- DEC-120 automatic loss attribution report ~1d

### Sprint 8 (+1)
- DEC-174 strategy classification by trigger type ~1d

### Sprint 9 (+4)
- DEC-043 retune framework ~1d
- DEC-243 Owner Approval Queue file ~0.5d
- DEC-269 Stage 4 entry criteria documentation ~0.5d
- DEC-292 quarterly Decision→CHECKLIST migration ~0.5d quarterly

### Sprint effort revisions
- Sprint 1: +2.5d → ~20.5-26.5d
- Sprint 4: +7.5d → ~41.75-54.25d
- Sprint 5: +2d → ~13.5-15.5d
- Sprint 6: +12-14d → ~62.25-76.75d (DEC-251 HARD-REVERSIBILITY +5-7d included)
- Sprint 7: +10.5-13.5d → ~74.5-83.5d
- Sprint 7-8: +4-5d → ~28-38d
- Sprint 8: +1d → ~37-55d
- Sprint 9: +2.5d → ~6d


---

## DEC-042 AgentGateConfig Spec (Pass 52 turn 121) — FINAL PENDING DECISION RESOLVED

Per CHECKLIST #58 — sprint-tracker assignment for DEC-042.

### Sprint 7 (+1 — final ENG addition Pass 52)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-042 | AgentGateConfig spec — WEIGHTED CONTINUOUS-SCORE GATE ARCHITECTURE: (1) WEIGHTED approval rule with continuous score 0.0-1.0 per agent; default equal weights 0.25 each REVISIT_AFTER_BACKTEST; (2) Risk Manager veto required (s_risk ≥ 0.5 hard gate) + continuous-Risk-score testing extensively per owner directive #3; (3) gate_score ≥ 0.5 enters trade pre-Risk-veto; (4) Bull-vs-Bear must align (s_bull > 0.5 AND s_bear > 0.5 for long; both < 0.5 for short); (5) Tier mapping ≥0.8 HIGH, 0.65-0.8 MED, 0.5-0.65 LOW per DEC-021 3-tier (5%/3%/1.5%); (6) Stage 2 deterministic, Stage 3+ owner override. Joint DEC-021/051/058/062/131/205-216/211 cluster. | (a) AgentGateConfig dataclass typed; weights sum to 1.0 invariant; scores 0.0-1.0 invariant; (b) Bull=0.8 Bear=0.7 Risk=0.6 Chart=0.5 → gate_score=0.65 + Risk≥0.5 + align → MED-tier entry; (c) Risk=0.4 below veto → REJECT; (d) Bull=0.8 Bear=0.3 disagreement → REJECT; (e) continuous-Risk A/B arm vs binary-veto arm produces measurable Sharpe delta; (f) DEC-216 A/B orchestrator passes config per arm | ~1-2d (config dataclass + defaults + integration with DEC-216 A/B orchestrator + Risk continuous-score test infra) |

Sprint 7 effort revised: +1.5d → ~76-85d total (was 74.5-83.5d)

### Pass 52 Final ENGINEERING_REGISTER Coverage

Per CHECKLIST #58 — all RESOLVED-DECIDED engineering decisions now have sprint slots with test signals + effort estimates. Substantively-homeless count: 0 ✓.


---

## BUG-111 Verification + DEC-298 Status Correction (Pass 52 turn 123)

Per CHECKLIST #58 — verification of resolution path for CRITICAL OPEN bug (BUG-111) + honest correction of DEC-298 status mislabel from turn 121.

### BUG-111 Resolution Path Verified

**Severity history:** MEDIUM (Pass 13) → HIGH (Pass 52) → CRITICAL (Pass 52)

**Resolution components:**
1. **DEC-355/356/357** (Sprint 8) — 3 chart pattern strategies with explicit retest variants (Trendline / Channel / Range break-and-retest)
2. **DEC-358-362** (Sprint 8) — 5 chart pattern strategies (Wedge/triangle, H&S, Double top/bottom, Cup/handle, Flag/pennant) with retest cross-cutting primitive
3. **Existing breakout strategies retest scope** — 25 strategies in screener.py categories (Breakout 6 + Pivot Based 10 + Confluence 9) may need `_retest` variants

### NEW Sprint 8 sub-decision: Shared Retest Primitive vs Explicit Variants

**Open architectural choice (per BUG-111 Pass 52 escalation):**

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| BUG-111-RESOLUTION (cross-cutting) | Shared retest entry-signal primitive that any breakout strategy can opt into (Option A) OR explicit `_retest` suffixed variant per existing breakout strategy (Option B). Owner direction needed at Sprint 8 implementation time. | (Option A) `def is_retest(symbol, breakout_level, lookback) -> bool` callable from any breakout strategy with `requires_retest=True` flag; (Option B) 25+ new `_retest` strategy classes; mechanical translation per breakout strategy | Option A: ~5-10d (1-2d primitive + 3-8d integration into existing breakout strategies); Option B: ~25-30d (1d per existing strategy `_retest` variant) |

**Recommendation: Option A** (shared primitive) — much smaller surface, opt-in flexibility, easier maintenance. Owner reviews at Sprint 8 implementation start.

### DEC-298 Status Correction

**Honest correction per #25:** Pass 52 turn 121 commit narrative claimed "DEC-298 PIT cache rebuild — still BLOCKED; gates DEC-377/411." This was wrong.

**Actual status (verified):** DEC-298 is **RESOLVED-DECIDED** (Pass 52 Theme 1 PIT closure). The decision was approved: switch `auto_adjust=False`, store raw OHLCV + corp actions, recompute adjusted-on-demand by as_of date.

**What's actually pending:** SPRINT EXECUTION of DEC-298 (cache rebuild ~5 engineering days). DEC-377 + DEC-411 wait for that implementation, not the decision.

**Tracking location:** Sprint 4 ENGINEERING_REGISTER (already in scope).

**Conclusion:** No status flip needed for DEC-298. Downstream "blocking" of DEC-377/411 is sprint-execution sequencing (Sprint 4 implementation of DEC-298 must complete before Sprint 4 DEC-377 + DEC-411), not decision pendency. Standard sprint dependency.


---

## DEC-459 (Pass 52 turn 129) — AgentGateConfig Option C Hybrid Architecture (SUPERSEDES DEC-042)

Per CHECKLIST #58 — sprint-tracker assignment for revised AgentGateConfig spec.

### Sprint 7 (REVISED — DEC-042 removed, DEC-459 added)

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-459 | AgentGateConfig — Option C Hybrid: TradingAgents Portfolio Manager native confidence as primary signal + separate Risk veto layer + Research Manager alignment check + DEC-021 tier mapping. Implements owner directives turn 121 (continuous-score, alignment, Risk extensive testing, tier modifier) carried forward but adapted to actual TradingAgents architecture. | (i) Dataclass typed (PM confidence 0.0-1.0); (ii) PM(BUY,0.85) + RM(align,0.7) + Risk(0.6) → HIGH-tier 5%; (iii) PM(BUY,0.85) + Risk(0.4) → veto REJECT; (iv) PM(BUY,0.7) + RM(contested,0.4) → align fail REJECT; (v) PM(HOLD) → REJECT; (vi) DEC-216 A/B arms full-with-veto/no-Risk/no-align config-driven; (vii) Continuous-Risk vs binary-veto A/B Sharpe delta measurable; (viii) LangGraph state extraction reachable. | ~2-3d (config dataclass 0.5d + LangGraph state extraction 1d + DEC-216 integration 0.5d + Risk continuous-score test infra 0.5d) |

(DEC-042 entry from earlier sprint-tracker assignment removed Pass 52 turn 129 per supersession by DEC-459)

### Sprint 7 effort revised

| Pre-supersession | Post-supersession | Delta |
|---|---|---|
| ~76-85d (DEC-042 ~1-2d included) | ~77-86d (DEC-459 ~2-3d, DEC-042 removed) | +1d |

### Implementation options within Option C (Sprint 7 implementation start)

(7a) Risk signal extraction method:
- LangGraph state hook (recommended; ~1d implementation)
- Separate Risk Manager call (cost+latency overhead; ~0.5d but ongoing cost penalty)
- PM risk-adjusted confidence only (collapses to pure Option B; no separate veto)

(7b) Research Manager alignment threshold: 0.5 default

(7c) Whether to log intermediate agent debate transcripts (per DEC-189 + DEC-200 Dashboard 2)

Owner direction needed at Sprint 7 implementation start.


---

## Sprint 7 — Pattern 2 Custom Toolkit Build (Pass 52 turn 130 — DEC-460 through DEC-468)

Per CHECKLIST #58 + #60 NEW (data dependency verification on architectural decisions).

Origin: TRADINGAGENTS_DATA_AUDIT.md (Pass 52 turn 130) identified critical data input gaps that would have invalidated Stage 2 A/B testing efficacy.

### Pre-Sprint-1 additions

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-460 | Verify Polygon Stocks Starter PIT fundamentals coverage | Documented endpoint inventory; sample fetch with as_of validation; freezegun PIT verification | ~0.5d |
| DEC-461 | (conditional on DEC-460) Subscribe to FMP $14-50/mo if Polygon insufficient | FMP API keys configured; sample fetch validated | ~0.25d (subscription only) |

### Sprint 7 Pattern 2 toolkit additions

| DEC-N | Description | Test signals | Effort |
|---|---|---|---|
| DEC-462 | OurTechnicalToolkit (extends TechnicalToolkit) — Polygon OHLCV + ICT/SMC + chart patterns + multi-timeframe regime + sector relative strength + liquidity + break-and-retest | Each method properly typed; PIT correctness via freezegun; ICT/SMC matches smartmoneyconcepts; multi-timeframe matches DEC-106 | ~3-4d |
| DEC-463 | OurFundamentalsToolkit (extends FundamentalsToolkit) — PIT financials + earnings transcripts + analyst estimates + Quiver smart money + Ortex short interest + government contracts + SEC filings + industry comparables | PIT correctness on every method; smart money composite matches DEC-124; Ortex date filter correct | ~4-5d |
| DEC-464 | OurNewsToolkit (extends NewsToolkit) — Polygon news + macro feed + FRED event calendar + Quiver analyst rating changes | Polygon news date ≤ as_of; event calendar respects DEC-349 asymmetric window | ~2d |
| DEC-465 | OurTraderToolkit (NEW) — current price + bid/ask + liquidity + DEC-021 sizing + DEC-092 slippage + DEC-399 borrow + portfolio state + cash + per-ticker cooldown DEC-018 + max-loss DEC-135 | Sizing matches DEC-021 exactly; slippage combines DEC-092+122+280; portfolio state from Portfolio class | ~3-4d |
| DEC-466 | OurRiskToolkit (NEW) — vol regime + ATR + correlation + sector concentration + drawdown + macro stress + event proximity + crisis flags + similar-setup outcomes | Correlation valid pairwise; sector concentration matches portfolio; crisis flags fire per DEC-262 | ~3-4d |
| DEC-467 | OurAgentState schema extension — 7 new state fields + Phase 1/2/3 injection points | State extends default cleanly; injection at correct LangGraph nodes; downstream agents can read | ~2d |
| DEC-468 | Wire Ortex short interest into OurFundamentalsToolkit + state injection for Bear/Risk Debaters | Ortex API keys configured; date filter correct; state injection works | ~1.5d |
| **Sub-total Sprint 7 toolkit additions** | | | **~19-22.5d** |

### Hard dependencies

- **DEC-465 OurTraderToolkit + DEC-466 OurRiskToolkit + DEC-467 portfolio_context state field:** Sprint 3 Portfolio class (BUG-095) MUST land first.
- **DEC-466 OurRiskToolkit + DEC-467 historical_outcomes state field:** DEC-189 reflection log (Sprint 7-8) — partial circular; start without, add later.
- **DEC-462 OurTechnicalToolkit:** Sprint 1 Polygon prefetch + Phase 0.D ICT/SMC fork (DEC-045).
- **DEC-463 OurFundamentalsToolkit:** DEC-460 verification + DEC-461 conditional FMP.

### Sprint 7 effort revised

| Pre-toolkit | Post-toolkit | Delta |
|---|---|---|
| ~77-86d (after DEC-459 +1d) | **~96-108.5d** | **+19-22.5d (~25-28%)** |

### Pre-Sprint-1 effort revised

| Pre-additions | Post-additions | Delta |
|---|---|---|
| ~9-11d (10 actions per Pass 52 turn 125) | **~9.75-11.75d** | **+0.75d (verification work)** |

### Sequencing recommendation

Sprint 7 Day 1 (parallel-able with Sprint 3 Portfolio class build):
- Start DEC-462 OurTechnicalToolkit
- Start DEC-463 OurFundamentalsToolkit (after DEC-460/461 resolution)
- Start DEC-464 OurNewsToolkit
- Start DEC-467 OurAgentState (partial — schema definition)

Sprint 7 after Portfolio class lands (Sprint 3 completion):
- DEC-465 OurTraderToolkit
- DEC-466 OurRiskToolkit
- DEC-467 OurAgentState (complete — portfolio_context wiring)
- DEC-468 Ortex wiring

### Critical path implication

Sprint 7 cannot fully complete until Sprint 3 Portfolio class (BUG-095) resolves. Same critical path dependency as before but now explicit: agent toolkit work has 3 distinct phases (parallel-able / Portfolio-blocked / DEC-189-blocked).

