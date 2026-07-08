<!-- Source: per CHECKLIST #77 canonical-source; Council 296 B1250 2026-07-08 engine bug audit for R5 readiness -->
# B1250 ENGINE BUG AUDIT — all layers, R5 readiness (2026-07-08, Council 296)

**Method:** source reads + pattern greps for known bug classes + RUNTIME PROBES (key-mismatch probe 8 tickers x 4 dates; literal_eval round-trip probe; trade_log forensics 8,433 Batch A trades; fresh 3-ticker/6-month mini-run end-to-end). Every finding classified VERIFIED (runtime/source evidence) or SUSPECTED (needs follow-up). All findings ticketed in EXECUTION_QUEUE B1250. Layer-coverage table at bottom states exactly what was and was not audited — no silent scope misses.

---

## HEADLINE: one P0 defect explains a cluster of known anomalies

### ENG-1 (P0, VERIFIED) — `signals_at_entry` is WIPED for every trade on every checkpoint/resume round-trip

**Mechanism (all steps verified by execution):**
1. Engine checkpoint (backtest.py:883) writes `str(dict)` containing **numpy scalar reprs** (`np.float64(45.2)`, `np.True_`) and **`nan`**.
2. writer.py final CSV JSON-stringifies complex columns (**`true`/`false`/`null`**).
3. The resume reader `_csv_row_to_closed_trade._parse_literal` (backtest.py:526) uses `ast.literal_eval`, which **fails on BOTH formats** (probe: `ValueError: malformed node` on `np.float64(...)`, on bare `nan`, and on JSON `false`) → silently returns the default `{}`.

**Empirical impact (Batch A, EXECUTED):** 255/255 sampled trades across 2022-2026 carry only 0-4 signal keys (the 4 keys added AFTER the `**cand["signals"]` expansion at backtest.py:2533). A fresh mini-run (3 tickers, 2024H1, 29 trades) carries the FULL ~20,053-char dict including `vix_band` + `rsi_14` — proving the live path is healthy and the loss is the resume round-trip (Batch A resumed at least once; resume infra is the DEFAULT posture per Council 201, so **every R5 run will hit this**).

**Blast radius:**
- Cube replay reads `sig.get("atr", entry_price*0.02)` (backtest.py:2943) → **ATR = crude 2%-of-price proxy for every replayed trade**.
- ALL signal-conditional exits in the cube (`atr_trail_vix_conditional`, `atr_trail_mae_conditional`, `smart_money_reversal`, `smc_mitigation_zone`, `reverse_signal`, `mfe_lockin` base) silently degrade to their fallback trails — **this root-causes the B1248 finding that these exits have medians IDENTICAL to `atr_trail_1x`**, and root-causes B1249 tickets S6-B1248-MAE-CONDITIONAL-NOOP + (partially) S6-B1248-REGIME-FLIP-DEGENERACY.
- Any signals-conditioned analytics on the trade log (confluence slicing, OR-arm attribution per S6-B1248-OR-ARM-ATTRIBUTION) are impossible on resumed runs.

