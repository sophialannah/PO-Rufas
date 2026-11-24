"""Re-run presentation evidence and related existing tests, preserving source modules."""

from datetime import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def public_text(value: str) -> str:
    """Keep evidence portable without exposing the local account/workspace path."""
    return value.replace(str(ROOT), ".").replace(ROOT.as_posix(), ".")


def run(name: str, arguments: list[str]) -> dict:
    start = perf_counter()
    command = [sys.executable, *arguments]
    process = subprocess.run(command, cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace")
    elapsed = perf_counter() - start
    (HERE / f"evidencias/{name}.md").write_text(
        f"# Execução: {name}\n\nComando: `{public_text(subprocess.list2cmdline(command))}`\n\n"
        f"Código de saída: {process.returncode}; duração: {elapsed:.3f} s.\n\n"
        f"```text\n{public_text(process.stdout)}\n{public_text(process.stderr)}\n```\n",
        encoding="utf-8",
    )
    if process.returncode:
        raise RuntimeError(f"{name} failed; read apresentacao/evidencias/{name}.md")
    print(f"{name}: OK ({elapsed:.3f} s)")
    return {
        "name": name,
        "command": [public_text(arg) for arg in command],
        "exit_code": process.returncode,
        "seconds": elapsed,
    }


def main() -> None:
    (HERE / "evidencias").mkdir(exist_ok=True)
    commands = [run("demo_terminal", ["-X", "utf8", "-m", "apresentacao.demo_solver", "--auto"])]
    commands.append(
        run(
            "testes",
            [
                "-X",
                "utf8",
                "-m",
                "pytest",
                "tests/test_biophysical/test_animal/test_ration",
                "tests/test_biophysical/test_animal/test_nutrients",
                "tests/test_biophysical/test_animal/test_data_types/test_nutrition_data_structures.py",
                "-q",
                "--junitxml=apresentacao/evidencias/testes.xml",
            ],
        )
    )
    commands.append(
        run(
            "catalogo",
            [
                "-X",
                "utf8",
                "-m",
                "RUFAS.biophysical.animal.ration.linear_diet_catalog",
                "--demo",
                "--seed",
                "42",
                "--output-dir",
                "apresentacao/evidencias/catalogo",
            ],
        )
    )
    test_tree = ET.parse(HERE / "evidencias/testes.xml")
    suite = test_tree.getroot()
    for test_suite in suite.iter("testsuite"):
        test_suite.attrib.pop("hostname", None)
    test_tree.write(HERE / "evidencias/testes.xml", encoding="utf-8", xml_declaration=True)
    counts = {
        key: sum(int(s.attrib.get(key, 0)) for s in suite.iter("testsuite"))
        for key in ("tests", "failures", "errors", "skipped")
    }
    paths = list((ROOT / "RUFAS/biophysical/animal/ration").glob("linear_diet*.py"))
    paths += [ROOT / "input/data/feed/NRC_comp.csv", HERE / "demo_solver.py"]
    report = dict(
        executed_at=datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(),
        python=sys.version,
        versions={name: importlib.metadata.version(name) for name in ("numpy", "scipy", "pytest", "python-pptx")},
        commands=commands,
        test_counts=counts,
        sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    )
    (HERE / "evidencias/validacao.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(counts)


if __name__ == "__main__":
    main()
