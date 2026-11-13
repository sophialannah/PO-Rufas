# Otimização linear de dietas integrada ao RuFaS

[Guia de instalação e execução](../README.md) · [Roteiro para apresentação](apresentacao_projeto.md)

Este documento detalha a formulação matemática, a integração, as fontes e os limites
dos exemplos. Para executar pela primeira vez, comece pelo README.

## Busca no catálogo completo (extensão)

O comando abaixo analisa os **300 registros** de `user_feeds.csv`, cruza os IDs com
`NRC_comp.csv` e `NASEM_Comp_with_TDN.csv` e fornece todos os candidatos ao LP:

```powershell
.\.venv\Scripts\python.exe -m RUFAS.biophysical.animal.ration.linear_diet_catalog --demo --seed 42
```

O núcleo `optimize_diet` já aceita qualquer tamanho de lista. O novo módulo
`linear_diet_catalog.py` automatiza a preparação da lista inteira, em vez de selecionar
três alimentos previamente. Não enumera subconjuntos: o solver escolhe simultaneamente
as quantidades de todas as variáveis e pode deixar várias em zero.

Nesta biblioteca, são 185 candidatos (43 forragens, 72 concentrados, 70 minerais) e
115 exclusões: 110 IDs sem composição nas duas tabelas consultadas, um com MS zero,
dois do tipo Milk, um Starter e um No. Essa seleção é um filtro de disponibilidade
de dados e categoria, **não uma certificação de aptidão nutricional ou sanitária**.
A biblioteca NRC tem prioridade quando o mesmo ID consta nas duas fontes; NASEM
completa os IDs ausentes. A composição inteira de cada alimento vem de uma única
linha, registrada no JSON. Não se misturam modelos de exigências NRC/NASEM:
somente os teores de composição são usados como coeficientes fixos do LP.

**O modo `--demo` é sintético:** os 300 nomes não fornecem preços, estoques ou NEL.
Por isso o programa gera um cenário reproduzível, sem atribuir seus valores ao NRC,
NASEM ou mercado. As hipóteses são:

| Categoria | Preço sorteado (R$/kg MS) | NEL arbitrária (Mcal/kg MS) | Máximo arbitrário (kg MS/dia) |
|---|---:|---:|---:|
| Forage | 0,90–1,80 | 1,4 | 14 |
| Conc | 1,50–3,00 | 1,9 | 8 |
| Mineral | 3,00–7,00 | 0 | 0,15 |

O estoque sorteado é entre 5 e 10 vezes o máximo diário; a inclusão mínima é zero.
Esses limites uniformes não consideram toxicidade, absorção, diferenças energéticas
entre alimentos da mesma categoria nem interações ruminais. Não são recomendações
de fornecimento. Os preços e estoques não devem ser comparados aos exemplos anteriores
como se fossem os mesmos dados econômicos.

A vaca também é sorteada com semente fixa. O consumo de MS é calculado pelo calculador
NRC do RuFaS; PB mínima de 16% da MS, NEL mínima de 1,55 Mcal por kg de MS e FDN
entre 28% e 40% são **metas demonstrativas**, não exigências calculadas para esse animal.
`--cp-min` e `--nel-min` permitem informar metas totais explícitas, em kg/dia e Mcal/dia.
Os minerais não têm exigências impostas nesta demonstração.

Com semente 42, a execução gerou uma vaca de 661 kg, DEL 94 e 28 kg de leite/dia.
O resultado foi `optimal`, custo sintético de R$ 23,5276/dia, com alfafa ID 1
(8,5806 kg MN), silagem de mistura de gramíneas/leguminosas ID 97 (16,3282 kg MN)
e farelo de soja por expeller ID 164 (7,1816 kg MN). As 375 verificações passaram.
Foram fornecidos 21,4490 kg MS, 5,7458 kg PB, 33,2459 Mcal NEL e 8,5796 kg FDN.
A PB pode ultrapassar o mínimo porque este modelo não impõe um máximo de PB.

Arquivos gerados em `output/catalog_diet/`:

- `result.json`: perfil, entradas do calculador, 300 registros auditados, fontes,
  185 ingredientes, quantidades inclusive zeros e verificações de restrições.
