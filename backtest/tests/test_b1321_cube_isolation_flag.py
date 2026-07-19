"""B1321 (Council 353, M2=(i) pure-signal isolation): the cube_isolation flag
must wire cleanly and default OFF (so the portfolio-sim / live path is
untouched). Behavioral validation (trade counts rise, no portfolio_gate /
cooldown / max_loss skips) is the isolation coverage-smoke built with #159.
"""
from backtest.engine.backtest import BacktestEngine


def test_flag_defaults_off():
    eng = BacktestEngine(universe=["SPY"], run_agents=False, walk_forward=False)
    assert eng.cube_isolation is False, "isolation must default OFF (BUG-61 path)"


def test_flag_propagates():
    eng = BacktestEngine(universe=["SPY"], run_agents=False, walk_forward=False,
                         cube_isolation=True)
    assert eng.cube_isolation is True


def test_isolation_guards_present_in_source():
    """Pin the guard points so a future edit can't silently drop one."""
    import pathlib
    src = pathlib.Path(BacktestEngine.__module__.replace(".", "/") + ".py")
    # resolve module file robustly
    import backtest.engine.backtest as _m
    text = pathlib.Path(_m.__file__).read_text(encoding="utf-8")
    for guard in [
        "self.cube_isolation = cube_isolation",           # constructor
        "candidates if self.cube_isolation else",          # candidate cap
        'if self.cube_isolation:\n                _bug61_mode = "ticker_strategy"',  # ticker
        "cooldown_breach and not self.cube_isolation",     # cooldown
        "_cum_pnl <= _cap_pct and not self.cube_isolation",  # max-loss
        "not ok and not self.cube_isolation",              # can_open
    ]:
        assert guard in text, f"isolation guard missing: {guard!r}"
