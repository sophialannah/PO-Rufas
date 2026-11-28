# Comparação dos otimizadores
[Sumário](README.md)

## Três perguntas diferentes

| Experimento | Mantém | Varia | Interpretação |
|---|---|---|---|
| A — mesmo LP estático | Objetivo, MN, matriz, bounds e dados | HiGHS/SLSQP | Comparação do algoritmo para a mesma formulação |
| B — formulações estáticas distintas | Animal, padrão e fontes | LP PB/NEL fixas versus modelo nativo | Diferença de formulação, não vantagem isolada do solver |
| Ano controlado | Condições iniciais, clima, manejo, preços e política mineral | SLSQP versus SLP/HiGHS no ciclo real | Desempenho das estratégias nesse cenário |

O experimento A executável usa Jacobianas analíticas para SLSQP linear, igualdade MS explícita, ftol=10⁻⁹ e maxiter=1000. Há aquecimento excluído e repetições registradas. O ponto inicial não deriva da solução HiGHS. Os dois algoritmos reproduziram os custos dentro das tolerâncias.

No B, consumo, energia e MP pertencem à formulação nativa; não são o mesmo problema do LP estático. Os valores históricos dos animais 98605/93785 continuam nas [evidências comparativas](../../evidencias/comparacao/README.md). Duas vacas/quatro alimentos não fundamentam superioridade geral.

## Resultado anual controlado vigente

As mesmas linhas NRC 2005 de minerais totais foram aplicadas aos dois solvers, com requisitos NRC 2001 nativos. Não se inferiu economia comparando modelos com políticas minerais diferentes.

| Grandeza | SLSQP controlado | HiGHS exclusivo |
|---|---:|---:|
| Consumo valorizado, UM | 2.319,34875854 | 2.316,45106770 |
| Despesa de compra, UM | 2.323,21061538 | 2.320,31250669 |
| Leite, kg | 140.223,666523 | 140.223,666523 |

Redução no consumo valorizado: 0,1249355%. O híbrido ampliado reproduziu os valores do exclusivo, sem precisar de fallback neste cenário. Não se generaliza economia a preços comerciais ou outros rebanhos e não se usa execução concorrente como benchmark de velocidade.

O exclusivo teve 1.002 formulações aceitas, mas somente 959 convergentes; 43 conservaram soluções viáveis sem convergência. As avaliações adultas e os 252 registros de bezerros não aprovados em cada estratégia são contabilizados separadamente. [Resultados](10-resultados.md).

## Reprodução

`python -X utf8 -m experiments.comparison --repeats 5 --output output/comparacao_nova` executa A/B. Para o anual, use experiments.annual com native_slsqp, linear_highs_all ou linear_highs_exclusive e diretórios novos.

## Histórico preservado

A primeira estratégia anual, limitada a lactação com fallback, teve 352 aceites e aumento de 9,05% no custo. Isso antecede a correção do primeiro dia e não é resultado vigente. [Relatório histórico](../../evidencias/anual/README.md).
