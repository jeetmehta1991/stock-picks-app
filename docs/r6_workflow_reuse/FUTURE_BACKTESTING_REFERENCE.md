<!-- Source: per CHECKLIST #77 canonical-source; renamed from RUN_WORKFLOWS.md ("the r6 document") per owner directive 2026-07-24 "document the comprehensive detailed aws run details ... in the r6 document. Rename the document to future backtesting reference document." Prior lineage: B1313 2026-07-18 "document local and aws run workflows, gates, etc. everything in the r6 document". -->

<!-- CANONICAL SYNC BANNER (2026-07-24, B1362) - READ FIRST -->
> **Sync status:** Canonical current state as of 2026-07-24:
> - **Backtest window LOCKED:** `2022-05-05 -> 2026-05-05` (~1002 NYSE trading days). Every batch, every rung, every chunk.
> - **Universe for the current run:** T1a S&P-500 PIT membership = **614 tickers** (503 currently-active + 111 removed-during-window, survivorship-free) from `Backtesting universe/Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv`.
> - **Frozen code SHA for the whole batch sequence:** `e846b6d2cfb3`. Every batch runs this exact SHA so outputs merge. `env_fingerprint.MERGE_CRITICAL` observed this run: `grid_total=1003`, `grid_hash=a6a8441d06cb9b32`, `calendar_backend=nyse_mcal`, `smc_active=true`, `code_sha=e846b6d2cfb3`.
> - **Cube shape:** ~219 strategies x 26 exit methods per ticker (per-(strategy x exit) CELL). ~202-206 strategies actually fire per 100-200 ticker batch.
> - **Progress:** batches 1-6 committed = 471/614 tickers; the 143-ticker tail (batch 7) finishes the 614 cube.
> - **Cost discipline:** $50 CAD HARD cap this run; ~$36 spent through batch 6.

---

# FUTURE BACKTESTING REFERENCE
## Local + AWS run workflows, cell isolation, sentinels, crons, monitors, gates, parity + environment checks

**Audience:** a new engineer OR a new AI agent picking up backtesting with zero prior context. This is the single ground-truth document for *how a validation cube run is structured, launched, monitored, gated, finalized, merged, and visualized*. Read it top to bottom once; thereafter jump to the section you need.

**One-paragraph mental model:** We measure every trading *strategy* against every *exit method* on a fixed universe over a fixed historical window, producing a "cube" of per-(strategy x exit) result cells. Because the full universe is large and cloud runs cost money and can be interrupted, we do NOT run it all at once. We freeze the engine code at one commit SHA, split the universe into ticker-disjoint **batches**, run each batch (locally for free or on an AWS spot instance for speed), commit each batch's slim results, and finally **merge** all batches into one cube and render a **dashboard**. Guardrails at every step (commit gates, launch gates, environment-parity checks, monitors, budget caps) exist because each has caught a real, expensive failure.

---

## 1. CELL ISOLATION — the core measurement principle (READ THIS FIRST)

The whole point of the cube is that **each (strategy x exit) cell is measured in isolation**, uncontaminated by portfolio-level interactions. This is enforced by **cube-isolation mode** (`--cube-isolation`, `backtest/engine/backtest.py`).

**What cube-isolation does:**
- **Every valid signal opens a trade.** There is no "max candidates per day" cap (normally 30), no position-sizing competition, no portfolio capital constraint. A strategy that fires 40 signals on one day opens 40 trades. This is deliberate: we want the *unconditional* per-cell performance of a strategy+exit, not what survives a portfolio filter.
- **Portfolio gates are bypassed:** `--no-portfolio-cap` (no open-position cap), `--no-dd-halt` (no drawdown circuit-breaker halt), dispersion circuit-breaker off. These are portfolio-construction concerns, not per-cell measurement concerns.
- **Every closed trade is replayed against ALL exit methods.** One entry signal -> `count(EXIT_STRATEGIES)` cells (26 this run). The cube stores, for each (strategy, exit) pair, the full trade population and its metrics. (Memory rule `feedback_cube_exit_count_must_equal_registered`: the per-closed-trade exit count MUST EQUAL `len(EXIT_STRATEGIES)`, not merely exceed a threshold — the only exception is still-open trades.)
- **There is NO unified equity curve** in cube-isolation. Because every signal trades independently with no shared capital, a portfolio equity curve is meaningless here. Equity-curve / portfolio tabs come only from a later portfolio-construction pass, NOT from the isolation cube.
- **Point-in-time (PIT) is non-negotiable.** A ticker is eligible on date D only if it was an index member at the year-start snapshot (annual PIT, `backtest.py` `_annual_liquid[year]`, BUG-222): membership is snapshotted at Jan 1; a mid-year entrant becomes eligible only the next Jan 1. This is why a ticker added mid-2024 first trades 2025-01-02, and a name removed before the window never trades even though its cache file exists.

