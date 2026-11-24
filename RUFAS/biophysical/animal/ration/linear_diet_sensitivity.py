"""Comparable price scenarios: re-solve the same animal, stocks and nutrient model."""

from dataclasses import asdict, replace
import json
from math import isfinite

from RUFAS.biophysical.animal.ration.linear_diet import AnimalProfile, Ingredient, optimize_diet


def compare_prices(
    animal: AnimalProfile,
    ingredients: list[Ingredient],
    scenarios: dict[str, dict[int, float]],
    *,
    period_days: float = 1.0,
) -> dict:
    """Prices are currency/kg fresh matter. No dual-based sensitivity interval is claimed.

    Each scenario changes only prices; inputs are not mutated. Deltas are daily
    modeled costs relative to the base, never observed farm savings.
    """
    ids = {item.identifier for item in ingredients}
    for name, prices in scenarios.items():
        if not name or name == "base":
            raise ValueError("Scenario names must be nonempty and different from base")
        if prices.keys() - ids:
            raise ValueError("Unknown ingredient ID in price scenario")
        if any(not isfinite(p) or p < 0 for p in prices.values()):
            raise ValueError("Prices must be finite and nonnegative")
    base = optimize_diet(animal, ingredients, period_days=period_days)
    rows = {}
    for name, prices in {"base": {}, **scenarios}.items():
        adjusted = [replace(i, price_per_kg=prices.get(i.identifier, i.price_per_kg)) for i in ingredients]
        result = base if name == "base" else optimize_diet(animal, adjusted, period_days=period_days)
        delta = None
        if result.status == base.status == "optimal":
            delta = result.cost_per_day - base.cost_per_day
        rows[name] = {
            "prices_per_kg_mn": {i.identifier: i.price_per_kg for i in adjusted},
            "result": asdict(result),
            "cost_delta_per_day": delta,
        }
    return {
        "animal": asdict(animal),
        "ingredients": [asdict(i) for i in ingredients],
        "period_days": period_days,
        "scenarios": rows,
        "scope": "Fixed nutritional model; price reoptimization, not observed savings or dual ranges",
    }


def main() -> None:
    from RUFAS.biophysical.animal.ration.linear_diet_example import example_inputs

    animal, ingredients = example_inputs()
    changes = {"prices_plus_10_percent": {i.identifier: 1.1 * i.price_per_kg for i in ingredients}}
    print(json.dumps(compare_prices(animal, ingredients, changes, period_days=7), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
