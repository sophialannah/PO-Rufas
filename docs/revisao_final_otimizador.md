> Registro de uma etapa anterior. Para o estado operacional e resultados reconferidos, consulte a [documentacao consolidada](po_rufas/README.md). Os numeros historicos deste arquivo foram preservados.

# Revisão final do otimizador PO-Rufas

Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva — 24/11/2026.

## Estado preservado

Antes da revisão, cópia dos arquivos locais alterados, núcleo/adaptador e pasta apresentacao em `%USERPROFILE%\AppData\Local\Temp\PO-Rufas-revisao-20261124-172253`. Linha de base: 435 testes aprovados. Não houve commit, push ou alteração de branch.

## TDN: prova do efeito

`example_calculator_inputs` fornece TDN=0,65. `NRCRequirementsCalculator.calculate_requirements` repassa esse argumento para `_calculate_protein_requirement`. A estimativa de proteína bacteriana usa DMI × 1000 × TDN × 0,13. Apesar do nome legado `TDN_percentage`, o contrato efetivo é fracionário: `Animal` calcula oferta de TDN/DMI e a constante padrão é 0,7.

Na execução do mesmo animal:

| Resultado nativo | TDN incorreto 65 | TDN correto 0,65 |
|---|---:|---:|
| Proteína metabolizável, g/dia | -21373,610782 | 2201,748528 |
| DMI, kg/dia | 22,545320002 | 22,545320002 |

A proteína negativa era um resultado intermediário incorreto. O LP não recebe MP nem TDN: recebe DMI e os limites externos PB=3,6 kg, NEL=35 Mcal e FDN=28–40%. Logo, nem a matriz, nem seus limites, nem os preços mudaram. O custo igual é consequência desse fluxo, não ajuste de resultados. O novo workflow rejeita TDN fora de [0,1]. Os chamadores legados gerais do RuFaS não foram modificados.

## Exigências e fontes

| Informação | Disponibilidade | Uso nesta entrega |
|---|---|---|
| DMI | Calculador NRC; perfil e produção fixos, kg/dia | Importada no LP como igualdade demonstrativa |
| Energia | RuFaS calcula componentes de mantença, crescimento, gestação, leite e atividade | Diagnóstico; NEL mínima e NEL dos ingredientes continuam externas |
| Proteína | RuFaS calcula MP, g/dia; LP trabalha com PB, kg/dia | MP apenas diagnóstico; nenhuma conversão arbitrária MP→PB |
| FDN | Composição dos alimentos; limites dependem do contexto da dieta | Frações externas explícitas; não chamadas de exigência individual NASEM |
| Minerais | Ca/P nativos e composição total dos alimentos | Nenhum requisito absorvido importado como total; mínimos totais opcionais externos |

Fontes primárias consultadas:

