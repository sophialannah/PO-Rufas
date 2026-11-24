"""Analytic LP cases, invalid inputs, and real RuFaS object integration."""

from dataclasses import replace
from unittest.mock import patch

import numpy as np
import pytest
from scipy.optimize import OptimizeResult

from RUFAS.biophysical.animal.ration.linear_diet import AnimalProfile, DietRequirements, Ingredient, optimize_diet
from RUFAS.biophysical.animal.ration.linear_diet_adapter import (
    ingredient_from_feed,
    requirements_from_rufas,
    profile_from_animal,
)
from RUFAS.biophysical.animal.ration.linear_diet_example import example_feeds, example_inputs
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import FeedInRation, NutritionSupplyCalculator


def profile(requirements: DietRequirements | None = None) -> AnimalProfile:
    return AnimalProfile(650, 100, 30, 3.8, 3.2, requirements or DietRequirements(10, 10, 2, 10), "Test fixture")


def ingredients() -> list[Ingredient]:
    # Exact optimum: 5 kg cheap + 5 kg protein, cost 15.
    return [Ingredient(1, "cheap", 1, 100, 1, 1, 0.1, 0.5), Ingredient(2, "protein", 2, 100, 1, 1, 0.3, 0.1)]


def test_known_optimum_and_all_nutrient_checks() -> None:
    result = optimize_diet(profile(), ingredients())
    assert result.status == "optimal"
    assert result.quantities_kg_day == pytest.approx({1: 5, 2: 5})
    assert result.cost_per_day == pytest.approx(15)
    assert result.totals == pytest.approx({"DM_kg": 10, "CP_kg": 2, "NEL_Mcal": 10, "NDF_kg": 3})
    assert all(check.satisfied for check in result.checks)


def test_fresh_matter_and_price_conversion() -> None:
    feed = Ingredient(1, "wet", Ingredient.price_from_tonne(1000), 100, 0.5, 2, 0.2, 0.3)
    result = optimize_diet(profile(), [feed])
    assert result.quantities_kg_day == pytest.approx({1: 20})
    assert result.ration_kg_dm_day == pytest.approx({1: 10})
    assert result.cost_per_day == pytest.approx(20)


@pytest.mark.parametrize("changes,period", [({"maximum_kg_day": 3}, 1), ({"stock_kg": 6}, 2)])
def test_inclusion_and_period_stock(changes: dict, period: float) -> None:
    feeds = ingredients()
    feeds[0] = replace(feeds[0], **changes)
    result = optimize_diet(profile(), feeds, period_days=period)
    assert result.quantities_kg_day == pytest.approx({1: 3, 2: 7})
    assert all(check.satisfied for check in result.checks)


def test_minimum_inclusion() -> None:
    feeds = ingredients()
    feeds[1] = replace(feeds[1], minimum_kg_day=8)
    result = optimize_diet(profile(), feeds)
    assert result.quantities_kg_day == pytest.approx({1: 2, 2: 8})


@pytest.mark.parametrize(
    "req,expected_cheap",
    [
        (DietRequirements(10, 10, 0, 10, ndf_max_fraction=0.3), 5),
        (DietRequirements(10, 10, 0, 10, ndf_min_fraction=0.4), 10),
        (DietRequirements(8, 12, 0, 10, ndf_max_fraction=0.3), 5),
    ],
)
def test_ndf_proportion_linearization(req: DietRequirements, expected_cheap: float) -> None:
    result = optimize_diet(profile(req), ingredients())
    assert result.status == "optimal"
    assert result.quantities_kg_day[1] == pytest.approx(expected_cheap)
    assert all(check.satisfied for check in result.checks)


def test_binding_ndf_minimum() -> None:
    feeds = ingredients()
    feeds[0] = replace(feeds[0], price_per_kg=3)
    result = optimize_diet(profile(DietRequirements(10, 10, 0, 10, ndf_min_fraction=0.4)), feeds)
    assert result.quantities_kg_day == pytest.approx({1: 7.5, 2: 2.5})


def test_total_dietary_minerals_and_missing_composition() -> None:
    req = DietRequirements(10, 10, 0, 10, mineral_min_kg={"calcium": 0.15})
    feeds = [replace(feed, mineral_fractions={"calcium": value}) for feed, value in zip(ingredients(), [0.01, 0.02])]
    result = optimize_diet(profile(req), feeds)
    assert result.quantities_kg_day == pytest.approx({1: 5, 2: 5})
    assert result.totals["mineral_calcium_kg"] == pytest.approx(0.15)
    with pytest.raises(ValueError, match="Missing"):
        optimize_diet(profile(req), ingredients())


@pytest.mark.parametrize(
    "feeds",
    [
        [Ingredient(1, "low protein", 1, 100, 1, 1, 0.1, 0.3)],
        [Ingredient(1, "no stock", 1, 0, 1, 1, 0.3, 0.3)],
        [Ingredient(1, "minimum exceeds stock", 1, 1, 1, 1, 0.3, 0.3, minimum_kg_day=2)],
    ],
)
def test_infeasible_has_no_ration_or_cost(feeds: list[Ingredient]) -> None:
    result = optimize_diet(profile(), feeds)
    assert result.status == "infeasible"
    assert not result.quantities_kg_day
    assert result.cost_per_day is None
    assert result.message


