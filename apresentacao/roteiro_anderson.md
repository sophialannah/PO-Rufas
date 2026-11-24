# Roteiro individual — Anderson Alberto da Costa Silva

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

O cronograma obrigatório prevalece sobre a sugestão inicial de 45–60 segundos para a demo: a demonstração tem **65 segundos**, divididos em 30 + 35. São **200 segundos de exposição + 100 segundos de perguntas = 300 segundos**.

Use um cronômetro visível. As durações são metas de ensaio, não uma medição das vozes dos integrantes. As falas são curtas para comportar respiração, troca de janela e execução. Não preencha o tempo restante com explicações extras. Ao chegar a 03:20, encerre a exposição; às 05:00, encerre as perguntas.

Sequência: slides 1 → 2 → 3 → Alt+Tab para o terminal → Enter para resolver → Alt+Tab de volta → slide 4. Não há quinto slide. O terminal deve estar preparado antes da contagem.

## 00:30–01:05 — Slide 2 — arquitetura

**Anderson Alberto da Costa Silva — 35 segundos**

> O programa recebe o perfil da vaca, a composição dos alimentos, os preços, estoques e metas nutricionais. Reutilizamos a biblioteca de alimentos e o calculador NRC do RuFaS para estimar o consumo de matéria seca. Os adaptadores convertem as unidades e entregam os dados ao otimizador. A saída contém a dieta e sua verificação. A aplicação automática ao ciclo diário da fazenda ainda não foi implementada.

**Cartão:** Animal + ingredientes + preços/estoques → adaptadores → SciPy/HiGHS → dieta. MS: RuFaS. Sem ciclo diário.

## 02:20–02:55 — Demonstração — resultado

**Anderson Alberto da Costa Silva — 35 segundos**

> O solver retornou status ótimo. A dieta contém aproximadamente 15,91 quilos de alfafa, 9,10 de milho e 0,18 de soja, em matéria natural por dia. O custo é aproximadamente 35 reais por dia. As onze verificações foram satisfeitas, incluindo nutrientes, estoques e inclusão. Esse é o mínimo para as opções e hipóteses informadas, não uma recomendação nutricional pronta.

**Cartão:** optimal → 15,91 / 9,10 / 0,18 kg MN → R$ 34,9978 → 11/11 OK → mínimo do cenário.

## 02:55–03:20 — Slide 4 — conclusão

**Anderson Alberto da Costa Silva — 25 segundos**

> Entregamos um núcleo executável, com conversões de unidades e verificação das restrições. A validação executou 433 testes dos componentes relacionados, todos aprovados. A contribuição é uma alternativa linear integrada aos dados do RuFaS. O próximo passo é substituir as hipóteses demonstrativas e ampliar a validação nutricional. Estamos disponíveis para perguntas.

**Cartão:** 433 testes → contribuição linear → parâmetros reais e validação completa → perguntas.

## Perguntas

Priorize arquitetura, dados, integração, resultados, testes e limitações. Ambos devem estudar o roteiro completo e o banco de perguntas.
