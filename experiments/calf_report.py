"""Read-only audit of native calf reporting; never changes native approval flags."""

from collections import Counter
import csv
import json
from pathlib import Path


def main():
    root = Path("evidencias/correcao_dinamica")
    target = Path("evidencias/publicacao")
    target.mkdir(parents=True, exist_ok=True)
    records, summary = [], {}
    for strategy, folder in (
        ("native_slsqp", "nativo_final_365"),
        ("linear_highs_all", "hibrido_final_365"),
        ("linear_highs_exclusive", "exclusivo_estoque_365"),
    ):
        counts, total, rejected = Counter(), 0, 0
        for line in (root / folder / "daily.jsonl").read_text(encoding="utf-8").splitlines():
            day = json.loads(line)
            for pen in day["pens"]:
                if pen["category"] != "calf":
                    continue
                total += 1
                rejected += not pen["approved"]
                for field, value in pen["evaluation"].items():
                    if value is None:
                        continue
                    clamped = field in {"ndf_percent", "metabolizable_protein", "dry_matter"}
                    bad = value != 0 if clamped else value < (-1e-9 if field == "fat_percent" else 0)
                    if bad:
                        counts[field] += 1
                        records.append(
                            dict(
                                strategy=strategy,
                                day=day["day"],
                                pen=pen["pen_id"],
                                field=field,
                                delta=value,
                                native_approved=pen["approved"],
                                scope=pen["evaluation_scope"],
                            )
                        )
        summary[strategy] = dict(calf_pen_days=total, native_not_approved=rejected, failed_fields=dict(counts))
    (target / "bezerros_auditoria.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (target / "bezerros_criterios.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
