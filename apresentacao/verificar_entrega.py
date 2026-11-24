"""Validate the final presentation artifacts; does not replace visual or oral rehearsal."""

import hashlib
import json
from pathlib import Path
import re

from pptx import Presentation
from pypdf import PdfReader

from apresentacao.conteudo import ANDERSON, SOPHIA, STAGES, QA

HERE = Path(__file__).resolve().parent


def main() -> None:
    required = [
        "apresentacao_rufas_5min.pptx",
        "apresentacao_rufas_5min.pdf",
        "roteiro_sophia.md",
        "roteiro_anderson.md",
        "roteiro_completo.md",
        "perguntas_e_respostas.md",
        "guia_demonstracao.md",
        "demonstracao_solver.bat",
        "resultados_validados.md",
        "checklist_apresentacao.md",
        "cartoes_consulta.md",
        "simulacao_arguicao.md",
    ]
    for name in required:
        assert (HERE / name).is_file(), name
    for path in HERE.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        assert not any(ord(c) < 32 and c not in "\n\r\t" for c in content), path
        if path.parent == HERE:
            assert SOPHIA in content and ANDERSON in content, path
        for link in re.findall(r"\]\(([^)]+)\)", content):
            if "://" not in link and not link.startswith("#"):
                assert (path.parent / link.split("#")[0]).exists(), (path, link)
    assert sum(stage[2] for stage in STAGES) == 300
    assert [stage[2] for stage in STAGES] == [45, 60, 75, 35, 50, 35]
    assert len(QA) >= 25
    prs = Presentation(HERE / "apresentacao_rufas_5min.pptx")
    assert len(prs.slides) == 4
    assert abs(prs.slide_width / prs.slide_height - 16 / 9) < 1e-5
    text = "\n".join(s.text for slide in prs.slides for s in slide.shapes if s.has_text_frame)
    assert SOPHIA in text and ANDERSON in text
    assert "34,9978" in text and "433" in text
    for slide in prs.slides:
        assert slide.has_notes_slide
        assert slide.notes_slide.notes_text_frame.text.strip()
    pdf = PdfReader(HERE / "apresentacao_rufas_5min.pdf")
    assert len(pdf.pages) == 4
    pdf_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    assert SOPHIA in pdf_text and ANDERSON in pdf_text
    assert "34,9978" in pdf_text
    native = json.loads((HERE / "evidencias/verificacao_powerpoint.json").read_text(encoding="utf-8-sig"))
    assert native["opened"] and native["slides"] == 4 and not native["text_overflow_candidates"]
    demo = json.loads((HERE / "evidencias/base_slides.json").read_text(encoding="utf-8"))
    assert demo["result"]["status"] == "optimal"
    assert len(demo["result"]["checks"]) == 11
    assert all(c["satisfied"] for c in demo["result"]["checks"])
    assert abs(demo["result"]["cost_per_day"] - demo["independent_cost"]) < 1e-9
    manifest = dict(
        checks_passed=True,
        slides=4,
        editable_pptx=True,
        pdf_pages=4,
        powerpoint_open_verified=True,
        planned_seconds=600,
        presentation_seconds=300,
        questions_seconds=300,
        oral_rehearsal_performed=False,
        projector_checked=False,
        qa_count=len(QA),
        cost=demo["result"]["cost_per_day"],
        artifacts={
            name: {
                "bytes": (HERE / name).stat().st_size,
                "sha256": hashlib.sha256((HERE / name).read_bytes()).hexdigest(),
            }
            for name in required
        },
    )
    (HERE / "evidencias/entrega_verificada.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Entrega verificada: 4 slides editaveis, PDF 4 paginas, nomes, resultados, links e cronograma OK.")
    print("Ensaio oral e projetor: pendentes da dupla.")


if __name__ == "__main__":
    main()
