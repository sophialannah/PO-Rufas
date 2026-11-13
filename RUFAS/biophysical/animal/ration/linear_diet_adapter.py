"""Explicit unit-safe bridge between existing RuFaS objects and the optional LP."""

from typing import TYPE_CHECKING

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed
from RUFAS.biophysical.animal.ration.linear_diet import AnimalProfile, DietRequirements, Ingredient

if TYPE_CHECKING:
    from RUFAS.biophysical.animal.animal import Animal


def ingredient_from_feed(
    feed: Feed, *, name: str, nel_mcal_per_kg_dm: float, nel_source: str, feed_source: str
) -> Ingredient:
    """Read a feed snapshot after stock allocation/update by the caller.

    RuFaS purchase_cost is currency/kg DM; amount_available and inclusion limits
    are kg DM. Convert to fresh matter. No automatic purchases or stock mutation.
    DE/DE_Base are deliberately not mapped to NEL. Currency is not converted.
    """
    dm = feed.DM / 100.0
    if not 0 < dm <= 1:
        raise ValueError("Feed.DM must be a percentage in (0, 100]")
    if not nel_source.strip() or not feed_source.strip():
        raise ValueError("NEL and feed provenance are required")
    sources = {
        field: feed_source
        for field in (
            "identifier",
            "name",
            "price_per_kg",
            "stock_kg",
            "dm_fraction",
            "cp_fraction",
            "ndf_fraction",
            "minimum_kg_day",
            "maximum_kg_day",
            "mineral_fractions",
        )
    }
    sources["nel_mcal_per_kg_dm"] = nel_source
    return Ingredient(
        identifier=feed.rufas_id,
        name=name,
        price_per_kg=feed.purchase_cost * dm,
        stock_kg=feed.amount_available / dm,
        dm_fraction=dm,
        nel_mcal_per_kg_dm=nel_mcal_per_kg_dm,
        cp_fraction=feed.CP / 100.0,
        ndf_fraction=feed.NDF / 100.0,
        minimum_kg_day=feed.lower_limit / dm,
        maximum_kg_day=feed.limit / dm,
        mineral_fractions={
            name: getattr(feed, name) / 100.0
            for name in ("calcium", "phosphorus", "magnesium", "potassium", "sodium", "chlorine", "sulfur")
        },
        sources=sources,
    )


def requirements_from_rufas(
    requirements: NutritionRequirements,
    *,
    cp_min_kg: float,
    nel_min_mcal: float,
    supplemental_source: str,
    ndf_min_fraction: float | None = None,
    ndf_max_fraction: float | None = None,
    mineral_min_kg: dict[str, float] | None = None,
) -> DietRequirements:
    """Import DMI from RuFaS and require compatible external dietary thresholds.

    No MP-to-CP, absorbed-to-total mineral, or net-energy-system conversion is
    implied. A caller must supply a documented *total* daily NEL threshold.
    requirements.lactation_energy alone omits maintenance and other functions.
    """
    if not supplemental_source.strip():
        raise ValueError("Supplemental dietary thresholds require provenance")
    sources = {
        name: supplemental_source
        for name in ("cp_min_kg", "nel_min_mcal", "ndf_min_fraction", "ndf_max_fraction", "mineral_min_kg")
    }
    sources.update(
        {
            "dm_min_kg": "RuFaS NutritionRequirements.dry_matter (kg/day)",
            "dm_max_kg": "RuFaS NutritionRequirements.dry_matter (kg/day)",
        }
    )
    return DietRequirements(
        requirements.dry_matter,
        requirements.dry_matter,
        cp_min_kg,
        nel_min_mcal,
        ndf_min_fraction,
        ndf_max_fraction,
        mineral_min_kg or {},
        sources,
    )


def profile_from_animal(animal: "Animal", requirements: DietRequirements) -> AnimalProfile:
    """Read an initialized RuFaS Animal without triggering a simulation update.

    Pass requirements_from_rufas(animal.nutrition_requirements, ...) explicitly.
    Milk composition is configured on the RuFaS MilkProduction class.
    """
    return AnimalProfile(
        body_weight_kg=animal.body_weight,
        days_in_milk=animal.days_in_milk,
        milk_kg_day=animal.milk_production.daily_milk_produced,
        milk_fat_percent=animal.milk_production.fat_percent,
        milk_protein_percent=animal.milk_production.true_protein_percent,
        requirements=requirements,
        source="RuFaS Animal and MilkProduction snapshot",
    )
