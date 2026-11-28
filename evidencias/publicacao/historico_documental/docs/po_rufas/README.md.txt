# Documentação acadêmica e técnica do PO-RuFaS

Revisão documental iniciada em 26/11/2026, base de código `5bb6775`. Integrantes Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

## Sumário navegável

1. [Contextualização](01-contextualizacao.md)
2. [Fundamentação teórica](02-fundamentacao.md)
3. [Dados de entrada e rastreabilidade](03-dados.md)
4. [Modelagem matemática](04-modelagem.md)
5. [Restrições nutricionais e parecer](05-restricoes.md)
6. [Implementação computacional](06-implementacao.md)
7. [Integração com RuFaS](07-integracao.md)
8. [Fósforo e cálcio, NRC e diagnóstico NASEM](08-minerais.md)
9. [Comparação dos otimizadores](09-comparacao.md)
10. [Resultados experimentais](10-resultados.md)
11. [Testes e validação](11-testes.md)
12. [Manual do usuário](12-manual.md)
13. [Limitações e trabalhos futuros](13-limitacoes.md)
14. [Referências científicas, autoria e glossário](14-referencias.md)

## Estado verificado

O fluxo operacional é NRC 2001, com restrições opcionais de P/Ca absorvíveis e avaliação nativa. O NASEM oferece diagnóstico de exigência de fósforo. A revisão reexecutou 462 testes e seis cenários. [Validação e divergências corrigidas](VALIDACAO.md)

## Documentação anterior e evidências

Os arquivos anteriores permanecem disponíveis para consulta da evolução. A contagem de testes e o alcance neles descritos pertencem à etapa indicada em cada documento.

- [Modelo original detalhado](../otimizador_linear.md)
- [Integração real](../integracao_real_rufas.md)
- [Análise científica dos minerais](../fosforo_nasem_2021.md)
- [Auditoria comparativa anterior](../auditoria_comparativa_rufas.md)
- [Correções de unidades e sensibilidade](../o_que_foi_corrigido.md)
- [Revisão anterior do otimizador](../revisao_final_otimizador.md)
- [Apresentação de projeto](../apresentacao_projeto.md)
- [Apresentação acadêmica e roteiros](../../apresentacao/README.md)
- [Evidências históricas](../../apresentacao/evidencias/)
- [Manual conciso do frontend](../../frontend/README.md)
- [Documentação original RuFaS](../README_RuFaS_original.md)
- [Fontes científicas originais](../scientific/)
- [Documentação Sphinx](../_src/index.rst)
- [Histórico disponível da conversa](../../HISTORICO_DESENVOLVIMENTO.md)



## Atualização experimental de 27/11

Os 14 capítulos foram aprofundados com experimentos A/B, substituição numérica, fundamentos nutricionais, cenário econômico parcial, capturas reais e gráficos. [Evidências e comandos](../../evidencias/comparacao/README.md). A suíte ampliada inclui os 462 testes anteriores e quatro regressões comparativas.




## Atualização de referência — correção dinâmica de 27/11/2026

Os 14 capítulos receberam seções sobre a reprodução do primeiro dia, tetos minerais explícitos, convergência sequencial, ampliação das categorias, estoque e avaliação científica. A rodada controlada definitiva está em [evidências da correção](../../evidencias/correcao_dinamica/README.md). A contagem vigente é **954 testes aprovados**. Resultados anteriores, inclusive o acréscimo histórico de 9,05%, ficam preservados como históricos e não descrevem a formulação corrigida.
