"""Least-cost LP with fixed nutrient coefficients; see docs/otimizador_linear.md.

Amounts and prices use fresh matter. Nutrient fractions use dry matter.
This optional model does not replace RuFaS's nonlinear nutrition model.
"""

from dataclasses import dataclass, field
from math import isfinite

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import linprog


def _nonnegative(name: str, value: float) -> None:
    if not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")


def _fraction(name: str, value: float) -> None:
    _nonnegative(name, value)
    if value > 1:
        raise ValueError(f"{name} must be a fraction in [0, 1]")


@dataclass(frozen=True)
class Ingredient:
    """One ingredient. All monetary values must use the same currency.

    stock_kg is the stock allocated to this animal over the planning period.
    sources maps parameter names to provenance; units are explicit in field names.
    mineral_fractions contains total (not absorbed) mineral kg per kg DM.
    """

    identifier: int
    name: str
    price_per_kg: float
    stock_kg: float
    dm_fraction: float
    nel_mcal_per_kg_dm: float
    cp_fraction: float
    ndf_fraction: float
    minimum_kg_day: float = 0.0
    maximum_kg_day: float | None = None
    mineral_fractions: dict[str, float] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("price_per_kg", "stock_kg", "nel_mcal_per_kg_dm", "minimum_kg_day"):
            _nonnegative(name, getattr(self, name))
        for name in ("dm_fraction", "cp_fraction", "ndf_fraction"):
            _fraction(name, getattr(self, name))
        if self.dm_fraction == 0 or not self.name:
            raise ValueError("Positive dry matter and a name are required")
        if self.maximum_kg_day is not None:
            _nonnegative("maximum_kg_day", self.maximum_kg_day)
            if self.maximum_kg_day < self.minimum_kg_day:
                raise ValueError("Maximum inclusion is below minimum")
        for name, value in self.mineral_fractions.items():
            _fraction(name, value)

    @staticmethod
    def price_from_tonne(price_per_tonne: float) -> float:
        """Convert price per metric tonne to price per kg on the SAME matter basis."""
        _nonnegative("price_per_tonne", price_per_tonne)
        return price_per_tonne / 1000.0


@dataclass(frozen=True)
class DietRequirements:
    """Daily fixed requirements; minerals refer to total dietary intake, kg/day."""

    dm_min_kg: float
    dm_max_kg: float
    cp_min_kg: float
    nel_min_mcal: float
    ndf_min_fraction: float | None = None
    ndf_max_fraction: float | None = None
    mineral_min_kg: dict[str, float] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("dm_min_kg", "dm_max_kg", "cp_min_kg", "nel_min_mcal"):
            _nonnegative(name, getattr(self, name))
        if self.dm_max_kg < self.dm_min_kg or self.dm_max_kg == 0:
            raise ValueError("Invalid dry matter interval")
        for name in ("ndf_min_fraction", "ndf_max_fraction"):
            value = getattr(self, name)
            if value is not None:
                _fraction(name, value)
        if (
            self.ndf_min_fraction is not None
            and self.ndf_max_fraction is not None
            and self.ndf_min_fraction > self.ndf_max_fraction
        ):
            raise ValueError("Invalid NDF interval")
        if self.dm_min_kg == 0 and (self.ndf_min_fraction is not None or self.ndf_max_fraction is not None):
            raise ValueError("NDF proportions require a strictly positive dry matter minimum")
        for name, value in self.mineral_min_kg.items():
            _nonnegative(name, value)


@dataclass(frozen=True)
class AnimalProfile:
    """Single animal snapshot; requirements are supplied, not inferred from milk yield."""

    body_weight_kg: float
    days_in_milk: int
    milk_kg_day: float
    milk_fat_percent: float
    milk_protein_percent: float
    requirements: DietRequirements
    source: str

    def __post_init__(self) -> None:
        for name in ("body_weight_kg", "days_in_milk", "milk_kg_day"):
            _nonnegative(name, getattr(self, name))
        if self.body_weight_kg == 0 or int(self.days_in_milk) != self.days_in_milk:
            raise ValueError("Positive body weight and integer days in milk are required")
        for name in ("milk_fat_percent", "milk_protein_percent"):
            _fraction(name, getattr(self, name) / 100.0)


