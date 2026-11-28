"""Compare identical linear programs and distinct native NRC formulations."""

from copy import deepcopy
from dataclasses import asdict
from importlib.metadata import version
import json
from pathlib import Path
from platform import python_version
from statistics import median
from time import perf_counter

import numpy as np
from scipy.optimize import linprog, minimize
from experiments.provenance import git_context

from frontend.service import (
    _NATIVE_LOCK,
    build_feeds,
    default_inputs,
    load_animals,
    load_catalog,
    run_scenario,
)
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.nutrients.nutrition_evaluator import NutritionEvaluator
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.ration.linear_diet import _Row, _check, _inequalities, _nutrient_rows
from RUFAS.biophysical.animal.ration.linear_diet_adapter import profile_from_animal, requirements_from_rufas
from RUFAS.biophysical.animal.ration.linear_diet_integrated_example import demo_inputs
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.data_structures.feed_storage_to_animal_connection import NutrientStandard

TOLERANCE = 1e-7


def _evaluate(animal, feeds, amounts):
    class NRCComparisonSupply(NutritionSupplyCalculator):
        nutrient_standard = NutrientStandard.NRC

    native = animal.calculate_nutrition_requirements("Barn", 0.0, 20.0, feeds)
    supply = NRCComparisonSupply.calculate_nutrient_supply(
        feeds_used=feeds,
        ration_formulation=amounts,
        body_weight=animal.body_weight,
        enteric_methane=0.0,
        urinary_nitrogen=0.0,
    )
    valid, evaluation = NutritionEvaluator.evaluate_nutrition_supply(native, supply, is_cow=True)
    return dict(
        requirements=asdict(native),
        supply=asdict(supply),
        deltas=asdict(evaluation),
        approved=bool(valid),
        criteria={key: bool(value) if value is not None else None for key, value in evaluation.report.items()},
    )


def _measure(solve, repeats):
    solve()  # Warm-up is excluded for every method.
    samples, runs, result = [], [], None
    for _ in range(repeats):
        start = perf_counter()
        result = solve()
        samples.append(perf_counter() - start)
        candidate = result[0] if isinstance(result, tuple) else result
        runs.append(
            dict(
                success=bool(candidate.success),
                message=str(candidate.message),
                iterations=int(candidate.nit),
                objective=float(candidate.fun),
                x=candidate.x.tolist(),
            )
        )
    return result, dict(
        samples_seconds=samples,
        median_seconds=median(samples),
        min_seconds=min(samples),
        max_seconds=max(samples),
        repeats=repeats,
        runs=runs,
    )


