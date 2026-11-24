# Fósforo absorvido no PO-RuFaS

A formulação e o parecer nativo usam NRC 2001 na implementação local do RuFaS. O seletor de restrições minerais ativa mínimos NRC de fósforo e cálcio absorvíveis. A opção NASEM 2021 calcula apenas uma exigência de fósforo independente.

## Exigência de fósforo segundo NASEM 2021

O capítulo 7, seção **Phosphorus**, descreve quatro componentes do fósforo absorvido, em g/dia:

- **Manutenção**, equação 7-5b, p. 112. Para vacas adultas, `1,0 × DMI + 0,0006 × BW`. DMI está em kg MS/dia e BW em kg. Os termos representam as perdas fecais endógenas e urinárias. A equação 7-5a usa 0,8 no termo de DMI para novilhas em crescimento.
- **Crescimento**, equação 7-6, p. 112. `(1,2 + 4,635 × (MatBW/BW)^0,22) × ADG`. O ganho médio diário (ADG) está em kg/dia. O fator representa gramas retidas por kg de ganho. No código local, o termo só é aplicado até a segunda lactação. A rotina nativa de crescimento fornece o ADG ao cálculo.
- **Gestação**, equação 7-7, p. 112. O RuFaS calcula `[F(t) − F(t−1)] × BW/715`, com `F(t) = 0,02743 × exp((0,05527 − 0,000075 × t) × t)`, e `t` em dias. O termo é zero antes do dia 190, ou se não há gestação registrada.
- **Lactação**, equações 7-8a e 7-8b, pp. 112–113. Com proteína verdadeira conhecida, `leite × (0,49 + 0,13 × proteína)`. Leite está em kg/dia e proteína em porcentagem, por exemplo, 3,2. A equação 7-8a usa 0,90 g P/kg de leite quando a proteína é desconhecida. O diagnóstico web usa o teor documentado no cenário.

A interface chama o despacho NASEM de `Animal.calculate_nutrition_requirements` em uma cópia local do animal. Essa chamada usa a estimativa de consumo do próprio NASEM e chega a `NASEMRequirementsCalculator._calculate_phosphorus_requirement`. O mínimo do calculador é zero. O diagnóstico considera a fisiologia e as hipóteses da fotografia do animal. O módulo diário de reservas e fluxos de fósforo da fazenda fica fora dessa execução. A regra local de manutenção para vacas secas também difere da descrição de vacas adultas do livro. O diagnóstico web cobre vacas em lactação.

