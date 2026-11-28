# Correção da formulação dinâmica e validação anual — 27/11/2026

## Escopo e preservação

Nenhum commit, push ou merge foi feito. `status_inicial.txt` registra as alterações já presentes antes deste trabalho. As evidências de `../anual/confirmacao` e os arquivos do projeto foram preservados. Este diretório acrescenta reproduções, tentativas intermediárias, testes e três execuções anuais controladas concluídas. A fonte antiga está congelada em `optimizer_anterior.py.txt`.

## Causa reproduzida do primeiro dia

O otimizador nativo inicializa alimentos sem ração anterior com `[1, random()*10, ...]`. Para o suplemento 231, a reprodução exata sorteou 9,8361876887 kg MS por animal. A região local fixa de 5 kg MS impunha artificialmente um mínimo transitório de 4,8361876887 kg, embora o limite físico inferior fosse zero. A rotina anterior aceitava a primeira candidata aprovada e encerrava, mantendo grande custo e excesso mineral. Não houve erro de conversão de gramas nessa causa: preço em UM/kg MS, composição em %MS e quantidades em kg MS foram conferidos.

A reprodução congela requisitos, alimentos, peso e entradas reais; restaura o estado dos geradores entre solvers. `replay_final/primeiro_dia_entradas.json` é estruturado; `replay_final/primeiro_dia_comparacao.json` contém todos os ingredientes, resíduos, avaliações, limites, traços e motivos. Os requisitos absorvíveis foram Ca=70,6328914242 e P=63,7278344512 g/dia.

| Solução do curral de lactação, por animal | Custo UM/dia | DMI kg MS | Ca absorvível g | P absorvível g | Iterações |
|---|---:|---:|---:|---:|---:|
| SLSQP original | 0,3453396277 | 33,214455 | 115,708767 | 70,109373 | 27 |
| HiGHS anterior | 26,5926553519 | 28,915258 | 1.056,776297 | 793,372088 | 1 |
| SLSQP controlado com MTL | 0,3453396277 | 33,214455 | 115,708767 | 70,109373 | 25 |
| HiGHS aprimorado | 0,3453402669 | 33,214347 | 115,709127 | 70,109314 | 5 |

Todas passam no indicador nativo, inclusive a candidata histórica excessiva. A antiga tinha aproximadamente Ca=4,174% e P=3,473% da MS. A nova tem aproximadamente Ca=1,160% e P=0,330%; usa zero do ingrediente 231 por resultado da otimização. A nova encerrou por estabilidade do objetivo e viabilidade original, não por primeira aprovação. O dia não foi excluído.

## Formulação mineral e referências científicas

