# Resultados validados e auditoria técnica

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

Validação registrada em **24/11/2026 00:29:02 -0300**, horário de São Paulo. Evidência: `evidencias/validacao.json`.

## Estado real e escopo investigado

Foram examinados os módulos `linear_diet`, adaptadores, exemplos, catálogo, testes de rações/nutrição,
`pyproject.toml`, documentação em `docs/`, entradas em `input/data/feed/` e saídas dos exemplos.
O repositório possui módulos de animais, alimentação, solo/culturas e demais subsistemas.
A validação se concentrou nos componentes ligados a este trabalho; não afirma auditoria de todo o simulador.

O otimizador original `ration_optimizer.py` usa `minimize` com SLSQP. O módulo novo usa
`scipy.optimize.linprog(method="highs")`, com escolha automática entre os métodos LP suportados pelo HiGHS.
Não afirmamos ter fixado simplex ou pontos interiores. O núcleo original não foi modificado para a apresentação.

## Entradas da demonstração escolhida

Animal: 650 kg, DEL 100, leite 30 kg/dia, gordura 3,8%, proteína verdadeira 3,2%.
No calculador: peso adulto 700 kg; 2ª lactação; sem gestação informada; ECC 3/5;
lactose 4,8%; alojamento Barn; demais parâmetros em `linear_diet_example.example_inputs`.
Período: dieta diária constante por sete dias, com estoque alocado a um animal.

| Ingrediente | R$/kg MN | Estoque kg MN | Máximo kg MN/dia | MS % | PB % MS | FDN % MS | NEL Mcal/kg MS |
|---|---:|---:|---:|---:|---:|---:|---:|
| Alfafa (farinha) | 1,2642 | 166,1130 | 17,7187 | 90,3 | 19,2 | 41,6 | 1,3 |
| Milho (moagem media) | 1,5858 | 113,5074 | 11,3507 | 88,1 | 9,4 | 9,5 | 2,0 |
| Farelo de soja | 2,5060 | 67,0391 | 6,7039 | 89,5 | 53,8 | 9,8 | 1,8 |

Preços, estoques, limites operacionais e NEL são ilustrativos. Composição: `input/data/feed/NRC_comp.csv`,
IDs 1, 44 e 167. PB e FDN são teores em base MS; o preço exibido é por kg MN.
MS exigida: 22,5453 kg/dia, calculada pelo RuFaS/NRC.
Metas ilustrativas: PB ≥ 3,6 kg/dia; NEL ≥ 35 Mcal/dia; FDN entre 28% e 40% da MS.

## Saída obtida de execução real

| Ingrediente | kg MN/dia | kg MS/dia | R$/dia |
|---|---:|---:|---:|
| Alfafa (farinha) | 15,9119 | 14,3685 | 20,1158 |
| Milho (moagem media) | 9,0957 | 8,0133 | 14,4239 |
| Farelo de soja | 0,1828 | 0,1636 | 0,4580 |

**Status:** `optimal`. **Custo:** R$ 34,9978/dia.
Custo independente recomputado: `34.997773642176`.
MS: 22,5453 kg; PB: 3,6000 kg;
NEL: 35,0000 Mcal; FDN: 6,7546 kg
(29,96% da MS).

| Verificação | Fornecido | Mínimo | Máximo | Folga | Status |
|---|---:|---:|---:|---:|---|
| DM_kg | 22.54532000 | 22.545320001976965 | 22.545320001976965 | -3.5527137e-15 | OK |
| CP_kg | 3.60000000 | 3.6 | None | 0 | OK |
| NEL_Mcal | 35.00000000 | 35.0 | None | 0 | OK |
| NDF_min_kg_residual | 0.44188290 | 0.0 | None | 0.4418829 | OK |
| NDF_max_kg_residual | -2.26355550 | None | 0.0 | 2.2635555 | OK |
| inclusion_1_kg_day | 15.91191822 | 0.0 | 17.718715393133998 | 1.8067972 | OK |
| stock_1_kg | 111.38342751 | 0.0 | 166.11295681063123 | 54.729529 | OK |
| inclusion_44_kg_day | 9.09565875 | 0.0 | 11.350737797956869 | 2.2550791 | OK |
| stock_44_kg | 63.66961122 | 0.0 | 113.50737797956869 | 49.837767 | OK |
| inclusion_167_kg_day | 0.18277374 | 0.0 | 6.70391061452514 | 0.18277374 | OK |
| stock_167_kg | 1.27941619 | 0.0 | 67.0391061452514 | 1.2794162 | OK |