- `parameters.csv`: valores econômicos, estoque, limites e NEL de cada candidato,
  todos em base MS, além de sua origem. A execução substitui esses arquivos.

Para usar dados próprios, copie o CSV, substitua os valores sintéticos e registre
as fontes. Todas as 185 linhas são obrigatórias; estoque/máximo zero pode representar
um alimento indisponível. Não remova linhas silenciosamente. Execute, por exemplo:

```powershell
.\.venv\Scripts\python.exe -m RUFAS.biophysical.animal.ration.linear_diet_catalog --parameters input/meus_parametros.csv --seed 42 --cp-min 3.5 --nel-min 34 --output-dir output/catalog_diet_real
```

Esse comando não transforma os limites informados em exigências validadas: eles
devem ser fundamentados para o animal. Antes de aplicação prática, faltam parâmetros
nutricionais compatíveis, critérios de uso por ingrediente e reavaliação completa.
Não se preenche composição ausente com zeros para forçar a participação dos 300 IDs.

Testes da extensão: `test_linear_diet_catalog.py` cobre auditoria completa,
reprodutibilidade, solução com todos os candidatos e rejeição de preços negativos,
fontes vazias e registros ausentes/duplicados.

## Objetivo e escopo

Implementação acadêmica de uma dieta de custo mínimo para **um animal ou perfil por execução**.
O núcleo usa `scipy.optimize.linprog(method="highs")`, dados tipados e verificação
numérica independente das restrições. A formulação é linear porque composição,
preços e exigências são parâmetros fixos durante cada execução.

A integração é um adaptador real e testável, dentro do pacote de rações do RuFaS.
Não houve substituição do otimizador da simulação nem integração automática ao ciclo diário.
O ótimo encontrado vale para os parâmetros fornecidos; não comprova adequação nutricional
completa, manutenção da produção leiteira ou aumento de margem econômica.

## Arquitetura investigada

| Componente existente | Responsabilidade e uso nesta entrega |
|---|---|
| `RUFAS/data_structures/feed_storage_to_animal_connection.py` | `Feed`, `NRCFeed`, `NASEMFeed`, `AvailableFeedsBuilder`: composição e dados dos alimentos. O adaptador recebe `Feed`; o exemplo constrói `NRCFeed` com registros reais da biblioteca. |
| `RUFAS/biophysical/feed_storage/feed_manager.py` | Estoques e compras. `update_available_feed_amounts()` atualiza `Feed.amount_available` em kg MS. O chamador deve atualizar e alocar o estoque ao animal antes da otimização. |
| `RUFAS/biophysical/animal/ration/ration_manager.py` | Gerencia configurações da formulação atual. Preservado. |
| `RUFAS/biophysical/animal/ration/ration_optimizer.py` | Otimizador **não linear**, com `scipy.optimize.minimize` e restrições NRC/NASEM. Preservado. |
| `RUFAS/biophysical/animal/nutrients/` | Calculadores NRC/NASEM de exigências, oferta e avaliação nutricional. O exemplo chama `NRCRequirementsCalculator.calculate_requirements`. |
| `RUFAS/biophysical/animal/data_types/nutrition_data_structures.py` | `NutritionRequirements`: MS, energia por função, proteína metabolizável e minerais. O adaptador importa MS diretamente. |
| `RUFAS/biophysical/animal/animal.py` | `Animal.calculate_nutrition_requirements`, `nutrition_requirements`, peso e DEL. `profile_from_animal` lê um animal já inicializado. |
| `RUFAS/biophysical/animal/milk/milk_production.py` | Produção diária e composição configurada do leite. Lidas pelo adaptador do animal. |

O modelo não linear existente calcula ofertas que dependem da dieta, como descontos
de digestibilidade e proteína metabolizável. Reutilizá-lo como se fosse um LP mudaria
o significado do problema. Por isso a opção linear foi adicionada como módulo adjacente,
reutilizando objetos, composição e calculadores existentes, sem alterar suas equações.
A documentação científica existente, `docs/scientific/animal.tex`, descreve a formulação
por lote e registra os preços de compra em **moeda/kg MS**.

