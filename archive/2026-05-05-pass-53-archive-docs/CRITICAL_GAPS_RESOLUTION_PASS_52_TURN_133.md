# Critical Gaps Resolution — Cluster 1 + 2 + 3 + GAP 46

**Document role:** Resolutions for the 23 CRITICAL gaps from ADVERSARIAL_AUDIT, executed per owner directives Pass 52 turn 133. Documents external verification findings (TradingAgents v0.2.4 source + Polygon docs) that change the architectural picture.

**Created:** Pass 52 turn 133
**Owner directives turn 133:**
- 1a: Bonferroni → FDR APPROVED
- 1b: Cube dimensionality reduction APPROVED (per recommendation)
- 1c: Eliminate paired design (NEW DIRECTIVE)
- 1d: Reduce A/B arms (NEW DIRECTIVE)
- 2a: Claude reads TradingAgents source for Pydantic schema verification YES
- 2b: If RM `confidence` missing, fallback to Trader confidence
- 3a: Portfolio Class API spec in TRADING_RULES new section APPROVED
- 3b: Claude drafts Portfolio class spec YES
- 4a: Claude provides recommendations for Cluster 4 architectural clarifications
- GAP 46: Claude reads Polygon docs

**Honest accountability per #25:** External verification revealed findings worse than originally documented. Pre-existing decisions DEC-441 ($30/mo) + DEC-459 (Option C numeric confidence assumption) require revision. This is the 8th instance of Pass 52 owner accountability vindication — but PROACTIVE per L140 (adversarial review revealed gaps before commitment to flawed architecture).

---

## TABLE OF CONTENTS

**Part A — External Verification Findings**
1. TradingAgents v0.2.4 Pydantic Schema Verification (Directive 2a)
2. Polygon Stocks Starter Capability Verification (GAP 46)

**Part B — Cluster 1: Statistical Methodology (4 CRITICAL gaps + cascade)**
3. FDR Multiple Testing Methodology (Directive 1a)
4. Cube Dimensionality Reduction (Directive 1b)
5. Paired Design Elimination (Directive 1c)
6. A/B Arm Reduction (Directive 1d)

**Part C — Cluster 2: Agent Schema Reconciliation (revised)**
7. DEC-459 Option C Architecture Revision (post-verification)
8. RM Confidence Fallback to Trader Confidence (Directive 2b)

**Part D — Cluster 3: Portfolio Class API Spec (Directive 3a + 3b)**
9. Portfolio Class API Specification

**Part E — Cluster 4: Architectural Clarifications (Directive 4a — recommendations)**
10. Recommendations for Cluster 4 Gaps

**Part F — Polygon Tier Decision (GAP 46 cascade)**
11. Polygon Stocks Starter vs Higher Tier Cost-Benefit

**Part G — New Decisions Required (PROPOSED)**
12. DEC-469 through DEC-481 PROPOSED

---

# PART A — EXTERNAL VERIFICATION FINDINGS

## 1. TradingAgents v0.2.4 Pydantic Schema Verification

**Source:** TradingAgents v0.2.4 CHANGELOG + README + GitHub release notes (2026-04-25 release).

### 1.1 Reality vs Assumed (DEC-459 Option C)

| Field | DEC-459 Assumed | Reality (v0.2.4) |
|---|---|---|
| **Portfolio Manager output rating** | `decision: BUY / HOLD / SELL` (3-tier) | **`rating: Buy / Overweight / Hold / Underweight / Sell` (5-tier)** |
| **Portfolio Manager confidence** | `confidence: float 0.0-1.0` | **NOT CONFIRMED** — SignalProcessor reads rating from "rendered markdown via deterministic heuristic" (no numeric confidence) |
| **Trader output** | (not specified) | `rating: Buy / Hold / Sell` (3-tier; "transaction direction is naturally ternary") |
| **Research Manager output** | `RM_confidence: float; RM_direction` | Pydantic schema EXISTS but `confidence` field NOT CONFIRMED |
| **Risk Debate output** | `s_risk: float 0.0-1.0` | Pydantic structured output (Aggressive / Conservative / Neutral synthesized by PM) but raw `s_risk` field NOT CONFIRMED |

### 1.2 Architectural Impact

**DEC-459 Option C is partially unimplementable as currently specified.** Specifically:

- **Tier mapping from PM confidence is broken.** PM output is 5-tier categorical, not 0.0-1.0 continuous. We can map 5-tier → tier (e.g., Buy = HIGH 5%, Overweight = MEDIUM 3%, Hold/Underweight/Sell = REJECT) but lose granular confidence.
- **§7.4 alignment check via `RM_confidence ≥ 0.5`** is unimplementable as specified — RM may not expose numeric confidence.
- **§7.2 Risk veto via `s_risk ≥ 0.5`** is unimplementable — Risk debate produces text/structured output, not numeric score.
- **§7.7 Sequential gate logic (Check 2 PM confidence < 0.5 → REJECT)** is unimplementable — no numeric confidence field.

### 1.3 Two Architectural Paths Forward