`None` indica ausência daquele lado do limite. As linhas de FDN verificam resíduos lineares em kg,
não percentuais diretamente. Folgas numericamente próximas de zero são avaliadas com tolerância absoluta de 1e-7.
As 11 linhas incluem cinco verificações nutricionais e seis de inclusão/estoques.
Não são onze nutrientes. Valores exibidos são arredondados; o solver usa precisão completa.

## Modelo auditado

```text
x_i = kg MN/dia; d_i = kg MS/kg MN; p_i = R$/kg MN.
c_i = kg PB/kg MS; e_i = Mcal NEL/kg MS; f_i = kg FDN/kg MS.
Min C = soma(p_i x_i)
MS_min <= soma(d_i x_i) <= MS_max
soma(d_i c_i x_i) >= PB_min
soma(d_i e_i x_i) >= NEL_min
soma(d_i (f_i-r_min) x_i) >= 0
soma(d_i (f_i-r_max) x_i) <= 0
L_i <= x_i <= U_i; T x_i <= S_i; x_i >= 0
```

Todas as expressões são lineares em x. A igualdade de MS usa os mesmos limites inferior/superior.
Para MS total positiva, a reformulação da proporção de FDN preserva equivalência algébrica.
O núcleo aceita mínimos minerais totais opcionais quando a composição é conhecida para todos os ingredientes;
não há minerais ativos nesta demo. Não há máximos minerais, máximo de PB ou modelo completo de aminoácidos.

No adaptador, preço por kg MS é multiplicado por d_i para virar preço por kg MN.
Estoque e limites em kg MS são divididos por d_i para virar kg MN. Percentuais são divididos por 100.
R$/tonelada é dividido por 1000 sem trocar a base. O período multiplica quantidades diárias, não o preço unitário.

## Integração comprovada e limites

Os testes usam Feed/NRCFeed, NutritionRequirements, calculador NRC, FeedInRation e cálculo de PB/FDN do RuFaS.
Há teste de snapshot mínimo de Animal/MilkProduction. Isso comprova os adaptadores; não uma simulação de fazenda.
O resultado fornece um dicionário em kg MS/dia compatível com rações. Não há aplicação automática nem baixa de estoque.

A única exigência importada diretamente para o LP nos exemplos é a MS. NRC (2001), capítulo 1, p. 4,
equação 1-2, é a referência do calculador reutilizado. NASEM (2021) integra as fontes do RuFaS e a biblioteca
alternativa do catálogo, mas não foi usado para calcular todas as metas da demo. DE não foi convertida em NEL;
proteína metabolizável não foi confundida com PB; minerais absorvidos não foram confundidos com totais.

## Testes e evidência de execução

**433 testes executados: zero falhas, zero erros e zero skips.**
Incluem 33 testes específicos dos módulos novos e testes preexistentes de rações, nutrição e estruturas relacionadas.
A suíte completa da fazenda não foi executada. Comandos e saída integral estão em `evidencias/testes.md`;
o relatório JUnit está em `evidencias/testes.xml`. Versões e hashes de fontes estão em `evidencias/validacao.json`.

Versões: {"numpy": "2.2.0", "scipy": "1.18.1", "pytest": "9.2.0", "python-pptx": "1.0.2"}.
Tempo de chamada do solver na demo registrada: 0.0039 s.
O tempo total do processo, com imports, foi 1.638 s nesta execução.
Não é benchmark. Pré-aqueça o ambiente antes da apresentação; a duração da fala precisa ser ensaiada.

## Outros resultados disponíveis

`output/linear_diet_example.json` e `output/linear_diet_cow_2.json` foram inspecionados, mas os slides usam
uma nova execução registrada em `evidencias/base_slides.json`. O cenário da segunda vaca é histórico.
O catálogo foi executado novamente com semente 42: ver `evidencias/catalogo.md` e `evidencias/catalogo/result.json`.
Ele avalia 300 registros, utiliza 185 candidatos e registra 115 exclusões. Essa execução é material de apoio,
não uma segunda demonstração durante os cinco minutos. Seus parâmetros diferem do exemplo de três alimentos.
Não há comparação válida de economia ou percentual de ganho nesta entrega.