Arquivos adicionados:

- `RUFAS/biophysical/animal/ration/linear_diet.py`: dados, LP, validação e resultados.
- `RUFAS/biophysical/animal/ration/linear_diet_adapter.py`: pontes para `Feed`, `NutritionRequirements` e `Animal`.
- `RUFAS/biophysical/animal/ration/linear_diet_example.py`: exemplo reproduzível com biblioteca real.
- `tests/test_biophysical/test_animal/test_ration/test_linear_diet.py`: testes do núcleo e integração.
- `docs/otimizador_linear.md`: este documento.

Não foram modificados os módulos existentes, os dados de entrada, `main.py` ou
`input/task_manager_metadata.json`. SciPy e NumPy já pertencem às dependências do projeto.

## Estruturas, unidades e proveniência

`Ingredient` representa cada item da lista Python:

| Campo | Unidade / significado |
|---|---|
| `identifier`, `name` | Identificador RuFaS e nome do ingrediente |
| `price_per_kg` | Moeda/kg de matéria natural (MN) |
| `stock_kg` | kg MN alocados a este animal para todo o período |
| `dm_fraction` | kg MS/kg MN; por exemplo, 90% → 0,90 |
| `nel_mcal_per_kg_dm` | Mcal NEL/kg MS; coeficiente fixo fornecido explicitamente |
| `cp_fraction`, `ndf_fraction` | kg PB ou FDN/kg MS |
| `mineral_fractions` | Nome → kg de mineral total/kg MS |
| `minimum_kg_day`, `maximum_kg_day` | Limites absolutos de inclusão, kg MN/dia; máximo opcional |
| `sources` | Campo → origem do valor; manter preenchido nas aplicações acadêmicas |

`Ingredient.price_from_tonne(p)` retorna `p/1000`. Essa conversão conserva a base:
R$/t MS vira R$/kg MS, enquanto R$/t MN vira R$/kg MN.

No adaptador `ingredient_from_feed`, com `d = Feed.DM/100`:

```text
preço_MN = Feed.purchase_cost × d
estoque_MN = Feed.amount_available / d
mínimo_MN = Feed.lower_limit / d
máximo_MN = Feed.limit / d
PB_MS = Feed.CP / 100
FDN_MS = Feed.NDF / 100
```

Não há conversão cambial: os preços nativos do RuFaS não se tornam reais automaticamente.
O exemplo atribui seus próprios preços ilustrativos em BRL. Não há compra automática nem
baixa de estoque. Não reutilize o mesmo estoque integral em vários animais sem alocação.

`AnimalProfile` registra peso (kg), DEL (dias inteiros), leite (kg/dia), gordura e proteína
verdadeira do leite (%), origem e um `DietRequirements`. Os dados produtivos documentam
o perfil; o LP usa suas exigências fixas, sem inferir exigências pelo peso ou leite sozinho.
`DietRequirements` contém intervalo de MS (kg/dia), mínimos de PB (kg/dia) e NEL (Mcal/dia),
limites opcionais de FDN como fração da MS e mínimos opcionais de minerais totais (kg/dia).

## Formulação matemática

Sejam `x_i` os kg MN/dia do ingrediente i, `p_i` seu custo por kg MN, `d_i` sua
fração de MS, `c_i` sua PB na MS, `f_i` sua FDN na MS e `e_i` sua NEL em Mcal/kg MS.

```text
minimizar C = Σ p_i x_i

MS_min ≤ Σ d_i x_i ≤ MS_max
Σ d_i c_i x_i ≥ PB_min
Σ d_i e_i x_i ≥ NEL_min
Σ d_i (f_i − FDN_min) x_i ≥ 0      [quando há mínimo de FDN]
Σ d_i (f_i − FDN_max) x_i ≤ 0      [quando há máximo de FDN]
Σ d_i m_ij x_i ≥ Mineral_j_min     [quando há dados compatíveis]
L_i ≤ x_i ≤ U_i
T x_i ≤ S_i
x_i ≥ 0
```

