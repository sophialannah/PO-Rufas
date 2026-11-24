# Roteiro individual — Anderson Alberto da Costa Silva

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

São cinco minutos exclusivos de apresentação, seguidos de cinco minutos de arguição: a demonstração tem **85 segundos**, divididos em 35 + 50. São **300 segundos de exposição + 300 segundos adicionais de perguntas = 600 segundos**.

Use um cronômetro visível. As durações são metas de ensaio, não uma medição das vozes dos integrantes. Ensaie as falas com pausas para respiração, troca de janela e execução. Ajuste o ritmo sem omitir as limitações. Às 05:00, encerre a exposição; às 10:00, encerre as perguntas.

Sequência: slides 1 → 2 → 3 → Alt+Tab para o terminal → Enter para resolver → Alt+Tab de volta → slide 4. Não há quinto slide. O terminal deve estar preparado antes da contagem. Sophia: 155 s (2min35s); Anderson: 145 s (2min25s).

## 00:45–01:45 — Slide 2 — arquitetura

**Anderson Alberto da Costa Silva — 60 segundos**

> O programa recebe o perfil da vaca, a composição dos alimentos, os preços, estoques e metas nutricionais. Reutilizamos a biblioteca de alimentos e o calculador NRC do RuFaS para estimar o consumo de matéria seca. Os adaptadores convertem as unidades e entregam os dados ao otimizador. A saída contém a dieta e sua verificação. A aplicação automática ao ciclo diário da fazenda ainda não foi implementada. Essa separação permite conferir cada entrada antes de resolver: o perfil descreve o animal; a composição informa o que cada alimento fornece; preços e estoques definem o cenário econômico. O adaptador compatibiliza matéria natural e matéria seca, evitando misturar bases de cálculo. Neste exemplo, proteína, energia e limites de fibra são metas ilustrativas explícitas. Agora Sophia apresenta como esses dados se tornam variáveis e restrições.

**Cartão:** Animal + ingredientes + preços/estoques → adaptadores → SciPy/HiGHS → dieta. MS: RuFaS. Sem ciclo diário.

## 03:35–04:25 — Demonstração — resultado

**Anderson Alberto da Costa Silva — 50 segundos**

> O solver retornou status ótimo. A dieta contém aproximadamente 15,91 quilos de alfafa, 9,10 de milho e 0,18 de soja, em matéria natural por dia. O custo é aproximadamente 35 reais por dia. As onze verificações foram satisfeitas, incluindo nutrientes, estoques e inclusão. Conferimos também o custo multiplicando cada quantidade pelo respectivo preço. A solução fornece aproximadamente 22,55 quilos de matéria seca, 3,6 quilos de proteína bruta e 35 megacalorias de energia líquida. As onze verificações incluem cinco nutricionais e seis de estoque e inclusão. A tabela arredonda os números apenas para exibição. Esse é o mínimo para as opções e hipóteses informadas, não uma recomendação nutricional pronta.

**Cartão:** optimal → 15,91 / 9,10 / 0,18 kg MN → R$ 34,9978 → 11/11 OK → mínimo do cenário.

## 04:25–05:00 — Slide 4 — conclusão

**Anderson Alberto da Costa Silva — 35 segundos**

> Entregamos um núcleo executável, com conversões de unidades e verificação das restrições. A validação executou 433 testes dos componentes relacionados, todos aprovados. A contribuição é uma alternativa linear integrada aos dados do RuFaS. O próximo passo é substituir as hipóteses demonstrativas e ampliar a validação nutricional. Ainda precisamos incorporar o resultado ao ciclo diário da simulação e investigar cenários com dados econômicos documentados. Não demonstramos um percentual de economia em fazenda. Encerramos os cinco minutos de apresentação e iniciamos os cinco minutos de perguntas.

**Cartão:** 433 testes → contribuição linear → parâmetros reais e validação completa → perguntas.

## Perguntas

Priorize arquitetura, dados, integração, resultados, testes e limitações. Ambos devem estudar o roteiro completo e o banco de perguntas.