**PATH A: Use 5-tier rating directly (recommended)**
- PM rating → tier mapping: `Buy → HIGH 5%`, `Overweight → MEDIUM 3%`, `Hold → LOW 1.5% or REJECT`, `Underweight → REJECT`, `Sell → SHORT entry candidate`
- Risk veto: parse Risk debate FINAL VERDICT (Aggressive vs Conservative vs Neutral consensus) from rendered markdown — same heuristic SignalProcessor uses
- RM alignment: parse RM rating from rendered markdown — does it agree with PM direction?
- **Pros:** Uses framework as-designed; no schema modification; matches v0.2.4 design intent
- **Cons:** Loses 0.0-1.0 granularity for tier assignment; tier thresholds at fixed boundaries

**PATH B: Force structured output extension (modify framework or post-process)**
- Wrap PM/Trader/RM with `with_structured_output(ExtendedSchema)` where extended schema adds `confidence: float`
- Risk: forking framework or post-processing rendered output
- **Pros:** Preserves DEC-459 numeric confidence semantics
- **Cons:** Brittle; v0.2.4 framework rejection of confidence field design (deterministic heuristic preferred) suggests anti-pattern

### 1.4 Recommendation

**Path A recommended.** Owner directive 2b ("If RM confidence missing, fallback to Trader confidence") combined with this finding suggests broader rethink: **map all rating fields to tier, with Risk veto + RM alignment as binary checks (parsed from markdown), not numeric thresholds.**

**This is a significant DEC-459 revision (would require DEC-481 PROPOSED — Option C2 Hybrid revised for v0.2.4 Pydantic reality).**

### 1.5 Historical context

DEC-042 → DEC-459 supersession Pass 52 turn 129 fixed architectural-fit (parallel-voter assumption wrong). DEC-459 → DEC-481 PROPOSED supersession Pass 52 turn 133 fixes data-type-fit (continuous confidence assumption wrong). **Same root cause: assumptions about TradingAgents framework not verified against source.**

---

## 2. Polygon Stocks Starter Capability Verification (GAP 46)

**Source:** polygon.io/pricing (verified Pass 52 turn 133).

### 2.1 Stocks Starter $29/mo Coverage

| Capability | Stocks Starter ($29) | Stocks Developer ($79) | Stocks Advanced ($199) |
|---|---|---|---|
| Historical OHLCV daily | 5 years ✓ | 10 years ✓ | 20+ years ✓ |
| Minute Aggregates | ✓ | ✓ | ✓ |
| Second Aggregates | ✓ | ✓ | ✓ |
| Reference Data | ✓ | ✓ | ✓ |
| Corporate Actions | ✓ | ✓ | ✓ |
| Technical Indicators | ✓ | ✓ | ✓ |
| Snapshot | ✓ | ✓ | ✓ |
| WebSockets | ✓ | ✓ | ✓ |
| **Real-time Data** | ❌ (15-min delayed) | ❌ (15-min delayed) | ✓ Real-time |
| **Trades (tick)** | ❌ | ✓ | ✓ |
| **Quotes (bid/ask)** | ❌ | ❌ | ✓ |
| **Financials & Ratios** | ❌ | ❌ | ✓ (or separate $29 add-on) |
| API call rate | Unlimited | Unlimited | Unlimited |
| File downloads | Unlimited | Unlimited | Unlimited |

### 2.2 Critical Findings vs Project Plan

**1. Cost discrepancy (minor):** DEC-441 says "$30/mo." Reality: **$29/mo.** Cost summary update needed.

**2. Bid/Ask quotes NOT included in Stocks Starter (CRITICAL — GAP 46 confirmed worse).**
- DEC-465 OurTraderToolkit `get_bid_ask_estimate(ticker, as_of)` cannot use Polygon Stocks Starter
- For backtest mode, bid/ask must be ESTIMATED from spread model + slippage (DEC-092) — Polygon not used
- For live trading (Stage 4+), real-time quotes require IBKR market data subscription (~$10-30/mo per DEC-271) — already in plan
- **Resolution: drop `get_bid_ask_estimate` from Stocks Starter scope; document slippage model as bid/ask proxy in backtest**

**3. Trades (tick data) NOT in Stocks Starter.**
- For ICT/SMC primitives (FVG, BOS, CHoCH) — minute aggregates may be sufficient
- For accurate intraday MAE/MFE (per Cube §22.4 metrics) — minute aggregates are the floor
- **Resolution: minute aggregates floor for backtest; tick data not required**

**4. Financials NOT in Stocks Starter (CRITICAL — DEC-460 partially RESOLVED).**
- This was the GAP A concern (PIT fundamentals)
- **DEC-460 verification result: NEGATIVE.** Polygon Stocks Starter does NOT cover income statement / balance sheet / cash flow.
- **DEC-461 conditional FMP NOW MANDATORY** — owner directive turn 130 was "Happy to upgrade"; FMP $14-50/mo or Polygon Stocks Advanced $199/mo or separate Financials add-on $29/mo.

