"""Compact live demonstration using the existing RuFaS example and optimizer.

Run: python -m apresentacao.demo_solver [--auto]
No nutritional equations or optimization logic are duplicated here.
"""

import argparse
from dataclasses import asdict
from datetime import datetime
import json
from math import isclose
from pathlib import Path
import sys
from time import perf_counter
from zoneinfo import ZoneInfo

from RUFAS.biophysical.animal.ration.linear_diet import optimize_diet
from RUFAS.biophysical.animal.ration.linear_diet_example import example_inputs

HERE = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auto", action="store_true", help="Skip the Enter prompt for validation/rehearsal")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    started = perf_counter()
    animal, ingredients = example_inputs()
    req = animal.requirements
    print("PO-RUFAS | DEMONSTRAÇÃO REAL DO SOLVER | 1 vaca, dieta diária por 7 dias")
    print("Composição: biblioteca RuFaS. Preços, estoques, NEL e metas PB/FDN: ilustrativos.")
    print(f"Vaca: {animal.body_weight_kg:.0f} kg | DEL {animal.days_in_milk} | leite {animal.milk_kg_day:.0f} kg/dia")
    print(f"Leite: gordura {animal.milk_fat_percent:.1f}% | proteína verdadeira {animal.milk_protein_percent:.1f}%")
    print("MN = matéria natural; MS = matéria seca; PB = proteína bruta; FDN = fibra.")
    print("ENTRADAS                 R$/kg MN  Estoque kg MN  Máx. kg MN/dia")
    for ingredient in ingredients:
        print(
            f"{ingredient.name:24} {ingredient.price_per_kg:8.4f}  {ingredient.stock_kg:13.4f}"
            f"  {ingredient.maximum_kg_day:14.4f}"
        )
    print(f"MS = {req.dm_min_kg:.4f} kg/dia (RuFaS/NRC); PB >= {req.cp_min_kg:.1f} kg/dia;")
    print(f"NEL >= {req.nel_min_mcal:.1f} Mcal/dia; FDN = 28–40% da MS; inclusões mínimas = zero.")
    if not args.auto:
        input("Sophia: pressione ENTER para executar linprog/HiGHS agora... ")
    solving = perf_counter()
    result = optimize_diet(animal, ingredients, period_days=7)
    solver_seconds = perf_counter() - solving
    if result.status != "optimal":
        print(f"SEM SOLUÇÃO ÓTIMA: {result.status} — {result.message}")
        raise SystemExit(1)
    recalculated_cost = sum(i.price_per_kg * result.quantities_kg_day[i.identifier] for i in ingredients)
    if not isclose(recalculated_cost, result.cost_per_day, abs_tol=1e-9, rel_tol=0):
        raise RuntimeError("Independent cost check failed")
    if not all(c.satisfied for c in result.checks):
        raise RuntimeError("Independent feasibility checks failed")
    print("\nRESULTADO CALCULADO AGORA: optimal | scipy.optimize.linprog(method='highs')")
    print("Ingrediente                kg MN/dia   kg MS/dia      R$/dia")
    for ingredient in ingredients:
        key = ingredient.identifier
        print(
            f"{ingredient.name:25} {result.quantities_kg_day[key]:10.4f}"
            f" {result.ration_kg_dm_day[key]:11.4f} {result.costs_per_day[key]:11.4f}"
        )
    print(f"CUSTO MÍNIMO DO CENÁRIO: R$ {result.cost_per_day:.4f}/dia")
    t = result.totals
    print(f"MS {t['DM_kg']:.4f} kg | PB {t['CP_kg']:.4f} kg | NEL {t['NEL_Mcal']:.4f} Mcal")
    print(f"FDN {t['NDF_kg']:.4f} kg = {100 * t['NDF_kg'] / t['DM_kg']:.2f}% da MS")
    print(f"{len(result.checks)}/{len(result.checks)} verificações OK: nutrientes, inclusão e estoques.")
    print(f"Custo reconferido por soma preço × quantidade. Chamada do solver: {solver_seconds:.3f} s.")
    print("Ótimo deste modelo demonstrativo; não é validação nutricional completa.")
    report = dict(
        executed_at=datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(),
        animal=asdict(animal),
        ingredients=[asdict(i) for i in ingredients],
        period_days=7,
        currency="BRL",
        result=asdict(result),
        independent_cost=recalculated_cost,
        solver_seconds=solver_seconds,
        elapsed_seconds_including_prompt=perf_counter() - started,
    )
    output = HERE / "evidencias/demo_resultado.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Registro completo: apresentacao/evidencias/demo_resultado.json")


if __name__ == "__main__":
    main()