`T` é o período em dias, `S_i` o estoque em kg MN, e `m_ij` a fração do mineral j na MS.
Uma dieta constante será fornecida durante T dias. O custo retornado continua sendo diário;
o custo do período é `T × C`. Os limites de inclusão também continuam diários.

A igualdade de MS é representada por limites inferior e superior iguais. As duas
desigualdades equivalem à igualdade. As proporções de FDN são reformuladas sem divisão
por uma variável; funcionam também quando a MS varia dentro de um intervalo.
Os limites de participação por ingrediente nesta versão são quantidades absolutas,
não percentuais. Todos os coeficientes nutricionais precisam permanecer fixos durante o LP.

Dados não finitos, percentuais usados incorretamente como frações, intervalos invertidos,
IDs repetidos e composição mineral ausente são rejeitados. Composição desconhecida não é zero.
Conflitos entre estoque e inclusão mínima geram diagnóstico específico. Outros problemas
inviáveis retornam o status e a mensagem do HiGHS; esta versão não calcula um conjunto
mínimo de restrições conflitantes.

## Fontes e limites nutricionais

Foram consultados os PDFs locais NRC (2001), o TCC de Daniel Brandão Silva Brito (2026)
e a estrutura do PDF fornecido como NASEM (2021), além do código/documentação RuFaS.
O arquivo NASEM contém páginas digitalizadas; a capa foi inspecionada, mas não foi
realizada transcrição/OCR integral nem extração de novas equações desse livro.

O exemplo reutiliza o calculador NRC do RuFaS. Para a vaca em lactação, o consumo
é baseado em NRC (2001), capítulo 1, página impressa 4, equação 1-2
(página 29 do PDF fornecido):

```text
FCM = 0,4 × leite + 15 × leite × gordura/100
DMI = (0,372 × FCM + 0,0968 × BW^0,75)
      × [1 − exp(−0,192 × (DEL/7 + 3,67))]
```

Unidades: leite e FCM em kg/dia, BW em kg, gordura em %, DEL em dias, DMI em kg MS/dia.
Aplicação descrita no NRC: estimativa de consumo para vacas Holandesas em lactação.
O RuFaS também aplica seus pisos de consumo existentes. O consumo é calculado antes
do LP, com o animal fixo; não se lineariza a potência `BW^0,75`.
Esta previsão não mede o consumo observado nem valida outros grupos animais.

**Divergência identificada no material secundário:** a listagem do TCC na página impressa 45
(página 46 do PDF) usa `DEL/7 − 3,67`; o NRC original e o RuFaS usam `DEL/7 + 3,67`.
Foi mantida a implementação do RuFaS. Também não foi importada a conversão simplificada
de proteína metabolizável para PB da mesma listagem.

O TCC, seção 4.5, páginas impressas 45–48, fundamenta a organização didática do problema:
lista de ingredientes, custo mínimo, matriz de nutrientes, limites e `linprog`/HiGHS.
Seus coeficientes nutricionais não foram tratados como automaticamente equivalentes ao
modelo fisiológico do RuFaS.

Distinções preservadas:

- `Feed.DE` e `NASEMFeed.DE_Base` são energia digestível; nenhum deles é importado como NEL.
- `NutritionRequirements.metabolizable_protein` está em g de proteína metabolizável;
  não é uma exigência de PB e não é convertido automaticamente.
- Energia de lactação isolada não inclui manutenção, atividade, gestação e crescimento.
  O adaptador exige uma meta diária total de NEL documentada, compatível com os coeficientes.
- Minerais dos alimentos são teores totais. Exigências absorvidas do RuFaS não são comparadas
  diretamente a esses teores. Os mínimos de ingestão total devem ser fornecidos explicitamente.
- Os parâmetros NEL, PB e FDN suplementares do exemplo são **ilustrativos**, sem atribuição ao NRC/NASEM.
  A constância de NEL por alimento é uma hipótese do LP; não reproduz os descontos e interações da dieta.

## Relação com as fotografias de aula

As cinco fotografias recebidas em 10/11/2026 foram consideradas como material de referência:

