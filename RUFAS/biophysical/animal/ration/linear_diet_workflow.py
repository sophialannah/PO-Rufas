"""Traceable NRC-to-LP workflow; external thresholds are never inferred from MP or DE."""

from dataclasses import asdict
import json
from math import isfinite
from pathlib import Path

from RUFAS.biophysical.animal.nutrients.nrc_requirements_calculator import NRCRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import FeedInRation, NutritionSupplyCalculator
from RUFAS.biophysical.animal.ration.linear_diet import AnimalProfile, optimize_diet
from RUFAS.biophysical.animal.ration.linear_diet_adapter import ingredient_from_feed, requirements_from_rufas


def run_nrc_workflow(
    animal_inputs: dict, feeds: list, feed_metadata: dict, external_thresholds: dict, *, period_days: float = 1.0
) -> dict:
    """Accept native NRCFeed objects with allocated stocks, prices and inclusion limits.

    Metadata keyed by feed ID must provide name, nel_mcal_per_kg_dm, nel_source,
    feed_source. external_thresholds follows requirements_from_rufas keyword args.
    The calculator's legacy TDN_percentage argument consumes a fraction, not percent.
    This workflow imports only DMI into the LP; other native outputs are diagnostic.
    """
    tdn = animal_inputs["TDN_percentage"]
    if not isfinite(tdn) or not 0 <= tdn <= 1:
        raise ValueError("TDN_percentage must be a fraction in [0, 1], e.g. 0.65")
    native = NRCRequirementsCalculator.calculate_requirements(**animal_inputs)
    requirements = requirements_from_rufas(native, **external_thresholds)
    animal = AnimalProfile(
        animal_inputs["body_weight"],
        animal_inputs["days_in_milk"],
        animal_inputs["milk_production"],
        animal_inputs["milk_fat"],
        animal_inputs["milk_true_protein"],
        requirements,
        "Caller animal inputs; NRC calculator supplies DMI only",
    )
    ingredients = [ingredient_from_feed(feed, **feed_metadata[feed.rufas_id]) for feed in feeds]
    result = optimize_diet(animal, ingredients, period_days=period_days)
    supply = None
    if result.status == "optimal":
        ration = [FeedInRation(result.ration_kg_dm_day[f.rufas_id], f) for f in feeds]
        supply = {
            nutrient: NutritionSupplyCalculator._calculate_nutritive_content(ration, nutrient)
            for nutrient in ("CP", "NDF")
        }
    return dict(
        animal_inputs={**animal_inputs, "animal_type": str(animal_inputs["animal_type"])},
        native_requirements=asdict(native),
        lp_animal=asdict(animal),
        ingredients=[asdict(i) for i in ingredients],
        period_days=period_days,
        result=asdict(result),
        native_supply_kg_day=supply,
        scope="DMI imported; PB/NEL/FDN/mineral thresholds external. No full nutritional certification.",
    )


def main() -> None:
    from RUFAS.biophysical.animal.ration.linear_diet_example import example_calculator_inputs, example_feeds

    inputs = example_calculator_inputs()
    feeds = example_feeds()
    names = {1: ("Alfafa (farinha)", 1.3), 44: ("Milho", 2.0), 167: ("Farelo de soja", 1.8)}
    metadata = {
        f.rufas_id: dict(
            name=names[f.rufas_id][0],
            nel_mcal_per_kg_dm=names[f.rufas_id][1],
            nel_source="Illustrative NEL, not calculated from DE",
            feed_source="NRC_comp.csv composition; illustrative BRL prices, stocks and limits",
        )
        for f in feeds
    }
    external = dict(
        cp_min_kg=3.6,
        nel_min_mcal=35.0,
        ndf_min_fraction=0.28,
        ndf_max_fraction=0.40,
        supplemental_source="Illustrative academic thresholds, not individual NASEM requirements",
    )
    report = run_nrc_workflow(inputs, feeds, metadata, external, period_days=7)
    wrong = NRCRequirementsCalculator.calculate_requirements(**{**inputs, "TDN_percentage": 65.0})
    report["tdn_comparison"] = dict(
        before_mp_g=wrong.metabolizable_protein,
        after_mp_g=report["native_requirements"]["metabolizable_protein"],
        before_dmi_kg=wrong.dry_matter,
        after_dmi_kg=report["native_requirements"]["dry_matter"],
        directly_used_by_lp=False,
    )
    target = Path("output/revisao_integracao.json")
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "TDN": report["tdn_comparison"],
                "status": report["result"]["status"],
                "cost": report["result"]["cost_per_day"],
                "native_supply": report["native_supply_kg_day"],
                "scope": report["scope"],
                "report": str(target),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if report["result"]["status"] != "optimal":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