**Why isolation matters for a newcomer:** if you see a strategy with thousands of trades and no equity curve, that is correct and expected. The cube answers "does strategy X with exit Y have edge?" per cell; it does not answer "what would my portfolio have returned?" — that is a separate, later question.

---

## 2. Two execution modes

| | LOCAL | AWS SPOT CHUNK |
|---|---|---|
| Command | `python -m backtest.run_phase1a ...` | `python scripts/aws_chunk_launch.py --chunk N [--resume]` |
| Instance | laptop (local cores) | `c6a.16xlarge` spot (64 vCPU, 128 GB) by default |
| Cost | free | ~$0.60-1.20/hr spot |
| Speed | bounded by laptop cores | ~100 sim-days / 15-min at 200 tickers; a 200-ticker batch ~2-4.5 h incl. finalization |
| Interruption | none (unless laptop sleeps) | spot reclaim (2-min notice) + 8 h `MAX_RUN_HOURS` cap |
| Merge-safe with cloud? | ONLY if env-fingerprint parity holds (Section 8) | yes — all-cloud is one platform |

**Hard rule (L207/L208/L209):** LOCAL and AWS produce *slightly different* trade sets even on identical inputs — platform float nondeterminism (Windows/Py3.14 vs Linux/Py3.11 numpy-BLAS) flips threshold-boundary signals (~33% trade-level churn; common trades are bit-identical PnL). **A clean cube uses ONE platform for all merged batches.** Mixing requires the Section 8 pre-merge cross-check to *earn* the mix. This run is **all-cloud** by choice.

---

## 3. The frozen-SHA batch sequence + parity (why every batch must match)

The cube is assembled from many separately-run batches. For their outputs to merge into one coherent measurement, every batch must have been produced by **identical engine semantics**. We guarantee this two ways:

1. **Frozen code tar.** The engine code is built once into `s3://<bucket>/payload/r5_code.tar` at a chosen SHA (`e846b6d2cfb3` this run) with a `.sha` sidecar. Every instance downloads THAT tar and runs it. Editing the local repo (even the launcher) does NOT change what the instance runs — the instance computes its `code_sha` from the frozen tar. **This is why launcher-config changes (Section 6) are frozen-SHA-safe: they never touch the tarred engine code.**
2. **`env_fingerprint.MERGE_CRITICAL`.** On every instance, `scripts/env_fingerprint.py --emit` writes `env_fingerprint.json` BEFORE the engine burns compute. Its `MERGE_CRITICAL` block — `code_sha`, `grid_total`, `grid_hash`, `calendar_backend`, `smc_active` — must be **byte-identical across all merged batches**. The merge (`merge_batch_outputs.py`) runs `env_fingerprint.py --check` and HARD-HALTs on any mismatch. Every batch's finalize step verifies its fingerprint matches the first batch before commit.

**Newcomer takeaway:** if you must fix an actual engine bug mid-sequence, you break the frozen SHA and cannot merge the fixed batch with the earlier ones — you would have to re-run everything at the new SHA. So during a sequence, prefer changes that do NOT alter the engine tar (roster, batch size, pool workers, instance type). An engine fix is a decision to restart the sequence.

---

## 4. Universe + validation ladder + batch partitioning

**Never jump from "data ready" to full universe** (L86/L95 — this pattern cost $150 twice). Scale through rungs; each rung is an owner gate.

