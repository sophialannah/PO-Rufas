> Registro de uma etapa anterior. Para o estado operacional e resultados reconferidos, consulte a [documentacao consolidada](po_rufas/README.md). Os numeros historicos deste arquivo foram preservados.

# Integração real do otimizador com RuFaS

Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

## Fluxo comprovado

`animal_population.json → Animal(record, RufasTime) → Animal.calculate_nutrition_requirements → NRCRequirementsCalculator → NutritionRequirements → lista NRCFeed → Ingredient → HiGHS → percentuais MS → RationManager → kg MS/animal/dia → FeedInRation → NutritionSupplyCalculator / NutritionEvaluator`.

A execução de 24/11/2026 selecionou deterministicamente a vaca HO **98605**, `DEL = 100`, paridade `4` e peso `627,560669 kg` (`output/integracao_real.json` e `apresentacao/evidencias/integracao_real.json`). Peso, idade, paridade e estado reprodutivo vêm de `input/data/animal/animal_population.json`; leite `30 kg/dia` e composição `3,8 / 3,2 / 4,8%` são hipóteses explícitas. O construtor original `Animal(record, RufasTime)` inicializa crescimento, reprodução, leite e nutrientes — não é `object.__new__` nem mock.

Para construir isoladamente o animal, `demo_inputs()` configura as médias e desvios de Wood a partir de `input/data/animal/lactation_curve_adjustment_inputs.json` e desativa genética. A curva não prevê leite nesta demonstração. O estado aleatório e as configurações de classe são restaurados ao sair do gerenciador de contexto. Essa preparação é para execução isolada, não concorrente com uma simulação ativa.

## Componentes reais utilizados

- **Nativos do RuFaS (sem alteração)**: `Animal`, `RufasTime`, `MilkProduction`, `NutritionRequirements`, `NRCRequirementsCalculator`, `NRCFeed`, `RationManager`, `FeedInRation`, `NutritionSupplyCalculator`, `NutritionEvaluator`, `OutputManager`. (Também foram inspecionados `NASEMRequirementsCalculator`, `NASEMFeed`, `Pen` e `RationOptimizer`.)
- **Módulos do projeto PO-Rufas**: `linear_diet.py`, `linear_diet_adapter.py`, `linear_diet_integration.py`, `linear_diet_integrated_example.py`, `linear_diet_example.py`, `linear_diet_catalog.py`, `linear_diet_sensitivity.py`, `linear_diet_workflow.py`.

## Contratos, origem das exigências e compatibilidade científica

- **`Animal.calculate_nutrition_requirements`**: executa o despacho real do animal para `NRCRequirementsCalculator`. Sem dieta anterior (`previous_nutrition_supply=None`), usa `AnimalModuleConstants.DEFAULT_TDN_PERCENTAGE = 0.7` (fração, não 70). Isso difere legitimamente de `linear_diet_example.py` (`TDN_percentage=0.65`, corrigido na revisão anterior).
- **Matéria seca (DMI)**: `NutritionRequirements.dry_matter` = **`22,231580 kg/dia`**, importada diretamente para o LP como `dm_min_kg == dm_max_kg`.
- **Proteína, energia, FDN e minerais**: `metabolizable_protein` (`2120,54 g/dia`), `lactation_energy` (`21,93 Mcal/dia`), `maintenance_energy` (`10,03 Mcal/dia`), `calcium` (`56,56 g/dia`) e `phosphorus` (`50,49 g/dia`) são registrados como diagnóstico. Não há conversão arbitrária de MP em PB, de DE (`Feed.DE`) em NEL, de energia de lactação isolada em NEL total, nem de minerais absorvíveis em minerais totais. PB mínima (`3,6 kg/dia`), NEL mínima (`35,0 Mcal/dia`), FDN (`28–40% MS`) e NEL por ingrediente continuam parâmetros externos explícitos com proveniência registrada.
- **Não mistura NRC/NASEM**: `optimize_animal_ration` exige `AnimalType.LAC_COW` e `NutrientStandard.NRC`, rejeitando padrões ou categorias incompatíveis sem misturar equações NRC (2001) e NASEM (2021).
- **`NRCFeed` e lista Python de `Ingredient`**: composições DM, CP, NDF e minerais totais vêm de `input/data/feed/NRC_comp.csv` (IDs `1`, `44`, `167`). Preços (`BRL/t MS`), estoques alocados (`kg MS`), limites (`kg MS/dia`) e NEL ilustrativa são informados externamente.
- **Conversões de unidades (`linear_diet_adapter.py`)**: com `d = Feed.DM / 100`, preço em MN = `purchase_cost * d`; estoque e inclusões em MN = `valor_MS / d`; PB, FDN e minerais totais em fração da MS = `valor_% / 100`; tonelada para kg preserva a base (`/ 1000`).
- **Solver (`linear_diet.py`)**: `scipy.optimize.linprog(..., method="highs")` minimiza `Σ p_i x_i` sujeito às restrições lineares de MS, PB, NEL, proporções de FDN linearizadas (`Σ d_i (f_i - r_min) x_i >= 0` e `<= 0`, exigindo `dm_min_kg > 0`), limites de inclusão e estoque no período (`T * x_i <= S_i`). Todas as 11 linhas são verificadas de forma independente após o solver com tolerância absoluta `1e-7`.

## Retorno ao `RationManager` e avaliação nativa

