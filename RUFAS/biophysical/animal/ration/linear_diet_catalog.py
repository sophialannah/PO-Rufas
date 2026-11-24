"""Audit the full RuFaS catalog and run a reproducible fixed-coefficient LP.

Run with --demo for explicitly synthetic economics/NEL, or --parameters CSV.
Neither mode certifies nutritional suitability for feeding a real animal.
"""

import argparse
import csv
from dataclasses import asdict, fields
import json
from pathlib import Path
import random
from typing import Any

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.nrc_requirements_calculator import NRCRequirementsCalculator
from RUFAS.biophysical.animal.ration.linear_diet import AnimalProfile, Ingredient, optimize_diet
from RUFAS.biophysical.animal.ration.linear_diet_adapter import ingredient_from_feed, requirements_from_rufas
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed, FeedCategorization, FeedComponentType
from RUFAS.units import MeasurementUnits

ROOT = Path(__file__).resolve().parents[4]
PARAMETER_FIELDS = [
    "identifier",
    "name",
    "price_brl_per_kg_dm",
    "stock_kg_dm",
    "minimum_kg_dm_day",
    "maximum_kg_dm_day",
    "nel_mcal_per_kg_dm",
    "source",
]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _exclusion(row: dict[str, str] | None) -> str:
    if row is None:
        return "No composition in NRC or NASEM library"
    if not 0 < float(row["DM"]) <= 100:
        return "Invalid dry matter percentage"
    if row["feed_type"] not in {"Forage", "Conc", "Mineral"}:
        return "Feed type outside this adult lactating-cow scenario: " + row["feed_type"]
    return ""


def catalog_candidates() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """NRC takes precedence; NASEM supplies IDs absent from NRC, never a mixture within a feed."""
    directory = ROOT / "input/data/feed"
    composition: dict[int, dict[str, str]] = {}
    sources: dict[int, str] = {}
    for filename in ("NASEM_Comp_with_TDN.csv", "NRC_comp.csv"):
        for row in _read_csv(directory / filename):
            key = int(row["rufas_id"])
            composition[key], sources[key] = row, "input/data/feed/" + filename
    candidates, audit = [], []
    for item in _read_csv(directory / "user_feeds.csv"):
        key = int(item["rufas_id"])
        selected_row = composition.get(key)
        reason = _exclusion(selected_row)
        record = {
            "identifier": key,
            "name": item["Name"] + " - " + item["feed_description"],
            "composition_source": sources.get(key),
            "reason": reason,
            "status": "excluded" if reason else "candidate",
        }
        audit.append(record)
        if not reason:
            candidates.append({**record, "composition": selected_row})
    return candidates, audit


