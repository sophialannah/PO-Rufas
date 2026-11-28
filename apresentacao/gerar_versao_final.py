"""Generate the current four-slide academic deck without replacing historical decks."""

import argparse
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

SLIDES = [
    (
        "PO-RuFaS: integração dinâmica",
        [
            "Pesquisa Operacional aplicada à formulação de dietas no RuFaS NRC",
            "365 dias FULL_FARM: requisitos, animais, consumo, compras e estoque reais",
            "LP estático preservado; programação linear sequencial no ciclo diário",
            "Sophia Lannah Beatriz Ferreira de Sousa",
            "Anderson Alberto da Costa Silva",
        ],
    ),
    (
        "Modelo e arquitetura",
        [
            "Estático: coeficientes fixos, variáveis kg MN, metas explícitas",
            "Dinâmico: funções nativas por categoria → LPs locais HiGHS → verificação original",
            "HerdManager → Pen → formulação → FeedManager → baixa física",
            "Requisitos NRC 2001; tetos totais Ca/P NRC 2005 comuns aos solvers",
            "Exclusivo: falha explícita, sem fallback SLSQP; bezerros seguem rotina própria",
        ],
    ),
    (
        "Resultado anual controlado",
        [
            "SLSQP: 2.319,34875854 UM | HiGHS exclusivo: 2.316,45106770 UM",
            "Redução: 0,1249355% — preços demonstrativos, cenário específico",
            "Leite: 140.223,666523 kg em ambas as estratégias",
            "1.002 formulações HiGHS; zero chamadas SLSQP no exclusivo",
            "959 convergentes; 43 soluções viáveis sem convergência",
        ],
    ),
    (
        "Validação e limites",
        [
            "954 testes aprovados; reprodução em cópia isolada e venv nova",
            "998 curral-dias ADULTOS aprovados no HiGHS",
            "252 curral-dias de BEZERROS não aprovados em cada estratégia",
            "Sem certificado de ótimo global não linear ou superioridade econômica universal",
            "Limites: indicadores de bezerros, absorção mineral e resposta biológica",
        ],
    ),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="apresentacao/apresentacao_po_rufas_final.pptx")
    target = Path(parser.parse_args().output)
    if target.exists():
        raise FileExistsError("Choose a new name; preserve the previous deck")
    presentation = Presentation()
    presentation.slide_width, presentation.slide_height = Inches(13.333), Inches(7.5)
    for number, (title, lines) in enumerate(SLIDES, 1):
        slide = presentation.slides.add_slide(presentation.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = RGBColor(17, 35, 47)
        heading = slide.shapes.add_textbox(Inches(0.7), Inches(0.55), Inches(12), Inches(0.8)).text_frame
        heading.text = title
        heading.paragraphs[0].font.size = Pt(32)
        heading.paragraphs[0].font.bold = True
        heading.paragraphs[0].font.color.rgb = RGBColor(100, 222, 188)
        body = slide.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.7), Inches(4.8)).text_frame
        body.word_wrap = True
        for index, line in enumerate(lines):
            p = body.paragraphs[0] if index == 0 else body.add_paragraph()
            p.text = line
            p.font.size, p.space_after = Pt(23), Pt(24)
            p.font.color.rgb = RGBColor(240, 245, 248)
        footer = slide.shapes.add_textbox(Inches(0.8), Inches(7), Inches(11), Inches(0.3)).text_frame
        footer.text = f"PO-RuFaS · versão acadêmica 27/11/2026 · {number}/4 · evidências no repositório"
        footer.paragraphs[0].font.size = Pt(12)
        footer.paragraphs[0].font.color.rgb = RGBColor(180, 200, 210)
    target.parent.mkdir(parents=True, exist_ok=True)
    presentation.save(target)
    print(target)


if __name__ == "__main__":
    main()
