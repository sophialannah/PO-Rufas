"""Regressões da aplicação local com o backend real."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

import numpy as np
import pytest

from frontend.service import (
    DEMO_ID,
    build_feeds,
    default_inputs,
    export_json,
    load_animals,
    load_catalog,
    nasem_phosphorus_diagnostic,
    run_scenario,
)
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.ration.linear_diet_adapter import ingredient_from_feed
from RUFAS.biophysical.animal.ration.linear_diet_integrated_example import demo_inputs
from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import NASEMRequirementsCalculator
from RUFAS.biophysical.animal.ration.ration_manager import RationManager


@pytest.fixture(scope="module")
def inputs():
    return load_animals(), load_catalog(), [dict(id=i, **v) for i, v in default_inputs().items()]


def solve(inputs, animal_id=DEMO_ID, milk=30, days=7):
    animals, catalog, rows = inputs
    return run_scenario(animals, catalog, animal_id, rows, milk, days, 3.6, 35, 28, 40)


def test_real_data_and_feed_conversion(inputs):
    animals, catalog, rows = inputs
    assert animals[DEMO_ID]["days_in_milk"] == 100
    assert animals[DEMO_ID]["body_weight"] == pytest.approx(627.560669)
    feeds, metadata = build_feeds(catalog, rows)
    for feed, row in zip(feeds, rows):
        ingredient = ingredient_from_feed(feed, **metadata[feed.rufas_id])
        assert ingredient.identifier == row["id"]
        assert ingredient.stock_kg == pytest.approx(row["stock"])
        assert ingredient.price_per_kg == pytest.approx(row["price"])
        assert ingredient.maximum_kg_day == pytest.approx(row["maximum"])
        assert ingredient.nel_mcal_per_kg_dm == row["nel"]


@pytest.mark.parametrize(("field", "value"), [("price", -1), ("stock", None), ("stock", float("inf")), ("minimum", 99)])
def test_parameter_validation(inputs, field, value):
    _, catalog, rows = inputs
    with pytest.raises(ValueError):
        build_feeds(catalog, [rows[0] | {field: value}])


def test_unsupported_animal_and_duplicates(inputs):
    _, catalog, rows = inputs
    with pytest.raises(ValueError, match="duplicado"):
        build_feeds(catalog, [rows[0], rows[0]])
    with pytest.raises(ValueError, match="Holandesa"):
        solve(inputs, animal_id=-1)


def test_infeasible(inputs):
    report = solve(inputs, days=10000)
    assert report["result"]["status"] == "infeasible"
    assert report["native_return"] is None


def test_integration_evaluation_and_export(inputs):
    report = solve(inputs)
    result, native = report["result"], report["native_return"]
    assert result["status"] == "optimal"
    assert result["cost_per_day"] == pytest.approx(35.1059017708)
    assert len(result["checks"]) == 11 and all(c["satisfied"] for c in result["checks"])
    assert native["ration_kg_dm_day"] == pytest.approx(result["ration_kg_dm_day"])
    evaluation = native["native_evaluation"]
    assert not evaluation["is_valid_cow_ration"]
    assert evaluation["deltas"]["phosphorus"] == pytest.approx(-6.6771465432)
    exported = json.loads(export_json(report))
    assert exported["animal"]["id"] == DEMO_ID
    assert exported["profile"]["requirements"]["sources"]
    assert exported["native_return"]["native_evaluation"] == evaluation
    assert exported["limitations"]


def test_parallel_requests_and_state_restored(inputs):
    owners = (
        (MilkProduction, "fat_percent"),
        (AnimalConfig, "simulate_genetics"),
        (RationManager, "user_defined_rations"),
    )
    before = [getattr(owner, key, None) for owner, key in owners]
    rng = np.random.get_state()
    other_id = next(i for i in inputs[0] if i != DEMO_ID)
    with ThreadPoolExecutor(max_workers=2) as executor:
        base, alternate = list(executor.map(lambda args: solve(inputs, *args), [(DEMO_ID, 30), (other_id, 31)]))
    assert base["profile"]["milk_kg_day"] == 30
    assert alternate["animal_id"] == other_id
    assert alternate["profile"]["milk_kg_day"] == 31
    assert [getattr(owner, key, None) for owner, key in owners] == before
    after = np.random.get_state()
    np.testing.assert_array_equal(after[1], rng[1])
    assert (after[0], *after[2:]) == (rng[0], *rng[2:])


def test_nasem_phosphorus_native_dispatch():
    with demo_inputs(animal_id=DEMO_ID) as (animal, _, _, _):
        standard = animal.nutrient_standard
        diagnostic = nasem_phosphorus_diagnostic(animal)
        assert animal.nutrient_standard is standard
        native = NASEMRequirementsCalculator._calculate_phosphorus_requirement(
            animal.body_weight,
            animal.mature_body_weight,
            animal.animal_type,
            animal.days_in_pregnancy if animal.is_pregnant else None,
            0,
            diagnostic["dmi_kg_day"],
            3.2,
            30,
            animal.calves,
        )
        expected = diagnostic["dmi_kg_day"] + 0.0006 * animal.body_weight + 30 * (0.49 + 0.13 * 3.2)
        assert diagnostic["requirement_g_day"] == pytest.approx(native)
        assert native == pytest.approx(expected)


def test_nasem_phosphorus_growth_gestation_and_floor():
    requirement = NASEMRequirementsCalculator._calculate_phosphorus_requirement
    physiology = (600.0, 700.0, AnimalType.LAC_COW)
    mature = requirement(*physiology, None, 0.5, 22.0, 3.2, 30.0, 3)
    young = requirement(*physiology, None, 0.5, 22.0, 3.2, 30.0, 2)
    assert young - mature == pytest.approx(0.5 * (1.2 + 4.635 * (700 / 600) ** 0.22))
    assert requirement(*physiology, 189, 0.5, 22.0, 3.2, 30.0, 3) == mature
    assert requirement(*physiology, 250, 0.5, 22.0, 3.2, 30.0, 3) > mature
    assert requirement(*physiology, None, 0.0, 0.0, 0.0, 0.0, 3) == pytest.approx(0.36)
    assert requirement(60.0, 700.0, AnimalType.CALF, None, 0.0, 0.0, 0.0, 0.0, 0) == 0


@pytest.mark.parametrize(
    ("animal_id", "milk", "baseline_cost", "deficit", "without_mineral"),
    [
        (98605, 30, 35.1059017708, -6.6771465432, "infeasible"),
        (93785, 31, 34.9440111041, -8.6107786857, "optimal"),
    ],
)
def test_nrc_absorbed_minerals_and_native_evaluation(inputs, animal_id, milk, baseline_cost, deficit, without_mineral):
    animals, catalog, rows = inputs
    baseline = solve(inputs, animal_id, milk)
    assert baseline["result"]["cost_per_day"] == pytest.approx(baseline_cost)
    assert baseline["native_return"]["native_evaluation"]["deltas"]["phosphorus"] == pytest.approx(deficit)
    constrained = run_scenario(animals, catalog, animal_id, rows, milk, 7, 3.6, 35, 28, 40, True)
    assert constrained["result"]["status"] == without_mineral
    if without_mineral == "infeasible":
        assert constrained["nrc_minerals"]["infeasibility"] == "phosphorus_conflict"
        assert constrained["native_return"] is None

    supplement = dict(id=231, price=5.0, stock=1.0, minimum=0.0, maximum=0.10, nel=0.0)
    report = run_scenario(animals, catalog, animal_id, rows + [supplement], milk, 7, 3.6, 35, 28, 40, True, True)
    result = report["result"]
    assert result["status"] == "optimal"
    assert len(result["checks"]) == 15 and all(check["satisfied"] for check in result["checks"])
    assert 0 < result["quantities_kg_day"][231] <= 0.10
    native = report["native_return"]
    assert native["ration_kg_dm_day"] == pytest.approx(result["ration_kg_dm_day"])
    minerals, evaluation = report["nrc_minerals"], native["native_evaluation"]
    phos = minerals["coefficients_g_per_kg_dm"]["phosphorus"]
    assert float(catalog[231]["composition"]["phosphorus"]) == 19.3
    assert phos[1] == pytest.approx(2.8 * 0.64)
    assert phos[44] == pytest.approx(float(catalog[44]["composition"]["phosphorus"]) * 10 * 0.70)
    assert phos[231] == pytest.approx(193 * 0.80)
    for mineral in ("phosphorus", "calcium"):
        row = next(c for c in result["checks"] if c["name"] == f"absorbed_{mineral}_g")
        assert row["supplied"] == pytest.approx(evaluation["supply_summary"][mineral + "_g"])
        assert evaluation["deltas"][mineral] >= 0
    assert minerals["phosphorus_total_g_day"] > evaluation["supply_summary"]["phosphorus_g"]
    assert evaluation["is_valid_cow_ration"]
    assert evaluation["criteria"] == dict.fromkeys(evaluation["deltas"], True)
    assert evaluation["deltas"]["fat_percent"] > 0
    assert report["nutrient_standard"] == "NRC 2001"
    assert json.loads(export_json(report))["nasem_phosphorus_diagnostic"]["standard"] == "NASEM 2021"


def test_streamlit_runs_real_solver_and_displays_native_alert():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "frontend/app.py"), default_timeout=30).run()
    assert not app.exception
    assert "report" not in app.session_state
    assert not any("Exigir fósforo" in field.label for field in app.checkbox)
    advanced = next(section for section in app.expander if section.label == "Configurações avançadas")
    diagnostic = next(field for field in advanced.checkbox if "NASEM 2021" in field.label)
    assert diagnostic.value is False
    next(button for button in app.button if button.label == "Executar otimização").click().run()
    assert not app.exception
    assert app.session_state["report"]["result"]["status"] == "infeasible"
    assert app.session_state["report"]["nrc_minerals"]["infeasibility"] == "phosphorus_conflict"
    assert app.session_state["report"]["nasem_phosphorus_diagnostic"] is None
    assert any("retirar somente o mínimo de fósforo" in warning.value for warning in app.warning)

    app.multiselect[0].select(231).run()
    editor = "editor-" + ",".join(map(str, app.multiselect[0].value))
    app.session_state[editor] = {
        "edited_rows": {3: dict(price=5.0, stock=1.0, minimum=0.0, maximum=0.1, nel=0.0)},
        "added_rows": [],
        "deleted_rows": [],
    }
    next(button for button in app.button if button.label == "Executar otimização").click().run()
    assert not app.exception
    without_diagnostic = app.session_state["report"]
    assert without_diagnostic["result"]["cost_per_day"] == pytest.approx(35.3416211228)
    assert any("Aprovada pelo NutritionEvaluator" in success.value for success in app.success)
    next(button for button in app.button if button.label == "Recalcular cenários").click().run()
    base, alternate = app.session_state["comparison_result"]
    assert base["Custo (R$/dia)"] == pytest.approx(35.3416211228)
    assert alternate["Custo (R$/dia)"] > base["Custo (R$/dia)"]

    next(field for field in app.number_input if field.label == "Período de estoque (dias)").set_value(10000)
    next(button for button in app.button if button.label == "Executar otimização").click().run()
    assert not app.exception
    assert any("Cenário inviável" in error.value for error in app.error)
    assert app.session_state["report"]["native_return"] is None

    next(field for field in app.number_input if field.label == "Período de estoque (dias)").set_value(7)
    next(field for field in app.checkbox if "NASEM 2021" in field.label).check()
    next(button for button in app.button if button.label == "Executar otimização").click().run()
    assert not app.exception
    assert any("Diagnóstico NASEM 2021" in component.value for component in app.markdown)
    assert app.session_state["report"]["nutrient_standard"] == "NRC 2001"
    report = app.session_state["report"]
    assert report["result"]["cost_per_day"] == without_diagnostic["result"]["cost_per_day"]
    assert report["result"]["quantities_kg_day"] == without_diagnostic["result"]["quantities_kg_day"]
    assert report["result"]["quantities_kg_day"][231] == pytest.approx(0.04418934)
    assert any("Balanço mineral" in component.value for component in app.subheader)
    assert any("Aprovada pelo NutritionEvaluator" in success.value for success in app.success)