**Fix rec (owner approval):** serialize `signals_at_entry` with `json.dumps` + explicit type coercion (numpy→python, nan→null) in BOTH writers; read with `json.loads` + `literal_eval` fallback for legacy files; PIN TEST: round-trip a dict containing np.float64/np.True_/nan/nested list through checkpoint-write→resume-read and assert key-count equality (PIVOT #37 writer-reader contract class). Then **re-run the exit cube before trusting any best-exit selection** — B1248's exit-method table has a visible caveat added this batch.

---

## VERIFIED GENUINE FINDINGS (fix recommended; owner-gated)

| ID | P | Finding | Evidence | Fix rec |
|---|---|---|---|---|
| ENG-1 | P0 | signals_at_entry resume wipe (above) | probes + 255-trade forensic + mini-run | JSON round-trip + pin test |
| ENG-2 | P0 | Cube replay ATR = 2%-of-price fallback for all Batch A trades (consequence of ENG-1 but independently fragile: no warning when fallback used) | backtest.py:2943 READ + ENG-1 | log-once counter on fallback + assert <5% fallback rate post-fix |
| ENG-3 | P1 | `trade_log.parquet` (DEC-491 CANONICAL artifact) MISSING from Batch A output; write failure degrades to warning-only (writer.py:76-82, CHECKLIST #122 class). Mini-run writes it fine — Batch A failure cause TBD | dir listing + source READ + mini-run | explicit success-check + post-run artifact assert in launch scripts |
| ENG-4 | P1 | `lead_lag_sector_rotation` REGISTRY BYPASS: DEC-458 merge injects candidates directly in screen_universe (screener.py:9058+) — 792 Batch A trades from a strategy NOT in ALL_STRATEGIES; escapes fire-count gates, roster, per-strategy tests, B1248/B1249 reviews | exit_compare reconcile + source READ | register formally (with category/affinity) OR remove merge; resolves S6-B1248-LEAD-LAG-ORPHAN |
| ENG-5 | P1 | Pool worker `except Exception: return None` (screener.py:8956) — any per-ticker crash silently drops that ticker's candidates for the day; systematic producer bugs = silent universe shrinkage | source READ | pair with `_log_silent_producer_failure`-style one-shot log + per-day dropped-ticker counter (CHECKLIST #122) |
| ENG-6 | P1 | LIVE banned pattern `not s.get("above_avwap_20high", True)` in strat_avwap_20high_rejection_short (screener.py:5225) — missed in the B612 conversion sweep; silent-kill when producer key absent; ALSO label says `vol_spike_15x` while gate is `vol_spike_12x` (5228 vs 5233) | source READ | convert to positive `below_avwap_20high` (B609 producer exists) + align label; explains part of this strategy's FS status |
| ENG-7 | P1 | `hanging_man` + `dark_cloud_cover` CONSUMED-NEVER-PRODUCED (screener.py:2549; zero producer hits repo-wide) — 2 of 4 OR-arms dead in shooting_star_short | grep + key-mismatch probe (8 tickers x 4 dates, 776 emitted keys, both absent) | add the 2 candle producers (Nison canonical) or drop the arms |
| ENG-8 | P2 | Relative `Path("data_prefetch/...")` in engine hot path: backtest.py:1332 (bear-composite yield-curve/AAII) + run_phase1a.py + config.py (2) — cwd-sensitive; silently degrades bear score to 0 when launched from another dir | grep count (6 occurrences, 3 files); macro.py verified `__file__`-anchored (safe) | normalize all to `__file__`-anchored roots |
| ENG-9 | P2 | `entry_date=as_of` (SIGNAL date) recorded while fill is next-bar open (backtest.py:2517 + 2655) — time-stop exits and hold-day metrics count from signal day = 1-day systematic bias; also exit scans include fill day correctly but "10d time stop" is really 9 post-fill days | source READ | record `fill_date` field; time-stops anchor on fill_date |
| ENG-10 | P2 | Checkpoint CSV write `except Exception: pass` (backtest.py:888-889) — atomic-pair flag stays False (pair-gating works) but the failure itself is never logged | source READ | add one-shot warning (CHECKLIST #122 pairing) |
| ENG-11 | P3 | Pool path drops `panel_signals` (worker call screener.py:8951-8955 lacks kwarg) while USE_PANEL_TECHNICAL_SIGNALS=True — panel pre-pass computed then discarded under pool mode. CORRECTNESS SAFE (skip-set is argument-conditional, verified 8386-8390); pure perf waste | source READ | pass panel dict through work_items or skip pre-pass when pool active |

## VERIFIED BENIGN / CORRECT (audit confirmations — no action)

| Area | Verdict | Evidence |
|---|---|---|
| SMC library 1-bar FVG + swing_length lookahead | HANDLED — `get_primitives_at` masks FVG at idx-1, swing-dependent at idx-swing_length; engine consumes only via masked path | smc_panel_cache.py:130-168 READ; consumers grep (backtest.py:687, smc_ict.py:154) |
| 52w-high/low + Donchian breakout levels | Exclude today's bar (B582/B584 fixes in place) | technical.py:1733-1743, 1445-1452 READ |
| Floor pivots / Camarilla / CPR | Computed from PRIOR bar (`df.iloc[-2]`) — no lookahead | technical.py:64-84 READ |
| Entry execution | Signal at as_of close → fill at NEXT bar open + gap filter + slippage | backtest.py:2056-2088, 2655-2662 READ |
| Exit ordering | Stop-hit check (yesterday's stop) BEFORE trail update — no same-bar leak | exit_manager.py:883 vs 909 |
| PIT choke point | `df[df.index.date <= as_of]` inclusive slice at engine + pool worker — 163 producer `iloc[-1]` uses safe given sliced input | backtest.py:1271; screener.py:8940-8944 |
| B657 weekly Kumo defaults | Live code uses default False (1399-1400 match was the docstring) | screener.py:1419-1420 |
| yfinance HARD CUT | `_fetch_from_yfinance` is a no-op stub returning empty + warning | cache.py:85-104 READ |
| VIX overlay wiring | Works end-to-end on fresh run (vix_band present in mini-run signals) — the "Batch A missing VIX" hypothesis was DISPROVEN mid-audit and superseded by ENG-1 | mini-run probe |
| Earnings PIT | `fetch_earnings_dates(as_of=entry_date)` per B1009 INV-057 | exit_strategies.py:514 READ |
| metrics.py datetime.now | Dashboard freshness banner only — not in scoring path | metrics.py:2020-2054 READ |
| BUG-287 stuck-ticker exit coverage | Open-trade tickers force-included in ohlcv_pit for exit checks | backtest.py:1295-1303 READ |

## Layer-coverage statement (no silent scope misses)

| Layer | Depth this audit |
|---|---|
| Engine core loop (backtest.py) | DEEP: PIT slice, regime, entry, exits, checkpoint/resume, cube replay |
| Exit layer (exit_manager + exit_strategies) | MEDIUM: ordering + earnings + vix/mae paths (B1248 covered per-method empirics) |
| Screener gates (screener.py) | MEDIUM: pattern sweeps (default-True, not-s.get, key-mismatch probe); NOT a per-strategy re-read (B1248 covered per-strategy) |
| Producers (signals/*) | MEDIUM: lookahead sweep + exception-swallow census + candle/pivot/52w/dc verification; congressional/chart_patterns swallow-blocks noted, individually unverified |
| Data layer (cache.py, macro.py, fetcher.py) | MEDIUM: get_ohlcv paths + HARD CUT + path anchoring; universe.py NOT deep-audited this pass (PIT loader has existing DEC-504 test coverage) |
| Results (writer.py, metrics.py) | LIGHT: serialization contract (ENG-1/3) + clock sweep; metrics formulas not re-derived (existing 14-criteria tests) |
| Agents / paper_trading / live_trading | NOT AUDITED (out of R5 scope — no agents in Phase 1A-beta) |

**R5 gate recommendation:** ENG-1 + ENG-2 + ENG-3 are pre-R5 blockers (resume is the default rollback path; a resumed R5 without the fix produces a trade log whose exit-cube replay is invalid). ENG-4-7 are strongly recommended pre-R5 (each is a quiet-fire/incorrect-fire class). ENG-8-11 can ship in the following batches.
