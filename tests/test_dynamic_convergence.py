"""Frozen first-day regression, numerical margins and explicit strategy boundaries."""

from copy import deepcopy
import json
from pathlib import Path
import random
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.biophysical.animal.ration.dynamic_linear_optimizer import DynamicRationOptimizer
from RUFAS.biophysical.animal.ration.mineral_limits import calcium_total_upper, phosphorus_total_upper, mineral_report
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    NRCFeed,
    NutrientStandard,
    FeedCategorization,
    FeedComponentType,
)
from RUFAS.units import MeasurementUnits


@pytest.fixture
def first_day():
    data = json.loads((Path(__file__).parent / "fixtures/dynamic_first_day.json").read_text())
    data["nutrient_standard"] = NutrientStandard(data["nutrient_standard"])
    data["animal_combination"] = AnimalCombination(data["animal_combination"])
    req = data["requirements"]
    req["essential_amino_acids"] = EssentialAminoAcidRequirements(**req["essential_amino_acids"])
    data["requirements"] = NutritionRequirements(**req)
    for f in data["pen_available_feeds"]:
        f["Fd_Category"] = FeedCategorization(f["Fd_Category"])
        f["feed_type"] = FeedComponentType(f["feed_type"])
        f["units"] = MeasurementUnits(f["units"])
    data["pen_available_feeds"] = [NRCFeed(**f) for f in data["pen_available_feeds"]]
    return data


def solve(data, **kwargs):
    optimizer = DynamicRationOptimizer("linear_highs", "fail", **kwargs)
    state = random.getstate()
    try:
        random.seed(3)
        result, config = optimizer.attempt_optimization(**deepcopy(data))
    finally:
        random.setstate(state)
    return optimizer, result, config


def test_first_day_large_initial_supplement_is_not_a_physical_lower_bound(first_day):
    feeds = first_day["pen_available_feeds"]
    first_day["previous_ration"] = {f.rufas_id: 1.0 for f in feeds}
    first_day["previous_ration"][231] = 9.836187688651739
    optimizer, result, config = solve(first_day)
    assert result.success and result.converged
    assert result.nit > 1
    assert result.x[-1] < 0.01
    assert result.fun < 1.0
    assert mineral_report(np.round(result.x, 6), config)["tolerable"]
    assert any(t["decision"] == "expand_for_feasibility" for t in optimizer.events[0]["trace"])
    assert all(v >= 0 for v in optimizer.events[0]["trace"][-1]["residuals"].values())


@pytest.mark.parametrize(
    "name,percent,check", [("calcium", 1.5, calcium_total_upper), ("phosphorus", 0.7, phosphorus_total_upper)]
)
@pytest.mark.parametrize("offset,sign", [(-0.01, 1), (0.0, 0), (0.01, -1)])
def test_total_mineral_ceiling_units(name, percent, check, offset, sign):
    feed = SimpleNamespace(calcium=0.0, phosphorus=0.0)
    setattr(feed, name, percent + offset)
    value = check(np.array([20.0]), SimpleNamespace(feeds_used=[feed]))
    assert np.sign(value) == sign


def test_rounding_residuals_and_inclusion_limits(first_day):
    first_day["pen_available_feeds"][-1].limit = 0.05
    optimizer, result, config = solve(first_day)
    assert result.success
    assert result.x[-1] <= 0.05
    trace = optimizer.events[0]["trace"]
    accepted = [t for t in trace if t.get("approved") and all(v >= 0 for v in t["residuals"].values())]
    assert accepted
    assert result.fun == min(t["cost"] for t in accepted)
    for t in trace:
        assert all(lo <= hi for lo, hi in t["local_bounds"])


def test_keeps_best_feasible_candidate_when_later_lp_fails(first_day):
    import RUFAS.biophysical.animal.ration.dynamic_linear_optimizer as module

    actual = module.optimize_diet
    valid_seen = False

    def run_lp(*args, **kwargs):
        nonlocal valid_seen
        result = actual(*args, **kwargs)
        if valid_seen:
            return SimpleNamespace(status="infeasible", message="Injected later LP failure")
        if result.status == "optimal" and result.cost_per_day < 0.346:
            valid_seen = True
        return result

    with patch.object(module, "optimize_diet", side_effect=run_lp):
        _, result, config = solve(first_day)
    # Independent validity of the retained point is required, not solver status alone.
    assert result.success
    assert mineral_report(np.round(result.x, 6), config)["tolerable"]


