"""Regressões da aplicação local com o backend real."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

import numpy as np
import pytest

from frontend.service import DEMO_ID, build_feeds, default_inputs, export_json, load_animals, load_catalog, run_scenario
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.ration.linear_diet_adapter import ingredient_from_feed
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


def test_streamlit_runs_real_solver_and_displays_native_alert():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "frontend/app.py"), default_timeout=30).run()
    assert not app.exception
    assert "report" not in app.session_state
    next(button for button in app.button if button.label == "Executar otimização").click().run()
    assert not app.exception
    assert app.session_state["report"]["result"]["cost_per_day"] == pytest.approx(35.1059017708)
    assert any("35,1059" in metric.value for metric in app.metric)
    assert any("fósforo absorvível" in warning.value and "6,68 g/dia" in warning.value for warning in app.warning)
    assert any("Não aprovada" in error.value for error in app.error)
    next(button for button in app.button if button.label == "Recalcular cenários").click().run()
    base, alternate = app.session_state["comparison_result"]
    assert base["Custo (R$/dia)"] == pytest.approx(35.1059017708)
    assert alternate["Custo (R$/dia)"] > base["Custo (R$/dia)"]

    next(field for field in app.number_input if field.label == "Período de estoque (dias)").set_value(10000)
    next(button for button in app.button if button.label == "Executar otimização").click().run()
    assert not app.exception
    assert any("Cenário inviável" in error.value for error in app.error)
    assert app.session_state["report"]["native_return"] is None
