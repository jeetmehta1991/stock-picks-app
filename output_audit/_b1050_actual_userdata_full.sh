#!/bin/bash
set -uxo pipefail
exec > >(tee /var/log/r5_v2_bootstrap.log) 2>&1
BUCKET=stock-picks-batch395-jm-7421
RUN_ID="r5_full_20260627_205318"
MODE="full"
MAX_PHASE_MIN=360

mkdir -p /tmp/sentinels
echo "BOOT $(date -u +%Y-%m-%dT%H:%M:%SZ) mode=${MODE}" > /tmp/sentinels/BOOT
aws s3 cp /tmp/sentinels/BOOT s3://${BUCKET}/${RUN_ID}/BOOT --quiet

# B-2: Python 3.11 install + VERIFICATION per CHECKLIST #122
dnf install -y git python3.11 python3.11-pip aws-cli 2>&1 | tail -3
python3.11 --version 2>&1 | tee /tmp/sentinels/PYTHON_VERSION || { echo "PYTHON_3_11_FAIL" > /tmp/sentinels/PYTHON_3_11_FAIL; aws s3 cp /tmp/sentinels/PYTHON_3_11_FAIL s3://${BUCKET}/${RUN_ID}/PYTHON_3_11_FAIL --quiet; sudo shutdown -h +5; exit 1; }
aws s3 cp /tmp/sentinels/PYTHON_VERSION s3://${BUCKET}/${RUN_ID}/PYTHON_VERSION --quiet

cd /home/ec2-user
git clone https://github.com/jeetmehta1991/stock-picks-app.git 2>&1 | tail -3
cd stock-picks-app

# B-2: Use python3.11 explicitly (not python3 default)
python3.11 -m venv venv
source venv/bin/activate
python --version  # should now be 3.11

pip install -q --upgrade pip 2>&1 | tail -2

# B-8: pandas-ta install with PAIRED VERIFICATION per CHECKLIST #122
pip install -q pandas numpy scipy pyarrow filelock requests freezegun 2>&1 | tail -3 || true
# Verify mandatory deps
python -c "import pandas, numpy, scipy, pyarrow, filelock, requests, freezegun" || { echo "MANDATORY_DEPS_MISSING" > /tmp/sentinels/MANDATORY_DEPS_MISSING; aws s3 cp /tmp/sentinels/MANDATORY_DEPS_MISSING s3://${BUCKET}/${RUN_ID}/MANDATORY_DEPS_MISSING --quiet; sudo shutdown -h +5; exit 1; }

# pandas-ta is optional (engine falls back per technical.py docstring) BUT we MUST log status per #122
pip install -q pandas-ta 2>&1 | tail -3 || true
python -c "import pandas_ta" 2>/dev/null && HAS_PANDAS_TA=1 || HAS_PANDAS_TA=0
echo "PANDAS_TA_STATUS=${HAS_PANDAS_TA}" > /tmp/sentinels/PANDAS_TA_STATUS
aws s3 cp /tmp/sentinels/PANDAS_TA_STATUS s3://${BUCKET}/${RUN_ID}/PANDAS_TA_STATUS --quiet
if [ "$HAS_PANDAS_TA" = "0" ]; then
    echo "WARN: pandas-ta unavailable; engine will use manual implementations"
fi

pip install -q -r requirements.txt 2>&1 | tail -3 || true

# B1039 Council 132 Item: vendored smartmoneyconcepts install (B416 H1 fix)
# Phase C smoke 2026-06-27 confirmed: ModuleNotFoundError: No module named
# 'smartmoneyconcepts'. Root cause: vendored/smartmoneyconcepts/ exists in
# repo but never installed in AWS user-data. This line fixes that.
# Paired verification per CHECKLIST #122.
pip install -q -e vendored/smartmoneyconcepts/ 2>&1 | tail -3 || true
python -c "from smartmoneyconcepts import smc; assert hasattr(smc, 'swing_highs_lows')" 2>/dev/null && HAS_SMC=1 || HAS_SMC=0
echo "SMARTMONEYCONCEPTS_STATUS=${HAS_SMC}" > /tmp/sentinels/SMARTMONEYCONCEPTS_STATUS
aws s3 cp /tmp/sentinels/SMARTMONEYCONCEPTS_STATUS s3://${BUCKET}/${RUN_ID}/SMARTMONEYCONCEPTS_STATUS --quiet
if [ "$HAS_SMC" = "0" ]; then
    echo "WARN: smartmoneyconcepts unavailable; 18 SMC strategies will short-circuit per SMC_PHASE=B-CANARY"
fi

python -c "from backtest.signals.screener import ALL_STRATEGIES; print(f'STRATEGIES={len(ALL_STRATEGIES)}')" || { echo "STRATEGY_IMPORT_FAIL" > /tmp/sentinels/STRATEGY_IMPORT_FAIL; aws s3 cp /tmp/sentinels/STRATEGY_IMPORT_FAIL s3://${BUCKET}/${RUN_ID}/STRATEGY_IMPORT_FAIL --quiet; sudo shutdown -h +5; exit 1; }

mkdir -p data_prefetch output_phase_smoke output_phase_1 output_phase_2 output_phase_3 output_phase_4_r5
aws s3 sync s3://${BUCKET}/data_prefetch/ data_prefetch/ --quiet --no-progress
echo "DATA_SYNC_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/sentinels/DATA_SYNC_DONE
aws s3 cp /tmp/sentinels/DATA_SYNC_DONE s3://${BUCKET}/${RUN_ID}/DATA_SYNC_DONE --quiet

# B-3/B-4/B-6: 60s S3 sync background loop (engine-progress equivalent)
# B1046 F-10 fix: atomic-snapshot read is enforced jointly by
#   (i) engine-side os.replace atomicity for engine_state.json + trade_log_
#       checkpoint.csv (backtest.py F-11/F-28 fixes), AND
#   (ii) --exclude '*.tmp' on the sync source side here.
# Together these guarantee monitors/sync never see partial-write states.
sync_loop() {
    while true; do
        aws s3 sync /home/ec2-user/stock-picks-app/output_phase_smoke/ s3://${BUCKET}/${RUN_ID}/output_phase_smoke/ --quiet --exclude '*.tmp' 2>/dev/null
        aws s3 sync /home/ec2-user/stock-picks-app/output_phase_1/ s3://${BUCKET}/${RUN_ID}/output_phase_1/ --quiet --exclude '*.tmp' 2>/dev/null
        aws s3 sync /home/ec2-user/stock-picks-app/output_phase_2/ s3://${BUCKET}/${RUN_ID}/output_phase_2/ --quiet --exclude '*.tmp' 2>/dev/null
        aws s3 sync /home/ec2-user/stock-picks-app/output_phase_3/ s3://${BUCKET}/${RUN_ID}/output_phase_3/ --quiet --exclude '*.tmp' 2>/dev/null
        aws s3 sync /home/ec2-user/stock-picks-app/output_phase_4_r5/ s3://${BUCKET}/${RUN_ID}/output_phase_4_r5/ --quiet --exclude '*.tmp' 2>/dev/null
        sleep 60
    done
}
sync_loop &
SYNC_PID=$!

# B1046 F-21 helper: guarded kill with empty-PID visibility.
# Source: B1045 F-21 + CHECKLIST #122 silent-failure-pairing.
guarded_kill() {
    local pid_var="$1"
    local label="$2"
    if [ -n "${pid_var:-}" ]; then
        kill "${pid_var}" 2>/dev/null || echo "WARN: kill ${label} pid=${pid_var} failed (already exited)"
    else
        echo "WARN: ${label} PID empty -- skip kill (silent-failure-pairing visibility per F-21)"
    fi
}

# B1046 F-33 helper: paired-verification S3 cp for CRITICAL sentinels.
# Source: B1045 F-33 + CHECKLIST #122. Non-critical sentinels (progress,
# heartbeat) use ; critical (PASS/FAIL/COMPLETE) use this.
s3_cp_or_warn() {
    local src="$1"; local dst="$2"
    aws s3 cp "${src}" "${dst}" --quiet || echo "WARN: S3_CP_FAIL src=${src} dst=${dst}"
}
echo "SYNC_LOOP_PID=${SYNC_PID}" > /tmp/sentinels/SYNC_LOOP_PID
aws s3 cp /tmp/sentinels/SYNC_LOOP_PID s3://${BUCKET}/${RUN_ID}/SYNC_LOOP_PID --quiet

# B-7: Phase timing watchdog (CHECKLIST #123)
phase_watchdog() {
    PHASE_NUM=$1
    MAX_MIN=$2
    PHASE_PID=$3
    sleep $((MAX_MIN * 60))
    if kill -0 $PHASE_PID 2>/dev/null; then
        echo "PHASE_${PHASE_NUM}_TIMEOUT_HALT $(date -u +%Y-%m-%dT%H:%M:%SZ) max=${MAX_MIN}min" > /tmp/sentinels/PHASE_${PHASE_NUM}_TIMEOUT_HALT
        aws s3 cp /tmp/sentinels/PHASE_${PHASE_NUM}_TIMEOUT_HALT s3://${BUCKET}/${RUN_ID}/PHASE_${PHASE_NUM}_TIMEOUT_HALT --quiet
        kill -9 $PHASE_PID 2>/dev/null
    fi
}

run_phase() {
    PHASE_NUM=$1
    TICKERS=$2
    PHASE_DIR=$3
    START_DATE=$4
    END_DATE=$5
    MAX_MIN=$6
    NCNT=$(echo "${TICKERS}" | tr ',' '\n' | wc -l)
    echo "=== PHASE ${PHASE_NUM} START: ${NCNT} tickers window=${START_DATE}..${END_DATE} max=${MAX_MIN}min ==="
    echo "PHASE_${PHASE_NUM}_RUNNING $(date -u +%Y-%m-%dT%H:%M:%SZ) n=${NCNT}" > /tmp/sentinels/PHASE_${PHASE_NUM}_RUNNING
    aws s3 cp /tmp/sentinels/PHASE_${PHASE_NUM}_RUNNING s3://${BUCKET}/${RUN_ID}/PHASE_${PHASE_NUM}_RUNNING --quiet
    mkdir -p ${PHASE_DIR}

    # B1043 F-02 + F-06: process substitution captures engine PID (not tee).
    # B1046 F-24 fix: launch engine via setsid -> new process group so a
    # negative-PID kill (kill -TERM -${ENGINE_PID}) propagates SIGTERM to
    # all 60 screen_pool worker subprocesses. Source: B1045 F-24 +
    # CHECKLIST #122 silent-failure-pairing rule.
    set +e
    export ENGINE_OUTPUT_DIR="${PHASE_DIR}"
    setsid python -m backtest.run_phase1a --phase 1a-beta --tickers "${TICKERS}" --start ${START_DATE} --end ${END_DATE} --no-news --no-git --no-walk-forward --output-dir ${PHASE_DIR} --screen-pool-workers 60 > ${PHASE_DIR}/engine.log 2>&1 &
    ENGINE_PID=$!
    phase_watchdog ${PHASE_NUM} ${MAX_MIN} $ENGINE_PID &
    WATCHDOG_PID=$!

    # B1042 Layer 2 + B1043 F-03/F-04/F-09: B1019 monitor wrap with corrected
    # baseline path + csv/parquet dispatch + active in smoke too.
    python scripts/b1019_phase_1_runtime_monitor.py \
        --engine-state ${PHASE_DIR}/engine_state.json \
        --trade-log ${PHASE_DIR}/trade_log_checkpoint.csv \
        --baseline output_audit/fire_count_measured_b660_full_universe.json \
        --poll-seconds 60 \
        --total-days 1006 \
        --total-cells 5694 \
        > ${PHASE_DIR}/b1019_monitor.log 2>&1 &
    B1019_PID=$!
    echo "B1019_MONITOR_PID=${B1019_PID} phase=${PHASE_NUM}" > /tmp/sentinels/PHASE_${PHASE_NUM}_B1019_PID
    aws s3 cp /tmp/sentinels/PHASE_${PHASE_NUM}_B1019_PID s3://${BUCKET}/${RUN_ID}/PHASE_${PHASE_NUM}_B1019_PID --quiet
    # B1019 HALT-CRITICAL watcher: SIGTERM engine if monitor signals halt.
    # B1046 F-34 fix: nohup + disown -h detaches subshell from session so
    # SIGHUP on parent exit does not orphan-kill watcher mid-poll. Source:
    # B1045 F-34 per CHECKLIST #122. Also F-24: send SIGTERM to engine
    # process-GROUP via negative-PID (kill -15 -$ENGINE_PID) so all 60
    # screen_pool workers receive teardown signal too.
    nohup bash -c "while kill -0 $ENGINE_PID 2>/dev/null && kill -0 $B1019_PID 2>/dev/null; do
          sleep 60
          if grep -q 'HALT-CRITICAL' ${PHASE_DIR}/b1019_monitor.log 2>/dev/null; then
              echo \"PHASE_${PHASE_NUM}_B1019_HALT $(date -u +%Y-%m-%dT%H:%M:%SZ)\" > /tmp/sentinels/PHASE_${PHASE_NUM}_B1019_HALT
              aws s3 cp /tmp/sentinels/PHASE_${PHASE_NUM}_B1019_HALT s3://${BUCKET}/${RUN_ID}/PHASE_${PHASE_NUM}_B1019_HALT --quiet || echo \"WARN: S3_CP_FAIL PHASE_${PHASE_NUM}_B1019_HALT\"
              kill -15 -$ENGINE_PID 2>/dev/null || kill -15 $ENGINE_PID 2>/dev/null
              break
          fi
      done" >/dev/null 2>&1 &
    HALT_WATCHER_PID=$!
    disown -h $HALT_WATCHER_PID 2>/dev/null || true

    wait $ENGINE_PID
    RC=$?
    # B1043 cleanup: kill watcher + monitor + watchdog (avoid PID leakage).
    # B1046 F-21 fix: each kill is guarded with explicit empty-PID WARN log
    # for silent-failure-pairing visibility per CHECKLIST #122.
    if [ -n "${B1019_PID:-}" ]; then kill $B1019_PID 2>/dev/null || echo "WARN: kill B1019_PID=${B1019_PID} failed (already exited)"; else echo "WARN: B1019_PID empty -- skip kill (F-21 visibility)"; fi
    if [ -n "${HALT_WATCHER_PID:-}" ]; then kill $HALT_WATCHER_PID 2>/dev/null || echo "WARN: kill HALT_WATCHER_PID=${HALT_WATCHER_PID} failed"; else echo "WARN: HALT_WATCHER_PID empty -- skip kill (F-21)"; fi
    if [ -n "${WATCHDOG_PID:-}" ]; then kill $WATCHDOG_PID 2>/dev/null || echo "WARN: kill WATCHDOG_PID=${WATCHDOG_PID} failed"; else echo "WARN: WATCHDOG_PID empty -- skip kill (F-21)"; fi
    set -e

    # Sync final state
    aws s3 sync ${PHASE_DIR}/ s3://${BUCKET}/${RUN_ID}/${PHASE_DIR}/ --quiet

    if [ $RC -ne 0 ]; then
        echo "PHASE_${PHASE_NUM}_FAIL rc=${RC} $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/sentinels/PHASE_${PHASE_NUM}_FAIL
        aws s3 cp /tmp/sentinels/PHASE_${PHASE_NUM}_FAIL s3://${BUCKET}/${RUN_ID}/PHASE_${PHASE_NUM}_FAIL --quiet
        return 1
    fi
    if [ ! -f ${PHASE_DIR}/trade_log.parquet ] && [ ! -f ${PHASE_DIR}/trade_log.csv ]; then
        echo "PHASE_${PHASE_NUM}_FAIL no-trade-log $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/sentinels/PHASE_${PHASE_NUM}_FAIL
        aws s3 cp /tmp/sentinels/PHASE_${PHASE_NUM}_FAIL s3://${BUCKET}/${RUN_ID}/PHASE_${PHASE_NUM}_FAIL --quiet
        return 1
    fi
    echo "PHASE_${PHASE_NUM}_PASS $(date -u +%Y-%m-%dT%H:%M:%SZ) n=${NCNT}" > /tmp/sentinels/PHASE_${PHASE_NUM}_PASS
    aws s3 cp /tmp/sentinels/PHASE_${PHASE_NUM}_PASS s3://${BUCKET}/${RUN_ID}/PHASE_${PHASE_NUM}_PASS --quiet
    return 0
}

# SMOKE MODE (Phase C): 1-ticker x 1-month with 15-min hard cap
if [ "${MODE}" = "smoke" ]; then
    run_phase smoke "NVDA" output_phase_smoke "2026-04-01" "2026-05-01" ${MAX_PHASE_MIN}
    SMOKE_RC=$?
    # B1046 F-21 fix: guarded SYNC_PID kill with explicit empty-PID WARN log.
    if [ -n "${SYNC_PID:-}" ]; then kill $SYNC_PID 2>/dev/null || echo "WARN: kill SYNC_PID=${SYNC_PID} failed (already exited)"; else echo "WARN: SYNC_PID empty -- skip kill (F-21 visibility)"; fi
    # Final sync
    aws s3 sync output_phase_smoke/ s3://${BUCKET}/${RUN_ID}/output_phase_smoke/ --quiet
    if [ $SMOKE_RC -eq 0 ]; then
        echo "SMOKE_COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/sentinels/SMOKE_COMPLETE
        aws s3 cp /tmp/sentinels/SMOKE_COMPLETE s3://${BUCKET}/${RUN_ID}/SMOKE_COMPLETE --quiet
    fi
    sudo shutdown -h +1
    exit 0
fi

# FULL MODE (Phase D): full ladder Phase 1 -> 2 -> 3 -> R5
# B1046 F-33 fix: CRITICAL PUT/GET pairs explicit error-check per CHECKLIST
# #122. Master tickers download is highest-criticality (Phase D inputs).
# Non-critical sentinel uploads (PHASE_RUNNING, PASS heartbeats) keep the
# implicit success pattern; high-criticality download paths get paired check.
aws s3 cp s3://${BUCKET}/r5_master_20260627_064008/master_ops_tickers.txt /tmp/master_ops_tickers.txt --quiet || { echo "S3_CP_FAIL_CRITICAL: master_ops_tickers.txt download failed (F-33)"; aws s3 cp /tmp/sentinels/AUTOLADDER_COMPLETE s3://${BUCKET}/${RUN_ID}/MASTER_TICKERS_DOWNLOAD_FAIL --quiet 2>/dev/null; sudo shutdown -h +5; exit 1; }
if [ ! -s /tmp/master_ops_tickers.txt ]; then echo "S3_CP_FAIL_CRITICAL: master_ops_tickers.txt empty after download (F-33)"; sudo shutdown -h +5; exit 1; fi
MASTER_TICKERS=$(cat /tmp/master_ops_tickers.txt)
TICKERS_PHASE_2="NVDA,AAPL,MSFT,GOOGL,META,XLF,UUP,COIN,SOFI,IONQ"
TICKERS_PHASE_3=$(python -c "ts='${MASTER_TICKERS}'.split(','); n=len(ts); step=max(1,n//50); print(','.join(ts[::step][:50]))")
START_DATE="2022-05-05"
END_DATE="2026-05-05"

# B1043 F-07 + B1049 PIVOT #29 fix: invoke preflight before Phase 1.
# B1049: PHASE_DIR was undefined at this point (set only inside run_phase
# function called later). Under set -u, bash errored on unbound var ->
# preflight never ran -> B1019_PREFLIGHT_FAIL sentinel fired via ||
# fallback -> Phase D HALTED at cost ~$0.50. Fix: use literal output_phase_1
# since this preflight is Phase 1-specific.
echo "=== B1019 PREFLIGHT: Phase 1 coverage check ==="
mkdir -p output_phase_1
python scripts/b1019_a5_phase_1_preflight_coverage_check.py \
    --ticker NVDA --start ${START_DATE} --end ${END_DATE} \
    --output output_phase_1/b1019_a5_preflight_report.json 2>&1 | head -50 || {
    echo "B1019_PREFLIGHT_FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/sentinels/B1019_PREFLIGHT_FAIL
    aws s3 cp /tmp/sentinels/B1019_PREFLIGHT_FAIL s3://${BUCKET}/${RUN_ID}/B1019_PREFLIGHT_FAIL --quiet
    sudo shutdown -h +5
    exit 1
}
echo "B1019_PREFLIGHT_PASS $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/sentinels/B1019_PREFLIGHT_PASS
aws s3 cp /tmp/sentinels/B1019_PREFLIGHT_PASS s3://${BUCKET}/${RUN_ID}/B1019_PREFLIGHT_PASS --quiet

# B1043 Sub-C: MAX_MIN raised per timing extrapolation (Phase 1 30->120;
# Phase 2 60->180; Phase 3 90->240; Phase 4 240->480; cumulative 7hr->17hr).
# B1046 F-21 fix: each || branch guards SYNC_PID kill with empty-check + WARN.
run_phase 1 "NVDA" output_phase_1 ${START_DATE} ${END_DATE} 120 || { if [ -n "${SYNC_PID:-}" ]; then kill $SYNC_PID 2>/dev/null || echo "WARN: SYNC_PID kill failed"; else echo "WARN: SYNC_PID empty (F-21)"; fi; aws s3 sync /tmp/sentinels/ s3://${BUCKET}/${RUN_ID}/sentinels/ --quiet; sudo shutdown -h +5; exit 1; }
run_phase 2 "${TICKERS_PHASE_2}" output_phase_2 ${START_DATE} ${END_DATE} 180 || { if [ -n "${SYNC_PID:-}" ]; then kill $SYNC_PID 2>/dev/null || echo "WARN: SYNC_PID kill failed"; else echo "WARN: SYNC_PID empty (F-21)"; fi; aws s3 sync /tmp/sentinels/ s3://${BUCKET}/${RUN_ID}/sentinels/ --quiet; sudo shutdown -h +5; exit 1; }
run_phase 3 "${TICKERS_PHASE_3}" output_phase_3 ${START_DATE} ${END_DATE} 240 || { if [ -n "${SYNC_PID:-}" ]; then kill $SYNC_PID 2>/dev/null || echo "WARN: SYNC_PID kill failed"; else echo "WARN: SYNC_PID empty (F-21)"; fi; aws s3 sync /tmp/sentinels/ s3://${BUCKET}/${RUN_ID}/sentinels/ --quiet; sudo shutdown -h +5; exit 1; }
run_phase 4 "${MASTER_TICKERS}" output_phase_4_r5 ${START_DATE} ${END_DATE} 480 || { if [ -n "${SYNC_PID:-}" ]; then kill $SYNC_PID 2>/dev/null || echo "WARN: SYNC_PID kill failed"; else echo "WARN: SYNC_PID empty (F-21)"; fi; aws s3 sync /tmp/sentinels/ s3://${BUCKET}/${RUN_ID}/sentinels/ --quiet; sudo shutdown -h +5; exit 1; }

# B1046 F-21 fix: final SYNC_PID kill guarded with empty-check + WARN log.
if [ -n "${SYNC_PID:-}" ]; then kill $SYNC_PID 2>/dev/null || echo "WARN: SYNC_PID=${SYNC_PID} kill failed (already exited)"; else echo "WARN: SYNC_PID empty -- skip kill (F-21 visibility)"; fi

# B1043 F-08: invoke post-run analyzer (was orphan script).
echo "=== B1019 POST-RUN: Phase 4 analyzer ==="
PHASE_4_TRADE_LOG="output_phase_4_r5/trade_log.parquet"
[ -f "${PHASE_4_TRADE_LOG}" ] || PHASE_4_TRADE_LOG="output_phase_4_r5/trade_log.csv"
if [ -f "${PHASE_4_TRADE_LOG}" ]; then
    python scripts/b1019_phase_1_post_run_analyzer.py \
        --trade-log "${PHASE_4_TRADE_LOG}" \
        --report output_phase_4_r5/b1019_post_run_report.json \
        --summary output_phase_4_r5/b1019_post_run_summary.md 2>&1 | head -30 || true
    aws s3 cp output_phase_4_r5/b1019_post_run_report.json s3://${BUCKET}/${RUN_ID}/B1019_POST_RUN_REPORT.json --quiet || true
    aws s3 cp output_phase_4_r5/b1019_post_run_summary.md s3://${BUCKET}/${RUN_ID}/B1019_POST_RUN_SUMMARY.md --quiet || true
else
    echo "[B1043 F-08 WARN] Phase 4 trade_log missing; skipping post-run analyzer"
fi

echo "AUTOLADDER_COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ) scope=Master-1929 4y" > /tmp/sentinels/AUTOLADDER_COMPLETE
aws s3 cp /tmp/sentinels/AUTOLADDER_COMPLETE s3://${BUCKET}/${RUN_ID}/AUTOLADDER_COMPLETE --quiet
aws s3 sync /tmp/sentinels/ s3://${BUCKET}/${RUN_ID}/sentinels/ --quiet
sudo shutdown -h +1