1. `ration_config_from_result(result, feeds)` exige status `optimal`, todas as verificações satisfeitas, IDs únicos e consistência de MS, convertendo `kg MS/dia` em percentuais de MS que somam `100%` (`60,24%`, `37,76%`, `2,00%`), sem arredondamento prévio.
2. Uma subclasse isolada por chamada (`SingleAnimalRationManager(RationManager)`) executa os métodos originais `set_user_defined_ration_tolerance`, `set_user_defined_rations`, `get_user_defined_ration_feeds` e `get_user_defined_ration(AnimalCombination.LAC_COW, total_dm)`, validando a soma dos percentuais, registrando no `OutputManager` e recuperando `kg MS/animal/dia` sem mutar os atributos de classe de `RationManager`.
3. `SingleAnimalSupplyCalculator(NutritionSupplyCalculator)` e `NutritionEvaluator.evaluate_nutrition_supply` recebem os objetos `FeedInRation` construídos com as quantidades recuperadas, confirmando exatamente PB (`3,6000 kg`) e FDN (`6,4120 kg`) e fornecendo o diagnóstico nativo completo da dieta: energia total (`+2,01 Mcal`), mantença (`+23,93 Mcal`), lactação (`+11,92 Mcal`), MP (`2300,94 g` vs `2120,54 g` req.), Ca (`+5,45 g`), FDN (`0,0`), FDN de forragem (`+10,06%`) e gordura (`+3,89%`) atendidos, além de explicitar **déficit de fósforo absorvível (`-6,68 g/dia`, `is_valid_cow_ration=False`)** pela ausência de suplemento mineral na lista demonstrativa de três alimentos.

## Resultado real da demonstração integrada

Status: **`optimal`**; custo: **`R$ 35,1059017708/animal/dia`** (reconferido por soma `preço × quantidade`).

| ID | Alimento | kg MN/dia | kg MS/dia | % MS | R$/dia |
|---|---|---:|---:|---:|---:|
| 1 | Alfafa | 14,8300 | 13,3915 | 60,24% | 18,7481 |
| 44 | Milho | 9,5283 | 8,3945 | 37,76% | 15,1100 |
| 167 | Farelo de soja | 0,4979 | 0,4456 | 2,00% | 1,2478 |

Totais: `MS = 22,2316 kg/dia`, `PB = 3,6000 kg/dia`, `NEL = 35,00 Mcal/dia`, `FDN = 6,4120 kg/dia` (`28,84% MS`). O exemplo anterior (`R$ 34,9978/dia`) permanece reproduzível em `linear_diet_example.py` e refere-se a outro animal (650 kg); não comparar custos entre cenários distintos como economia.

## Comparação com repositórios de referência

- **`RuminantFarmSystems/RuFaS` (`main`)**: estrutura de `RationManager` (`set_user_defined_rations`, `get_user_defined_ration`), `RationOptimizer` (`SLSQP`), `NRCRequirementsCalculator`, `NASEMRequirementsCalculator` e `NutritionSupplyCalculator` compatível; nossa versão local de `RationManager` inclui suporte adicional às opções de controle de consumo (`IntakeOption`).
- **`gmdsouza/RuFaS` (`feat/planejamento-nasem-local`)**: inspecionada estaticamente; implementa três frentes (`nrc2001_dieta_lp/solver.py` iterativo com HiGHS, `nasem2021_dieta_lp/dieta_pulp.py` iterativo com PuLP/CBC e `interface_rufas/rufas_solver.py` não linear com `SLSQP`). Nenhuma dessas implementações foi copiada nem misturada ao nosso LP.
- **`sophialannah/PO-Rufas` (`feat/apresentacao-academica-rufas`)**: único repositório alterado; PR #6 já mesclado anteriormente para a base da apresentação, com trabalho subsequente preservado localmente antes de novo commit/push.

## Testes

Comando executado após as edições finais de código e testes:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/test_biophysical/test_animal/test_ration tests/test_biophysical/test_animal/test_nutrients tests/test_biophysical/test_animal/test_data_types/test_nutrition_data_structures.py -q --junitxml=apresentacao/evidencias/testes.xml
```

Resultado: **442 aprovados em 4,69 s** (incluindo **42 testes específicos** do núcleo linear, catálogo e integração ponta a ponta sem mocks com `Animal`, `NRCFeed`, `RationManager`, `FeedInRation`, `NutritionSupplyCalculator` e `NutritionEvaluator`). Não foi executada a suíte completa da fazenda inteira.

## Níveis de integração e pendências

1. **Dados**: comprovado com `Animal` (`animal_population.json`), `NRCRequirementsCalculator` e `NRCFeed` (`NRC_comp.csv`).
2. **Otimização**: comprovado com DMI nativa e limites externos explícitos no `linprog/HiGHS`.
3. **Saída e avaliação**: comprovado com `RationManager`, `FeedInRation`, `NutritionSupplyCalculator` e `NutritionEvaluator` reais.
4. **Ciclo diário da fazenda**: **não implementado** — sem execução completa de `Pen`, consumo diário ao longo da simulação, baixa automática de estoque no `FeedManager` ou atualização contínua do rebanho.

Pendências científicas explícitas: substituição das metas externas de PB/NEL/FDN por formulação nutricionalmente completa validada (incluindo fósforo/cálcio compatíveis, suplemento mineral e revisão das equações dependentes da dieta em NRC 2001 / NASEM 2021).

## Execução da demonstração no Windows

Na raiz do repositório:

```powershell
.\apresentacao\demonstracao_integrada.bat
```

Modo automático (sem pausa para Enter):

```powershell
.\apresentacao\demonstracao_integrada.bat --auto
```

Alternativa direta:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m RUFAS.biophysical.animal.ration.linear_diet_integrated_example
```

Referência anterior (sem retorno ao `RationManager`): `.\apresentacao\demonstracao_solver.bat`.
