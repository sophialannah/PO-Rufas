"""Apresentação e exportação dos resultados do modelo integrado."""

import pandas as pd
import streamlit as st

from frontend.service import export_json

NUTRIENTS = {
    "total_energy": ("Energia total", "Mcal/dia"),
    "maintenance_energy": ("Energia de mantença", "Mcal/dia"),
    "lactation_energy": ("Energia de lactação", "Mcal/dia"),
    "growth_energy": ("Energia de crescimento", "Mcal/dia"),
    "pregnancy_energy": ("Energia de gestação", "Mcal/dia"),
    "activity_energy": ("Energia de atividade", "Mcal/dia"),
    "metabolizable_protein": ("Proteína metabolizável", "g/dia"),
    "calcium": ("Cálcio absorvível", "g/dia"),
    "phosphorus": ("Fósforo absorvível", "g/dia"),
    "dry_matter": ("Matéria seca", "kg/dia"),
    "ndf_percent": ("FDN", "p.p. de MS"),
    "forage_ndf_percent": ("FDN de forragem", "p.p. de MS"),
    "fat_percent": ("Gordura", "p.p. de MS"),
}

CHECKS = {
    "absorbed_phosphorus_g": "Fósforo absorvível (g/dia)",
    "absorbed_calcium_g": "Cálcio absorvível (g/dia)",
    "DM_kg": "Matéria seca (kg MS/dia)",
    "CP_kg": "Proteína bruta (kg/dia)",
    "NEL_Mcal": "Energia líquida (Mcal/dia)",
    "NDF_min_kg_residual": "FDN mínima (resíduo em kg/dia)",
    "NDF_max_kg_residual": "FDN máxima (resíduo em kg/dia)",
}


def decimal(value: float, places: int = 4) -> str:
    return f"{value:,.{places}f}".translate(str.maketrans(",.", ".,"))


def money(value: float | None, places: int = 4) -> str:
    return "—" if value is None else f"R$ {decimal(value, places)}"


def native_status(report: dict) -> str:
    native = report["native_return"]
    if native is None:
        return "Não avaliada"
    return "Aprovada" if native["native_evaluation"]["is_valid_cow_ration"] else "Não aprovada"


def requirements_table(requirements: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Exigência NRC": name, "Valor": requirements[key], "Unidade": unit}
            for key, (name, unit) in NUTRIENTS.items()
            if key in requirements and requirements[key] is not None
        ]
    )


def diet_table(report: dict) -> pd.DataFrame:
    result, native = report["result"], report["native_return"]
    if native is None:
        return pd.DataFrame()
    share = {item["feed_type"]: item["ration_percentage"] for item in native["config"]["rations"][0]["feeds"]}
    return pd.DataFrame(
        [
            {
                "ID RuFaS": identifier,
                "Ingrediente": item["name"],
                "kg MN/dia": result["quantities_kg_day"][identifier],
                "kg MS/dia": result["ration_kg_dm_day"][identifier],
                "Participação (% MS)": share[identifier],
                "R$/dia": result["costs_per_day"][identifier],
            }
            for item in report["ingredients"]
            for identifier in [item["identifier"]]
            if result["quantities_kg_day"][identifier] > 0
        ]
    )


def evaluation(report: dict) -> None:
    native = report["native_return"]
    st.subheader("Avaliação nutricional nativa")
    status = f"{native_status(report)} pelo NutritionEvaluator nos critérios avaliados."
    if native_status(report) == "Aprovada":
        st.success(status)
    else:
        st.error(status)
    ev = native["native_evaluation"]
    criteria = ev.get("criteria", {})
    if criteria.get("fat_percent", ev["deltas"]["fat_percent"] >= 0) is False:
        st.warning(f"Gordura acima do limite em **{abs(ev['deltas']['fat_percent']):.3g} p.p. de MS**.")
    for key, value in ev["deltas"].items():
        if value is None or abs(value) < 1e-8:
            continue
        name, unit = NUTRIENTS[key]
        if key in {"ndf_percent", "dry_matter", "metabolizable_protein"}:
            condition = "acima" if value > 0 else "abaixo"
            st.warning(f"{name} {condition} da faixa nativa em {decimal(abs(value), 2)} {unit}.")
        elif value < 0 and key != "fat_percent":
            st.warning(f"Déficit de {name.lower()} de **{decimal(abs(value), 2)} {unit}** pelo critério do RuFaS.")
    st.caption(
        "O RationManager recuperou as quantidades em kg MS/dia. A oferta foi calculada com FeedInRation e NutritionSupplyCalculator."
    )
    with st.expander("Conferir oferta, critérios avaliados e retorno do RationManager"):
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Critério avaliado": NUTRIENTS[key][0],
                        "Delta nativo": value,
                        "Unidade": NUTRIENTS[key][1],
                        "Atendido": criteria.get(key),
                    }
                    for key, value in ev["deltas"].items()
                ]
            ),
            hide_index=True,
        )
        st.json(native, expanded=1)


