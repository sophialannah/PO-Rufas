# Documentação vigente do PO-RuFaS

Versão acadêmica consolidada em 27/11/2026. Autores: Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

O projeto oferece LP estático, comparação experimental e simulação dinâmica FULL_FARM de 365 dias. O HiGHS exclusivo substituiu SLSQP nas 1.002 chamadas das categorias adultas ativas do cenário NRC validado. A contagem de referência é **954 testes aprovados**.

## Sumário

1. [Contextualização](01-contextualizacao.md)
2. [Fundamentação teórica](02-fundamentacao.md)
3. [Dados e rastreabilidade](03-dados.md)
4. [Modelagem matemática estática e dinâmica](04-modelagem.md)
5. [Restrições, parecer e bezerros](05-restricoes.md)
6. [Implementação](06-implementacao.md)
7. [Integração diária com RuFaS](07-integracao.md)
8. [Minerais e separação NRC/NASEM](08-minerais.md)
9. [Comparação controlada](09-comparacao.md)
10. [Resultados oficiais](10-resultados.md)
11. [Testes](11-testes.md)
12. [Manual e capturas finais](12-manual.md)
13. [Limitações](13-limitacoes.md)
14. [Referências, autoria e glossário](14-referencias.md)

[Validação e histórico](VALIDACAO.md) · [Publicação e reprodução isolada](../../evidencias/publicacao/README.md) · [Apresentação vigente](../../apresentacao/README.md).

## Leitura dos resultados

SLSQP controlado: 2.319,34875854 UM; HiGHS exclusivo: 2.316,45106770 UM; redução demonstrativa de 0,1249355%. Leite igual: 140.223,666523 kg. Das formulações HiGHS, 959 convergiram e 43 conservaram soluções viáveis sem convergência.

Os 998 curral-dias adultos aprovados no HiGHS não incluem os 252 curral-dias de bezerros não aprovados em cada estratégia. Não se declara ótimo global, economia universal ou aprovação nutricional de todo o rebanho.

## Evidências e histórico

- [Rodada controlada oficial](../../evidencias/correcao_dinamica/README.md).
- [Experimentos estáticos A/B](../../evidencias/comparacao/README.md).
- [Primeira integração anual — histórica](../../evidencias/anual/README.md).
- [Cópias documentais anteriores à consolidação](../../evidencias/publicacao/historico_documental/manifesto.json).
- [README acadêmico anterior — histórico](README_ANTERIOR.md).
- [Documentação original RuFaS](../README_RuFaS_original.md), [documentação científica](../scientific/) e [Sphinx](../_src/index.rst).

As contagens 462/466/937 e o resultado +9,05% pertencem às etapas históricas. Os registros foram preservados com sua origem. O histórico pessoal da conversa permanece local e não é dependência da reprodução científica.
