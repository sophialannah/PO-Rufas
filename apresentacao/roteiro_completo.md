# Roteiro completo — 5 minutos

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

| Intervalo | Etapa | Responsável | Duração |
|---|---|---|---:|
| 00:00–00:30 | Slide 1 — projeto | Sophia Lannah Beatriz Ferreira de Sousa | 30 s |
| 00:30–01:05 | Slide 2 — arquitetura | Anderson Alberto da Costa Silva | 35 s |
| 01:05–01:50 | Slide 3 — modelo | Sophia Lannah Beatriz Ferreira de Sousa | 45 s |
| 01:50–02:20 | Demonstração — entradas | Sophia Lannah Beatriz Ferreira de Sousa | 30 s |
| 02:20–02:55 | Demonstração — resultado | Anderson Alberto da Costa Silva | 35 s |
| 02:55–03:20 | Slide 4 — conclusão | Anderson Alberto da Costa Silva | 25 s |
| 03:20–05:00 | Perguntas | Ambos | 100 s |

O cronograma obrigatório prevalece sobre a sugestão inicial de 45–60 segundos para a demo: a demonstração tem **65 segundos**, divididos em 30 + 35. São **200 segundos de exposição + 100 segundos de perguntas = 300 segundos**.

Use um cronômetro visível. As durações são metas de ensaio, não uma medição das vozes dos integrantes. As falas são curtas para comportar respiração, troca de janela e execução. Não preencha o tempo restante com explicações extras. Ao chegar a 03:20, encerre a exposição; às 05:00, encerre as perguntas.

Sequência: slides 1 → 2 → 3 → Alt+Tab para o terminal → Enter para resolver → Alt+Tab de volta → slide 4. Não há quinto slide. O terminal deve estar preparado antes da contagem.

## 00:00–00:30 — Slide 1 — projeto

**Sophia Lannah Beatriz Ferreira de Sousa — 30 segundos**

> Nosso projeto aplica Pesquisa Operacional à formulação de dietas para bovinos leiteiros. Buscamos as quantidades de ingredientes que atendem às restrições com o menor custo diário. Desenvolvemos um módulo linear integrado às estruturas do RuFaS. Vamos mostrar o modelo e uma execução real, com dados demonstrativos claramente identificados.

**Cartão:** Problema → quantidades → custo mínimo → módulo linear → demonstração identificada.

## 00:30–01:05 — Slide 2 — arquitetura

**Anderson Alberto da Costa Silva — 35 segundos**

> O programa recebe o perfil da vaca, a composição dos alimentos, os preços, estoques e metas nutricionais. Reutilizamos a biblioteca de alimentos e o calculador NRC do RuFaS para estimar o consumo de matéria seca. Os adaptadores convertem as unidades e entregam os dados ao otimizador. A saída contém a dieta e sua verificação. A aplicação automática ao ciclo diário da fazenda ainda não foi implementada.

**Cartão:** Animal + ingredientes + preços/estoques → adaptadores → SciPy/HiGHS → dieta. MS: RuFaS. Sem ciclo diário.

## 01:05–01:50 — Slide 3 — modelo

**Sophia Lannah Beatriz Ferreira de Sousa — 45 segundos**

> Cada variável representa os quilos diários de um ingrediente em matéria natural. Multiplicamos essas quantidades pelos preços e minimizamos a soma. As restrições controlam matéria seca, proteína, energia, fibra, estoques e limites de inclusão. A composição é convertida para a mesma base de unidades. Os coeficientes permanecem fixos durante a otimização, tornando o problema linear. As proporções de fibra são reescritas sem divisão por variável. Usamos a função linprog do SciPy com HiGHS. Agora vamos executar.

**Cartão:** x = kg MN/dia; p = R$/kg MN; min Σpx; MS/PB/NEL/FDN; estoque/inclusão; coeficientes fixos.

## 01:50–02:20 — Demonstração — entradas

**Sophia Lannah Beatriz Ferreira de Sousa — 30 segundos**

> Esta vaca tem 650 quilos, 100 dias em lactação e produz 30 quilos de leite por dia. Aqui estão alfafa, milho e soja, com seus preços e estoques. A matéria seca vem do calculador do RuFaS; preços e metas suplementares são ilustrativos. Vou executar o solver agora. Anderson, explique o resultado.

**Cartão:** 650 kg / DEL 100 / leite 30 → tabela de entradas → sintéticos identificados → ENTER → passar a Anderson.

## 02:20–02:55 — Demonstração — resultado

**Anderson Alberto da Costa Silva — 35 segundos**

> O solver retornou status ótimo. A dieta contém aproximadamente 15,91 quilos de alfafa, 9,10 de milho e 0,18 de soja, em matéria natural por dia. O custo é aproximadamente 35 reais por dia. As onze verificações foram satisfeitas, incluindo nutrientes, estoques e inclusão. Esse é o mínimo para as opções e hipóteses informadas, não uma recomendação nutricional pronta.

**Cartão:** optimal → 15,91 / 9,10 / 0,18 kg MN → R$ 34,9978 → 11/11 OK → mínimo do cenário.

## 02:55–03:20 — Slide 4 — conclusão

**Anderson Alberto da Costa Silva — 25 segundos**

> Entregamos um núcleo executável, com conversões de unidades e verificação das restrições. A validação executou 433 testes dos componentes relacionados, todos aprovados. A contribuição é uma alternativa linear integrada aos dados do RuFaS. O próximo passo é substituir as hipóteses demonstrativas e ampliar a validação nutricional. Estamos disponíveis para perguntas.

**Cartão:** 433 testes → contribuição linear → parâmetros reais e validação completa → perguntas.

## 03:20–05:00 — perguntas

Sophia inicia respostas de modelagem; Anderson, de integração e validação. Cada resposta deve durar 10–20 segundos. O banco de perguntas serve para estudo; não se pretende responder todas as perguntas em 100 segundos.
