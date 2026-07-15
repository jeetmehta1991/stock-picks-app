<!-- Source: per CHECKLIST #77 canonical-source; B1278-B1279 Council 317 2026-07-15 owner-requested migration guide (simplified rewrite) -->
# Moving to a New Laptop — Simple Step-by-Step

**The whole idea: copy 2 folders with a USB drive, install 4 programs, run 3 commands. ~1 hour, mostly copying time.**

---

## PART A — On your OLD laptop: put 2 zips on Google Drive (20-40 min, mostly upload)

**A1.** Open File Explorer, go to `C:\Users\jeetm\Github`. Right-click the `stock-picks-app` folder → **Compress to ZIP file**. Wait for `stock-picks-app.zip` (~2-4 GB) to finish.
This zip is EVERYTHING — code, data, run results, and your API keys (.env).

**A2.** Go to `C:\Users\jeetm\.claude\projects`. Right-click the folder `c--Users-jeetm-Github-stock-picks-app` → **Compress to ZIP file** (~400 MB).
This zip is your entire Claude Code history for this project — every session (including the current one) and Claude's memory.
*Can't see the `.claude` folder? File Explorer → View → Show → Hidden items.*

**A3.** Go to **drive.google.com** (your jeetmehta1991@gmail.com account) → New → File upload → upload both zips. (The project zip takes the longest — start it and walk away.)

**A4.** In VS Code: click the little account icon (bottom-left) → **Turn on Settings Sync** (if it isn't already) → sign in with GitHub. This puts your VS Code settings and extensions in the cloud.

Done with the old laptop. Don't wipe it yet — keep it until Part D passes.

*Alternative if both laptops are on the same WiFi and you'd rather skip the upload: Windows **Nearby Sharing** (Settings → System → Nearby sharing → Everyone nearby, on BOTH laptops; then right-click each zip → Share → pick the new laptop). Faster on slow internet; the Drive route is more reliable for multi-GB files.*

---

## PART B — On your NEW laptop: install 4 programs (20 min)

Install these, in this order, accepting the default options:

**B1.** **Git for Windows** — download from git-scm.com, run installer, click Next through everything.

**B2.** **Python 3.14** — download from python.org. **IMPORTANT: on the first installer screen, tick the checkbox "Add python.exe to PATH"** before clicking Install.

**B3.** **VS Code** — download from code.visualstudio.com, install. Open it, click the account icon (bottom-left), **sign in with the same GitHub account** → your settings and extensions appear automatically.

**B4.** **Claude Code** — download from claude.com/claude-code (or in a terminal: `npm install -g @anthropic-ai/claude-code` if you have Node.js). Then open PowerShell, type `claude`, press Enter, and log in with **jeetmehta1991@gmail.com** when the browser opens.

---

## PART C — On your NEW laptop: download + extract the 2 zips (15 min + download time)

**C1.** Go to drive.google.com, download both zips.

**C2.** Create the folder `Github` in your user folder if it doesn't exist: open File Explorer, go to `C:\Users\<YOURNAME>`, right-click → New → Folder → name it `Github`.

**C3.** Right-click `stock-picks-app.zip` → **Extract All** → extract so the final result is exactly:
```
C:\Users\<YOURNAME>\Github\stock-picks-app
```
(⚠ Watch for double-nesting: if extraction gives you `...\Github\stock-picks-app\stock-picks-app\`, move the inner folder up one level.)

**C4.** Right-click the second zip → Extract All → put the extracted folder into `C:\Users\<YOURNAME>\.claude\projects\` (the `.claude` folder was created when you logged into Claude Code in step B4). Same double-nesting check.

**C5.** ⚠ **ONLY IF your username on the new laptop is NOT `jeetm`:** rename the folder you just pasted. The name encodes the path — replace `jeetm` with your new username:
- was: `c--Users-jeetm-Github-stock-picks-app`
- becomes (example, username `bob`): `c--Users-bob-Github-stock-picks-app`

If your username is still `jeetm`, skip this step — the name already matches.

---

## PART D — On your NEW laptop: 3 commands + check it worked (15 min)

Open PowerShell and paste these lines one at a time (replace `<YOURNAME>`):

**D1.** Go to the project and set up Python (takes ~5 min):
```powershell
cd C:\Users\<YOURNAME>\Github\stock-picks-app
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**D2.** Install the safety hooks and run the test suite (~1 min; MUST end with "876 passed, 2 skipped"):
```powershell
scripts\install_git_hooks.bat
python -m pytest backtest/tests/test_unit.py backtest/tests/test_integration.py -q
```

**D3.** Open the session — this is the "did my context survive?" moment:
```powershell
claude --resume
```
A list of past sessions appears. Pick the newest one (the R5 ladder session). Ask Claude: **"state check - where did we leave off?"** — the answer should say: rung 4 HELD, scope locked, window locked at 2026-05-05, all pre-R5 fixes shipped. If it does: **everything transferred, zero context lost.**

---

## PART E — Cleanup (later, only after D3 worked)

**E1.** On github.com → Settings → Developer settings → Personal access tokens: revoke the old laptop's token; create a new one when Claude next needs to push (it will ask).

**E2.** Keep the old laptop untouched for a week as backup, then delete at will.

**E3.** Delete both zips from Google Drive (the project zip contains your `.env` API keys — don't leave it in the cloud longer than needed).

---

### If something goes wrong
| Symptom | Fix |
|---|---|
| `claude --resume` shows no sessions | The folder name from C5 doesn't match your project path — recheck the username spelling in the folder name |
| Tests fail or `python` not found | Python wasn't added to PATH — reinstall Python with the checkbox ticked (B2) |
| Git asks who you are on first commit | `git config --global user.name "jeetmehta1991"` and `git config --global user.email "jeetmehta1991@gmail.com"` |
| Push asks for password | Paste a fresh PAT (E1) as the password |

---

*Advanced/alternative path (git clone + selective payload copy) was in the B1278 version of this doc — see git history if ever needed. The copy-everything path above is equivalent and simpler.*