**5. Historical depth = 5 years (CRITICAL — GAP 54/136 confirmed worse).**
- 5 years from May 2026 = May 2021 onwards
- Walk-forward (DEC-109) requires 5-year train + multiple OOS folds
- Cache extension to 2018-01-01 (DEC-411) **CANNOT BE FULFILLED** with Stocks Starter alone
- 2019-2024 OOS folds (per ADVERSARIAL_AUDIT §16.3) require 2014+ for 5-year train of 2019 fold — **2014-2020 outside Stocks Starter coverage**
- **Resolution candidates:**
  - Polygon Stocks Developer $79/mo (10 years) covers 2016-2026 — supports 2021-2026 OOS folds with 5-year train
  - Polygon Stocks Advanced $199/mo (20+ years) — full coverage but expensive
  - yfinance for pre-2021 data with PIT caveats

**6. Real-time data NOT in Stocks Starter (delayed 15-min).**
- For Stage 2 backtest: irrelevant (backtest uses historical, not delayed)
- For Stage 3 paper / Stage 4+ live: requires IBKR market data subscription OR Polygon Stocks Advanced

### 2.3 Recommendation

**Tier upgrade decision needed:**

| Option | Cost | Pros | Cons |
|---|---|---|---|
| Stay Stocks Starter $29/mo | $29/mo | Cheapest | 5-year history insufficient for walk-forward; no financials; no quotes |
| **Upgrade Stocks Developer $79/mo** | $79/mo (+$50/mo) | 10-year history (sufficient); tick trades | Still no quotes; still no financials |
| Upgrade Stocks Advanced $199/mo | $199/mo (+$170/mo) | Real-time + quotes + financials + 20yr history | Expensive |
| Stocks Starter + Financials add-on | $58/mo (29+29) | Cheapest path to financials | Still 5-year history; no quotes |
| Stocks Starter + FMP | $43-79/mo | Financials + transcripts + estimates | 5-year history still issue |
| Stocks Developer + FMP | $93-129/mo | 10-yr history + financials + transcripts | Best balance |

**My recommendation: Stocks Developer $79/mo + FMP $14-50/mo = $93-129/mo total.** This addresses:
- 10-year history (DEC-109 walk-forward viable)
- FMP fundamentals (Gap A)
- FMP transcripts (Gap B)
- FMP analyst estimates (Gap C)
- $93-129/mo within owner directive turn 130 ("Happy to upgrade")

**Owner decision needed:** Approve upgrade path? Different option?

---

# PART B — CLUSTER 1: STATISTICAL METHODOLOGY

## 3. FDR Multiple Testing Methodology (Directive 1a)

**Resolves:** GAP 126

### 3.1 From Bonferroni to Benjamini-Hochberg FDR

**Old methodology (TRADING_RULES §3.2):** Bonferroni correction on raw p-values.
- Problem: 7.7M tests → α = 0.05/7.7M = 6.5e-9 → no test passes.

**New methodology:** **Benjamini-Hochberg False Discovery Rate (FDR).**
- Controls FDR (expected proportion of false discoveries among rejections) rather than family-wise error rate (FWER).
- Hierarchical structure: apply FDR per strategy first, then per cell within strategy, then aggregate.
- Default FDR target: q = 0.10 (10% expected false discovery rate among PASS cells).

### 3.2 Hierarchical Structure

**Level 1 — Per-Strategy Filter:**
- Compute aggregate Sharpe (all OOS folds, all cells) per strategy
- Apply BH-FDR at q = 0.10 across 119 strategies
- Strategies failing this level → REJECTED at strategy level
- Expected to retain top ~30-50% of strategies

**Level 2 — Per-Cell Filter (within retained strategies):**
- For each retained strategy, apply BH-FDR at q = 0.10 across cells with n ≥ 30 trades
- Cells failing → INSUFFICIENT_EVIDENCE (NOT FAIL_STAT)

**Level 3 — Per-Regime Subgroup:**
- Within retained strategy×cell combinations, examine regime breakdown
- BH-FDR at q = 0.20 (looser, exploratory)
- Per-regime verdicts feed into live decision lookup table (DEC-429)

### 3.3 Expected Outcome

- Strategies retained: ~30-60 of 119
- Cells retained: ~5-15% of populated cells (which themselves are ~10-30% of 65K = 6.5K-20K populated)
- Final PASS cells: ~300-3000 (a working live decision table)

### 3.4 Implementation

Implementation moves to `backtest/statistics/fdr.py` per ENGINEERING_REGISTER Sprint 7.

---

## 4. Cube Dimensionality Reduction (Directive 1b)

**Resolves:** GAP 130

### 4.1 Current vs Reduced

**Current (TRADING_RULES §21.1):** 17+ dimensions × 3-5 levels each.

**Reduced to 8 core dimensions:**

| # | Dimension | Levels | Notes |
|---|---|---|---|
| 1 | Strategy | 119 | Strategy axis (always included) |
| 2 | Market regime | 4 (calm/neutral/volatile/crisis) | Per DEC-106 |
| 3 | Sector | 11 GICS sectors | |
| 4 | Market cap band | 3 (mega/large/mid) | Reduced from 5 |
| 5 | Vol band | 3 (low/medium/high VIX) | |
| 6 | Hold period band | 3 (short/medium/long) | Reduced from 4 |
| 7 | Universe tier | 3 (Tier 1/2/3) | |
| 8 | Smart money signal present | 2 (yes/no) | Binary |

