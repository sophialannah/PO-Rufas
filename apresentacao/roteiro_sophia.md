# Roteiro individual — Sophia Lannah Beatriz Ferreira de Sousa

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

O cronograma obrigatório prevalece sobre a sugestão inicial de 45–60 segundos para a demo: a demonstração tem **65 segundos**, divididos em 30 + 35. São **200 segundos de exposição + 100 segundos de perguntas = 300 segundos**.

Use um cronômetro visível. As durações são metas de ensaio, não uma medição das vozes dos integrantes. As falas são curtas para comportar respiração, troca de janela e execução. Não preencha o tempo restante com explicações extras. Ao chegar a 03:20, encerre a exposição; às 05:00, encerre as perguntas.

Sequência: slides 1 → 2 → 3 → Alt+Tab para o terminal → Enter para resolver → Alt+Tab de volta → slide 4. Não há quinto slide. O terminal deve estar preparado antes da contagem.

## 00:00–00:30 — Slide 1 — projeto

**Sophia Lannah Beatriz Ferreira de Sousa — 30 segundos**

> Nosso projeto aplica Pesquisa Operacional à formulação de dietas para bovinos leiteiros. Buscamos as quantidades de ingredientes que atendem às restrições com o menor custo diário. Desenvolvemos um módulo linear integrado às estruturas do RuFaS. Vamos mostrar o modelo e uma execução real, com dados demonstrativos claramente identificados.

**Cartão:** Problema → quantidades → custo mínimo → módulo linear → demonstração identificada.

## 01:05–01:50 — Slide 3 — modelo

**Sophia Lannah Beatriz Ferreira de Sousa — 45 segundos**

> Cada variável representa os quilos diários de um ingrediente em matéria natural. Multiplicamos essas quantidades pelos preços e minimizamos a soma. As restrições controlam matéria seca, proteína, energia, fibra, estoques e limites de inclusão. A composição é convertida para a mesma base de unidades. Os coeficientes permanecem fixos durante a otimização, tornando o problema linear. As proporções de fibra são reescritas sem divisão por variável. Usamos a função linprog do SciPy com HiGHS. Agora vamos executar.

**Cartão:** x = kg MN/dia; p = R$/kg MN; min Σpx; MS/PB/NEL/FDN; estoque/inclusão; coeficientes fixos.

## 01:50–02:20 — Demonstração — entradas

**Sophia Lannah Beatriz Ferreira de Sousa — 30 segundos**

> Esta vaca tem 650 quilos, 100 dias em lactação e produz 30 quilos de leite por dia. Aqui estão alfafa, milho e soja, com seus preços e estoques. A matéria seca vem do calculador do RuFaS; preços e metas suplementares são ilustrativos. Vou executar o solver agora. Anderson, explique o resultado.

**Cartão:** 650 kg / DEL 100 / leite 30 → tabela de entradas → sintéticos identificados → ENTER → passar a Anderson.

## Perguntas

Priorize função objetivo, unidades, variáveis, restrições, linearidade e solver. Ambos devem estudar o roteiro completo e o banco de perguntas.
