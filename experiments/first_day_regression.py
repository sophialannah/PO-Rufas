"""Replay the exact first native lactating call, restoring RNG between solvers.

The historical implementation is loaded from an immutable evidence snapshot.
Only this experiment instruments dispatch; the production engine is unchanged.
"""

from copy import deepcopy
from dataclasses import asdict
from dataclasses import is_dataclass
from enum import Enum
import json
from pathlib import Path
import random
import types
import argparse

import numpy as np

from experiments.annual import run
from experiments.comparison import json_text
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.ration.dynamic_linear_optimizer import DynamicRationOptimizer
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.biophysical.animal.ration.mineral_limits import mineral_report
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.nutrients.nutrition_evaluator import NutritionEvaluator
from RUFAS.data_structures.feed_storage_to_animal_connection import NutrientStandard


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="evidencias/correcao_dinamica/replay_validado")
    root = Path(parser.parse_args().output)
    root.mkdir(parents=True, exist_ok=False)
    old = types.ModuleType("historical_optimizer")
    exec(
        compile(
            Path("evidencias/correcao_dinamica/optimizer_anterior.py.txt").read_text(encoding="utf-8"),
            "historical_optimizer",
            "exec",
        ),
        old.__dict__,
    )
    original = DynamicRationOptimizer.attempt_optimization
    captured = False

    def observe(self, *args, **kwargs):
        nonlocal captured
        from inspect import signature

        bound = signature(RationOptimizer.attempt_optimization).bind(self, *args, **kwargs)
        bound.apply_defaults()
        inputs = dict(bound.arguments)
        inputs.pop("self")
        if not captured and inputs["animal_combination"] is AnimalCombination.LAC_COW:
            captured = True
            state = random.getstate()
            np_state = np.random.get_state()

            def serial(value):
                if is_dataclass(value):
                    return serial(asdict(value))
                if isinstance(value, Enum):
                    return value.value
                if isinstance(value, dict):
                    return {k: serial(v) for k, v in value.items()}
                if isinstance(value, (list, tuple)):
                    return [serial(v) for v in value]
                if isinstance(value, np.generic):
                    return value.item()
                return value

            (root / "primeiro_dia_entradas.json").write_text(json.dumps(serial(inputs), indent=2), encoding="utf-8")
            reports = []
            # Use original method directly to avoid recursive experimental interception.
            solvers = [
                ("SLSQP_original", RationOptimizer(), RationOptimizer.attempt_optimization),
                (
                    "HiGHS_anterior",
                    old.DynamicRationOptimizer("linear_highs", "fail"),
                    old.DynamicRationOptimizer.attempt_optimization,
                ),
                (
                    "SLSQP_MTL_controlado",
                    DynamicRationOptimizer("native_slsqp", mineral_policy="nrc2005_mtl"),
                    original,
                ),
                ("HiGHS_aprimorado", DynamicRationOptimizer("linear_highs", "fail"), original),
            ]
            try:
                for name, solver, method in solvers:
                    random.setstate(state)
                    np.random.set_state(np_state)
                    result, config = method(solver, **deepcopy(inputs))

                    class Supply(NutritionSupplyCalculator):
                        nutrient_standard = NutrientStandard.NRC

                    rounded = np.round(result.x, 6)
                    supply = Supply.calculate_nutrient_supply(
                        feeds_used=config.feeds_used,
                        ration_formulation={f.rufas_id: float(q) for f, q in zip(config.feeds_used, rounded)},
                        body_weight=config.pen_average_body_weight,
                        enteric_methane=0.0,
                        urinary_nitrogen=0.0,
                    )
                    valid, evaluation = NutritionEvaluator.evaluate_nutrition_supply(
                        inputs["requirements"], supply, True
                    )
                    solver.set_constraints(config)
                    residuals = {
                        c["fun"].__name__: float(c["fun"](rounded, config))
                        for c in solver._select_constraints(inputs["animal_combination"])
                    }
                    reports.append(
                        dict(
                            solver=name,
                            solver_success=bool(result.success),
                            native_approved=bool(valid),
                            cost=float(result.fun),
                            iterations=int(result.get("nit", 0)),
                            termination=str(result.message),
                            ration_kg_dm={f.rufas_id: float(q) for f, q in zip(config.feeds_used, result.x)},
                            requirements=asdict(inputs["requirements"]),
                            supply=asdict(supply),
                            evaluation=asdict(evaluation),
                            minerals=mineral_report(rounded, config),
                            residuals=residuals,
                            active_constraints=[k for k, v in residuals.items() if abs(v) <= 1e-3],
                            events=getattr(solver, "events", []),
                        )
                    )
            finally:
                random.setstate(state)
                np.random.set_state(np_state)
            (root / "primeiro_dia_comparacao.json").write_text(json_text(reports), encoding="utf-8")
        return original(self, *args, **kwargs)

    DynamicRationOptimizer.attempt_optimization = observe
    try:
        run(root / "reproducao_original_1", 1, 10, 42, mineral_policy="native")
    finally:
        DynamicRationOptimizer.attempt_optimization = original


if __name__ == "__main__":
    main()
