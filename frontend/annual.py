"""Launch and inspect isolated full-farm simulations from Streamlit."""

import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pandas as pd
import streamlit as st
from frontend.annual_history import history_panel, read_json, read_daily, economic_cards
from frontend.usability import display_table, label, COLUMNS

ROOT = Path(__file__).resolve().parents[1]

STRATEGIES = {
    "Comparação SLSQP versus HiGHS híbrido": ["native_slsqp", "linear_highs_all"],
    "Comparação SLSQP versus HiGHS exclusivo": ["native_slsqp", "linear_highs_exclusive"],
    "SLSQP nativo controlado": ["native_slsqp"],
    "HiGHS híbrido ampliado": ["linear_highs_all"],
    "HiGHS exclusivo": ["linear_highs_exclusive"],
}


def launch_runs(strategies, days, cows, seed, interval, fallback, overrides, adult_ids):
    folder = ROOT / "output" / "annual_ui" / uuid4().hex
    folder.mkdir(parents=True)
    inputs = folder / "economics.json"
    inputs.write_text(json.dumps(overrides, indent=2), encoding="utf-8")
    jobs = []
    for strategy in strategies:
        destination = folder / strategy
        command = [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "experiments.annual",
            "--days",
            str(days),
            "--cows",
            str(cows),
            "--seed",
            str(seed),
            "--interval",
            str(interval),
            "--strategy",
            strategy,
            "--fallback",
            fallback,
            "--output",
            str(destination),
            "--feed-overrides",
            str(inputs),
            "--adult-feed-ids",
            ",".join(map(str, adult_ids)),
        ]
        with (folder / f"{strategy}.log").open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                stdout=log,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
        jobs.append(dict(path=str(destination), strategy=strategy, process=process, requested_days=days))
    return jobs


def annual_panel():
    st.header("Simulação anual")
    mode = st.radio("Tipo de análise", ["Otimização estática de um dia", "Simulação dinâmica integrada"])
    history_panel(ROOT)
    if mode.startswith("Otimização"):
        st.info("Selecione o animal e configure a dieta nas áreas Animal, Ingredientes e Otimização.")
        show_jobs()
        return
    st.caption("Cenário Freestall NRC experimental, clima de 2013 e rebanho inicial amostrado da população RuFaS.")
    st.warning(
        "HiGHS híbrido registra cada fallback. HiGHS exclusivo interrompe em falhas e nunca chama SLSQP. "
        "A aprovação nativa não certifica adequação nutricional completa. Tetos totais NRC 2005 são aplicados igualmente aos modelos."
    )
    a, b, c = st.columns(3)
    days = a.number_input("Duração dinâmica (dias)", min_value=1, max_value=365, value=365)
    cows = b.number_input("Meta de vacas iniciais", min_value=6, max_value=100, value=10)
    seed = c.number_input("Semente dinâmica", min_value=1, value=42)
    interval = st.number_input("Intervalo de reformulação (dias)", min_value=1, max_value=30, value=1)
    option = st.selectbox("Otimizador dinâmico", list(STRATEGIES))
    strategies = STRATEGIES[option]
    exclusive = "linear_highs_exclusive" in strategies
    if exclusive:
        st.info("HiGHS exclusivo: não há fallback para SLSQP. Uma falha interrompe essa execução e fica registrada.")
    fallback = st.selectbox(
        "Política de falha ou categoria incompatível",
        ["fail"] if exclusive else ["native_slsqp", "fail"],
        format_func=label,
    )
    feed = json.loads((ROOT / "input/data/feed/example_Midwest_feed.json").read_text())
    records = [
        dict(id=item["feed_type"], price=item["purchased_feed_cost"], daily_purchase=item["runtime_purchase_allowance"])
        for item in feed["feeds"]
        if item["feed_type"] not in (301, 302)
    ]
    records.extend(dict(id=i, price=p, daily_purchase=1000.0) for i, p in ((1, 1.4), (167, 2.8), (231, 5.0)))
    st.caption(
        "Preços em unidades monetárias do cenário por kg MS. São demonstrativos. Estoques, colheitas e compras são geridos pelo FeedManager."
    )
    adults = [row["id"] for row in records if row["id"] not in (202, 216)]
    selected = st.multiselect("Ingredientes disponíveis para categorias adultas", adults, default=adults)
    edited = st.data_editor(
        pd.DataFrame(records),
        hide_index=True,
        disabled=["id"],
        key="annual_economics",
        column_config={
            "id": "ID RuFaS",
            "price": st.column_config.NumberColumn("Preço (UM/kg MS)", min_value=0.0),
            "daily_purchase": st.column_config.NumberColumn("Compra diária máxima (kg MS/rebanho)", min_value=0.0),
        },
    )
    if st.button("Iniciar simulação dinâmica", type="primary"):
        if not selected:
            st.error("Selecione ingredientes para as categorias adultas.")
        else:
            overrides = {
                str(row["id"]): dict(purchased_feed_cost=row["price"], runtime_purchase_allowance=row["daily_purchase"])
                for row in edited.to_dict("records")
            }
            jobs = launch_runs(strategies, days, cows, seed, interval, fallback, overrides, selected)
            st.session_state.setdefault("annual_jobs", []).extend(jobs)
    show_jobs()