def test_exclusive_never_calls_native_even_on_failure(first_day):
    optimizer = DynamicRationOptimizer("linear_highs_exclusive", max_iterations=0)
    with patch.object(
        RationOptimizer, "attempt_optimization", autospec=True, side_effect=AssertionError("SLSQP called")
    ):
        with pytest.raises(RuntimeError, match="Exclusive HiGHS failed"):
            optimizer.attempt_optimization(**first_day)
    assert len(optimizer.events) == 1


@pytest.mark.parametrize(
    "category", [AnimalCombination.GROWING, AnimalCombination.CLOSE_UP, AnimalCombination.GROWING_AND_CLOSE_UP]
)
def test_all_categories_select_their_native_constraints(first_day, category):
    first_day["animal_combination"] = category
    optimizer = DynamicRationOptimizer("linear_highs_all", "fail", max_iterations=0)
    with patch.object(
        RationOptimizer, "attempt_optimization", autospec=True, side_effect=AssertionError("SLSQP called")
    ):
        _, config = optimizer.attempt_optimization(**first_day)
    names = [c["fun"].__name__ for c in optimizer._select_constraints(category)]
    assert "NE_lactation_constraint" not in names and "NE_total_constraint" not in names
    assert "NE_growth_constraint" in names and "calcium_total_upper" in names
    assert config.animal_combination is category


def test_exclusive_calf_is_not_counted_as_native_fallback(first_day):
    first_day["animal_combination"] = AnimalCombination.CALF
    optimizer = DynamicRationOptimizer("linear_highs_exclusive")
    with patch.object(
        RationOptimizer, "attempt_optimization", autospec=True, side_effect=AssertionError("SLSQP called")
    ):
        with pytest.raises(ValueError, match="unsupported"):
            optimizer.attempt_optimization(**first_day)
    assert len(optimizer.events) == 1
    assert optimizer.events[0]["used"] == "unsupported"
    assert optimizer.events[0]["reason"] == "unsupported_category_or_standard"


@pytest.mark.parametrize("requested", [0.0014, 0.003])
def test_small_real_storage_batches_are_consumed_without_fabricating_mass(requested):
    from datetime import date
    from RUFAS.biophysical.feed_storage.feed_manager import FeedManager
    from RUFAS.biophysical.feed_storage.purchased_feed_storage import PurchasedFeed
    from unittest.mock import MagicMock

    manager = FeedManager.__new__(FeedManager)
    batches = [PurchasedFeed(104, q, date(2013, 5, 6)) for q in (0.000038, 0.000689347375, 0.000809200519)]
    before = sum(b.dry_matter_mass for b in batches)
    manager._om = MagicMock()
    manager._cumulative_purchased_feeds_fed = {}
    manager._cumulative_farmgrown_feeds_fed = {}
    with (
        patch.object(manager, "_gather_available_feeds_by_id", return_value=({}, {104: batches})),
        patch.object(manager, "_gather_valid_farmgrown_feed_ids", return_value=set()),
        patch.object(manager, "_log_feed_deductions"),
    ):
        if requested > before + 0.001:
            with pytest.raises(ValueError, match="Not adequate feed"):
                manager._deduct_feeds_from_inventory({104: requested}, 125)
        else:
            result = manager._deduct_feeds_from_inventory({104: requested}, 125)
            after = sum(b.dry_matter_mass for b in batches)
            assert result.purchased[104] == pytest.approx(requested)
            assert before - after == pytest.approx(result.purchased[104])
            assert after >= 0


def test_exclusive_real_annual_loop_categories_transitions_and_inventory(tmp_path):
    import subprocess
    import sys

    target = tmp_path / "exclusive_year"
    completed = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "experiments.annual",
            "--days",
            "365",
            "--strategy",
            "linear_highs_exclusive",
            "--output",
            str(target),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
    )
    assert completed.returncode == 0, completed.stderr
    summary = json.loads((target / "summary.json").read_text())
    records = [json.loads(line) for line in (target / "daily.jsonl").read_text().splitlines()]
    assert summary["simulated_days"] == len(records) == 365
    assert summary["native_attempts"] == summary["fallbacks"] == 0
    assert summary["highs_attempts"] == summary["highs_accepted"] > 0
    categories = {e["category"] for r in records for e in r["formulations"]}
    assert categories == {"growing", "close_up", "lac_cow"}
    first = {a["id"]: a["category"] for a in records[0]["animals"]}
    assert any(first.get(a["id"], a["category"]) != a["category"] for r in records[1:] for a in r["animals"])
    assert all(v >= -1e-6 for r in records for v in r["inventory_kg_dm"].values())
    assert all(p["minerals"]["tolerable"] for r in records for p in r["pens"] if p["category"] != "calf")
    assert summary["estimated_diet_cost"] == pytest.approx(sum(r["estimated_diet_cost"] for r in records))
