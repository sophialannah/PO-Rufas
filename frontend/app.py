"""Interface Streamlit do projeto PO-RuFaS."""

import logging
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

# Streamlit também aceita a execução direta por caminho de arquivo.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from frontend.results import money, native_status, requirements_table, show_results
from frontend.service import (
    COMPOSITION,
    DEMO_ID,
    INPUTS,
    POPULATION,
    animal_requirements,
    default_inputs,
    load_animals,
    load_catalog,
    run_scenario,
)

LOGGER = logging.getLogger(__name__)
CATALOG_COLUMNS = [
    "id",
    "Ingrediente",
    "Tipo NRC",
    "MS (% MN)",
    "PB (% MS)",
    "FDN (% MS)",
    "P total (% MS)",
    "Ca total (% MS)",
    "Composição",
]


def animal_panel(record: dict, milk: float) -> None:
    st.caption(f"População do RuFaS · {POPULATION}")
    cols = st.columns(4)
    for col, label, value in zip(
        cols,
        ("Raça", "Peso corporal", "Dias em lactação", "Paridade"),
        ("Holandesa (HO)", f"{record['body_weight']:.2f} kg", record["days_in_milk"], record["parity"]),
    ):
        col.metric(label, value)
    st.info(
        f"Hipóteses do cenário · leite {milk:g} kg/dia · gordura 3,8% · proteína verdadeira 3,2% · lactose 4,8%. "
        "Alojamento Barn, caminhada zero e temperatura anterior de 20 °C."
    )
    st.subheader("Exigências calculadas pelo NRC")
    st.caption("Prévia calculada com os ingredientes da demonstração. O resultado registra as exigências da execução.")
    if milk <= 0:
        st.warning("Informe produção de leite positiva.")
        return
    try:
        with st.spinner("Calculando exigências…"):
            requirements = preview_requirements(record["id"], milk)
        st.dataframe(requirements_table(requirements), hide_index=True)
    except (ValueError, RuntimeError, KeyError, ArithmeticError):
        LOGGER.exception("Falha ao calcular prévia NRC")
        st.error("O RuFaS não conseguiu calcular as exigências para este animal e cenário.")


@st.cache_data(show_spinner=False)
def preview_requirements(animal_id: int, milk: float) -> dict:
    return animal_requirements(animal_id, milk)


def ingredient_record(item: dict) -> dict:
    row = item["composition"]
    return dict(
        zip(
            CATALOG_COLUMNS,
            [
                item["identifier"],
                item["name"],
                row["feed_type"],
                float(row["DM"]),
                float(row["CP"]) if row["CP"] else None,
                float(row["NDF"]) if row["NDF"] else None,
                float(row["phosphorus"]) if row["phosphorus"] else None,
                float(row["calcium"]) if row["calcium"] else None,
                item["composition_source"],
            ],
        )
    )


