"""Full-catalog coverage, reproducibility, and parameter validation."""

import pytest

from RUFAS.biophysical.animal.ration.linear_diet import optimize_diet
from RUFAS.biophysical.animal.ration.linear_diet_catalog import (
    catalog_candidates,
    demo_parameters,
    make_ingredients,
    random_cow,
)


def test_catalog_audit_accounts_for_every_record() -> None:
    candidates, audit = catalog_candidates()
    assert len(audit) == 300
    assert len({item["identifier"] for item in audit}) == 300
    assert len(candidates) == 185
    assert sum(item["status"] == "excluded" for item in audit) == 115
    assert all(item["reason"] for item in audit if item["status"] == "excluded")
    assert any("NASEM" in item["composition_source"] for item in candidates)
    assert any("NRC_comp" in item["composition_source"] for item in candidates)


def test_catalog_solution_and_repeatability() -> None:
    candidates, _ = catalog_candidates()
    params = demo_parameters(candidates, 42)
    assert params == demo_parameters(candidates, 42)
    cow, inputs = random_cow(42)
    assert (cow, inputs) == random_cow(42)
    ingredients = make_ingredients(candidates, params)
    result = optimize_diet(cow, ingredients, period_days=7)
    assert result.status == "optimal"
    assert len(result.quantities_kg_day) == 185
    assert all(check.satisfied for check in result.checks)
    assert len(result.checks) == 375
    assert result.cost_per_day == pytest.approx(23.527636, abs=1e-4)
    # More optional candidates cannot worsen an optimum with identical inputs.
    subset = [i for i in ingredients if i.identifier in {1, 44, 167}]
    restricted = optimize_diet(cow, subset, period_days=7)
    if restricted.status == "optimal":
        assert result.cost_per_day <= restricted.cost_per_day + 1e-7


@pytest.mark.parametrize("operation", ["missing", "duplicate", "negative_price", "no_source"])
def test_parameter_errors_are_not_silently_ignored(operation: str) -> None:
    candidates, _ = catalog_candidates()
    params = demo_parameters(candidates, 42)
    if operation == "missing":
        params.pop()
    elif operation == "duplicate":
        params.append(params[0])
    elif operation == "negative_price":
        params[0]["price_brl_per_kg_dm"] = -1
    else:
        params[0]["source"] = ""
    with pytest.raises(ValueError):
        make_ingredients(candidates, params)
