"""Read-only evidence loading and presentation; never reruns the annual backend."""

from itertools import islice
import json
from pathlib import Path

import streamlit as st

from frontend.results import decimal
from frontend.usability import economic_comparison, label

GROUPS = {
    "Comparação controlada validada — NRC, 365 dias": [
        "evidencias/correcao_dinamica/nativo_final_365",
        "evidencias/correcao_dinamica/hibrido_final_365",
        "evidencias/correcao_dinamica/exclusivo_estoque_365",
    ],
    "Histórico anterior à correção — 365 dias": [
        "evidencias/anual/confirmacao/native_slsqp_365",
        "evidencias/anual/confirmacao/linear_highs_365",
    ],
}


@st.cache_data(show_spinner=False, max_entries=24)
def _json_snapshot(path, modified_ns, size):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_json(path):
    path = Path(path)
    stat = path.stat()
    return _json_snapshot(str(path), stat.st_mtime_ns, stat.st_size)


@st.cache_data(show_spinner=False, max_entries=8)
def _daily_snapshot(path, modified_ns, size, completed):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in islice(stream, completed)]


def read_daily(path, completed):
    path = Path(path)
    stat = path.stat()
    return _daily_snapshot(str(path), stat.st_mtime_ns, stat.st_size, completed)


def evidence_jobs(root, group):
    jobs = []
    for folder in GROUPS[group]:
        path = Path(root) / folder
        summary = read_json(path / "summary.json")
        if summary["status"] != "complete" or summary["simulated_days"] != 365 or not (path / "daily.jsonl").is_file():
            raise ValueError("Evidência anual incompleta: " + folder)
        jobs.append(
            dict(
                path=str(path),
                strategy=summary["strategy"],
                requested_days=365,
                source="evidence",
                group_id="evidence:" + group,
            )
        )
    return jobs


def history_panel(root):
    with st.expander("Resultados anuais já calculados", expanded=False):
        st.caption("Carregamento somente de leitura das evidências. Não inicia uma nova simulação.")
        group = st.selectbox("Conjunto de resultados arquivados", list(GROUPS))
        if st.button("Carregar resultados anuais das evidências"):
            try:
                st.session_state["annual_evidence_jobs"] = evidence_jobs(root, group)
            except (OSError, ValueError, KeyError) as error:
                st.error(f"Não foi possível carregar as evidências: {error}")


def economic_cards(original, alternative, strategy, currency="UM"):
    result = economic_comparison(original, alternative)
    a, b = st.columns(2)
    a.metric("Custo alimentar do RuFaS original", f"{decimal(original, 8)} {currency}")
    b.metric("Custo alimentar do PO-RuFaS", f"{decimal(alternative, 8)} {currency}")
    a, b, c = st.columns(3)
    a.metric("Diferença absoluta", f"{decimal(result['absolute_difference'], 8)} {currency}")
    b.metric(
        "Diferença percentual",
        "Não definida (base zero)" if result["percent"] is None else f"{decimal(result['percent'], 7)}%",
    )
    winner = {"original": "RuFaS original", "po": label(strategy), "tie": "Mesmo custo"}[result["winner"]]
    c.metric("Estratégia mais econômica", winner)
    st.caption(
        "Percentual = 100 × (RuFaS − PO-RuFaS) / RuFaS; positivo favorece PO-RuFaS, negativo favorece RuFaS. "
        "Diferença absoluta é a magnitude. Preços demonstrativos; não implica superioridade universal."
    )