def ingredient_panel(catalog: dict, defaults: dict) -> list[dict]:
    st.header("Ingredientes NRC")
    st.caption(f"Composição da biblioteca {COMPOSITION}. MN = matéria natural · MS = matéria seca.")
    left, right = st.columns(2)
    query = left.text_input("Buscar por nome ou ID").strip().casefold()
    kind = right.selectbox(
        "Tipo de ingrediente",
        ["Todos", "Forage", "Conc", "Mineral"],
        format_func={"Todos": "Todos", "Forage": "Forragem", "Conc": "Concentrado", "Mineral": "Mineral"}.get,
    )
    visible = [
        ingredient_record(item) | {"NEL demo (Mcal/kg MS)": defaults.get(identifier, {}).get("nel")}
        for identifier, item in catalog.items()
        if (kind == "Todos" or item["composition"]["feed_type"] == kind)
        and (query in item["name"].casefold() or query in str(identifier))
    ]
    st.dataframe(pd.DataFrame(visible), hide_index=True)
    if not visible:
        st.info("Nenhum ingrediente corresponde aos filtros.")
    selected = st.multiselect(
        "Ingredientes disponíveis para a otimização",
        list(catalog),
        default=[identifier for identifier in defaults if identifier in catalog],
        format_func=lambda identifier: f"{identifier} · {catalog[identifier]['name']}",
    )
    st.caption(
        "Preços, estoques, limites e NEL pré-preenchidos são hipóteses da demonstração. "
        "Para os demais ingredientes, preencha os campos antes de executar."
    )
    st.caption(
        "O filtro Mineral inclui os fosfatos 231 e 232. Informe os dados econômicos, a inclusão máxima e a NEL de cada fonte selecionada."
    )
    edits = st.session_state.setdefault("ingredient_values", {})
    # A base fica fixa para cada seleção. Os deltas do editor sobrevivem a reruns.
    base = st.session_state.get("ingredient_editor_base")
    if not base or base[0] != selected:
        st.session_state["ingredient_editor_base"] = (
            selected.copy(),
            {i: edits.get(i, defaults.get(i, {})).copy() for i in selected},
        )
    _, saved = st.session_state["ingredient_editor_base"]
    rows = [ingredient_record(catalog[i]) | {k: saved[i].get(k) for k in INPUTS} for i in selected]
    frame = pd.DataFrame(rows, columns=CATALOG_COLUMNS + list(INPUTS))
    if selected:
        frame = st.data_editor(
            frame.astype({k: float for k in INPUTS}),
            hide_index=True,
            disabled=CATALOG_COLUMNS,
            key="editor-" + ",".join(map(str, selected)),
            column_config={
                "id": "ID RuFaS",
                **{
                    key: st.column_config.NumberColumn(label, min_value=0.0, format="%.4f")
                    for key, label in INPUTS.items()
                },
            },
        )
    st.download_button(
        "Baixar ingredientes selecionados (CSV)",
        frame.rename(columns=INPUTS).to_csv(index=False).encode("utf-8-sig"),
        "ingredientes.csv",
        "text/csv",
        disabled=not selected,
    )
    records = frame.to_dict("records")
    edits.update({row["id"]: {k: row[k] for k in INPUTS} for row in records})
    return records


def run(animals: dict, catalog: dict, animal_id: int, rows: list[dict], milk: float, inputs: tuple) -> dict | None:
    try:
        with st.spinner("Executando HiGHS e avaliação nutricional RuFaS…"):
            return run_scenario(animals, catalog, animal_id, rows, milk, *inputs)
    except ValueError as error:
        st.error(str(error))
    except (RuntimeError, KeyError, ArithmeticError):
        LOGGER.exception("Falha na otimização integrada")
        st.error("Falha durante o cálculo ou retorno ao RuFaS. Revise os parâmetros do cenário.")
    return None


