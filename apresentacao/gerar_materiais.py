"""Build the editable four-slide deck and Portuguese guides from verified evidence.

Requires python-pptx only for authoring, not for the live optimizer demo.
Run after: python -m apresentacao.validar_projeto
"""

from datetime import datetime
import json
from pathlib import Path
import re

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from pptx.util import Inches, Pt

from apresentacao.conteudo import ANDERSON, SOPHIA, STAGES, CARDS, QA

HERE = Path(__file__).resolve().parent
NAVY = "172E3B"
GREEN = "126B5B"
GOLD = "BD842C"
PAPER = "F5F4EF"
MUTED = "52646C"
PALE = "E5EEE8"
WHITE = "FFFFFF"


def pt_number(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def stamp(seconds: int) -> str:
    return f"{seconds // 60:02}:{seconds % 60:02}"


def write(name: str, text: str) -> None:
    (HERE / name).write_text(text.strip() + "\n", encoding="utf-8")


def guides(demo: dict, validation: dict) -> None:
    names = f"**Integrantes:** {SOPHIA} e {ANDERSON}."
    timing = ["| Intervalo | Etapa | Responsável | Duração |", "|---|---|---|---:|"]
    clock = 0
    sections = []
    for index, (title, speaker, seconds, speech) in enumerate(STAGES):
        interval = f"{stamp(clock)}–{stamp(clock + seconds)}"
        timing.append(f"| {interval} | {title} | {speaker} | {seconds} s |")
        sections.append(
            f"## {interval} — {title}\n\n**{speaker} — {seconds} segundos**\n\n"
            f"> {speech}\n\n**Cartão:** {CARDS[index]}\n"
        )
        clock += seconds
    assert clock == 300
    timing.append("| 05:00–10:00 | Perguntas | Ambos | 300 s |")
    table = "\n".join(timing)
    instructions = (
        "São cinco minutos exclusivos de apresentação, seguidos de cinco minutos de arguição: "
        "a demonstração tem **85 segundos**, divididos em 35 + 50. São **300 segundos de exposição "
        "+ 300 segundos adicionais de perguntas = 600 segundos**.\n\n"
        "Use um cronômetro visível. As durações são metas de ensaio, não uma medição das vozes dos integrantes. "
        "Ensaie as falas com pausas para respiração, troca de janela e execução. Ajuste o ritmo "
        "sem omitir as limitações. Às 05:00, encerre a exposição; às 10:00, encerre as perguntas.\n\n"
        "Sequência: slides 1 → 2 → 3 → Alt+Tab para o terminal → Enter para resolver → "
        "Alt+Tab de volta → slide 4. Não há quinto slide. O terminal deve estar preparado antes da contagem. "
        "Sophia: 155 s (2min35s); Anderson: 145 s (2min25s)."
    )
    write(
        "roteiro_completo.md",
        f"# Roteiro completo — 5 minutos de apresentação + 5 de arguição\n\n{names}\n\n{table}\n\n{instructions}\n\n"
        + "\n".join(sections)
        + "\n## 05:00–10:00 — perguntas\n\n"
        "Sophia inicia respostas de modelagem; Anderson, de integração e validação. "
        "Cada resposta deve durar 15–35 segundos. O banco de perguntas serve para estudo; "
        "não se pretende responder todas as perguntas nos cinco minutos adicionais.\n",
    )
    for person, filename in [(SOPHIA, "roteiro_sophia.md"), (ANDERSON, "roteiro_anderson.md")]:
        selected = [section for section, stage in zip(sections, STAGES) if stage[1] == person]
        write(
            filename,
            f"# Roteiro individual — {person}\n\n{names}\n\n{instructions}\n\n"
            + "\n".join(selected)
            + "\n## Perguntas\n\n"
            + (
                "Priorize função objetivo, unidades, variáveis, restrições, linearidade e solver."
                if person == SOPHIA
                else "Priorize arquitetura, dados, integração, resultados, testes e limitações."
            )
            + " Ambos devem estudar o roteiro completo e o banco de perguntas.\n",
        )
    write(
        "cartoes_consulta.md",
        f"# Cartões de consulta\n\n{names}\n\n"
        + "\n\n".join(
            f"**{title} — {seconds}s — {speaker.split()[0]}**\n\n{card}"
            for (title, speaker, seconds, _), card in zip(STAGES, CARDS)
        )
        + "\n\n**05:00: encerrar a apresentação e iniciar perguntas. 10:00: encerrar a arguição.**\n"
        "\nNúmeros-chave: 650 kg; DEL 100; leite 30 kg/dia; MS 22,5453; PB mínima 3,6; "
        "NEL mínima 35; FDN 28–40%; R$ 34,9978/dia; 11 verificações; 433 testes.\n",
    )
    groups = [
        ("Básicas", [1, 2, 3, 4, 5, 9]),
        ("Intermediárias", [6, 7, 10, 13, 14, 17, 23]),
        ("Avançadas", [8, 11, 15, 16, 22, 25, 26]),
        ("Críticas sobre limitações", [12, 18, 19, 20, 21, 24, 27]),
    ]
    questions = []
    for group, indices in groups:
        questions.append(f"## {group}")
        for index in indices:
            question, person, answer = QA[index - 1]
            questions.append(f"### {index}. {question}\n\n**Resposta sugerida: {person}**\n\n{answer}")
    write(
        "perguntas_e_respostas.md",
        f"# Banco de 27 perguntas — arguição separada de cinco minutos\n\n{names}\n\n"
        "As perguntas ocupam 05:00–10:00, após a apresentação. Ambos devem dominar todas as respostas. "
        "Respostas iniciais de 15–35 segundos; o professor pode aprofundar qualquer tópico. "
        "Não é necessário responder às 27 perguntas em uma sessão.\n\n"
        "Base verificável: [resultados e fontes](resultados_validados.md), "
        "[solver](../RUFAS/biophysical/animal/ration/linear_diet.py), "
        "[adaptador](../RUFAS/biophysical/animal/ration/linear_diet_adapter.py), "
        "[exemplo](../RUFAS/biophysical/animal/ration/linear_diet_example.py) e "
        "[validação](evidencias/testes.md). Veja a [simulação oral](simulacao_arguicao.md).\n\n"
        + "\n\n".join(questions),
    )
    extensions = [
        " No exemplo, somamos as parcelas de alfafa, milho e soja com precisão completa. "
        "O resultado é 34,9978 reais por dia. Esse mínimo depende dos preços, ingredientes e "
        "restrições informados; mudar o cenário pode mudar a solução.",
        " A contribuição está na ligação entre os dados existentes e um núcleo linear verificável. "
        "A conversão entre matéria natural e seca mantém as unidades consistentes. "
        "A baixa automática de estoque e o uso no ciclo diário ainda são trabalhos futuros.",
        " A mesma transformação vale para o limite superior, invertendo a desigualdade. "
        "Isso funciona porque a proporção exigida é constante e a matéria seca é positiva. "
        "Não significa linearizar todas as relações biológicas do animal.",
        " A composição dos três ingredientes vem da biblioteca NRC utilizada pelo projeto. "
        "Preços, estoques e energia suplementar estão identificados como didáticos. "
        "Para uma aplicação prática, precisaríamos documentar esses parâmetros e ampliar a avaliação nutricional.",
        " Também recalculamos o custo fora do resultado retornado pelo solver. "
        "Essas verificações apoiam a correção computacional do cenário. "
        "Os 433 casos são dos componentes relacionados, não de toda a suíte, e não substituem validação em animais.",
        " Um ótimo matemático satisfaz o modelo fornecido; a qualidade da decisão depende também "
        "da qualidade desse modelo. Portanto, a evolução exige dados documentados e avaliação especializada, "
        "antes de transformar esta demonstração em uma recomendação para a fazenda.",
    ]
    simulation = []
    for round_index, question_index in enumerate([3, 11, 7, 12, 15, 24]):
        question, _, answer = QA[question_index - 1]
        person = SOPHIA if round_index % 2 == 0 else ANDERSON
        start = round_index * 50
        simulation.append(
            f"## {stamp(start)}–{stamp(start + 50)} — {person}\n\n"
            f"- Professor, 10 s: {question}\n"
            f"- Resposta, cerca de 35 s: {answer}{extensions[round_index]}\n"
            "- Pausa e troca de interlocutor, 5 s.\n"
        )
    write(
        "simulacao_arguicao.md",
        f"# Simulação de arguição — cinco minutos adicionais\n\n{names}\n\n"
        "Inicie um novo cronômetro ao terminar a apresentação: 00:00 aqui corresponde a 05:00 "
        "da atividade. Seis rodadas de 50 segundos somam 300 segundos; a atividade termina às 10:00. "
        "Os tempos incluem a pergunta, a resposta e a transição. São metas de ensaio, não uma gravação medida. "
        "Cada integrante conduz três rodadas; depois invertam os papéis para estudar todo o projeto.\n\n"
        + "\n".join(simulation),
    )
    write(
        "guia_demonstracao.md",
        rf"""# Demonstração ao vivo — 85 segundos

{names}

## Comando principal

No PowerShell do Antigravity, a partir da raiz do projeto:

```powershell
.\apresentacao\demonstracao_solver.bat
```

Alternativa direta:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m apresentacao.demo_solver
```

O BAT localiza a raiz a partir de sua própria pasta e usa `.venv\Scripts\python.exe`.
Execute no terminal já aberto, não por duplo clique: assim a saída permanece visível.
Não execute `activate_this.py` nem edite arquivos dentro da `.venv`.
O ambiente deve estar preparado antes da aula; não faça instalações durante os cinco minutos.

## Preparação antes de iniciar o cronômetro

1. Abra o PowerPoint no slide 1 e deixe o terminal como única outra janela da demonstração.
2. Amplie o terminal, aumente a fonte e use pelo menos 100 colunas e cerca de 32 linhas visíveis.
3. Execute uma vez ` .\apresentacao\demonstracao_solver.bat --auto` para aquecer os imports e validar o ambiente.
4. Execute novamente sem `--auto`. O programa mostra as entradas e espera Enter **antes de chamar o solver**.
5. Volte aos slides. Ao terminar o slide 3, use Alt+Tab; as entradas já estarão na tela.

Preparar as entradas antes da contagem não pré-calcula a solução: `optimize_diet` é chamado somente após Enter.

## Divisão da fala

| Relógio geral | Ação |
|---|---|
| 03:00–03:35 | Sophia mostra o perfil, os três ingredientes, preços, estoques e metas. Pressiona Enter. |
| 03:35–04:25 | Anderson explica as quantidades, custo e 11/11 verificações. |
| 04:25 | Alt+Tab para os slides; avançar ao slide 4. |

Transição: “Vou executar o solver agora. Anderson, explique o resultado.”
Resultado esperado: `optimal`, custo aproximado de R$ 34,9978/dia; todos os checks verdadeiros.
A soma usa quantidades completas; a tabela arredonda apenas para apresentação.

## O que é real e o que é ilustrativo

O programa executa o solver real; não lê uma dieta pronta do JSON. Reutiliza `example_inputs()` e
`optimize_diet()` existentes. A composição vem da biblioteca NRC do RuFaS e a MS do seu calculador NRC.
Os preços, estoques, NEL por ingrediente e metas suplementares são didáticos. Minerais opcionais não são ativados.
A demonstração recebe um perfil, não instancia nem executa uma fazenda inteira.

## Registro e contingência

Cada execução grava `apresentacao/evidencias/demo_resultado.json` e substitui o registro anterior.
O registro consolidado usado para criar os slides fica em `apresentacao/evidencias/base_slides.json`.

Se houver falha, não tente depurar durante a fala. Informe que a execução ao vivo falhou,
retorne ao slide 4 e identifique o resultado como **execução previamente validada**.
`evidencias/demo_terminal.md` guarda a saída real anterior. Não a apresente como uma execução ao vivo.
Se o PowerPoint não abrir, use `apresentacao_rufas_5min.pdf`, quando disponível, ou as prévias PNG.
Não acrescente uma segunda demo ou uma instalação ao cronograma.

## Dependências

Para a demo: as dependências originais do projeto e Python 3.12 ou 3.13.
Para recriar o PowerPoint: `python-pptx==1.0.2` (instalado apenas no ambiente de preparação).
Não é necessário python-pptx no computador que apenas abrirá o PPTX.
""",
    )
    result = demo["result"]
    t = result["totals"]
    executed = datetime.fromisoformat(validation["executed_at"]).strftime("%d/%m/%Y %H:%M:%S %z")
    ingredient_rows, output_rows = [], []
    for ingredient in demo["ingredients"]:
        key = str(ingredient["identifier"])
        ingredient_rows.append(
            f"| {ingredient['name']} | {pt_number(ingredient['price_per_kg'])} | "
            f"{pt_number(ingredient['stock_kg'])} | {pt_number(ingredient['maximum_kg_day'])} | "
            f"{pt_number(100 * ingredient['dm_fraction'], 1)} | {pt_number(100 * ingredient['cp_fraction'], 1)} | "
            f"{pt_number(100 * ingredient['ndf_fraction'], 1)} | {pt_number(ingredient['nel_mcal_per_kg_dm'], 1)} |"
        )
        output_rows.append(
            f"| {ingredient['name']} | {pt_number(result['quantities_kg_day'][key])} | "
            f"{pt_number(result['ration_kg_dm_day'][key])} | {pt_number(result['costs_per_day'][key])} |"
        )
    checks = "\n".join(
        f"| {c['name']} | {c['supplied']:.8f} | {c['lower']} | {c['upper']} | "
        f"{c['slack']:.8g} | {'OK' if c['satisfied'] else 'FALHOU'} |"
        for c in result["checks"]
    )
    write(
        "resultados_validados.md",
        f"""# Resultados validados e auditoria técnica

{names}

Validação registrada em **{executed}**, horário de São Paulo. Evidência: `evidencias/validacao.json`.

## Estado real e escopo investigado

Foram examinados os módulos `linear_diet`, adaptadores, exemplos, catálogo, testes de rações/nutrição,
`pyproject.toml`, documentação em `docs/`, entradas em `input/data/feed/` e saídas dos exemplos.
O repositório possui módulos de animais, alimentação, solo/culturas e demais subsistemas.
A validação se concentrou nos componentes ligados a este trabalho; não afirma auditoria de todo o simulador.

O otimizador original `ration_optimizer.py` usa `minimize` com SLSQP. O módulo novo usa
`scipy.optimize.linprog(method="highs")`, com escolha automática entre os métodos LP suportados pelo HiGHS.
Não afirmamos ter fixado simplex ou pontos interiores. O núcleo original não foi modificado para a apresentação.

## Entradas da demonstração escolhida

Animal: 650 kg, DEL 100, leite 30 kg/dia, gordura 3,8%, proteína verdadeira 3,2%.
No calculador: peso adulto 700 kg; 2ª lactação; sem gestação informada; ECC 3/5;
lactose 4,8%; alojamento Barn; demais parâmetros em `linear_diet_example.example_inputs`.
Período: dieta diária constante por sete dias, com estoque alocado a um animal.

| Ingrediente | R$/kg MN | Estoque kg MN | Máximo kg MN/dia | MS % | PB % MS | FDN % MS | NEL Mcal/kg MS |
|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(ingredient_rows)}

Preços, estoques, limites operacionais e NEL são ilustrativos. Composição: `input/data/feed/NRC_comp.csv`,
IDs 1, 44 e 167. PB e FDN são teores em base MS; o preço exibido é por kg MN.
MS exigida: {pt_number(t['DM_kg'])} kg/dia, calculada pelo RuFaS/NRC.
Metas ilustrativas: PB ≥ 3,6 kg/dia; NEL ≥ 35 Mcal/dia; FDN entre 28% e 40% da MS.

## Saída obtida de execução real

| Ingrediente | kg MN/dia | kg MS/dia | R$/dia |
|---|---:|---:|---:|
{chr(10).join(output_rows)}

**Status:** `{result['status']}`. **Custo:** R$ {pt_number(result['cost_per_day'])}/dia.
Custo independente recomputado: `{demo['independent_cost']:.12f}`.
MS: {pt_number(t['DM_kg'])} kg; PB: {pt_number(t['CP_kg'])} kg;
NEL: {pt_number(t['NEL_Mcal'])} Mcal; FDN: {pt_number(t['NDF_kg'])} kg
({pt_number(100 * t['NDF_kg'] / t['DM_kg'], 2)}% da MS).

| Verificação | Fornecido | Mínimo | Máximo | Folga | Status |
|---|---:|---:|---:|---:|---|
{checks}

`None` indica ausência daquele lado do limite. As linhas de FDN verificam resíduos lineares em kg,
não percentuais diretamente. Folgas numericamente próximas de zero são avaliadas com tolerância absoluta de 1e-7.
As 11 linhas incluem cinco verificações nutricionais e seis de inclusão/estoques.
Não são onze nutrientes. Valores exibidos são arredondados; o solver usa precisão completa.

## Modelo auditado

```text
x_i = kg MN/dia; d_i = kg MS/kg MN; p_i = R$/kg MN.
c_i = kg PB/kg MS; e_i = Mcal NEL/kg MS; f_i = kg FDN/kg MS.
Min C = soma(p_i x_i)
MS_min <= soma(d_i x_i) <= MS_max
soma(d_i c_i x_i) >= PB_min
soma(d_i e_i x_i) >= NEL_min
soma(d_i (f_i-r_min) x_i) >= 0
soma(d_i (f_i-r_max) x_i) <= 0
L_i <= x_i <= U_i; T x_i <= S_i; x_i >= 0
```

Todas as expressões são lineares em x. A igualdade de MS usa os mesmos limites inferior/superior.
Para MS total positiva, a reformulação da proporção de FDN preserva equivalência algébrica.
O núcleo aceita mínimos minerais totais opcionais quando a composição é conhecida para todos os ingredientes;
não há minerais ativos nesta demo. Não há máximos minerais, máximo de PB ou modelo completo de aminoácidos.

No adaptador, preço por kg MS é multiplicado por d_i para virar preço por kg MN.
Estoque e limites em kg MS são divididos por d_i para virar kg MN. Percentuais são divididos por 100.
R$/tonelada é dividido por 1000 sem trocar a base. O período multiplica quantidades diárias, não o preço unitário.

## Integração comprovada e limites

Os testes usam Feed/NRCFeed, NutritionRequirements, calculador NRC, FeedInRation e cálculo de PB/FDN do RuFaS.
Há teste de snapshot mínimo de Animal/MilkProduction. Isso comprova os adaptadores; não uma simulação de fazenda.
O resultado fornece um dicionário em kg MS/dia compatível com rações. Não há aplicação automática nem baixa de estoque.

A única exigência importada diretamente para o LP nos exemplos é a MS. NRC (2001), capítulo 1, p. 4,
equação 1-2, é a referência do calculador reutilizado. NASEM (2021) integra as fontes do RuFaS e a biblioteca
alternativa do catálogo, mas não foi usado para calcular todas as metas da demo. DE não foi convertida em NEL;
proteína metabolizável não foi confundida com PB; minerais absorvidos não foram confundidos com totais.

## Testes e evidência de execução

**{validation['test_counts']['tests']} testes executados: zero falhas, zero erros e zero skips.**
Incluem 33 testes específicos dos módulos novos e testes preexistentes de rações, nutrição e estruturas relacionadas.
A suíte completa da fazenda não foi executada. Comandos e saída integral estão em `evidencias/testes.md`;
o relatório JUnit está em `evidencias/testes.xml`. Versões e hashes de fontes estão em `evidencias/validacao.json`.

Versões: {json.dumps(validation['versions'], ensure_ascii=False)}.
Tempo de chamada do solver na demo registrada: {demo['solver_seconds']:.4f} s.
O tempo total do processo, com imports, foi {validation['commands'][0]['seconds']:.3f} s nesta execução.
Não é benchmark. Pré-aqueça o ambiente antes da apresentação; a duração da fala precisa ser ensaiada.

## Outros resultados disponíveis

`output/linear_diet_example.json` e `output/linear_diet_cow_2.json` foram inspecionados, mas os slides usam
uma nova execução registrada em `evidencias/base_slides.json`. O cenário da segunda vaca é histórico.
O catálogo foi executado novamente com semente 42: ver `evidencias/catalogo.md` e `evidencias/catalogo/result.json`.
Ele avalia 300 registros, utiliza 185 candidatos e registra 115 exclusões. Essa execução é material de apoio,
não uma segunda demonstração durante os cinco minutos. Seus parâmetros diferem do exemplo de três alimentos.
Não há comparação válida de economia ou percentual de ganho nesta entrega.
""",
    )
    write(
        "checklist_apresentacao.md",
        f"""# Checklist de apresentação

{names}

## Validação técnica registrada

- [x] Solver executado novamente e custo reconferido.
- [x] 11/11 verificações satisfeitas na demonstração.
- [x] 433 testes relacionados aprovados, incluindo 33 específicos.
- [x] Dados ilustrativos identificados em slides, terminal e roteiro.
- [x] Quatro slides gerados, com nomes completos e notas de fala.
- [x] Cronograma de 300 segundos de apresentação + 300 segundos de arguição = 600 segundos.
- [x] BAT e modo automático preparados para o Windows.
- [x] Integração descrita como adaptador; sem alegação de ciclo diário completo.
- [x] Sem percentual de economia inventado e sem comparação de cenários incompatíveis.

## Antes de apresentar — verificar manualmente

- [ ] Abrir o PPTX no computador e projetor que serão usados; conferir fontes e proporção 16:9.
- [ ] Consultar `evidencias/verificacao_powerpoint.json` para conferir abertura e exportação automáticas.
- [ ] Ensaiar a dupla com cronômetro: slide 1 até 00:45; slide 2 até 01:45; slide 3 até 03:00.
- [ ] Ensaiar demo até 04:25, conclusão até 05:00, perguntas separadas até 10:00.
- [ ] Executar o BAT com `--auto` antes da aula; depois deixá-lo aguardando Enter nas entradas.
- [ ] Deixar somente PowerPoint e terminal necessários à apresentação; testar Alt+Tab.
- [ ] Usar fonte de terminal legível e largura suficiente para as tabelas.
- [ ] Fechar notificações e conectar o carregador.
- [ ] Guardar PPTX, PDF/prévias e cópia das evidências localmente para uso sem internet.
- [ ] Estudar os cartões e pelo menos as perguntas prioritárias.

Os itens manuais não foram marcados como concluídos: não houve ensaio oral da dupla nem teste do projetor.
Se ocorrer falha ao vivo, identificar a saída de contingência como execução anterior, nunca como execução ao vivo.
""",
    )
    write(
        "README.md",
        rf"""# Apresentação acadêmica — PO-Rufas

{names}

**Exatamente quatro slides, 5 minutos de exposição e demonstração + 5 minutos adicionais de perguntas.**
**Total: 10 minutos.**

Abra [apresentacao_rufas_5min.pptx](apresentacao_rufas_5min.pptx).
Leia o [roteiro completo](roteiro_completo.md) e o [guia da demonstração](guia_demonstracao.md).
Use os [cartões](cartoes_consulta.md) para ensaiar e o [banco de perguntas](perguntas_e_respostas.md) para estudar.
Arguição: [simulação de cinco minutos](simulacao_arguicao.md).
Falas individuais: [Sophia](roteiro_sophia.md) e [Anderson](roteiro_anderson.md).

```powershell
.\apresentacao\demonstracao_solver.bat
```

O terminal mostra as entradas; Enter inicia uma nova chamada do solver. A apresentação escolhe
o exemplo de três ingredientes para caber no tempo. A busca no catálogo permanece disponível como apoio.

Resultados: [relatório técnico](resultados_validados.md). Preparação: [checklist](checklist_apresentacao.md).
As saídas em `evidencias/` documentam execuções reais; os parâmetros ilustrativos continuam identificados.

## Recriar os materiais

Dependências opcionais de autoria e verificação:

```powershell
.\.venv\Scripts\python.exe -m pip install -r apresentacao/requirements.in
```

Os registros versionados omitem caminhos pessoais e o nome da máquina; os resultados numéricos são preservados.

Na raiz do repositório, com o ambiente preparado e `python-pptx==1.0.2` instalado:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m apresentacao.validar_projeto
.\.venv\Scripts\python.exe -X utf8 -m apresentacao.gerar_materiais
```

A regeneração substitui os arquivos gerados e atualiza a base de resultados dos slides.
`conteudo.py` centraliza as falas e perguntas; `gerar_materiais.py` cria o PowerPoint e os guias.
O solver e as equações continuam nos módulos originais do projeto.
A entrega é acompanhada no [PR #6](https://github.com/sophialannah/PO-Rufas/pull/6).
""",
    )


def box(slide, x, y, w, h, fill, radius=False):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(fill)
    shape.line.fill.background()
    return shape


def text(slide, x, y, w, h, content, size=20, color=NAVY, bold=False, font="Calibri"):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    for n, line in enumerate(content.split("\n")):
        p = tf.paragraphs[0] if n == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = font
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = RGBColor.from_string(color)
        p.space_after = Pt(6)
    return shape


def base(prs, index, title, speaker, interval):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = RGBColor.from_string(PAPER)
    box(slide, 0, 0, 13.333, 0.12, GREEN)
    text(slide, 0.62, 0.37, 10.9, 0.35, "PO-RUFAS  /  PESQUISA OPERACIONAL", 12, GREEN, True)
    text(slide, 0.62, 0.91, 12.1, 0.72, title, 31, NAVY, True)
    box(slide, 0.62, 6.91, 12.05, 0.012, "CCD5D3")
    text(slide, 0.62, 7.02, 10.8, 0.29, f"{speaker}  ·  {interval}  |  Cenário acadêmico demonstrativo", 11, MUTED)
    text(slide, 12.0, 7.0, 0.65, 0.30, f"0{index}/04", 12, GREEN, True)
    return slide


def notes(slide, content):
    slide.notes_slide.notes_text_frame.text = content


def deck(demo: dict, validation: dict) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333333), Inches(7.5)
    prs.core_properties.title = "Otimização de Dietas para Bovinos Leiteiros com Python e RuFaS"
    prs.core_properties.subject = "Apresentação de cinco minutos + cinco de arguição — quatro slides"
    prs.core_properties.author = f"{SOPHIA}; {ANDERSON}"
    prs.core_properties.keywords = "PO-Rufas, programação linear, SciPy, HiGHS, dados demonstrativos"
    s = base(prs, 1, "", "Sophia", "00:00–00:45")
    text(s, 0.62, 1.02, 9.0, 2.15, "Otimização de Dietas para\nBovinos Leiteiros\ncom Python e RuFaS", 37, NAVY, True)
    text(
        s, 0.66, 3.30, 8.5, 0.95, "Aplicação de Programação Linear à Formulação\nNutricional de Menor Custo.", 21, GREEN
    )
    text(
        s,
        0.66,
        4.42,
        8.30,
        0.85,
        "Como combinar ingredientes para atender às restrições\nnutricionais com o menor custo possível?",
        21,
    )
    text(s, 0.66, 5.65, 8.4, 0.92, f"{SOPHIA}\n{ANDERSON}", 18, NAVY, True)
    box(s, 9.70, 1.12, 2.95, 5.37, NAVY, True)
    for y, number, label, sub in [
        (1.55, "01", "DADOS", "Animal + alimentos"),
        (3.04, "02", "MODELO LINEAR", "Minimizar Σ pᵢ xᵢ"),
        (4.54, "03", "DECISÃO", "Dieta + verificação"),
    ]:
        text(s, 10.0, y, 2.3, 0.34, number, 14, "6AC8AE", True)
        text(s, 10.0, y + 0.37, 2.4, 0.40, label, 17, WHITE, True)
        text(s, 10.0, y + 0.83, 2.35, 0.42, sub, 16, "CBDFD8")
    notes(
        s, f"{SOPHIA} — 45 segundos\n{STAGES[0][3]}\nDados do exemplo são demonstrativos; objetivo é validar o núcleo."
    )

    s = base(prs, 2, "Arquitetura e integração com o RuFaS", "Anderson", "00:45–01:45")
    columns = [
        (0.65, 3.83, "ENTRADAS", "Perfil do animal\nLista de ingredientes\nPreços e estoques\nMetas nutricionais"),
        (5.05, 3.30, "OTIMIZADOR", "Adaptadores RuFaS\nConversão MN ↔ MS\nSciPy • linprog / HiGHS"),
        (8.94, 3.73, "SAÍDA", "Quantidades por alimento\nCusto diário mínimo\nRestrições verificadas"),
    ]
    for x, width, label, content in columns:
        box(s, x, 2.0, width, 2.85, WHITE, True)
        box(s, x, 2.0, width, 0.55, GREEN, True)
        text(s, x + 0.20, 2.09, width - 0.4, 0.35, label, 17, WHITE, True)
        text(s, x + 0.20, 2.80, width - 0.4, 1.92, content, 21)
    for x in [4.56, 8.42]:
        arrow = s.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(x), Inches(3.05), Inches(0.38), Inches(0.55))
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = RGBColor.from_string(GOLD)
        arrow.line.fill.background()
    text(
        s,
        0.68,
        5.18,
        6.0,
        0.82,
        "RuFaS: composição + consumo de MS (NRC).\nCenário: preços, estoques, NEL e metas extras.",
        19,
    )
    box(s, 7.42, 5.12, 5.20, 1.23, PALE, True)
    text(
        s,
        7.64,
        5.30,
        4.77,
        0.87,
        "Integração modular testada.\nSem aplicação automática ao ciclo diário.",
        19,
        GREEN,
        True,
    )
    notes(
        s,
        f"{ANDERSON} — 60 segundos\n{STAGES[1][3]}\n"
        "Fontes locais: linear_diet_adapter.py, linear_diet_example.py e NRC_comp.csv. "
        "Só MS é importada diretamente como exigência; PB/NEL/FDN são ilustrativas. "
        "Feed, NutritionRequirements e Animal são estruturas reais. Não é execução completa da fazenda.",
    )

    s = base(prs, 3, "Modelo matemático: custo mínimo", "Sophia", "01:45–03:00")
    box(s, 0.65, 1.98, 4.16, 3.97, NAVY, True)
    text(s, 0.90, 2.22, 3.67, 0.40, "FUNÇÃO OBJETIVO", 15, "6AC8AE", True)
    text(s, 0.90, 2.94, 3.70, 0.75, "Min C = Σ pᵢ xᵢ", 30, WHITE, True)
    text(
        s,
        0.90,
        4.06,
        3.70,
        1.62,
        "xᵢ: kg MN do alimento i / dia\npᵢ: R$ / kg MN\nC: custo total em R$ / dia",
        19,
        WHITE,
    )
    text(s, 5.20, 1.94, 7.39, 0.40, "RESTRIÇÕES IMPLEMENTADAS", 16, GREEN, True)
    equations = [
        "MSmín ≤ Σ dᵢ xᵢ ≤ MSmáx",
        "Σ dᵢ cᵢ xᵢ ≥ PBmín     |     Σ dᵢ eᵢ xᵢ ≥ NELmín",
        "rmín Σ dᵢ xᵢ ≤ Σ dᵢ fᵢ xᵢ ≤ rmáx Σ dᵢ xᵢ",
        "Lᵢ ≤ xᵢ ≤ Uᵢ     |     T xᵢ ≤ Sᵢ     |     xᵢ ≥ 0",
    ]
    for i, eq in enumerate(equations):
        box(s, 5.18, 2.60 + i * 0.67, 7.45, 0.55, WHITE, True)
        text(s, 5.35, 2.69 + i * 0.67, 7.10, 0.40, eq, 20)
    text(
        s,
        5.22,
        5.44,
        7.38,
        0.63,
        "d: fração MS; c: PB/MS; e: NEL/MS; f: FDN/MS.\nT: dias; S: estoque MN; L/U: limites; r: fração de FDN.",
        15,
        MUTED,
    )
    text(
        s,
        0.69,
        6.22,
        12.0,
        0.43,
        "Coeficientes fixos → LP linear. Minerais: mínimos opcionais, não ativados na demonstração.",
        18,
        GREEN,
        True,
    )
    notes(
        s,
        f"{SOPHIA} — 75 segundos\n{STAGES[2][3]}\n"
        "Após este slide, Alt+Tab para o terminal já aguardando Enter. Demo: Sophia 35 s, Anderson 50 s. "
        "Retornar ao slide 4 às 04:25. A restrição de FDN é equivalente à proporção para MS total positiva. "
        "O calculador NRC roda previamente; não houve linearização arbitrária de suas equações.",
    )

    s = base(prs, 4, "Resultados verificados e contribuição", "Anderson", "04:25–05:00; perguntas: 05:00–10:00")
    result = demo["result"]
    text(
        s,
        0.69,
        1.76,
        11.8,
        0.46,
        "Cenário ao vivo: 650 kg  ·  DEL 100  ·  30 kg de leite/dia  ·  3 ingredientes",
        19,
        MUTED,
    )
    table = s.shapes.add_table(4, 3, Inches(0.68), Inches(2.55), Inches(7.05), Inches(2.35)).table
    table.columns[0].width, table.columns[1].width, table.columns[2].width = Inches(3.38), Inches(1.84), Inches(1.83)
    data = [["Ingrediente", "kg MN/dia", "R$/dia"]]
    for ingredient in demo["ingredients"]:
        key = str(ingredient["identifier"])
        label = {1: "Alfafa, farinha", 44: "Milho", 167: "Farelo de soja"}[ingredient["identifier"]]
        data.append([label, pt_number(result["quantities_kg_day"][key]), pt_number(result["costs_per_day"][key])])
    for r in range(4):
        for c in range(3):
            cell = table.cell(r, c)
            cell.text = data[r][c]
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor.from_string(GREEN if r == 0 else WHITE if r % 2 else PALE)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = Inches(0.14)
            for p in cell.text_frame.paragraphs:
                p.font.name, p.font.size, p.font.bold = "Calibri", Pt(19), r == 0
                p.font.color.rgb = RGBColor.from_string(WHITE if r == 0 else NAVY)
    box(s, 8.05, 2.55, 4.55, 2.35, NAVY, True)
    text(s, 8.32, 2.83, 4.0, 0.34, "CUSTO MÍNIMO DO CENÁRIO", 14, "6AC8AE", True)
    text(s, 8.32, 3.40, 4.0, 0.78, f"R$ {pt_number(result['cost_per_day'])}", 34, WHITE, True)
    text(s, 8.32, 4.30, 4.0, 0.38, "por vaca / dia  ·  status optimal", 17, WHITE)
    text(
        s,
        0.70,
        5.15,
        6.10,
        0.48,
        f"11/11 verificações  •  {validation['test_counts']['tests']} testes aprovados",
        22,
        GREEN,
        True,
    )
    text(
        s,
        0.70,
        5.79,
        11.85,
        0.46,
        "Contribuição: núcleo linear executável e integrado aos dados do RuFaS.",
        21,
        NAVY,
        True,
    )
    text(
        s,
        0.70,
        6.37,
        11.85,
        0.30,
        "Parâmetros suplementares ilustrativos. Próximo passo: dados documentados e validação nutricional completa.",
        14,
        MUTED,
    )
    notes(
        s,
        f"{ANDERSON} — 35 segundos\n{STAGES[5][3]}\n"
        f"Fonte: execução real em {demo['executed_at']}; base_slides.json. "
        "As 11 verificações são linhas de nutrientes e limites, não 11 nutrientes. "
        "433 testes relacionados, não suíte integral. Não há economia percentual comprovada. "
        "Encerrar a apresentação às 05:00; arguição adicional até 10:00 (300 s). Nomes: " + SOPHIA + "; " + ANDERSON,
    )
    target = HERE / "apresentacao_rufas_5min.pptx"
    prs.save(target)
    verify_deck(target)


