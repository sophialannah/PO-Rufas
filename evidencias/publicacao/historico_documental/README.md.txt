# PO-RuFaS | Otimização Inteligente de Dietas

Projeto acadêmico de Pesquisa Operacional desenvolvido por **Sophia Lannah Beatriz Ferreira de Sousa** e **Anderson Alberto da Costa Silva**, integrado ao simulador RuFaS.

O sistema formula uma dieta diária de custo mínimo para uma vaca Holandesa em lactação, com preços, composição, estoque e limites definidos. A solução é verificada matematicamente, enviada ao RationManager e avaliada pelos componentes nutricionais do RuFaS.

## Documentação e objetivos

A aplicação demonstra modelagem linear, conversões de unidades, integração com dados reais do simulador e distinção entre viabilidade matemática e parecer nutricional. [Sumário dos 14 capítulos](docs/po_rufas/README.md)

## Tecnologias e arquitetura

Python 3.12/3.13, Streamlit 1.67.0, Pandas, NumPy e SciPy/HiGHS compõem o fluxo acadêmico. O RuFaS preserva seu otimizador SLSQP. O frontend importa os módulos Python diretamente.

```mermaid
flowchart LR
    A[Animal RuFaS] --> B[Exigências NRC]
    C[NRCFeed e parâmetros] --> D[Adaptadores]
    B --> D
    D --> E[LP HiGHS]
    E --> F[Checks do LP]
    F --> G[RationManager]
    G --> H[Oferta nativa]
    H --> I[NutritionEvaluator]
    I --> J[Resultados Streamlit]
```

## Funcionalidades

- Seleção de animais do arquivo de população e consulta de requisitos.
- Catálogo NRC com composição e parâmetros econômicos editáveis.
- Otimização com MS, PB, NEL, FDN, estoque e inclusão.
- Mínimos opcionais de fósforo e cálcio absorvíveis coerentes com o motor NRC local.
- Diagnóstico independente da exigência de fósforo NASEM 2021.
- Dieta em matéria natural e seca, custos, gráficos e critérios nutricionais individuais.
- Reotimização de cenários e exportação CSV, JSON e resumo Markdown.

## Instalação e execução no Windows

Na raiz, para ambiente novo:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pip install -r frontend/requirements.txt
.\frontend\iniciar_frontend.bat
```

Em ambiente preparado, execute apenas o BAT e abra http://127.0.0.1:8501. [Manual e alternativas para venv sem pip](frontend/README.md)

A demonstração passa pelas abas **Animal**, **Ingredientes**, **Otimização** e **Resultados**. A aba **Visão geral** mostra o fluxo e **Cenários** recalcula variações. Para minerais, selecione o fosfato 231 e informe os [parâmetros reproduzíveis](docs/po_rufas/03-dados.md), depois ative os mínimos P/Ca.

Alternativa por terminal:

```powershell
.\apresentacao\demonstracao_integrada.bat --auto
```

Essa alternativa conserva a referência de três alimentos e mínimos minerais desligados. [Guia de demonstração acadêmica](apresentacao/guia_demonstracao_web.md)

## Modelo matemático

$$\min C=\sum_{i\in I}p_i x_i$$

A variável x mede kg MN/animal/dia. As restrições limitam MS, PB, NEL, proporção de FDN, estoque por período e inclusão. Os mínimos absorvíveis de P/Ca são opcionais. Os coeficientes são fixos durante a resolução. [Equações, unidades, hipóteses e funções responsáveis](docs/po_rufas/04-modelagem.md)

## Integração e resultados

O fluxo NRC usa Animal, NRCFeed, adaptadores, HiGHS, RationManager, FeedInRation, NutritionSupplyCalculator e NutritionEvaluator. O cenário suplementado de sete dias usa composição do fosfato bicálcico do catálogo e valores econômicos ilustrativos.

| Animal | Leite assumido kg/dia | Custo com suplemento R$/dia | Checks LP | Critérios nativos |
|---|---:|---:|---|---|
|98605|30|35,3416|15/15|11/11 atendidos|
|93785|31|35,2480|15/15|11/11 atendidos|

As referências de três alimentos, sem mínimos minerais ativos, custam R$35,1059 e R$34,9440 e reprovam por P absorvível. A aprovação suplementada resulta da avaliação nativa após correção da comparação de gordura máxima. [Resultados e condições](docs/po_rufas/10-resultados.md)

## Testes

A suíte relevante foi reexecutada nesta revisão e retornou **462 aprovados em 19,24 s**. Abrange frontend, rações, nutrientes e estruturas nutricionais.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/test_frontend.py tests/test_biophysical/test_animal/test_ration tests/test_biophysical/test_animal/test_nutrients tests/test_biophysical/test_animal/test_data_types/test_nutrition_data_structures.py -q
```

