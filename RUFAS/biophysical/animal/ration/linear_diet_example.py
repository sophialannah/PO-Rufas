"""Run from repository root: python -m RUFAS.biophysical.animal.ration.linear_diet_example."""

import csv
from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.nrc_requirements_calculator import NRCRequirementsCalculator
from RUFAS.biophysical.animal.ration.linear_diet import AnimalProfile, Ingredient, optimize_diet
from RUFAS.biophysical.animal.ration.linear_diet_adapter import ingredient_from_feed, requirements_from_rufas
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    NRCFeed,
    FeedCategorization,
    FeedComponentType,
)
from RUFAS.units import MeasurementUnits


def example_feeds() -> list[NRCFeed]:
    """Real NRC library composition; illustrative prices, allocated stocks and bounds."""
    path = Path(__file__).resolve().parents[4] / "input/data/feed/NRC_comp.csv"
    # ID: (price/tonne DM in BRL, stock kg DM, maximum kg DM/day).
    scenario = {1: (1400.0, 150.0, 16.0), 44: (1800.0, 100.0, 10.0), 167: (2800.0, 60.0, 6.0)}
    feeds = []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            identifier = int(row["rufas_id"])
            if identifier not in scenario:
                continue
            values: dict[str, Any] = {
                key: float(value)
                for key, value in row.items()
                if key not in {"rufas_id", "Fd_Category", "feed_type", "units", "is_fat", "is_wetforage"}
            }
            price, stock, maximum = scenario[identifier]
            values.update(
                rufas_id=identifier,
                Fd_Category=FeedCategorization(row["Fd_Category"]),
                feed_type=FeedComponentType(row["feed_type"]),
                units=MeasurementUnits(row["units"]),
                is_fat=row["is_fat"].upper() == "TRUE",
                is_wetforage=row["is_wetforage"].upper() == "TRUE",
                purchase_cost=Ingredient.price_from_tonne(price),
                on_farm_cost=0.0,
                amount_available=stock,
                buffer=0.0,
                limit=maximum,
                lower_limit=0.0,
            )
            feeds.append(NRCFeed(**values))
    if len(feeds) != len(scenario):
        raise ValueError("Example feed IDs missing from NRC library")
    return feeds


def example_calculator_inputs() -> dict[str, Any]:
    """Explicit synthetic animal and prior-diet inputs; TDN uses a fraction."""
    return dict(
        body_weight=650.0,
        mature_body_weight=700.0,
        day_of_pregnancy=None,
        body_condition_score_5=3.0,
        days_in_milk=100,
        average_daily_gain_heifer=0.0,
        animal_type=AnimalType.LAC_COW,
        parity=2,
        calving_interval=365,
        milk_fat=3.8,
        milk_true_protein=3.2,
        milk_lactose=4.8,
        milk_production=30.0,
        housing="Barn",
        distance=0.0,
        previous_temperature=20.0,
        net_energy_diet_concentration=1.6,
        days_born=1500,
        TDN_percentage=0.65,  # Native implementation consumes a fraction despite the argument name.
        process_based_phosphorus_requirement=0.0,
    )


def example_inputs() -> tuple[AnimalProfile, list[Ingredient]]:
    """Use the real RuFaS NRC calculator for DMI; other LP thresholds are illustrative."""
    rufas_requirements = NRCRequirementsCalculator.calculate_requirements(**example_calculator_inputs())
    req = requirements_from_rufas(
        rufas_requirements,
        cp_min_kg=3.6,
        nel_min_mcal=35.0,
        ndf_min_fraction=0.28,
        ndf_max_fraction=0.40,
        supplemental_source="Illustrative academic scenario; not NRC/NASEM dietary recommendations",
    )
    animal = AnimalProfile(650.0, 100, 30.0, 3.8, 3.2, req, "Illustrative animal; DMI computed by RuFaS NRC calculator")
    settings = {1: ("Alfafa (farinha)", 1.3), 44: ("Milho (moagem media)", 2.0), 167: ("Farelo de soja", 1.8)}
    ingredients = []
    for feed in example_feeds():
        name, nel = settings[feed.rufas_id]
        ingredient = ingredient_from_feed(
            feed,
            name=name,
            nel_mcal_per_kg_dm=nel,
            nel_source="Illustrative fixed NEL, Mcal/kg DM",
            feed_source=f"input/data/feed/NRC_comp.csv; rufas_id={feed.rufas_id}",
        )
        for parameter in ("name", "price_per_kg", "stock_kg", "minimum_kg_day", "maximum_kg_day"):
            ingredient.sources[parameter] = "Illustrative scenario in linear_diet_example.py; currency BRL"
        ingredients.append(ingredient)
    return animal, ingredients


def main() -> None:
    animal, ingredients = example_inputs()
    result = optimize_diet(animal, ingredients, period_days=7)
    print("Exemplo academico: composicao RuFaS; precos, estoques, NEL e limites suplementares ilustrativos.")
    print(f"Resultado: {result.status} | {result.message}")
    if result.status != "optimal":
        raise SystemExit(1)
    print("Ingrediente                 | kg MN/dia | kg MS/dia | R$/dia")
    for ingredient in ingredients:
        identifier = ingredient.identifier
        print(
            f"{ingredient.name:27} | {result.quantities_kg_day[identifier]:9.4f} | "
            f"{result.ration_kg_dm_day[identifier]:9.4f} | {result.costs_per_day[identifier]:7.4f}"
        )
    print(f"Custo total: R$ {result.cost_per_day:.4f}/dia")
    print(f"Totais: {result.totals}")
    for check in result.checks:
        print(
            f"{check.name}: fornecido={check.supplied:.6f}; min={check.lower}; max={check.upper}; "
            f"folga={check.slack:.6f}; {'OK' if check.satisfied else 'FALHOU'}"
        )
    output = Path("output/linear_diet_example.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "animal": asdict(animal),
                "ingredients": [asdict(i) for i in ingredients],
                "period_days": 7,
                "currency": "BRL",
                "result": asdict(result),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Entrada e resultado completos: {output}")


if __name__ == "__main__":
    main()