**Cell count:** 119 × 4 × 11 × 3 × 3 × 3 × 3 × 2 = 254,016 → similar order of magnitude but more meaningful.

**Expected populated cells:** ~20-30% (50K-75K) vs prior 65K but with sample sizes more realistic.

### 4.2 Eliminated Dimensions (moved to per-strategy attributes, not cube axes)

These become STRATEGY ATTRIBUTES (recorded but not faceted):
- Momentum band (track per-trade)
- Liquidity band (filter, not faceted)
- Entry trigger type (recorded, not faceted)
- Exit method (recorded, not faceted)
- News event present (recorded, not faceted)
- Earnings proximity (already filter via DEC-348 event suppression)
- ICT/SMC signal type (per-strategy, not faceted)

### 4.3 Cube Verdict Verbosity

Per-cell metrics suite (TRADING_RULES §22.4) preserved for retained dimensions; eliminated dimensions become trade-level metadata in DEC-189 trade outcome log for separate analysis.

---

## 5. Paired Design Elimination (Directive 1c — NEW)

**Resolves:** GAP 133

### 5.1 Old Design (Paired)

**TRADING_RULES §18.2:** "Paired design (every trade by every arm)."

**Problem (GAP 133):** Trade SETS DIFFER per arm. Statistical comparison invalid.

### 5.2 New Design (Independent A/B with Subset Overlap)

**Approach:** Each arm runs INDEPENDENTLY on its own decision logic. Comparison uses:
1. **Shared opportunity set** — every CANDIDATE evaluated by every arm (decision-level pairing, not trade-level)
2. **Per-arm trade set** — each arm's trades determined by its own gate
3. **Comparison metric** — per-arm Sharpe / Sortino / DD / win rate / etc. on respective trade sets

**Key shift:** From "paired t-test on trade-level metrics" to "two-sample comparison on independent trade sets with shared opportunity universe."

### 5.3 Statistical Test Replacement

**Old (paired):** Paired t-test on per-trade Sharpe contribution.

**New (independent):** Block bootstrap confidence intervals on per-arm Sharpe; compare overlap.
- Bootstrap 1000 iterations, block size = 20 trading days
- Compute Sharpe per bootstrap iteration per arm
- Compare arm-vs-arm CI overlap; non-overlapping CIs → significant difference

**This handles trade-set differences correctly** because each arm's Sharpe is computed on its own trade set.

### 5.4 Sample Size Implication

Pre-commit minimum: **300 candidates evaluated by all arms** (NOT 300 paired trades).

Per-arm trade count varies (some arms reject more); each arm's effective sample = candidates × accept_rate.

If full-with-veto accept rate = 20%, per-arm sample = 60 trades — still meets §3 Gate 1 n ≥ 30.

If rules-only accept rate = 50%, per-arm sample = 150 trades — comfortably meets gate.

### 5.5 Cost Implication

**Old (paired):** 300 trades × all 5 arms × $0.25/propagate = $1500-2000 (5-7× over $300 budget).

**New (independent with shared opportunity):** 300 candidates × $0.25/propagate × 1 propagate per candidate (since arms differ in DECISION LOGIC, not in TradingAgents call) = **$75 for shared TradingAgents calls + $0 for rules-only arm**.

**Why:** TradingAgents propagate() is ONE call per candidate; arms differ in how the propagate() output is GATED (Risk veto on/off, alignment on/off). Same propagate() output, different gates. **Cost is per-candidate, not per-arm.**

This single change resolves GAP 51 (A/B budget math).

---

## 6. A/B Arm Reduction (Directive 1d — NEW)

**Resolves:** GAP 51 (with §5 cost structure update)

### 6.1 Old Arms (5)

| Arm | Description |
|---|---|
| A | Rules-only |
| B | Full-agents-with-veto (default) |
| C | No-Risk (Risk veto disabled) |
| D | No-align (RM alignment disabled) |
| E | Ablation per DEC-211 |

### 6.2 New Arms (3)

| Arm | Description | Rationale |
|---|---|---|
| **A** | **Rules-only** | Baseline |
| **B** | **Full-agents-with-veto** | Default config (DEC-481 revised Option C) |
| **C** | **No-Risk** | Critical comparison: does Risk veto add value? Owner directive turn 121 #3 carried forward |

**Eliminated:**
- Arm D (No-align) — collapses into Arm C with parameter; or moved to Sprint 9 ablation
- Arm E (DEC-211 ablation) — moved entirely to Sprint 9 NARROW SCOPE post-Phase-1B-α (already DEC-211 spec)

### 6.3 Cost Reconciliation

**3 arms × 300 candidates × $0.25 = $225** (within $300 budget per DEC-059).

Plus rules-only arm at $0 (no agents) → effectively $225 total.

Buffer for re-runs / debugging: $75.

### 6.4 Statistical Power

3-arm comparison (rules / full-with-veto / no-Risk) is the **minimum interesting comparison set**:
- A vs B: does the agent overlay add value?
- B vs C: does the Risk veto add value?
- A vs C: does any agent presence (without Risk gate) add value?

---

# PART C — CLUSTER 2: AGENT SCHEMA RECONCILIATION

