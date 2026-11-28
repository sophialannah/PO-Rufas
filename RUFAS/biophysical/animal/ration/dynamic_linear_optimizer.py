"""Opt-in sequential HiGHS formulation using the native daily NRC constraint functions."""

from dataclasses import asdict
from inspect import signature

import numpy as np
from scipy.optimize import OptimizeResult

from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.nutrients.nutrition_evaluator import NutritionEvaluator
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.ration.linear_diet import AnimalProfile, DietRequirements, Ingredient, optimize_diet
from RUFAS.biophysical.animal.ration.ration_optimizer import RationConfig, RationOptimizer
from RUFAS.data_structures.feed_storage_to_animal_connection import NRCFeed, NutrientStandard, FeedComponentType
from RUFAS.biophysical.animal.ration.mineral_limits import (
    calcium_total_upper,
    phosphorus_total_upper,
    mineral_report,
)


class DynamicRationOptimizer(RationOptimizer):
    """Instance-local selection and explicit fallbacks. Native calls use the original method."""

    def __init__(self, strategy="native_slsqp", fallback="native_slsqp", max_iterations=60, mineral_policy=None):
        super().__init__()
        if strategy not in {
            "native_slsqp",
            "linear_highs",
            "linear_highs_all",
            "linear_highs_exclusive",
        } or fallback not in {"native_slsqp", "fail"}:
            raise ValueError("Unknown optimizer strategy or fallback")
        self.strategy = strategy
        self.fallback = "fail" if strategy == "linear_highs_exclusive" else fallback
        self.mineral_policy = mineral_policy or ("native" if strategy == "native_slsqp" else "nrc2005_mtl")
        if self.mineral_policy not in {"native", "nrc2005_mtl"}:
            raise ValueError("Unknown mineral policy")
        self.max_iterations = max_iterations
        self.events = []

    def set_constraints(self, ration_config):
        super().set_constraints(ration_config)
        if self.mineral_policy == "nrc2005_mtl":
            if ration_config.nutrient_standard is not NutrientStandard.NRC:
                raise ValueError("NRC mineral policy is only enabled with NRC requirements")
            for collection in (self.cow_constraints, self.heifer_constraints):
                collection.extend(
                    dict(type="ineq", fun=f, args=(ration_config,))
                    for f in (calcium_total_upper, phosphorus_total_upper)
                )

    def attempt_optimization(self, *args, **kwargs):
        bound = signature(RationOptimizer.attempt_optimization).bind(self, *args, **kwargs)
        bound.apply_defaults()
        inputs = dict(bound.arguments)
        inputs.pop("self")
        supported = (
            inputs["nutrient_standard"] is NutrientStandard.NRC
            and inputs["animal_combination"]
            in (
                (AnimalCombination.LAC_COW,)
                if self.strategy == "linear_highs"
                else (
                    AnimalCombination.LAC_COW,
                    AnimalCombination.GROWING,
                    AnimalCombination.CLOSE_UP,
                    AnimalCombination.GROWING_AND_CLOSE_UP,
                )
            )
            and not inputs["user_defined_ration_dictionary"]
            and all(isinstance(f, NRCFeed) for f in inputs["pen_available_feeds"])
        )
        reason = None
        if self.strategy != "native_slsqp" and supported:
            result, config, trace = self._linear_attempt(inputs)
            self.events.append(
                dict(
                    requested=self.strategy,
                    used="linear_highs",
                    success=bool(result.success),
                    reason=None,
                    trace=trace,
                    requirements=asdict(inputs["requirements"]),
                    category=inputs["animal_combination"].value,
                    mineral_policy=self.mineral_policy,
                    termination=str(result.message),
                    converged=bool(result.get("converged", False)),
                )
            )
            if self.strategy == "linear_highs_exclusive" and not result.success:
                raise RuntimeError(f"Exclusive HiGHS failed for {inputs['animal_combination'].value}: {result.message}")
            if result.success or self.fallback == "fail":
                return result, config
            reason = "highs_failure_or_native_rejection"
        elif self.strategy != "native_slsqp":
            reason = "unsupported_category_or_standard"
            if self.fallback == "fail":
                self.events.append(
                    dict(
                        requested=self.strategy,
                        used="unsupported",
                        success=False,
                        reason=reason,
                        trace=[],
                        category=inputs["animal_combination"].value,
                        requirements=asdict(inputs["requirements"]),
                        termination="unsupported_category_or_standard",
                    )
                )
                raise ValueError("Category or nutrient standard unsupported by linear_highs")
        result, config = super().attempt_optimization(*args, **kwargs)
        self.events.append(
            dict(
                requested=self.strategy,
                used="native_slsqp",
                success=bool(result.success),
                reason=reason,
                trace=[],
                requirements=asdict(inputs["requirements"]),
                category=inputs["animal_combination"].value,
                mineral_policy=self.mineral_policy,
                termination=str(result.message),
            )
        )
        return result, config

    def _linear_attempt(self, inputs):
        feeds = sorted(inputs["pen_available_feeds"], key=lambda f: f.rufas_id)
        req = inputs["requirements"]
        config = RationConfig(
            inputs["nutrient_standard"],
            req,
            feeds,
            inputs["initial_dry_matter_requirement"],
            inputs["initial_protein_requirement"],
            inputs["pen_average_body_weight"],
            inputs["pen_average_enteric_methane"],
            inputs["pen_average_urine_nitrogen"],
            inputs["animal_combination"],
        )
        self.set_constraints(config)
        constraints = self._select_constraints(inputs["animal_combination"])
        bounds = self._build_bounds(config)
        # Keep native RNG consumption identical, then align the warm start by feed ID.
        initial = self._build_initial_value(inputs["previous_ration"], config)
        if inputs["previous_ration"]:
            initial = [float(inputs["previous_ration"].get(f.rufas_id, 0.0)) for f in feeds]
        x = self._check_initial_bounds(bounds, np.array(initial, dtype=float))
        dm = np.array([f.DM / 100 for f in feeds])
        if np.any(dm <= 0):
            raise ValueError("Positive dry matter is required")
        requirements = DietRequirements(
            max(1e-6, inputs["initial_dry_matter_requirement"] * (1 - config.dmi_constraint_fraction)),
            inputs["initial_dry_matter_requirement"] * (1 + config.dmi_constraint_fraction),
            0.0,
            0.0,
            sources={"dynamic": "Native NRC constraints, sequential linearization"},
        )
        profile = AnimalProfile(
            inputs["pen_average_body_weight"],
            0,
            0.0,
            0.0,
            0.0,
            requirements,
            "Requirements-only carrier; milk and DEL placeholders are not biological inputs",
        )
        trace = []
        result = OptimizeResult(
            success=False, x=x, fun=float(self.objective(x, config)), message="No accepted HiGHS candidate", status=2
        )
        best = None
        radius = 5.0
        max_radius = max(10.0, requirements.dm_max_kg * 2)
        # Normalize disparate energy, grams and percent rows only for merit decisions.
        scales = np.maximum(1.0, np.abs([c["fun"](x, config) for c in constraints]))

        def violation(point):
            return float(np.maximum(0.0, -np.array([c["fun"](point, config) for c in constraints]) / scales).sum())

        merit = self.objective(x, config) + 1e4 * violation(x)
        termination = "iteration_limit"
        restarted = False
        for iteration in range(self.max_iterations):
            rows = []
            for constraint in constraints:
                function = constraint["fun"]
                value = float(function(x, config))
                gradient = np.zeros(len(feeds))
                for i in range(len(feeds)):
                    delta = np.zeros(len(feeds))
                    delta[i] = 1e-4
                    gradient[i] = (function(x + delta, config) - value) / delta[i]
                # Each linear row is in MN; native gradients are with respect to kg MS.
                rows.append(
                    (
                        function.__name__,
                        {f.rufas_id: float(g * d) for f, g, d in zip(feeds, gradient, dm)},
                        # Pen rounds every ingredient to 1e-6 kg. Reserve one
                        # quantum times ||gradient||_1, then verify the real
                        # rounded nonlinear values; never change nutrient data.
                        float(1e-4 + 1e-6 * np.abs(gradient).sum() - value + gradient @ x),
                    )
                )
            ingredients = [
                Ingredient(
                    f.rufas_id,
                    str(f.rufas_id),
                    f.purchase_cost * d,
                    upper / d,
                    d,
                    0.0,
                    f.CP / 100,
                    f.NDF / 100,
                    maximum_kg_day=min(upper, amount + radius) / d,
                    minimum_kg_day=max(low, amount - radius) / d,
                    sources={"dynamic": "NRCFeed native price, daily pen limits and trust region"},
                )
                for f, d, amount, (low, upper) in zip(feeds, dm, x, bounds)
            ]
            lp = optimize_diet(profile, ingredients, linear_constraints=rows)
            trace.append(
                dict(
                    iteration=iteration,
                    lp_status=lp.status,
                    x_before=x.tolist(),
                    radius=radius,
                    feed_ids=[f.rufas_id for f in feeds],
                    physical_bounds=bounds,
                    local_bounds=[(max(lo, v - radius), min(hi, v + radius)) for v, (lo, hi) in zip(x, bounds)],
                )
            )
            if lp.status != "optimal":
                result.message = lp.message
                if radius < max_radius:
                    radius = min(max_radius, radius * 2)
                    trace[-1]["decision"] = "expand_for_feasibility"
                    continue
                if best is None and not restarted:
                    # Alternative numerical starting point, not an imposed diet:
                    # distribute the predicted intake over non-mineral feeds,
                    # honoring all real feed bounds. Original nonlinear
                    # constraints still decide feasibility of every candidate.
                    x = np.array([lo for lo, _ in bounds], dtype=float)
                    eligible = [i for i, f in enumerate(feeds) if f.feed_type is not FeedComponentType.MINERAL]
                    remaining = max(0.0, inputs["initial_dry_matter_requirement"] - x.sum())
                    while eligible and remaining > 1e-8:
                        share = remaining / len(eligible)
                        for i in eligible:
                            addition = min(share, bounds[i][1] - x[i])
                            x[i] += addition
                            remaining -= addition
                        eligible = [i for i in eligible if x[i] < bounds[i][1] - 1e-8]
                    merit = self.objective(x, config) + 1e4 * violation(x)
                    restarted = True
                    trace[-1]["decision"] = "restart_balanced_after_infeasible_linearization"
                    continue
                termination = "linearized_problem_infeasible"
                break
            candidate = np.array([lp.ration_kg_dm_day[f.rufas_id] for f in feeds])

            class NRCSupply(NutritionSupplyCalculator):
                nutrient_standard = NutrientStandard.NRC

            # Check the exact quantities that the native Pen will apply (six decimals).
            rounded = np.round(candidate, 6)
            residuals = {c["fun"].__name__: float(c["fun"](rounded, config)) for c in constraints}
            supply = NRCSupply.calculate_nutrient_supply(
                feeds_used=feeds,
                ration_formulation={f.rufas_id: float(q) for f, q in zip(feeds, rounded)},
                body_weight=inputs["pen_average_body_weight"],
                enteric_methane=0.0,
                urinary_nitrogen=0.0,
            )
            approved, evaluation = NutritionEvaluator.evaluate_nutrition_supply(
                req, supply, inputs["animal_combination"] is AnimalCombination.LAC_COW
            )
            trace[-1].update(
                residuals=residuals,
                deltas=asdict(evaluation),
                approved=bool(approved),
                x_candidate=candidate.tolist(),
                cost=lp.cost_per_day,
                minerals=mineral_report(rounded, config),
            )
            accepted = bool(approved) and all(value >= 0.0 for value in residuals.values())
            trial = OptimizeResult(
                success=accepted,
                x=candidate,
                fun=lp.cost_per_day,
                nit=iteration + 1,
                message=(
                    "Checked HiGHS sequential candidate" if accepted else "Native criteria rejected HiGHS candidate"
                ),
                status=0 if accepted else 2,
                linear_diet_result=asdict(lp),
            )
            result = trial
            if accepted and (best is None or trial.fun < best.fun):
                best = trial
                trace[-1]["best_cost"] = best.fun
            candidate_merit = self.objective(candidate, config) + 1e4 * violation(candidate)
            improvement = float(self.objective(x, config) - trial.fun)
            trace[-1]["objective_improvement"] = improvement
            if accepted and violation(x) <= 1e-8 and abs(improvement) <= 1e-7 * max(1.0, abs(trial.fun)):
                termination = "objective_and_original_feasibility_converged"
                trace[-1]["decision"] = "converged"
                break
            if candidate_merit < merit - 1e-9 or (accepted and violation(x) > 1e-8):
                step = float(np.max(np.abs(candidate - x)))
                x = candidate
                merit = candidate_merit
                if step >= 0.8 * radius:
                    radius = min(max_radius, radius * 2)
                trace[-1]["decision"] = "accept_step"
            else:
                radius *= 0.5
                trace[-1]["decision"] = "shrink_rejected_step"
                if radius < 1e-5:
                    termination = "trust_region_stalled"
                    break
        if best is not None:
            result = best
        result.message = termination
        result.converged = termination == "objective_and_original_feasibility_converged"
        result.nit = len(trace)
        return result, config, trace
