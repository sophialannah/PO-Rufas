# Minerais e separação NRC/NASEM
[Sumário](README.md)

## Requisitos absorvíveis e composição total

O mínimo P é max(P NRC, P processual); Ca usa a exigência NRC do curral. O motor local calcula oferta absorvível por classe alimentar:

| Classe | Coeficiente P | Coeficiente Ca |
|---|---:|---:|
| Forragem | 0,64 | 0,30 |
| Concentrado | 0,70 | 0,60 |
| Mineral | 0,80 | 0,95 |

A composição da biblioteca é %MS. Para q kg MS, a massa total em gramas é q·teor·10; multiplicar pelo coeficiente local gera a oferta absorvível. Esses coeficientes genéricos não reproduzem integralmente os coeficientes específicos por fonte dos livros científicos. Permanecem preservados e identificados como limitação.

No LP estático, mínimos absorvíveis P/Ca são opcionais e a avaliação nativa é posterior. No dinâmico, os mínimos nativos são atualizados por curral e há tetos totais adicionais.

## Tetos totais do modelo dinâmico

A política nrc2005_mtl acrescenta Ca total≤1,5% MS e P total≤0,7% MS, segundo NRC 2005, Mineral Tolerance of Animals. São limites de tolerância, não recomendações de consumo ou multiplicadores das exigências absorvíveis. São aplicados igualmente a ambos os solvers controlados.

A relação Ca:P é registrada sem igualdade ou faixa estreita universal inventada. Não se modelam todas as interações, toxicidade crônica, qualidade comercial, vitaminas ou DCAD de vacas secas. [Equações](04-modelagem.md).

## Diagnóstico NASEM

O fluxo estático pode copiar o animal e calcular exigência de P pelo despacho NASEM, sem alimentar os mínimos NRC. O capítulo 7 de NASEM 2021 distingue formas/fontes de P; a oferta local por categoria não implementa toda essa distinção. O ano operacional validado continua NRC. [Análise anterior preservada](../fosforo_nasem_2021.md).

## Correção histórica do primeiro dia

A reprodução confirmou q₀=9,8361876887 kg MS do suplemento 231 e mínimo local transitório de 4,8361876887 devido ao raio 5. A rotina antiga encerrava na primeira candidata aprovada, que tinha aproximadamente Ca=4,174% e P=3,473% totais na MS. O avaliador nativo de mínimos não detectava os excessos.

A formulação corrigida continua minimizando, verifica os tetos e encontra zero desse suplemento no primeiro dia. Isso foi resultado da otimização, sem exclusão do alimento ou ajuste artificial de preço/nutrientes. [Comparação completa](../../evidencias/correcao_dinamica/replay_final/primeiro_dia_comparacao.json).

## Bezerros

Os requisitos Ca/P do ramo CALF possuem zeros e TODO nativo; não são comprovação de adequação mineral. Tampouco os tetos adultos fornecem certificação específica dessa rotina. Os 252 curral-dias de bezerros não aprovados são preservados separadamente. [Investigação e contratos de grandezas](05-restricoes.md) · [Referências](14-referencias.md).
