# Process-Death Watchdog with Auto-Resume (Batch 1094-A I4 2026-07-02)
# Council 228 Option A: prevents 4-day Batch B silent-death disasters.
#
# Behavior:
#   - Poll engine PID every $PollSeconds
#   - If engine ALIVE + trade_log_checkpoint stale >30 min: alert-only WARN (do not kill; owner decides)
#   - If engine DEAD:
#       - If backtest_results.json exists: clean completion; exit gracefully
#       - Else: fatal death; retry logic:
#           - Wait 60 sec for graceful checkpoint flush
#           - Auto-fix state.json via scripts/fix_engine_state_from_checkpoint.py
#           - Relaunch engine with --resume-from-checkpoint (via Start-Process detached)
#           - Increment retry_count
#           - If retry_count >= MaxRetries: alert-only mode; exit
#
# Usage:
#   .\scripts\laptop_watchdog.ps1 -BatchDir output_batch_B_1787 -EnginePid 12345 -MaxRetries 2

param(
    [Parameter(Mandatory = $true)][string]$BatchDir,
    [Parameter(Mandatory = $true)][int]$EnginePid,
    [int]$MaxRetries = 2,
    [int]$PollSeconds = 60,
    [int]$StaleMinutes = 30
)

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = "C:\Users\jeetm\Github\stock-picks-app"
$VENV_PYTHON = "$PROJECT_ROOT\.venv\Scripts\python.exe"

Set-Location $PROJECT_ROOT

$alertLog = "$BatchDir\WATCHDOG_ALERT.log"
$stateFile = "$BatchDir\watchdog_state.json"

function Write-Alert {
    param([string]$Message, [string]$Level = "INFO")
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$ts] [$Level] $Message"
    Add-Content -Path $alertLog -Value $line
    Write-Host $line
}

function Get-RetryCount {
    if (Test-Path $stateFile) {
        try {
            $state = Get-Content $stateFile -Raw | ConvertFrom-Json
            return [int]$state.retry_count
        } catch { return 0 }
    }
    return 0
}

function Set-RetryCount {
    param([int]$Count, [int]$NewPid = 0)
    @{
        retry_count      = $Count
        last_engine_pid  = $NewPid
        last_update      = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    } | ConvertTo-Json | Out-File -FilePath $stateFile -Encoding utf8
}

# Initialize
Write-Alert "Watchdog starting: BatchDir=$BatchDir EnginePid=$EnginePid MaxRetries=$MaxRetries PollSeconds=$PollSeconds" "INFO"
$currentEnginePid = $EnginePid
$retryCount = Get-RetryCount
Set-RetryCount -Count $retryCount -NewPid $currentEnginePid

# Main loop
while ($true) {
    Start-Sleep -Seconds $PollSeconds

    # 1. Check engine PID alive
    $engineProc = Get-Process -Id $currentEnginePid -ErrorAction SilentlyContinue

    if ($engineProc) {
        # ENGINE ALIVE - check for staleness (trade_log_checkpoint stopped growing)
        $checkpointCsv = "$BatchDir\trade_log_checkpoint.csv"
        if (Test-Path $checkpointCsv) {
            $lastWrite = (Get-Item $checkpointCsv).LastWriteTime
            $staleMin = ((Get-Date) - $lastWrite).TotalMinutes
            if ($staleMin -gt $StaleMinutes) {
                Write-Alert "STALE-WARN: trade_log_checkpoint.csv last written $([math]::Round($staleMin,0)) min ago (>$StaleMinutes min threshold). Engine may be stuck. Alert-only; owner decides intervention." "WARN"
            }
        }
        continue
    }

    # 2. ENGINE DEAD - check for clean completion
    Write-Alert "Engine PID $currentEnginePid no longer alive; investigating..." "WARN"

    # Wait 60 sec for graceful flush
    Start-Sleep -Seconds 60

    if (Test-Path "$BatchDir\backtest_results.json") {
        Write-Alert "backtest_results.json present; treating as CLEAN COMPLETION. Watchdog exiting." "INFO"
        exit 0
    }

    # 3. FATAL DEATH - check retry budget
    $retryCount = Get-RetryCount
    if ($retryCount -ge $MaxRetries) {
        Write-Alert "MaxRetries=$MaxRetries reached. Auto-resume disabled. Alert-only mode; owner must intervene manually." "FATAL"
        Write-Alert "Recovery instructions: (1) inspect $BatchDir\launch.log tail; (2) run scripts/fix_engine_state_from_checkpoint.py --batch-dir $BatchDir; (3) launch resume via appropriate detached script." "INFO"
        exit 2
    }

    # 4. AUTO-FIX state.json from CSV
    $nextRetry = $retryCount + 1
    Write-Alert "Retry $nextRetry/$MaxRetries : auto-fixing state.json from CSV..." "INFO"
    $fixOutput = & $VENV_PYTHON scripts/fix_engine_state_from_checkpoint.py --batch-dir $BatchDir 2>&1
    $fixExit = $LASTEXITCODE
    Write-Alert "fix_engine_state_from_checkpoint.py exit=$fixExit output: $fixOutput" "INFO"

    if ($fixExit -eq 2) {
        Write-Alert "state.json fix failed with error; cannot auto-resume. Exiting alert-only mode." "FATAL"
        exit 3
    }
    # exit 0 = no fix needed (state was already current); exit 1 = fix applied. Both are OK to proceed.

    # 5. RELAUNCH engine detached (same args as original launch)
    Write-Alert "Relaunching engine detached..." "INFO"
    $engineLog = "$BatchDir\launch_retry_$nextRetry.log"
    $engineErr = "$BatchDir\launch_retry_$nextRetry" + "_err.log"
    $engineArgs = @(
        "-u",
        "-m", "backtest.run_phase1a",
        "--phase", "1a-beta",
        "--tickers-file", "$BatchDir\tickers.txt",
        "--start", "2022-05-05",
        "--end", "2026-05-05",
        "--output-dir", "$BatchDir",
        "--resume-from-checkpoint", "$BatchDir",
        "--max-run-hours", "120.0",
        "--warn-run-hours", "100.0",
        "--screen-pool-workers", "1",
        "--no-news",
        "--no-git",
        "--no-walk-forward",
        "--no-agents",
        "--no-portfolio-cap",
        "--no-dd-halt"
    )

    try {
        $newEngine = Start-Process -FilePath $VENV_PYTHON `
            -ArgumentList $engineArgs `
            -RedirectStandardOutput $engineLog `
            -RedirectStandardError $engineErr `
            -WindowStyle Hidden `
            -PassThru `
            -WorkingDirectory $PROJECT_ROOT
        $currentEnginePid = $newEngine.Id
        $retryCount++
        Set-RetryCount -Count $retryCount -NewPid $currentEnginePid
        Write-Alert "Engine relaunched: new PID=$currentEnginePid retry_count=$retryCount log=$engineLog" "INFO"
    } catch {
        Write-Alert "Relaunch FAILED: $_" "FATAL"
        exit 4
    }
}
