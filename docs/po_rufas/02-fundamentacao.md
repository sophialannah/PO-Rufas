# Fundamentação teórica
[Sumário](README.md)

O **LP estático** possui objetivo e restrições afins com coeficientes fixos. O **modelo dinâmico** resolve uma sequência de LPs que aproximam localmente as restrições nutricionais nativas, atualizadas ao longo da simulação.

## LP estático

A forma é min pᵀx, sujeito a Ax≤b e L≤x≤U. A região viável é convexa; um ótimo verificado pertence ao LP informado. Isso não transforma metas simplificadas de PB/NEL em um modelo fisiológico completo.

MN inclui água; MS a exclui. PB descreve composição, MP envolve utilização. DE, ME e NEL representam bases energéticas diferentes. Não há conversão automática dessas grandezas por fator arbitrário. As hipóteses e metas externas são explícitas.

## Programação linear sequencial

O custo permanece linear nas quantidades, mas as funções nutricionais g(q) podem depender da candidata. Em cada ponto, o método usa aproximações afins dentro de uma região de confiança e valida as quantidades nas funções originais. O status optimal de um LP local não prova ótimo global do problema não linear.

A busca continua após a primeira candidata aceitável enquanto houver progresso relevante, conserva a melhor candidata viável e informa convergência, estagnação e orçamento separadamente. [Critérios executados](04-modelagem.md).

## Padrões e limites científicos

Os requisitos operacionais são NRC 2001 implementados no RuFaS. A política adicional NRC 2005 limita **concentrações totais** de Ca/P; os requisitos permanecem **absorvíveis**. Tetos de tolerância não são metas de consumo.

NASEM 2021 é um diagnóstico separado de exigência de P no fluxo estático. Suas equações não foram misturadas à comparação NRC anual. A aprovação de indicadores comuns não certifica toda a nutrição, especialmente na rotina de leite e concentrado inicial dos bezerros. [Referências](14-referencias.md) · [Limitações](13-limitacoes.md).