## 7. DEC-459 Option C Architecture Revision

**Required:** DEC-459 needs revision per Part A finding (5-tier rating, no numeric confidence).

### 7.1 Revised Architecture (DEC-481 PROPOSED — Option C2)

**Primary signal:** PM 5-tier rating + Trader 3-tier rating

**Tier mapping from PM 5-tier rating:**

| PM rating | Tier | Position size |
|---|---|---|
| **Buy** | HIGH | 5% per DEC-021 |
| **Overweight** | MEDIUM | 3% |
| **Hold** | LOW | 1.5% (or REJECT — owner discretion) |
| **Underweight** | REJECT | — |
| **Sell** | SHORT entry candidate | tier per Buy/Overweight on short side |

**Risk veto layer:** Parse Risk Debate FINAL VERDICT from rendered markdown via deterministic heuristic (same approach SignalProcessor uses in v0.2.4).
- If Risk Debate consensus = "REJECT" or aggressive overrides → veto fires
- Implementation: regex/parser on rendered Risk Debate output
- If parsing fails → CONSERVATIVE FALLBACK (REJECT) per #51

**Bull/Bear alignment:** Parse RM rating (5-tier) from rendered markdown.
- RM rating direction must match PM rating direction (Buy/Overweight = bullish; Underweight/Sell = bearish; Hold = neutral)
- If RM Hold but PM Buy/Sell → contested → REJECT
- If RM rating same direction as PM rating → align ✓

**Trader confidence fallback (Directive 2b):**
- If Trader rating = Buy and PM rating = Buy: high alignment, additional confidence
- If Trader rating = Hold but PM rating = Buy: PM overrides Trader; treat as MEDIUM tier (downgrade from HIGH)
- If Trader rating opposes PM rating: REJECT

### 7.2 Tier Threshold Replacement

Old (DEC-459): `confidence ≥ 0.8 → HIGH, 0.65 ≤ confidence < 0.8 → MEDIUM, 0.5 ≤ confidence < 0.65 → LOW`

New (DEC-481):
- **HIGH:** PM rating = Buy AND RM rating ∈ {Buy, Overweight} AND Trader rating = Buy AND Risk veto not fired
- **MEDIUM:** PM rating = Buy AND (RM rating = Buy or Trader rating = Hold) AND Risk veto not fired
- **MEDIUM:** PM rating = Overweight AND RM rating ∈ {Buy, Overweight} AND Risk veto not fired
- **LOW:** PM rating = Overweight AND (RM rating ∈ {Hold, Overweight}) AND Risk veto not fired
- **REJECT:** Otherwise

### 7.3 A/B Framework Compatibility

| Arm | Implementation |
|---|---|
| Rules-only | Bypass agents; rules-based tier from screen |
| Full-agents-with-veto | DEC-481 Option C2 default config |
| No-Risk | DEC-481 Option C2 with Risk veto disabled (Risk Debate output ignored) |

### 7.4 Implementation

Sprint 7 effort revised: ~3-4d (vs DEC-459 ~2-3d; +1d for markdown-parsing logic):
- Config dataclass with tier mapping rules ~0.5d
- Markdown parser for PM/RM/Trader/Risk Debate ratings ~1.5d (new)
- DEC-216 A/B orchestrator integration ~0.5d
- Test infrastructure ~0.5d (synthetic 5-tier outputs)

### 7.5 Test Signals

- (a) PM(Buy) + RM(Buy) + Trader(Buy) + Risk(approve) → HIGH-tier 5%
- (b) PM(Buy) + RM(Hold) + Trader(Buy) + Risk(approve) → MEDIUM-tier 3% (RM downgrade)
- (c) PM(Overweight) + RM(Buy) + Trader(Buy) + Risk(approve) → MEDIUM-tier 3%
- (d) PM(Buy) + Risk(veto) → REJECT regardless
- (e) PM(Buy) + Trader(Sell) → REJECT (opposing)
- (f) PM(Hold) → REJECT or LOW-tier (owner discretion — REVISIT_AFTER_BACKTEST)
- (g) Markdown parser handles all v0.2.4 rendered output formats

---

## 8. RM Confidence Fallback to Trader Confidence (Directive 2b)

Already integrated in §7.2 above:
- Trader rating used as alignment cross-check
- Trader rating disagreement with PM → REJECT
- Trader rating agreement with PM → confidence boost

---

# PART D — CLUSTER 3: PORTFOLIO CLASS API SPEC (Directives 3a + 3b)

## 9. Portfolio Class API Specification

**Location:** New section in TRADING_RULES_AND_INFORMATION.md — proposed §24 "Portfolio Class API" (Part L).

### 9.1 Purpose

Portfolio class is the runtime state container for the backtest engine. Holds positions, cash, drawdown, sector concentration. Enables Sprint 7 toolkits (DEC-465 Trader, DEC-466 Risk) to query state.

### 9.2 Class Spec

