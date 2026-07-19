<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1234 2026-07-07 doc-sync sweep -->

<!-- COUNCIL 278-287 SYNC BANNER (B1234 2026-07-07) - READ FIRST -->
> **Sync status:** Body may contain refs stale as of 2026-06-27 or earlier. Canonical current state (B1231):
> - `len(ALL_STRATEGIES) = 219` (post-B1189 DELETE dxy_headwind); `STRATEGIES_DISABLED_MISSING_PRODUCER = set()`
> - Test count: 880 passed, 2 skipped on test_unit + test_integration
> - CHECKLIST items #1-#158, LEARNINGS through L209, latest batch B1310
> - Councils 278-287: 40 strategies loosened + 11 silent misses remediated + 25+ producer coverage audits + historical timeline finding + 2 critical bugs FIXED via graceful degradation
> - Stage 4 walks: ARCHIVED to `archive/2026-07-07-stage-4-walks-complete/`
> - Sprint 5 tickets: 3 queued (S5-B1214 HIGH / S5-B1216 MED post-B1230 correction / S5-B1212 MED)
> - Comprehensive coverage report: `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

# AWS Launch Playbook - R6 Operational Reference

# Source: B1052 sub-agent Alpha synthesis of B1028-B1051 AWS launch lineage per owner directive 2026-06-28 "Document the current workflow, processes, phases etc for reuse in r6" per CHECKLIST #77.

**Doc F of 7-doc r6_workflow_reuse bundle.**

**⚠ Current-model note:** the chunk-based execution model (local + AWS spot chunks, `aws_chunk_launch.py`) is documented in `docs/r6_workflow_reuse/RUN_WORKFLOWS.md` (Doc G). This doc's Section 1 Gates 1-6 + AZ/spot/externalization recipes remain the authoritative AWS-mechanics reference and are cross-referenced from Doc G.

**Cross-link:** companion `docs/r6_workflow_reuse/R5_WORKFLOW.md` (Doc A) covers per-phase workflow + sentinel contract. **Read Doc A first**; this doc covers AWS-mechanics that are orthogonal to phase logic.

---

## How to use this in R6

**R6 owner / Claude:** when launching the R6 cube on AWS, this doc is the operational ground-truth for **AWS-mechanics pre-flight + AZ failover + spot-capacity handling + bootstrap fallback + polling pattern + cost arithmetic**. Treat it as a runbook: each section is a self-contained recipe you execute in order. Doc A tells you "what phase 2 does"; Doc F tells you "how to handle MaxSpotInstanceCountExceeded when you launch the instance."

**Specific R6 consumers:**

1. R6 pre-launch sign-off - Section 1 (4-gate pre-flight) is the go/no-go checklist.
2. R6 AZ selection - Section 2 (us-east-1 AZ failover order) tells you the empirically-ranked sequence.
3. R6 spot capacity error - Section 4 (spot capacity handling) tells you how to recover.
4. R6 monitoring - Section 6 (polling sub-agent pattern) gives the Bash recipe.
5. R6 budget gate - Section 7 (cost arithmetic) gives the $$$ ceilings.

---

## 1. Pre-flight gates (must pass before `aws ec2 run-instances`)

These six gates fire BEFORE any AWS spend. Skipping any of them is a CHECKLIST violation.

### Gate 1 - CHECKLIST #116: user-data 16KB after base64 encoding

**Limit:** 16,384 bytes base64-encoded (≈ 12,288 bytes raw before 33% expansion).

**Check:**
```bash
RAW_SIZE=$(wc -c < "$USER_DATA_FILE")
B64_SIZE=$(base64 -w0 "$USER_DATA_FILE" | wc -c)
if [ "$B64_SIZE" -gt 16384 ]; then
    echo "FAIL: base64 size $B64_SIZE > 16384"
    # Fallback: S3 externalization (see Section 3)