def compare(animals: dict, catalog: dict, animal_id: int, rows: list[dict], milk: float, inputs: tuple) -> None:
    st.header("Cenários")
    st.caption(
        "Recalcule a mesma formulação após variar um parâmetro de um ingrediente. Diferenças são custos modelados."
    )
    if not rows:
        st.info("Selecione ingredientes para comparar cenários.")
        return
    with st.form("comparison"):
        names = {row["id"]: row["Ingrediente"] for row in rows}
        target = st.selectbox("Ingrediente da variação", list(names), format_func=names.get)
        field = st.selectbox("Parâmetro alterado", list(INPUTS)[:-1], format_func=INPUTS.get)
        variation = st.number_input("Variação (%)", min_value=-100.0, value=10.0, step=1.0)
        submitted = st.form_submit_button("Recalcular cenários")
    if submitted:
        st.session_state.pop("comparison_result", None)
        baseline = run(animals, catalog, animal_id, rows, milk, inputs)
        if baseline is None:
            return
        changed = [row | {field: row[field] * (1 + variation / 100)} if row["id"] == target else row for row in rows]
        alternate = run(animals, catalog, animal_id, changed, milk, inputs)
        if alternate is not None:
            st.session_state["comparison_result"] = [
                {
                    "Cenário": label,
                    "LP": report["result"]["status"],
                    "Animal": report["animal_id"],
                    "Dias": report["period_days"],
                    "Custo (R$/dia)": report["result"]["cost_per_day"],
                    "RuFaS": native_status(report),
                }
                for label, report in [
                    ("Base", baseline),
                    (f"{names[target]} · {INPUTS[field]} {variation:+g}%", alternate),
                ]
            ]
    if comparison := st.session_state.get("comparison_result"):
        st.caption("Última comparação executada")
        st.dataframe(pd.DataFrame(comparison), hide_index=True)
    st.subheader("Comparação dos otimizadores")
    experiment = st.selectbox(
        "Experimento",
        ["A · Mesmo LP", "B · Formulações diferentes"],
        help="A usa a matriz do LP nos dois algoritmos. B inclui a formulação nutricional nativa do RuFaS.",
    )
    repetitions = st.number_input("Repetições de medição", min_value=2, max_value=20, value=5, step=1)
    if st.button("Executar comparação dos otimizadores"):
        from experiments.comparison import compare_models

        try:
            with st.spinner("Resolvendo modelos e avaliando candidatas…"):
                st.session_state["optimizer_comparison"] = compare_models(
                    animal_id,
                    rows,
                    milk,
                    *inputs,
                    repeats=repetitions,
                )
        except (ValueError, RuntimeError, KeyError, ArithmeticError) as error:
            st.error(str(error))
    if report := st.session_state.get("optimizer_comparison"):
        from experiments.comparison import json_text

        selected_methods = ["A_HiGHS", "A_SLSQP"] if experiment.startswith("A") else ["A_HiGHS", "B_SLSQP_native"]
        st.caption(f"Última execução · animal {report['animal_id']} · NRC 2001 · {report['days']} dias")
        if experiment.startswith("B"):
            st.warning("Formulações diferentes. Consumo e restrições nutricionais variam entre os modelos.")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Método": name,
                        "Convergiu": method["success"],
                        "Viável na tolerância": method["feasible"],
                        "R$/dia": method["cost_per_day"],
                        "R$/kg leite assumido": method["cost_per_kg_milk"],
                        "MS (kg/dia)": sum(method["quantities_kg_dm_day"].values()),
                        "Tempo mediano (s)": method["timing"]["median_seconds"],
                        "Iterações": method["iterations"],
                        "Parecer RuFaS": method["native"]["approved"],
                    }
                    for name in selected_methods
                    for method in [report["methods"][name]]
                ]
            ),
            hide_index=True,
        )
        st.caption("Parecer da última candidata de cada método. O JSON contém as candidatas de todas as repetições.")
        st.download_button(
            "Baixar comparação completa (JSON)", json_text(report), "comparacao.json", "application/json"
        )
        with st.expander("Conferir restrições, folgas, ofertas e pareceres"):
            st.json({name: report["methods"][name] for name in selected_methods}, expanded=1)


def overview(report: dict | None, animal_id: int, available: int, selected: int) -> None:
    st.subheader("Visão geral")
    st.write(
        "Otimização linear do custo de dietas para bovinos leiteiros com integração aos componentes de nutrição e alimentação do RuFaS."
    )
    result = report["result"] if report else {}
    native = report and report["native_return"]
    first = st.columns(3)
    first[0].metric("Animal selecionado", str(animal_id))
    first[1].metric("Ingredientes no catálogo", available)
    first[2].metric("Método de otimização", "HiGHS")
    second = st.columns(3)
    second[0].metric("Última execução do LP", result.get("status", "Pendente"))
    second[1].metric("Último custo diário", money(result.get("cost_per_day")))
    second[2].metric("Avaliação RuFaS", native_status(report) if report else "Pendente")
    if report:
        st.caption(f"Última execução · cenário {report['scenario_id']} · animal {report['animal_id']}")
    st.subheader("Fluxo integrado")
    stages = [
        (True, "Animal RuFaS"),
        (bool(report), "Exigências"),
        (selected > 0, "Ingredientes"),
        (bool(report), "Solver"),
        (bool(native), "Dieta"),
        (bool(native), "RationManager"),
        (bool(native), "Avaliação nutricional"),
    ]
    st.markdown(" → ".join(("✓ " if done else "○ ") + label for done, label in stages))
    st.caption("As etapas a partir do solver mostram o estado da última execução.")
    st.divider()
    st.caption("Projeto acadêmico de Pesquisa Operacional")
    st.write("Sophia Lannah Beatriz Ferreira de Sousa · Anderson Alberto da Costa Silva")


