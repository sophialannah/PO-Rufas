# Simulação de arguição — cinco minutos adicionais

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

Inicie um novo cronômetro ao terminar a apresentação: 00:00 aqui corresponde a 05:00 da atividade. Seis rodadas de 50 segundos somam 300 segundos; a atividade termina às 10:00. Os tempos incluem a pergunta, a resposta e a transição. São metas de ensaio, não uma gravação medida. Cada integrante conduz três rodadas; depois invertam os papéis para estudar todo o projeto.

## 00:00–00:50 — Sophia Lannah Beatriz Ferreira de Sousa

- Professor, 10 s: Qual é a função objetivo?
- Resposta, cerca de 35 s: Minimizar C = soma de preço por quantidade. O preço está em reais por kg de matéria natural e a quantidade em kg por dia; portanto, o resultado é reais por dia. No exemplo, somamos as parcelas de alfafa, milho e soja com precisão completa. O resultado é 34,9978 reais por dia. Esse mínimo depende dos preços, ingredientes e restrições informados; mudar o cenário pode mudar a solução.
- Pausa e troca de interlocutor, 5 s.

## 00:50–01:40 — Anderson Alberto da Costa Silva

- Professor, 10 s: Como foi feita a integração com o RuFaS?
- Resposta, cerca de 35 s: Usamos objetos Feed e NutritionRequirements, biblioteca de composição e calculador NRC existentes. Há um adaptador de Animal e saída em kg de MS compatível com rações. Ainda não aplicamos a dieta automaticamente à simulação diária. A contribuição está na ligação entre os dados existentes e um núcleo linear verificável. A conversão entre matéria natural e seca mantém as unidades consistentes. A baixa automática de estoque e o uso no ciclo diário ainda são trabalhos futuros.
- Pausa e troca de interlocutor, 5 s.

## 01:40–02:30 — Sophia Lannah Beatriz Ferreira de Sousa

- Professor, 10 s: Como funciona a linearização da FDN?
- Resposta, cerca de 35 s: Para matéria seca total positiva, FDN dividida pela MS maior que r equivale a FDN menos r vezes MS maior ou igual a zero. Como r é fixo, a restrição resultante é linear e equivalente. A mesma transformação vale para o limite superior, invertendo a desigualdade. Isso funciona porque a proporção exigida é constante e a matéria seca é positiva. Não significa linearizar todas as relações biológicas do animal.
- Pausa e troca de interlocutor, 5 s.

## 02:30–03:20 — Anderson Alberto da Costa Silva

- Professor, 10 s: Quais são as fontes das exigências nutricionais?
- Resposta, cerca de 35 s: Nesta demonstração, somente o consumo de MS é importado do calculador NRC do RuFaS. PB, NEL e limites de FDN são metas ilustrativas. Não afirmamos que todas as necessidades foram calculadas pelo NRC ou NASEM. A composição dos três ingredientes vem da biblioteca NRC utilizada pelo projeto. Preços, estoques e energia suplementar estão identificados como didáticos. Para uma aplicação prática, precisaríamos documentar esses parâmetros e ampliar a avaliação nutricional.
- Pausa e troca de interlocutor, 5 s.

## 03:20–04:10 — Sophia Lannah Beatriz Ferreira de Sousa

- Professor, 10 s: Como vocês validaram o programa?
- Resposta, cerca de 35 s: Executamos 433 testes dos componentes relacionados, incluindo 33 testes específicos do novo trabalho. Há casos com solução conhecida, conversões, limites, inviabilidade e integração. O exemplo também confere as onze restrições após o solver. Também recalculamos o custo fora do resultado retornado pelo solver. Essas verificações apoiam a correção computacional do cenário. Os 433 casos são dos componentes relacionados, não de toda a suíte, e não substituem validação em animais.
- Pausa e troca de interlocutor, 5 s.

## 04:10–05:00 — Anderson Alberto da Costa Silva

- Professor, 10 s: Essa dieta pode ser fornecida diretamente a uma vaca?
- Resposta, cerca de 35 s: A execução valida o modelo matemático demonstrativo. Ainda faltam parâmetros reais, restrições completas por ingrediente e reavaliação nutricional, inclusive proteína metabolizável, minerais e resposta produtiva. Não é uma recomendação pronta. Um ótimo matemático satisfaz o modelo fornecido; a qualidade da decisão depende também da qualidade desse modelo. Portanto, a evolução exige dados documentados e avaliação especializada, antes de transformar esta demonstração em uma recomendação para a fazenda.
- Pausa e troca de interlocutor, 5 s.