**Escalating-ladder model (this run):** the 614-ticker T1a universe is covered by an escalating sequence of ticker-disjoint batches, each larger than the last, so a problem surfaces cheap:

| Batch | Chunk | Tickers | Purpose |
|---|---|---|---|
| 1 | chunk11 | 10 | pipeline sanity |
| 2 | chunk12 | 20 | multi-ticker |
| 3 | chunk13 | 50 | first real metrics |
| 4 | chunk14 | 100 | scale + fixes (BRK-B/BF-B cache-filename bug caught here) |
| 5 | chunk15 | 200 | **HUNG at day 100** — pool-memory at scale (see Section 7 + L220) |
| 5a | chunk16 | 100 | first half of the split; ran clean to day 1002 -> proved the hang was scale, not a bad ticker |
| 6 | chunk17 | 200 | relaunched at `--pool-workers 8` (B1358 fix); ran the full window -> pool-memory RCA confirmed |
| 7 | (tail) | 143 | finishes 614 |

**Partitioning rule:** partition by **ticker**, disjoint sets. Ticker-disjoint batches `concat` cleanly at merge. SPY benchmark is auto-added to every batch -> the merge dedup removes duplicates. The pre-launch gate (`prelaunch_gate.py`) enforces disjointness against all committed batches.

**Roster carving:** the master 614 set is the T1a canonical CSV (read with `comment='#'` — it has a banner). `remaining = master - union(committed batches)`. Batch rosters live in `output_batches/batch_<N>_roster.json`; the S3 ticker list is `chunks/chunk<N>_tickers.txt` (single line, comma-separated).

**Delisted/PIT-nontraded is normal.** Many T1a rows were removed before or during the window. A ticker with `removed_date < 2022-05-05`, or `added_date` after the window, or that churned mid-year, will legitimately produce **0 trades** (0 cube cells) — this is correct PIT behavior, NOT a bug. Distinguish it from the BRK-B class (an ACTIVE ticker that zero-trades due to a cache-filename or index-registration bug — that IS a bug). Verify by checking `removed_date` in the T1a CSV and whether the cache file exists + covers the window. A separate class is "eligible-yet-zero-fire" (cache present, PIT-eligible, still 0 trades e.g. ABMD/BIO/MLM, ESS/SATS/CIEN) -> deferred investigation, non-blocking (0 trades = 0 cells).

---

## 5. AWS spot chunk workflow (`scripts/aws_chunk_launch.py`)

### 5.1 Launch
```bash
python scripts/aws_chunk_launch.py --chunk N \
    --manifest output_batches/run_manifest_batch<N>.json \
    --pool-workers 8            # 200-tkr batches (Section 6); default 16
    [--instance-type r6a.16xlarge]   # escalate RAM if 8-worker/128GB still hangs
    [--resume]                  # from S3 checkpoint
```
`--manifest` runs `scripts/prelaunch_gate.py` LOCALLY first — a FAIL means **zero AWS spend** (Section 8C). Constants at the top of the script: `INSTANCE_TYPE=c6a.16xlarge`, spot max `$1.40`, `MAX_RUN_HOURS=8.0`, `POOL_WORKERS=16`, bucket `stock-picks-r5-jm-2026`, region `us-east-1`.

### 5.2 What the launcher does
1. **Presigned URLs (no IAM role).** GETs for `payload/r5_code.tar` (frozen engine+deps), `payload/r5_payload.tar` (~3.2 GB data_prefetch cache), `payload/r5_cache_refresh.tar` (~139 MB overlay), `chunks/chunk{N}_tickers.txt`, and (resume) `chunk{N}/ckpt.tar`. PUTs for `chunk{N}/heartbeat.txt`, `ckpt.tar`, `artifacts.tar`, `r5chunk.log`. Keeps user-data < 16 KB (Gate 1).
2. **Cache-refresh overlay:** the instance extracts `payload.tar` then `cache_refresh.tar` ON TOP. The overlay is a full tar of `backtest/data/cache` INCLUDING its `index.json` — and the index is what actually serves OHLCV. A parquet present in the payload but absent from the index gets a cache MISS -> 0 trades (the BRK-B class). So **the overlay's index is the authoritative coverage source**, not the payload.
3. **Pre-engine gate:** `preengine_gate.py` validates the tar's baked SHA == `@EXPECT_SHA@` before the engine runs (stale-artifact guard).
4. **Engine run** (cube-isolation, Section 1) with `--screen-pool-workers @POOL@ --max-run-hours 8.0 --warn-run-hours 7.0`.
5. **Finalize on the instance:** engine writes the full output (trade_log + all `exit_by_*.csv` cube CSVs) -> shell tars `output_chunk{N}` -> `artifacts.tar` -> uploads -> writes `CHUNK{N}_COMPLETE` -> self-terminates (`InstanceInitiatedShutdownBehavior=terminate`).

