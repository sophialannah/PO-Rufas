# Limitações científicas e de validação
[Sumário](README.md)

## Escopo comprovado

A integração FULL_FARM foi executada por 365 dias no cenário NRC, incluindo growing, close_up e lac_cow. O exclusivo teve 1.002 chamadas HiGHS aceitas e zero SLSQP. Isso não valida automaticamente NASEM, dietas prescritas, todos os agrupamentos possíveis, grandes rebanhos, outros climas ou condições econômicas.

Growing_and_close_up tem teste de seleção das restrições nativas, mas não um experimento anual próprio. Bezerros mantêm a rotina original e não são chamadas de otimização/fallback.

## Convergência

A aproximação sequencial é local e heurística. Há 959 formulações convergentes e 43 viáveis sem convergência. Pontos iniciais, diferenças finitas, escalas do mérito, região local e orçamento influenciam a busca. O status ótimo de um LP não prova ótimo global do problema não linear.

## Avaliação nutricional

Os tetos totais Ca/P foram implementados dinamicamente e são diferentes dos mínimos absorvíveis. Não cobrem toxicidade crônica, todas as interações, DCAD, vitaminas ou coeficientes específicos por suplemento. Os coeficientes locais genéricos foram preservados.

A aprovação é por média de curral e pelos critérios implementados. Não garante adequação individual de todos os animais. Há **252 curral-dias de bezerros não aprovados por estratégia**, com problemas de aplicabilidade dos limites adultos e contratos de grandezas em MP/DMI. Não foram convertidos em aprovações. [Investigação](05-restricoes.md).

## Resposta biológica e inventário

A curva de leite e equações de crescimento originais não respondem genericamente a qualquer diferença de dieta. Estados e leite iguais não certificam equivalência fisiológica. Há efeito da oferta em requisitos subsequentes e digestão/excreção; o modelo biológico não foi alterado.

O inventário mantém tolerância operacional de 0,001 kg MS. O maior desvio registrado entre dieta solicitada e fornecimento foi 0,00082 kg por alimento/dia no HiGHS e 0,000788 no SLSQP. A correção de pequenos lotes remove massa real, sem criar fornecimento.

## Economia e padrões

A redução de 0,1249355% é condicionada a preços demonstrativos, pequeno rebanho e restrições presentes. Não demonstra superioridade econômica universal. Há cotações verificadas parciais, sem orçamento comercial completo; preços ausentes não foram inventados.

O LP estático simplifica PB/NEL com coeficientes fixos e possui limitações diferentes do modelo dinâmico com MP/energia nativas. O diagnóstico NASEM de P não constitui formulação NASEM completa.

## Reprodução e autoria

Python 3.12 foi exercitado; 3.13 é permitido pelo metadado, sem validação equivalente documentada. Os tempos de teste não são benchmarks controlados. A revisão upstream d471c742 é candidata com alta correspondência, sem prova de ancestralidade exata. As licenças correspondentes foram recuperadas e os avisos de autoria mantidos.
