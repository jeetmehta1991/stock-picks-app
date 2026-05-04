# PROJECT HANDOFF — Stock Picks & Automated Trading System

**Date created:** May 4, 2026
**Current commit on main:** `2ed20c04`
**Owner:** Jeet Mehta (`jeetmehta1991` on GitHub)
**Repo:** https://github.com/jeetmehta1991/stock-picks-app

**Purpose of this document:** Comprehensive context dump for a new Claude chat. Owner is uploading this directly to a fresh session because the prior session became slow due to accumulated context. Read this end-to-end before responding to anything.

---

## 1. PROJECT OVERVIEW

### 1.1 What is this project?

A comprehensive algorithmic trading platform for swing trading US equities. The owner's philosophy: **high-return performance with medium-high risk tolerance**, explicitly accepting drawdowns in pursuit of higher ROI. Owner buys dips in volatile and crisis markets.

### 1.2 Stages

- **Stage 1 (COMPLETE):** Daily Python script `fetch_stocks.py` fetching US top gainers and TSX quotes via Alpha Vantage; outputs dark-themed `index.html` updated daily via GitHub Actions.
- **Stage 2 (ACTIVE — current focus):** Full backtesting + automated trading engine. ~1015 instruments (S&P 500 + R1000 + NASDAQ 100), 6 market regimes, ~119 strategies, multi-signal universe (technical / smart money / options / macro / sentiment).
- **Stage 3+ (FUTURE):** Paper trading → small-live → full-live transitions.
- **Out of scope:** Intraday trading (separate future project).

### 1.3 Critical working principle (NON-NEGOTIABLE)

**Every filter, threshold, position sizing rule, and strategy parameter change requires the owner's explicit approval before implementation.** Claude's role is to provide recommendations only, never to make unilateral strategy or rule decisions. Owner has corrected Claude firmly multiple times when this boundary was crossed.

### 1.4 Tools & infrastructure

| Layer | Tool |
|---|---|
| **Dev environment** | VS Code on Windows laptop (was: GitHub Codespaces "vigilant system" — switched May 4, 2026 Pass 53) |
| **Language** | Python 3.11+, Parquet via pyarrow, GitHub Actions |
| **Version control** | GitHub `jeetmehta1991/stock-picks-app` |
| **Documentation** | Plain-English markdown in repo (PROJECT_PLAN.md, CLAUDE.md, etc.) — Word docs deprecated |
| **Data APIs** | Alpha Vantage (Stage 1 only), Polygon Stocks Starter $29/mo (just subscribed), Quiver paid (~$50-100/mo, already active), FRED (free), AAII + CNN F&G scrapes (free), planned: SEC EDGAR (free, Sprint 4) |
| **AI overlay** | TradingAgents v0.2.4 LangGraph framework (Phase 1B; not Phase 1A) |

---

## 2. CURRENT STATE — WHERE WE ARE RIGHT NOW

### 2.1 Pass 53 work completed (this session)

The current Pass 53 multi-turn session has accomplished the following commits on main, in order:

1. `0d5182c2` — Phase 1A restoration across 9 canonical docs
2. `deb75c7d` — Phase 1A dependency sweep across 14 dependency docs
3. `d9836f12` — Sprint 1 pre-flight batch approval — 11 owner decisions logged (DEC-477/478/479/482/483/484/485/486/487/488/490)
4. `b892dc26` — Adversarial audit migration (167 GAPs + 10 Stage 2 Blockers tracking + DEC-469-481 PROPOSED added to AUDIT_INDEX) + VS Code infrastructure update across 7 docs
5. `effa1f84` — Polygon prefetch scripts created + L143 + CHECKLIST #64 codified
6. `2ed20c04` — Small-scale 5-ticker test infrastructure (argparse + verification script)

**Current decision counts:**
- Total decisions: 494 (was 472 pre-Pass-53)
- RESOLVED-DECIDED: 379
- PROPOSED: 13 (DEC-469-481 cluster — Sprint 7 deliverables, NOT Sprint 1 blockers)

### 2.2 Owner subscriptions confirmed active (May 4, 2026)