- NRC 2001, capítulo 2, pp. 18–19, PDF local `NRC 2001.pdf`, páginas PDF 43–44; [edição oficial](https://www.nationalacademies.org/publications/9825). A mantença usa 0,08 × peso^0,75. Para energia do leite, p. 19 distingue PB e proteína verdadeira; indica coeficiente 0,0563 para proteína verdadeira. O método compartilhado `nutrition_requirements_calculator.py::_calculate_lactation_energy_requirements` usa 0,0547/0,93. Essa diferença de formulação impede apresentar sua saída como reprodução exata daquela equação NRC sem revisão adicional. Não alteramos o calculador compartilhado, utilizado por outros fluxos.
- [NASEM 2021, capítulo Energy](https://www.ncbi.nlm.nih.gov/books/NBK600598/): a mantença foi revista para 0,10, diferente do NRC 2001. O acesso integral web encontrou bloqueio; os trechos indexados não bastam para implementar o sistema completo.
- [NASEM 2021, Protein](https://www.ncbi.nlm.nih.gov/books/NBK600611/): o sistema distingue proteína degradável, não degradável digestível e oferta metabolizável. PB total não substitui essas avaliações.
- [NASEM 2021, Minerals](https://www.ncbi.nlm.nih.gov/books/NBK600600/?report=reader): distingue exigências absorvidas e dietéticas.

O PDF NASEM local foi identificado, mas não forneceu texto pesquisável útil na extração. Não declaramos verificação integral de suas equações. Não distribuímos nenhum PDF de terceiros. Por essas razões, a decisão é manter os parâmetros externos identificados, como permitido no escopo da revisão, em vez de ampliar cálculos não comprovados.

## Matemática e unidades

x_i = kg MN/dia; d_i = kg MS/kg MN; p_i = R$/kg MN; T = dias fixos.

- Objetivo soma p_i x_i: R$/dia, recalculado após resolver.
- MS: soma d_i x_i; PB: soma d_i c_i x_i; NEL: soma d_i e_i x_i. Coeficientes fixos.
- FDN mínima: soma d_i(f_i-r_min)x_i >= 0; máxima: soma d_i(f_i-r_max)x_i <= 0. Reformulação exata da proporção para MS positiva.
- Correção desta revisão: rejeitar mínimo MS zero quando há limites proporcionais de FDN. Antes, a dieta zero podia satisfazer a linha linear embora a proporção 0/0 fosse indefinida.
- Estoque: T x_i <= S_i; inclusão: L_i <= x_i <= U_i; x_i >= 0. Estoque alocado a um animal, não disponibilidade ilimitada da fazenda.
- Feed.DM, CP, NDF e minerais percentuais são divididos por 100. Preço por kg MS multiplica por d_i para virar preço/kg MN. Estoque e inclusão em MS dividem por d_i. Preço/tonelada divide por 1000 sem trocar a base.
- Minerais totais usam kg/kg MS e kg/dia, não gramas absorvidos. DE não é NEL. Não foi encontrada outra troca percentual/fração nos coeficientes do LP examinados.
- Todas as linhas são lineares. Não há iteração de coeficientes nem SLSQP. Inviabilidade, falha do solver e falha de verificação têm estados distintos; falhas não retornam ração utilizável.

A igualdade DMI é uma hipótese do exemplo, não prova de que consumo previsto seja exigência exata. Limites fornecidos são verificados; nutrientes não modelados não são certificados.

## Integração executável comprovada

`linear_diet_workflow.run_nrc_workflow(animal_inputs, feeds, feed_metadata, external_thresholds, period_days=...)` recebe dados de um animal e lista de Feed com preços, estoques e limites. Executa o calculador NRC, converte para Ingredient/DietRequirements, resolve e entrega a ração em kg MS para `FeedInRation` e `NutritionSupplyCalculator`. A oferta nativa de PB e FDN é comparada à do LP nos testes.

Classes originais efetivamente executadas: NRCRequirementsCalculator, NutritionRequirements, NRCFeed, FeedInRation e NutritionSupplyCalculator. Classes próprias: AnimalProfile, Ingredient, DietRequirements e DietResult. Preços, estoque, NEL, metas suplementares e dados sintéticos do animal são externos e aparecem no relatório. O teste não inicializa uma fazenda nem comprova atualização de Animal; o adaptador de snapshot já existente tem alcance limitado.

O JSON registra todas as entradas, saídas nativas diagnósticas, limites efetivamente usados, solução, verificações e conferência da oferta. Ainda não há dieta automaticamente aplicada à simulação, baixa de estoque ou validação nutricional completa.

## Execução e resultados

```powershell
.\apresentacao\demonstracao_solver.bat
.\.venv\Scripts\python.exe -m RUFAS.biophysical.animal.ration.linear_diet_workflow
```

O segundo comando grava `output/revisao_integracao.json`, incluindo a comparação de TDN. Resultado: optimal; R$ 34,997773642175794/dia; alfafa 15,911918 kg MN/dia, milho 9,095659, soja 0,182774. MS 22,545320 kg; PB 3,6 kg; NEL 35 Mcal; FDN 6,754572 kg. Onze verificações satisfeitas.

Após mudanças: **437 testes passaram em 4,42 s** nos diretórios ration, nutrients e test_nutrition_data_structures.py. Foram adicionados testes do domínio positivo da FDN e do workflow real, incluindo resposta à produção, rejeição de percentual incorreto e cenário inviável. A suíte integral da fazenda não foi executada.

## Apresentação e defesa

Permanecem 5 minutos de slides/demo + 5 de perguntas. Resultados e equações dos slides não mudaram para o cenário positivo. A apresentação já identifica os parâmetros suplementares como ilustrativos e a necessidade de validação completa; os 433 testes nela são a execução histórica registrada. A revisão atual tem 437. Não apresentar o relatório diagnóstico como certificação NRC/NASEM.

Resposta curta sobre TDN: “Corrigimos uma unidade do cálculo intermediário de MP. O custo não mudou porque nosso LP usa DMI nativa e limites externos de PB, NEL e fibra. A integração é executável, mas ainda parcial no aspecto nutricional.”

Arquivos desta revisão: `linear_diet.py`, `linear_diet_example.py`, novo `linear_diet_workflow.py`, `test_linear_diet.py`, este relatório e nota de revisão na apresentação. As mudanças anteriores de catálogo, sensibilidade e auditoria permanecem locais.
