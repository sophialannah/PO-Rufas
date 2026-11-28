"""UI-only regressions using the published scenarios and annual evidence."""

import json
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from frontend.annual_history import GROUPS, evidence_jobs, read_daily, read_json
from frontend.service import load_catalog
from frontend.usability import economic_comparison, original_parameters, display_table, validated_demo

ROOT = Path(__file__).resolve().parents[1]


def test_original_catalog_parameters_do_not_invent_economics_or_energy():
    catalog = load_catalog()
    item = catalog[232]
    parameters = original_parameters(item)
    assert parameters["price"] is parameters["stock"] is parameters["nel"] is None
    dm = float(item["composition"]["DM"]) / 100
    assert parameters["maximum"] == float(item["composition"]["limit"]) / dm
    assert parameters["minimum"] == float(item["composition"]["lower_limit"]) / dm
    missing_source = item | {"composition": item["composition"] | {"limit": "", "lower_limit": ""}}
    assert original_parameters(missing_source)["maximum"] is None
    assert original_parameters(missing_source)["minimum"] is None


def test_validated_demo_comes_from_published_evidence():
    original = json.loads((ROOT / "evidencias/comparacao/configuracao.json").read_text())["rows"]
    demo = validated_demo(ROOT)
    assert set(demo) == {1, 44, 167, 231}
    assert demo[231] == {key: original[-1][key] for key in demo[231]}


@pytest.mark.parametrize(
    "original,po,winner,percentage",
    [
        (100, 90, "po", 10),
        (100, 110, "original", -10),
        (100, 100, "tie", 0),
        (0, 0, "tie", None),
        (0, 1, "original", None),
    ],
)
def test_economics_is_symmetric_and_handles_zero_reference(original, po, winner, percentage):
    result = economic_comparison(original, po)
    assert result["winner"] == winner
    assert result["percent"] == percentage
    assert result["absolute_difference"] == abs(original - po)


@pytest.mark.parametrize("cost", [float("nan"), float("inf"), -1])
def test_invalid_costs_are_not_presented_as_economy(cost):
    with pytest.raises(ValueError):
        economic_comparison(100, cost)


def test_translation_changes_display_only():
    frame = pd.DataFrame(
        [
            dict(
                strategy="native_slsqp",
                estimated_diet_cost=2319.34875854,
                milk_kg=140223.666523,
                elapsed_seconds=35,
                category="growing",
            )
        ]
    )
    original = frame.copy(deep=True)
    shown = display_table(frame)
    pd.testing.assert_frame_equal(frame, original)
    assert shown["Estratégia"].iloc[0] == "RuFaS original"
    assert shown["Custo alimentar estimado"].iloc[0] == frame["estimated_diet_cost"].iloc[0]
    assert "Produção de leite (kg)" in shown and "Tempo de execução (s)" in shown
    assert shown["Categoria"].iloc[0] == "Recria"


def test_published_evidence_loading_does_not_launch_workers():
    with patch("subprocess.Popen", side_effect=AssertionError("No new simulation")):
        jobs = evidence_jobs(ROOT, next(iter(GROUPS)))
    assert len(jobs) == 3
    assert all(j["source"] == "evidence" and "process" not in j for j in jobs)
    summaries = {j["strategy"]: read_json(Path(j["path"]) / "summary.json") for j in jobs}
    assert summaries["linear_highs_exclusive"]["estimated_diet_cost"] == pytest.approx(2316.451067700519)
    assert summaries["native_slsqp"]["estimated_diet_cost"] == pytest.approx(2319.3487585416196)


def test_cache_preserves_precision_and_invalidates_after_file_change(tmp_path):
    journal = tmp_path / "daily.jsonl"
    journal.write_text('{"cost": 2316.451067700519}\n', encoding="utf-8")
    first = read_daily(journal, 1)
    first[0]["cost"] = 0  # Cached data must not expose shared mutable state.
    assert read_daily(journal, 1)[0]["cost"] == 2316.451067700519
    with journal.open("a", encoding="utf-8") as stream:
        stream.write('{"cost": 0.12493553763438835}\n')
    assert read_daily(journal, 2)[1]["cost"] == 0.12493553763438835
    assert len(read_daily(journal, 1)) == 1


def test_multiselect_preserves_edits_and_demo_runs_real_solver():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(ROOT / "frontend/app.py", default_timeout=40).run()
    next(b for b in app.button if b.label == "Carregar cenário demonstrativo validado (4 ingredientes)").click().run()
    assert not app.exception
    assert app.multiselect[0].value == [1, 44, 167, 231]
    old_key = "editor-1,44,167,231"
    app.session_state[old_key] = dict(edited_rows={0: {"price": 2.0}}, added_rows=[], deleted_rows=[])
    app.run()
    app.multiselect[0].select(232).run()
    assert not app.exception
    assert app.session_state["ingredient_values"][1]["price"] == 2.0
    assert pd.isna(app.session_state["ingredient_values"][232]["nel"])
    assert any("Campos obrigatórios" in e.value for e in app.error)
    assert pd.isna(app.session_state["ingredient_values"][232]["price"])
    new_key = "editor-1,44,167,231,232"
    app.session_state[new_key] = dict(edited_rows={0: {"price": 2.5}}, added_rows=[], deleted_rows=[])
    app.multiselect[0].unselect(232).run()
    assert not app.exception
    assert app.session_state["ingredient_values"][1]["price"] == 2.5
    next(b for b in app.button if b.label == "Carregar cenário demonstrativo validado (4 ingredientes)").click().run()
    next(b for b in app.button if b.label == "Executar otimização").click().run()
    assert not app.exception
    report = app.session_state["report"]
    assert report["result"]["cost_per_day"] == pytest.approx(35.3416211228)
    assert report["result"]["quantities_kg_day"][231] == pytest.approx(0.04418934)
    next(s for s in app.number_input if s.label == "Repetições de medição").set_value(2)
    next(b for b in app.button if b.label == "Executar comparação dos otimizadores").click().run()
    next(s for s in app.selectbox if s.label == "Experimento").set_value("B · Formulações diferentes").run()
    assert not app.exception
    assert any(m.value == "RuFaS original" for m in app.metric if m.label == "Estratégia mais econômica")


def test_history_is_read_only_and_winner_changes_for_older_evidence():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(ROOT / "frontend/app.py", default_timeout=40).run()
    with (
        patch("frontend.annual.launch_runs", side_effect=AssertionError("No workers")),
        patch("frontend.annual.read_daily", side_effect=AssertionError("Load details only on request")),
    ):
        next(b for b in app.button if b.label == "Carregar resultados anuais das evidências").click().run()
        assert not app.exception
        assert len(app.session_state["annual_evidence_jobs"]) == 3
        assert any(m.value == "PO-RuFaS exclusivo" for m in app.metric if m.label == "Estratégia mais econômica")
        assert any("Resultados carregados de evidências" in c.value for c in app.caption)
        next(s for s in app.selectbox if s.label == "Conjunto de resultados arquivados").set_value(
            list(GROUPS)[1]
        ).run()
        next(b for b in app.button if b.label == "Carregar resultados anuais das evidências").click().run()
        assert not app.exception
        assert any(m.value == "RuFaS original" for m in app.metric if m.label == "Estratégia mais econômica")
    # Real historical series remain accessible without a simulation worker.
    next(c for c in app.checkbox if c.label == "Carregar séries diárias e detalhes desta execução").check().run()
    assert not app.exception
    assert any("Ca absorvível requerido (g)" in f.value.columns for f in app.dataframe)
