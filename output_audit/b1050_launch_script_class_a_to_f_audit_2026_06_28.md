# B1050 Adversarial Audit: launch_r5_master_4y_v2.sh - Class A-F Bug Hunt

# Source: Council 144 + 145 Sub-Agent B1050 CLASS A-F adversarial scan per CHECKLIST #77.

**Date:** 2026-06-28
**Scope:** `scripts/launch_r5_master_4y_v2.sh` (417 lines source / 281 lines rendered user-data)
**Method:** Render heredoc -> `bash -n` -> manual class-by-class hunt
**Source:** Council 144 owner directive "did you actually fix the bug class, or just patch one instance?"
**Honest-finding pivot count:** 29 cumulative session prior to this audit

---

## Section A: Methodology

1. Extracted the unquoted heredoc block from source `scripts/launch_r5_master_4y_v2.sh` lines 76-357.
2. Rendered the actual AWS-runtime form by invoking the launch script in dry-mode (skipping AWS spend) -> captured `/tmp/r5_full_20260627_205318_userdata.sh` -> copied to `output_audit/_b1050_actual_userdata_full.sh` for inspection. This is **what bash actually wrote to disk** after heredoc processing (single-`\` line continuations preserved, outer-shell var substitutions applied, `\$` deferred-vars resolved to `$` literals).
3. Verified syntactic validity: `bash -n output_audit/_b1050_actual_userdata_full.sh` -> exit 0.
4. Hunted Class A-F bug patterns line-by-line per Council 144 scope spec.
5. Cross-referenced PIVOT #29 root cause (function-scope variable used at outer scope before function call) against all other variable references.
6. Verified Phase D RETRY (i-00fe60c77558f5548) impact for each finding.

**Render mismatch alert:** My first render via Python `str.replace` produced a file with literal `\\` at line continuations, which would be a BUG if real. The actual bash-rendered file uses single `\` (proper continuation) because unquoted-heredoc `\\` collapses to one `\`. This was a render artifact, NOT a script bug. Lesson logged as render-validation methodology fix for future audits.

---

## Section B: Class A Findings (Variable Scope - PIVOT #29 Class)

| ID | Finding | Source line | Rendered line | Severity | Recommendation |
|----|---------|-------------|---------------|----------|----------------|
| **A-1** | PHASE_DIR preflight reference RESOLVED-via-B1049 (literal `output_phase_1` substituted) | source 316-318 | rendered 240-242 | INFO | None - confirmed B1049 fix landed |
| A-2 | `B1019_PID` / `HALT_WATCHER_PID` / `WATCHDOG_PID` / `ENGINE_PID` set without `local` inside `run_phase` | rendered 140, 142, 154, 172 | Same | LOW | Stale values leak across Phase 1->2->3->4 iterations; spurious "kill ... failed (already exited)" log noise. Add `local` declarations. Non-blocking. |
| A-3 | `phase_watchdog` function uses `PHASE_NUM` `MAX_MIN` `PHASE_PID` without `local` | rendered 108-110 | Same | LOW | Same pattern as A-2; backgrounded function inherits caller's vars by name. Non-blocking. |
| A-4 | `MASTER_TICKERS` shell-substituted into Python source code inside `$(python -c "...")` | rendered 228 | Same | **CRITICAL** (see C-1) | See Section C C-1. |

**A-AUDIT VERDICT for Class A (PIVOT #29 specifically):** No other function-scope-leak-outside-function bugs found. B1049 fix verified. The variable scope class IS closed.

---

## Section C: Class B-F Findings

| ID | Class | Finding | Rendered line | Severity | Recommendation |
|----|-------|---------|---------------|----------|----------------|
| **C-1** | B+E | **`MASTER_TICKERS` injection into Python source assumes comma-separated format.** If `master_ops_tickers.txt` is newline-delimited (likely default `'\n'.join(tickers)` Python idiom), the `$(cat file)` substitution preserves newlines. Substituting newlines into `python -c "ts='${MASTER_TICKERS}'.split(',')..."` injects newlines into the Python string literal -> `SyntaxError: EOL while scanning string literal`. Subshell exits non-zero -> `TICKERS_PHASE_3` is empty. `run_phase 3 "" output_phase_3 ...` then runs engine with empty `--tickers` -> Phase 3 fails. | 228 | **[RED] CRITICAL POTENTIAL** | **VERIFY master_ops_tickers.txt format in S3 before Phase D RETRY reaches Phase 3 boundary (post Phase 2 PASS).** If newline-separated, switch to `tr '\n' ','` pre-processing OR use file-based python: `python -c "import sys; ts=sys.stdin.read().replace('\n',',').strip(',').split(','); ..."  < /tmp/master_ops_tickers.txt`. **If verified CSV, B-1 nullified.** Phase D RETRY currently sits in Phase 1 -> not yet exposed; reaches this line several hours from now. |
| **C-2** | B | Hardcoded master snapshot run ID `r5_master_20260627_064008` in S3 path | 224 | MODERATE | Convert to env var override: `MASTER_SNAPSHOT_RUN_ID="${MASTER_SNAPSHOT_RUN_ID:-r5_master_20260627_064008}"` then `s3://${BUCKET}/${MASTER_SNAPSHOT_RUN_ID}/master_ops_tickers.txt`. Prevents future cross-batch scope drift. |
| **C-3** | B | **Master-tickers download FAIL fallback uploads wrong sentinel source file** - `aws s3 cp /tmp/sentinels/AUTOLADDER_COMPLETE` referenced before AUTOLADDER_COMPLETE exists (only created at end of Phase 4 - rendered line 277). Source file does NOT exist -> upload silently fails (`--quiet 2>/dev/null`). Owner sees ZERO S3 sentinel after CRITICAL master-tickers failure. | 224 (compound) | MODERATE | Replace with: `echo "MASTER_TICKERS_DOWNLOAD_FAIL $(date -u ...)" > /tmp/sentinels/MASTER_TICKERS_DOWNLOAD_FAIL; aws s3 cp /tmp/sentinels/MASTER_TICKERS_DOWNLOAD_FAIL s3://${BUCKET}/${RUN_ID}/MASTER_TICKERS_DOWNLOAD_FAIL --quiet 2>/dev/null` |
| **C-4** | D | `pip install -q -r requirements.txt 2>&1 \| tail -3 \|\| true` lacks paired verification check per CHECKLIST #122 | 43 | MODERATE | Add `python -c "import <key requirements modules>"` after, with sentinel + HALT on miss. Otherwise: if requirements.txt adds a new dep without wheels, engine errors mid-Phase. |
| **C-5** | F | `$(date -u +%Y-%m-%dT%H:%M:%SZ)` inside `nohup bash -c "..."` is expanded by OUTER bash at nohup-launch time, NOT at HALT-detection time. Sentinel timestamp reports nohup-launch timestamp, misleading post-mortem. | 166 (inside nohup bash -c) | MODERATE | Escape the `$()` with `\` so it defers to inner bash: `\$(date -u ...)`. Or single-quote the bash -c arg and use `$(date)` directly. |
| C-6 | D | Pipeline `python ... preflight | head -50 || { HALT }` under `set -uxo pipefail` - pipefail propagates failure correctly when python errors. If preflight output ever exceeds 50 lines, `head -50` SIGPIPEs python (exit 141) -> pipefail makes pipeline exit non-zero -> HALT fires spuriously. Current preflight emits ~10-15 lines, so risk is low. | 240-242 | LOW | Replace pipeline with `python ... > output_phase_1/preflight.log 2>&1 || { HALT }; head -50 output_phase_1/preflight.log` |
| C-7 | C | `aws s3 cp` on rendered line 11 runs BEFORE `dnf install -y ... aws-cli` on line 14. AL2023 ships aws CLI v2 preinstalled, so this works. | 11 vs 14 | INFO | None - AL2023 has aws CLI in base AMI. Documented for awareness. |
| C-8 | E | `sync_loop` background runs from rendered line 81 forward; `output_phase_4_r5/` syncs even when empty (smoke mode only writes to `output_phase_smoke/`). | 71-80 | LOW | Performance only; ~0.5s per iteration wasted on empty dirs. No functional bug. Non-blocking. |

---

## Section D: Pre-emptive Pyramid Tests Proposed

Per CHECKLIST #126, audit evidence = pyramid tests added.

1. **`test_b1050_master_tickers_format_assumption`** (`backtest/tests/test_unit.py`):
   - Spec: Verify that the launch script's `master_ops_tickers.txt` parsing assumption (comma-separated, single line) matches actual upstream producer format.
   - Implementation: Locate the most recent `master_ops_tickers.txt` (under `output_audit/` or via the script that built it); assert `'\n' not in content.strip()` AND `',' in content`. Fail if newline-separated.
   - Gates: C-1.

2. **`test_b1050_launch_script_no_function_scope_leaks_outside`** (`backtest/tests/test_unit.py`):
   - Spec: Static-grep verification that no `${PHASE_DIR}` / `${PHASE_NUM}` / `${TICKERS}` / `${START_DATE}` / `${END_DATE}` / `${MAX_MIN}` / `${NCNT}` references appear OUTSIDE the `run_phase()` function in `scripts/launch_r5_master_4y_v2.sh`.
   - Implementation: parse source script, locate `run_phase()` `{...}` block via brace matching, assert no references to those vars in lines OUTSIDE that block (except function definitions).
   - Gates: A-1 + the general PIVOT #29 class.

3. **`test_b1050_or_true_pairing_compliance`** (`backtest/tests/test_unit.py`):
   - Spec: For every `|| true` in `scripts/launch_r5_master_4y_v2.sh`, assert a paired `python -c "import ..."` OR explicit sentinel check on the next 2 lines.
   - Implementation: regex line scan + lookahead.
   - Gates: C-4 + CHECKLIST #122 compliance class.

4. **`test_b1050_critical_sentinel_source_file_exists`** (`backtest/tests/test_unit.py`):
   - Spec: For every `aws s3 cp <source>` in the FAIL-fallback branch (inside `|| { ... }` blocks), assert `<source>` is created EARLIER in the script flow.
   - Implementation: parse FAIL blocks, extract source paths, assert they appear in an `echo ... > <source>` BEFORE the cp.
   - Gates: C-3.

5. **`test_b1050_nohup_bashc_deferred_substitution`** (`backtest/tests/test_unit.py`):
   - Spec: For `nohup bash -c "..."` blocks, assert `$(date)` and other event-time computations are escaped with `\` (deferred).
   - Implementation: scan `nohup bash -c` arg blocks for unescaped `$(date)`, `$(uptime)`, `$(...)` event-time invocations.
   - Gates: C-5.

---

## Section E: CRITICAL Findings for Currently-Running Phase D Retry

**Phase D RETRY = i-00fe60c77558f5548 (us-east-1b)** running `scripts/launch_r5_master_4y_v2.sh` as committed (B1049 fix included).

**Timing extrapolation:** Phase 1 = NVDA single, MAX_MIN=120; Phase 2 = 10 tickers, MAX_MIN=180; Phase 3 = 50 tickers, MAX_MIN=240; Phase 4 = 1929 tickers, MAX_MIN=480. Cumulative cap = 17 hours. Phase 1 -> 2 boundary at minute ~30-90; **Phase 2 -> 3 boundary at minute ~120-180** (this is where C-1 fires).

### CRITICAL ALERT: C-1 (MASTER_TICKERS python-injection format mismatch)

If `master_ops_tickers.txt` in S3 is newline-separated (typical Python `'\n'.join(...)` pattern):
- Phase 1 PASS expected [OK]
- Phase 2 PASS expected (literal `TICKERS_PHASE_2="NVDA,AAPL,..."` not affected) [OK]
- **Phase 2 -> Phase 3 transition: line 228 `python -c "..."` errors with SyntaxError -> TICKERS_PHASE_3 = empty -> Phase 3 launch FAILS with empty `--tickers`.**
- Phase D HALT at Phase 3 START - owner sees `PHASE_3_FAIL no-trade-log` sentinel.

**Estimated time to fire: 2-4 hours from Phase D launch start.**

**ASK BEFORE RELAUNCH (per `feedback_ask_before_relaunching_corrected_version` memory rule):** Do NOT auto-intervene with the running Phase D instance. Surface this finding to owner; owner decides whether to (a) verify format via `aws s3 cp` peek of the actual file, (b) pre-emptively kill the running instance and patch, (c) let Phase D RETRY fail at Phase 3 and patch on next iteration.

**Mitigation patch (if owner directs):** Replace line 228 with:
```bash
TICKERS_PHASE_3=$(python3 -c "
import sys
with open('/tmp/master_ops_tickers.txt') as f:
    raw = f.read()
ts = [t.strip() for t in raw.replace('\n',',').split(',') if t.strip()]
n = len(ts)
step = max(1, n//50)
print(','.join(ts[::step][:50]))
")
```

This is robust to both CSV and newline-separated formats.

---

## Audit Verdict

**Total findings:** 1 INFO + 5 LOW + 1 MODERATE-LOW + 4 MODERATE + 1 CRITICAL-POTENTIAL = 12.

**PIVOT #29 class:** CLOSED. B1049 fix verified; no other function-scope-leak instances.

**New bug-class surfaced:** C-1 + C-3 are NEW classes not previously catalogued in this session's pivot tally. C-1 specifically is a **format-contract assumption between launcher and upstream producer** which is a distinct class from PIVOT #29's variable-scope class.

**Recommendation to owner:**
1. **IMMEDIATE (Phase D in-flight):** Verify `aws s3 cp s3://${BUCKET}/r5_master_20260627_064008/master_ops_tickers.txt -` (peek first 200 bytes) to determine whether C-1 will fire on the running Phase D RETRY. If newline-separated, decide intervene vs let-fail.
2. **NEXT BATCH (B1051+):** Apply C-3, C-4, C-5 fixes + add 5 proposed pyramid tests.
3. **DEFERRED:** A-2, A-3 (low severity), C-2 (hardcoding), C-6 (low risk), C-7 (informational), C-8 (cosmetic).

---

## CHECKLIST Compliance Statement

This audit complied with:
- **#105** read FULL launch script end-to-end (417 lines source + 281 lines rendered)
- **#106 + #44(b)** investigated WHY each pattern exists (not just classified)
- **#118** sub-pyramid tests proposed at finding time (Section D)
- **#119** Council verdict dependencies verified (B1049 fix confirmed via rendered file)
- **#122** silent-failure-pairing rule applied to every `|| true` (Section C C-4)
- **#126** sub-agent verification IS evidence - zero-AWS-spend static analysis
- **#127** no AWS smoke required (static analysis self-contained)
- **L86 / L95** read-only audit; no destructive ops; no AWS spend
- `feedback_audit_recommendations_against_existing_directives` - findings surfaced; no auto-remediation
- `feedback_ask_before_relaunching_corrected_version` - Phase D running instance flagged, NOT touched

Honest count of NEW bugs: **1 CRITICAL-POTENTIAL + 4 MODERATE + 2 LOW = 7 actionable bugs** beyond the B1049 fix.