[Registro de validação e distinção de evidências antigas](docs/po_rufas/VALIDACAO.md)

## Limitações e autoria

O padrão integrado é NRC 2001. O cálculo NASEM é um diagnóstico de exigência de P. PB, NEL, preços e estoques da demonstração são hipóteses identificadas. A avaliação não cobre limites superiores minerais, Ca:P ou todos os aspectos produtivos. A integração termina no parecer nutricional, antes do ciclo diário e da baixa automática de estoque.

O custo é condicionado às entradas e restrições. O ensaio histórico SLSQP tem consumo e formulação diferentes. [Comparação dos modelos](docs/po_rufas/09-comparacao.md) · [Limitações](docs/po_rufas/13-limitacoes.md)

O simulador, dados e modelos originais pertencem aos autores do [RuFaS](https://github.com/RuminantFarmSystems/RuFaS). O projeto declara GPL-3.0-only no pyproject.toml. A documentação original permanece em [docs/README_RuFaS_original.md](docs/README_RuFaS_original.md). [Referências científicas, glossário e atribuição](docs/po_rufas/14-referencias.md)


## Estudo comparativo reproduzível

A aba Cenários agora executa **A · Mesmo LP** (HiGHS e SLSQP) e **B · Formulações diferentes** (LP e RuFaS nativo). O estudo inicial usa os animais 98605 e 93785 com cinco repetições por método. O experimento A reproduziu os mesmos custos nos dois algoritmos. O menor custo do nativo em B acompanha outras condições de consumo e restrições.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m experiments.comparison --repeats 5
```

[Evidências, versões, tabelas, gráficos e comandos](evidencias/comparacao/README.md) · [Manual com capturas reais](docs/po_rufas/12-manual.md). A suíte ampliada retornou 466 testes aprovados. A cotação IFAG de milho alimenta um cenário econômico separado e parcial; os casos demonstrativos de regressão foram preservados.


## Integração dinâmica ao simulador anual

A área **Simulação anual** executa o motor FULL_FARM real, com evolução animal, formulação, consumo e FeedManager. O padrão native_slsqp mantém o mecanismo original. A estratégia linear_highs usa LPs HiGHS sequenciais para vacas lactantes NRC e fallback explícito quando necessário.

Duas execuções de 365 dias foram concluídas. A primeira comparação encontrou aumento de 9,05% no custo estimado da estratégia híbrida, com 352 aceites HiGHS e 13 fallbacks. Os valores são condicionados a preços demonstrativos e ao pequeno rebanho experimental.

[Evidências, auditoria e reprodução anual](evidencias/anual/README.md) · [Manual](docs/po_rufas/12-manual.md). A comparação estática e os cenários 98605/93785 continuam disponíveis.




## Correção dinâmica e comparação controlada — 27/11/2026

Os resultados da integração anual anterior são históricos. A causa do custo anormal do primeiro dia foi reproduzida e corrigida: a região local não pode ser tratada como limite físico de suplementação, e a primeira candidata aprovada não encerra a minimização. Foram separados os requisitos NRC 2001 e os tetos totais NRC 2005, aplicados igualmente aos dois solvers na comparação controlada.

SLSQP controlado: **2.319,35 UM/ano**; HiGHS híbrido ampliado e exclusivo: **2.316,45 UM/ano**, diferença de **0,125%** neste cenário demonstrativo. O exclusivo completou **365 dias e 1.002 chamadas sem SLSQP**, com 998 curral-dias adultos aprovados e dentro dos tetos minerais. Das chamadas HiGHS, 43 conservaram candidatas viáveis sem atingir o critério de convergência; não há certificado de ótimo global. O modo NASEM e os demais agrupamentos não foram universalmente validados.

**954 testes passaram**, incluindo os 937 anteriores e uma simulação exclusiva anual real. [Resultados, arquivos, reprodução e limitações](evidencias/correcao_dinamica/README.md). A aba anual oferece as estratégias e seus registros de convergência. Nenhum commit, push ou merge foi feito automaticamente.
