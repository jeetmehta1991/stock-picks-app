# Selected-exit correlation over the Phase-1B members (S6-B3288, zero engine runs)

- members blended: 23 of 23 long roster members (mirrors listed, not blended: 10)
- holdout window 2025-05-05 .. 2026-05-05; basis net = roster_core.net_pnl (winsorize 300.0, cost 20.0 bps)
- average pairwise rho 0.0948, median 0.0303, 10 of 253 pairs above 0.5 in magnitude
- eigenvalue effective N 12.165 of 23
- equal-weight holdout blend: Sharpe 6.244 over 261 of 261 business days (SPY: exchange trading days), max drawdown -4.6 pct; the live pooled bar 1.0 is cleared
- admissions-only blend Sharpe 4.558; funnel-only blend Sharpe 5.314; SPY buy-and-hold Sharpe 1.972 (the control)

| pair | rho |
|---|---|
| institutional_committed_growth_long / institutional_strong_conviction_long | 0.9767 |
| institutional_committed_growth_long / institutional_multi_quarter_persistence_long | 0.9435 |
| institutional_multi_quarter_persistence_long / institutional_strong_conviction_long | 0.9264 |
| institutional_high_conviction_long / institutional_strong_conviction_long | 0.8188 |
| institutional_committed_growth_long / institutional_high_conviction_long | 0.8129 |
| institutional_high_conviction_long / institutional_multi_quarter_persistence_long | 0.7832 |
| institutional_recent_init_momentum_long / institutional_recent_init_volume_long | 0.6616 |
| institutional_breakout_confirmation_long / institutional_recent_init_momentum_long | 0.6514 |
| institutional_breakout_confirmation_long / institutional_recent_init_volume_long | 0.597 |
| pead_long_high_yoy_growth_only / pead_with_smart_money_long | 0.5509 |

Caveats: exit-date attribution with zero-filled days deflates every pairwise rho toward 0 and every standalone vol; right for how streams add, wrong for a standalone Sharpe claim (B2182) / one holdout year, one regime: the crisis rho is the one that matters and this window cannot measure it / the members were SELECTED on this holdout (each line's gates were read on it at admission), so the blend inherits that selection - DISCLOSED-RE-READ, no new read spent / equal weight per line (no admitted line carries a ruled tier); pnl realized at exit, so intra-trade drawdown is understated / the blend stats and the matrix cover the holdout business days only: pnl realised after the holdout end (late entries on trailing exits) is outside every figure here
