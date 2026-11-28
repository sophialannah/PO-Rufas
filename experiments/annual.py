"""Isolated full-farm RuFaS runs with daily ration reformulation."""

import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
import random
import traceback
from time import perf_counter
from uuid import uuid4
from dataclasses import asdict

import numpy as np

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager, LogVerbosity
from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.simulation_engine import SimulationEngine, SimulationType
from RUFAS.task_manager import TaskManager
from experiments.comparison import json_text
from experiments.provenance import git_context
from RUFAS.biophysical.animal.ration.mineral_limits import mineral_report
from types import SimpleNamespace


def prepare(
    target: Path,
    days: int,
    cows: int = 10,
    strategy="native_slsqp",
    fallback="native_slsqp",
    interval=1,
    feed_overrides=None,
    adult_feed_ids=None,
    mineral_policy="nrc2005_mtl",
) -> Path:
    if not 1 <= days <= 365 or cows < 6 or interval < 1:
        raise ValueError("Use 1–365 dias, pelo menos seis vacas e intervalo positivo.")
    if strategy not in {
        "native_slsqp",
        "linear_highs",
        "linear_highs_all",
        "linear_highs_exclusive",
    } or fallback not in {"native_slsqp", "fail"}:
        raise ValueError("Unknown strategy or fallback")
    target.mkdir(parents=True, exist_ok=False)
    metadata = json.loads(Path("input/metadata/example_freestall_dairy_metadata.json").read_text())
    config = json.loads(Path("input/data/config/example_freestall_config.json").read_text())
    config.update(start_date="2013:1", end_date=f"2013:{days}", nutrient_standard="NRC")
    animal = json.loads(Path("input/data/animal/example_freestall_animal.json").read_text())
    animal["ration"].update(
        formulation_interval=interval,
        user_input=False,
        maximum_ration_reformulation_attempts=8,
        optimizer_strategy=strategy,
        optimizer_fallback=fallback,
        optimizer_record_events=True,
        optimizer_mineral_policy=mineral_policy,
    )
    animal["herd_information"].update(
        calf_num=8,
        heiferI_num=2,
        heiferII_num=2,
        heiferIII_num_springers=5,
        cow_num=cows,
        replace_num=5000,
        herd_num=cows,
        herd_size_buy_threshold=cows - 1,
        herd_size_sell_threshold=cows + 1,
    )
    feed = json.loads(Path("input/data/feed/example_Midwest_feed.json").read_text())
    feed["feeds"] = [item for item in feed["feeds"] if item["feed_type"] not in (301, 302)]
    for identifier, price in ((1, 1.4), (167, 2.8), (231, 5.0)):
        feed["feeds"].append(
            dict(
                feed_type=identifier,
                purchased_feed_cost=price,
                buffer=0.15,
                runtime_purchase_allowance=1000.0,
                advance_purchase_allowance=1000000.0,
                planning_cycle_allowance=1000.0,
            )
        )
    for item in feed["feeds"]:
        if feed_overrides and str(item["feed_type"]) in feed_overrides:
            allowed = {
                "purchased_feed_cost",
                "runtime_purchase_allowance",
                "advance_purchase_allowance",
                "planning_cycle_allowance",
            }
            values = feed_overrides[str(item["feed_type"])]
            if set(values) - allowed or any(not np.isfinite(v) or v < 0 for v in values.values()):
                raise ValueError("Invalid economic or purchase allowance override")
            item.update(feed_overrides[str(item["feed_type"])])
    for ration in feed["rations"]:
        ration["feeds"] = [item for item in ration["feeds"] if item["feed_type"] not in (301, 302)]
        total = sum(item["ration_percentage"] for item in ration["feeds"])
        for item in ration["feeds"]:
            item["ration_percentage"] *= 100 / total
        if ration["animal_combination"] != "calf":
            ration["feeds"].extend(dict(feed_type=i, ration_percentage=0.0) for i in (1, 167, 231))
            if adult_feed_ids is not None:
                ration["feeds"] = [item for item in ration["feeds"] if item["feed_type"] in adult_feed_ids]
                if not ration["feeds"]:
                    raise ValueError("Every adult category needs available ingredients.")
                total = sum(item["ration_percentage"] for item in ration["feeds"])
                for item in ration["feeds"]:
                    item["ration_percentage"] = (
                        item["ration_percentage"] * 100 / total if total else 100 / len(ration["feeds"])
                    )
    for key, data in (("config", config), ("animal", animal), ("feed", feed)):
        path = target / f"{key}.json"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        metadata["files"][key]["path"] = path.as_posix()
    path = target / "metadata.json"
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return path


