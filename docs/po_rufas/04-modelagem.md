# Modelagem matemática estática e dinâmica
[Sumário](README.md)

Existem dois problemas distintos: o LP estático com coeficientes fixos e a programação linear sequencial dinâmica. Seus custos, variáveis, exigências e interpretações não devem ser intercambiados.

## Modelo 1 — LP estático

## Conjuntos, variáveis e parâmetros

O conjunto $I$ contém os ingredientes selecionados; $J$ contém os minerais totais opcionais. A variável contínua $x_i\ge0$ mede kg de matéria natural por animal/dia.

| Símbolo | Significado | Unidade |
|---|---|---|
| $p_i$ | Preço | R$/kg MN |
| $d_i$ | Fração de MS | kg MS/kg MN |
| $c_i,f_i$ | Fração PB e FDN na MS | kg/kg MS |
| $e_i$ | NEL fixa | Mcal/kg MS |
| $S_i,T$ | Estoque alocado e período | kg MN; dias |
| $L_i,U_i$ | Inclusão mínima e máxima | kg MN/dia |
| $D_{\min},D_{\max}$ | Intervalo de MS | kg/dia |
| $B,E$ | Mínimos PB e NEL | kg/dia; Mcal/dia |
| $r_{\min},r_{\max}$ | Faixa FDN | fração MS |
| $a_{Pi},a_{Cai}$ | Oferta absorvível por ingrediente | g/kg MS |
| $R_P,R_{Ca}$ | Exigências absorvidas | g/dia |

## Objetivo

$$\min C=\sum_{i\in I}p_i x_i$$

O custo diário é linear e recalculado por soma de custos individuais. Em T dias, o custo estimado é TC. Implementação em `optimize_diet`, no módulo [linear_diet.py](../../RUFAS/biophysical/animal/ration/linear_diet.py). A origem é a formulação de custo mínimo em Pesquisa Operacional; os preços vêm do cenário.

## Matéria seca

$$D_{\min}\le\sum_{i\in I}d_i x_i\le D_{\max}$$

A linha `DM_kg` em `_nutrient_rows` limita o consumo. O adaptador `requirements_from_rufas` usa a previsão nativa NRC para as duas extremidades. A igualdade é uma hipótese operacional de consumo fixo; a fonte do cálculo é o método NRC reutilizado pelo Animal.

## Proteína bruta

$$\sum_{i\in I}d_i c_i x_i\ge B$$

A linha `CP_kg` soma a oferta de PB. Composição vem da biblioteca NRC; B é meta externa. A MP calculada pelo RuFaS é avaliada posteriormente, com sua própria unidade e modelo.

## Energia

$$\sum_{i\in I}d_i e_i x_i\ge E$$

A linha `NEL_Mcal` usa coeficientes e meta NEL explicitamente fornecidos. O cenário demonstrativo os fixa; não se deduz NEL de DE. A avaliação nativa calcula suas próprias ofertas de energia.

## FDN

$$\sum_{i\in I}d_i(f_i-r_{\min})x_i\ge0$$
$$\sum_{i\in I}d_i(f_i-r_{\max})x_i\le0$$

As linhas `NDF_min_kg_residual` e `NDF_max_kg_residual` reformulam exatamente a faixa proporcional quando a MS é positiva. Composição vem da biblioteca; os limites são metas externas. `DietRequirements` rejeita mínimo de MS zero quando há proporções de FDN.

## Estoque e inclusão

$$T x_i\le S_i,\qquad L_i\le x_i\le U_i,\qquad x_i\ge0$$

`optimize_diet` usa teto min(S_i/T,U_i), com U_i opcional. Registra também linhas de estoque e inclusão para conferir o resultado. A hipótese é dieta constante durante T dias, sem reposição ou perdas. Esses limites são definidos pelo usuário.

## Fósforo e cálcio absorvíveis

$$\sum_{i\in I}d_i a_{Pi}x_i\ge R_P+\epsilon_P$$
$$\sum_{i\in I}d_i a_{Cai}x_i\ge R_{Ca}+\epsilon_{Ca}$$

As linhas opcionais `absorbed_phosphorus_g` e `absorbed_calcium_g` são construídas em `optimize_diet(absorbed_minerals=...)`. `optimize_animal_ration` calcula os coeficientes chamando a oferta nativa para 1 kg MS de cada ingrediente. $R_P=\max(P_{\mathrm{NRC}},P_{\mathrm{processual}})$ e $R_{Ca}=Ca_{\mathrm{NRC}}$. A margem é $10^{-6}$ g/dia para metas positivas e zero para meta zero. A origem fisiológica é o calculador NRC e a oferta por categoria implementada pelo RuFaS. [Detalhes minerais](08-minerais.md).

## Minerais totais opcionais da API

$$\sum_{i\in I}d_i m_{ij}x_i\ge M_j,\quad j\in J$$

`_nutrient_rows` suporta frações totais e mínimos totais em kg/dia. Esse contrato é independente das novas linhas absorvíveis. O formulário web não oferece edição de mínimos totais adicionais.

## Tolerâncias e linearidade

O verificador `_check` aceita folga ≥ −tolerance em cada unidade de linha, padrão $10^{-7}$, com argumento positivo até $10^{-4}$. O solver tem critérios internos próprios. A reconciliação de P/Ca entre LP e oferta nativa usa tolerância absoluta $10^{-7}$, sem tolerância relativa.