### 5.3 The screen pool (why 200 tickers hung at 16 workers)
The signal-screening step uses a multiprocessing pool (`screener.py` `_pool_init`): each of N workers holds a full copy of the ohlcv dict + pre-warmed Quiver bulk caches (~1M insider + 500K 13F rows/worker, a fixed per-worker cost). At 200 tickers x 16 workers the concurrent duplication + accumulating trade state pushed 128 GB toward OOM; a dead worker deadlocks the parent `imap_unordered` while the heartbeat thread keeps ticking (the frozen-engine + live-heartbeat signature). **Fix = fewer workers (`--pool-workers 8`) to halve duplication, and/or a bigger instance (`--instance-type r6a.16xlarge`, 512 GB).** Both are launcher-config only -> frozen-SHA-safe. Proven: 200 tkr hung at pool=16 (day 100); the identical roster ran the full window at pool=8 (B1358/B1360). A LOCAL per-ticker screen sweep at the hang date ruled out a single bad ticker before this conclusion (bisection).

### 5.4 Completion marker (do not regress — B1312)
User-data emits `CHUNK{N}_COMPLETE` **only if** `engine_state.json status == "complete"` (full-window finalize), else `CHUNK{N}_CAPPED`. `--max-run-hours` / spot-interruption leave `status="running"`. A prior launcher wrote COMPLETE unconditionally after process exit -> a 67%-done chunk was marked complete and the resume controller stopped it. **A completion marker must reflect actual completion, not process exit.**

---

## 6. Batch constraints + launcher-config levers (all frozen-SHA-safe)

These are the ONLY knobs to turn mid-sequence, because none changes the engine tar / `code_sha`:

| Lever | Where | When |
|---|---|---|
| `--pool-workers N` | `aws_chunk_launch.py` CLI (B1358) | drop 16->8 for 200-tkr batches to avoid the pool-memory hang |
| `--instance-type T` | `aws_chunk_launch.py` CLI (B1358) | escalate to `r6a.16xlarge` (512 GB) if 8-worker/128 GB still hangs |
| batch size (roster) | `batch_<N>_roster.json` + `chunks/chunk<N>_tickers.txt` | smaller = cheaper blast radius; larger = fewer runs |
| `MAX_RUN_HOURS` | constant | hard per-instance cap; bounds a single spot-interrupt loss |
| resume | `--resume` | continue a capped/interrupted batch from `ckpt.tar` |

**Batch-cap discipline (Council 201):** <= 3 substantive engine fixes per code change; but for a FROZEN sequence you make NO engine fixes at all — only the levers above.

---

## 7. Sentinels, monitors, crons (the operational safety net)

A cloud batch runs for hours unattended, so **three independent mechanisms** watch it. Understand all three.

### 7.1 On-instance monitor (baked into user-data)
- **Heartbeat + periodic checkpoint:** every ~60 s writes `hb_utc + engine_state.json` to `chunk{N}/heartbeat.txt`; periodically tars `output_chunk{N}` -> `ckpt.tar`. Worst-case progress loss on any death mode <= a few min (a manual/hard kill sends no IMDS notice, so checkpointing cannot be interruption-only — B1300 Catch 1).
- **IMDS interruption watcher:** polls `169.254.169.254/.../spot/instance-action` every ~5 s; on the 2-min reclaim notice, flushes `ckpt.tar`.

