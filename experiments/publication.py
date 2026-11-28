"""Audit and export the reviewable worktree without Git metadata, caches or secrets.

Read-only with respect to Git: never stages, commits, pushes, or deletes files.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "evidencias/publicacao"
CATALOGS = {"evidencias/publicacao/candidato_inventario.json", "evidencias/publicacao/candidato_arquivos.csv"}
PATTERNS = [rb"AKIA[0-9A-Z]{16}", rb"gh[pousr]_[A-Za-z0-9]{30,}", rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"]


def candidate_files():
    result = subprocess.check_output(["git", "ls-files", "-c", "-o", "--exclude-standard", "-z"], cwd=ROOT)
    files = sorted({p.decode("utf-8") for p in result.split(b"\0") if p})
    records, findings = [], []
    for name in files:
        if name in CATALOGS:
            continue  # A self-describing catalog cannot include its own content hash.
        path = ROOT / name
        if not path.is_file():
            continue
        parts = path.relative_to(ROOT).parts
        if (
            any(p in {".git", "__pycache__", ".pytest_cache", ".venv", ".venv-python", "node_modules"} for p in parts)
            or path.suffix == ".pyc"
        ):
            raise ValueError(f"Generated/private file in candidate: {name}")
        data = path.read_bytes()
        if len(data) >= 100 * 1024 * 1024:
            raise ValueError(f"File exceeds GitHub 100 MiB limit: {name}")
        if b"\0" not in data[:8192]:
            for pattern in PATTERNS:
                if re.search(pattern, data):
                    findings.append(name)
        records.append(dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    if findings:
        raise ValueError(f"Review credential-pattern matches (values suppressed): {sorted(set(findings))}")
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="New isolated source directory; defaults to system temp outside original repo")
    args = parser.parse_args()
    destination = (
        Path(args.output) if args.output else Path(tempfile.gettempdir()) / ("PO-RuFaS-publicacao-" + uuid4().hex[:10])
    )
    destination = destination.resolve()
    if destination.is_relative_to(ROOT):
        raise ValueError("Isolation must be outside the original repository")
    destination.mkdir(parents=True, exist_ok=False)
    records = candidate_files()
    for row in records:
        target = destination / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / row["path"], target)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == row["sha256"]
    manifest = dict(
        branch=subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        scope="Current tracked and untracked nonignored worktree files, excluding the two self-describing catalogs from their own hashes; no commit/staging performed",
        files=records,
        total_bytes=sum(r["bytes"] for r in records),
    )
    (destination / "PUBLICATION_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    REPORT.mkdir(parents=True, exist_ok=True)
    (REPORT / "candidato_inventario.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (REPORT / "candidato_arquivos.csv").write_text(
        "path,bytes,sha256\n" + "\n".join(f"{r['path']},{r['bytes']},{r['sha256']}" for r in records) + "\n",
        encoding="utf-8",
    )
    for name in CATALOGS:
        catalog = destination / name
        catalog.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, catalog)
    # Absolute local path is only in ignored output, not the publication report.
    (ROOT / "output").mkdir(exist_ok=True)
    (ROOT / "output/publication_location.json").write_text(json.dumps(dict(path=str(destination))), encoding="utf-8")
    print(json.dumps(dict(path=str(destination), files=len(records), bytes=manifest["total_bytes"])))


if __name__ == "__main__":
    main()
