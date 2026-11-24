# O que foi corrigido

Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

## Resultado e alcance

Esta entrega corrige um erro comprovado de unidade e acrescenta análise de preços. Não encerra a ampliação científica para exigências completas NRC/NASEM. A auditoria está em [auditoria_comparativa_rufas.md](auditoria_comparativa_rufas.md).

1. Os exemplos enviavam TDN=65 ao calculador, que efetivamente usa fração. Agora enviam 0,65. O nome antigo do argumento é enganoso; conferimos a fórmula interna e o chamador Animal antes de corrigir. Isso corrige o cálculo intermediário de proteína metabolizável. Como somente DMI entra no LP demonstrativo, a dieta e seu custo não mudaram.
2. Foi criada `linear_diet_sensitivity.compare_prices`: ela recebe o mesmo animal e ingredientes, altera somente preços e resolve novamente. Registra entradas, estados, custos e diferenças. Não altera a lista original, rejeita preços inválidos e não apresenta diferença econômica quando não há solução ótima.
3. Foram adicionados testes de regressão de TDN, custo conhecido, repetibilidade, preservação dos dados, cenário inviável e entradas inválidas.

## Evidências locais

- Antes: 433 testes passaram em 5,64 s.
- Depois: 435 testes passaram em 9,49 s, nos mesmos diretórios e com dois testes adicionais.
- Flake8: zero erros nos quatro arquivos Python alterados/criados.
- Execução real: optimal, R$ 34,997773642175794/dia; 11 restrições verificadas.
- Quantidades: alfafa 15,911918 kg MN/dia; milho 9,095659; soja 0,182774.
- Não executamos a suíte geral da fazenda nem o código do colega.

## Comandos no Windows

Na raiz do projeto:

```powershell
.\apresentacao\demonstracao_solver.bat
.\.venv\Scripts\python.exe -m RUFAS.biophysical.animal.ration.linear_diet_sensitivity
.\.venv\Scripts\python.exe -m pytest tests/test_biophysical/test_animal/test_ration tests/test_biophysical/test_animal/test_nutrients tests/test_biophysical/test_animal/test_data_types/test_nutrition_data_structures.py -q
```

O módulo de sensibilidade compara o cenário base com todos os preços 10% maiores. Isso é um exercício controlado, não uma cotação de mercado ou economia obtida em fazenda. As mesmas restrições permanecem ativas no modelo; as quantidades podem mudar em outros cenários de preços.

## Como defender o trabalho

O nosso modelo é LP com coeficientes fixos; o ótimo vale para esses dados e restrições. A referência possui LPs iterativos e também SLSQP não linear: funcionalidades diferentes não tornam automaticamente o nosso LP incorreto. O adaptador local usa Feed e NutritionRequirements e devolve kg MS para consumo por outros componentes; não executa automaticamente a fazenda.

A apresentação mantém cinco minutos de slides e demonstração, mais cinco de perguntas. Os números da dieta continuam válidos. Os 433 testes nos slides são a execução histórica registrada na entrega; a auditoria posterior acrescentou dois, totalizando 435. As evidências antigas não foram reescritas como se pertencessem à nova execução.

## Pendências científicas explícitas

Somente DMI é importada como exigência no LP demonstrado. PB, NEL e FDN suplementares continuam ilustrativos. O teste de Animal usa um snapshot mínimo, não uma inicialização completa. Faltam a conferência independente das equações nos livros, a avaliação de MP e minerais absorvíveis compatível com a oferta, e validação nutricional da dieta candidata. Não somar todas as energias nativas e chamar de NEL sem analisar suas bases; não converter MP em PB por um fator arbitrário. A correção não torna a dieta uma recomendação de alimentação.

Os documentos não certificam revisão completa de cada subsistema do RuFaS. Nenhuma implementação externa foi copiada, nenhum push ou merge foi feito. As alterações ficam locais para revisão.