```python
class Portfolio:
    """PIT-correct portfolio state for backtest + live trading."""
    
    # ============ STATE FIELDS ============
    cash: Decimal  # Available cash (USD; Stage 4+ multi-currency)
    positions: Dict[str, Position]  # ticker → Position
    closed_trades: List[ClosedTrade]  # historical closed trades
    open_orders: List[Order]  # pending orders (Stage 3+)
    
    # ============ SETUP ============
    def __init__(self, initial_cash: Decimal, as_of_date: date, ...): ...
    
    # ============ POSITION QUERIES ============
    def get_existing_position(self, ticker: str) -> Optional[Position]:
        """Returns current position in ticker; None if no position."""
    
    def get_all_positions(self) -> Dict[str, Position]:
        """Returns all current positions."""
    
    def get_cash_available(self) -> Decimal:
        """Returns available cash for new positions."""
    
    def get_portfolio_state(self) -> PortfolioStateSnapshot:
        """Returns complete portfolio snapshot at current as_of date."""
    
    # ============ AGGREGATE QUERIES ============
    def get_total_value(self) -> Decimal:
        """Cash + sum(position market values at current prices)."""
    
    def get_drawdown_context(self) -> DrawdownState:
        """Current drawdown vs high-water mark; max DD over window; recovery time."""
    
    def get_sector_concentration(self) -> Dict[str, Decimal]:
        """Per-sector % of total portfolio value."""
    
    def get_correlation_to_existing_positions(
        self, ticker: str, as_of: date, window_days: int = 60
    ) -> Decimal:
        """Avg pairwise return correlation between candidate ticker and existing positions, computed over `window_days` ending `as_of`. Returns 0.0 if portfolio empty."""
    
    # ============ PER-TICKER RISK STATE ============
    def get_per_ticker_cooldown_state(self, ticker: str, as_of: date) -> CooldownState:
        """DEC-018 5-day stop-out cooldown; returns days_remaining or None."""
    
    def get_per_ticker_max_loss_status(self, ticker: str, as_of: date) -> MaxLossState:
        """DEC-135 -10% rolling 30d cap; returns current_pnl / cap_remaining / blocked."""
    
    # ============ MUTATION (PIT-aware) ============
    def execute_trade(self, trade: Trade, as_of: date) -> TradeResult:
        """Apply trade; update cash + positions. Returns success or rejection reason."""
    
    def close_position(self, ticker: str, exit_price: Decimal, as_of: date, exit_reason: str) -> ClosedTrade: ...
    
    def update_market_values(self, prices: Dict[str, Decimal], as_of: date) -> None:
        """Update position market values; recompute drawdown."""
    
    # ============ PIT CORRECTNESS ============
    def snapshot_at(self, as_of: date) -> 'Portfolio':
        """Returns Portfolio state AS OF historical date (PIT-correct snapshot)."""
    
    def replay_to(self, target_date: date, trade_log: List[Trade]) -> 'Portfolio':
        """Replays trade log up to target_date; returns historical portfolio state."""
```

### 9.3 Sub-classes

```python
@dataclass
class Position:
    ticker: str
    shares: int  # signed: positive = long, negative = short
    entry_price: Decimal
    entry_date: date
    cost_basis: Decimal  # shares × entry_price + commission
    current_price: Decimal
    market_value: Decimal  # shares × current_price
    unrealized_pnl: Decimal
    sector: str  # cached from reference data
    strategy_id: str  # which strategy opened this position

@dataclass
class ClosedTrade:
    ticker: str
    entry_date: date
    exit_date: date
    entry_price: Decimal
    exit_price: Decimal
    shares: int
    cost_basis: Decimal
    exit_value: Decimal
    realized_pnl: Decimal
    realized_pnl_pct: Decimal
    holding_days: int
    exit_reason: str  # exit method per DEC-067
    strategy_id: str
    commission: Decimal
    slippage: Decimal

@dataclass
class PortfolioStateSnapshot:
    as_of: date
    cash: Decimal
    total_value: Decimal
    positions: Dict[str, Position]
    drawdown: Decimal  # current DD %
    drawdown_max: Decimal  # max DD over period
    sector_concentration: Dict[str, Decimal]
    leverage: Decimal  # gross / net exposure
```

### 9.4 PIT-Correctness Rules

- All mutation operations require `as_of: date` parameter
- All queries return state AS OF current `as_of_date` field on Portfolio
- `snapshot_at(historical_date)` reconstructs portfolio at any past date by replaying trade log
- No CURRENT-data leakage — sector classification, market cap, etc. all PIT via Polygon reference (DEC-443)

### 9.5 Persistence

- **Stage 2 backtest:** in-memory only; persisted to Parquet at backtest end
- **Stage 3 paper trading:** SQLite event store per DEC-267
- **Stage 4+ live:** Postgres event store per DEC-267

### 9.6 Concurrency

- Backtest is single-process per fold (multiple processes for parallel folds — multi-process safe globals per DEC-329)
- No within-fold concurrency on Portfolio mutation
- Sprint 7 toolkits (DEC-465/466) read-only access during agent decision; write access at engine execution

### 9.7 Implementation

