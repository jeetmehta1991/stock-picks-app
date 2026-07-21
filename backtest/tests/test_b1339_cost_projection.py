"""B1339 (Council 366): cost-projection measure-and-project model + budget
hard-stop (Fable B1334 item 5: linear extrapolation from 10-tkr smokes is
unreliable; must fit fixed+marginal from measured batches and stop at cap)."""
import scripts.cost_projection as cp


def test_single_point_is_unfittable_honest():
    m = cp.fit([(10, 18.0)])
    assert m["fittable"] is False
    assert cp.project(m, 20) is None  # refuses to guess (L211)


def test_two_points_fit_fixed_and_marginal():
    # 10->18min, 20->26min  => marginal 0.8 min/tkr, fixed 10 min
    m = cp.fit([(10, 18.0), (20, 26.0)])
    assert m["fittable"] is True
    assert abs(m["marginal_min_per_ticker"] - 0.8) < 1e-6
    assert abs(m["fixed_min"] - 10.0) < 1e-6


def test_projection_and_saturation_flag():
    m = cp.fit([(10, 18.0), (20, 26.0)])
    p50 = cp.project(m, 50)
    assert p50["n_tickers"] == 50 and p50["vcpu_saturated"] is False
    p503 = cp.project(m, 503)
    assert p503["vcpu_saturated"] is True and "UPPER-BOUND" in p503["estimate_quality"]


def test_budget_hard_stop():
    ok, proj = cp.check_budget(spent=48.0, next_cost=5.0, cap=50.0)
    assert ok is False and proj == 53.0
    ok2, _ = cp.check_budget(spent=10.0, next_cost=5.0, cap=50.0)
    assert ok2 is True


def test_cost_scales_with_rate():
    m = cp.fit([(10, 60.0), (20, 120.0)])  # 6 min/tkr, fixed 0
    p = cp.project(m, 10)
    assert abs(p["cost_usd"] - (60/60 * cp.HOURLY_RATE_USD)) < 1e-6
