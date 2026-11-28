"""Derive auditable comparisons from corrected journals; preserve historical evidence."""

from collections import Counter
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path("evidencias/correcao_dinamica")
RUNS = {
    "SLSQP_MTL": "nativo_final_365",
    "HiGHS_hibrido": "hibrido_final_365",
    "HiGHS_exclusivo": "exclusivo_estoque_365",
}


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    summaries, series, pen_rows, failures, convergence = [], {}, [], [], []
    states, physical = {}, {}
    for name, folder in RUNS.items():
        path = ROOT / folder
        summary = json.loads((path / "summary.json").read_text())
        assert summary["status"] == "complete" and summary["simulated_days"] == 365
        rows = [json.loads(line) for line in (path / "daily.jsonl").read_text(encoding="utf-8").splitlines()]
        assert [r["day"] for r in rows] == list(range(365))
        summaries.append(dict(model=name, **summary))
        states[name] = dict(
            initial=json.loads((path / "initial_state.json").read_text()), animals=[r["animals"] for r in rows]
        )
        series[name] = pd.DataFrame(
            [
                dict(
                    day=r["day"],
                    cost=r["estimated_diet_cost"],
                    milk=r["milk_kg"],
                    dry_matter=sum(r["fed_kg_dm"].values()),
                    inventory=sum(r["inventory_kg_dm"].values()),
                )
                for r in rows
            ]
        ).set_index("day")
        series[name]["accumulated_cost"] = series[name]["cost"].cumsum()
        series[name].to_csv(ROOT / f"serie_{name}.csv")
        differences = []
        for row in rows:
            requested = Counter()
            for pen in row["pens"]:
                for key, value in pen["ration"].items():
                    if key.isdigit():
                        requested[key] += value * pen["population"]
            for key, value in requested.items():
                delta = row["fed_kg_dm"].get(key, 0) - value
                if abs(delta) > 1e-8:
                    differences.append(
                        dict(day=row["day"], feed=key, requested=value, fed=row["fed_kg_dm"].get(key, 0), delta=delta)
                    )
        physical[name] = dict(
            minimum_recorded_stock=min(v for r in rows for v in r["inventory_kg_dm"].values()),
            maximum_ration_vs_fulfilled_difference_kg=max([abs(d["delta"]) for d in differences] or [0]),
            differences=differences,
        )
        for r in rows:
            for p in r["pens"]:
                if p["category"] == "calf":
                    continue
                minerals = p["minerals"]
                pen_rows.append(
                    dict(
                        model=name,
                        day=r["day"],
                        pen=p["pen_id"],
                        category=p["category"],
                        approved=p["approved"],
                        **minerals,
                        calcium_absorbed_g=p["supply"]["calcium"],
                        calcium_required_g=p["requirements"]["calcium"],
                        phosphorus_absorbed_g=p["supply"]["phosphorus"],
                        phosphorus_required_g=max(
                            p["requirements"]["phosphorus"], p["requirements"]["process_based_phosphorus"]
                        ),
                    )
                )
                for field, value in p["evaluation"].items():
                    if value is None:
                        continue
                    clamped = field in {"metabolizable_protein", "ndf_percent", "dry_matter"}
                    unacceptable = value != 0 if clamped else value < (-1e-9 if field == "fat_percent" else 0)
                    if unacceptable:
                        failures.append(
                            dict(
                                model=name,
                                day=r["day"],
                                pen=p["pen_id"],
                                category=p["category"],
                                nutrient=field,
                                delta=value,
                                classification=(
                                    "numerical_deviation"
                                    if abs(value) <= 1e-3
                                    else ("excess" if clamped and value > 0 or field == "fat_percent" else "deficiency")
                                ),
                            )
                        )
                for field in ("calcium", "phosphorus"):
                    excess = minerals[f"{field}_total_g"] - minerals[f"{field}_upper_g"]
                    if excess > 1e-6:
                        failures.append(
                            dict(
                                model=name,
                                day=r["day"],
                                pen=p["pen_id"],
                                category=p["category"],
                                nutrient=field + "_total_upper",
                                delta=excess,
                                classification="total_mineral_excess_not_native_evaluator",
                            )
                        )
            for e in r["formulations"]:
                convergence.append(
                    dict(
                        model=name,
                        day=r["day"],
                        pen=e["pen_id"],
                        category=e["category"],
                        used=e["used"],
                        success=e["success"],
                        reason=e["reason"],
                        termination=e.get("termination"),
                        converged=e.get("converged"),
                        iterations=len(e["trace"]),
                    )
                )
    pd.DataFrame(summaries).to_csv(ROOT / "comparacao_anual.csv", index=False)
    pd.DataFrame(pen_rows).to_csv(ROOT / "minerais_por_curral_dia.csv", index=False)
    pd.DataFrame(failures).to_csv(ROOT / "reprovacoes_detalhadas.csv", index=False)
    pd.DataFrame(convergence).to_csv(ROOT / "convergencia_por_categoria.csv", index=False)
    nutritional = {}
    for name in RUNS:
        pens = [p for p in pen_rows if p["model"] == name]
        events = [e for e in convergence if e["model"] == name]
        nutritional[name] = dict(
            approved_adult_pen_days=sum(p["approved"] for p in pens),
            rejected_adult_pen_days=sum(not p["approved"] for p in pens),
            minerals_tolerable_pen_days=sum(p["tolerable"] for p in pens),
            failure_classification=dict(Counter(f["classification"] for f in failures if f["model"] == name)),
            failure_nutrients=dict(Counter(f["nutrient"] for f in failures if f["model"] == name)),
            categories={
                category: dict(
                    attempts=len(group := [e for e in events if e["category"] == category]),
                    accepted=sum(e["success"] for e in group),
                    converged=sum(bool(e["converged"]) for e in group),
                )
                for category in sorted({e["category"] for e in events})
            },
        )
    baseline = summaries[0]["estimated_diet_cost"]
    report = dict(
        initial_states_equal=all(s["initial"] == states["SLSQP_MTL"]["initial"] for s in states.values()),
        recorded_biological_states_equal=all(s["animals"] == states["SLSQP_MTL"]["animals"] for s in states.values()),
        reduction_percent={s["model"]: 100 * (baseline - s["estimated_diet_cost"]) / baseline for s in summaries},
        nutrition=nutritional,
        numerical_classification="Operational audit threshold 1e-3 in each field's native unit; no approvals or constraints altered. Not a biological threshold.",
    )
    write_json(ROOT / "auditoria_resultados.json", report)
    write_json(ROOT / "auditoria_fisica.json", physical)
    for column in ("cost", "accumulated_cost", "milk", "dry_matter", "inventory"):
        fig, ax = plt.subplots(figsize=(9, 4))
        for name, frame in series.items():
            ax.plot(frame.index + 1, frame[column], label=name)
        ax.set(
            xlabel="Dia",
            ylabel={
                "cost": "Custo diário (UM)",
                "accumulated_cost": "Custo acumulado (UM)",
                "milk": "Leite (kg/dia)",
                "dry_matter": "Consumo (kg MS/dia)",
                "inventory": "Estoque (kg MS)",
            }[column],
        )
        ax.legend()
        fig.tight_layout()
        fig.savefig(ROOT / f"{column}.png", dpi=150)
        plt.close(fig)
    sources = [
        "RUFAS/biophysical/animal/ration/dynamic_linear_optimizer.py",
        "RUFAS/biophysical/animal/ration/mineral_limits.py",
        "RUFAS/biophysical/feed_storage/feed_manager.py",
        "experiments/annual.py",
        "tests/test_dynamic_convergence.py",
        "frontend/annual.py",
        "RUFAS/biophysical/animal/herd_manager.py",
        "RUFAS/input/metadata/properties/default.json",
        "experiments/first_day_regression.py",
        "experiments/recover_licenses.py",
        "experiments/convergence_report.py",
        "tests/fixtures/dynamic_first_day.json",
        "COPYING.txt",
        "COPYING.LESSER.txt",
    ]
    write_json(
        ROOT / "hashes_implementacao.json", {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sources}
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