No avaliador, somente a comparação de gordura recebe tolerância $10^{-9}$ ponto percentual. A margem mineral e a tolerância de gordura têm unidades e finalidades distintas.

Todos os coeficientes e requisitos são fixados antes do LP. O modelo não otimiza leite, não atualiza composição por iteração e não inclui as equações biológicas não lineares do SLSQP. Os checks após resolver conferem o modelo informado.



## Substituição numérica de um cenário operacional

Para 98605 com minerais, a ordem é alfafa, milho, soja e fosfato 231:

$$x=(14.682165595,\ 9.587444468,\ 0.540986131,\ 0.044189340)$$
$$d=(0.903,\ 0.881,\ 0.895,\ 0.97),\quad p=(1.2642,\ 1.5858,\ 2.506,\ 5)$$

Custo: $1.2642x_1+1.5858x_2+2.506x_3+5x_4=35.3416211$ R$/dia.

MS: $0.903x_1+0.881x_2+0.895x_3+0.97x_4=22.2315804$ kg/dia.

PB: $0.903(0.192)x_1+0.881(0.094)x_2+0.895(0.538)x_3=3.6000000$ kg/dia.

NEL: $0.903(1.3)x_1+0.881(2.0)x_2+0.895(1.8)x_3=35.0000000$ Mcal/dia.

FDN: $0.903(0.416)x_1+0.881(0.095)x_2+0.895(0.098)x_3=6.3651972$ kg/dia, aproximadamente 28,63% MS. Resíduos da linha mínima e máxima são +0,1403547 e −2,5274349 kg/dia.

P absorvível: coeficientes por kg MS $(1.792,\ 2.1,\ 4.9,\ 154.4)$; $\sum d_i a_{Pi}x_i=50.4867027$ g/dia, atendendo ao mínimo acrescido da margem numérica.

Ca absorvível: coeficientes por kg MS $(4.41,\ 0.24,\ 2.1,\ 209.0)$; $\sum d_i a_{Cai}x_i=70.4702178$ g/dia frente ao mínimo de 56,5564303.

Estoque: $7x_i\le(166.1129568,\ 113.5073780,\ 67.0391061,\ 1.0)_i$. Inclusão: $0\le x_i\le(17.7187154,\ 11.3507378,\ 6.7039106,\ 0.1)_i$.

As composições zero do mineral constam da biblioteca. Estes números são arredondados para exposição; os JSON e CSV guardam a precisão completa. As restrições ativas são identificadas pela folga e tolerância. O módulo comparativo reutiliza _nutrient_rows, _inequalities e _check do backend, com os minerais do relatório operacional.

## Modelo 2 — programação linear sequencial dinâmica

O vetor q representa kg MS por ingrediente, por animal/dia no contrato do RationOptimizer. O custo é cᵀq, com preços em UM/kg MS. A entrada nativa contém requisitos do curral e funções g_j(q)≥0, selecionadas conforme categoria.

Em torno de qᵏ, o LP local usa:

g_j(qᵏ) + J_j(qᵏ)(q−qᵏ) ≥ ε_j,

L_i ≤ q_i ≤ U_i, com |q_i−qᵏ_i| ≤ Δ.

O adaptador resolve no contrato MN do núcleo: q_i=d_i x_i, coeficiente J_ji d_i e preço c_i d_i. As metas PB/NEL externas do formulário estático não substituem energia/MP nativas nesse fluxo. O estoque privado da montagem LP representa limites disponíveis para a formulação; o inventário físico é gerido pelo FeedManager.

### Região local, avaliação e convergência

O raio Δ inicia em 5 kg MS, expande por fator 2 conforme inviabilidade local ou passo na fronteira e retrai por 1/2 quando o mérito não melhora. Teto do raio: max(10, 2·DMI máxima). Os limites locais sempre intersectam os limites físicos e não são um mínimo real de suplementação.

A função de mérito é custo + 10⁴ vezes a soma das violações normalizadas; as escalas são fixadas no ponto inicial. Se a linearização persistir inviável sem candidata viável, uma inicialização alternativa distribui a DMI prevista entre alimentos não minerais, respeitando limites reais. Isso não modifica composição ou prescreve a dieta final.

O Jacobiano usa diferenças finitas progressivas de 10⁻⁴ kg MS. A reserva de arredondamento é ε_j=10⁻⁴+10⁻⁶‖J_j‖₁. O método confere as funções originais e o NutritionEvaluator sobre as quantidades arredondadas a seis casas, como o Pen.

Convergência exige viabilidade original e variação do objetivo ≤10⁻⁷·max(1,|custo|). Há 60 LPs no máximo e parada por estagnação se o raio cai abaixo de 10⁻⁵. A melhor candidata viável encontrada é conservada; não se encerra na primeira aprovação.

No ano validado, 959 chamadas convergiram, 42 estagnaram e uma atingiu o orçamento; as últimas 43 mantiveram soluções viáveis sem convergência. Nenhum desses retornos certifica ótimo global não linear.

### Restrições minerais adicionais

Com Ca_i e P_i em %MS e q_i em kg MS:

Σq_i(15−10Ca_i)≥0; Σq_i(7−10P_i)≥0.

São tetos totais NRC 2005 de 1,5% Ca e 0,7% P na MS. Não são mínimos absorvíveis nem metas nutricionais. A política controlada aplica as mesmas linhas ao SLSQP e ao HiGHS. [Restrições e escopo](05-restricoes.md) · [Minerais](08-minerais.md).
