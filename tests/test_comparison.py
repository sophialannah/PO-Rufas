"""Real solver comparison regressions."""

import json
from pathlib import Path
import pytest

from experiments.comparison import compare_models, json_text
from frontend.service import default_inputs


@pytest.mark.parametrize("animal,milk", [(98605, 30), (93785, 31)])
def test_identical_lp_and_native_candidate(animal, milk):
    rows = [dict(id=i, **values) for i, values in default_inputs().items()]
    rows.append(dict(id=231, price=5.0, stock=1.0, minimum=0.0, maximum=0.10, nel=0.0))
    original = json.dumps(rows)
    report = compare_models(animal, rows, milk, repeats=2)
    assert json.dumps(rows) == original
    high, slsqp = report["methods"]["A_HiGHS"], report["methods"]["A_SLSQP"]
    assert high["cost_per_day"] == pytest.approx(report["reference"]["result"]["cost_per_day"], abs=1e-7)
    assert high["cost_per_day"] == pytest.approx(slsqp["cost_per_day"], abs=1e-6)
    for candidate in (high, slsqp):
        assert candidate["success"] and candidate["feasible"]
        assert all(row["satisfied"] for row in candidate["checks"])
        assert candidate["native"]["approved"]
    assert not report["equivalent_experiment_B"]
    for candidate in report["methods"].values():
        assert len(candidate["timing"]["runs"]) == 2
        assert sum(candidate["quantities_kg_dm_day"].values()) == pytest.approx(
            candidate["native"]["supply"]["dry_matter"]
        )
        assert candidate["native"]["approved"] == candidate["native"]["criteria"]["is_valid_cow_ration"]
    assert json.loads(json_text(report))["animal_id"] == animal


def test_invalid_repetitions():
    with pytest.raises(ValueError, match="repetições"):
        compare_models(98605, [], repeats=1)


def test_frontend_comparison_executes_real_models():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "frontend/app.py", default_timeout=40).run()
    app.multiselect[0].select(231).run()
    editor = "editor-" + ",".join(map(str, app.multiselect[0].value))
    app.session_state[editor] = {
        "edited_rows": {3: dict(price=5.0, stock=1.0, minimum=0.0, maximum=0.1, nel=0.0)},
        "added_rows": [],
        "deleted_rows": [],
    }
    next(field for field in app.number_input if field.label == "Repetições de medição").set_value(2)
    next(button for button in app.button if button.label == "Executar comparação dos otimizadores").click().run()
    assert not app.exception
    report = app.session_state["optimizer_comparison"]
    assert report["methods"]["A_HiGHS"]["cost_per_day"] == pytest.approx(35.3416211228)
    assert len(report["methods"]) == 3