def show_minerals(report: dict) -> None:
    minerals = report["nrc_minerals"]
    native = report["native_return"]
    evaluation = native["native_evaluation"] if native else None
    st.subheader("Balanço mineral · NRC 2001")
    st.caption(
        "Mínimos de fósforo e cálcio absorvíveis "
        + ("ativos no LP." if minerals["enabled"] else "desativados no LP.")
        + " O NutritionSupplyCalculator estima a oferta por categoria de ingrediente."
    )
    st.markdown("[Referência da exigência NRC 2001, capítulo 6 — Minerals](https://doi.org/10.17226/9825)")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Mineral": name,
                    "Exigência absorvida (g/dia)": minerals["requirement_g_day"][key],
                    "Oferta absorvível (g/dia)": evaluation["supply_summary"][key + "_g"] if evaluation else None,
                    "Diferença (g/dia)": evaluation["deltas"][key] if evaluation else None,
                }
                for key, name in (("phosphorus", "Fósforo"), ("calcium", "Cálcio"))
            ]
        ),
        hide_index=True,
    )
    if native:
        st.caption(f"Fósforo total ingerido · {decimal(minerals['phosphorus_total_g_day'], 2)} g/dia")
    if diagnostic := report.get("nasem_phosphorus_diagnostic"):
        st.markdown(
            f"**Diagnóstico NASEM 2021** · Exigência de P absorvido **{decimal(diagnostic['requirement_g_day'], 2)} g/dia** "
            f"com consumo estimado de **{decimal(diagnostic['dmi_kg_day'], 2)} kg MS/dia**. "
            f"[NASEM 2021, capítulo 7 — Minerals]({diagnostic['source']})"
        )
        st.caption("Diagnóstico restrito à exigência. O balanço de oferta e o parecer acima usam o padrão NRC.")


def show_results(report: dict | None) -> None:
    st.header("Resultados")
    if report is None:
        st.info("Execute uma otimização para gerar a dieta e o parecer nutricional.")
        return
    result, days = report["result"], report["period_days"]
    st.caption(
        f"Cenário {report['scenario_id']} · Animal {report['animal_id']} · {days} dias · {report['nutrient_standard']}"
    )
    cost = result["cost_per_day"]
    st.download_button(
        "Baixar resultado completo (JSON)",
        export_json(report),
        f"dieta-{report['scenario_id']}.json",
        "application/json",
    )
    if result["status"] != "optimal":
        if result["status"] == "infeasible":
            st.error("Cenário inviável. Confira estoque para o período, limites de inclusão e metas nutricionais.")
            diagnostic = {
                "phosphorus_conflict": "O cenário voltou a ser viável ao retirar somente o mínimo de fósforo absorvível.",
                "calcium_conflict": "O mínimo de cálcio absorvível já torna o cenário inviável mesmo sem o mínimo de fósforo.",
                "mineral_conflict": "O cenário ficou viável sem os mínimos minerais, mas o conflito individual não pôde ser isolado.",
            }.get(report["nrc_minerals"]["infeasibility"])
            if diagnostic:
                st.warning(diagnostic)
        else:
            st.error("O solver não entregou uma solução ótima.")
        st.caption(f"HiGHS · {result['status']} · {result['message']}")
        show_minerals(report)
        return

    checks = result["checks"]
    passed = sum(check["satisfied"] for check in checks)
    a, b, c = st.columns(3)
    a.metric("Custo mínimo diário", money(cost))
    b.metric(f"Custo estimado · {days} dias", money(cost * days, 2))
    c.metric("Restrições do LP", f"{passed}/{len(checks)} · {result['status']}")
    evaluation(report)
    show_minerals(report)
    st.subheader("Dieta otimizada")
    diet = diet_table(report)
    st.dataframe(diet, hide_index=True)
    left, right = st.columns(2)
    left.bar_chart(diet, x="Ingrediente", y="Participação (% MS)", color="#0B7668", horizontal=True)
    right.bar_chart(diet, x="Ingrediente", y="R$/dia", color="#3A6292", horizontal=True)
    st.download_button("Baixar dieta (CSV)", diet.to_csv(index=False).encode("utf-8-sig"), "dieta.csv", "text/csv")
    summary = (
        f"# Cenário {report['scenario_id']}\n\nAnimal {report['animal_id']} · {days} dias\n\n"
        f"Custo {money(cost)}/dia · LP {result['status']} · {passed}/{len(checks)} verificações\n\n"
        f"Avaliação RuFaS — {native_status(report)}\n\n"
        + "\n".join(
            f"- {NUTRIENTS[key][0]} · delta {decimal(value, 2)} {NUTRIENTS[key][1]}"
            for key, value in report["native_return"]["native_evaluation"]["deltas"].items()
            if value is not None
        )
        + "\n\n"
        + "\n".join(f"- {item}" for item in report["limitations"])
    )
    st.download_button("Baixar resumo (Markdown)", summary, "resumo-dieta.md", "text/markdown")
    with st.expander("Composição nutricional e restrições", expanded=True):
        totals = result["totals"]
        st.dataframe(
            pd.DataFrame(
                [
                    {"Total do LP": label, "Valor": totals[key]}
                    for key, label in (
                        ("DM_kg", "Matéria seca (kg/dia)"),
                        ("CP_kg", "PB (kg/dia)"),
                        ("NEL_Mcal", "NEL (Mcal/dia)"),
                        ("NDF_kg", "FDN (kg/dia)"),
                    )
                ]
            ),
            hide_index=True,
        )
        rows = []
        for check in checks:
            name = check["name"]
            if name not in CHECKS:
                kind, identifier, *_ = name.split("_")
                name = f"ID {identifier} · " + (
                    "estoque (kg MN/período)" if kind == "stock" else "inclusão (kg MN/dia)"
                )
            else:
                name = CHECKS[name]
            rows.append(
                dict(
                    Restrição=name,
                    Calculado=check["supplied"],
                    Mínimo=check["lower"],
                    Máximo=check["upper"],
                    Folga=check["slack"],
                    Atendida=check["satisfied"],
                )
            )
        st.dataframe(pd.DataFrame(rows), hide_index=True)
    with st.expander("Origem dos dados e limitações"):
        st.table(requirements_table(report["requirements"]))
        st.json(report["assumptions"])
        st.json(report["profile"]["requirements"])
        st.json({item["name"]: item["sources"] for item in report["ingredients"]}, expanded=False)
        for item in report["limitations"]:
            st.markdown(f"- {item}")