### 7.2 Owner-facing cadence + HANG-check cron (this session's pattern)
A session-only cron (`CronCreate`, every 15 min) reads `chunk{N}/heartbeat.txt` and the EC2 state and either reports progress or acts. It is the OWNER-facing cadence (memory `feedback_batch_run_update_cadence`: at every cost-bearing launch, arm a `*/15` check + a completion `PushNotification`; delete the cron on completion). Its logic (copy this contract for future runs):

**HANG check (L220 + L221 + L221b — CHECKPOINT-AWARE):** treat as HUNG **only if** `status != 'complete'` AND `simulated_day < 1002` AND engine `timestamp` is **> 60 min** stale AND `simulated_day` unchanged from ~15 min ago. Then terminate the instance, PushNotification, CronDelete, do NOT relaunch, surface to owner (escalate to `r6a.16xlarge`).

**Why 60 min and not 8 min — the two hard-won calibrations:**
- **L221:** the every-100-days checkpoint re-serializes ALL fat-dict trades to CSV and legitimately FREEZES the engine heartbeat while it does. At 20k trades this is ~18 min. A frozen `engine_state.timestamp` at a `day % 100 == 0` boundary is a SLOW CHECKPOINT, not a hang. Confirm-before-terminate: the day-400 checkpoint froze 18 min then advanced — a blind terminate would have killed a healthy 50%-done run.
- **L221b:** checkpoint freeze time SCALES with cumulative trades — day-400 @20k ~18 min, day-800 @44k ~40 min, the final ~55k-trade checkpoint ~48 min. A threshold sized off ONE sample is exceeded later. Size for the WORST case at run's end. 60 min clears the largest checkpoint yet stays far below the 8 h `MAX_RUN_HOURS` cap that bounds a true hang anyway.
- **Finalization is also NOT a hang:** at `day == 1002` OR `status == 'complete'`, a frozen timestamp is end-of-run finalization/upload (writing the huge cube CSVs for 50k+ trades + a multi-GB `artifacts.tar` upload takes tens of minutes). Wait for `artifacts.tar`; the instance self-terminates after upload.

**Liveness vs progress:** a fresh wrapper `hb_utc` (or S3 `LastModified` on `heartbeat.txt`) proves the INSTANCE is up, NOT that the engine loop is progressing (the heartbeat loop is a separate background shell). Only `simulated_day` advancing proves progress. A live wrapper around a stuck engine is the trap. To disambiguate a suspicious freeze: check whether `ckpt.tar` on S3 is growing/fresh (active writing) and whether `simulated_day` advances on a short re-poll. **CloudWatch CPU has been unreliable in this account (returns datapoints time-stamped hours off / predating instance launch) — do NOT base a terminate decision on it.**

**Never take the destructive action (terminate a paid run) on a single ambiguous reading when a cheap confirmation exists** — a 60-90 s confirm-waiter (does day advance? does stale exceed a hard ceiling?) costs ~$0.30 and resolves it.

### 7.3 Harness-tracked waiters (for landing events)
For a single "notify me when X happens" (artifacts land, instance gone), use a **Bash `run_in_background` with an until-loop that exits on the condition** — the harness notifies on exit. Do NOT wrap it in `nohup ... &` (that detaches it from the harness and you get no notification). Cover every terminal state (present / instance-gone / a stall signal / timeout), not just the happy path.

---

## 8. Gate reference (four distinct gate systems — do not conflate)

### 8A. Commit gates C1-C10 (`scripts/preflight.py`, pre-commit hook)
Fire on every `git commit`; a violation BLOCKS (bypass only via `--no-verify`, discouraged; `GIT_QUEUE_EXEMPT=1` legitimately skips the queue-anchor gate for amend/data commits).

