# Contextualização
[Sumário](README.md)

O PO-RuFaS aplica Pesquisa Operacional à formulação de dietas dentro do RuFaS. Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva desenvolveram o módulo acadêmico preservando a autoria e a biologia do simulador original.

O objetivo principal foi atingido no cenário NRC validado: **365 dias FULL_FARM**, **1.002 formulações HiGHS sem chamadas SLSQP no exclusivo**, requisitos recalculados, evolução animal, consumo, compras e baixa real de estoque. A referência computacional possui **954 testes aprovados**.

## Dois escopos

O LP estático mantém requisitos e coeficientes fixos durante uma resolução. Serve à demonstração individual, conversões MN/MS, comparação de algoritmos e avaliação nutricional posterior.

O modelo dinâmico usa programação linear sequencial sobre as funções nativas não lineares da categoria, recebe novos requisitos por curral/dia e participa do ciclo de alimentação. Não repete uma fotografia animal por 365 iterações.

## Resultado e interpretação

SLSQP controlado: 2.319,34875854 UM; HiGHS exclusivo: 2.316,45106770 UM; redução de 0,1249355%, com preços demonstrativos. Leite: 140.223,666523 kg em ambos. Há 959 formulações convergentes e 43 soluções viáveis sem convergência, sem certificado de ótimo global não linear.

Os 998 curral-dias adultos aprovados não incluem os 252 registros de bezerros não aprovados em cada estratégia. O fluxo de bezerros possui limitações próprias.

## Histórico

A etapa estática antecedeu a comparação experimental e a primeira integração anual híbrida. O aumento histórico de +9,05% decorreu quase integralmente de um defeito no primeiro dia, depois reproduzido e corrigido. [Evidências anteriores](../../evidencias/anual/README.md) e [resultados oficiais corrigidos](../../evidencias/correcao_dinamica/README.md) são distintos.

A base Git é 5bb6775, branch fix/validacao-nutricional-rufas, acrescida das alterações locais revisadas. O [relatório de publicação](../../evidencias/publicacao/README.md) identifica o candidato, sem commit ou envio automático.