fi
```

**Why:** B1028 first attempt: 12,740 raw / 16,988 base64 -> EXCEEDED -> silent EC2 RunInstances failure (B1028 sunk $0 because launch never happened; B1028 retries cost $1.41 cumulative).

### Gate 2 - CHECKLIST #117: Monitor arm-at-event boundary

**Rule:** Bash `Monitor` tool armed at event boundary (e.g., after BOOT sentinel lands), NOT pre-launch with a multi-hour timeout. **Reason:** Monitor timeouts must match the async-AWS wall-clock window. Arming pre-launch with a 1-hr timeout expires before the instance even reaches Phase 1 (B1021 lesson - monitor expired 1 hr later before B1024 instance launched).

**Practical pattern:** poll S3 every 5 min via Bash `run_in_background` (see Section 6).

### Gate 3 - CHECKLIST #121: Monitor armed in user-data (grep verification)

**Check:**
```bash
grep -E 'b1019_phase_1_runtime_monitor\.py' "$USER_DATA_FILE" || {
    echo "FAIL: B1019 monitor NOT armed in user-data"
    exit 1
}
```

**Why:** B1028 meta-bug: B1019 monitor was DESIGNED in repo but NOT wrapped around the engine in user-data - owner had to ask "Has phase 1 landed?" because no sentinels were emitting (`feedback_monitor_design_vs_operational_gap`). Grep must match the actual invocation, not a comment or loose proxy (`sync_loop|phase_watchdog` was the B1028 false-positive).

### Gate 4 - CHECKLIST #124: IAM SSM precondition

**Check:**
```bash
SSM_ATTACHED=$(aws iam list-attached-role-policies \
    --role-name "$IAM_INSTANCE_PROFILE" --output text 2>/dev/null \
    | grep -c AmazonSSMManagedInstanceCore || true)
if [ "$SSM_ATTACHED" -lt 1 ]; then
    echo "FAIL: SSM not attached"
    echo "FIX: aws iam attach-role-policy --role-name $IAM_INSTANCE_PROFILE --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    exit 1
fi
```

**Why:** Without SSM, mid-run inspection requires SSH (key issues + security group rules + ENI access). SSM lets you `aws ssm start-session` into a running instance for free; B1028 forensics were blocked by missing SSM.

### Gate 5 - B1256: install git compliance hooks on fresh clones

**Rule:** any user-data / bootstrap that clones the repo AND commits from the instance (checkpoint pushes, result commits) MUST install the git hooks right after clone -- git hooks live in `.git/`, which does NOT travel with clones, so a fresh clone silently skips ALL commit gates (C1-C9: unicode/em-dash/canonical-source/pyramid-stamp/banned-patterns/queue-entry/doc-queue-xcheck per B1254-B1255).

**Bootstrap line (add immediately after `git clone`):**
```bash
bash scripts/install_git_hooks.sh   # Windows launch scripts: scripts\install_git_hooks.bat
```

**Verification (in user-data self-check block):**
```bash
grep -q "preflight.py" .git/hooks/pre-commit || echo "FAIL: compliance hooks not installed"
```

**Note:** the Stop hook (Gate B, `.claude/settings.json`) and the preflight script itself ARE committed and travel with the clone automatically -- only the `.git/hooks/` shims need this install step. Instances that never `git commit` (pure compute + S3-upload pattern) can skip this gate; state the skip explicitly in the launch checklist per no-silent-skip.

### Gate 6 - CHECKLIST #158 / B1309: environment-fingerprint parity (package set + day-grid)

**Rule:** every instance that runs a MERGEABLE backtest chunk MUST emit an environment fingerprint into its output dir at launch, and every chunk's fingerprint MUST agree on the merge-critical fields (`grid_total`, `grid_hash`, `calendar_backend`) before its artifacts feed the merged cube. This closes the B1305/B1308 class: chunk 1 ran the Mon-Fri fallback grid (1043d) while cloud chunks ran NYSE (1002d), and the deeper ~33pct local-vs-cloud trade churn was platform nondeterminism (Win/Py3.14 vs Linux/Py3.11 numpy-BLAS) -- neither caught by any gate because no environment-parity check existed.

**In user-data (emit at launch, before/after the engine starts):**
```bash
python3.11 scripts/env_fingerprint.py --emit output_chunk${N}/env_fingerprint.json
# calendar_backend != nyse_mcal in the output => degraded Mon-Fri fallback (L207) => HALT, do not spend
```

**Pre-merge verification (local, HARD HALT on mismatch):**
```bash
python scripts/env_fingerprint.py --check output_chunk*/env_fingerprint.json
# merge_batch_outputs.py runs this automatically and aborts on mismatch (override: --allow-env-mismatch, logged)
```

**Parity requirement for a clean measurement cube:** all chunks share ONE platform + calendar. Mixing Windows-local with Linux-cloud chunks introduces float-nondeterminism churn (~33pct at trade level; cube-cell materiality at full scale UNKNOWN, per S6-B1308 -- resolve via the $1 20-ticker cloud-vs-local cell-stability cross-check before trusting a mixed-platform merge). The fingerprint captures pandas/numpy/pyarrow versions + code SHA; extend to OS+python for full platform parity.

**Note:** compute-only chunks that never merge can skip; but any chunk feeding the R5 cube CANNOT.

---

## 2. AZ failover order (us-east-1)

R5 session learnings established this empirical order. **Try in sequence; on `InsufficientInstanceCapacity` or `MaxSpotInstanceCountExceeded`, fall through to the next.**

| Rank | AZ | Why this rank |
|---|---|---|
| 1 | us-east-1b | Phase D RETRY (i-00fe60c77558f5548) launched here successfully |
| 2 | us-east-1c | Empirically reliable spot availability for c6a.16xlarge |
| 3 | us-east-1d | Backup; lower-frequency capacity issues |
| 4 | us-east-1a | Historical default; sometimes capacity-constrained for c6a.16xlarge |
| 5 | us-east-1f | B1028 original launch AZ; spot capacity failed there |

**Subnet mapping:** `SUBNET_ID` env var must be set to the subnet associated with the chosen AZ. The launch script uses `subnet-0c24265a68a460ce7` by default (currently us-east-1b per Phase D RETRY).

**Recommended R6 pattern:** parameterize `SUBNET_ID` per AZ + retry loop on capacity errors.

---

## 3. S3 user-data externalization (fallback when raw >12 KB)

When user-data exceeds the 16 KB base64 limit, externalize the bulk to S3 and pass only a small bootstrap loader as user-data. **B1044 pattern** (developed during B1028 failure recovery):

### Pattern

1. **Write the full user-data to S3** (`s3://<bucket>/<run_id>/userdata_full.sh`).
2. **Generate a small bootstrap loader** (~1-2 KB) that:
   - Downloads the full user-data from S3
   - Emits `BOOTSTRAP_LOADER` sentinel
   - `exec` into the downloaded script