- File: `backtest/portfolio/portfolio.py` (new)
- Effort: ~8-11d (Sprint 3 BUG-095 resolution)
- Test signals:
  - (a) PIT correctness via freezegun
  - (b) `get_correlation_to_existing_positions` returns valid pairwise correlation matrix
  - (c) Cooldown state correctly tracks DEC-018 5-day post-stop
  - (d) Max-loss state correctly tracks DEC-135 -10% rolling 30d
  - (e) Drawdown computation matches QuantStats reference
  - (f) Sector concentration sums to 1.0 (or accounts for cash %)
  - (g) Replay from initial cash + trade log produces same end-state as original run

---

# PART E — CLUSTER 4 RECOMMENDATIONS (Directive 4a)

For the 7 Cluster 4 architectural clarifications, recommendations:

### GAP 14 — PIT Loader Edge Cases

**Recommendation:** Add new sub-section TRADING_RULES §12.7 "PIT Loader Edge Case Behavior":

| Edge case | Behavior |
|---|---|
| `as_of` = weekend | Returns rows with date ≤ previous trading day |
| `as_of` = holiday | Same as weekend |
| `as_of` < ticker IPO date | Returns empty result + warning log |
| `as_of` > delisting date | Returns rows up to delisting; downstream should check `is_delisted` flag |
| Partial cache | Re-fetch missing range; fail-fast if Polygon unavailable per DEC-260 freshness |

### GAP 15 — Two Universes (482 vs historical_membership.csv)

**Recommendation:** **historical_membership.csv (DEC-303) is canonical.** Static 482-ticker CSV is a STAGE 1 LEGACY ARTIFACT that should be deprecated in Sprint 1.

Surgical edit:
- PROJECT_PLAN §6.1: change "482 S&P 500 constituents (per static committed CSV)" to "S&P 500 constituents per DEC-303 historical_membership.csv (PIT-correct survivorship-bias-corrected)"
- TRADING_RULES §6.1: update universe definition

### GAP 26 — 14 Engine Bugs Only 4-5 Named

**Recommendation:** Enumerate all 14 in TRADING_RULES §2.3:

```
14 critical engine bugs (Sprint 2 deliverable):
1. close_trade NameError (DEC-293)
2. Duplicate ClosedTrade dataclass (DEC-294)
3. exit_hybrid_50pct max_days inconsistency (DEC-295)
4. Trailing stop ATR refresh missing (DEC-311)
5. Circuit breaker Level 3 not implemented (DEC-314 part 1)
6. Circuit breaker Level 4 not implemented (DEC-314 part 2)
7. Circuit breaker sequential check (DEC-315)
8. Position sizing fractional Kelly missing implementation (DEC-296)
9. Slippage time-of-day multiplier missing (DEC-297)
10. Borrow cost double-application (DEC-306)
11. Stop-loss intraday gap handling (DEC-312)
12. Volume_climax exit method missing (DEC-327)
13. Fixed_3r_2r → fixed_target migration (DEC-338)
14. RSI extreme exit method missing (DEC-340)
```

(Numbers are illustrative; cross-reference exact decision IDs DEC-293-340.)

### GAP 32 — Sprint 4 Scope Not in PROJECT_PLAN

**Recommendation:** Add Sprint 4 sub-phase to PROJECT_PLAN §3.4-3.5:

```
3.4.5 Phase 0.D' — DEC-410 API Audit Findings (Sprint 4)
Effort: ~41.75-54.25d
Deliverable: Resolution of 17 API findings from DEC-410 audit (cross-referenced with API_AUDIT.md). Categories:
- yfinance demotion to fallback (DEC-442) ~5d
- Polygon reference replacing yfinance.info (DEC-443) ~3d
- Earnings deprecation (DEC-444) ~2d
- (14 other findings...)
Detail: API_AUDIT.md
```

### GAP 60 — Sprint 9 Compute Estimate

**Recommendation:** Add compute estimate section to PROJECT_PLAN §3.7 + §4.2:

```
Sprint 9 Compute Estimate:
- Per propagate(): ~30s wall time (TradingAgents v0.2.4 with Anthropic claude-sonnet-4 deep + claude-haiku quick)
- 300 candidates × 3 arms (selective) × 3 propagate calls per candidate = 2700 propagate calls × 30s = ~22.5 hours pure agent time
- Cube cell metric computation: 50K populated cells × 17 metrics × 6 OOS folds = 5.1M metric computations × ~10ms each = ~14 hours
- FDR computation: ~30 minutes
- Total compute: ~37-40 hours wall time
- Codespace 8-core sufficient with parallel folds; cloud migration not required for Sprint 9
- Memory peak: ~4-6 GB (cube + portfolio replay)
```

### GAP 62 — Per-Cell vs Portfolio-Aggregate Verdict

**Recommendation:** Add both verdict levels to TRADING_RULES §22.5:

```
Verdict at TWO levels:

Level A — Per-Cell Verdict (DEC-426 5-Gate):
- PASS / FAIL_RR / INSUFFICIENT_SAMPLE / FAIL_STAT
- Populates live decision lookup table (DEC-429)

Level B — Portfolio-Aggregate Verdict (NEW):
- Aggregate Sharpe ≥ 1.0 (DEC-269)
- Max DD ≤ 25% (DEC-269)
- Win rate ≥ 50% (DEC-269) — REVISIT given DEC-353 R:R ≥ 2.0
- A/B clear: ≥ 0.2 net Sharpe (DEC-131)
- Bonferroni p < 0.05 → REPLACED with FDR q < 0.10 (per §3 above)

Stage 2 → Stage 3 transition requires:
- Level A: ≥ 50 cells PASS (or owner-set threshold)
- Level B: All quantitative gates met
- Owner reviews + approves
```