@dataclass(frozen=True)
class ConstraintCheck:
    """Signed residual in the original row units; nonnegative means feasible."""

    name: str
    supplied: float
    lower: float | None
    upper: float | None
    slack: float
    satisfied: bool


@dataclass
class DietResult:
    status: str
    message: str
    quantities_kg_day: dict[int, float] = field(default_factory=dict)
    ration_kg_dm_day: dict[int, float] = field(default_factory=dict)
    costs_per_day: dict[int, float] = field(default_factory=dict)
    cost_per_day: float | None = None
    totals: dict[str, float] = field(default_factory=dict)
    checks: list[ConstraintCheck] = field(default_factory=list)


@dataclass
class _Row:
    name: str
    coefficients: NDArray[np.float64]
    lower: float | None = None
    upper: float | None = None


def _nutrient_rows(ingredients: list[Ingredient], req: DietRequirements) -> list[_Row]:
    dm = np.array([i.dm_fraction for i in ingredients], dtype=np.float64)
    cp = dm * np.array([i.cp_fraction for i in ingredients])
    nel = dm * np.array([i.nel_mcal_per_kg_dm for i in ingredients])
    ndf = dm * np.array([i.ndf_fraction for i in ingredients])
    rows = [
        _Row("DM_kg", dm, req.dm_min_kg, req.dm_max_kg),
        _Row("CP_kg", cp, req.cp_min_kg),
        _Row("NEL_Mcal", nel, req.nel_min_mcal),
    ]
    if req.ndf_min_fraction is not None:
        rows.append(_Row("NDF_min_kg_residual", ndf - req.ndf_min_fraction * dm, 0.0))
    if req.ndf_max_fraction is not None:
        rows.append(_Row("NDF_max_kg_residual", ndf - req.ndf_max_fraction * dm, upper=0.0))
    for mineral, minimum in req.mineral_min_kg.items():
        if any(mineral not in i.mineral_fractions for i in ingredients):
            raise ValueError(f"Missing total dietary {mineral} composition; unknown is not zero")
        composition = np.array([i.mineral_fractions[mineral] for i in ingredients], dtype=np.float64)
        rows.append(_Row(f"mineral_{mineral}_kg", np.asarray(dm * composition, dtype=np.float64), minimum))
    return rows


def _check(row: _Row, x: NDArray[np.float64], tolerance: float) -> ConstraintCheck:
    supplied = float(row.coefficients @ x)
    slacks = []
    if row.lower is not None:
        slacks.append(supplied - row.lower)
    if row.upper is not None:
        slacks.append(row.upper - supplied)
    slack = min(slacks)
    return ConstraintCheck(
        row.name, supplied, row.lower, row.upper, float(slack), bool(isfinite(supplied) and slack >= -tolerance)
    )


