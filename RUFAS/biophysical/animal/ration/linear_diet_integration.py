"""Opt-in bridge from one initialized RuFaS Animal to native ration management."""

from dataclasses import asdict
from math import isclose, isfinite

from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.nutrition_evaluator import NutritionEvaluator
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import FeedInRation, NutritionSupplyCalculator
from RUFAS.biophysical.animal.ration.linear_diet import DietResult, optimize_diet
from RUFAS.biophysical.animal.ration.linear_diet_adapter import (
    ingredient_from_feed,
    profile_from_animal,
    requirements_from_rufas,
)
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.data_structures.feed_storage_to_animal_connection import FeedComponentType, NRCFeed, NutrientStandard

# Keep an active mineral bound above both the LP verification tolerance and round-off
# in the native round-trip. NutritionEvaluator compares against zero exactly.
MINERAL_ROUNDING_MARGIN_G = 1e-6


def ration_config_from_result(result: DietResult, feeds: list[NRCFeed]) -> dict:
    """Convert a checked LP solution to native user-ration percentages on DM basis."""
    if result.status != "optimal" or not result.checks or not all(c.satisfied for c in result.checks):
        raise ValueError("Only independently checked optimal solutions can be exported")
    ids = [f.rufas_id for f in feeds]
    if len(set(ids)) != len(ids) or set(ids) != set(result.ration_kg_dm_day):
        raise ValueError("Feed IDs must uniquely match the solution")
    for feed in feeds:
        value = result.ration_kg_dm_day[feed.rufas_id]
        if not isfinite(value) or value < 0 or not 0 < feed.DM <= 100:
            raise ValueError("Invalid dry matter amount or composition")
        if not isclose(value, result.quantities_kg_day[feed.rufas_id] * feed.DM / 100, abs_tol=1e-7):
            raise ValueError("Feed DM does not match the optimized composition")
    total = sum(result.ration_kg_dm_day.values())
    if total <= 0:
        raise ValueError("Native ration requires positive total dry matter")
    return dict(
        rations=[
            dict(
                animal_combination="lac_cow",
                feeds=[dict(feed_type=i, ration_percentage=100 * result.ration_kg_dm_day[i] / total) for i in ids],
            )
        ],
        ration_formulation_parameters=dict(user_defined_ration_tolerance=1e-7),
    )