def compare_models(
    animal_id,
    rows,
    milk=30.0,
    days=7,
    cp=3.6,
    nel=35.0,
    ndf_min=28.0,
    ndf_max=40.0,
    minerals=True,
    diagnostic=False,
    *,
    repeats=5,
):
    """Run both experiments on the same input snapshot. Timings cover solver calls."""
    if not isinstance(repeats, int) or isinstance(repeats, bool) or repeats < 2:
        raise ValueError("Informe pelo menos duas repetições.")
    animals, catalog = load_animals(), load_catalog()
    reference = run_scenario(
        animals, catalog, animal_id, rows, milk, days, cp, nel, ndf_min, ndf_max, minerals, diagnostic
    )
    feeds, _ = build_feeds(catalog, rows)
    if reference["result"]["status"] != "optimal":
        raise ValueError("O cenário de referência precisa de solução ótima para esta comparação.")
    with _NATIVE_LOCK, demo_inputs(animal_id=animal_id, milk_kg_day=milk) as (animal, *_):
        native = animal.calculate_nutrition_requirements("Barn", 0.0, 20.0, feeds)
        req = requirements_from_rufas(
            native,
            cp_min_kg=cp,
            nel_min_mcal=nel,
            ndf_min_fraction=ndf_min / 100,
            ndf_max_fraction=ndf_max / 100,
            supplemental_source="Comparison scenario",
        )
        ingredients = reference["ingredients"]
        # Reuse the operational backend builder for the original nutrient rows.
        from RUFAS.biophysical.animal.ration.linear_diet import Ingredient

        objects = [Ingredient(**item) for item in ingredients]
        profile = profile_from_animal(animal, req)
        lp_rows = _nutrient_rows(objects, profile.requirements)
        for mineral, target in reference["nrc_minerals"]["lp_minimum_g_day"].items():
            coeff = reference["nrc_minerals"]["coefficients_g_per_kg_dm"][mineral]
            lp_rows.append(
                _Row(
                    f"absorbed_{mineral}_g",
                    np.array([item.dm_fraction * coeff[item.identifier] for item in objects]),
                    lower=target,
                )
            )
        bounds = [
            (
                item.minimum_kg_day,
                min(item.stock_kg / days, item.maximum_kg_day if item.maximum_kg_day is not None else np.inf),
            )
            for item in objects
        ]
        checks = list(lp_rows)
        for i, item in enumerate(objects):
            unit = np.eye(len(objects))[i]
            checks.extend(
                [
                    _Row(f"inclusion_{item.identifier}_kg_day", unit, item.minimum_kg_day, item.maximum_kg_day),
                    _Row(f"stock_{item.identifier}_kg", unit * days, 0.0, item.stock_kg),
                ]
            )
        costs = np.array([item.price_per_kg for item in objects])
        aub, bub = _inequalities(lp_rows)
        equality = [r for r in lp_rows if r.lower is not None and r.lower == r.upper]
        inequality = [r for r in lp_rows if not (r.lower is not None and r.lower == r.upper)]
        # Avoid equality represented as two dependent inequalities in SLSQP.
        ia, ib = _inequalities(inequality)
        ea = np.array([r.coefficients for r in equality])
        eb = np.array([r.lower for r in equality])
        constraints = [dict(type="ineq", fun=lambda x: ib - ia @ x, jac=lambda x: -ia)]
        if equality:
            constraints.append(dict(type="eq", fun=lambda x: ea @ x - eb, jac=lambda x: ea))
        start_x = np.array([(low + high) / 2 for low, high in bounds])
        methods = {
            "A_HiGHS": lambda: linprog(costs, A_ub=aub, b_ub=bub, bounds=bounds, method="highs"),
            "A_SLSQP": lambda: minimize(
                lambda x: costs @ x,
                start_x.copy(),
                jac=lambda x: costs,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"ftol": 1e-9, "maxiter": 1000},
            ),
        }
        output = {}
        for name, solve in methods.items():
            result, timing = _measure(solve, repeats)
            evaluated = [asdict(_check(row, result.x, TOLERANCE)) for row in checks]
            amounts = {item.identifier: float(x * item.dm_fraction) for item, x in zip(objects, result.x)}
            finite = bool(np.all(np.isfinite(result.x)))
            output[name] = dict(
                success=bool(result.success),
                message=str(result.message),
                iterations=int(result.nit),
                cost_per_day=float(costs @ result.x),
                cost_per_kg_milk=float(costs @ result.x) / milk,
                quantities_kg_mn_day={item.identifier: float(x) for item, x in zip(objects, result.x)},
                quantities_kg_dm_day=amounts,
                checks=evaluated,
                feasible=finite and all(check["satisfied"] for check in evaluated),
                timing=timing,
                native=_evaluate(animal, feeds, amounts) if finite and all(x >= 0 for x in result.x) else None,
            )
            for run in timing["runs"]:
                run["checks"] = [asdict(_check(row, np.array(run["x"]), TOLERANCE)) for row in checks]
                run["native"] = _evaluate(
                    animal, feeds, {item.identifier: float(x * item.dm_fraction) for item, x in zip(objects, run["x"])}
                )
        native_feeds = deepcopy(feeds)
        for feed in native_feeds:
            feed.limit = min(feed.limit, feed.amount_available / days)
        optimizer = RationOptimizer()

        def solve_native():
            return optimizer.attempt_optimization(
                nutrient_standard=NutrientStandard.NRC,
                pen_average_body_weight=animal.body_weight,
                pen_average_enteric_methane=None,
                pen_average_urine_nitrogen=None,
                requirements=native,
                initial_dry_matter_requirement=native.dry_matter,
                initial_protein_requirement=native.metabolizable_protein,
                pen_available_feeds=native_feeds,
                animal_combination=AnimalCombination.LAC_COW,
            )

        (result, config), timing = _measure(solve_native, repeats)
        amounts = {feed.rufas_id: float(x) for feed, x in zip(config.feeds_used, result.x)}
        residuals = [
            dict(name=constraint["fun"].__name__, slack=float(constraint["fun"](result.x, config)))
            for constraint in optimizer._select_constraints(AnimalCombination.LAC_COW)
        ]
        for feed, value in zip(config.feeds_used, result.x):
            residuals.extend(
                [
                    dict(name=f"lower_{feed.rufas_id}", slack=float(value - feed.lower_limit)),
                    dict(name=f"upper_{feed.rufas_id}", slack=float(feed.limit - value)),
                ]
            )
        output["B_SLSQP_native"] = dict(
            success=bool(result.success),
            message=str(result.message),
            iterations=int(result.nit),
            cost_per_day=float(result.fun),
            cost_per_kg_milk=float(result.fun) / milk,
            quantities_kg_dm_day=amounts,
            quantities_kg_mn_day={f.rufas_id: amounts[f.rufas_id] / (f.DM / 100) for f in config.feeds_used},
            checks=[row | {"satisfied": row["slack"] >= -TOLERANCE} for row in residuals],
            feasible=bool(np.all(np.isfinite(result.x))) and all(r["slack"] >= -TOLERANCE for r in residuals),
            timing=timing,
            native=_evaluate(animal, native_feeds, amounts),
        )
        for run in timing["runs"]:
            vector = np.array(run["x"])
            run["constraint_residuals"] = [
                dict(name=c["fun"].__name__, slack=float(c["fun"](vector, config)))
                for c in optimizer._select_constraints(AnimalCombination.LAC_COW)
            ]
            run["native"] = _evaluate(
                animal, native_feeds, {feed.rufas_id: float(x) for feed, x in zip(config.feeds_used, run["x"])}
            )
    return dict(
        animal_id=animal_id,
        nutrient_standard="NRC 2001",
        milk_kg_day=milk,
        days=days,
        reference=reference,
        methods=output,
        equivalent_experiment_A=True,
        equivalent_experiment_B=False,
        controls=dict(
            initial_x_mn=start_x.tolist(),
            bounds_mn=bounds,
            A_ub=aub.tolist(),
            b_ub=bub.tolist(),
            objective=costs.tolist(),
            verification_tolerance=TOLERANCE,
            slsqp_A_ftol=1e-9,
            slsqp_A_maxiter=1000,
            native_options="RuFaS/SciPy defaults; initial vector built by RationOptimizer",
            native_dmi_constraint_fraction=config.dmi_constraint_fraction,
            native_dmi_requirement_boost=config.dmi_requirement_boost,
            native_initial_x_dm=optimizer._check_initial_bounds(
                optimizer._build_bounds(config), np.array(optimizer._build_initial_value(None, config), dtype=float)
            ).tolist(),
            timing_scope="One excluded warm-up, sequential repetitions, solver calls only; final candidate evaluated",
        ),
    )