def _inequalities(rows: list[_Row]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Convert lower/upper rows to the A_ub x <= b_ub convention."""
    coefficients, limits = [], []
    for row in rows:
        if row.lower is not None:
            coefficients.append(-row.coefficients)
            limits.append(-row.lower)
        if row.upper is not None:
            coefficients.append(row.coefficients)
            limits.append(row.upper)
    return np.array(coefficients), np.array(limits)


def optimize_diet(
    animal: AnimalProfile,
    ingredients: list[Ingredient],
    *,
    period_days: float = 1.0,
    tolerance: float = 1e-7,
    absorbed_minerals: dict[str, tuple[float, dict[int, float]]] | None = None,
) -> DietResult:
    """Minimize daily cost for a constant daily ration over period_days.

    All nutrient rows and variable/stock bounds are independently checked after
    HiGHS returns. Failed or infeasible solves never expose a usable ration.
    Absorbed mineral rows use (minimum g/day, coefficient in g/kg DM by feed ID).
    """
    if not isfinite(period_days) or period_days <= 0:
        raise ValueError("period_days must be finite and positive")
    if not isfinite(tolerance) or not 0 < tolerance <= 1e-4:
        raise ValueError("tolerance must be in (0, 1e-4]")
    ids = {ingredient.identifier for ingredient in ingredients}
    if not ingredients or len(ids) != len(ingredients):
        raise ValueError("Provide a nonempty list of ingredients with unique IDs")
    rows = _nutrient_rows(ingredients, animal.requirements)
    for mineral, (minimum_g, by_id) in (absorbed_minerals or {}).items():
        _nonnegative(f"Absorbed {mineral} minimum (g/day)", minimum_g)
        if by_id.keys() != ids:
            raise ValueError(f"Absorbed {mineral} composition must cover every ingredient ID")
        for value in by_id.values():
            _nonnegative(f"Absorbed {mineral} coefficient (g/kg DM)", value)
        coefficients = np.array([by_id[i.identifier] * i.dm_fraction for i in ingredients], dtype=np.float64)
        rows.append(_Row(f"absorbed_{mineral}_g", coefficients, lower=minimum_g))
    bounds = []
    bound_rows = []
    for index, ingredient in enumerate(ingredients):
        upper = ingredient.stock_kg / period_days
        if ingredient.maximum_kg_day is not None:
            upper = min(upper, ingredient.maximum_kg_day)
        if ingredient.minimum_kg_day > upper:
            return DietResult(
                "infeasible", f"Ingredient {ingredient.identifier}: minimum exceeds stock/period or maximum"
            )
        bounds.append((ingredient.minimum_kg_day, upper))
        unit = np.zeros(len(ingredients), dtype=np.float64)
        unit[index] = 1.0
        bound_rows.append(
            _Row(
                f"inclusion_{ingredient.identifier}_kg_day", unit, ingredient.minimum_kg_day, ingredient.maximum_kg_day
            )
        )
        bound_rows.append(
            _Row(
                f"stock_{ingredient.identifier}_kg",
                np.asarray(unit * period_days, dtype=np.float64),
                0.0,
                ingredient.stock_kg,
            )
        )
    a_ub, b_ub = _inequalities(rows)
    costs = np.array([i.price_per_kg for i in ingredients])
    solution = linprog(costs, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not solution.success:
        status = "infeasible" if solution.status == 2 else "solver_failure"
        return DietResult(status, str(solution.message))
    checks = [_check(row, solution.x, tolerance) for row in rows + bound_rows]
    if not np.all(np.isfinite(solution.x)) or not all(check.satisfied for check in checks):
        return DietResult("verification_failed", "Solver solution failed independent feasibility checks", checks=checks)
    quantities = {i.identifier: float(x) for i, x in zip(ingredients, solution.x)}
    dry = {i.identifier: quantities[i.identifier] * i.dm_fraction for i in ingredients}
    daily_costs = {i.identifier: quantities[i.identifier] * i.price_per_kg for i in ingredients}
    totals = {
        "DM_kg": sum(dry.values()),
        "CP_kg": sum(dry[i.identifier] * i.cp_fraction for i in ingredients),
        "NEL_Mcal": sum(dry[i.identifier] * i.nel_mcal_per_kg_dm for i in ingredients),
        "NDF_kg": sum(dry[i.identifier] * i.ndf_fraction for i in ingredients),
    }
    for mineral in animal.requirements.mineral_min_kg:
        totals[f"mineral_{mineral}_kg"] = sum(dry[i.identifier] * i.mineral_fractions[mineral] for i in ingredients)
    return DietResult(
        "optimal", str(solution.message), quantities, dry, daily_costs, sum(daily_costs.values()), totals, checks
    )