| Gate | Enforces |
|---|---|
| C1 UNICODE | no unicode in non-docstring runtime code |
| C2 EM-DASH | no em-dash in `scripts/*.py` |
| C3 CANONICAL-SOURCE | new docs/dashboards carry a `Source:` declaration |
| C4/C5 | `prefetch_*.py` path-restricted git capture + registry |
| C6 PYRAMID-STAMP | a GREEN full-pyramid `.pyramid_stamp` exists AND is fresher than every staged `.py`. Stamp is written by `conftest.py::pytest_sessionfinish` ONLY when a session runs BOTH `test_unit.py`+`test_integration.py` and exits 0 (`880 passed, 2 skipped`). Touch any `.py` -> must re-run the pyramid to re-stamp. |
| C7 BANNED-PATTERNS | a: no `not s.get(...)`; b: no default-`True` strategy gate; c: no relative `data_prefetch` path; d: no `except: pass` |
| C8 QUEUE-ENTRY | the commit stages `EXECUTION_QUEUE.md` (or `GIT_QUEUE_EXEMPT=1`) |
| C9 DOC-QUEUE-XCHECK | ticket IDs in staged docs exist in the queue; in merge context also runs env-fingerprint parity |
| C10 BATCH-OUTPUTS | a queue line CLAIMING a batch complete requires `output_batches/batch_<N>/` to be tracked. **Known false-match:** the regex `BATCH[ _-]?(\d+)...(COMPLETE\|PASS\|SUCCESS)` reads "batch 5a" as batch 5 and any "batch 7 ... complete/pass/success" within 60 chars. Reword prose (e.g. "finish" not "complete", "the 143-tkr tail" not "batch 7 ... complete") or add `preflight-allow: C10`. |

