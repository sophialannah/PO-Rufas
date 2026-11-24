"""Adaptador da aplicação local para o fluxo integrado do RuFaS."""

from dataclasses import asdict
from copy import copy
import json
from math import isfinite
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4

from RUFAS.biophysical.animal.ration.linear_diet_adapter import ingredient_from_feed
from RUFAS.biophysical.animal.ration.linear_diet_catalog import catalog_candidates
from RUFAS.biophysical.animal.ration.linear_diet_example import example_feeds
from RUFAS.biophysical.animal.ration.linear_diet_integrated_example import demo_inputs
from RUFAS.biophysical.animal.ration.linear_diet_integration import optimize_animal_ration
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    FeedCategorization,
    FeedComponentType,
    NRCFeed,
    NutrientStandard,
)
from RUFAS.units import MeasurementUnits

ROOT = Path(__file__).resolve().parents[1]
POPULATION = "input/data/animal/animal_population.json"
COMPOSITION = "input/data/feed/NRC_comp.csv"
NASEM_SOURCE = "https://www.ncbi.nlm.nih.gov/books/NBK600600/"
DEMO_ID = 98605
DEMO_FEEDS = {1: ("Alfafa", 1.3), 44: ("Milho", 2.0), 167: ("Farelo de soja", 1.8)}
INPUTS = {
    "price": "Preço (R$/kg MN)",
    "stock": "Estoque (kg MN/período)",
    "minimum": "Mínimo (kg MN/dia)",
    "maximum": "Máximo (kg MN/dia)",
    "nel": "NEL (Mcal/kg MS)",
}
ASSUMPTIONS = {
    "gordura_pct": 3.8,
    "proteina_verdadeira_pct": 3.2,
    "lactose_pct": 4.8,
    "alojamento": "Barn",
    "distancia_caminhada": 0.0,
    "temperatura_anterior_c": 20.0,
    "origem": "Hipóteses do cenário integrado RuFaS",
}
LIMITATIONS = [
    "Escopo de uma vaca Holandesa em lactação no padrão NRC.",
    "O LP usa consumo de MS calculado pelo RuFaS e metas externas de PB, NEL e FDN.",
    "Os dados econômicos e valores de NEL pré-preenchidos são ilustrativos.",
    "O parecer nativo se aplica aos critérios avaliados. A simulação da fazenda e a baixa de estoque estão fora do fluxo.",
]
# Protege as configurações temporárias das classes RuFaS e o RNG usado pelo construtor.
_NATIVE_LOCK = Lock()


def load_animals() -> dict[int, dict]:
    population = json.loads((ROOT / POPULATION).read_text(encoding="utf-8"))
    keys = ("id", "breed", "body_weight", "days_in_milk", "parity")
    return {
        row["id"]: {key: row[key] for key in keys}
        for row in population["cows"]
        if row["animal_type"] == "LacCow" and row["breed"] == "HO" and all(row.get(key) is not None for key in keys)
    }


def load_catalog() -> dict[int, dict]:
    candidates, _ = catalog_candidates()
    return {
        item["identifier"]: {
            **item,
            "name": DEMO_FEEDS.get(item["identifier"], (item["name"], None))[0],
        }
        for item in candidates
        if item["composition_source"] == COMPOSITION
    }


def default_inputs() -> dict[int, dict]:
    defaults = {}
    for feed in example_feeds():
        name, nel = DEMO_FEEDS[feed.rufas_id]
        ingredient = ingredient_from_feed(
            feed, name=name, nel_mcal_per_kg_dm=nel, nel_source="Hipótese da demonstração", feed_source=COMPOSITION
        )
        defaults[feed.rufas_id] = dict(
            price=ingredient.price_per_kg,
            stock=ingredient.stock_kg,
            minimum=ingredient.minimum_kg_day,
            maximum=ingredient.maximum_kg_day,
            nel=nel,
        )
    return defaults


def number(value: Any, label: str) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Informe um valor numérico para {label}.") from None
    if not isfinite(value) or value < 0:
        raise ValueError(f"{label} deve ser finito e não negativo.")
    return value


