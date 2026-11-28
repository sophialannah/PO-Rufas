# Publicação dos ajustes finais do frontend — 28/11/2026

Esta entrega preserva o solver, o modelo matemático, a integração anual e todas as evidências científicas anteriores. Base: d13ef5d; branch fix/validacao-nutricional-rufas. O inventário registra os arquivos desta revisão e seus hashes antes do commit.

## Validação

A suíte relevante passou **969 testes em 362,68 s**, sem falhas ou erros: [JUnit](usability_full_suite.xml) e [log](usability_full_suite.log). São os 954 casos anteriores mais 15 regressões de usabilidade. A checagem direcionada final passou [33 casos](usability_final_ui_tests.log); antes da publicação, a repetição desses casos passou novamente em [36,36 s](publication_frontend_recheck.log). O comando completo está no [capítulo de testes](../../docs/po_rufas/11-testes.md). Os arquivos foram copiados das execuções reais, com remoção de caminhos pessoais e hostname do relatório; contagens e resultados foram preservados.

As regressões verificam fonte NRC sem valores inventados, cenário publicado, persistência da edição, campos pendentes, custos com ambas as estratégias vencedoras/empate/base zero, rótulos sem mutação dos dados, leitura das evidências sem criar processo anual, invalidação/cópia do cache e precisão dos valores. A suíte inclui a regressão anual exclusiva real já existente. A reprodução em cópia isolada da publicação anterior validou os 954 casos da base, sem atribuir a ela as regressões novas.

## Interface e desempenho

P/Ca absorvíveis são obrigatórios no fluxo NRC; NASEM é diagnóstico complementar avançado, inicialmente desligado. Há multisseleção, preservação da edição, cenário demonstrativo com 231, pendências explícitas e explicação da inviabilidade. Resultados anuais arquivados podem ser carregados sem simulação nova, com cartões econômicos dinâmicos e rótulos em português. O cache e o carregamento opcional dos diários afetam somente exibição.

A [medição local](usability_performance.json) comparou leitura do diário, cache e resumo, com igualdade dos valores completos. Não é benchmark do solver nem promessa de aceleração universal.

## Capturas e materiais

As [capturas reais](telas/manifesto.json) registram a interface atual em servidor local e os resultados anuais arquivados; não representam nova execução de 365 dias. O [manual](../../docs/po_rufas/12-manual.md) e a [apresentação vigente](../../apresentacao/README.md) foram atualizados, preservando cinco minutos de exposição e cinco de arguição. Imagens e decks anteriores permanecem históricos.

## Resultados científicos preservados

365 dias: SLSQP 2.319,34875854 UM; HiGHS exclusivo 2.316,45106770 UM; redução 0,1249355%; leite 140.223,666523 kg em ambos. Foram 1.002 formulações HiGHS sem SLSQP/fallback, 959 convergentes e 43 viáveis sem convergência; 998 curral-dias adultos aprovados. Os 252 registros de bezerros não aprovados por estratégia continuam identificados separadamente. Preços demonstrativos; sem ótimo global não linear ou superioridade econômica universal.
