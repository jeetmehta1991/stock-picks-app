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