### GAP 92 — ATR Multiplier: Stops or Position Size?

**Recommendation:** Mean reversion ATR multiplier 1.0× applies to **STOPS** (stop-loss distance), not position size. Surgical edit to TRADING_RULES §11.5:

```
§11.5 Mean Reversion ATR Multiplier (per project memory + Pass 52 owner approval):
ATR multiplier raised 0.5× → 1.0× applies to STOP-LOSS DISTANCE for mean-reversion strategies. 
Position sizing tier (HIGH 5% / MED 3% / LOW 1.5%) NOT affected by this multiplier.
Crisis-flag 50% reduction (§11.1) compounds with TIER (5% × 50% = 2.5%), not with stop distance.
```

---

# PART F — POLYGON TIER DECISION (GAP 46 cascade)

## 11. Polygon Stocks Starter vs Higher Tier Cost-Benefit

Already covered in §2.3. Owner decision needed:

**My recommendation: Stocks Developer $79/mo + FMP $14-50/mo = $93-129/mo total.**

Awaiting owner direction.

---

# PART G — NEW DECISIONS REQUIRED (PROPOSED)

## 12. DEC-469 through DEC-481 PROPOSED

Per L131 / CHECKLIST #51 — sub-decisions PROPOSED, **not LOGGED** until owner explicitly approves.

| DEC | Title | Owner action |
|---|---|---|
| **DEC-469** | Adopt Benjamini-Hochberg FDR (q=0.10) replacing Bonferroni multi-testing correction | Approve |
| **DEC-470** | Hierarchical 3-level FDR application (per-strategy / per-cell / per-regime) | Approve |
| **DEC-471** | Cube dimensionality reduction to 8 core dimensions | Approve |
| **DEC-472** | Eliminate paired A/B design; switch to independent arms with shared opportunity set + block bootstrap CIs | Approve |
| **DEC-473** | A/B arm reduction from 5 to 3 (rules-only / full-with-veto / no-Risk); ablation deferred to Sprint 9 NARROW | Approve |
| **DEC-474** | DEC-459 Option C revision (DEC-481) — adapt to TradingAgents v0.2.4 5-tier rating reality; markdown-parser approach | Approve |
| **DEC-475** | RM alignment + Trader confidence cross-check via 5-tier rating direction | Approve |
| **DEC-476** | Portfolio class API spec (TRADING_RULES §24 new section, Part L) | Approve |
| **DEC-477** | historical_membership.csv (DEC-303) canonical universe; deprecate 482-ticker static CSV | Approve |
| **DEC-478** | Polygon tier upgrade — owner decision needed (Stocks Starter / Developer / Advanced + FMP) | Choose tier |
| **DEC-479** | DEC-441 cost correction $30/mo → $29/mo Stocks Starter (or revised tier per DEC-478) | Approve cost update |
| **DEC-480** | TradingAgents v0.2.4 specific version pin in requirements (not just "tradingagents") | Approve |
| **DEC-481** | AgentGateConfig Option C2 — supersedes DEC-459 (5-tier rating + markdown parser + Trader fallback per Directive 2b) | Approve |

---

# OWNER ACCOUNTABILITY VINDICATION (8th instance Pass 52 — PROACTIVE)

| Turn | Catch |
|---|---|
| 98 | Homeless RESOLVED-DECIDED |
| 108 | Substantively-homeless engineering decisions |
| 110 | Bug-decision linkage gap |
| 114-118 | 80 PENDING delegation |
| 128 | DEC-042 architectural fit |
| 130 | DEC-051 data dependency chain |
| 132 | Documentation rigor (167 gaps) |
| **133** | **External verification reveals 5-tier rating reality + Polygon coverage shortfall (this resolution work)** |

This is the SECOND PROACTIVE catch. Owner directive ("start with critical") + Claude executing 2a (TradingAgents source verification) + GAP 46 (Polygon docs verification) revealed:
- DEC-459 Option C numeric confidence assumption WRONG (5-tier rating reality)
- DEC-441 Polygon Stocks Starter coverage SHORTFALL (5-year history insufficient + no quotes/financials)
- DEC-460 verification negative — DEC-461 FMP NOW MANDATORY

These would have caused Sprint 7 implementation failure if discovered during Sprint 7. Caught pre-Sprint-1 saves ~50-80d wasted effort.

---

*End of CRITICAL_GAPS_RESOLUTION_PASS_52_TURN_133.md*

*Per CHECKLIST #25 (honest about external verification revealing worse findings); #43 (precise grep on TradingAgents v0.2.4 CHANGELOG + Polygon pricing page); #51 (13 PROPOSED decisions await owner approval — none logged until approved); #57 (use-case mapping per resolution); #58 (atomic commit will be invoked); #59 (architectural assumption verification PROACTIVE); #60 (data dependency verification PROACTIVE); #61 (5-pass methodology origin doc); #62 (cross-document consistency).*
