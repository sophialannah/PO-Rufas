"""Apply the verified integration demo to existing presentation assets, preserving layout."""

import json
from pathlib import Path
from pptx import Presentation

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def replace_text(text, replacements):
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def update_slide(slide, replacements, note):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.text = replace_text(run.text, replacements)
    notes = replace_text(slide.notes_slide.notes_text_frame.text, replacements)
    if note not in notes:
        notes += "\n" + note
    slide.notes_slide.notes_text_frame.text = notes


def main():
    report = json.loads((ROOT / "output/integracao_real.json").read_text(encoding="utf-8"))
    assert report["result"]["status"] == "optimal" and report["native_return"]
    assert "native_evaluation" in report["native_return"]
    cost = f"{report['result']['cost_per_day']:.4f}".replace(".", ",")
    cost_full = f"{report['result']['cost_per_day']:.10f}".replace(".", ",")
    note = (
        "Integração comprovada: Animal 98605 construído de animal_population.json → cálculo NRC → "
        "lista NRCFeed/Ingredient → HiGHS → percentuais MS → RationManager → FeedInRation → "
        "NutritionSupplyCalculator e NutritionEvaluator. "
        "DEL 100, leite 30 kg/dia assumido. DMI calculada; PB/NEL/FDN externas; déficit diagnóstico "
        "de P absorvível (-6,68 g/dia) sem suplemento mineral no LP. "
        "O ciclo diário da fazenda não foi executado. Demo: demonstracao_integrada.bat. "
        "5 minutos de apresentação + 5 minutos adicionais de perguntas."
    )
    replacements = {
        "650 kg": "627,56 kg",
        "650 quilos": "627,56 quilos",
        "650 kg;": "627,56 kg;",
        "34,9977736422": cost_full,
        "34,9978": cost,
        "433 testes": "442 testes",
        "440 testes": "442 testes",
        "433 casos": "442 casos",
        "433 ": "442 ",
        "440 ": "442 ",
        "33 testes específicos": "42 testes específicos",
        "33 específicos": "42 específicos",
        "22,55": "22,23",
        "22,5453": "22,2316",
        "6,7546": "6,4120",
        "29,96%": "28,84%",
        "15,91": "14,83",
        "9,10": "9,53",
        "0,18": "0,50",
        "demonstracao_solver.bat": "demonstracao_integrada.bat",
        "-m apresentacao.demo_solver": "-m RUFAS.biophysical.animal.ration.linear_diet_integrated_example",
        "apresentacao/evidencias/demo_resultado.json": "output/integracao_real.json (cópia em apresentacao/evidencias/integracao_real.json)",
        "Reutiliza `example_inputs()` e\n`optimize_diet()` existentes.": "Reutiliza `demo_inputs()`, `Animal`, `NRCFeed`, `optimize_animal_ration()` e `RationManager`.",
        "A demonstração recebe um perfil, não instancia nem executa uma fazenda inteira.":
            "A demonstração instancia o Animal 98605 real, mas não executa o ciclo diário completo da fazenda.",
        "Integração modular testada.": "Retorno ao RationManager testado.",
        "Adaptadores RuFaS\nConversão MN ↔ MS\nSciPy • linprog / HiGHS":
            "Animal → cálculo NRC\nConversão MN ↔ MS\nSciPy • linprog / HiGHS",
        "Quantidades por alimento\nCusto diário mínimo\nRestrições verificadas":
            "Dieta → RationManager\nCusto diário mínimo\nOferta PB/FDN conferida",
        "Usamos objetos Feed e NutritionRequirements, biblioteca de composição e calculador NRC existentes. Há um adaptador de Animal e saída em kg de MS compatível com rações. Ainda não aplicamos a dieta automaticamente à simulação diária.":
            "Construímos o Animal 98605 real a partir de animal_population.json, calculamos exigências NRC, convertemos NRCFeed em Ingredient, otimizamos no HiGHS, convertemos a dieta para % de MS e a enviamos ao RationManager, conferindo a oferta via NutritionSupplyCalculator e NutritionEvaluator. Ainda não aplicamos a dieta automaticamente ao ciclo diário da fazenda.",
        "Executamos 442 testes dos componentes relacionados, incluindo 42 testes específicos do novo trabalho. Há casos com solução conhecida, conversões, limites, inviabilidade e integração. O exemplo também confere as onze restrições após o solver.":
            "Executamos 442 testes dos componentes relacionados, incluindo 42 testes específicos do novo trabalho. Há casos com solução conhecida, conversões, limites, inviabilidade e integração ponta a ponta sem mocks com Animal, NRCFeed, RationManager e NutritionSupplyCalculator. O exemplo também confere as onze restrições após o solver.",
    }
    prs = Presentation(HERE / "apresentacao_rufas_5min.pptx")
    for slide in prs.slides:
        update_slide(slide, replacements, note)
    table = next(s.table for s in prs.slides[3].shapes if s.has_table)
    ids = [1, 44, 167]
    for row, identifier in enumerate(ids, 1):
        for col, value in [
            (1, report["result"]["quantities_kg_day"][str(identifier)]),
            (2, report["result"]["costs_per_day"][str(identifier)]),
        ]:
            cell = table.cell(row, col)
            cell.text_frame.paragraphs[0].runs[0].text = f"{value:.4f}".replace(".", ",")
    prs.save(HERE / "apresentacao_rufas_5min.pptx")
    for name in (
        "roteiro_completo.md",
        "roteiro_sophia.md",
        "roteiro_anderson.md",
        "cartoes_consulta.md",
        "guia_demonstracao.md",
        "checklist_apresentacao.md",
        "perguntas_e_respostas.md",
        "simulacao_arguicao.md",
    ):
        path = HERE / name
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        text = text.split("\n\n## Integração comprovada nesta versão")[0]
        text += "\n\n## Integração comprovada nesta versão\n\n" + note + "\n\n"
        text += "Resultado: R$ " + cost + "/dia. Relatório: [integração real](../docs/integracao_real_rufas.md).\n"
        path.write_text(text, encoding="utf-8")
    (HERE / "evidencias/integracao_real.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
