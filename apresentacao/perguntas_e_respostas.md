# Banco de 27 perguntas — arguição separada de cinco minutos

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

As perguntas ocupam 05:00–10:00, após a apresentação. Ambos devem dominar todas as respostas. Respostas iniciais de 15–35 segundos; o professor pode aprofundar qualquer tópico. Não é necessário responder às 27 perguntas em uma sessão.

Base verificável: [resultados e fontes](resultados_validados.md), [solver](../RUFAS/biophysical/animal/ration/linear_diet.py), [adaptador](../RUFAS/biophysical/animal/ration/linear_diet_adapter.py), [exemplo](../RUFAS/biophysical/animal/ration/linear_diet_example.py) e [validação](evidencias/testes.md). Veja a [simulação oral](simulacao_arguicao.md).

## Básicas

### 1. O que é Pesquisa Operacional?

**Resposta sugerida: Sophia**

É o uso de modelos matemáticos para apoiar decisões sob restrições. Aqui, decidimos as quantidades dos alimentos que minimizam o custo de uma dieta dentro de limites definidos.

### 2. O que é programação linear?

**Resposta sugerida: Sophia**

É otimização com função objetivo e restrições lineares nas variáveis. Neste modelo, cada quantidade aparece multiplicada apenas por coeficientes fixos; não multiplicamos quantidades desconhecidas entre si.

### 3. Qual é a função objetivo?

**Resposta sugerida: Sophia**

Minimizar C = soma de preço por quantidade. O preço está em reais por kg de matéria natural e a quantidade em kg por dia; portanto, o resultado é reais por dia.

### 4. O que são variáveis de decisão?

**Resposta sugerida: Sophia**

São as quantidades diárias de cada ingrediente, em kg de matéria natural. O solver escolhe essas quantidades; pesos, preços, composição e metas são dados fixos durante a execução.

### 5. Quais são as restrições?

**Resposta sugerida: Sophia**

Matéria seca dentro do intervalo definido, mínimos de PB e NEL, proporção de FDN, estoque por período e inclusão mínima/máxima. O núcleo também aceita mínimos minerais opcionais; eles não estão ativados nesta demonstração.

### 9. O que é um solver?

**Resposta sugerida: Sophia**

É o software que recebe a função objetivo e as restrições e procura uma solução ótima ou informa uma falha, como inviabilidade. Nosso código monta o problema e confere o resultado retornado.

## Intermediárias

### 6. Por que o problema precisa ser linear?

**Resposta sugerida: Sophia**

Porque escolhemos resolvê-lo como programação linear com linprog. A linearidade permite otimizar esse modelo com coeficientes fixos. A nutrição real tem relações não lineares que essa simplificação não representa completamente.

### 7. Como funciona a linearização da FDN?

**Resposta sugerida: Sophia**

Para matéria seca total positiva, FDN dividida pela MS maior que r equivale a FDN menos r vezes MS maior ou igual a zero. Como r é fixo, a restrição resultante é linear e equivalente.

### 10. Qual solver e algoritmo foram utilizados?

**Resposta sugerida: Sophia**

Usamos scipy.optimize.linprog com method igual a highs. HiGHS resolve o LP; nessa opção a escolha entre os métodos internos é automática. Não fixamos no código simplex ou pontos interiores especificamente.

### 13. O que acontece se não houver solução viável?

**Resposta sugerida: Sophia**

O módulo retorna infeasible e uma mensagem, sem expor uma dieta nem custo como se fossem ótimos. Também distingue falha do solver e reprovação da solução na conferência numérica.

### 14. Como é calculado o custo mínimo?

**Resposta sugerida: Sophia**

O LP minimiza a soma dos preços vezes as quantidades dentro da região viável. Depois recalculamos a soma na demonstração. O mínimo vale somente para os ingredientes, preços, estoques e restrições fornecidos.

### 17. Matéria natural e matéria seca são a mesma coisa?

**Resposta sugerida: Sophia**

Não. Matéria natural inclui água. Multiplicamos kg de matéria natural pela fração de matéria seca. A composição em base seca precisa dessa conversão antes de entrar nas restrições.

### 23. Como o estoque de sete dias entra no modelo?

**Resposta sugerida: Sophia**

Cada variável é uma quantidade diária constante. Multiplicamos essa quantidade por sete e limitamos pelo estoque disponível para o animal. O custo retornado permanece diário, não semanal.

## Avançadas

### 8. Vocês linearizaram as equações NRC/NASEM?

**Resposta sugerida: Sophia**

Não. O consumo de MS é calculado antes do LP para um perfil fixo, usando o calculador NRC do RuFaS. Não transformamos as interações nutricionais completas em uma suposta equação linear.

### 11. Como foi feita a integração com o RuFaS?

**Resposta sugerida: Anderson**

