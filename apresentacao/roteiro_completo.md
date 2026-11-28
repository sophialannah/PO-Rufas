# Roteiro completo — versão final

Quatro slides; **300 segundos de exposição/demonstração + 300 segundos de perguntas**. Tempos são metas de ensaio, não gravações medidas. Os números oficiais e limites estão em [resultados validados](resultados_validados.md).

| Intervalo | Etapa | Responsável | Duração |
|---|---|---|---:|
| 00:00–00:45 | Slide 1 — objetivo | Sophia | 45 s |
| 00:45–01:45 | Slide 2 — arquitetura | Anderson | 60 s |
| 01:45–03:00 | Slide 3 — modelos | Sophia | 75 s |
| 03:00–03:35 | Demonstração — seleção | Sophia | 35 s |
| 03:35–04:25 | Demonstração — resultado | Anderson | 50 s |
| 04:25–05:00 | Slide 4 — validação e limites | Anderson | 35 s |

## 00:00–00:45 — Slide 1 — objetivo

**Sophia — 45 segundos**

Nosso projeto integra um otimizador de dietas ao RuFaS. Mantivemos o LP estático e acrescentamos programação linear sequencial no ciclo real da fazenda. O cenário NRC completou 365 dias com formulação, evolução animal, compras, consumo e baixa de estoque. Os dados de composição vêm do simulador; os preços são demonstrativos. A contribuição é uma integração verificável, sem alterar a biologia para criar resultados.

## 00:45–01:45 — Slide 2 — arquitetura

**Anderson — 60 segundos**

HerdManager configura o otimizador de cada curral. A cada dia, Pen recebe requisitos atualizados e chama o método escolhido. O HiGHS devolve uma candidata no contrato nativo, que é conferida no modelo nutricional original. FeedManager atende os pedidos e retira estoque real; o observador registra, sem fazer outra dedução. Growing, close_up e lactação usam suas próprias restrições. Bezerros seguem uma rotina prescrita, fora do otimizador. O exclusivo não tem fallback para SLSQP.

## 01:45–03:00 — Slide 3 — modelos

**Sophia — 75 segundos**

No LP estático, as quantidades em matéria natural são as variáveis; composição e metas de PB e NEL são fixas. O custo é a soma de preço vezes quantidade. No modelo dinâmico, o contrato é em matéria seca e as restrições nutricionais originais podem ser não lineares. Calculamos aproximações locais e resolvemos LPs dentro de uma região de confiança. A candidata precisa passar nas funções originais após arredondamento. A busca continua além da primeira aprovação e conserva a melhor solução viável. Os tetos totais de cálcio e fósforo NRC 2005 são iguais para os dois solvers controlados; os requisitos absorvíveis continuam NRC 2001. Ótimo de um LP local não significa ótimo global do modelo não linear.

## 03:00–03:35 — Demonstração — seleção

**Sophia — 35 segundos**

Em Ingredientes, carregamos o cenário validado com quatro alimentos; a multisseleção preserva os parâmetros e destaca pendências. P e Ca são obrigatórios; NASEM fica avançado e separado do NRC. Em Simulação anual, carregamos as evidências de 365 dias sem reexecutá-las. Os cartões mostram custos e diferenças reais, identificando dinamicamente a estratégia mais econômica. O exclusivo segue sem fallback.

## 03:35–04:25 — Demonstração — resultado

**Anderson — 50 segundos**

O ano controlado registrou 2.319,34875854 unidades monetárias no SLSQP e 2.316,45106770 no exclusivo: redução de 0,1249355%, com preços demonstrativos. O leite foi 140.223,666523 quilos em ambos. O exclusivo teve 1.002 formulações HiGHS e nenhuma chamada SLSQP. Foram 959 convergentes e 43 viáveis sem convergência. Há 998 curral-dias adultos aprovados, mas também 252 registros de bezerros não aprovados em cada estratégia. Não afirmamos aprovação do rebanho inteiro.

## 04:25–05:00 — Slide 4 — validação e limites

**Anderson — 35 segundos**

A referência computacional tem 969 testes aprovados, incluindo um ano exclusivo real. A base anterior de 954 casos foi conferida em cópia isolada, com venv nova; os 15 novos casos passaram na revisão de usabilidade. A solução não certifica ótimo global não linear nem vantagem econômica universal. Permanecem limitações dos coeficientes minerais, da resposta biológica e dos indicadores de bezerros. As evidências históricas foram preservadas. Encerramos a apresentação e iniciamos cinco minutos de perguntas.

## 05:00–10:00 — perguntas

Sophia conduz modelagem e unidades; Anderson, integração e validação. Ambos devem estudar as limitações e o [banco de perguntas](perguntas_e_respostas.md). Encerrar a atividade às 10:00.