def demo_parameters(candidates: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    """Synthetic scenario assumptions, NOT nutrient equations or market quotations."""
    settings = {"Forage": (0.9, 1.8, 1.4, 14.0), "Conc": (1.5, 3.0, 1.9, 8.0), "Mineral": (3.0, 7.0, 0.0, 0.15)}
    result = []
    for item in candidates:
        rng = random.Random(seed + item["identifier"])
        low, high, nel, maximum = settings[item["composition"]["feed_type"]]
        result.append(
            dict(
                identifier=item["identifier"],
                name=item["name"],
                price_brl_per_kg_dm=round(rng.uniform(low, high), 4),
                stock_kg_dm=round(rng.uniform(5, 10) * maximum, 4),
                minimum_kg_dm_day=0.0,
                maximum_kg_dm_day=maximum,
                nel_mcal_per_kg_dm=nel,
                source=f"SYNTHETIC DEMO seed={seed}: arbitrary category prices/NEL/stock/bounds",
            )
        )
    return result


def make_ingredients(candidates: list[dict[str, Any]], parameters: list[dict[str, Any]]) -> list[Ingredient]:
    """Require explicit supplemental values for every candidate; do not silently drop missing prices."""
    by_id = {int(row["identifier"]): row for row in parameters}
    expected = {item["identifier"] for item in candidates}
    if len(by_id) != len(parameters) or set(by_id) != expected:
        raise ValueError("Parameter CSV must contain exactly one row for every candidate ID")
    ingredients = []
    for item in candidates:
        row, data = item["composition"], by_id[item["identifier"]]
        source = str(data["source"]).strip()
        if not source:
            raise ValueError("Parameter provenance is required")
        values: dict[str, Any] = {
            f.name: float(row[f.name])
            for f in fields(Feed)
            if f.name in row
            and f.name not in {"rufas_id", "Fd_Category", "feed_type", "units", "is_fat", "is_wetforage"}
        }
        values.update(
            rufas_id=item["identifier"],
            Fd_Category=FeedCategorization(row["Fd_Category"]),
            feed_type=FeedComponentType(row["feed_type"]),
            units=MeasurementUnits(row["units"]),
            is_fat=row["is_fat"].upper() == "TRUE",
            is_wetforage=row["is_wetforage"].upper() == "TRUE",
            purchase_cost=float(data["price_brl_per_kg_dm"]),
            on_farm_cost=0.0,
            buffer=0.0,
            amount_available=float(data["stock_kg_dm"]),
            lower_limit=float(data["minimum_kg_dm_day"]),
            limit=float(data["maximum_kg_dm_day"]),
        )
        ingredient = ingredient_from_feed(
            Feed(**values),
            name=item["name"],
            nel_mcal_per_kg_dm=float(data["nel_mcal_per_kg_dm"]),
            nel_source=source,
            feed_source=item["composition_source"],
        )
        for name in ("price_per_kg", "stock_kg", "minimum_kg_day", "maximum_kg_day"):
            ingredient.sources[name] = source
        ingredient.sources["name"] = "input/data/feed/user_feeds.csv"
        ingredients.append(ingredient)
    return ingredients


def random_cow(
    seed: int, cp_min: float | None = None, nel_min: float | None = None
) -> tuple[AnimalProfile, dict[str, Any]]:
    rng = random.Random(seed)
    inputs: dict[str, Any] = dict(
        body_weight=float(rng.randint(580, 700)),
        mature_body_weight=720.0,
        day_of_pregnancy=None,
        body_condition_score_5=3.0,
        days_in_milk=rng.randint(80, 200),
        average_daily_gain_heifer=0.0,
        animal_type=AnimalType.LAC_COW,
        parity=2,
        calving_interval=365,
        milk_fat=round(rng.uniform(3.5, 4.2), 2),
        milk_true_protein=round(rng.uniform(3.0, 3.5), 2),
        milk_lactose=4.8,
        milk_production=float(rng.randint(25, 35)),
        housing="Barn",
        distance=0.0,
        previous_temperature=20.0,
        net_energy_diet_concentration=1.6,
        days_born=1500,
        TDN_percentage=0.65,  # Native implementation consumes a fraction despite the argument name.
        process_based_phosphorus_requirement=0.0,
    )
    req = NRCRequirementsCalculator.calculate_requirements(**inputs)
    limits = requirements_from_rufas(
        req,
        cp_min_kg=cp_min if cp_min is not None else 0.16 * req.dry_matter,
        nel_min_mcal=nel_min if nel_min is not None else 1.55 * req.dry_matter,
        ndf_min_fraction=0.28,
        ndf_max_fraction=0.40,
        supplemental_source="Scenario thresholds, NOT calculated animal requirements: "
        "default CP=16% DM, NEL=1.55 Mcal/kg DM; optional user CP/NEL overrides; NDF=28-40% DM",
    )
    cow = AnimalProfile(
        inputs["body_weight"],
        inputs["days_in_milk"],
        inputs["milk_production"],
        inputs["milk_fat"],
        inputs["milk_true_protein"],
        limits,
        f"Synthetic random cow seed={seed}; only DMI is imported from RuFaS NRC",
    )
    return cow, {**inputs, "animal_type": "LAC_COW"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Use explicitly synthetic prices, stocks and NEL")
    mode.add_argument("--parameters", type=Path, help="CSV with explicit prices, stock, bounds, NEL and provenance")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cp-min", type=float)
    parser.add_argument("--nel-min", type=float)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output/catalog_diet")
    args = parser.parse_args()
    candidates, audit = catalog_candidates()
    parameters = demo_parameters(candidates, args.seed) if args.demo else _read_csv(args.parameters)
    ingredients = make_ingredients(candidates, parameters)
    cow, calculator_inputs = random_cow(args.seed, args.cp_min, args.nel_min)
    result = optimize_diet(cow, ingredients, period_days=7)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "parameters.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=PARAMETER_FIELDS)
        writer.writeheader()
        writer.writerows(parameters)
    report = dict(
        mode="synthetic_demo" if args.demo else "supplied_parameters",
        seed=args.seed,
        currency="BRL",
        period_days=7,
        catalog_audit=audit,
        animal=asdict(cow),
        calculator_inputs=calculator_inputs,
        ingredients=[asdict(i) for i in ingredients],
        result=asdict(result),
    )
    (args.output_dir / "result.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Cenario de PL: metas suplementares nao validam exigencias nutricionais completas.")
    print("Precos/estoques/NEL:", "SIMULADOS" if args.demo else "arquivo informado")
    excluded_count = len(audit) - len(ingredients)
    print(f"Catalogo avaliado: {len(audit)}; candidatos: {len(ingredients)}; excluidos: {excluded_count}")
    print(f"Vaca: {cow.body_weight_kg} kg; DEL {cow.days_in_milk}; leite {cow.milk_kg_day} kg/dia")
    print("Status:", result.status, result.message)
    if result.status != "optimal":
        raise SystemExit(1)
    print("ID | alimento | kg MN/dia | kg MS/dia | R$/dia")
    for ingredient in ingredients:
        key = ingredient.identifier
        if result.quantities_kg_day[key] > 1e-7:
            print(
                f"{key} | {ingredient.name} | {result.quantities_kg_day[key]:.4f} | "
                f"{result.ration_kg_dm_day[key]:.4f} | {result.costs_per_day[key]:.4f}"
            )
    print(f"Custo minimo do cenario: R$ {result.cost_per_day:.4f}/dia")
    print("Totais:", result.totals)
    print(f"Restricoes atendidas: {sum(c.satisfied for c in result.checks)}/{len(result.checks)}")
    print("Arquivos:", args.output_dir)


if __name__ == "__main__":
    main()