3. **Pass the loader as the EC2 user-data parameter.**

### Loader template

```bash
#!/bin/bash
set -uxo pipefail
exec > >(tee /var/log/r5_bootstrap_loader.log) 2>&1

BUCKET="<bucket>"
RUN_ID="<run_id>"

mkdir -p /tmp/sentinels
echo "BOOTSTRAP_LOADER $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/sentinels/BOOTSTRAP_LOADER
aws s3 cp /tmp/sentinels/BOOTSTRAP_LOADER s3://${BUCKET}/${RUN_ID}/BOOTSTRAP_LOADER --quiet

aws s3 cp s3://${BUCKET}/${RUN_ID}/userdata_full.sh /tmp/userdata_full.sh
chmod +x /tmp/userdata_full.sh
exec /tmp/userdata_full.sh
```

**Size budget:** loader is ~600 bytes raw / ~800 bytes base64 -> comfortably under 16 KB.

**Cost:** one extra `s3 cp` at boot (~1 s, negligible).

---

## 4. Spot capacity handling

R5 session encountered both error classes. Recipes for each:

### `MaxSpotInstanceCountExceeded`

**Cause:** account spot quota for `c6a.16xlarge` exceeded.

**Recovery:**
1. Check current spot instance count: `aws ec2 describe-instances --filters Name=instance-state-name,Values=running,pending`
2. Terminate orphan/zombie instances from prior batches (`aws ec2 terminate-instances --instance-ids ...`)
3. Wait 1-2 min for quota to release
4. Retry `aws ec2 run-instances`

**Permanent fix:** request quota increase via AWS Service Quotas console (not automatable mid-launch).

### `InsufficientInstanceCapacity`

**Cause:** spot pool for the AZ x instance-type has no available capacity.

**Recovery:**
1. Fall through to next AZ in the order (Section 2)
2. If all 5 AZs fail, fall back to on-demand for Phase 1 only (`--instance-market-options 'MarketType=spot'` removed); ~$3.06/hr vs spot ~$1.05/hr; cost differential ~$2/hr for the bootstrap window
3. If on-demand also fails, switch to smaller instance type (c6a.8xlarge) for Phase 1+2; re-evaluate for Phase 3+4

**Never blindly retry the same AZ** - the spot pool can be cold for hours.

---

## 5. Bootstrap loader pattern (B1044 fallback)