| Service | Cost | Status | Where key lives |
|---|---|---|---|
| Polygon Stocks Starter | $29/mo (USD; billed by Massive.com Inc., Polygon's parent rebranded) | Active | `.env` at repo root: `POLYGON_API_KEY` (key starts `JikWQlXo...`) |
| Quiver paid tier | ~$50-100/mo | Active (per DEC-450/452) | `.env`: `QUIVER_API_KEY` |
| FRED | free | Active | `.env`: `FRED_API_KEY` |

### 2.3 What's NOT yet done

The major in-flight item: **Polygon prefetch is partially built but not yet executed at full scale.**

Specifically:
- ✅ Polygon API verified working (smoke test passed 14/14 endpoints)
- ✅ Prefetch scripts written and committed
- ✅ Small-scale 5-ticker test infrastructure built and committed
- ⏳ **NEXT STEP:** Owner runs 5-ticker test on laptop (~10-15 min wall) — has not yet been executed
- ⏳ Owner pastes test output back for Claude analysis
- ⏳ Decision: proceed to full 484-ticker prefetch (~4-7 hours wall) only after small-scale test verified
- ⏳ Quiver prefetch deferred to tomorrow per owner directive
- ⏳ Universe build (DEC-477 historical_membership.csv + R1000 + NDX year-grain) deferred to tomorrow

---

## 3. IMMEDIATE NEXT STEPS — WHAT THE NEW CHAT SHOULD DO FIRST

### 3.1 Read these files in the repo

The new chat should `git pull` and read the following canonical docs to orient:

1. **`CLAUDE.md`** — short context document for Claude Code (~200 lines)
2. **`PROJECT_PLAN.md`** — main project plan
3. **`DETAILED_PROJECT_PLAN.md`** — Pass 53 implementation playbook (Parts 0-12)
4. **`CHECKLIST.md`** — methodology rules (#64 is most recently added)
5. **`LEARNINGS.md`** — accumulated learnings (L143 most recent)
6. **`AUDIT_INDEX.md`** — master decision table (494 rows, mostly RESOLVED-DECIDED)
7. **`scripts/SPRINT1_POLYGON_PREFETCH_README.md`** — how the prefetch works
8. **`PASS_53_PRIORITIES.md`** — current pass's priority list

### 3.2 What the owner needs to do next on his laptop

```bash
cd ~/Github/stock-picks-app/stock-picks-app
git pull origin main

# Run the 5-ticker test (should take 10-15 min)
bash scripts/run_polygon_5ticker_test.sh

# Verify the parquet output
python scripts/verify_polygon_test_output.py
```

Then paste both outputs back to Claude.

### 3.3 What Claude should do next

When owner pastes the test output:

1. Review the wall time — flag if significantly different from 10-15 min target
2. Review the verification output — every `✓` or `✗` should be examined
3. Especially look for:
   - AAPL news >1000 articles (validates pagination)
   - GOOGL 2022 split present (validates corp actions return real data)
   - Sentiment field populated >30% on news (validates Polygon Stocks Starter actually provides sentiment)
   - No 0-byte parquet files
   - Schema integrity end-to-end
4. If all checks pass, ask owner whether to proceed to full 484-ticker prefetch
5. If any checks fail, do NOT recommend full prefetch — investigate the failure first

---

## 4. CRITICAL CONTEXT — RECENT PROCESS FAILURES (KEEP IN MIND)

### 4.1 The "decision-state vs artifact-state" gap (5-instance pattern)

**Owner has caught Claude 5 times** with the same failure mode: Claude marks an architectural decision as "RESOLVED-DECIDED" in AUDIT_INDEX without verifying the physical artifacts (files, data, credentials) referenced by that decision actually exist on disk.

The 5 instances:
1. Pass 52 turn 128 — DEC-042 architectural fit
2. Pass 52 turn 130 — DEC-051 data dependency chain
3. Pass 53 — Phase 1A omission (silently dropped from PROJECT_PLAN)
4. Pass 53 — DEC-469-481 phantom labels (referenced as PROPOSED but not in AUDIT_INDEX)
5. Pass 53 (this session) — Universe artifacts referenced by RESOLVED-DECIDED DECs do not exist on disk

**5/5 caught reactively by owner**, 0/5 caught proactively by Claude's audit methodology.

**Codification (still being tested):** CHECKLIST #64 added Pass 53 — sprint readiness requires BOTH decision-state AND artifact-state verification. L143 codifies the methodology gap.

**For new chat:** before claiming any sprint is "ready" or "unblocked", run `ls`/`wc -l`/`head` checks on the actual files referenced. The verification is a 30-second check that has been repeatedly skipped.

### 4.2 The owner's stated mistrust position

The owner has explicitly stated: **"You should mistrust 'Sprint X is ready' claims unless backed by artifact-verification evidence."**

For new chat: do not claim readiness without showing `ls -la` + `wc -l` + smoke test output as evidence. If Claude makes a sprint-ready claim without that evidence, owner will (rightly) push back.

### 4.3 The session became slow

This handoff document exists because the prior session accumulated too much context (large file reads via `cat AUDIT.md`, repeated verification commands dumping thousands of lines, mid-session AUDIT.md updates). New chat should:

- Use `wc -l` instead of `cat` when only count matters
- Use `grep -c` instead of full grep output
- Use `view` with line ranges instead of full file reads
- Avoid mid-session AUDIT.md / LEARNINGS.md writes — batch documentation updates to end of session
- Trust earlier-session commits without re-verifying via re-reading

---

## 5. KEY DECISIONS LOGGED THIS SESSION (Pass 53)

### 5.1 Sprint 1 pre-flight decisions (RESOLVED-DECIDED)

| DEC | Description |
|---|---|
| DEC-477 | `data/universe/historical_membership.csv` is canonical PIT universe source (day-grain S&P 500 add/delete dates); deprecates static survivorship-biased CSV |
| DEC-478 | Polygon Stocks Starter $29/mo confirmed (not Developer $79 or higher) — 5y history, unlimited API calls, 15-min delayed, no quotes/financials |
| DEC-479 | Cost correction $30/mo → $29/mo |
| DEC-482 | Walk-forward methodology revised: expanding window 2y+/6mo OOS × 5 folds within 5y Polygon Stocks Starter window. SUPERSEDES DEC-109 |
| DEC-483 | Universe expansion: T1a S&P 500 (~503) + T1b R1000 (~497 net new, year-grain PIT) + T1c NDX (~15 net new, year-grain PIT) = ~1015 total |
| DEC-484 | SEC EDGAR direct parsing replaces FMP for fundamentals (Sprint 4); Phase 1A skips 2 strategies needing full financials. SUPERSEDES DEC-461 |
| DEC-485 | Earnings transcripts dropped from Stage 2 scope (not available free at scale; FMP free tier insufficient) |
| DEC-486 | Phase 1A baseline = rules-only (no agents); Phase 1A-α = scale-validation cube |
| DEC-487 | Phase 1A-α single-arm cube populator (rules-only, no A/B framework) |
| DEC-488 | Phase 1A-β scale-validation methodology |
| DEC-490 | Phase 1A explicitly skipped strategies: `buyback_announcements` (needs SEC EDGAR), `guidance_driven_momentum` (needs transcripts) |

### 5.2 Sprint 7 Sprint-blocker decisions (PROPOSED — awaits owner approval)

These are NOT Sprint 1 blockers. They block Sprint 7 (statistical methodology + agent overlay implementation) which is much later.

| DEC | Description |
|---|---|
| DEC-469 | Benjamini-Hochberg FDR (q=0.10) replacing Bonferroni multi-testing correction |
| DEC-470 | Hierarchical 3-level FDR application (per-strategy / per-cell / per-regime) |
| DEC-471 | Cube dimensionality reduction 17+→8 dims |
| DEC-472 | Eliminate paired A/B; independent arms + block bootstrap CIs |
| DEC-473 | A/B arm reduction 5→3; ablation deferred to Sprint 9 NARROW |
| DEC-474 | DEC-459 Option C → DEC-481 Option C2 supersession (5-tier rating reality) |
| DEC-475 | RM/Trader cross-check via 5-tier rating direction |
| DEC-476 | Portfolio class API spec (TRADING_RULES §24 NEW Part L) |
| DEC-480 | TradingAgents v0.2.4 specific version pin |
| DEC-481 | AgentGateConfig Option C2 (5-tier rating + markdown parser + Trader fallback) |

These can be approved as a batch later (before Sprint 7 begins). They don't gate Sprint 1 prefetch.

---

## 6. WHAT'S BEEN BUILT THIS SESSION

### 6.1 Polygon prefetch scripts (committed in `effa1f84`)

| File | Purpose | Wall time est. |
|---|---|---|
| `scripts/smoke_test_polygon.py` | Verify 5 endpoints × 5 tickers work | ~5 min |
| `scripts/prefetch_polygon_ohlcv_daily.py` | Daily OHLCV 5y for universe | ~30-60 min for 484 |
| `scripts/prefetch_polygon_reference.py` | Ticker reference + CIK | ~5-10 min for 484 |
| `scripts/prefetch_polygon_corp_actions.py` | Splits + dividends paginated | ~5-10 min |
| `scripts/prefetch_polygon_news.py` | News + sentiment 5y | ~3-5 hours for 484 |
| `scripts/run_polygon_prefetch_all.sh` | Orchestrator | ~4-7 hours total |
| `scripts/SPRINT1_POLYGON_PREFETCH_README.md` | Documentation | — |

### 6.2 Small-scale test infrastructure (committed in `2ed20c04`)

| File | Purpose |
|---|---|
| `scripts/run_polygon_5ticker_test.sh` | Test orchestrator (AAPL/MSFT/GOOGL/JPM/XOM, ~10-15 min) |
| `scripts/verify_polygon_test_output.py` | ~30-check parquet inspection (file counts, schema, content sanity, pagination evidence, checkpoint validity) |

All 4 prefetch scripts now have argparse with `--limit-tickers N` and `--tickers SYM1 SYM2` flags so the same code path is used for both test and production.

### 6.3 Methodology codifications added this session

| File | Addition |
|---|---|
| `CHECKLIST.md` | #64 — sprint readiness requires BOTH decision-state AND artifact-state verification |
| `LEARNINGS.md` | L143 — decision-state vs artifact-state are different things (5-instance pattern documented) |
| `AUDIT.md` | Pass 53 process-failure entry; 167 GAP tracking table; 10 Stage 2 Blockers tracking; DEC-469-481 individual entries per template |
| `AUDIT_INDEX.md` | DEC-469-481 PROPOSED rows formally added to master decision table |

---

## 7. WHAT WAS DEFERRED (DO NOT FORGET)

The owner approved deferring these items per Pass 53 "we will do 3 and 4 later":

1. **Codespace allowlist verification** (item 3) — moot since owner switched to local VS Code
2. **BUG-007 verification** (item 4) — Sprint 6.5 blocker, NOT Sprint 1 blocker

The owner also approved deferring to **tomorrow's session**:

1. **Universe build** — DEC-477 `historical_membership.csv` (day-grain PIT) + DEC-483 T1b Russell 1000 + T1c NASDAQ 100 (year-grain PIT)
2. **Supplementary Polygon prefetch** for ~531 net-new tickers (T1b + T1c + historical-S&P-delisted)
3. **Quiver paid endpoint prefetch** — all 13 endpoints per DEC-450 (~14-18 GB; ~22-32 hours wall)

These are tomorrow's work. Tonight's scope is ONLY Polygon prefetch on existing 484 sp500_tickers.csv — explicit Path A pragmatic choice with survivorship-bias acknowledgment.

---

## 8. GIT PERSONAL ACCESS TOKEN (PAT) — ACTUAL HISTORY

### 8.1 What was actually set up

On **April 27, 2026** (in a prior chat, before this Pass 53 session), the owner generated a GitHub Personal Access Token with these specifications:

- **Type:** Classic PAT
- **Name:** `claude-sync`
- **Expiration:** No expiration
- **Scope:** `repo` (full control of repositories)
- **Generated via:** github.com on mobile → Settings → Developer settings → Personal access tokens → Tokens (classic)

The token was originally created so Claude (in GitHub Codespaces at the time) could push directly to a `claude-updates` branch on the owner's behalf without manual git push from the owner.

### 8.2 The token was pasted into chat at creation time

**Security note for the new chat:** the token value was pasted into the prior conversation when it was generated. This means it has been visible in conversation history to any subsequent Claude session that searches past chats. Treat as exposed.

### 8.3 What changed during Pass 53 (May 4, 2026)

The owner switched from GitHub Codespaces to **local VS Code on a Windows laptop** during this Pass 53 session. The PAT migration happened **implicitly**:

- Windows Credential Manager picked up the credentials (likely cached during an earlier `git push` prompt on the laptop before this session)
- All git pushes during this Pass 53 session (commits `0d5182c2`, `deb75c7d`, `d9836f12`, `b892dc26`, `effa1f84`, `2ed20c04`) succeeded silently without re-auth prompts
- This confirms the credentials are stored in Windows Credential Manager on the owner's laptop

The owner's path going forward is local-only: PAT lives in Windows Credential Manager, accessed automatically by Git Bash + VS Code on the laptop.

### 8.4 Recommended action — rotate the exposed PAT

The PAT being in conversation history is a real security exposure. The new chat should encourage the owner to:

1. **Revoke the existing `claude-sync` PAT** at https://github.com/settings/tokens (find `claude-sync` in the list, click Delete)
2. **Generate a fresh classic PAT** with the same scope (`repo`), preferably with an expiration date this time (90 days is standard)
3. **Store the new PAT only in Windows Credential Manager** — do NOT paste into chat:
   ```bash
   git config --global credential.helper manager
   git push origin main
   # Prompt: username = jeetmehta1991; password = paste new PAT
   # After this, all pushes are silent
   ```
4. The old PAT being in chat history is unrecoverable (can't be unsent), but revoking it kills the token; the leaked string becomes useless

### 8.5 What Claude does NOT have

Claude in the new chat does **not** have direct access to push to the repo. The PAT lives on the owner's laptop. When Claude makes code changes during the new session, the **owner runs `git push`** (or it pushes silently because credentials are cached). Claude's role is to write code, commit messages, and rationale — the owner controls the actual push to GitHub.

This is how the current Pass 53 sessions have worked: Claude writes scripts in a sandbox, commits them via the sandbox's git (which has its own credential setup separate from the owner's laptop), and the owner pulls the commits to their laptop with `git pull origin main`. Claude never touches the owner's PAT directly.

### 8.6 Summary for the new chat

| Question | Answer |
|---|---|
| Does the owner have a PAT? | Yes — `claude-sync`, classic, `repo` scope, no expiration, generated April 27, 2026 |
| Is it stored anywhere on the laptop? | Yes — Windows Credential Manager (implicit cache; pushes work silently) |
| Is it exposed? | Yes — was pasted into a prior chat in plaintext |
| Should it be rotated? | Yes — recommended action at next opportunity |
| Does the new chat need the PAT value? | NO — never ask the owner to paste it |
| What does the new chat do for git operations? | Write code; commit in sandbox; owner pulls + pushes from laptop (silent due to cached credentials) |

---

## 9. METHODOLOGY RULES (REFERENCE)

These are CHECKLIST items the new chat should respect. Most relevant:

| # | Rule | Why it matters |
|---|---|---|
| #25 | Honest accounting; don't minimize failures or dress up gaps | Owner has caught 5 instances of pattern-failure; trust depends on honesty |
| #43 | Verify before claiming; show evidence (`ls`, `wc -l`, `head`) | Owner mistrust position; need concrete proof |
| #51 | Surface options before mass execution; don't pick for the owner | Owner approves all decisions |
| #58 | Atomic commits across related files | Don't leave repo in half-state |
| #59/#60 | Architectural assumption + data dependency verification | Where the 5-instance pattern emerged |
| #61 | Adversarial 5-pass methodology | How major reviews happen |
| #62 | Cross-document consistency | Decisions referenced across docs must match |
| #63 | Archive comparison in audits | Pass 53 added to catch silent omissions during refactoring |
| #64 (NEW) | Sprint readiness requires BOTH decision-state AND artifact-state verification | The pattern-failure codification |

---

## 10. PROJECT PHASES (FOR CONTEXT)

### 10.1 Stage 2 phases

| Phase | Description | Status |
|---|---|---|
| Phase 0.A — Polygon Foundation | Sprint 1 prefetch + cache infrastructure | IN PROGRESS (this session) |
| Phase 0.B — Portfolio Class | Sprint 3 — DEC-476 PROPOSED spec | BLOCKED on owner approval of DEC-476 |
| Phase 0.C — Engine bug fixes Tier A | Sprint 2 — X53 batch | NOT STARTED |
| Phase 0.D — ICT/SMC primitives | Future sprint | NOT STARTED |
| Phase 0.E — Catch-mechanism + hygiene | Sprint 6 | NOT STARTED |
| Phase 1A — Rules-only baseline (no agents) | Sprint 6.5 | NOT STARTED — DEC-486 |
| Phase 1A-α — Scale-validation cube | Sprint 6.5 | NOT STARTED — DEC-487 |
| Phase 1A-β — Scale-validation methodology | Sprint 6.5 | NOT STARTED — DEC-488 |
| Phase 1B-α — Full A/B with agent overlay | Sprint 9 | BLOCKED on Sprint 7 (DEC-469-481 cluster) |
| Phase 1B+ — Subsequent expansions | Sprint 10+ | FAR FUTURE |

### 10.2 Sprints

| Sprint | Phase | Effort estimate | Status |
|---|---|---|---|
| Sprint 1 | Phase 0.A Polygon Foundation | ~25-35 days | IN PROGRESS |
| Sprint 2 | Engine bug fixes Tier A (X53 batch) | TBD | NOT STARTED |
| Sprint 3 | Portfolio Class (Phase 0.B) | ~5-7 days | BLOCKED on DEC-476 |
| Sprint 4 | SEC EDGAR fundamentals + financials cache (DEC-484) | ~3-5 days | NOT STARTED |
| Sprint 5 | Universe management (Tier 2 + Tier 3) | ~5-7 days | NOT STARTED |
| Sprint 6 | Catch-mechanism + hygiene | TBD | NOT STARTED |
| Sprint 6.5 | Phase 1A run | TBD | NOT STARTED |
| Sprint 7 | Statistical methodology + A/B + custom toolkits | TBD | BLOCKED on DEC-469-481 |
| Sprint 8 | Strategy categories | TBD | NOT STARTED |
| Sprint 9 | Phase 1B-α run | TBD | NOT STARTED |

---

## 11. HOW TO OPEN A NEW CHAT EFFICIENTLY

When the owner uploads this document to a new chat, the new Claude should:

1. **Read this entire handoff document first** before responding
2. **Acknowledge** the project state, recent process failures, and tonight's immediate next step
3. **Ask** the owner to run the 5-ticker test and paste output back (or proceed with whatever the owner directs)
4. **Don't repeat** the file-reading mistakes of the prior session — use targeted commands, not full file dumps
5. **Don't auto-trust** smoke-test results or claim "Sprint X ready" without artifact-verification evidence

### 11.1 First message template the new chat should use

> Read your handoff. Project state: Pass 53 active; Polygon prefetch scripts written and committed (`2ed20c04`); 5-ticker test infrastructure ready but not yet executed. Decisions logged: 494 (379 RESOLVED-DECIDED, 13 PROPOSED). Owner has caught 5 instances of decision-state-vs-artifact-state pattern; CHECKLIST #64 codifies the fix.
>
> Immediate next step: owner runs `bash scripts/run_polygon_5ticker_test.sh` followed by `python scripts/verify_polygon_test_output.py` on laptop, pastes output back for analysis.
>
> Ready when you are.

This is short, accurate, and signals to the owner that context is loaded without re-dumping everything.

---

## 12. APPENDIX — RECENT KEY FILES (DOWNLOAD AND READ)

When the new chat starts, these are the files most relevant to tonight's work:

```
scripts/run_polygon_5ticker_test.sh           # what owner runs next
scripts/verify_polygon_test_output.py         # validates test output
scripts/smoke_test_polygon.py                 # already passed 14/14
scripts/prefetch_polygon_ohlcv_daily.py       # production daily OHLCV
scripts/prefetch_polygon_reference.py         # production reference
scripts/prefetch_polygon_corp_actions.py      # production corp actions
scripts/prefetch_polygon_news.py              # production news
scripts/SPRINT1_POLYGON_PREFETCH_README.md    # workflow doc
CHECKLIST.md                                  # #64 most recent
LEARNINGS.md                                  # L143 most recent
PASS_53_PRIORITIES.md                         # current pass priorities
```

`AUDIT_INDEX.md` (510 rows decision table) and `AUDIT.md` (~26,000 lines) are large reference files — do NOT `cat` them. Use `grep -c "DECISION-XXX"` or `view` with specific line ranges only when needed.

---

## 13. END OF HANDOFF

**Last commit on main:** `2ed20c04` (May 4, 2026 06:16)

**Pending actions:**
1. Owner runs 5-ticker test on laptop
2. Owner pastes test output to new chat
3. New chat reviews; if all checks pass, asks owner whether to proceed to full 484-ticker prefetch
4. Owner decides; new chat executes if approved

**This handoff document is the authoritative state-of-project as of session end.**