class RecordedSimulation(SimulationEngine):
    """Observe native consumption and purchases without performing stock deductions."""

    def __init__(self, target, days):
        self.target = target
        self.requested_days = days
        self.daily_records = []
        self.day_fed = dict(purchased={}, farmgrown={})
        self.day_bought = {}
        super().__init__(SimulationType.FULL_FARM)
        (target / "initial_state.json").write_text(
            json_text(
                dict(
                    inventory_kg_dm=self.feed_manager._query_available_feed_totals(
                        [f.rufas_id for f in self.available_feeds]
                    ),
                    animals=[
                        dict(
                            id=a.id,
                            category=a.animal_type.name,
                            weight=a.body_weight,
                            days_in_milk=a.days_in_milk,
                            days_in_pregnancy=a.days_in_pregnancy,
                        )
                        for a in self.herd_manager.all_animals
                    ],
                )
            ),
            encoding="utf-8",
        )
        original_request = self.feed_manager.manage_daily_feed_request
        original_purchase = self.feed_manager.purchase_feed

        def observe_request(*args, **kwargs):
            fulfilled, result = original_request(*args, **kwargs)
            for source in ("purchased", "farmgrown"):
                for key, value in getattr(result, source).items():
                    self.day_fed[source][key] = self.day_fed[source].get(key, 0.0) + value
            return fulfilled, result

        def observe_purchase(amounts, *args, **kwargs):
            before = self.feed_manager._query_available_feed_totals(list(amounts))
            result = original_purchase(amounts, *args, **kwargs)
            after = self.feed_manager._query_available_feed_totals(list(amounts))
            for key in amounts:
                self.day_bought[key] = self.day_bought.get(key, 0.0) + after[key] - before[key]
            return result

        self.feed_manager.manage_daily_feed_request = observe_request
        self.feed_manager.purchase_feed = observe_purchase

    def _advance_time(self):
        prices = {f.rufas_id: f.purchase_cost for f in self.available_feeds}
        feed_ids = list(prices)
        total_fed = {
            key: self.day_fed["purchased"].get(key, 0.0) + self.day_fed["farmgrown"].get(key, 0.0) for key in feed_ids
        }
        pens, events = [], []
        for pen in self.herd_manager.all_pens:
            optimizer = pen.ration_optimizer
            if hasattr(optimizer, "events"):
                events.extend(
                    event | {"pen_id": pen.id, "category": pen.animal_combination.value} for event in optimizer.events
                )
                optimizer.events.clear()
            if pen.is_populated:
                pens.append(
                    dict(
                        pen_id=pen.id,
                        category=pen.animal_combination.value,
                        population=len(pen.animals_in_pen),
                        ration=dict(pen.ration),
                        requirements=asdict(pen.average_nutrition_requirements),
                        supply=asdict(pen.average_nutrition_supply),
                        evaluation=asdict(pen.average_nutrition_evaluation),
                        approved=(
                            pen.average_nutrition_evaluation.is_valid_cow_ration
                            if pen.animal_combination.value == "lac_cow"
                            else pen.average_nutrition_evaluation.is_valid_heifer_ration
                        ),
                        evaluation_scope=(
                            "calf_native_reporting"
                            if pen.animal_combination.value == "calf"
                            else "native_adult_criteria"
                        ),
                        minerals=mineral_report(
                            np.array([float(pen.ration.get(f.rufas_id, 0.0)) for f in self.available_feeds]),
                            SimpleNamespace(feeds_used=self.available_feeds),
                        ),
                    )
                )
        inventory = self.feed_manager._query_available_feed_totals(feed_ids)
        if any(value < -1e-6 for value in inventory.values()):
            raise RuntimeError("Negative native inventory detected")
        record = dict(
            day=self.time.simulation_day,
            date=str(self.time.current_date.date()),
            pens=pens,
            formulations=events,
            fed_kg_dm=total_fed,
            sources_kg_dm=self.day_fed,
            bought_kg_dm=self.day_bought,
            inventory_kg_dm=inventory,
            estimated_diet_cost=sum(prices[key] * value for key, value in total_fed.items()),
            actual_purchase_expense=sum(prices[key] * value for key, value in self.day_bought.items()),
            milk_kg=float(self.herd_manager.herd_statistics.daily_milk_production),
            animal_count=len(self.herd_manager.all_animals),
            animals=[
                dict(
                    id=a.id,
                    category=a.animal_type.name,
                    body_weight=a.body_weight,
                    days_in_milk=a.days_in_milk,
                    days_in_pregnancy=a.days_in_pregnancy,
                )
                for a in self.herd_manager.all_animals
            ],
        )
        self.daily_records.append(record)
        with (self.target / "daily.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json_text(record).replace("\n", "") + "\n")
        self.day_fed = dict(purchased={}, farmgrown={})
        self.day_bought = {}
        progress = self.target / "progress.tmp"
        progress.write_text(
            json_text(dict(completed_days=len(self.daily_records), requested_days=self.requested_days)),
            encoding="utf-8",
        )
        progress.replace(self.target / "progress.json")
        super()._advance_time()


def run(
    target: Path,
    days: int,
    cows: int,
    seed: int,
    strategy="native_slsqp",
    fallback="native_slsqp",
    interval=1,
    feed_overrides=None,
    adult_feed_ids=None,
    mineral_policy="nrc2005_mtl",
):
    metadata = prepare(target, days, cows, strategy, fallback, interval, feed_overrides, adult_feed_ids, mineral_policy)
    om = OutputManager()
    om.run_startup_sequence(
        verbosity=LogVerbosity.ERRORS,
        exclude_info_maps=True,
        output_directory=target,
        clear_output_directory=False,
        chunkification=False,
        max_memory_usage_percent=0,
        max_memory_usage=0,
        save_chunk_threshold_call_count=0,
        variables_file_path=Path(""),
        output_prefix="annual",
        task_id="annual",
        is_end_to_end_testing_run=False,
    )
    TaskManager().check_dependencies()
    im = InputManager()
    if not im.start_data_processing(metadata, Path(""), "annual", None):
        om.dump_all_nondata_pools(target / "logs", True, "block")
        raise ValueError("Input validation failed. Inspect run logs.")
    random.seed(seed)
    np.random.seed(seed)
    (target / "effective_inputs.json").write_text(
        json_text(
            dict(
                config=im.get_data("config"),
                herd_information=im.get_data("animal.herd_information"),
                ration=im.get_data("animal.ration"),
                feed=im.get_data("feed"),
                seed=seed,
                economics="Illustrative monetary units per kg dry matter; no market quotation",
            )
        ),
        encoding="utf-8",
    )
    HerdFactory(False, False).initialize_herd()
    start = perf_counter()
    try:
        engine = RecordedSimulation(target, days)
        engine.simulate()
    except Exception as error:
        progress_path = target / "progress.json"
        progress = json.loads(progress_path.read_text()) if progress_path.exists() else {"completed_days": 0}
        failure = dict(
            status="failed",
            error=str(error),
            progress=progress,
            traceback=traceback.format_exc().replace(str(Path.cwd()), "<repository>"),
            formulations=(
                [event for pen in engine.herd_manager.all_pens for event in getattr(pen.ration_optimizer, "events", [])]
                if "engine" in locals()
                else []
            ),
        )
        if "engine" in locals():
            grown, purchased = engine.feed_manager._gather_available_feeds_by_id()
            failure["remaining_storage_batches_kg_dm"] = {
                source: {key: [float(s.dry_matter_mass) for s in batches] for key, batches in collection.items()}
                for source, collection in (("farmgrown", grown), ("purchased", purchased))
            }
        (target / "summary.json").write_text(json_text(failure), encoding="utf-8")
        raise
    records = engine.daily_records
    events = [event for row in records for event in row["formulations"]]
    cost = sum(row["estimated_diet_cost"] for row in records)
    milk = sum(row["milk_kg"] for row in records)
    animal_days = sum(row["animal_count"] for row in records)
    summary = dict(
        days=days,
        simulated_days=engine.time.simulation_day,
        cows_initial=cows,
        seed=seed,
        elapsed_seconds=perf_counter() - start,
        status="complete",
        strategy=strategy,
        estimated_diet_cost=cost,
        milk_kg=milk,
        animal_days=animal_days,
        cost_per_animal_day=cost / animal_days if animal_days else None,
        cost_per_kg_milk=cost / milk if milk else None,
        purchase_expense=sum(row["actual_purchase_expense"] for row in records),
        highs_attempts=sum(e["used"] == "linear_highs" for e in events),
        highs_accepted=sum(e["used"] == "linear_highs" and e["success"] for e in events),
        native_attempts=sum(e["used"] == "native_slsqp" for e in events),
        unsupported_native=sum(e["reason"] == "unsupported_category_or_standard" for e in events),
        fallbacks=sum(e["reason"] == "highs_failure_or_native_rejection" for e in events),
        **git_context(),
    )
    (target / "summary.json").write_text(json_text(summary), encoding="utf-8")
    print(summary)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, choices=range(1, 366), default=1)
    parser.add_argument("--cows", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output")
    parser.add_argument(
        "--strategy",
        choices=["native_slsqp", "linear_highs", "linear_highs_all", "linear_highs_exclusive"],
        default="native_slsqp",
    )
    parser.add_argument("--mineral-policy", choices=["native", "nrc2005_mtl"], default="nrc2005_mtl")
    parser.add_argument("--fallback", choices=["native_slsqp", "fail"], default="native_slsqp")
    parser.add_argument("--interval", type=int, default=1)
    parser.add_argument("--feed-overrides", help="JSON file mapping feed IDs to native economic/allowance fields")
    parser.add_argument(
        "--adult-feed-ids", help="Comma-separated eligible adult feed IDs; defaults preserve the scenario"
    )
    args = parser.parse_args()
    overrides = json.loads(Path(args.feed_overrides).read_text(encoding="utf-8")) if args.feed_overrides else None
    run(
        Path(args.output or f"output/annual/{uuid4().hex}"),
        args.days,
        args.cows,
        args.seed,
        args.strategy,
        args.fallback,
        args.interval,
        overrides,
        [int(value) for value in args.adult_feed_ids.split(",")] if args.adult_feed_ids else None,
        args.mineral_policy,
    )


if __name__ == "__main__":
    main()