def build_feeds(catalog: dict[int, dict], rows: list[dict]) -> tuple[list[NRCFeed], dict]:
    if not rows:
        raise ValueError("Selecione pelo menos um ingrediente.")
    feeds, metadata = [], {}
    for row in rows:
        identifier = int(row["id"])
        if identifier in metadata:
            raise ValueError(f"Ingrediente duplicado (ID {identifier}).")
        item = catalog.get(identifier)
        if item is None:
            raise ValueError(f"Ingrediente {identifier} indisponível no catálogo NRC.")
        name = item["name"]
        data = {key: number(row.get(key), f"{name} · {label}") for key, label in INPUTS.items()}
        if data["minimum"] > data["maximum"]:
            raise ValueError(f"O mínimo supera o máximo para {name}.")
        composition = item["composition"]
        if composition["units"] != "kg":
            raise ValueError(f"Unidade de composição incompatível para {name}.")
        codes = {"rufas_id", "Fd_Category", "feed_type", "units", "is_fat", "is_wetforage"}
        values = {key: number(value, f"{name} · NRC/{key}") for key, value in composition.items() if key not in codes}
        dm = values["DM"] / 100.0
        feeds.append(
            NRCFeed(
                **(values | {"limit": data["maximum"] * dm, "lower_limit": data["minimum"] * dm}),
                rufas_id=identifier,
                Fd_Category=FeedCategorization(composition["Fd_Category"]),
                feed_type=FeedComponentType(composition["feed_type"]),
                units=MeasurementUnits(composition["units"]),
                is_fat=composition["is_fat"].upper() == "TRUE",
                is_wetforage=composition["is_wetforage"].upper() == "TRUE",
                purchase_cost=data["price"] / dm,
                amount_available=data["stock"] * dm,
                on_farm_cost=0.0,
                buffer=0.0,
            )
        )
        metadata[identifier] = dict(
            name=name,
            nel_mcal_per_kg_dm=data["nel"],
            nel_source="Hipótese da demonstração ou valor informado no cenário web",
            feed_source=COMPOSITION,
        )
    return feeds, metadata


def animal_requirements(animal_id: int, milk: float) -> dict:
    with _NATIVE_LOCK, demo_inputs(animal_id=animal_id, milk_kg_day=milk) as (animal, feeds, _, _):
        return asdict(animal.calculate_nutrition_requirements("Barn", 0.0, 20.0, feeds))


def nasem_phosphorus_diagnostic(animal) -> dict:
    """Use the native NASEM requirements dispatch on an isolated adult animal snapshot."""
    snapshot = copy(animal)
    snapshot.nutrient_standard = NutrientStandard.NASEM
    # Adult requirements use physiological state and the previous intake snapshot.
    # The feeds argument is consumed by the calf branch only.
    requirements = snapshot.calculate_nutrition_requirements("Barn", 0.0, 20.0, [])
    return dict(
        standard="NASEM 2021",
        requirement_g_day=float(requirements.phosphorus),
        dmi_kg_day=float(requirements.dry_matter),
        source=NASEM_SOURCE,
    )


def run_scenario(
    animals: dict[int, dict],
    catalog: dict[int, dict],
    animal_id: int,
    rows: list[dict],
    milk: float,
    days: int,
    cp: float,
    nel: float,
    ndf_min: float,
    ndf_max: float,
    constrain_absorbed_minerals: bool = False,
    show_nasem_diagnostic: bool = False,
) -> dict:
    if animal_id not in animals:
        raise ValueError("Selecione uma vaca Holandesa em lactação disponível no arquivo RuFaS.")
    if days < 1:
        raise ValueError("O período deve ter pelo menos um dia.")
    milk = number(milk, "produção de leite")
    if milk == 0:
        raise ValueError("Informe produção de leite positiva para a vaca em lactação.")
    if not 0 <= ndf_min <= ndf_max <= 100:
        raise ValueError("Informe limites ordenados de FDN entre 0 e 100%.")
    feeds, metadata = build_feeds(catalog, rows)
    thresholds = dict(
        cp_min_kg=number(cp, "PB mínima"),
        nel_min_mcal=number(nel, "NEL mínima"),
        ndf_min_fraction=ndf_min / 100,
        ndf_max_fraction=ndf_max / 100,
        supplemental_source="Metas externas do cenário web",
    )
    with _NATIVE_LOCK, demo_inputs(animal_id=animal_id, milk_kg_day=milk) as (animal, _, _, _):
        report = optimize_animal_ration(
            animal,
            feeds,
            metadata,
            thresholds,
            period_days=days,
            constrain_absorbed_minerals=constrain_absorbed_minerals,
        )
        nasem = nasem_phosphorus_diagnostic(animal) if show_nasem_diagnostic else None
    for ingredient in report["ingredients"]:
        for param in ("price_per_kg", "stock_kg", "minimum_kg_day", "maximum_kg_day"):
            ingredient["sources"][param] = "Parâmetros da demonstração ou valores informados no cenário web"
    return dict(
        **report,
        scenario_id=uuid4().hex[:12],
        animal=animals[animal_id],
        period_days=days,
        nutrient_standard="NRC 2001",
        nasem_phosphorus_diagnostic=nasem,
        assumptions={**ASSUMPTIONS, "leite_kg_dia": milk, "origem_animal": POPULATION},
        limitations=LIMITATIONS,
    )


def export_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
