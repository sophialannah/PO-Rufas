> Registro de uma etapa anterior. Para o estado operacional e resultados reconferidos, consulte a [documentacao consolidada](po_rufas/README.md). Os numeros historicos deste arquivo foram preservados.

# Auditoria comparativa PO-Rufas

Data: 24/11/2026. Integrantes: Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

Base local: `58329000203c065d0ed3e9c5e787ea8f29f5176d`, branch `feat/apresentacao-academica-rufas`, inicialmente limpa. PR #6 já integrado e fechado. Nenhum push ou merge autorizado nesta auditoria.

## Método e alcance

Leitura estática da branch [feat/planejamento-nasem-local](https://github.com/gmdsouza/RuFaS/tree/feat/planejamento-nasem-local), consultada pelo conector GitHub. Não executamos código externo nem copiamos sua implementação. O README declara GPLv3. Os testes externos foram lidos, não executados: sua presença não comprova aprovação. A auditoria abaixo cobre os caminhos nutricionais e de otimização examinados, não certifica todos os subsistemas da fazenda nem todas as equações dos livros.

Linha de base local: 433 testes passaram em 5,64 s, executando os diretórios de rações, nutrientes e `test_nutrition_data_structures.py`.

## Matriz de diferenças

| Funcionalidade | Projeto de referência | Nosso projeto | Diferença identificada | Prioridade | Ação recomendada |
|---|---|---|---|---|---|
| Arquitetura | `helpful_scripts/interface_rufas/rufas_solver.py`, `Formulator` usa calculadores, oferta e restrições nativas | `linear_diet.py`, `optimize_diet`; adaptadores e exemplo dentro do módulo ration | Interface externa não é intrinsecamente superior; ambos reutilizam RuFaS, nenhum aplica automaticamente ao ciclo completo | P2 | Preservar arquitetura local |
| LP NRC | `nrc2001_dieta_lp/solver.py`, `resolver` chama HiGHS dual simplex até 50 vezes | HiGHS com coeficientes fixos | A referência recalcula passagem e desconto após cada solução; não equivale a um único LP global | P1 | Explicar alcance do ótimo; não copiar iteração como linearização exata |
| NASEM | `nasem2021_dieta_lp/dieta_pulp.py` usa PuLP/CBC e até 100 rodadas | Não há formulação NASEM completa no LP local | Equações dietodependentes na referência exigem avaliação além do último LP | P1 | Não anunciar equivalência nutricional; validar fontes antes de ampliar |
| Solver da interface | `Formulator.solve`: HiGHS prepara partida, SLSQP resolve restrições nativas | `optimize_diet`: somente LP | SLSQP é não linear e fornece solução local | P1 | Manter LP para a proposta de PO |
| TDN | `Formulator.requirements` fornece `TDN_fraction`; API externa difere da nossa | `linear_diet_example.example_inputs` e `linear_diet_catalog.random_cow` passam 65 ao argumento `TDN_percentage` | Nosso `_calculate_protein_requirement` multiplica diretamente por TDN_conc; `Animal` usa TDN/DMI e constante padrão 0.7 | P0 | Corrigir fronteira local para 0.65, sem copiar assinatura externa |
| Animal | `rufas_data.holstein_profile` seleciona registro HO da população; produção e ECC são hipóteses | Perfil sintético explícito; `profile_from_animal` lê Animal | Perfil da população também não é medição individual de todos os parâmetros | P1 | Distinguir registros, hipóteses e cálculo; manter escopo de um animal |
| Exigências | Interface chama NRC/NASEM por candidata; estudos LP usam animal/tabela específicos | `requirements_from_rufas` importa exclusivamente DMI | PB/NEL/FDN suplementares continuam ilustrativos | P1 | Não transformar MP em PB ou energia de crescimento em NEL por simples soma |
| Energia e proteína | Interface avalia oferta nativa dietodependente; estudo NRC fixa NEL da tabela | NEL por ingrediente e PB mínima fornecidas externamente | Não há dados suficientes no LP atual para certificar nutrição completa | P1 | Manter limitação explícita; não inventar coeficientes |
| Minerais | Interface avalia Ca/P; estudos usam absorção e limites adicionais | Mínimos totais opcionais, não ativados na demo | Mineral absorvível não equivale a mineral total | P1 | Exigir base compatível e fonte; não importar gramas absorvíveis como kg totais |
| Ingredientes | `rufas_data.catalog` combina composição e CSV de preços | Lista Python de Ingredient, proveniência, conversão de Feed; catálogo audita elegibilidade | Nosso catálogo permite parâmetros externos, demo usa sintéticos | P1 | Manter identificação; cotação precisa de data, moeda e base |
| Estoque | Interface divide estoque por vacas × dias | `optimize_diet` impõe x_i × dias <= estoque alocado ao animal | Escopos diferentes, ambos lineares | P2 | Não estender para rebanho sem alocação explícita |
| Unidades | Variáveis kg MS e preços convertidos de MN | Variáveis kg MN e nutrientes por kg MS | Ambas corretas com conversão explícita | P2 | Preservar testes de equivalência |
| Inviabilidade | Interface separa LP inviável de falha de convergência | Status infeasible, solver_failure, verification_failed; sem ração utilizável na falha | Nosso LP já distingue falhas | P2 | Preservar; diagnóstico mínimo conflitante não implementado |
| Sensibilidade | NRC `sensibilidade` reotimiza preços; `relatorio` mostra marginais do último LP | Sem rotina própria de comparação de preços | Lacuna útil à defesa acadêmica | P1 | Acrescentar reotimização de cenários comparáveis, sem alegar economia observada |
| Economia | Interface calcula receita-meta menos custo alimentar | Custo diário | Margem alimentar não é lucro completo de fazenda | P2 | Não comparar valores entre cenários distintos |
| Testes | `interface_rufas/test_rufas.py` testa bibliotecas, requisitos, estoque, horizonte | Casos analíticos, conversões, falhas e FeedInRation reais; Animal é snapshot mínimo no teste | Snapshot não prova inicialização completa da fazenda | P1 | Descrever cobertura real, testar regressão de TDN |
| Horizonte | `planejar` verifica dias de blocos e avança DEL/gestação | Dieta diária constante sobre período de estoque | Não é erro do LP de um animal | P2 | Deixar planejamento dinâmico para etapa posterior |

## Verificação matemática local

Com x_i em kg MN/dia, d_i fração MS, c_i PB/MS, e_i Mcal/kg MS e f_i FDN/MS:

- Objetivo: soma p_i x_i, R$/dia.
- MS: limite inferior <= soma d_i x_i <= superior.
- PB e NEL: soma d_i c_i x_i >= PB; soma d_i e_i x_i >= NEL.
- FDN: soma d_i(f_i-r_min)x_i >= 0; soma d_i(f_i-r_max)x_i <= 0. É equivalente à proporção quando MS total > 0. O caso degenerado de MS zero não define proporção e não certifica uma dieta alimentar.
- Estoque: T x_i <= S_i, com T fixo e positivo; inclusão por limites de x.
- Minerais totais: soma d_i m_i x_i >= exigência total em kg/dia. Composição desconhecida é rejeitada.

Nenhuma dessas linhas contém produto entre variáveis de decisão. Fixar coeficientes dietodependentes gera um modelo condicionado a esses valores, não uma reformulação equivalente da biologia inteira. Repetir LPs até estabilizar não demonstra ótimo global do problema não linear.

## Evidência P0: TDN

Em `nrc_requirements_calculator.py::_calculate_protein_requirement`, a estimativa bacteriana é DMI × 1000 × TDN_conc × 0.13. Em `animal.py`, TDN é oferta/DMI; `AnimalModuleConstants.DEFAULT_TDN_PERCENTAGE = 0.7`. Portanto, 65 é incompatível com o contrato efetivo, apesar do nome e docstring do argumento. Corrigir apenas os chamadores próprios evita alterar globalmente código legado sem revisar todos os consumidores.

## Limites científicos e próximos passos

A referência cita NRC capítulos 3–6 e tabelas 14-7/15-1 e NASEM capítulos 2/3/6 e tabela 21-1. Essas citações no código externo não constituem conferência independente dos livros. Não incorporamos suas equações nem afirmamos certificação científica. Uma ampliação para MP, energia e minerais absorvíveis exige revisar as equações originais, unidades de oferta e domínio fisiológico. A interface externa declara também correções locais de amido e estado uterino; elas não devem ser transplantadas sem reproduzir o defeito na nossa versão.

Fontes examinadas na branch indicada: README raiz; `helpful_scripts/interface_rufas/{README.md,rufas_solver.py,rufas_data.py,test_rufas.py}`; `helpful_scripts/nrc2001_dieta_lp/solver.py`; `helpful_scripts/nasem2021_dieta_lp/dieta_pulp.py`. A branch pode mudar após a consulta.