- Imagens `19.37.21`, `19.37.22` e `19.37.23`: lista de alfafa, milho e soja, preços,
  função `min Σ x_i p_i` e nutrientes. Correspondem às estruturas e à formulação implementadas.
  Os números do quadro não possuem composição/unidades de base suficientes para uma dieta validada.
- Imagem `19.37.19`: fluxo simulador → otimizador → cenários e curva de produção.
  O adaptador implementa a ligação de dados; sensibilidade e avaliação produtiva são próximos passos.
- Imagem `19.37.18`: exercício de arroz/milho para **suínos**, com carboidratos e proteína.
  Serve como ilustração de PL; seus limites não foram transferidos para bovinos leiteiros.

Não foi inferida uma equação fisiológica a partir dos desenhos ou dos expoentes manuscritos.

## Execução no Windows

Na raiz do repositório, com Python 3.12 ou 3.13 disponível:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m RUFAS.biophysical.animal.ration.linear_diet_example
```

O ambiente `.venv` desta entrega já foi preparado com Python 3.12; basta executar a última linha.
Não é necessário ativar o ambiente nem alterar a política de execução do PowerShell.
A instalação do ambiente de validação usou `uv` em diretórios `.venv-*`, ignorados pelo Git.
`pypdf` foi utilizado apenas para consultar referências locais, sem virar dependência do módulo.

O exemplo produz uma tabela no terminal e grava `output/linear_diet_example.json`, contendo
animal, exigências, lista de ingredientes com proveniência, período, moeda e resultado.
A execução seguinte substitui esse arquivo de exemplo. O diretório `output` já é ignorado pelo projeto.
IDs inteiros são serializados como chaves de texto no JSON; a API Python mantém chaves inteiras.

## Exemplo de entrada e resultado real

Animal: 650 kg, DEL 100, 30 kg leite/dia, gordura 3,8%, proteína verdadeira 3,2%.
O calculador NRC do RuFaS retorna **22,545320 kg MS/dia** para o cenário especificado.
Metas suplementares ilustrativas: PB ≥ 3,6 kg/dia, NEL ≥ 35 Mcal/dia, FDN entre
28% e 40% da MS. Período: 7 dias, com dieta diária constante.

| ID | Ingrediente | MS (%) | PB (% MS) | FDN (% MS) | NEL ilustrativa (Mcal/kg MS) | Preço ilustrativo (R$/t MS) | Estoque (kg MS) | Máximo (kg MS/dia) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | Alfafa, farinha | 90,3 | 19,2 | 41,6 | 1,3 | 1400 | 150 | 16 |
| 44 | Milho, moagem média | 88,1 | 9,4 | 9,5 | 2,0 | 1800 | 100 | 10 |
| 167 | Farelo de soja | 89,5 | 53,8 | 9,8 | 1,8 | 2800 | 60 | 6 |

Composição: registros de `input/data/feed/NRC_comp.csv`. Nomes explicativos em português;
preços, estoques, NEL e limites operacionais definidos em `example_feeds`/`example_inputs`.
O JSON exportado é a referência completa dos valores efetivamente carregados.

| Ingrediente | kg MN/dia | kg MS/dia | R$/dia |
|---|---:|---:|---:|
| Alfafa | 15,9119 | 14,3685 | 20,1158 |
| Milho | 9,0957 | 8,0133 | 14,4239 |
| Farelo de soja | 0,1828 | 0,1636 | 0,4580 |
| **Total** | **25,1904** | **22,5453** | **34,9978** |

Resultado: `optimal`; PB 3,6000 kg/dia, NEL 35,0000 Mcal/dia, FDN 6,7546 kg/dia
(aproximadamente 29,96% da MS). Todas as 11 verificações são satisfeitas:
MS, PB, NEL, dois limites de FDN, três intervalos de inclusão e três estoques.
Os arredondamentos desta tabela são apenas de apresentação; o resultado interno não é arredondado.

O custo mínimo é o menor custo diário permitido por **este conjunto de ingredientes,
preços, estoques e restrições**. Não significa melhor desempenho biológico, lucro máximo
ou economia comprovada em relação a uma dieta anterior.

## Uso por outros componentes

```python
from RUFAS.biophysical.animal.ration.linear_diet import optimize_diet
from RUFAS.biophysical.animal.ration.linear_diet_example import example_inputs