def optimize_animal_ration(
    animal,
    feeds: list[NRCFeed],
    metadata: dict,
    external_thresholds: dict,
    *,
    period_days: float = 1.0,
    housing: str = "Barn",
    walking_distance: float = 0.0,
    previous_temperature: float = 20.0,
    constrain_absorbed_minerals: bool = False,
) -> dict:
    """Use Animal's actual NRC dispatch, then round-trip through native RationManager.

    DMI and optionally the native absorbed P and Ca minima are imported into the LP.
    A per-call subclass isolates user-ration settings; no change to Pen or farm defaults.
    """
    if animal.animal_type is not AnimalType.LAC_COW or animal.nutrient_standard is not NutrientStandard.NRC:
        raise ValueError("This bridge supports NRC lactating cows only")
    if not feeds or any(not isinstance(f, NRCFeed) for f in feeds):
        raise ValueError("A nonempty list of native NRCFeed objects is required")
    if constrain_absorbed_minerals:
        supported = {FeedComponentType.FORAGE, FeedComponentType.CONC, FeedComponentType.MINERAL}
        missing = [f.rufas_id for f in feeds if f.feed_type not in supported]
        if missing:
            raise ValueError(f"Absorção de fósforo e cálcio indisponível para os ingredientes {missing}.")
    native = animal.calculate_nutrition_requirements(housing, walking_distance, previous_temperature, feeds)
    req = requirements_from_rufas(native, **external_thresholds)
    profile = profile_from_animal(animal, req)
    ingredients = [ingredient_from_feed(f, **metadata[f.rufas_id]) for f in feeds]
    targets = {"phosphorus": max(native.phosphorus, native.process_based_phosphorus), "calcium": native.calcium}
    coefficients = {
        mineral: {f.rufas_id: calculator([FeedInRation(1.0, f)]) for f in feeds}
        for mineral, calculator in (
            ("phosphorus", NutritionSupplyCalculator.calculate_phosphorus_supply),
            ("calcium", NutritionSupplyCalculator.calculate_calcium_supply),
        )
    }
    mineral_rows = (
        {
            mineral: (target + MINERAL_ROUNDING_MARGIN_G if target > 0 else target, coefficients[mineral])
            for mineral, target in targets.items()
        }
        if constrain_absorbed_minerals
        else {}
    )
    result = optimize_diet(profile, ingredients, period_days=period_days, absorbed_minerals=mineral_rows)
    diagnosis = None
    if mineral_rows and result.status == "infeasible":
        baseline = optimize_diet(profile, ingredients, period_days=period_days)
        if baseline.status == "optimal":
            calcium_only = optimize_diet(
                profile, ingredients, period_days=period_days, absorbed_minerals={"calcium": mineral_rows["calcium"]}
            )
            diagnosis = (
                "phosphorus_conflict"
                if calcium_only.status == "optimal"
                else ("calcium_conflict" if calcium_only.status == "infeasible" else "mineral_conflict")
            )
    report = dict(
        animal_id=animal.id,
        profile=asdict(profile),
        requirements=asdict(native),
        ingredients=[asdict(i) for i in ingredients],
        result=asdict(result),
        native_return=None,
        nrc_minerals=dict(
            enabled=constrain_absorbed_minerals,
            requirement_g_day=targets,
            lp_minimum_g_day={name: row[0] for name, row in mineral_rows.items()},
            coefficients_g_per_kg_dm=coefficients,
            source="RuFaS NRC: NutritionSupplyCalculator.calculate_phosphorus_supply/calculate_calcium_supply",
            infeasibility=diagnosis,
            phosphorus_total_g_day=None,
        ),
    )
    if result.status != "optimal":
        return report
    config = ration_config_from_result(result, feeds)

    class SingleAnimalRationManager(RationManager):
        """Own class storage; inherited native methods execute unchanged."""

    SingleAnimalRationManager.set_user_defined_ration_tolerance(config)
    SingleAnimalRationManager.set_user_defined_rations(config)
    ration_feeds = SingleAnimalRationManager.get_user_defined_ration_feeds(AnimalCombination.LAC_COW)
    total = sum(result.ration_kg_dm_day.values())
    recovered = SingleAnimalRationManager.get_user_defined_ration(AnimalCombination.LAC_COW, total)
    if any(not isclose(recovered[i], value, abs_tol=1e-7) for i, value in result.ration_kg_dm_day.items()):
        raise RuntimeError("Native ration round-trip changed amounts")
    if ration_feeds != [f.rufas_id for f in feeds]:
        raise RuntimeError("Native ration feed IDs do not match input feeds")

    class SingleAnimalSupplyCalculator(NutritionSupplyCalculator):
        """Own nutrient_standard storage; native supply methods execute unchanged."""

        nutrient_standard = NutrientStandard.NRC

    ration = [FeedInRation(recovered[f.rufas_id], f) for f in feeds]
    supply = {key: SingleAnimalSupplyCalculator._calculate_nutritive_content(ration, key) for key in ("CP", "NDF")}
    if not isclose(supply["CP"], result.totals["CP_kg"], abs_tol=1e-7) or not isclose(
        supply["NDF"], result.totals["NDF_kg"], abs_tol=1e-7
    ):
        raise RuntimeError("Native supply does not match LP totals")
    full_supply = SingleAnimalSupplyCalculator.calculate_nutrient_supply(
        feeds_used=feeds,
        ration_formulation=recovered,
        body_weight=animal.body_weight,
        enteric_methane=0.0,
        urinary_nitrogen=0.0,
    )
    report["nrc_minerals"]["phosphorus_total_g_day"] = sum(recovered[f.rufas_id] * f.phosphorus * 10.0 for f in feeds)
    for check in result.checks:
        if check.name in {"absorbed_phosphorus_g", "absorbed_calcium_g"}:
            mineral = check.name.removeprefix("absorbed_").removesuffix("_g")
            if not isclose(check.supplied, getattr(full_supply, mineral), rel_tol=0.0, abs_tol=1e-7):
                raise RuntimeError(f"Native absorbed {mineral} supply does not match the LP")
    is_valid_cow_ration, evaluation = NutritionEvaluator.evaluate_nutrition_supply(native, full_supply, is_cow=True)
    report["native_return"] = dict(
        config=config,
        ration_feeds=ration_feeds,
        ration_kg_dm_day=recovered,
        total_dm=total,
        supply_kg=supply,
        native_evaluation=dict(
            is_valid_cow_ration=bool(is_valid_cow_ration),
            deltas={k: float(v) if v is not None else None for k, v in asdict(evaluation).items()},
            criteria={
                key.removesuffix("_acceptable"): bool(value) if value is not None else None
                for key, value in evaluation.report.items()
                if key.endswith("_acceptable")
            },
            supply_summary=dict(
                metabolizable_protein_g=float(full_supply.metabolizable_protein),
                maintenance_energy_mcal=float(full_supply.maintenance_energy),
                lactation_energy_mcal=float(full_supply.lactation_energy),
                calcium_g=float(full_supply.calcium),
                phosphorus_g=float(full_supply.phosphorus),
                forage_ndf_kg=float(full_supply.forage_ndf_supply),
                fat_kg=float(full_supply.fat_supply),
            ),
        ),
        consumer="RationManager.set_user_defined_rations/get_user_defined_ration",
    )
    return report