@st.fragment(run_every="3s")
def show_jobs():
    jobs = st.session_state.get("annual_jobs", []) + st.session_state.get("annual_evidence_jobs", [])
    summaries = []
    groups = {}
    for job in jobs:
        path = Path(job["path"])
        progress = path / "progress.json"
        status = (
            read_json(progress) if progress.exists() else dict(completed_days=0, requested_days=job["requested_days"])
        )
        completed, requested = status["completed_days"], status["requested_days"]
        archived = job.get("source") == "evidence"
        st.write(f"{label(job['strategy'])} · {'evidência arquivada' if archived else 'nova simulação'}")
        st.caption(
            f"Resultados carregados de evidências — não é nova simulação. {job['group_id'].removeprefix('evidence:')}"
            if archived
            else f"Nova execução · {path.parent.name[:8]}"
        )
        st.progress(min(completed / requested, 1.0), text=f"{completed}/{requested} dias efetivamente simulados")
        summary_file = path / "summary.json"
        if summary_file.exists():
            summary = read_json(summary_file)
            if summary["status"] == "complete":
                summaries.append(
                    summary | {"execution_origin": "Evidências arquivadas" if archived else "Nova simulação"}
                )
                group = job.get("group_id", "new:" + str(path.parent))
                groups.setdefault(group, {})[job["strategy"]] = summary
                st.success(
                    f"Evidência carregada: {summary['simulated_days']} dias já calculados."
                    if archived
                    else f"Simulação concluída em {summary['simulated_days']} dias."
                )
            else:
                st.error(summary.get("error", "Simulação interrompida."))
        elif not archived and job["process"].poll() is not None:
            st.error("Processo encerrado antes da conclusão. Consulte o log no diretório desta execução.")
        daily = path / "daily.jsonl"
        if (
            daily.exists()
            and completed
            and st.checkbox(
                "Carregar séries diárias e detalhes desta execução",
                key="details-" + str(path),
                value=False,
                help="Lê o diário somente quando solicitado; o cache é invalidado quando o arquivo muda.",
            )
        ):
            records = read_daily(daily, completed)
            frame = pd.DataFrame(
                [
                    dict(
                        day=r["day"],
                        cost=r["estimated_diet_cost"],
                        milk=r["milk_kg"],
                        dry_matter=sum(r["fed_kg_dm"].values()),
                        inventory=sum(r["inventory_kg_dm"].values()),
                        approved_pens=sum(bool(p["approved"]) for p in r["pens"] if p["category"] != "calf"),
                        rejected_pens=sum(not bool(p["approved"]) for p in r["pens"] if p["category"] != "calf"),
                        calf_not_approved=sum(not bool(p["approved"]) for p in r["pens"] if p["category"] == "calf"),
                    )
                    for r in records
                ]
            ).set_index("day")
            frame["accumulated_cost"] = frame["cost"].cumsum()
            frame.index.name = "Dia"
            with st.expander("Consultar séries diárias e dia específico"):
                st.caption(
                    "A série de aprovação considera currais adultos. Os registros de bezerros permanecem no JSON, sob o fluxo nativo próprio."
                )
                st.line_chart(frame[["cost", "accumulated_cost"]].rename(columns=COLUMNS))
                st.line_chart(frame[["milk", "dry_matter"]].rename(columns=COLUMNS))
                st.line_chart(frame[["inventory"]].rename(columns=COLUMNS))
                st.line_chart(frame[["approved_pens", "rejected_pens"]].rename(columns=COLUMNS))
                st.caption(
                    "Bezerros: registros nativos separados; os indicadores comuns de novilhas não certificam adequação da dieta de leite e concentrado inicial."
                )
                st.line_chart(frame[["calf_not_approved"]].rename(columns=COLUMNS))
                ingredients = pd.DataFrame([r["fed_kg_dm"] for r in records]).fillna(0)
                st.area_chart(ingredients)
                day = st.number_input(
                    "Dia a consultar (índice inicial 0)",
                    min_value=0,
                    max_value=completed - 1,
                    value=completed - 1,
                    key="day-" + str(path),
                )
                st.caption("JSON técnico original para auditoria; nomes internos e precisão preservados.")
                st.json(records[day], expanded=1)
                mineral_rows = []
                for row in records:
                    for pen in row["pens"]:
                        if pen["category"] == "calf":
                            continue
                        mineral_rows.append(
                            dict(
                                day=row["day"],
                                category=pen["category"],
                                pen=pen["pen_id"],
                                calcium_required_g=pen["requirements"]["calcium"],
                                calcium_absorbed_g=pen["supply"]["calcium"],
                                phosphorus_required_g=max(
                                    pen["requirements"]["phosphorus"], pen["requirements"]["process_based_phosphorus"]
                                ),
                                phosphorus_absorbed_g=pen["supply"]["phosphorus"],
                                native_approved=pen["approved"],
                                **pen.get("minerals", {}),
                            )
                        )
                st.caption(
                    "Minerais por dia e categoria: requisitos absorvíveis separados dos tetos totais; déficits nos deltas nativos do JSON."
                )
                if mineral_rows:
                    st.dataframe(display_table(pd.DataFrame(mineral_rows)), hide_index=True)
                convergence = [
                    dict(
                        day=row["day"],
                        category=e.get("category"),
                        used=e["used"],
                        success=e["success"],
                        reason=e.get("reason"),
                        termination=e.get("termination"),
                        converged=e.get("converged"),
                        iterations=len(e["trace"]),
                    )
                    for row in records
                    for e in row["formulations"]
                ]
                st.caption("Formulações e convergência; histórico completo das iterações no JSON do dia selecionado.")
                st.dataframe(display_table(pd.DataFrame(convergence)), hide_index=True)
                st.download_button(
                    "Baixar resumo diário CSV",
                    frame.rename(columns=COLUMNS).to_csv(),
                    "serie_anual.csv",
                    "text/csv",
                    key="download-" + str(path),
                )
    if summaries:
        st.subheader("Indicadores das execuções concluídas")
        st.dataframe(display_table(pd.DataFrame(summaries)), hide_index=True)
        for group, complete in groups.items():
            for alternative in ("linear_highs_all", "linear_highs_exclusive", "linear_highs"):
                if "native_slsqp" in complete and alternative in complete:
                    st.subheader(f"Comparação econômica · {label(alternative)}")
                    st.caption(
                        ("Evidências carregadas · " + group.removeprefix("evidence:"))
                        if group.startswith("evidence:")
                        else "Novas simulações do mesmo conjunto de entradas"
                    )
                    economic_cards(
                        complete["native_slsqp"]["estimated_diet_cost"],
                        complete[alternative]["estimated_diet_cost"],
                        alternative,
                    )
