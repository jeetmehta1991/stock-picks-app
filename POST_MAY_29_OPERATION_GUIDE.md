# POST_MAY_29_OPERATION_GUIDE.md

**Authored:** 2026-05-20 (Batch 258)
**Audience:** Owner, post-Claude-downgrade from Max to Pro plan (May 29, 2026)
**Purpose:** Single playbook for operating the trading system with minimal Claude credits. Most operations are `python scripts/X.py` triggers; Claude sessions reserved for analysis + bug-fix only.

---

## 1. What's built and ready (zero Claude needed to RUN)

| Stage | What you can do without Claude |
|---|---|
| **Stage 2 Phase 1A-alpha** | `python scripts/run_t0_close_out.py` (merge + dashboards + commit) |
| **Stage 2 Phase 1A-beta** | `python scripts/run_phase1a.py --phase 1a-beta --tickers "$(cat scripts/_batch_t1a_N.txt)" ...` per batch + `merge_batch_outputs.py` |
| **Stage 2 1A-beta verdict** | `python scripts/extract_phase_1a_beta_winners.py` -> `winners.parquet` |
| **Stage 2 1B-alpha smoke** | `python scripts/run_phase_1b_alpha_smoke.py --dry-run` then live |
| **Stage 2 1B-alpha demo** | `python scripts/run_phase_1b_alpha_demo.py --dry-run` then live |
| **Stage 2 1B-alpha full** | `python scripts/run_phase_1b_alpha.py --include-p2 --budget-cap 150` |
| **Stage 2 T5b precompute** | `python scripts/precompute_cointegrated_pairs.py` |
| **Stage 3 daily picks** | `python scripts/run_paper_morning.py --send-email` (cron 8 AM ET) |
| **Stage 3 EOD** | `python scripts/run_paper_end_of_day.py --send-email` (cron 4 PM ET) |
| **Stage 3 dashboard refresh** | `python scripts/build_dashboard_stage_3.py` |
| **Stage 4 daily live (when ready)** | `python scripts/run_live_morning.py` (dry-run default) |
| **Stage 4 deploy** | `bash scripts/deploy_live.sh stock-picks-live` |

---

## 2. Critical day-1 setup (one-time, no Claude needed)

```bash
# Verify all dependencies installed (CI parity)
pip install -e vendored/smartmoneyconcepts/
pip install xgboost scikit-learn numba>=0.58.1

# Verify env vars for email (Stage 3)
export EMAIL_SMTP_HOST=smtp.gmail.com
export EMAIL_SMTP_USER=jeetmehta1991@gmail.com
export EMAIL_SMTP_PASSWORD=<gmail-app-password>

# Verify env vars for live (Stage 4, when activated)
export IB_USERNAME=<your-ib-username>
export IB_PASSWORD=<your-ib-password>

# Sanity: full 13-tier pyramid passes locally
python -m pytest backtest/tests/ -q
```

---

## 3. Common workflows

### 3.1 Phase 1A-alpha complete -> run T0 close-out

```bash
# After all 5 batches finish (last_run.txt files present)
python scripts/run_t0_close_out.py
#   -> merges output_phase_1a_alpha_batch_[1-5]/ into output_v2/
#   -> recomputes DSR / Bonferroni / PBO
#   -> refreshes Dashboard 2 + Dashboard 3
#   -> commits + pushes
```

### 3.2 Phase 1A-beta full-universe run

```bash
# 5-batch parallel (each batch ~3-4 days at full 1937-tkr scope)
# Use existing batch splits or regenerate

# Per batch (run 5 in parallel, e.g. via tmux/screen):
python backtest/run_phase1a.py --phase 1a-beta \
    --tickers "$(cat scripts/_batch_X.txt)" \
    --no-news --no-agents --no-git --no-walk-forward \
    --output-dir output_phase_1a_beta_batch_X

# When all 5 finish:
python scripts/run_t0_close_out.py \
    --input-pattern "output_phase_1a_beta_batch_*"
python scripts/extract_phase_1a_beta_winners.py  # -> winners.parquet
```

### 3.3 Phase 1B-alpha (winners-only, $50-150)

```bash
# Gate 1: smoke (~$3)
python scripts/run_phase_1b_alpha_smoke.py
#   -> reviews 5 P1 winners x 30 days

# Gate 2: demo (~$10)
python scripts/run_phase_1b_alpha_demo.py
#   -> 20 winners x 1 quarter

# Gate 3: FULL (~$50-150)
python scripts/run_phase_1b_alpha.py --budget-cap 150
#   -> all P1 winners across 4y
#   -> writes ab_results.parquet (3-arm verdict per combo)
```

### 3.4 Stage 3 daily paper trading

Daily cron schedule (Windows Task Scheduler OR cron):

```
0 8 * * 1-5  cd /repo && python scripts/run_paper_morning.py --send-email
0 16 * * 1-5 cd /repo && python scripts/run_paper_end_of_day.py --send-email
30 16 * * 1-5 cd /repo && python scripts/build_dashboard_stage_3.py
```

### 3.5 Stage 4 deploy (when ready)

```bash
# One-time AWS Lightsail setup (~$5-15/mo)
export AWS_REGION=us-east-1
export IB_USERNAME=...
export IB_PASSWORD=...
export EMAIL_SMTP_HOST=smtp.gmail.com
export EMAIL_SMTP_USER=jeetmehta1991@gmail.com
export EMAIL_SMTP_PASSWORD=...

bash scripts/deploy_live.sh stock-picks-live

# Daily Stage 4 (cron on Lightsail):
# 0 8 * * 1-5  python scripts/run_live_morning.py --send-email
# (Then YOU reply to approval email with pick IDs)
# 0 9 * * 1-5  python scripts/run_live_morning.py --execute-approved <IDs> --no-dry-run
```

