"""A-E demonstration with an actual Animal constructor and native ration consumer."""

from contextlib import contextmanager
from datetime import datetime
import argparse
import json
from pathlib import Path
import numpy as np

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.ration.linear_diet_adapter import ingredient_from_feed
from RUFAS.biophysical.animal.ration.linear_diet_example import example_feeds
from RUFAS.biophysical.animal.ration.linear_diet_integration import optimize_animal_ration
from RUFAS.data_structures.feed_storage_to_animal_connection import NutrientStandard
from RUFAS.rufas_time import RufasTime

ROOT = Path(__file__).resolve().parents[4]


@contextmanager
def demo_inputs(*, animal_id: int | None = None, milk_kg_day: float = 30.0):
    """Controlled standalone setup; restore native class settings and RNG on exit.

    Population provides physiological state; milk_kg_day is an explicit scenario
    assumption with a 30 kg/day default. Wood means initialize the
    actual constructor but the curve is not used to predict milk in this demo.
    """
    population = json.loads((ROOT / "input/data/animal/animal_population.json").read_text())
    candidates = [a for a in population["cows"] if a["animal_type"] == "LacCow" and a["breed"] == "HO"]
    if animal_id is None:
        record = min(candidates, key=lambda a: (abs(a["days_in_milk"] - 100), a["id"]))
    else:
        record = next((a for a in candidates if a["id"] == animal_id), None)
    if record is None:
        raise ValueError("Animal indisponível: selecione uma vaca Holandesa em lactação (NRC).")
    curves = json.loads((ROOT / "input/data/animal/lactation_curve_adjustment_inputs.json").read_text())
    attrs = [
        (LactationCurve, "_parity_to_parameter_mapping"),
        (LactationCurve, "_parity_to_std_dev_mapping"),
        (AnimalConfig, "simulate_genetics"),
        (MilkProduction, "fat_percent"),
        (MilkProduction, "true_protein_percent"),
        (MilkProduction, "lactose_percent"),
    ]
    sentinel = object()
    saved = [(cls, name, getattr(cls, name, sentinel)) for cls, name in attrs]
    rng = np.random.get_state()
    try:
        np.random.seed(42)
        AnimalConfig.simulate_genetics = False
        means = curves["parameter_mean_values"]
        LactationCurve._parity_to_parameter_mapping = {
            p: {k: means["parameter_" + k + "_mean"] for k in ("l", "m", "n")} for p in (1, 2, 3)
        }
        LactationCurve._parity_to_std_dev_mapping = {
            int(k): v for k, v in curves["parameter_standard_deviations"].items()
        }
        MilkProduction.set_milk_quality(3.8, 3.2, 4.8)
        animal = Animal(record.copy(), RufasTime(datetime(2026, 1, 1), datetime(2026, 1, 2)))
        animal.nutrient_standard = NutrientStandard.NRC
        animal.milk_production._milk_production_variance = 0.0
        animal.milk_production.daily_milk_produced = milk_kg_day
        feeds = example_feeds()
        settings = {1: ("Alfafa", 1.3), 44: ("Milho", 2.0), 167: ("Farelo de soja", 1.8)}
        metadata = {
            f.rufas_id: dict(
                name=settings[f.rufas_id][0],
                nel_mcal_per_kg_dm=settings[f.rufas_id][1],
                nel_source="Illustrative fixed NEL",
                feed_source="NRC_comp.csv composition; illustrative prices/stocks/inclusion",
            )
            for f in feeds
        }
        thresholds = dict(
            cp_min_kg=3.6,
            nel_min_mcal=35.0,
            ndf_min_fraction=0.28,
            ndf_max_fraction=0.4,
            supplemental_source="External illustrative PB/NEL/FDN; no full nutritional certification",
        )
        yield animal, feeds, metadata, thresholds
    finally:
        np.random.set_state(rng)
        for cls, name, value in saved:
            if value is sentinel:
                delattr(cls, name)
            else:
                setattr(cls, name, value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auto", action="store_true", help="Skip the Enter pause before solving")
    args = parser.parse_args()
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    with demo_inputs() as (animal, feeds, metadata, thresholds):
        print("PO-RUFAS | INTEGRACAO REAL RUFAS -> SOLVER -> RATIONMANAGER (7 dias)")
        print(
            f"1. Animal RuFaS: id={animal.id} | raca={animal.breed.name} | "
            f"peso={animal.body_weight:.2f} kg | DEL={animal.days_in_milk} | paridade={animal.calves}"
        )
        print("   Origem: animal_population.json (construtor Animal); leite=30 kg/dia (3,8/3,2/4,8%) = hipoteses.")
        native = animal.calculate_nutrition_requirements("Barn", 0.0, 20.0, feeds)
        print(
            f"2. Exigencias NRC: DMI={native.dry_matter:.4f} kg/dia (importada no LP) | "
            f"Diagnostico: MP={native.metabolizable_protein:.1f} g, NEl_lac={native.lactation_energy:.2f} Mcal, "
            f"Ca={native.calcium:.2f} g, P={native.phosphorus:.2f} g"
        )
        print("   Metas externas (LP): PB >= 3,6 kg/dia | NEL >= 35,0 Mcal/dia | FDN 28-40% MS")
        ingredients = [ingredient_from_feed(feed, **metadata[feed.rufas_id]) for feed in feeds]
        print("3. Lista Python (NRCFeed -> Ingredient): ID | Nome | R$/kg MN | Estoque MN | Max MN/dia")
        for ing in ingredients:
            print(
                f"   {ing.identifier:<3} | {ing.name:<15} | {ing.price_per_kg:8.4f} | "
                f"{ing.stock_kg:10.2f} | {ing.maximum_kg_day:10.2f}"
            )
        if not args.auto:
            input("Sophia: pressione ENTER para executar HiGHS e enviar a dieta ao RationManager... ")
        report = optimize_animal_ration(animal, feeds, metadata, thresholds, period_days=7)
        res = report["result"]
        if report["native_return"] is None or res["status"] != "optimal":
            raise RuntimeError("Demo failed; no ration returned to RuFaS")
        print(
            f"4. Solver (linprog/HiGHS): status={res['status']} | "
            f"{len(res['checks'])}/{len(res['checks'])} verificacoes OK"
        )
        print("   ID  | Ingrediente     | kg MN/dia | kg MS/dia |    R$/dia")
        for feed in feeds:
            fid = feed.rufas_id
            name = metadata[fid]["name"]
            print(
                f"   {fid:<3} | {name:<15} | {res['quantities_kg_day'][fid]:9.4f} | "
                f"{res['ration_kg_dm_day'][fid]:9.4f} | {res['costs_per_day'][fid]:9.4f}"
            )
        totals = res["totals"]
        ndf_pct = 100.0 * totals["NDF_kg"] / totals["DM_kg"]
        print(
            f"5. Custo otimizado: R$ {res['cost_per_day']:.4f}/dia | "
            f"MS={totals['DM_kg']:.4f} kg | PB={totals['CP_kg']:.4f} kg | "
            f"NEL={totals['NEL_Mcal']:.2f} Mcal | FDN={totals['NDF_kg']:.4f} kg ({ndf_pct:.2f}% MS)"
        )
        pct_str = ", ".join(
            f"ID {item['feed_type']}: {item['ration_percentage']:.2f}%"
            for item in report["native_return"]["config"]["rations"][0]["feeds"]
        )
        print(f"6. Conversao RuFaS (% MS, soma=100%): {pct_str}")
        recovered = report["native_return"]["ration_kg_dm_day"]
        rec_str = ", ".join(f"ID {k}: {v:.4f}" for k, v in recovered.items())
        sup = report["native_return"]["supply_kg"]
        ev = report["native_return"]["native_evaluation"]
        print(f"7. RationManager recuperou (kg MS/dia): {rec_str}")
        print(
            f"   NutritionSupplyCalculator: PB={sup['CP']:.4f} kg, FDN={sup['NDF']:.4f} kg | "
            f"NutritionEvaluator P_delta={ev['deltas']['phosphorus']:.2f} g/dia (sem mineral no LP)"
        )
        print("   Limite: integracao ate interface nativa comprovada; ciclo diario da fazenda nao executado.")
        target = ROOT / "output/integracao_real.json"
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
