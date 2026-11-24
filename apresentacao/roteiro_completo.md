# Roteiro completo — 5 minutos de apresentação + 5 de arguição

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

| Intervalo | Etapa | Responsável | Duração |
|---|---|---|---:|
| 00:00–00:45 | Slide 1 — projeto | Sophia Lannah Beatriz Ferreira de Sousa | 45 s |
| 00:45–01:45 | Slide 2 — arquitetura | Anderson Alberto da Costa Silva | 60 s |
| 01:45–03:00 | Slide 3 — modelo | Sophia Lannah Beatriz Ferreira de Sousa | 75 s |
| 03:00–03:35 | Demonstração — entradas | Sophia Lannah Beatriz Ferreira de Sousa | 35 s |
| 03:35–04:25 | Demonstração — resultado | Anderson Alberto da Costa Silva | 50 s |
| 04:25–05:00 | Slide 4 — conclusão | Anderson Alberto da Costa Silva | 35 s |
| 05:00–10:00 | Perguntas | Ambos | 300 s |

São cinco minutos exclusivos de apresentação, seguidos de cinco minutos de arguição: a demonstração tem **85 segundos**, divididos em 35 + 50. São **300 segundos de exposição + 300 segundos adicionais de perguntas = 600 segundos**.

Use um cronômetro visível. As durações são metas de ensaio, não uma medição das vozes dos integrantes. Ensaie as falas com pausas para respiração, troca de janela e execução. Ajuste o ritmo sem omitir as limitações. Às 05:00, encerre a exposição; às 10:00, encerre as perguntas.

Passe pelos slides 1 a 3 e mude para o navegador. Faça a demonstração seguindo o [guia web](guia_demonstracao_web.md) e volte ao PowerPoint para o slide 4. Deixe o terminal preparado como alternativa. Sophia fala por 155 s (2min35s) e Anderson por 145 s (2min25s).

## 00:00–00:45 — Slide 1 — projeto

**Sophia Lannah Beatriz Ferreira de Sousa — 45 segundos**

> Nosso projeto aplica Pesquisa Operacional à formulação de dietas para bovinos leiteiros. Buscamos as quantidades de ingredientes que atendem às restrições com o menor custo diário. Desenvolvemos um módulo linear integrado às estruturas do RuFaS. Vamos mostrar o modelo e uma execução real, com dados demonstrativos claramente identificados. A alimentação envolve uma decisão recorrente: um ingrediente barato pode fornecer poucos nutrientes e exigir uma quantidade maior. Por isso, avaliamos a combinação completa, respeitando disponibilidade e limites nutricionais. O objetivo desta entrega é demonstrar uma decisão reproduzível e verificável. Anderson vai explicar como os dados chegam ao modelo.

**Cartão:** Problema → quantidades → custo mínimo → módulo linear → demonstração identificada.

## 00:45–01:45 — Slide 2 — arquitetura

**Anderson Alberto da Costa Silva — 60 segundos**

> O programa recebe o perfil da vaca, a composição dos alimentos, os preços, estoques e metas nutricionais. Reutilizamos a biblioteca de alimentos e o calculador NRC do RuFaS para estimar o consumo de matéria seca. Os adaptadores convertem as unidades e entregam os dados ao otimizador. A saída contém a dieta e sua verificação. A aplicação automática ao ciclo diário da fazenda ainda não foi implementada. Essa separação permite conferir cada entrada antes de resolver: o perfil descreve o animal; a composição informa o que cada alimento fornece; preços e estoques definem o cenário econômico. O adaptador compatibiliza matéria natural e matéria seca, evitando misturar bases de cálculo. Neste exemplo, proteína, energia e limites de fibra são metas ilustrativas explícitas. Agora Sophia apresenta como esses dados se tornam variáveis e restrições.

**Cartão:** Animal + ingredientes + preços/estoques → adaptadores → SciPy/HiGHS → dieta. MS: RuFaS. Sem ciclo diário.

## 01:45–03:00 — Slide 3 — modelo

**Sophia Lannah Beatriz Ferreira de Sousa — 75 segundos**