This is the recipe for the rare case where user-data exceeds 16 KB AND S3 externalization is also constrained (e.g., S3 PutObject perm missing). **B1044 fallback** decomposes the user-data into 2-3 chunks, each below the limit, glued by an inline `cat <<EOF` chain.

**Not the default recipe** - only use if Section 3 (S3 externalization) is blocked. Documented for completeness.

```bash
# Chunk 1: bootstrap base (Python install + repo clone)
USERDATA_CHUNK1="..."  # ~10 KB raw

# Chunk 2: phase logic (engine + monitor + post-run)
USERDATA_CHUNK2="..."  # ~10 KB raw

# Stitch via inline cat in chunk1 that writes chunk2 from a base64-embedded payload
```

**Caveat:** this is fragile. Prefer Section 3 (S3 externalization). Documented because R5 session B1044 used a variant of this when initial S3 perms were unclear.

---

## 6. Polling sub-agent pattern (Bash run_in_background; 5-min interval)

**Goal:** monitor a multi-hour AWS instance without burning Claude context tokens on idle polls.

**Pattern:**

```bash
# Launch poller in background
(
    while true; do
        TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
        echo "[$TS] sentinels:"
        aws s3 ls "s3://${BUCKET}/${RUN_ID}/" --recursive | tail -20

        # Check terminal sentinels
        if aws s3 ls "s3://${BUCKET}/${RUN_ID}/AUTOLADDER_COMPLETE" --quiet; then
            echo "[$TS] AUTOLADDER_COMPLETE landed; exiting poller"
            break
        fi
        if aws s3 ls "s3://${BUCKET}/${RUN_ID}/" | grep -E 'PHASE_._FAIL|PHASE_._B1019_HALT|PHASE_._TIMEOUT_HALT'; then
            echo "[$TS] HALT sentinel detected; exiting poller"
            break
        fi

        sleep 300  # 5 min
    done
) > /tmp/r5_poller.log 2>&1 &
POLLER_PID=$!
echo "Poller PID: $POLLER_PID"
```

**Use with Bash `run_in_background`:**

```python
Bash(
    command="bash /tmp/launch_r5_poller.sh",
    run_in_background=True,
    description="Launch R5 polling agent",
)
```

**17-hour cap:** poller should self-terminate at 17 hr (cumulative MAX_MIN across all phases). Add:

```bash
START_TS=$(date +%s)
MAX_SECS=$((17 * 3600))
while true; do
    NOW=$(date +%s)
    if [ $((NOW - START_TS)) -gt $MAX_SECS ]; then
        echo "17-hr cap hit; exiting poller"
        break
    fi
    # ... rest of loop
done
```

---

## 7. Cost arithmetic + budget gates

### Per-phase ceiling (spot c6a.16xlarge @ ~$1.05/hr)

| Phase | MAX_MIN | Max cost (MAX_MIN @ spot) | Expected cost |
|---|---|---|---|
| Bootstrap | n/a | ~$0.50 | $0.30-0.50 |
| Phase 1 | 120 min | $2.10 | $0.50-1.50 |
| Phase 2 | 180 min | $3.15 | $1.50-3.00 |
| Phase 3 | 240 min | $4.20 | $3.00-4.50 |
| Phase 4 | 480 min | $8.40 | $2.00-5.00 |
| Post-run | n/a | negligible | negligible |
| **Total** | 17 hr cap | **~$18 absolute ceiling** | **$7-15 expected** |

### Smoke run cost

**Phase C smoke** (NVDA x 22 trading days = 1 month, MAX_MIN=15):
- Wall-clock: ~10-11 min engine + 5 min bootstrap = ~16 min
- Cost: ~$0.30 (well under $0.49 budget gate)

### Budget gate