def main() -> None:
    st.set_page_config(page_title="PO-RuFaS | Otimização Inteligente de Dietas", layout="wide")
    st.html(Path(__file__).with_name("style.css"))
    st.title("PO-RuFaS | Otimização Inteligente de Dietas")
    try:
        animals, catalog, defaults = st.cache_data(load_animals)(), st.cache_data(load_catalog)(), default_inputs()
        if DEMO_ID not in animals or not catalog:
            raise ValueError("Dados base incompletos.")
    except (OSError, KeyError, ValueError):
        LOGGER.exception("Falha ao carregar arquivos de entrada")
        st.error("Não foi possível carregar os arquivos de população ou composição NRC do repositório.")
        st.stop()

    with st.sidebar:
        st.header("Animal do cenário")
        ids = [DEMO_ID, *sorted(animals.keys() - {DEMO_ID})]
        animal_id = st.selectbox("ID RuFaS", ids, format_func=lambda i: f"{i} · Holandesa em lactação")
        milk = st.number_input("Produção de leite assumida (kg/dia)", min_value=0.0, value=30.0, step=0.5)
        st.caption("Padrão da formulação e da avaliação nativa · NRC 2001 · vacas Holandesas em lactação")

    home, animal, ingredients, optimization, results, scenarios, annual = st.tabs(
        ["Visão geral", "Animal", "Ingredientes", "Otimização", "Resultados", "Cenários", "Simulação anual"]
    )
    with animal:
        st.header(f"Animal {animal_id}")
        animal_panel(animals[animal_id], milk)
    with ingredients:
        rows = ingredient_panel(catalog, defaults)
    with optimization:
        st.header("Otimização")
        st.caption(
            f"Animal {animal_id} · {len(rows)} ingredientes selecionados. Edite disponibilidade e preços na aba Ingredientes."
        )
        st.write("O NRC fornece a meta diária de matéria seca. PB, NEL e FDN são metas externas do cenário.")
        if milk > 0:
            try:
                dmi = preview_requirements(animal_id, milk)["dry_matter"]
                st.metric("Consumo de MS calculado na prévia", f"{dmi:.3f} kg/dia")
            except (ValueError, RuntimeError, KeyError, ArithmeticError):
                st.warning("Prévia de consumo indisponível para este animal.")
        a, b, c = st.columns(3)
        days = a.number_input("Período de estoque (dias)", min_value=1, value=7, step=1)
        cp = b.number_input("PB mínima (kg/dia)", min_value=0.0, value=3.6, step=0.1)
        nel = c.number_input("NEL mínima (Mcal/dia)", min_value=0.0, value=35.0, step=0.5)
        a, b = st.columns(2)
        ndf_min = a.number_input("FDN mínima (% MS)", min_value=0.0, max_value=100.0, value=28.0)
        ndf_max = b.number_input("FDN máxima (% MS)", min_value=0.0, max_value=100.0, value=40.0)
        minerals = st.checkbox(
            "Exigir fósforo e cálcio absorvíveis no LP (NRC 2001)",
            help="Usa as exigências NRC e a oferta por categoria calculada pelo RuFaS.",
        )
        nasem = st.checkbox(
            "Calcular exigência de fósforo NASEM 2021 para diagnóstico",
            help="Calcula a exigência em separado, sem alterar a formulação nem emitir parecer NASEM.",
        )
        inputs = (days, cp, nel, ndf_min, ndf_max, minerals, nasem)
        if st.button("Executar otimização", type="primary"):
            st.session_state["report"] = run(animals, catalog, animal_id, rows, milk, inputs)
            if st.session_state["report"]:
                result = st.session_state["report"]["result"]
                st.info(f"HiGHS · {result['status']}. Abra Resultados para consultar a execução.")
    report = st.session_state.get("report")
    with home:
        overview(report, animal_id, len(catalog), len(rows))
    with results:
        show_results(report)
    with scenarios:
        compare(animals, catalog, animal_id, rows, milk, inputs)
    with annual:
        from frontend.annual import annual_panel

        annual_panel()


main()
