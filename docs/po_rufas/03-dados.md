# Dados de entrada e rastreabilidade
[Sumário](README.md)

## Cenário anual oficial

O runner copia example_freestall_dairy_metadata e as configurações para uma pasta nova. Os três cenários controlados usam NRC, clima de 2013, semente 42, intervalo de um dia, meta de 10 vacas e 26 animais efetivos inicialmente. A população é determinada pelo HerdFactory nativo; o alvo não equivale ao total efetivo.

Os arquivos config.json, animal.json, feed.json, effective_inputs.json e initial_state.json de cada execução documentam entradas brutas, entradas validadas e estado inicial. Diários e summaries ficam em [nativo_final_365](../../evidencias/correcao_dinamica/nativo_final_365/), [hibrido_final_365](../../evidencias/correcao_dinamica/hibrido_final_365/) e [exclusivo_estoque_365](../../evidencias/correcao_dinamica/exclusivo_estoque_365/).

O exemplo original era NASEM: na cópia NRC foram retirados 301/302 e acrescentados 1/167/231. Os parâmetros originais permanecem preservados. Preços anuais são UM/kg MS, demonstrativos, distintos dos preços R$ do LP estático.

O catálogo dá ao suplemento 231 DM=97%, Ca=22% MS, P=19,3% MS e limite de 100 kg MS/animal/dia neste cenário. Esse limite amplo é um dado de entrada, não recomendação científica. A política dinâmica limita concentrações totais de Ca/P; não inventa um máximo fixo próprio do suplemento.

## Dados do LP estático

| Parâmetro | Valor demonstrativo | Unidade | Classificação e origem | Arquivo / função |
|---|---:|---|---|---|
| Animal inicial | 98605 | ID | Registro RuFaS | `input/data/animal/animal_population.json`; `load_animals` |
| Peso do animal 98605 | 627,560669 | kg | Registro RuFaS | Mesmo arquivo; construtor `Animal` |
| DEL / paridade 98605 | 100 / 4 | dias / contagem | Registro RuFaS | Mesmo arquivo |
| Animal alternativo | 93785 | ID | Registro RuFaS | Mesmo arquivo |
| Leite | 30 ou 31 | kg/dia | Hipótese do cenário | `demo_inputs`, `run_scenario` |
| Gordura / proteína verdadeira / lactose do leite | 3,8 / 3,2 / 4,8 | % | Hipóteses | `frontend/service.py::ASSUMPTIONS` |
| Ambiente | Barn, caminhada 0, temperatura anterior 20 | configuração / distância nativa / °C | Hipóteses | `demo_inputs`, `run_scenario` |
| MS dos alimentos | 90,3 / 88,1 / 89,5 | % MN | Biblioteca NRC, IDs 1/44/167 | `input/data/feed/NRC_comp.csv` |
| PB / FDN / P / Ca dos alimentos | Por registro | % MS | Biblioteca NRC | Mesmo arquivo; `build_feeds` |
| Preço alfafa / milho / soja | 1.400 / 1.800 / 2.800 | R$/t MS | Hipóteses econômicas | `linear_diet_example.py::example_feeds` |
| Estoque alfafa / milho / soja | 150 / 100 / 60 | kg MS | Hipóteses alocadas ao animal | `example_feeds` |
| Máximos alfafa / milho / soja | 16 / 10 / 6 | kg MS/dia | Hipóteses de inclusão | `example_feeds` |
| NEL alfafa / milho / soja | 1,3 / 2,0 / 1,8 | Mcal/kg MS | Hipóteses de coeficientes fixos | `DEMO_FEEDS` |
| PB mínima / NEL mínima | 3,6 / 35 | kg/dia / Mcal/dia | Metas externas | Widgets em `frontend/app.py` |
| FDN mínima / máxima | 28 / 40 | % MS | Metas externas | Mesmo arquivo |
| Horizonte | 7 | dias | Hipótese operacional | `run_scenario` |
| Consumo de MS | Calculado por animal | kg MS/dia | Calculador NRC | `Animal.calculate_nutrition_requirements` |
| P / Ca absorvidos requeridos | Calculados | g/dia | Calculador NRC e exigência processual de P | `optimize_animal_ration` |
| Fosfato bicálcico 231 | 97 MS; 19,3 P; 22 Ca | % | Biblioteca NRC | `NRC_comp.csv` |
| Preço / estoque / máximo ID 231 | 5 / 1 / 0,10 | R$/kg MN / kg MN / kg MN/dia | Hipóteses de reprodução | Entrada manual em Ingredientes |
| NEL ID 231 | 0 | Mcal/kg MS | Valor explícito no cenário mineral | Entrada manual |

O frontend disponibiliza somente candidatos com composição NRC. A ferramenta de catálogo por terminal possui uma auditoria mais ampla, com precedência NRC e candidatos NASEM quando ausentes no NRC. Seus resultados pertencem a outro fluxo.

Conversões do adaptador, para `d=DM/100`:
- preço por kg MN = preço por kg MS × d;
- estoque MN = estoque MS / d;
- limite MN = limite MS / d;
- percentual de PB, FDN ou mineral dividido por 100 gera fração na MS;
- preço por tonelada dividido por 1.000 conserva a base original.

O período representa estoque alocado a um animal. Reutilizar esse estoque integral para vários animais exige uma alocação adicional. [Código do adaptador](../../RUFAS/biophysical/animal/ration/linear_diet_adapter.py)

## Entradas congeladas e bases comerciais

A fixture tests/fixtures/dynamic_first_day.json guarda alimentos completos, unidades, categoria, peso e requisitos do primeiro dia. A reprodução restaura os geradores entre solvers; entradas e todas as quantidades estão em [replay_final](../../evidencias/correcao_dinamica/replay_final/). O código anterior está congelado em optimizer_anterior.py.txt.

A composição vem das bibliotecas RuFaS; disponibilidade, preços e metas suplementares da demonstração não são observações de fazenda. As cotações IFAG do experimento estático e CEPEA da correção anual pertencem a cenários **parciais e separados**. Não foram usadas para reescrever os preços demonstrativos da comparação oficial.

[cenario_comercial_parcial.json](../../evidencias/correcao_dinamica/cenario_comercial_parcial.json) documenta uma cotação CEPEA datada de 04/09/2026, 70,93 R$/saca de 60 kg MN, convertida com DM=0,881. Os preços não verificados ficam nulos. Não existe orçamento comercial completo validado nem se mistura moeda BRL com UM.

## Proveniência

O [inventário candidato](../../evidencias/publicacao/candidato_inventario.json) registra caminhos, tamanhos e hashes da cópia isolada. O histórico pessoal da conversa não integra os dados científicos necessários. [Referências e autoria](14-referencias.md).
