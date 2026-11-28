"""Regression tests for daily native-loop integration and strategy provenance."""

import json
from pathlib import Path
import random
import subprocess
import sys

import numpy as np
import pytest

from RUFAS.biophysical.animal.ration.dynamic_linear_optimizer import DynamicRationOptimizer
from RUFAS.biophysical.animal.ration.linear_diet_integrated_example import demo_inputs
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination


def test_invalid_strategy():
    with pytest.raises(ValueError, match="strategy"):
        DynamicRationOptimizer("unknown")


def test_native_dispatch_preserves_solver():
    with demo_inputs() as (animal, feeds, _, _):
        requirements = animal.calculate_nutrition_requirements("Barn", 0.0, 20.0, feeds)
        kwargs = dict(
            nutrient_standard=animal.nutrient_standard,
            pen_average_body_weight=animal.body_weight,
            pen_average_enteric_methane=None,
            pen_average_urine_nitrogen=None,
            requirements=requirements,
            initial_dry_matter_requirement=requirements.dry_matter,
            initial_protein_requirement=requirements.metabolizable_protein,
            pen_available_feeds=feeds,
            animal_combination=AnimalCombination.LAC_COW,
        )
        saved = random.getstate()
        try:
            random.seed(17)
            expected, _ = RationOptimizer().attempt_optimization(**kwargs)
            random.seed(17)
            optimizer = DynamicRationOptimizer("native_slsqp")
            actual, _ = optimizer.attempt_optimization(**kwargs)
            np.testing.assert_allclose(actual.x, expected.x, atol=0, rtol=0)
            assert actual.success == expected.success
            assert optimizer.events[0]["used"] == "native_slsqp"
        finally:
            random.setstate(saved)


def test_fallback_is_explicit():
    with demo_inputs() as (animal, feeds, _, _):
        requirements = animal.calculate_nutrition_requirements("Barn", 0.0, 20.0, feeds)
        optimizer = DynamicRationOptimizer("linear_highs", max_iterations=0)
        optimizer.attempt_optimization(
            nutrient_standard=animal.nutrient_standard,
            pen_average_body_weight=animal.body_weight,
            pen_average_enteric_methane=None,
            pen_average_urine_nitrogen=None,
            requirements=requirements,
            initial_dry_matter_requirement=requirements.dry_matter,
            initial_protein_requirement=requirements.metabolizable_protein,
            pen_available_feeds=feeds,
            animal_combination=AnimalCombination.LAC_COW,
        )
        assert optimizer.events[0]["used"] == "linear_highs"
        assert not optimizer.events[0]["success"]
        assert optimizer.events[1]["reason"] == "highs_failure_or_native_rejection"


def run_worker(target, strategy):
    completed = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "experiments.annual",
            "--days",
            "2",
            "--strategy",
            strategy,
            "--output",
            str(target),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads((target / "summary.json").read_text()), [
        json.loads(line) for line in (target / "daily.jsonl").read_text(encoding="utf-8").splitlines()
    ]


def test_real_daily_loop_inventory_and_reproducibility(tmp_path):
    first, records = run_worker(tmp_path / "first", "linear_highs")
    second, repeated = run_worker(tmp_path / "second", "linear_highs")
    assert first["simulated_days"] == second["simulated_days"] == 2
    assert first["highs_attempts"] >= 2 and first["highs_accepted"] > 0
    assert first["unsupported_native"] > 0
    assert first["estimated_diet_cost"] == pytest.approx(second["estimated_diet_cost"])
    assert [r["day"] for r in records] == [0, 1]
    assert first["estimated_diet_cost"] == pytest.approx(sum(r["estimated_diet_cost"] for r in records))
    assert first["milk_kg"] == second["milk_kg"]
    assert records[0]["animals"][0]["category"] == repeated[0]["animals"][0]["category"]
    assert any(a != b for a, b in zip(records[0]["animals"], records[1]["animals"]))
    for record in records:
        assert all(v >= -1e-6 for v in record["inventory_kg_dm"].values())
        assert any(v > 0 for v in record["fed_kg_dm"].values())
    assert any(
        event["trace"] and event["trace"][-1]["lp_status"] == "optimal"
        for record in records
        for event in record["formulations"]
        if event["used"] == "linear_highs"
    )


def test_annual_frontend_starts_isolated_real_workers():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "frontend/app.py", default_timeout=30).run()
    next(radio for radio in app.radio if radio.label == "Tipo de análise").set_value(
        "Simulação dinâmica integrada"
    ).run()
    assert not app.exception
    next(field for field in app.number_input if field.label == "Duração dinâmica (dias)").set_value(1)
    for label, alternative in (
        ("Comparação SLSQP versus HiGHS híbrido", "linear_highs_all"),
        ("Comparação SLSQP versus HiGHS exclusivo", "linear_highs_exclusive"),
    ):
        next(field for field in app.selectbox if field.label == "Otimizador dinâmico").set_value(label).run()
        next(button for button in app.button if button.label == "Iniciar simulação dinâmica").click().run()
        jobs = app.session_state["annual_jobs"][-2:]
        assert [job["strategy"] for job in jobs] == ["native_slsqp", alternative]
        assert jobs[0]["path"] != jobs[1]["path"]
        for job in jobs:
            assert job["process"].wait(timeout=120) == 0
            result = json.loads((Path(job["path"]) / "summary.json").read_text())
            assert result["simulated_days"] == 1 and result["status"] == "complete"
            if job["strategy"] == "linear_highs_exclusive":
                assert result["native_attempts"] == result["fallbacks"] == 0
        app.run()
        assert not app.exception