**R6 pre-launch sign-off:** verify expected cost <= $15 + absolute ceiling <= $20. If cost projections exceed these, raise to owner BEFORE launch per L86/L95 (`feedback_audit_recommendations_against_existing_directives` + CHECKLIST #29).

### Sunk cost tracking

R5 session sunk cost lineage: B1024 -> B1025 -> B1026 -> B1027 cumulative = **$1.41** (HALT-chain before B1028 launched). B1028 expected $1.20-2.70; actual TBD pending Phase D completion.

**R6 rule:** track sunk cost per launch attempt. If a single batch exceeds $5 cumulative without a `PHASE_1_PASS` sentinel, HALT and escalate.

---

## 8. Phase D session learnings (R5)

Three session-specific lessons that informed this playbook:

### 8.1 - B1028 spot failure -> externalization

**What happened:** B1028 first attempt at us-east-1f failed with user-data 16,988 bytes base64 > 16,384 limit. EC2 silently rejected the launch. Three subsequent batches (B1024-B1027) burned $1.41 before B1028 succeeded with S3 externalization.

**Lesson:** Gate 1 (#116) pre-flight check is non-negotiable. Externalize via Section 3 pattern any time raw user-data exceeds 12 KB.

### 8.2 - B1048 PHASE_DIR scope bug

**What happened:** `PHASE_DIR` was set inside `run_phase()` function but referenced at outer-script scope in the preflight block. Function-local variable was empty at the call site -> preflight check operated on empty path -> silent pass / false-positive.

**Lesson:** B1049 fix substituted literal `output_phase_1` at outer scope; B1050 Sub-B audit verified via rendered file. **For R6:** add `local` declarations in every shell function + grep for function-var references outside the function (B1050 Section D Test 2).

### 8.3 - B1052 silent engine concern (current session)

**What happened:** During this session, engine ran without intermediate `engine_state.json` emits visible to monitor (F-01 schema mismatch + F-05 first-emit-after-cap). Monitor was operationally armed but consumed no progress signal until B1043 fixes landed.

**Lesson:** "Armed" ≠ "consuming evidence." Per CHECKLIST #126 (DESIGNED-VS-VERIFIED), the evidence artifact for "monitor armed and producing useful signal" is a smoke run where the monitor reads at least one `engine_state.json` emit and logs it. **For R6:** verify monitor-reading-emit before scaling to Phase 4.

---

## 9. Honest gap acknowledgment template

Per `feedback_audit_recommendations_against_existing_directives` + CHECKLIST #126:

> **What we know:** [empirical evidence from smoke / Phase C / prior R5 runs]
> **What we estimate:** [extrapolation from known data points]
> **What we do NOT know:** [explicit gaps requiring R6 measurement]
> **Risk acceptance:** [owner sign-off if the gap is being accepted]

**Concrete R6 examples to fill:**

- Phase 4 wall-clock: **estimate** 1.4-2.8 hr (Sub-C extrapolation); **NOT known** empirically until R5 completes; **R6 should use R5's measured time as anchor.**
- Spot price stability: **estimate** $1.05/hr based on prior weeks; **NOT known** for R6 launch date; **check `aws ec2 describe-spot-price-history` 1 hr before launch.**
- Universe scope: **PROJECT_PLAN line 193 = Master 1937**; CLAUDE.md banner = T1a 503 (illustrative); **ops intersection = 1929**. For R6 verify 3-way reconciliation per `feedback_readiness_audit_must_verify_universe_scope`.

---

## 10. Cross-references

**Code:**
- `scripts/launch_r5_master_4y_v2.sh` (canonical launcher)
- `scripts/b1019_phase_1_runtime_monitor.py` (per-phase monitor wrap)

**Docs:**
- `docs/r6_workflow_reuse/R5_WORKFLOW.md` (Doc A - per-phase workflow + sentinels)
- `output_audit/b1050_launch_script_class_a_to_f_audit_2026_06_28.md` (B1050 7-bug class A-F audit)
- `output_audit/b1043_phase_d_timing_analysis_2026_06_28.md` (Sub-C timing math)
- `output_audit/b1042_audit_a_monitor_validator_wrapper_2026_06_28.md` (monitor wrapper rationale)

**CHECKLIST items in force:**
- #77 doc Source header
- #116 user-data 16KB
- #117 monitor arm-at-event
- #121 monitor-armed grep
- #122 silent-failure pairing
- #124 IAM SSM precondition
- #126 designed-vs-verified evidence artifact
- #127 AWS smoke mandatory gate

**Memory rules in force:**
- `feedback_aws_user_data_size_preflight`
- `feedback_monitor_arm_at_event_not_pre_launch`
- `feedback_monitor_design_vs_operational_gap`
- `feedback_silent_failure_pairing_rule`
- `feedback_ask_before_relaunching_corrected_version`
- `feedback_audit_recommendations_against_existing_directives`
- `feedback_readiness_audit_must_verify_universe_scope`
- `feedback_aws_artifact_count_not_proxy_for_project_scope`

**L86/L95 lineage:** "Small test batch -> manual review -> owner approval -> scale. NEVER jump from data ready to full run." Embedded in Section 7 (per-phase ceiling) + Section 1 (pre-flight gates).
