# Compute-venue decision — local vs AWS vs Hetzner (B2108, S6-B2107a)

Owner-named next step (2026-08-23 ruling): pick the venue for the approved A1 program under the
new **3-hour local-run cap**. One recommendation at the end; nothing runs until you pick.

## The workload being venued

| block | shape | engine hours (B2038 basis, 0.2613 s/ticker-day) | with the 1.75x overrun factor |
|---|---|---|---|
| W-A (EMA axis, 5 levels) | 5 x 200t x 1y | 18.2 h | 31.9 h |
| W-B (SMC axis, 5 levels) | 5 x 200t x 1y | 18.2 h | 31.9 h |
| Step-2 VALIDATE (one run, all carried combos subset-safe) | 344t x 2y | 12.5 h | 21.9 h |
| **program total** | 11 runs | **48.9 h** | **85.7 h** |

Every W run is 3.64 h — **over the 3 h local cap as a single piece**. Sources: the B2038 cost
table (plan section 10.2 rate, B2021-bracketed end to end); the 1.75x factor is the S6-B1680a
measured wave-1 overrun carried per the A1 design.

## The three venues

### A. Local, resume-chunked ($0)
Each config as TWO sub-3h legs (~1.9 h each) on the proven checkpoint/resume infra (B1076/B1078;
resume validated live at B1079 with +515 trades post-resume; the engine checkpoints every 100
days). At the measured N=2 concurrency (~1.0x per-arm at the 100t shape, b1576_par.log), the
11-run program is ~2.5-4 wall-clock DAYS of babysat local compute.
**Honest note:** this satisfies the cap's letter, not obviously its spirit — the ruling's stated
reason is time consumed, and this is the slowest option. Presented as the $0 fallback only.

### B. Hetzner CCX43 (~EUR 38 program)
EUR 0.4423/h (post-June-2026 dedicated-vCPU pricing; sources searched 2026-08-23: northflank.com
price-increase notice, sparecores.com/server/hcloud/ccx43) x 3.64 h = **~EUR 1.61 per config**;
the 85.7-h factored program = **~EUR 38**. Dedicated vCPU = no spot interruptions; schedule cost
is certain.
**Prerequisites:** you provision a Hetzner account + API token (I cannot open accounts); I port
the launch playbook (Linux side is proven lineage — R5 ran on Linux EC2); and the A4-approved
**~EUR 2 reproduction benchmark runs FIRST** — one 50t x 1y config, PASS = byte-identical
trade_exit_detail.csv vs local (the determinism sha regime makes this a one-command diff).

### C. AWS, right-sized + quote-first (~$25 program, inside your standing $50 CAD cap)
The ENTIRE mechanism already exists and survived R5: docs/r6_workflow_reuse/AWS_LAUNCH_PLAYBOOK.md
+ R5_WORKFLOW.md (spot handling, AZ failover, S3 user-data, sentinels), the prelaunch gate's S3
sidecar path, the resume infra that ate real spot interruptions. R5-era measured price:
c6a.16xlarge spot at **$1.05/hr** (stale-with-source, R5_WORKFLOW.md line 283). At 64 vCPU that
instance is oversized for one config (the pool=16 lesson, B1070 F-7.1); a **16-vCPU c6a.4xlarge-
class** instance at roughly a quarter of that rate prices the factored program at **~$22-28** —
**QUOTE-FIRST before any spend per your standing rule**; the number above is sizing, not a quote.
Reproduction benchmark: same ~$1 one-config diff as Hetzner, and half-proven already — R5 itself
ran there.

## Recommendation

**C — AWS, right-sized, quote-first.** The playbook, gates, account lineage, and spot-survival
infra exist and are battle-tested here; Hetzner saves little (~EUR 38 vs ~$25-quoted) while
costing owner-side account provisioning plus a first-time platform proof; local chunking spends
the one resource your ruling says matters most — days of time.
**Contrarian case against:** Hetzner's dedicated vCPU makes the schedule CERTAIN (no spot
interruptions, no AZ failover dance) and its price is list, not quoted — if you value
determinism-of-schedule over infrastructure reuse, pick B and I port the playbook behind the
EUR-2 benchmark. And the true contrarian floor: option A costs zero dollars and zero new trust,
if days of wall-clock are acceptable after all.

## What happens on your pick
- **"AWS"** -> I prepare the quote (instance type + spot price + total), you approve the number,
  the repro benchmark runs, then W-A launches per the A1 design through launch_sweep.py.
- **"Hetzner"** -> you provision the account/token; I port the playbook; EUR-2 benchmark; W-A.
- **"Local chunked"** -> W-A starts immediately as sub-3h resume legs, ~2.5-4 days.

## The 20L + 20S target this all serves
One W-A wave measures the EMA axis for **114 long-side consumers** at power-sized pooled shapes
(block floor 0.2245 vs the 0.281 margin); survivors carry mirrors by your standing
mirror-shorts-by-default directive. The funnel to 20 long + 20 mirror-short Phase-1B entries runs
through exactly these waves plus Step-2 — venue is the only thing between here and the first one.