O calculador NRC local usa `1,0 × DMI + 0,002 × BW` para manutenção da vaca em lactação, `0,90 × leite` para lactação, o fator `ADG/0,96` no componente de crescimento e o incremento gestacional sem a escala `BW/715`, após 190 dias. O avaliador NRC compara a oferta com o maior valor entre a exigência calculada e a exigência processual registrada no animal. [NASEM 2021, capítulo 7, pp. 112–114 e tabela 19-3](https://www.ncbi.nlm.nih.gov/books/NBK600603/pdf/Bookshelf_NBK600603.pdf) · [NRC 2001, capítulo 6](https://doi.org/10.17226/9825)

## Oferta de fósforo e viabilidade do modo NASEM

O NASEM 2021, na seção **Dietary Requirement and Efficiency of Absorption**, p. 113, usa os coeficientes 0,84 para a fração inorgânica e 0,68 para a orgânica em alimentos basais, ponderados pelas frações da fonte. O livro informa como tratar alimentos sem fracionamento e tabula os coeficientes de suplementos por fonte na tabela 19-3. O exemplo do fosfato bicálcico usa 0,75 como referência na p. 113.

A biblioteca NASEM local tem campos `P_inorg`, `P_org` e `Abs_phosphorus`. A tabela local lista `Abs_phosphorus = 0,8` para o ID 231. A rotina nativa de oferta ignora esses campos nos dois padrões e aplica 0,64 a forragens, 0,70 a concentrados e 0,80 aos minerais. A rotina de energia NASEM também retorna energia de mantença e crescimento zeradas na estrutura entregue ao avaliador. Esses comportamentos impedem expor a integração atual como modo NASEM completo. A interface exibe a exigência NASEM sem estimar um balanço NASEM a partir da oferta NRC. [NASEM 2021, capítulo 7, p. 113](https://www.ncbi.nlm.nih.gov/books/NBK600600/)

## Restrição de fósforo e cálcio no LP NRC

Se `xᵢ` é a inclusão em kg de matéria natural/dia, `dᵢ` a fração de matéria seca e `cᵢ` a oferta absorvível em g/kg MS, o mínimo é `Σ(xᵢ × dᵢ × cᵢ) ≥ exigência em g/dia`. A oferta total ingerida é `Σ(xᵢ × dᵢ × teor em % MS × 10)`. Exemplo com o ID 231, teor de 19,3% MS → 193 g P total/kg MS → 154,4 g P absorvível/kg MS pelo cálculo local.

O adaptador integrado obtém cada coeficiente chamando `NutritionSupplyCalculator` com exatamente 1 kg MS daquele ingrediente. Para cálcio, a mesma API usa 0,30, 0,60 e 0,95, respectivamente. A matéria seca é fixada antes da resolução. As duas linhas entram no mesmo HiGHS, com coeficientes fixos e uma margem numérica de 0,000001 g/dia para estabilizar o teste nativo de sinal após o retorno pelo RationManager. O JSON distingue a exigência nativa e o mínimo numérico do LP. O resultado é reconferido contra a oferta recalculada a partir do RationManager.

Os mínimos de MS, PB e NEL, a faixa de FDN, os limites de inclusão e o estoque continuam aplicáveis. A verificação nativa inclui energia total, mantença, lactação, crescimento, proteína metabolizável, cálcio, fósforo, matéria seca, FDN total, FDN de forragem e gordura. Os mínimos minerais deixam em aberto limites superiores, proporção Ca:P, outros minerais e a resposta a excesso de fósforo. A seleção de suplementos exige dados de inclusão e disponibilidade do cenário.

## Reprodução pelo frontend

1. Inicie `frontend/iniciar_frontend.bat`. Escolha 98605 com 30 kg de leite/dia ou 93785 com 31 kg/dia. Mantenha os três ingredientes padrão, sete dias, PB mínima de 3,6 kg/dia, NEL mínima de 35 Mcal/dia e FDN entre 28% e 40% MS.
2. Execute uma vez com a opção mineral desativada. Repita com **Exigir fósforo e cálcio absorvíveis no LP (NRC 2001)** ativa.
3. Em **Ingredientes**, filtre por Mineral, adicione o fosfato bicálcico ID 231 e configure preço R$ 5,00/kg MN, estoque 1,00 kg MN, inclusão de 0 a 0,10 kg MN/dia e NEL 0 Mcal/kg MS. Os valores de preço, estoque e limite são hipóteses para reprodução. A composição do fosfato vem do arquivo NRC, que registra DE zero para o ID. Execute com a opção mineral ativa.
4. Abra **Resultados** e consulte o balanço, as verificações e o parecer. Para comparar também a exigência NASEM, ative a caixa de diagnóstico antes de executar.

Os IDs 231 (fosfato bicálcico, 19,3% P e 22,0% Ca na MS) e 232 (fosfato monocálcico, 21,6% P e 16,4% Ca na MS) estão no catálogo NRC. A simulação abaixo usa 231. A interface exibe os teores totais e exige parâmetros de cenário para ingredientes adicionais.

| Animal | Restrições P/Ca | ID 231 | LP | R$/dia | MS kg/d | PB kg/d | NEL Mcal/d | FDN kg/d | P total g/d | P absorvível g/d | P exigido g/d | Δ P g/d | Parecer RuFaS |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 98605 | Desativadas | Ausente | Ótimo | 35,1059 | 22,232 | 3,600 | 35,00 | 6,412 | 65,80 | 43,81 | 50,49 | −6,68 | Não aprovada |
| 98605 | Ativas | Ausente | Inviável | — | — | — | — | — | — | — | 50,49 | — | Não avaliada |
| 98605 | Ativas | Presente | Ótimo | 35,3416 | 22,232 | 3,600 | 35,00 | 6,365 | 74,12 | 50,49 | 50,49 | ≈0,00 | Aprovada |
| 93785 | Desativadas | Ausente | Ótimo | 34,9440 | 22,701 | 3,600 | 35,00 | 6,925 | 65,23 | 43,16 | 51,77 | −8,61 | Não aprovada |
| 93785 | Ativas | Ausente | Ótimo | 38,2663 | 22,701 | 4,840 | 35,00 | 6,660 | 77,32 | 51,77 | 51,77 | ≈0,00 | Aprovada |
| 93785 | Ativas | Presente | Ótimo | 35,2480 | 22,701 | 3,600 | 35,00 | 6,865 | 75,96 | 51,77 | 51,77 | ≈0,00 | Aprovada |

| Animal | P/Ca ativos | Alfafa | Milho | Farelo de soja | Fosfato 231 |
|---|---|---:|---:|---:|---:|
| 98605 | Não | 14,8300 | 9,5283 | 0,4979 | — |
| 98605 | Sim, com suplemento | 14,6822 | 9,5874 | 0,5410 | 0,0442 |
| 93785 | Não | 16,4499 | 8,8805 | 0,0261 | — |
| 93785 | Sim, sem suplemento | 15,5065 | 6,4632 | 3,3574 | — |
| 93785 | Sim, com suplemento | 16,2592 | 8,9568 | 0,0816 | 0,0570 |

Quantidades da segunda tabela em kg MN por animal/dia. Com suplemento, as 15 verificações do LP foram atendidas em ambos os casos. As ofertas de Ca absorvível foram 70,47 g/dia e 78,35 g/dia, respectivamente, ante exigências de 56,56 e 56,46 g/dia. Na execução isolada NASEM, as exigências de P foram 49,73 e 49,97 g/dia, respectivamente.

Para 98605, retirar apenas o mínimo de fósforo devolve a viabilidade aos três alimentos. Para 93785, os três alimentos conseguem suprir o mínimo NRC de fósforo com mais farelo de soja. Os dois cenários de referência com os mínimos desligados continuam reprovados por déficit de P.

## Auditoria do parecer nativo após a correção de gordura

O método de oferta calcula a margem como `7% da MS − teor de gordura da dieta`, com gordura representada pelo extrato etéreo. A comparação antiga exigia margem zero. A regra corrigida aceita margem não negativa, com tolerância absoluta de `1e-9` ponto percentual para arredondamento. O NRC 2001 descreve 6–7% de gordura total como limite superior geral, com orientação dependente do estágio e do tipo de gordura. O NASEM 2021 discute separadamente o limite geral para ácidos graxos, uma medida distinta do extrato etéreo. [NRC 2001, p. 32](https://doi.org/10.17226/9825) · [NASEM 2021, capítulo 4 — Fat](https://www.ncbi.nlm.nih.gov/books/NBK600599/)

| Critério nativo | Unidade do delta | 98605 com ID 231 | 93785 com ID 231 |
|---|---|---:|---:|
| Energia total | Mcal/dia | +2,0558 | +1,5405 |
| Energia de mantença | Mcal/dia | +23,9809 | +24,1442 |
| Energia de lactação | Mcal/dia | +11,9515 | +11,0716 |
| Energia de crescimento | Mcal/dia | +20,5804 | +20,0915 |
| Proteína metabolizável | g/dia | 0 | 0 |
| Cálcio absorvível | g/dia | +13,9138 | +21,8858 |
| Fósforo absorvível | g/dia | ≈+0,000001 | ≈+0,000001 |
| Matéria seca | kg/dia | 0 | 0 |
| FDN total | p.p. de MS | 0 | 0 |
| FDN de forragem | p.p. de MS | +9,8085 | +11,9048 |
| Margem até o máximo de gordura | p.p. de MS | +3,8894 | +3,9197 |

Os 11 critérios foram atendidos nas duas dietas. Os teores de gordura calculados foram 3,1106% e 3,0803% MS, respectivamente. O parecer cobre o conjunto de critérios do avaliador NRC local. Permanecem fora dessa verificação os limites superiores de minerais, a razão Ca:P, o perfil de ácidos graxos e uma avaliação NASEM completa.