Construímos o Animal 98605 real a partir de animal_population.json, calculamos exigências NRC, convertemos NRCFeed em Ingredient, otimizamos no HiGHS, convertemos a dieta para % de MS e a enviamos ao RationManager, conferindo a oferta via NutritionSupplyCalculator e NutritionEvaluator. Ainda não aplicamos a dieta automaticamente ao ciclo diário da fazenda.

### 15. Como vocês validaram o programa?

**Resposta sugerida: Anderson**

Executamos 442 testes dos componentes relacionados, incluindo 42 testes específicos do novo trabalho. Há casos com solução conhecida, conversões, limites, inviabilidade e integração ponta a ponta sem mocks com Animal, NRCFeed, RationManager e NutritionSupplyCalculator. O exemplo também confere as onze restrições após o solver.

### 16. Qual é a principal contribuição?

**Resposta sugerida: Anderson**

Uma alternativa linear modular, reproduzível e verificável dentro do RuFaS, com unidades explícitas, estoques e rastreabilidade. O RuFaS já possuía um otimizador não linear; não estamos apresentando o primeiro otimizador do sistema.

### 22. Por que o resultado tem aproximadamente 35 reais, se a tabela soma outro valor arredondado?

**Resposta sugerida: Sophia**

O cálculo utiliza valores completos, sem arredondar a decisão. As tabelas arredondam apenas para exibição. O custo interno é 35,1059017708 reais por dia; pequenas diferenças na soma visual vêm do arredondamento.

### 25. Como vocês tratam a tolerância numérica?

**Resposta sugerida: Sophia**

Após resolver, cada restrição é recalculada. A tolerância absoluta padrão é dez elevado a menos sete na unidade da linha. Valores arredondados do terminal não substituem essa verificação com precisão completa.

### 26. Existe análise de sensibilidade?

**Resposta sugerida: Anderson**

A API permite repetir cenários alterando parâmetros. Não entregamos uma análise formal de sensibilidade ou de preços-sombra. Isso e a comparação econômica controlada são próximos passos.

## Críticas sobre limitações

### 12. Quais são as fontes das exigências nutricionais?

**Resposta sugerida: Anderson**

Nesta demonstração, somente o consumo de MS é importado do calculador NRC do RuFaS. PB, NEL e limites de FDN são metas ilustrativas. Não afirmamos que todas as necessidades foram calculadas pelo NRC ou NASEM.

### 18. A proteína bruta equivale à metabolizável? E DE equivale à NEL?

**Resposta sugerida: Anderson**

Não. PB e proteína metabolizável representam grandezas diferentes; energia digestível e NEL também. Por isso o adaptador exige parâmetros suplementares explícitos e não faz essas conversões automaticamente.

### 19. Vocês escolheram os três ingredientes ou o solver?

**Resposta sugerida: Anderson**

Nesta demonstração curta, nós disponibilizamos três ingredientes e o solver escolhe as quantidades. Existe também uma busca no catálogo que avalia 300 registros e oferece 185 candidatos com composição utilizável ao LP.

### 20. Por que não usar os 300 alimentos diretamente?

**Resposta sugerida: Anderson**

O catálogo de nomes não garante composição disponível. O cruzamento atual exclui 110 registros sem composição e cinco por MS zero ou categoria fora do cenário. Os motivos são registrados; dados ausentes não viram zero.

### 21. Houve economia em relação à dieta anterior?

**Resposta sugerida: Anderson**

Não fizemos uma comparação controlada com dieta de referência válida. Portanto, não apresentamos percentual de economia. Também não comparamos os custos dos exemplos como economia, pois seus preços e hipóteses diferem.

### 24. Essa dieta pode ser fornecida diretamente a uma vaca?

**Resposta sugerida: Anderson**

A execução valida o modelo matemático demonstrativo. Ainda faltam parâmetros reais, restrições completas por ingrediente e reavaliação nutricional, inclusive proteína metabolizável, minerais e resposta produtiva. Não é uma recomendação pronta.

### 27. Vocês já executaram a fazenda completa?

**Resposta sugerida: Anderson**

A evidência desta entrega cobre a execução do LP, adaptadores e testes dos componentes relacionados. Não é uma execução completa da fazenda, nem prova de integração automática ao ciclo diário.


## Integração comprovada nesta versão

Integração comprovada: Animal 98605 construído de animal_population.json → cálculo NRC → lista NRCFeed/Ingredient → HiGHS → percentuais MS → RationManager → FeedInRation → NutritionSupplyCalculator e NutritionEvaluator. DEL 100, leite 30 kg/dia assumido. DMI calculada; PB/NEL/FDN externas; déficit diagnóstico de P absorvível (-6,68 g/dia) sem suplemento mineral no LP. O ciclo diário da fazenda não foi executado. Demo: demonstracao_integrada.bat. 5 minutos de apresentação + 5 minutos adicionais de perguntas.

Resultado: R$ 35,1059/dia. Relatório: [integração real](../docs/integracao_real_rufas.md).
