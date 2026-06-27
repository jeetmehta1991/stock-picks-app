# Sector History — Proposed Changes Draft (Owner Spot-Check Required)

**Date:** 2026-06-27
**Source:** Option-3a Claude research under L88 exception per memo `c3_sector_history_refresh_owner_memo_2026_06_27.md`
**Status:** DRAFT — DO NOT COMMIT until owner spot-checks ≥4 reclassifications per L88 caveat (iii)
**Target file:** `Backtesting universe/sector_history.csv` (stale since 2023-03-17)

---

## Research Summary

Searched S&P DJI press releases + cross-source confirmation (LSEG, ETF Strategy, SSGA, Marquette Associates, GlobeNewswire) for GICS sector reclassifications affecting S&P 500 (T1a) constituents OR our broader 5-tier universe (T1a/T1b/T1c/T2/T3) since 2023-03-17.

**Finding count:** 1 confirmed change relevant to OUR universe (CRS in T3) + 2 universe-edge cases for owner review + 1 confirmed NULL event (Aug-2024 was definition-only, zero company moves).

---

## Proposed Additions

### Change #1 — CRS (Carpenter Technology) — Materials → Industrials (Aerospace & Defense)

| Field | Value |
|---|---|
| Symbol | CRS |
| Old Sector | Materials |
| New Sector | Industrials |
| Old GICS sub-industry | Steel (15104050) |
| New GICS sub-industry | Aerospace & Defense (20101010) |
| Effective Date | 2025-09-30 |
| Source | https://ir.carpentertechnology.com/news-events/news/news-details/2025/Carpenter-Technology-Announces-GICS-Aerospace--Defense-Sector-Reclassification/default.aspx |
| Cross-source | GlobeNewswire 2025-09-17, Nasdaq, GuruFocus |
| Universe impact | T3 (multiple snapshots 2023-2025 carry sector "Materials") |
| Confidence | **HIGH** (company press release + MSCI/S&P DJI joint determination cited; 3+ source cross-verify) |

**Proposed CSV rows:**
```
CRS,Materials,,2025-09-30
CRS,Industrials,2025-09-30,
```

---

## Universe-Edge Cases (Owner Decision Required)

### Edge #1 — AIMD (Ainos) — NOT IN UNIVERSE
- Reclassified to Technology Hardware, Storage & Peripherals effective 2025-10-01.
- Not in T1a/T1b/T1c/T2/T3 (~$30M micro-cap).
- **Recommendation:** SKIP — out of universe; no strategy impact.

### Edge #2 — Tickers renamed during window (B561a-class)
- Per prior B561a follow-on pattern, ticker renames (e.g., FISV→FI, FLT→CPAY) get pre-rename rows preserved.
- No new renames identified in 2023-03-17 → 2026-06-27 window in S&P 500 that require sector_history treatment beyond standard ticker_lifecycle_events handling.

---

## Confirmed NULL Events (no CSV change needed)

### NULL #1 — Aug 1, 2024 GICS Definition Update
- MSCI + S&P DJI joint announcement (PDF `1473681_2024gicsdefinitionannouncement-1aug.pdf`).
- **Verdict:** Expanded select sub-industry **definitions only**; **zero company-level GICS reclassifications**.
- Source: https://www.spglobal.com/spdji/en/documents/index-news-and-announcements/1473681_2024gicsdefinitionannouncement-1aug.pdf
- **No action needed.**

### NULL #2 — 2024 & early-2025 S&P 500 sweep
- Cross-source search (LSEG, SSGA, Marquette, Yahoo Finance, Indexology Blog) found **no multi-name S&P 500 GICS reclassifications** between 2023-03-17 and 2026-06-27.
- Pattern matches Batch 561 note ("2023-03-17 was the only multi-name event in this window").

---

## Coverage Caveats (per L88 + L89)

1. **S&P DJI press release archive not fully crawled** — Claude relied on web search aggregators (Yahoo, GlobeNewswire, SEC EDGAR 497 filings, GuruFocus). Direct S&P DJI press release archive index (https://www.spglobal.com/spdji/en/landing/announcements/) requires manual browse — owner spot-check should re-verify against this primary source.
2. **Single-name spin-off / merger reclassifications may exist below detection threshold** — per Batch 561 caveat line 49-52 of current CSV. Add as discovered.
3. **L89 SNDK lag pattern** — if a 2024-2026 reclassification exists but only appeared in low-coverage press, this draft will miss it. Owner annual review recommended.
4. **Tier 1c (NDX) and Tier 2 (spinoffs/IPOs) not fully audited** — focus was on T1a + cross-tier matches; deep T1c/T2-only walk deferred.

---

## Owner Spot-Check Checklist (per L88 caveat iii)

Owner must independently verify ≥4 of the following before commit:

```
[ ] CRS effective date 2025-09-30 vs S&P DJI / MSCI primary press release
[ ] CRS new sector = Industrials (Aerospace & Defense sub-industry 20101010) [confirm GICS sector vs sub-industry mapping]
[ ] CRS old sector was Materials (Steel) — verify pre-2025-09-30
[ ] AIMD universe-exclusion verdict correct (confirm not in T1a/T2/T3)
[ ] Aug-2024 GICS update was definition-only (zero company moves) per primary S&P DJI PDF
[ ] No additional S&P 500 reclassifications missed in 2023-04 → 2026-06 window
```

---

## Proposed Diff (apply ONLY after owner approval)

```diff
@@ Backtesting universe/sector_history.csv @@
+# Batch [NEXT] (2026-06-27): C-3 refresh per W4 audit + owner-approved
+# Option-3a (Claude research under L88 + owner spot-check).
+# Added: CRS Materials -> Industrials (Aerospace & Defense), eff 2025-09-30.
+# Confirmed NULL: Aug-2024 GICS update was definition-only (0 company moves).
+# Audit window: 2023-03-18 to 2026-06-27.
+
 ... existing 2018-09-24 + 2023-03-17 rows ...
+CRS,Materials,,2025-09-30
+CRS,Industrials,2025-09-30,
```

---

## Status

**🔴 AWAITING OWNER SPOT-CHECK** — do not commit until ≥4 checklist items verified per L88 caveat (iii). Per `feedback_audit_recommendations_against_existing_directives`.

Word count: ~640.
