"""Real Animal -> NRC -> LP -> RationManager -> native supply, without mocks."""

from dataclasses import replace
import pytest
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.biophysical.animal.ration.linear_diet import DietResult
from RUFAS.biophysical.animal.ration.linear_diet_integration import optimize_animal_ration, ration_config_from_result
from RUFAS.biophysical.animal.ration.linear_diet_integrated_example import demo_inputs
from RUFAS.data_structures.feed_storage_to_animal_connection import NutrientStandard


def test_real_animal_roundtrip_and_original_manager_unchanged():
    previous = getattr(RationManager, "user_defined_rations", None)
    previous_tol = getattr(RationManager, "tolerance", None)
    previous_std = getattr(NutritionSupplyCalculator, "nutrient_standard", None)
    with demo_inputs() as (animal, feeds, metadata, thresholds):
        assert isinstance(animal, Animal)
        stocks = [f.amount_available for f in feeds]
        report = optimize_animal_ration(animal, feeds, metadata, thresholds, period_days=7)
        assert report["result"]["status"] == "optimal"
        assert all(c["satisfied"] for c in report["result"]["checks"])
        returned = report["native_return"]
        assert returned["ration_feeds"] == [f.rufas_id for f in feeds]
        assert sum(f["ration_percentage"] for f in returned["config"]["rations"][0]["feeds"]) == pytest.approx(100)
        assert returned["ration_kg_dm_day"] == pytest.approx(report["result"]["ration_kg_dm_day"])
        assert sum(returned["ration_kg_dm_day"].values()) == pytest.approx(report["requirements"]["dry_matter"])
        assert returned["supply_kg"]["CP"] == pytest.approx(report["result"]["totals"]["CP_kg"])
        assert returned["supply_kg"]["NDF"] == pytest.approx(report["result"]["totals"]["NDF_kg"])
        eval_info = returned["native_evaluation"]
        assert eval_info["supply_summary"]["metabolizable_protein_g"] > report["requirements"]["metabolizable_protein"]
        assert eval_info["deltas"]["dry_matter"] == pytest.approx(0.0)
        assert eval_info["deltas"]["phosphorus"] < 0
        assert eval_info["is_valid_cow_ration"] is False
        assert report["result"]["cost_per_day"] == pytest.approx(
            sum(returned["ration_kg_dm_day"][f.rufas_id] * f.purchase_cost for f in feeds)
        )
        assert [f.amount_available for f in feeds] == stocks
        assert getattr(RationManager, "user_defined_rations", None) is previous
        assert getattr(RationManager, "tolerance", None) is previous_tol
        assert getattr(NutritionSupplyCalculator, "nutrient_standard", None) is previous_std
        assert optimize_animal_ration(animal, feeds, metadata, thresholds, period_days=7) == report


def test_integration_rejects_unsupported_animal_or_standard():
    with demo_inputs() as (animal, feeds, metadata, thresholds):
        animal.nutrient_standard = NutrientStandard.NASEM
        with pytest.raises(ValueError, match="NRC lactating cows"):
            optimize_animal_ration(animal, feeds, metadata, thresholds)
        animal.nutrient_standard = NutrientStandard.NRC
        animal.animal_type = AnimalType.DRY_COW
        with pytest.raises(ValueError, match="NRC lactating cows"):
            optimize_animal_ration(animal, feeds, metadata, thresholds)


def test_infeasible_result_never_reaches_native_ration():
    with demo_inputs() as (animal, feeds, metadata, thresholds):
        report = optimize_animal_ration(animal, feeds, metadata, {**thresholds, "cp_min_kg": 10000})
        assert report["result"]["status"] == "infeasible"
        assert report["native_return"] is None
        with pytest.raises(ValueError, match="optimal"):
            ration_config_from_result(DietResult("infeasible", "test"), feeds)


def test_output_rejects_duplicate_or_changed_feed_composition():
    with demo_inputs() as (animal, feeds, metadata, thresholds):
        report = optimize_animal_ration(animal, feeds, metadata, thresholds)
        from RUFAS.biophysical.animal.ration.linear_diet import ConstraintCheck

        result = DietResult(
            **{**report["result"], "checks": [ConstraintCheck(**c) for c in report["result"]["checks"]]}
        )
        with pytest.raises(ValueError, match="IDs"):
            ration_config_from_result(result, [feeds[0], feeds[0]])
        with pytest.raises(ValueError, match="DM"):
            ration_config_from_result(result, [replace(feeds[0], DM=50), *feeds[1:]])


def test_integrated_demo_cli_executes_cleanly(monkeypatch, capsys):
    import sys
    from RUFAS.biophysical.animal.ration import linear_diet_integrated_example

    monkeypatch.setattr(sys, "argv", ["linear_diet_integrated_example", "--auto"])
    linear_diet_integrated_example.main()
    out = capsys.readouterr().out
    assert "98605" in out
    assert "35.1059" in out
    assert "RationManager" in out
    assert "NutritionEvaluator" in out
