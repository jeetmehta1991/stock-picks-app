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

# Sprint 0A Coverage Dashboard

Interactive HTML dashboard for tracking universe / tier / API / endpoint / field coverage during Sprint 0A prefetch execution.

## Files

- `index.html` — dashboard UI (open directly in browser, no server needed)
- `data.js` — auto-generated snapshot (loaded by index.html)
- `data.json` — same data, JSON form (for programmatic access)
- `last_run.txt` — timestamp of last refresh
- `refresh.bat` — Windows scheduled-task helper

## Usage

### View
Open `dashboard_sprint0a/index.html` in any modern browser (file:// works; no server needed).

### Refresh manually
```bash
python scripts/build_dashboard_sprint0a.py
```

### Hourly auto-refresh (Windows Task Scheduler)
1. Open Task Scheduler → Create Task
2. Trigger: Daily, repeat every 1 hour, indefinitely
3. Action: Start a program
   - Program: `cmd.exe`
   - Arguments: `/c "C:\Users\jeetm\Github\stock-picks-app\dashboard_sprint0a\refresh.bat"`
4. Save

### Hourly auto-refresh (cron-style on a *nix machine)
```
0 * * * * cd /path/to/repo && python scripts/build_dashboard_sprint0a.py
```

## What the dashboard shows

- **API Matrix** — per-API: endpoints accessible / OK / total files cached
- **Endpoint Detail** — every endpoint × coverage % × field count × status; filter + search
- **Ticker Drill-down** — pick any ticker, see coverage across all APIs / endpoints / row counts
- **Field/Dimension Audit** — per-endpoint, all captured columns; identify lost dimensions
- **Status Overview** — counts by status + endpoints below 50% coverage (attention list)

## Status colors

- OK (green): coverage ≥ 80%
- PARTIAL (yellow): 30% ≤ coverage < 80%
- LOW (red): coverage < 30%
- EMPTY (gray): no data

## Drill / drill-through

- Click any ticker's "drill" link → sub-table of all endpoints + row counts for that ticker
- Click any endpoint's field count → expandable list of all captured columns
- Filter API Matrix → filtered Endpoint Detail follows
