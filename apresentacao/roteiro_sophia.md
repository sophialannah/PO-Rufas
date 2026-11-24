# Roteiro individual — Sophia Lannah Beatriz Ferreira de Sousa

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

São cinco minutos exclusivos de apresentação, seguidos de cinco minutos de arguição: a demonstração tem **85 segundos**, divididos em 35 + 50. São **300 segundos de exposição + 300 segundos adicionais de perguntas = 600 segundos**.

Use um cronômetro visível. As durações são metas de ensaio, não uma medição das vozes dos integrantes. Ensaie as falas com pausas para respiração, troca de janela e execução. Ajuste o ritmo sem omitir as limitações. Às 05:00, encerre a exposição; às 10:00, encerre as perguntas.

Sequência: slides 1 → 2 → 3 → Alt+Tab para o terminal → Enter para resolver → Alt+Tab de volta → slide 4. Não há quinto slide. O terminal deve estar preparado antes da contagem. Sophia: 155 s (2min35s); Anderson: 145 s (2min25s).

## 00:00–00:45 — Slide 1 — projeto

**Sophia Lannah Beatriz Ferreira de Sousa — 45 segundos**

> Nosso projeto aplica Pesquisa Operacional à formulação de dietas para bovinos leiteiros. Buscamos as quantidades de ingredientes que atendem às restrições com o menor custo diário. Desenvolvemos um módulo linear integrado às estruturas do RuFaS. Vamos mostrar o modelo e uma execução real, com dados demonstrativos claramente identificados. A alimentação envolve uma decisão recorrente: um ingrediente barato pode fornecer poucos nutrientes e exigir uma quantidade maior. Por isso, avaliamos a combinação completa, respeitando disponibilidade e limites nutricionais. O objetivo desta entrega é demonstrar uma decisão reproduzível e verificável. Anderson vai explicar como os dados chegam ao modelo.

**Cartão:** Problema → quantidades → custo mínimo → módulo linear → demonstração identificada.

## 01:45–03:00 — Slide 3 — modelo

**Sophia Lannah Beatriz Ferreira de Sousa — 75 segundos**

> Cada variável representa os quilos diários de um ingrediente em matéria natural. Multiplicamos essas quantidades pelos preços e minimizamos a soma. As restrições controlam matéria seca, proteína, energia, fibra, estoques e limites de inclusão. A composição é convertida para a mesma base de unidades. Os coeficientes permanecem fixos durante a otimização, tornando o problema linear. As proporções de fibra são reescritas sem divisão por variável. Por exemplo, o total de proteína é a soma da quantidade de cada alimento multiplicada por sua fração de matéria seca e seu teor proteico. Esse total precisa atingir a meta. Para o estoque, multiplicamos a quantidade diária pelo período e limitamos ao disponível. Não multiplicamos variáveis de decisão entre si. O perfil da vaca e suas metas ficam fixos durante essa resolução; não linearizamos todo o sistema nutricional NRC ou NASEM. Usamos a função linprog do SciPy com HiGHS para procurar o mínimo sujeito a essas condições. Depois, o programa confere a solução retornada. Agora vamos executar.

**Cartão:** x = kg MN/dia; p = R$/kg MN; min Σpx; MS/PB/NEL/FDN; estoque/inclusão; coeficientes fixos.

## 03:00–03:35 — Demonstração — entradas

**Sophia Lannah Beatriz Ferreira de Sousa — 35 segundos**

> Esta vaca tem 650 quilos, 100 dias em lactação e produz 30 quilos de leite por dia. Aqui estão alfafa, milho e soja, com seus preços e estoques. A matéria seca vem do calculador do RuFaS; preços e metas suplementares são ilustrativos. Vou executar o solver agora. Anderson, explique o resultado.

**Cartão:** 650 kg / DEL 100 / leite 30 → tabela de entradas → sintéticos identificados → ENTER → passar a Anderson.

## Perguntas

Priorize função objetivo, unidades, variáveis, restrições, linearidade e solver. Ambos devem estudar o roteiro completo e o banco de perguntas.
