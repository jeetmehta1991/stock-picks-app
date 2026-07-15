<!-- Source: per CHECKLIST #77 canonical-source; B1278 Council 317 2026-07-15 owner-requested migration guide -->
# Laptop Migration Guide — project + Claude Code + VS Code + session continuity

**Written B1278 (2026-07-15) at owner request. Measured payloads: repo (git) + 2.8 GB `data_prefetch/` + 0.1 GB OHLCV cache + ~434 MB Claude session/memory folder. Python 3.14.4.**

**CRITICAL PATH RULE (read first):** Claude Code keys sessions AND persistent memory to the project's *absolute path* (slug `c--Users-<user>-Github-stock-picks-app`). To carry this session and memory over losslessly, the project MUST live at the same-shaped path on the new laptop: `C:\Users\<newuser>\Github\stock-picks-app`. If `<newuser>` differs from `jeetm`, you must RENAME the copied Claude project folder to match the new slug (step 4c).

## Step 1 — New laptop prerequisites
1. Install: Git for Windows, Python 3.14.x (match minor version), VS Code, Node.js LTS (if using npm-based Claude Code install).
2. Install Claude Code: `npm install -g @anthropic-ai/claude-code` (or the native installer) → run `claude` once → log in with the SAME Anthropic account (jeetmehta1991@gmail.com).

## Step 2 — Repo (git-tracked content)
```powershell
mkdir C:\Users\<newuser>\Github; cd C:\Users\<newuser>\Github
git clone https://github.com/jeetmehta1991/stock-picks-app.git
```
Auth: issue a fresh fine-grained PAT (repo-scoped, 30d) per the CLAUDE.md PAT pattern. NEVER write it into any repo file.

Then install the compliance hooks (they live in `.git/`, which does NOT clone — AWS_LAUNCH_PLAYBOOK Gate 5):
```powershell
cd stock-picks-app
scripts\install_git_hooks.bat
```

## Step 3 — Non-git payload (external SSD or LAN robocopy from OLD laptop)
These are gitignored/untracked and MUST be copied manually:
| What | Path (relative to repo root) | Size |
|---|---|---|
| Data prefetch caches | `data_prefetch\` (36 subdirs incl. finnhub/finra/fred/quiver/polygon) | 2.8 GB |
| OHLCV cache | `backtest\data\cache\` | 0.1 GB |
| Run outputs (rungs 1-3 + Batch A) | `output_r5_rung1\`, `output_r5_rung2\`, `output_r5_rung3\`, `output_batch_A_150\`, `output_audit\` untracked members, `.archive\` | check sizes |
| Secrets | `.env` (API keys: Polygon, Quiver, FRED, Finnhub...) — transfer via secure channel, never email/commit | KB |

```powershell
# From OLD laptop (adjust target):
robocopy C:\Users\jeetm\Github\stock-picks-app\data_prefetch  \\NEWLAPTOP\share\data_prefetch /E /Z /MT:8
robocopy C:\Users\jeetm\Github\stock-picks-app\backtest\data\cache \\NEWLAPTOP\share\cache /E /Z /MT:8
```

## Step 4 — Claude Code session + memory (THE no-context-loss step)
The whole conversation history (all session .jsonl transcripts, including the current R5-ladder session) AND the persistent memory (feedback_* rules, R5 path decisions) live in ONE folder on the old laptop:
```
C:\Users\jeetm\.claude\projects\c--Users-jeetm-Github-stock-picks-app\   (~434 MB)
```
4a. Copy that entire folder to the new laptop under `C:\Users\<newuser>\.claude\projects\`.
4b. Also copy user-level config if customized: `C:\Users\jeetm\.claude\settings.json`, `keybindings.json`, `CLAUDE.md` (user-global, if any). Do NOT copy `.claude.json` credentials — log in fresh.
4c. **If the username differs**, rename the copied folder so the slug matches the new project path, e.g. `c--Users-bob-Github-stock-picks-app`.
4d. Verify: `cd C:\Users\<newuser>\Github\stock-picks-app` then `claude --resume` → the session list must show this project's sessions; pick the latest (R5 ladder) to continue with full context. `claude --continue` opens the most recent directly.

Note: even if transcript resume ever failed, the DURABLE context is triple-redundant by design: repo docs (CLAUDE.md banner, EXECUTION_QUEUE batch log through B1278, audit docs) + the memory folder + this guide. A fresh session recovers state from those in one turn.

## Step 5 — VS Code
1. Sign into VS Code **Settings Sync** on the OLD laptop (GitHub/Microsoft account) if not already → syncs settings, extensions, keybindings to cloud.
2. New laptop: sign into the same account → everything restores. Install the Claude Code extension from the marketplace if not auto-restored; it picks up the CLI login.

## Step 6 — Python environment (recreate, don't copy)
`.venv` is machine-specific — do NOT copy it:
```powershell
cd C:\Users\<newuser>\Github\stock-picks-app
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Parity note: this machine runs WITHOUT pandas-ta (manual-implementation fallback everywhere). Keep it uninstalled on the new laptop for identical signal behavior, OR install it knowingly (behavior may shift; pyramid must stay green either way).

## Step 7 — Verification checklist on the new laptop (run in order)
```powershell
git status                          # clean tree
python -m pytest backtest/tests/test_unit.py backtest/tests/test_integration.py -q
                                    # expect 876 passed, 2 skipped (writes .pyramid_stamp)
python scripts/preflight.py --all   # hook logic sanity
python scripts/data_readiness_audit.py --sample 25
                                    # expect coverage ~99% rows matching the 2026-07-08 audit
claude --resume                     # session list shows this project; open latest
```
Then in the resumed session, ask: "Any silent misses? state check" — Claude should reconstruct standing state (rung 4 HELD, scope locked, window locked 2026-05-05) from memory + queue.

## Step 8 — Old laptop decommission (only after step 7 fully green)
- Revoke the old PAT at github.com/settings/personal-access-tokens; issue fresh on new machine.
- Keep the old `~/.claude/projects/` folder + `.env` until the new machine has run one full rung successfully.
