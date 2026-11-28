# Roteiro individual — Sophia

Siga o [cronograma completo](roteiro_completo.md). O conteúdo abaixo pertence à versão dinâmica validada; os roteiros anteriores estão preservados no histórico documental.

## 00:00–00:45 — Slide 1 — objetivo

Nosso projeto integra um otimizador de dietas ao RuFaS. Mantivemos o LP estático e acrescentamos programação linear sequencial no ciclo real da fazenda. O cenário NRC completou 365 dias com formulação, evolução animal, compras, consumo e baixa de estoque. Os dados de composição vêm do simulador; os preços são demonstrativos. A contribuição é uma integração verificável, sem alterar a biologia para criar resultados.

## 01:45–03:00 — Slide 3 — modelos

No LP estático, as quantidades em matéria natural são as variáveis; composição e metas de PB e NEL são fixas. O custo é a soma de preço vezes quantidade. No modelo dinâmico, o contrato é em matéria seca e as restrições nutricionais originais podem ser não lineares. Calculamos aproximações locais e resolvemos LPs dentro de uma região de confiança. A candidata precisa passar nas funções originais após arredondamento. A busca continua além da primeira aprovação e conserva a melhor solução viável. Os tetos totais de cálcio e fósforo NRC 2005 são iguais para os dois solvers controlados; os requisitos absorvíveis continuam NRC 2001. Ótimo de um LP local não significa ótimo global do modelo não linear.

## 03:00–03:35 — Demonstração — seleção

Na área Simulação anual, vemos cinco opções. Vou mostrar Comparação SLSQP versus HiGHS exclusivo. O aviso informa que o exclusivo não tem fallback. As duas estratégias recebem as mesmas entradas. O progresso e os resultados vêm de processos reais. Se executarmos apenas um dia ao vivo, esse será um teste curto; os números anuais pertencem às evidências de 365 dias.
