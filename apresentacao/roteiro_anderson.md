# Roteiro individual — Anderson

Siga o [cronograma completo](roteiro_completo.md). O conteúdo abaixo pertence à versão dinâmica validada; os roteiros anteriores estão preservados no histórico documental.

## 00:45–01:45 — Slide 2 — arquitetura

HerdManager configura o otimizador de cada curral. A cada dia, Pen recebe requisitos atualizados e chama o método escolhido. O HiGHS devolve uma candidata no contrato nativo, que é conferida no modelo nutricional original. FeedManager atende os pedidos e retira estoque real; o observador registra, sem fazer outra dedução. Growing, close_up e lactação usam suas próprias restrições. Bezerros seguem uma rotina prescrita, fora do otimizador. O exclusivo não tem fallback para SLSQP.

## 03:35–04:25 — Demonstração — resultado

O ano controlado registrou 2.319,34875854 unidades monetárias no SLSQP e 2.316,45106770 no exclusivo: redução de 0,1249355%, com preços demonstrativos. O leite foi 140.223,666523 quilos em ambos. O exclusivo teve 1.002 formulações HiGHS e nenhuma chamada SLSQP. Foram 959 convergentes e 43 viáveis sem convergência. Há 998 curral-dias adultos aprovados, mas também 252 registros de bezerros não aprovados em cada estratégia. Não afirmamos aprovação do rebanho inteiro.

## 04:25–05:00 — Slide 4 — validação e limites

A referência computacional tem 969 testes aprovados, incluindo um ano exclusivo real. A base anterior de 954 casos foi conferida em cópia isolada, com venv nova; os 15 novos casos passaram na revisão de usabilidade. A solução não certifica ótimo global não linear nem vantagem econômica universal. Permanecem limitações dos coeficientes minerais, da resposta biológica e dos indicadores de bezerros. As evidências históricas foram preservadas. Encerramos a apresentação e iniciamos cinco minutos de perguntas.