def json_text(data):
    """Serialize NumPy scalars while retaining strict finite JSON."""
    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
        allow_nan=False,
        default=lambda x: x.item() if isinstance(x, np.generic) else str(x),
    )


def main():
    import argparse
    import pandas as pd
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="evidencias/comparacao")
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    target = Path(args.output)
    target.mkdir(parents=True, exist_ok=True)
    rows = [dict(id=i, **values) for i, values in default_inputs().items()]
    rows.append(dict(id=231, price=5.0, stock=1.0, minimum=0.0, maximum=0.10, nel=0.0))
    reports = [compare_models(i, rows, milk, repeats=args.repeats) for i, milk in ((98605, 30), (93785, 31))]
    metadata = dict(
        **git_context(),
        python=python_version(),
        dependencies={p: version(p) for p in ("numpy", "scipy", "pandas", "streamlit", "pytest")},
        command="python -m experiments.comparison --repeats " + str(args.repeats),
    )
    (target / "resultados.json").write_text(json_text(dict(metadata=metadata, scenarios=reports)), encoding="utf-8")
    (target / "configuracao.json").write_text(json_text(dict(rows=rows, metadata=metadata)), encoding="utf-8")
    summary = []
    for report in reports:
        for name, method in report["methods"].items():
            summary.append(
                dict(
                    animal=report["animal_id"],
                    method=name,
                    cost=method["cost_per_day"],
                    milk_cost=method["cost_per_kg_milk"],
                    dry_matter=sum(method["quantities_kg_dm_day"].values()),
                    feasible=method["feasible"],
                    approved=method["native"]["approved"],
                    median_seconds=method["timing"]["median_seconds"],
                    iterations=method["iterations"],
                )
            )
    frame = pd.DataFrame(summary)
    frame.to_csv(target / "resumo.csv", index=False)
    for column, title in (("cost", "Custo diário (R$)"), ("median_seconds", "Tempo mediano (s)")):
        ax = frame.pivot(index="animal", columns="method", values=column).plot.bar(rot=0, figsize=(9, 5))
        ax.set_ylabel(title)
        ax.set_xlabel("Animal")
        plt.tight_layout()
        plt.savefig(target / (column + ".png"), dpi=160)
        plt.close()
    quantities = []
    for report in reports:
        for name, method in report["methods"].items():
            quantities.extend(
                dict(animal=report["animal_id"], method=name, ingredient=i, kg_dm=value)
                for i, value in method["quantities_kg_dm_day"].items()
            )
    pd.DataFrame(quantities).to_csv(target / "ingredientes.csv", index=False)
    detail_checks, detail_times = [], []
    for report in reports:
        for name, method in report["methods"].items():
            detail_checks.extend(row | dict(animal=report["animal_id"], method=name) for row in method["checks"])
            detail_times.extend(
                dict(animal=report["animal_id"], method=name, repetition=i + 1, seconds=seconds)
                for i, seconds in enumerate(method["timing"]["samples_seconds"])
            )
    pd.DataFrame(detail_checks).to_csv(target / "restricoes.csv", index=False)
    pd.DataFrame(detail_times).to_csv(target / "tempos.csv", index=False)
    for report in reports:
        shares = pd.DataFrame({name: m["quantities_kg_dm_day"] for name, m in report["methods"].items()})
        shares = shares.div(shares.sum(axis=0), axis=1) * 100
        shares.plot.bar(rot=0, figsize=(9, 5), ylabel="Participação (% MS)")
        plt.tight_layout()
        plt.savefig(target / f"ingredientes_{report['animal_id']}.png", dpi=160)
        plt.close()
    nutrition = []
    for report in reports:
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        for axis, (key, unit) in zip(
            axes, (("phosphorus", "g/dia"), ("calcium", "g/dia"), ("metabolizable_protein", "g/dia"))
        ):
            values = {}
            for name, method in report["methods"].items():
                native = method["native"]
                required = native["requirements"][key]
                if key == "phosphorus":
                    required = max(required, native["requirements"]["process_based_phosphorus"])
                values[name] = [required, native["supply"][key]]
                nutrition.append(
                    dict(
                        animal=report["animal_id"],
                        method=name,
                        nutrient=key,
                        required=required,
                        supplied=native["supply"][key],
                        unit=unit,
                    )
                )
            pd.DataFrame(values, index=["Exigência", "Oferta"]).T.plot.bar(ax=axis, rot=30)
            axis.set_title(key)
            axis.set_ylabel(unit)
        fig.tight_layout()
        fig.savefig(target / f"nutricao_{report['animal_id']}.png", dpi=160)
        plt.close(fig)
    pd.DataFrame(nutrition).to_csv(target / "nutricao.csv", index=False)
    sensitivity = []
    animals, catalog = load_animals(), load_catalog()
    for animal, milk in ((98605, 30), (93785, 31)):
        for change in (-20, -10, 0, 10, 20):
            changed = [row | {"price": row["price"] * (1 + change / 100)} if row["id"] == 44 else row for row in rows]
            report = run_scenario(animals, catalog, animal, changed, milk, 7, 3.6, 35, 28, 40, True)
            sensitivity.append(dict(animal=animal, corn_price_change_percent=change, report=report))
    (target / "sensibilidade.json").write_text(json_text(sensitivity), encoding="utf-8")
    sf = pd.DataFrame(
        [
            dict(animal=r["animal"], change=r["corn_price_change_percent"], cost=r["report"]["result"]["cost_per_day"])
            for r in sensitivity
        ]
    )
    sf.to_csv(target / "sensibilidade.csv", index=False)
    sf.pivot(index="change", columns="animal", values="cost").plot(
        marker="o", ylabel="R$/dia", xlabel="Variação do preço do milho (%)", figsize=(8, 5)
    )
    plt.tight_layout()
    plt.savefig(target / "sensibilidade.png", dpi=160)
    plt.close()
    corn_quote = dict(
        ingredient="Milho disponível em Goiás",
        price=54.48,
        unit="R$/saca",
        observation_period="09–13/11/2026",
        publication_date="2026-11-17",
        source="IFAG, Programa Apoiar",
        url="https://apoiar.sistemafaeg.org.br/milho/%F0%9F%8C%BD-destaques-semanal-do-mercado-do-milho-em-goias-09-11-a-13-11-ifag/",
        conversion_assumption="Saca de 60 kg MN; composição do milho 44 usada como aproximação do produto comercial",
        brl_per_kg_mn=54.48 / 60,
        brl_per_kg_dm=(54.48 / 60) / 0.881,
        limitations="Indicador ao produtor; moagem, frete, impostos e margem de compra não incluídos. Demais preços demonstrativos.",
    )
    economic_rows = [row | {"price": corn_quote["brl_per_kg_mn"]} if row["id"] == 44 else row for row in rows]
    economics = dict(
        classification="Cenário híbrido exploratório: cotação apenas do milho; demais preços demonstrativos",
        quote=corn_quote,
        scenarios=[
            run_scenario(animals, catalog, i, economic_rows, milk, 7, 3.6, 35, 28, 40, True)
            for i, milk in ((98605, 30), (93785, 31))
        ],
    )
    (target / "economico_parcial.json").write_text(json_text(economics), encoding="utf-8")
    pd.DataFrame([corn_quote]).to_csv(target / "cotacoes.csv", index=False)
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
