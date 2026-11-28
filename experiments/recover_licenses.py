"""Recover only license files from the audited upstream candidate, without overwrite."""

import hashlib
import json
from pathlib import Path
import urllib.request

REVISION = "d471c742eadc2e37b76545d0d0f0d10b6c9ef763"


def main():
    records = []
    tree = json.loads(Path("output/annual/upstream_audit/tree.json").read_text(encoding="utf-8"))
    entries = {e["path"]: e for e in tree["tree"]}
    for name in ("COPYING.txt", "COPYING.LESSER.txt"):
        destination = Path(name)
        url = f"https://raw.githubusercontent.com/RuminantFarmSystems/RuFaS/{REVISION}/{name}"
        data = urllib.request.urlopen(url, timeout=30).read()
        git_hash = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert git_hash == entries[name]["sha"], name
        if destination.exists():
            assert destination.read_bytes() == data, "Preserve differing existing license"
        else:
            destination.write_bytes(data)
        records.append(dict(path=name, url=url, git_blob=git_hash, sha256=hashlib.sha256(data).hexdigest()))
    Path("evidencias/correcao_dinamica/licencas_recuperadas.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )
    others = {}
    directory = Path("evidencias/correcao_dinamica/ausentes_upstream")
    directory.mkdir(exist_ok=True)
    for name in (
        ".github/workflows/combined_format_lint_test_mypy.yml",
        "helpful_scripts/herd_inputs_calculator/herd_inputs_calculator.py",
        "output/output_filters/.keep",
        "output/output_filters/_csv_all_variables.txt",
    ):
        url = f"https://raw.githubusercontent.com/RuminantFarmSystems/RuFaS/{REVISION}/{name}"
        data = urllib.request.urlopen(url, timeout=30).read()
        git_hash = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert git_hash == entries[name]["sha"]
        target = directory / (name.replace("/", "__") + ".txt")
        target.write_bytes(data)
        others[name] = dict(url=url, git_blob=git_hash, audit_copy=target.as_posix(), installed_in_original_path=False)
    (directory / "manifesto.json").write_text(json.dumps(others, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