@pytest.mark.parametrize(
    "field,value",
    [
        ("dm_fraction", 0),
        ("dm_fraction", 90),
        ("cp_fraction", -1),
        ("price_per_kg", float("nan")),
        ("stock_kg", float("inf")),
        ("maximum_kg_day", -1),
        ("nel_mcal_per_kg_dm", -1),
    ],
)
def test_invalid_ingredient(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        replace(ingredients()[0], **{field: value})


def test_invalid_problem() -> None:
    with pytest.raises(ValueError):
        optimize_diet(profile(), [])
    with pytest.raises(ValueError):
        optimize_diet(profile(), ingredients() * 2)
    with pytest.raises(ValueError):
        optimize_diet(profile(), ingredients(), period_days=0)
    with pytest.raises(ValueError):
        DietRequirements(10, 9, 1, 1)


def test_independent_verification_rejects_false_success() -> None:
    with patch(
        "RUFAS.biophysical.animal.ration.linear_diet.linprog",
        return_value=OptimizeResult(success=True, x=np.array([0.0, 0.0])),
    ):
        result = optimize_diet(profile(), ingredients())
    assert result.status == "verification_failed"
    assert result.cost_per_day is None
    assert not result.quantities_kg_day


def test_solver_failure_is_not_infeasibility() -> None:
    with patch(
        "RUFAS.biophysical.animal.ration.linear_diet.linprog",
        return_value=OptimizeResult(success=False, status=4, message="numerical failure"),
    ):
        result = optimize_diet(profile(), ingredients())
    assert result.status == "solver_failure"
    assert not result.quantities_kg_day


def test_real_feed_adapter_units() -> None:
    feed = example_feeds()[0]
    ingredient = ingredient_from_feed(
        feed, name="Alfalfa", nel_mcal_per_kg_dm=1.3, nel_source="Test fixed NEL", feed_source="RuFaS library"
    )
    assert ingredient.dm_fraction == pytest.approx(feed.DM / 100)
    assert ingredient.stock_kg * ingredient.dm_fraction == pytest.approx(feed.amount_available)
    assert ingredient.price_per_kg / ingredient.dm_fraction == pytest.approx(feed.purchase_cost)
    assert ingredient.maximum_kg_day * ingredient.dm_fraction == pytest.approx(feed.limit)
    assert ingredient.nel_mcal_per_kg_dm != feed.DE


def test_requirements_adapter_does_not_confuse_mp_cp_or_minerals() -> None:
    req = NutritionRequirements.make_empty_nutrition_requirements()
    req.dry_matter = 10
    req.metabolizable_protein = 2000
    req.calcium = 100
    req.lactation_energy = 20
    converted = requirements_from_rufas(req, cp_min_kg=3, nel_min_mcal=35, supplemental_source="Test")
    assert converted.cp_min_kg == 3
    assert converted.nel_min_mcal == 35
    assert converted.dm_min_kg == converted.dm_max_kg == 10
    assert converted.mineral_min_kg == {}


def test_real_calculator_library_and_supply_integration() -> None:
    animal, feeds = example_inputs()
    result = optimize_diet(animal, feeds, period_days=7)
    assert result.status == "optimal"
    assert result.totals["DM_kg"] == pytest.approx(animal.requirements.dm_min_kg)
    # The returned dictionary can be consumed on the exact basis used by RuFaS.
    ration = [FeedInRation(result.ration_kg_dm_day[feed.rufas_id], feed) for feed in example_feeds()]
    cp = NutritionSupplyCalculator._calculate_nutritive_content(ration, "CP")
    ndf = NutritionSupplyCalculator._calculate_nutritive_content(ration, "NDF")
    assert cp == pytest.approx(result.totals["CP_kg"])
    assert ndf == pytest.approx(result.totals["NDF_kg"])
    assert result.cost_per_day == pytest.approx(
        sum(result.ration_kg_dm_day[feed.rufas_id] * feed.purchase_cost for feed in example_feeds())
    )
    assert all(check.satisfied for check in result.checks)


def test_animal_snapshot_fields() -> None:
    from RUFAS.biophysical.animal.animal import Animal
    from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
    from RUFAS.biophysical.animal.milk.milk_production import MilkProduction

    # Real types, minimal initialized snapshot; avoid starting a whole-farm simulation.
    animal = object.__new__(Animal)
    animal.animal_type = AnimalType.LAC_COW
    animal.body_weight = 650
    animal.days_in_milk = 100
    animal.milk_production = object.__new__(MilkProduction)
    animal.milk_production._milk_production_variance = 0.0
    animal.milk_production.milk_production_reduction = 0.0
    animal.milk_production.daily_milk_produced = 30
    with (
        patch.object(MilkProduction, "fat_percent", 3.8, create=True),
        patch.object(MilkProduction, "true_protein_percent", 3.2, create=True),
    ):
        snapshot = profile_from_animal(animal, profile().requirements)
    assert snapshot.body_weight_kg == 650
    assert snapshot.days_in_milk == 100
    assert snapshot.milk_kg_day == 30
    assert snapshot.milk_fat_percent == 3.8


def test_example_tdn_matches_native_fraction_contract() -> None:
    from RUFAS.biophysical.animal.nutrients.nrc_requirements_calculator import NRCRequirementsCalculator
    from RUFAS.biophysical.animal.ration.linear_diet_catalog import random_cow

    original = NRCRequirementsCalculator.calculate_requirements
    for build in (example_inputs, lambda: random_cow(42)):
        with patch.object(NRCRequirementsCalculator, "calculate_requirements", wraps=original) as calculate:
            build()
        inputs = calculate.call_args.kwargs
        assert inputs["TDN_percentage"] == pytest.approx(0.65)
        corrected = original(**inputs)
        wrong = original(**{**inputs, "TDN_percentage": 65.0})
        assert corrected.metabolizable_protein > 0
        assert corrected.metabolizable_protein != pytest.approx(wrong.metabolizable_protein)
        # Only DMI is imported into the demonstration LP, so its optimum is preserved.
        assert corrected.dry_matter == pytest.approx(wrong.dry_matter)
    animal, feeds = example_inputs()
    result = optimize_diet(animal, feeds, period_days=7)
    assert result.status == "optimal"
    assert result.cost_per_day == pytest.approx(34.997773642175794)


def test_price_scenarios_are_comparable_and_do_not_mutate_inputs() -> None:
    from RUFAS.biophysical.animal.ration.linear_diet_sensitivity import compare_prices

    feeds = ingredients()
    result = compare_prices(profile(), feeds, {"double": {1: 2, 2: 4}})
    assert result["scenarios"]["base"]["result"]["cost_per_day"] == pytest.approx(15)
    assert result["scenarios"]["double"]["cost_delta_per_day"] == pytest.approx(15)
    assert [f.price_per_kg for f in feeds] == [1, 2]
    assert result == compare_prices(profile(), feeds, {"double": {1: 2, 2: 4}})
    with pytest.raises(ValueError, match="Unknown"):
        compare_prices(profile(), feeds, {"bad": {999: 2}})
    with pytest.raises(ValueError, match="Prices"):
        compare_prices(profile(), feeds, {"bad": {1: float("nan")}})
    impossible = [replace(f, stock_kg=0) for f in feeds]
    failed = compare_prices(profile(), impossible, {"double": {1: 2, 2: 4}})
    assert failed["scenarios"]["double"]["result"]["status"] == "infeasible"
    assert failed["scenarios"]["double"]["cost_delta_per_day"] is None


def test_ndf_fraction_rejects_undefined_zero_dm_domain() -> None:
    with pytest.raises(ValueError, match="strictly positive"):
        DietRequirements(0, 10, 0, 0, ndf_min_fraction=0.28)


def test_workflow_native_calculation_and_consumption() -> None:
    from RUFAS.biophysical.animal.ration.linear_diet_workflow import run_nrc_workflow
    from RUFAS.biophysical.animal.ration.linear_diet_example import example_calculator_inputs

    feeds = example_feeds()
    metadata = {
        f.rufas_id: dict(
            name=str(f.rufas_id),
            nel_mcal_per_kg_dm={1: 1.3, 44: 2.0, 167: 1.8}[f.rufas_id],
            nel_source="Test external NEL",
            feed_source="NRC library and test prices",
        )
        for f in feeds
    }
    thresholds = dict(
        cp_min_kg=3.6,
        nel_min_mcal=35.0,
        ndf_min_fraction=0.28,
        ndf_max_fraction=0.4,
        supplemental_source="Test external thresholds",
    )
    inputs = example_calculator_inputs()
    report = run_nrc_workflow(inputs, feeds, metadata, thresholds, period_days=7)
    assert report["result"]["status"] == "optimal"
    assert report["native_supply_kg_day"]["CP"] == pytest.approx(report["result"]["totals"]["CP_kg"])
    assert report["native_supply_kg_day"]["NDF"] == pytest.approx(report["result"]["totals"]["NDF_kg"])
    assert report["native_requirements"]["dry_matter"] == report["lp_animal"]["requirements"]["dm_min_kg"]
    assert report["result"]["cost_per_day"] == pytest.approx(34.997773642175794)
    with pytest.raises(ValueError, match="fraction"):
        run_nrc_workflow({**inputs, "TDN_percentage": 65.0}, feeds, metadata, thresholds)
    changed = run_nrc_workflow({**inputs, "milk_production": 20.0}, feeds, metadata, thresholds)
    assert changed["native_requirements"]["dry_matter"] != report["native_requirements"]["dry_matter"]
    failed = run_nrc_workflow(inputs, feeds, metadata, {**thresholds, "cp_min_kg": 10000.0})
    assert failed["result"]["status"] == "infeasible"
    assert failed["native_supply_kg_day"] is None
    assert failed["result"]["quantities_kg_day"] == {}