A política `nrc2005_mtl` acrescenta tetos de Ca total de 1,5% MS e P total de 0,7% MS, segundo [NRC 2005, Mineral Tolerance of Animals](https://www.nationalacademies.org/publications/11309), DOI 10.17226/11309. São tetos de tolerância, não metas nutricionais ou máximos absorvíveis. Os requisitos continuam NRC 2001. A atribuição e a distinção entre concentração e absorção foram conferidas no [capítulo Minerals da National Academies](https://www.ncbi.nlm.nih.gov/books/NBK600600/); não se importaram equações NASEM 2021 para o NRC.

Se x_i é kg MS e Ca_i/P_i são percentuais da MS, as novas linhas são Σx_i(15−10Ca_i)≥0 e Σx_i(7−10P_i)≥0. Os tetos dependem da DMI total. A mesma política entra no SLSQP e no HiGHS das comparações controladas. O cenário histórico pode ser reproduzido com `--mineral-policy native`.

A relação Ca:P fica registrada, sem faixa estreita ou igualdade inventada. O limite nativo do suplemento é 100 kg MS/animal/dia neste cenário, amplo demais para ser interpretado como recomendação mineral. Não se inventou um máximo próprio do produto: usam-se os limites reais e as concentrações totais da dieta. A absorção genérica local por classe alimentar continua sendo uma limitação, não uma reprodução integral de todos os coeficientes específicos do livro NRC 2001.

## Algoritmo e critérios de encerramento

A linearização usa as funções nativas da categoria, diferenças finitas progressivas de 10⁻⁴ kg MS e conversão explícita para as variáveis em matéria natural do LP. O raio inicia em 5, expande em caso de inviabilidade local ou passo na fronteira e retrai quando a função de mérito não melhora. A função de mérito soma custo e 10⁴ vezes violações normalizadas. O teto do raio é max(10, 2·DMI máxima). Se a linearização continuar inviável e não existir candidata viável, há uma tentativa com inicialização distribuída entre alimentos não minerais, respeitando limites reais. Isso é apenas um ponto de partida numérico.

A reserva de arredondamento é 10⁻⁴+10⁻⁶‖gradiente‖₁ por linha. As candidatas são conferidas com as restrições não lineares originais e com o NutritionEvaluator após arredondamento de seis casas, igual ao Pen. A melhor candidata viável é conservada. O orçamento é de 60 LPs; raio abaixo de 10⁻⁵ sinaliza estagnação. O critério de convergência exige viabilidade original e mudança de custo não superior a 10⁻⁷·max(1,|custo|). Ótimo local de um LP não certifica ótimo global do problema original.

No ano ampliado, houve 959 chamadas convergentes, 42 encerramentos por estagnação e um por limite de iterações. As 43 últimas conservaram candidatas viáveis e são explicitamente marcadas como não convergentes. São limitações presentes, sem declaração de ótimo global.

## Execuções progressivas e comparação controlada

As pastas `hibrido_validado_1`, `hibrido_7`, `hibrido_30`, `hibrido_365` registram primeiro a correção da lactação, antes dos experimentos com demais categorias. Nessa rodada, as 365 chamadas HiGHS foram aceitas; as outras categorias permaneceram nativas. O custo foi 2.317,17574260 UM.

A ampliação foi testada em `todas_reinicio_1`, `hibrido_todas_final_7`, `hibrido_todas_final_30`, e na execução definitiva `hibrido_final_365`. O exclusivo definitivo está em `exclusivo_estoque_1`, `_7`, `_30`, `_365`. O nativo controlado está em `nativo_mtl_1`, `_7`, `_30` e `nativo_final_365`. Todos usam semente 42, clima de 2013, preços/ingredientes/estoques/manejo equivalentes. Os três estados iniciais definitivos são idênticos, com 26 animais efetivos.

| Indicador de 365 dias | SLSQP controlado | HiGHS híbrido ampliado | HiGHS exclusivo |
|---|---:|---:|---:|
| Valor do alimento efetivamente deduzido, UM | 2.319,34875854 | 2.316,45106770 | 2.316,45106770 |
| Despesa de compra, UM | 2.323,21061538 | 2.320,31250669 | 2.320,31250669 |
| Leite, kg | 140.223,666523 | 140.223,666523 | 140.223,666523 |
| Chamadas HiGHS aceitas | 0 | 1.002 | 1.002 |
| Chamadas SLSQP | 1.002 | 0 | 0 |
| Fallbacks | 0 | 0 | 0 |
| Curral-dias adultos aprovados | 362 | 998 | 998 |
| Curral-dias adultos reprovados | 636 | 0 | 0 |
| Curral-dias adultos dentro dos tetos Ca/P | 998 | 998 | 998 |

A diferença no valor consumido é de 2,89769084 UM, ou **0,1249355%**. Não se alterou a metodologia contábil já auditada. Não é resultado comercial e não se conclui velocidade relativa a partir de execuções concorrentes.

## Categorias e modo exclusivo

As chamadas ampliadas foram growing=365, close_up=272 e lac_cow=365. Close_up contém vacas secas e novilhas de pré-parto; não foi criada uma equação de lactação para elas. A seleção heifer nativa remove as linhas de energia total e lactação e mantém suas demais condições. Os bezerros mantêm o fluxo próprio, sem serem contados como fallback.

O exclusivo impõe falha explícita em vez de invocar SLSQP. Sua execução anual passou sem fallback neste cenário. `growing and close_up` tem teste de seleção das equações nativas, mas não ocorre no agrupamento padrão fixado pelo HerdManager e não teve um cenário anual próprio. A validação não é universal para NASEM, dietas prescritas pelo usuário ou todos os possíveis agrupamentos.

## Estoques e correspondência física

A ampliação encontrou uma falha nativa após 125 dias: a consulta incluía três lotes do alimento 104 de 0,000038; 0,000689347375; 0,00080920051875 kg MS, enquanto a retirada ignorava cada um. A soma era 0,00153654789375 kg MS. `diagnostico_estoque_126/summary.json` guarda os lotes reais remanescentes e o traceback. A correção usa uma segunda passagem para retirar massa real desses lotes antes de declarar falta; não cria alimento, aumenta estoque ou altera quantidades nutricionais.

As execuções definitivas receberam a mesma correção em FeedManager. Nenhum estoque registrado foi negativo. `auditoria_fisica.json` compara a soma das dietas dos currais multiplicadas pelas populações com o fornecimento efetivamente deduzido. A tolerância nativa de 0,001 kg MS permanece: o maior desvio foi 0,00082 kg MS por alimento/dia no HiGHS e 0,000788 no SLSQP. Não se afirmou correspondência matemática perfeita onde existe essa tolerância operacional.

## Reprovações e limitações do indicador nativo

`reprovacoes_historicas.csv` e `auditoria_historica.json` distinguem as 654 reprovações adultas do SLSQP histórico e 481 do híbrido antigo. O primeiro dia antigo tinha dois excessos totais minerais, não representados pelo avaliador. As outras ocorrências verificadas dos campos de reprovação foram desvios abaixo de 10⁻³ nas respectivas unidades. O limiar serve exclusivamente para classificar a auditoria: não alterou avaliações nem transformou reprovações em aprovações.

No SLSQP controlado atual, as 636 reprovações corresponderam a 751 ocorrências de critérios, pois um curral-dia pode reprovar em mais de um. Campos: DMI=358, P=305, NDF=59, proteína metabolizável=26, Ca=2, energia total=1. Todas ficaram abaixo de 10⁻³ na unidade própria e estão em `reprovacoes_detalhadas.csv`, por dia, curral e categoria. HiGHS não apresentou reprovação adulta nessa rodada. A aprovação continua limitada aos indicadores implementados, mesmo com os tetos adicionais.

## Por que leite e pesos são iguais

`MilkProduction._update_daily_milk_production` calcula a curva de Wood com DEL e parâmetros de lactação, adicionando variação e eventual redução gerenciada. A rotina não recebe a dieta como variável direta. As equações de crescimento de bezerros, novilhas e vacas usam metas, idade, peso maduro, prenhez e mobilização tecidual por DEL/paridade, sem ajuste energético genérico em função de cada dieta formulada.

`Pen.set_animal_nutritional_supply` transfere a oferta anterior e calcula a nova; `Animal.calculate_nutrition_requirements` utiliza dados anteriores de dieta em cálculos de requisitos. A oferta também participa de digestão e excreção. Há integração dinâmica real, porém resposta produtiva e de peso não equivale a um modelo mecanístico completo de limitação alimentar. Os estados registrados e o leite iguais foram observados, não impostos. O modelo biológico não foi modificado.

## Preços comerciais e licenças

`cenario_comercial_parcial.json` guarda uma cotação CEPEA verificável e datada, com conversão MN→MS; os outros preços ficam nulos. Não há base verificada suficiente para declarar uma ração anual inteiramente a preços comerciais. Frete, processamento e volumosos requerem referências próprias. O cenário demonstrativo permanece integralmente preservado.

`COPYING.txt` e `COPYING.LESSER.txt` foram recuperados da revisão candidata upstream d471c742eadc2e37b76545d0d0f0d10b6c9ef763. Seus hashes de blob foram conferidos com a árvore upstream e estão em `licencas_recuperadas.json`. Os avisos de autoria originais permanecem.

Os outros quatro ausentes foram inspecionados individualmente e guardados em `ausentes_upstream`: workflow de CI com operações de formatação/push (não instalado para não introduzir automação alheia); calculadora manual de composição inicial do rebanho (auxiliar, não dependência do motor); `.keep` vazio (marcador de diretório); filtro CSV `.*` (seleção de todas as variáveis, dispensável para o diário próprio). Não foi importada uma versão recente completa. A revisão permanece candidata temporal com alta correspondência, sem prova de ancestralidade exata.

## Testes e reprodução

**954 testes passaram em 128,87 s**, preservando os 937 anteriores e adicionando 17 regressões. Inclui um subprocesso real de 365 dias exclusivo e teste do frontend com processos reais. Não se relaxaram os testes anteriores. `testes_finais.xml` e `correcao_suite_final.log.txt` registram o resultado. Tentativas intermediárias falhas estão preservadas; a versão inicial da nova interface teve uma chave incorreta de curral, corrigida antes dessa suíte final.

```powershell
.venv/Scripts/python.exe -X utf8 -m experiments.annual --days 365 --strategy native_slsqp --output output/nativo_controlado_novo
.venv/Scripts/python.exe -X utf8 -m experiments.annual --days 365 --strategy linear_highs_all --output output/hibrido_controlado_novo
.venv/Scripts/python.exe -X utf8 -m experiments.annual --days 365 --strategy linear_highs_exclusive --output output/exclusivo_controlado_novo
.venv/Scripts/python.exe -X utf8 -m experiments.first_day_regression --output output/replay_novo
.venv/Scripts/python.exe -X utf8 -m experiments.convergence_report
```

O runner recusa reutilizar a pasta de uma execução. O relatório deriva gráficos e CSVs dos diários definitivos. `hashes_implementacao.json` identifica as fontes atuais; a revisão Git sozinha não inclui as alterações locais ainda não commitadas.

## Arquivos de implementação desta rodada

Modificados: `dynamic_linear_optimizer.py`, `herd_manager.py`, `feed_manager.py`, `RUFAS/input/metadata/properties/default.json`, `experiments/annual.py`, `frontend/annual.py`, READMEs e os 14 capítulos. Novos: `mineral_limits.py`, `first_day_regression.py`, `recover_licenses.py`, `convergence_report.py`, `tests/test_dynamic_convergence.py`, fixture congelada, licenças recuperadas e evidências deste diretório. Não houve remoção de arquivos do projeto. `linear_diet.py`, frontend/app e outros documentos já tinham alterações locais anteriores; foram preservadas, sem atribuir toda a diferença Git a esta rodada.




## Verificação final do estado apresentado

Após os últimos ajustes de despacho e registro de incompatibilidades, a suíte completa passou novamente: **954 aprovados em 11.233,60 s (3:07:13)**, conforme `testes_verificacao.xml` e `correcao_verificacao.log.txt`. A rodada anterior havia passado em 128,87 s; esses tempos de execuções sem controle de ambiente não foram usados como benchmark. Uma verificação direcionada adicional passou **206 testes em 185,64 s** (`correcao_config_policy.log.txt`), sem somar casos sobrepostos à contagem de 954.

`nativo_mtl_flag_false_1/configuration_check.json` registra a checagem real de um dia com a flag de gravação desligada e política NRC 2005 explicitamente selecionada: o despacho continuou aplicando a política. `manifesto_rodadas.json` identifica ambiente, diretórios definitivos, semente e escopo dos hashes. Alterações posteriores às rodadas numéricas ficaram limitadas ao registro de incompatibilidades e à ativação explícita da política quando a flag está desligada; a regressão anual real passou novamente no estado de revisão.