def verify_deck(target: Path) -> None:
    """Check the actual generated package, including slide count and text bounds."""
    reopened = Presentation(target)
    assert len(reopened.slides) == 4
    all_text = "\n".join(sh.text for slide in reopened.slides for sh in slide.shapes if sh.has_text_frame)
    assert SOPHIA in all_text and ANDERSON in all_text
    for slide in reopened.slides:
        for shape in slide.shapes:
            assert shape.left >= 0 and shape.top >= 0
            assert shape.left + shape.width <= reopened.slide_width + 100
            assert shape.top + shape.height <= reopened.slide_height + 100
    print("PowerPoint generated and structurally reopened: 4 slides, names, shapes in bounds.")


def main() -> None:
    demo = json.loads((HERE / "evidencias/demo_resultado.json").read_text(encoding="utf-8"))
    validation = json.loads((HERE / "evidencias/validacao.json").read_text(encoding="utf-8"))
    assert demo["result"]["status"] == "optimal"
    assert validation["test_counts"]["tests"] == 433
    assert validation["test_counts"]["failures"] == validation["test_counts"]["errors"] == 0
    (HERE / "evidencias/base_slides.json").write_text(json.dumps(demo, ensure_ascii=False, indent=2), encoding="utf-8")
    guides(demo, validation)
    deck(demo, validation)
    word_counts = [
        {"stage": title, "seconds": seconds, "words": len(re.findall(r"\S+", speech))}
        for title, _, seconds, speech in STAGES
    ]
    (HERE / "evidencias/roteiro_tempos.json").write_text(
        json.dumps(
            {
                "speaking_and_demo_seconds": 300,
                "questions_seconds": 300,
                "total_seconds": 600,
                "note": "Planned schedule; not a measured oral rehearsal",
                "stages": word_counts,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("Guides generated; timing plan: 300 + 300 = 600 seconds.")


if __name__ == "__main__":
    main()