animal, ingredientes = example_inputs()  # lista Python de Ingredient
resultado = optimize_diet(animal, ingredientes, period_days=7)
if resultado.status == "optimal":
    quantidades_mn = resultado.quantities_kg_day
    racao_rufas = resultado.ration_kg_dm_day  # dict[RUFAS_ID, kg MS/dia]
```

Para um animal real inicializado, construa os limites com
`requirements_from_rufas(animal.nutrition_requirements, cp_min_kg=..., nel_min_mcal=...,
supplemental_source=...)` e use `profile_from_animal(animal, limites)`.
Cada alimento é convertido por `ingredient_from_feed`, exigindo NEL e sua origem.
São necessários um snapshot atualizado e parâmetros suplementares compatíveis.

`ration_kg_dm_day` tem o formato de entrada de `NutritionSupplyCalculator.calculate_nutrient_supply`.
Os testes comprovam a mesma oferta de PB e FDN com `FeedInRation` e os cálculos existentes.
Uma reavaliação energética/proteica completa pelo modelo não linear pode apontar diferenças;
o status ótimo do LP não substitui essa reavaliação. O módulo não aplica a dieta à simulação.

## Validação e testes

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_biophysical/test_animal/test_ration/test_linear_diet.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_biophysical/test_animal/test_ration tests/test_biophysical/test_animal/test_nutrients tests/test_biophysical/test_animal/test_data_types/test_nutrition_data_structures.py -q
```

Na validação de 10/11/2026, a segunda chamada executou **427 testes, todos aprovados**,
incluindo 27 casos novos. Não foi executada a suíte completa da fazenda.
Flake8 e Black aprovaram os quatro arquivos Python novos; MyPy aprovou os três
módulos de implementação com `--follow-imports=silent`. Ambiente utilizado:
Python 3.12.16, NumPy 2.2.0, SciPy 1.18.1 e pytest 9.2.0.
Foram cobertos ótimo analítico conhecido, MS/MN, preço por tonelada, mínimos/máximos,
estoques por período, PB/NEL/FDN, minerais, entradas inválidas, inviabilidade,
falha numérica e rejeição de uma falsa solução ótima pelo verificador independente.
Os testes de integração usam `NRCFeed`, biblioteca real, calculador NRC, `NutritionRequirements`,
`FeedInRation`, calculador de oferta e snapshot mínimo das classes `Animal`/`MilkProduction`.
O snapshot mínimo não equivale à execução de uma fazenda completa.

Cada restrição é recalculada após o solver, inclusive os limites de inclusão e estoques.
A tolerância absoluta padrão é `1e-7` na unidade da linha; resíduos de FDN são kg MS
ponderados pela diferença de frações. O chamador pode ajustar a tolerância positiva
até `1e-4`. A tolerância do verificador é independente da usada internamente pelo solver.
Statuses sem ótimo (`infeasible`, `solver_failure`, `verification_failed`) não expõem
uma ração utilizável nem custo como se fossem solução ótima.

## Limitações e evolução

Não há formulação simultânea de lotes, compras, perdas de armazenamento, custos fixos,
aceitabilidade, aminoácidos, amido, FDN de forragem ou adaptação ruminal neste LP.
Minimizar custo com PB total e NEL fixa é uma simplificação acadêmica explícita.
Minerais têm mínimos opcionais de ingestão total; limites máximos não foram implementados.
A rastreabilidade por campo deve ser mantida pelo chamador quando fornecer dados próprios.

A API separa entradas de resultados, permitindo gerar cenários com `dataclasses.replace`
e repetir o LP variando preços, estoques e exigências. A análise de sensibilidade,
comparação com dieta original e IOFC exigem cenários e dados econômicos adicionais.
Para integrar ao ciclo diário, será necessário coordenar alocação/baixa de estoque,
reavaliar a dieta pelo modelo nutricional completo e definir o tratamento das divergências.
Interface gráfica e previsão de resposta produtiva ficam para etapas posteriores.