> Cada variável representa os quilos diários de um ingrediente em matéria natural. Multiplicamos essas quantidades pelos preços e minimizamos a soma. As restrições controlam matéria seca, proteína, energia, fibra, estoques e limites de inclusão. A composição é convertida para a mesma base de unidades. Os coeficientes permanecem fixos durante a otimização, tornando o problema linear. As proporções de fibra são reescritas sem divisão por variável. Por exemplo, o total de proteína é a soma da quantidade de cada alimento multiplicada por sua fração de matéria seca e seu teor proteico. Esse total precisa atingir a meta. Para o estoque, multiplicamos a quantidade diária pelo período e limitamos ao disponível. Não multiplicamos variáveis de decisão entre si. O perfil da vaca e suas metas ficam fixos durante essa resolução; não linearizamos todo o sistema nutricional NRC ou NASEM. Usamos a função linprog do SciPy com HiGHS para procurar o mínimo sujeito a essas condições. Depois, o programa confere a solução retornada. Agora vamos executar.

**Cartão:** x = kg MN/dia; p = R$/kg MN; min Σpx; MS/PB/NEL/FDN; estoque/inclusão; coeficientes fixos.

## 03:00–03:35 — Demonstração — entradas

**Sophia Lannah Beatriz Ferreira de Sousa — 35 segundos**

> O arquivo do RuFaS traz a vaca 98605 com 627,56 quilos, 100 dias em lactação e paridade quatro. Assumimos 30 quilos de leite por dia. Na aba Ingredientes, vemos alfafa, milho e farelo de soja com composição NRC e preços ilustrativos. Na aba Otimização, o consumo de matéria seca vem do cálculo NRC. O período é de sete dias. Vou clicar em Executar otimização.

**Cartão:** Animal 98605 → Ingredientes → Otimização → Executar otimização → passar a Anderson.

## 03:35–04:25 — Demonstração — resultado

**Anderson Alberto da Costa Silva — 50 segundos**

> Em Resultados, o HiGHS retornou a solução ótima para os parâmetros deste cenário. O custo diário é de cerca de 35 reais e as onze verificações do modelo linear passaram. A tabela mostra as quantidades de alfafa, milho e farelo de soja em matéria natural e seca. O RationManager recebeu a dieta em percentuais de matéria seca e recuperou as quantidades para calcular a oferta de nutrientes. O NutritionEvaluator apontou um déficit de 6,68 gramas diárias de fósforo absorvível. Por isso, o parecer do RuFaS é Não aprovada. O fósforo absorvível está entre os critérios da avaliação nativa e fica fora das metas configuradas no modelo linear desta execução.

**Cartão:** Resultados → R$ 35,1059/dia → 11/11 no LP → RationManager → déficit de P → parecer Não aprovada.

## 04:25–05:00 — Slide 4 — conclusão

**Anderson Alberto da Costa Silva — 35 segundos**

> Entregamos um núcleo executável, com conversões de unidades e verificação das restrições. A validação executou 442 testes dos componentes relacionados, todos aprovados. A contribuição é uma alternativa linear integrada aos dados do RuFaS. O próximo passo é substituir as hipóteses demonstrativas e ampliar a validação nutricional. Ainda precisamos incorporar o resultado ao ciclo diário da simulação e investigar cenários com dados econômicos documentados. Não demonstramos um percentual de economia em fazenda. Encerramos os cinco minutos de apresentação e iniciamos os cinco minutos de perguntas.

**Cartão:** 442 testes → contribuição linear → parâmetros reais e validação completa → perguntas.

## 05:00–10:00 — perguntas

Sophia inicia respostas de modelagem; Anderson, de integração e validação. Cada resposta deve durar 15–35 segundos. O banco de perguntas serve para estudo; não se pretende responder todas as perguntas nos cinco minutos adicionais.


## Integração comprovada nesta versão

Integração comprovada: Animal 98605 construído de animal_population.json → cálculo NRC → lista NRCFeed/Ingredient → HiGHS → percentuais MS → RationManager → FeedInRation → NutritionSupplyCalculator e NutritionEvaluator. DEL 100, leite 30 kg/dia assumido. DMI calculada; PB/NEL/FDN externas; déficit diagnóstico de P absorvível (-6,68 g/dia) sem suplemento mineral no LP. O ciclo diário da fazenda não foi executado. Demo: demonstracao_integrada.bat. 5 minutos de apresentação + 5 minutos adicionais de perguntas.

Resultado: R$ 35,1059/dia. Relatório: [integração real](../docs/integracao_real_rufas.md).