---

## 4. When you DO need a Claude session (~1-2 sessions/month)

| Trigger | What to ask | Estimated cost |
|---|---|---|
| Phase 1A-beta verdict comes back; want analysis | "Analyze winners.parquet; which combos are most promising?" | ~$3-5 |
| Phase 1B-alpha A/B verdict comes back | "Did agents add value? Show per-combo A/B + recommend next step" | ~$3-5 |
| Stage 3 paper-trading week one review | "Compare paper PnL to baseline expectations; flag divergence" | ~$3-5 |
| A specific bug in a module | "Trade X exited at Y on date Z but should have exited at W; what's wrong?" | ~$5-10 |
| New strategy idea to test | "Add strategy X to screener; full pyramid; commit" | ~$10-20 |
| Stage 3 -> Stage 4 transition | "Walk me through Stage 4 activation prerequisites + risk checklist" | ~$5-10 |

**DO NOT use Claude for:**
- Running pre-built scripts (zero cost; just run them)
- Reading dashboards (just open the HTML)
- Cron scheduling (one-time setup, no Claude needed)
- Reviewing trade logs (you can open the CSVs)

---

## 5. Money safety checks (per CHECKLIST #13/22/23/29)

**Before ANY paid API run:**

1. Run smoke first: `--dry-run` flag estimates cost without API calls
2. Verify estimate is below your acceptable threshold
3. Run demo: small-N actual API spend (~$10) to validate framework
4. Owner-review demo verdict
5. Only then run full

**Phase 1B-alpha budget guard:**
- `run_phase_1b_alpha.py` HARD-rejects `--budget-cap > 300` (owner pre-approved ceiling)
- Smoke + demo combined ~$13 protect the $150 default cap

---

## 6. What to monitor weekly

| Signal | Source | Action if bad |
|---|---|---|
| Phase 1A/B run completes | `last_run.txt` in output dirs | If missing >48h, check for crash |
| Test pyramid CI status | https://github.com/jeetmehta1991/stock-picks-app/actions | If red, ask Claude |
| Paper portfolio dropping >5% in a week | `dashboard_stage_3/data.js` `current_dd_pct` | Pause, review strategies, ask Claude |
| Email alerts firing daily | Inbox | If silent for 2+ days, check cron + SMTP env vars |
| Live paper-vs-backtest divergence >10% | Compare trade_log.parquet to paper portfolio | Ask Claude for diagnostic |

---

## 7. Emergency: what NEVER to do without Claude

- **Push a commit while CI is red** (Test Pyramid workflow). Pyramid must pass before any commit lands. See Batch 249/250 for what happened when CI went red unnoticed for 30+ commits.
- **Activate live trading without paper-trading 30+ days** of data showing divergence < 20% from backtest. Per DEC-269.
- **Increase Phase 1B-alpha budget beyond $300** without revising the owner-approved cap. The script hard-rejects this.
- **Delete `data_prefetch/`** OR `output_v2/`. These are cache+results that take days to regenerate.
- **Run a backtest while another is running on the same hardware** (CPU steal kills both).

---

## 8. Repo state at downgrade (May 29, 2026)

| Item | State | Notes |
|---|---|---|
| Strategy roster | 111+ strategies | 25 added Batches 252-255 (chart/index/pairs/news/calendar/x-asset/vol-profile) |
| Exit method roster | 25+ methods | Over-delivered DEC-067 (canonical 17) |
| Stage 2 phases | 1A-alpha RUNNING, 1A-beta + 1B-alpha scripted | Ready to launch on owner trigger |
| Stage 3 paper trading | Skeleton COMPLETE | Activates when Stage 2 verdict good |
| Stage 4 live trading | Skeleton COMPLETE, NOT ACTIVATED | Owner-deploy via deploy_live.sh |
| Dashboards | Dashboard 1/2/3 live; Dashboard 4 (Stage 3) skeleton | Auto-refresh via build_dashboard_*.py |
| Cloud deployment | AWS Lightsail config built, not deployed | Owner activates with IB + AWS creds |
| Test pyramid | All 13 tiers green | CI auto-runs on every push |

---

## 9. Reference docs (open these, not Claude)

- [PROJECT_PLAN.md](PROJECT_PLAN.md) - what the project is + sprint structure
- [STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md](STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md) - phase summary table
- [DETAILED_PROJECT_PLAN.md](DETAILED_PROJECT_PLAN.md) - engineering detail
- [TRADING_RULES_AND_INFORMATION.md](TRADING_RULES_AND_INFORMATION.md) - passing criteria + thresholds
- [AUDIT_INDEX.md](AUDIT_INDEX.md) - 700+ decision history
- [LEARNINGS.md](LEARNINGS.md) - 150+ lessons (read before any new endeavor)
- [CHECKLIST.md](CHECKLIST.md) - pre-action checklist

---

## 10. When you eventually upgrade back to Max

Tell Claude: "Resume from the master plan in STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md. Current state: [paste git log -1 + current dashboard verdict]. Pick up from [specific next item]."

The repo's audit/decisions structure means a new Claude session can pick up cold without context loss. Average ramp time: 1 turn.
