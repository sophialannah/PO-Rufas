"""Produce auditable annual tables and plots from completed native-loop journals."""

import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from experiments.comparison import json_text


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="evidencias/anual")
    args = parser.parse_args()
    target = Path(args.root)
    summaries = []
    tables = {}
    for strategy in ("native_slsqp", "linear_highs"):
        folder = target / f"{strategy}_365"
        summary = json.loads((folder / "summary.json").read_text())
        records = [json.loads(line) for line in (folder / "daily.jsonl").read_text(encoding="utf-8").splitlines()]
        assert len(records) == summary["simulated_days"] == 365
        assert all(r["day"] == day for day, r in enumerate(records))
        rows = []
        for r in records:
            rows.append(
                dict(
                    day=r["day"],
                    date=r["date"],
                    diet_cost=r["estimated_diet_cost"],
                    purchase_expense=r["actual_purchase_expense"],
                    milk=r["milk_kg"],
                    dry_matter=sum(r["fed_kg_dm"].values()),
                    inventory=sum(r["inventory_kg_dm"].values()),
                    animals=r["animal_count"],
                    approved_pens=sum(bool(p["approved"]) for p in r["pens"] if p["category"] != "calf"),
                    rejected_pens=sum(not bool(p["approved"]) for p in r["pens"] if p["category"] != "calf"),
                )
            )
        frame = pd.DataFrame(rows).set_index("day")
        frame["accumulated_cost"] = frame["diet_cost"].cumsum()
        frame.to_csv(folder / "daily.csv")
        tables[strategy] = frame
        summaries.append(summary)
        pd.DataFrame([r["fed_kg_dm"] for r in records]).fillna(0).plot.area(figsize=(11, 5))
        plt.xlabel("Dia")
        plt.ylabel("Consumo fornecido (kg MS/rebanho/dia)")
        plt.tight_layout()
        plt.savefig(folder / "ingredientes.png", dpi=150)
        plt.close()
    pd.DataFrame(summaries).to_csv(target / "resumo.csv", index=False)
    for column, label in (
        ("diet_cost", "Custo estimado da dieta (UM/dia)"),
        ("accumulated_cost", "Custo acumulado (UM)"),
        ("milk", "Leite (kg/dia)"),
        ("dry_matter", "MS fornecida (kg/dia)"),
        ("inventory", "Estoque (kg MS)"),
        ("rejected_pens", "Currais reprovados por dia"),
    ):
        pd.DataFrame({name: frame[column] for name, frame in tables.items()}).plot(figsize=(10, 4))
        plt.xlabel("Dia")
        plt.ylabel(label)
        plt.tight_layout()
        plt.savefig(target / f"{column}.png", dpi=150)
        plt.close()
    baseline, alternative = summaries
    comparison = dict(
        food_cost_reduction_percent=100
        * (baseline["estimated_diet_cost"] - alternative["estimated_diet_cost"])
        / baseline["estimated_diet_cost"],
        milk_difference_kg=alternative["milk_kg"] - baseline["milk_kg"],
        scope="Hybrid strategy; feed consumption valued at scenario purchase prices, distinct from purchase expense",
    )
    (target / "comparacao.json").write_text(json_text(comparison), encoding="utf-8")
    inventory_path = Path("output/annual/upstream_audit/tree.json")
    if inventory_path.exists():
        upstream = {
            item["path"]: item["sha"]
            for item in json.loads(inventory_path.read_text(encoding="utf-8-sig"))["tree"]
            if item["type"] == "blob"
        }
        tree = subprocess.check_output(["git", "ls-tree", "-r", "-z", "b297245"])
        original = {}
        for entry in tree.split(b"\0"):
            if entry:
                left, name = entry.split(b"\t", 1)
                original[name.decode("utf-8")] = left.decode().split()[2]
        shared = upstream.keys() & original.keys()
        original_audit = dict(
            upstream_candidate="d471c742eadc2e37b76545d0d0f0d10b6c9ef763",
            upstream_identity="Temporal candidate preceding initial local commit; ancestry absent from local git",
            local_initial="b297245960c5820c2d1d8d3d16c2cead456b3a2c",
            matching=sum(original[p] == upstream[p] for p in shared),
            shared=len(shared),
            absent=sorted(upstream.keys() - original.keys()),
            changed=sorted(p for p in shared if upstream[p] != original[p]),
            rufas_source_matches=all(original[p] == upstream[p] for p in shared if p.startswith("RUFAS/")),
        )
        (target / "auditoria_upstream.json").write_text(json_text(original_audit), encoding="utf-8")
    metadata = json.loads((target / "native_slsqp_365/metadata.json").read_text())
    paths = {key: value["path"] for key, value in metadata["files"].items()}
    audit = dict(
        metadata_files={
            key: dict(
                path=path,
                present=Path(path).exists(),
                sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).exists() else None,
            )
            for key, path in paths.items()
        },
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        branch=subprocess.check_output(["git", "branch", "--show-current"], text=True).strip(),
        submodules=subprocess.check_output(["git", "submodule", "status"], text=True).strip(),
        modified=subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines(),
    )
    (target / "auditoria_local.json").write_text(json_text(audit), encoding="utf-8")
    tests = target / "testes.xml"
    if tests.exists():
        tree = ET.parse(tests)
        for node in tree.iter():
            node.attrib.pop("hostname", None)
        tree.write(tests, encoding="utf-8", xml_declaration=True)
    print(json_text(dict(summaries=summaries, comparison=comparison)))


if __name__ == "__main__":
    main()