### 8B. Turn gate — Stop-hook (`scripts/verify_turn_compliance.py`)
Blocks turn-end if tracked files are modified-but-uncommitted (CHECKLIST #67 per-turn doc-sweep). Escape for a live run churning tracked cache files: `.stop_exempt` (one-shot, logged).

### 8C. AWS pre-launch gates (zero-spend, run LOCALLY before any `run_instances`)
- **`prelaunch_gate.py --manifest`:** required-fields present; `isolation==true`; `calendar==nyse_mcal`; S3 tar `.sha` sidecar == manifest `frozen_sha` (stale-artifact guard); **tickers disjoint from every committed batch**; all prior batches committed; budget `spent + projected <= cap`. FAIL = no AWS calls.
- **Coverage gate — `verify_payload_coverage.py`:** confirms the data payload can serve every ticker. Its DEFAULT mode checks the PAYLOAD's `index.json`; but this run serves the index via the `cache_refresh.tar` OVERLAY, so the payload-only check FALSE-FAILS. The authoritative check is the OVERLAY's `index.json` (download `payload/r5_cache_refresh.tar`, read `backtest/data/cache/index.json`, confirm each ticker is a key). Unregistered tickers that are removed-before-window are fine (they nontrade legitimately); an ACTIVE unregistered ticker is the BRK-B bug.
- **In-launcher gates:** Gate 1 (user-data <= 16 KB base64) + Gate 3 (monitor present in user-data) print inline before `run_instances`.

### 8D. Environment-parity Gate 6 (the merge gate)
`env_fingerprint.py --emit` at launch; `--check` HARD-HALT pre-merge. `MERGE_CRITICAL` = `{code_sha, grid_total, grid_hash, calendar_backend, smc_active}`. Every batch's finalize verifies this matches batch_4's before commit; the merge re-verifies across all inputs.

---

## 9. Finalize -> slim -> commit workflow (per batch)

When a batch's `artifacts.tar` lands (or the cron/waiter detects it):
1. **Download** `chunk{N}/artifacts.tar` (2.5 GB for 100 tkr, ~5.25 GB for 200 tkr).
2. **Extract** `output_chunk{N}/trade_log.parquet`, `exit_strategy_comparison.csv`, `env_fingerprint.json`. (The tar has NO plain `summary.json` — do not grab `regime_stratified_summary.json` by mistake; regenerate summary yourself. L217.)
3. **Slim** `trade_log` to the canonical **20 columns** via pyarrow column projection (skips the fat `signals_at_entry`/`context`/`agent` columns that bloat the tar to GBs), write zstd. Canonical 20 cols: `ticker, entry_date, exit_date, direction, strategy, category, sector, confidence_tier, regime, exit_reason, entry_price, exit_price, pnl_pct, pnl_dollar, win, hold_days, max_adverse_excursion, initial_stop, trailing_stop_at_exit, highest_close`.
4. **Regenerate `summary.json`** in the batch-metadata format (fields: `batch, chunk, frozen_sha, window, trades, traded_strategies, tickers_traded, cost_usd, instance_terminated, known_flags`).
5. **Verify `MERGE_CRITICAL` == batch_4** before committing. If it differs, DO NOT commit — investigate.
6. **Commit** `output_batches/batch_<N>/` (4 slim files) + append `batch_ledger.json` + an `EXECUTION_QUEUE.md` note (reword to avoid the C10 false-match). Push. PushNotification.

**Process gap to fix for R6:** the slim commit KEEPS only `trade_log`; the full per-cell CSVs (`backtest_results.csv`, `exit_by_*.csv`) the dashboard needs are DISCARDED with the deleted tar. To build the dashboard you must re-download the full `artifacts.tar` for each batch. Better: at finalize, extract + retain the full `output_chunk{N}/` cube CSVs (or push a `merged` dir to S3) so the dashboard merge does not require a ~10 GB re-download.

---

## 10. Merge + dashboard workflow

### 10.1 Merge
`python scripts/merge_batch_outputs.py --input-dirs <full per-batch dirs...> --output-dir output_r5_merged_<range>` — concatenates ticker-disjoint cubes, rebuilds engine-schema metrics FROM the combined trade_log, dedups the SPY benchmark, and runs `env_fingerprint --check` (HARD-HALT on mismatch). It needs each batch's FULL cube CSVs (not the committed slims) — so re-download the artifacts first (see Section 9 gap).

### 10.2 Dashboard
- **The R5 dashboard is `dashboard_r5_cube/`** (the 22-tab template; `data.js` = `window.PHASE_1A_DATA`, `data.json` for consumers, banner from `current_round` + `archive/cube_rounds/rounds.json`). Built by `scripts/build_dashboard_phase_1a.py --source output_r5_merged_<range> --output-dir dashboard_r5_cube`.
- **Older dashboards** (`dashboard_phase_1a`, `_phase_1a_beta`, `_phase_1b`, `dashboard_r5`) were ARCHIVED 2026-07-24 to `archive/dashboards_pre_r5_2026-07-24/` — superseded by `dashboard_r5_cube`. Retained live: `dashboard_sprint0a` (API coverage), `dashboard_stage_2` (decisions/bugs), `dashboard_r5_cube`.
- **ALWAYS verify the rendered artifact, not just "data generated":** `python scripts/verify_dashboard.py --dir dashboard_r5_cube [--url <deployed>]` (asset-completeness + non-empty data + banner-metadata + live-render). The 8-bug dashboard episode (missing app.js -> stuck loading, 404, empty tabs, R3 banner) all sailed through because nothing checked the ARTIFACT. "Generated the data" != "the page works" (CHECKLIST #128/#163, L217/L218).
- **Deploy:** GitHub Pages via `.github/workflows/deploy_pages.yml` (copies only the retained dashboards). A dashboard dir must be in that workflow's copy-list or the Pages link 404s.

---

## 11. Cost, cadence, budget

- **Hard cap this run: $50 CAD.** Track sunk cost per launch (`batch_ledger.json` `cost_usd` = `wall_min/60 * hourly_rate`); the manifest `spent_usd` tracks total session spend. Through batch 6: ~$36 (ladder batches ~$11.6; the rest is prior R5 attempts + tar builds + dashboard experiments).
- **Spot pricing:** c6a.16xlarge ~$0.60-1.20/hr; a 100-tkr batch ~$2, a 200-tkr batch ~$5.6 (incl. the slow finalization), a resume tail ~$1-2.
- **8 h `MAX_RUN_HOURS`** bounds a single spot-interrupt loss; resume continues the tail.
- **Cadence:** owner-set. This run — AWS 15-min cron + completion push. Match Monitor/cron timeouts to wall-clock.
- **Ladder discipline (L86/L95):** rungs with owner gates; never skip to full universe. **No auto-launch of a paid batch without explicit owner approval** (`feedback_no_auto_launch_batch_b`).

---

## 12. Lessons embedded

| Lesson | Rule it created |
|---|---|
| L86/L95 | never jump data-ready -> full run; validation ladder with owner gates |
| L207 | calendar silent Mon-Fri fallback -> env-fingerprint parity gate (#158) |
| L208 | a mid-sequence correctness fix needs a CROSS-run consistency check |
| L209 | measure materiality before asserting it |
| B1300 | checkpoint shipping can't be interruption-only; success markers must be freshness-checked |
| B1312 | completion markers reflect actual completion, not process exit |
| ENG-1 (B1260) | writer-reader signal contract via `signals_serde.py` -> `signals_at_entry` survives resume |
| L217 | enumerate ALL candidates (dirs/templates/files) before claiming/replicating; restart with full enumeration after a correction |
| L218 | verify the RENDERED artifact end-to-end, not "data generated" |
| L219 | a promised cadence must be MECHANICAL (cron + push), not remember-to-report |
| L220 | a long-run cadence check must verify PROGRESS, not just liveness; change ONE axis at a time (batch 5 changed size AND delisted-inclusion) |
| L221 | a slow checkpoint at 20k+ trades mimics a hang; confirm before the destructive terminate |
| L221b | checkpoint freeze scales with cumulative trades; size a monitor threshold for the WORST case at run's end, not the first sample |
| B1358 | the 200-tkr pool-memory hang; fix via `--pool-workers`/`--instance-type` (launcher-config, frozen-SHA-safe) |

---

## 13. Cross-references

**Code:**
- `scripts/aws_chunk_launch.py` — AWS spot launcher + on-instance monitor + `--pool-workers`/`--instance-type` (B1358) + B1312 marker
- `backtest/run_phase1a.py` — local engine entry; `--cube-isolation`, `--resume-from-checkpoint`
- `backtest/engine/backtest.py` — main loop, annual PIT (`_annual_liquid`), checkpoints, cube-isolation
- `backtest/signals/screener.py` — screen pool (`_pool_init`); `ALL_STRATEGIES`, `EXIT_STRATEGIES`
- `backtest/util/signals_serde.py` — ENG-1 writer-reader contract
- `scripts/env_fingerprint.py` — `--emit`/`--check`; `MERGE_CRITICAL`
- `scripts/prelaunch_gate.py` — zero-spend pre-launch gate
- `scripts/preengine_gate.py` — on-instance frozen-SHA gate
- `scripts/verify_payload_coverage.py` — payload/overlay coverage (note the overlay-index caveat)
- `scripts/merge_batch_outputs.py` — merge + env-parity + dedup
- `scripts/build_dashboard_phase_1a.py` — 22-tab dashboard generator (`--source`, `--output-dir`)
- `scripts/verify_dashboard.py` — rendered-artifact gate
- `scripts/preflight.py` — commit gates C1-C10
- `scripts/verify_turn_compliance.py` — Stop-hook turn gate
- `backtest/tests/conftest.py::pytest_sessionfinish` — C6 pyramid-stamp writer

**Docs (r6_workflow_reuse bundle):**
- `AWS_LAUNCH_PLAYBOOK.md` — AWS-mechanics recipes (AZ failover, spot-capacity, S3 externalization)
- `R5_WORKFLOW.md` — original monolith autoladder + sentinel contract (historical)
- `STRUCTURAL_DEFENSES.md`, `CHECKLIST_INTEGRATION_GUIDE.md`, `COUNCIL_PATTERN_GUIDE.md`, `HONEST_FINDING_PIVOT_PATTERN.md`
- `CLAUDE.md` (project rules), `CHECKLIST.md`, `LEARNINGS.md`, `EXECUTION_QUEUE.md`
- `.claude/skills/execution-discipline/SKILL.md` — turn protocol + GENERALIZATION MANDATE

**Memory rules in force:** `feedback_generalization_mandate_and_premerge_rca`, `feedback_batch_run_update_cadence`, `feedback_no_auto_launch_batch_b`, `feedback_cube_exit_count_must_equal_registered`, `feedback_confirm_existing_template_before_replicating`, `feedback_verify_rendered_artifact_end_to_end`, `feedback_ask_before_relaunching_corrected_version`, `project_r5_path_decisions_2026_07_08`.
