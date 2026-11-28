"""Display labels and UI-only state helpers; no changes to nutrient calculations."""

import json
from math import isfinite
from pathlib import Path

from frontend.service import INPUTS

LABELS = {
    "native_slsqp": "RuFaS original",
    "linear_highs_all": "PO-RuFaS híbrido",
    "linear_highs_exclusive": "PO-RuFaS exclusivo",
    "linear_highs": "PO-RuFaS (lactação)",
    "static_highs": "PO-RuFaS estático",
    "A_HiGHS": "PO-RuFaS — mesmo LP (HiGHS)",
    "A_SLSQP": "Mesmo LP (SLSQP)",
    "B_SLSQP_native": "RuFaS original — formulação nativa",
    "growing": "Recria",
    "close_up": "Secas e pré-parto",
    "lac_cow": "Vacas em lactação",
    "calf": "Bezerros",
    "growing and close_up": "Recria e pré-parto",
    "Forage": "Forragem",
    "Conc": "Concentrado",
    "Mineral": "Mineral",
    "complete": "Concluída",
    "failed": "Falhou",
    "optimal": "Ótimo do LP",
    "infeasible": "Inviável",
    "native_slsqp_mineral": "RuFaS original controlado",
    "fail": "Interromper sem fallback",
    "unsupported_category_or_standard": "Categoria ou padrão não suportado",
    "highs_failure_or_native_rejection": "Falha do HiGHS ou reprovação nativa",
    "objective_and_original_feasibility_converged": "Objetivo estabilizado e viabilidade verificada",
    "trust_region_stalled": "Região de confiança estagnada",
    "iteration_limit": "Limite de iterações",
    "linearized_problem_infeasible": "Aproximação local inviável",
    "Optimization terminated successfully": "Otimização concluída",
    "git_worktree": "Cópia de trabalho Git",
    "exported_source_without_git": "Fonte exportada sem metadados Git",
    "git_unavailable": "Git indisponível",
    "NRC 2005 doi:10.17226/11309; total dietary minerals, not absorbed requirements": "NRC 2005 (10.17226/11309): minerais totais, distintos das exigências absorvíveis",
}
COLUMNS = {
    "id": "ID RuFaS",
    "day": "Dia",
    "date": "Data",
    "strategy": "Estratégia",
    "estimated_diet_cost": "Custo alimentar estimado",
    "milk_kg": "Produção de leite (kg)",
    "elapsed_seconds": "Tempo de execução (s)",
    "days": "Dias solicitados",
    "simulated_days": "Dias simulados",
    "cows_initial": "Meta inicial de vacas",
    "seed": "Semente",
    "status": "Situação",
    "animal_days": "Animal-dias",
    "cost_per_animal_day": "Custo por animal-dia",
    "cost_per_kg_milk": "Custo por kg de leite",
    "purchase_expense": "Despesa de compras",
    "highs_attempts": "Tentativas HiGHS",
    "highs_accepted": "Formulações HiGHS aceitas",
    "native_attempts": "Chamadas SLSQP",
    "unsupported_native": "Categorias encaminhadas ao nativo",
    "fallbacks": "Fallbacks",
    "commit": "Revisão Git",
    "dirty": "Alterações locais",
    "source": "Origem",
    "execution_origin": "Origem da execução",
    "category": "Categoria",
    "pen": "Curral",
    "used": "Método utilizado",
    "success": "Aceita pelo solver",
    "reason": "Motivo",
    "termination": "Encerramento",
    "converged": "Convergiu",
    "iterations": "Iterações",
    "cost": "Custo alimentar (UM/dia)",
    "accumulated_cost": "Custo acumulado (UM)",
    "milk": "Leite (kg/dia)",
    "dry_matter": "Consumo (kg MS/dia)",
    "inventory": "Estoque (kg MS)",
    "approved_pens": "Currais adultos aprovados",
    "rejected_pens": "Currais adultos reprovados",
    "calf_not_approved": "Registros de bezerros não aprovados",
    "calcium_required_g": "Ca absorvível requerido (g)",
    "calcium_absorbed_g": "Ca absorvível fornecido (g)",
    "phosphorus_required_g": "P absorvível requerido (g)",
    "phosphorus_absorbed_g": "P absorvível fornecido (g)",
    "native_approved": "Aprovação nativa",
    "dry_matter_kg": "Matéria seca (kg)",
    "calcium_total_g": "Cálcio total (g)",
    "phosphorus_total_g": "Fósforo total (g)",
    "calcium_percent_dm": "Cálcio (% MS)",
    "phosphorus_percent_dm": "Fósforo (% MS)",
    "calcium_upper_g": "Teto de cálcio total (g)",
    "phosphorus_upper_g": "Teto de fósforo total (g)",
    "calcium_to_phosphorus": "Relação Ca:P",
    "tolerable": "Dentro dos tetos minerais",
}


def label(value):
    return LABELS.get(value, value)


def display_table(frame):
    result = frame.copy()
    for key in ("strategy", "category", "used", "reason", "termination", "status", "source"):
        if key in result:
            result[key] = result[key].map(lambda value: label(value) if isinstance(value, str) else value)
    return result.rename(columns={c: COLUMNS.get(c, c.replace("_", " ").capitalize()) for c in result.columns})


def original_parameters(item):
    """Only copy fields present in NRC; never infer NEL from DE or fabricate economics."""
    composition = item["composition"]
    dm = float(composition["DM"]) / 100
    values = {key: None for key in INPUTS}
    for key, column in (("minimum", "lower_limit"), ("maximum", "limit")):
        if composition.get(column) not in (None, ""):
            values[key] = float(composition[column]) / dm
    return values


def validated_demo(root):
    path = Path(root) / "evidencias/comparacao/configuracao.json"
    rows = json.loads(path.read_text(encoding="utf-8"))["rows"]
    assert {int(r["id"]) for r in rows} == {1, 44, 167, 231}
    return {int(r["id"]): {key: r[key] for key in INPUTS} for r in rows}


def preserve_editor_values(state):
    """Commit outstanding editor deltas using the OLD row IDs before selection changes."""
    base = state.get("ingredient_editor_base")
    if not base:
        return
    ids, rows = base
    edits = state.setdefault("ingredient_values", {})
    pending = state.get("editor-" + ",".join(map(str, ids)), {}).get("edited_rows", {})
    for index, changes in pending.items():
        identifier = ids[int(index)]
        rows[identifier].update({k: v for k, v in changes.items() if k in INPUTS})
    edits.update({i: rows[i].copy() for i in ids})


def missing_parameters(rows):
    return [
        dict(Ingrediente=row["Ingrediente"], Campo=INPUTS[key])
        for row in rows
        for key in INPUTS
        if row.get(key) is None or not isfinite(float(row[key]))
    ]


def economic_comparison(original, alternative):
    costs = [float(original), float(alternative)]
    if any(not isfinite(v) or v < 0 for v in costs):
        raise ValueError("A comparação exige custos finitos e não negativos.")
    difference = costs[0] - costs[1]
    return dict(
        difference=difference,
        absolute_difference=abs(difference),
        percent=100 * difference / costs[0] if costs[0] else None,
        winner="original" if difference < 0 else "po" if difference > 0 else "tie",
    )
