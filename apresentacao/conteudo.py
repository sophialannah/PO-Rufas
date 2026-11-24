"""Shared, reviewable presentation text used by the deck and rehearsal guides."""

SOPHIA = "Sophia Lannah Beatriz Ferreira de Sousa"
ANDERSON = "Anderson Alberto da Costa Silva"

STAGES = [
    (
        "Slide 1 — projeto",
        SOPHIA,
        45,
        "Nosso projeto aplica Pesquisa Operacional à formulação de dietas para bovinos leiteiros. "
        "Buscamos as quantidades de ingredientes que atendem às restrições com o menor custo diário. "
        "Desenvolvemos um módulo linear integrado às estruturas do RuFaS. Vamos mostrar o modelo e uma execução real, "
        "com dados demonstrativos claramente identificados. A alimentação envolve uma decisão recorrente: "
        "um ingrediente barato pode fornecer poucos nutrientes e exigir uma quantidade maior. Por isso, "
        "avaliamos a combinação completa, respeitando disponibilidade e limites nutricionais. "
        "O objetivo desta entrega é demonstrar uma decisão reproduzível e verificável. Anderson vai explicar "
        "como os dados chegam ao modelo.",
    ),
    (
        "Slide 2 — arquitetura",
        ANDERSON,
        60,
        "O programa recebe o animal real construído da população do RuFaS, a lista Python de ingredientes, "
        "os preços, estoques e metas nutricionais. Reutilizamos o calculador NRC do RuFaS para estimar o consumo "
        "de matéria seca e os objetos NRCFeed para a composição. Os adaptadores convertem as unidades e entregam "
        "os dados ao otimizador. A saída é convertida em percentuais de matéria seca e recebida pelo RationManager, "
        "que devolve os quilos por alimento conferidos pelo NutritionSupplyCalculator. "
        "A aplicação automática ao ciclo diário da fazenda ainda não foi implementada. "
        "Neste exemplo, proteína bruta, energia líquida e limites de fibra são metas ilustrativas explícitas. "
        "Agora Sophia apresenta como esses dados se tornam variáveis e restrições.",
    ),
    (
        "Slide 3 — modelo",
        SOPHIA,
        75,
        "Cada variável representa os quilos diários de um ingrediente em matéria natural. "
        "Multiplicamos essas quantidades pelos preços e minimizamos a soma. "
        "As restrições controlam matéria seca, proteína, energia, fibra, estoques e limites de inclusão. "
        "A composição é convertida para a mesma base de unidades. "
        "Os coeficientes permanecem fixos durante a otimização, tornando o problema linear. "
        "As proporções de fibra são reescritas sem divisão por variável. "
        "Por exemplo, o total de proteína é a soma da quantidade de cada alimento multiplicada "
        "por sua fração de matéria seca e seu teor proteico. Esse total precisa atingir a meta. "
        "Para o estoque, multiplicamos a quantidade diária pelo período e limitamos ao disponível. "
        "Não multiplicamos variáveis de decisão entre si. O perfil da vaca e suas metas ficam fixos "
        "durante essa resolução; não linearizamos todo o sistema nutricional NRC ou NASEM. "
        "Usamos a função linprog do SciPy com HiGHS para procurar o mínimo sujeito a essas condições. "
        "Depois, o programa confere a solução retornada. Agora vamos executar.",
    ),
    (
        "Demonstração — entradas",
        SOPHIA,
        35,
        "Esta é a vaca 98605 da população do RuFaS, com 627,56 quilos, 100 dias em lactação e 30 quilos "
        "de leite assumidos por dia. Aqui estão alfafa, milho e soja em NRCFeed, com seus preços e estoques. "
        "A matéria seca vem do calculador do RuFaS; preços e metas suplementares são ilustrativos. "
        "Vou executar o solver e enviar a dieta ao RationManager. Anderson, explique o resultado.",
    ),
    (
        "Demonstração — resultado",
        ANDERSON,
        50,
        "O solver retornou status ótimo. A dieta contém aproximadamente 14,83 quilos de alfafa, "
        "9,53 de milho e 0,50 de soja, em matéria natural por dia. "
        "O custo é aproximadamente 35,11 reais por dia, com onze verificações satisfeitas. "
        "A solução fornece 22,23 quilos de matéria seca, 3,6 quilos de proteína bruta, 35 megacalorias "
        "e 6,41 quilos de FDN. Convertemos os quilos de matéria seca para percentuais somando 100%, "
        "o RationManager recebeu e devolveu as quantidades exatas, e o NutritionSupplyCalculator conferiu "
        "PB e FDN. Esse é o mínimo do cenário demonstrativo, não uma recomendação nutricional pronta.",
    ),
    (
        "Slide 4 — conclusão",
        ANDERSON,
        35,
        "Entregamos um núcleo linear integrado de ponta a ponta ao Animal, NRCFeed, RationManager e "
        "calculadores de oferta do RuFaS. A validação executou 442 testes dos componentes relacionados, todos aprovados. "
        "A contribuição é uma alternativa linear reproduzível dentro das interfaces nativas do sistema. "
        "O próximo passo é substituir as hipóteses demonstrativas, completar minerais e incorporar a dieta "
        "ao ciclo diário da fazenda. Encerramos os cinco minutos de apresentação e iniciamos os cinco minutos "
        "de perguntas.",
    ),
]

CARDS = [
    "Problema → quantidades → custo mínimo → módulo linear → demonstração identificada.",
    "Animal → NRC → NRCFeed → HiGHS → % MS → RationManager → oferta conferida. Sem ciclo diário.",
    "x = kg MN/dia; p = R$/kg MN; min Σpx; MS/PB/NEL/FDN; estoque/inclusão; coeficientes fixos.",
    "Animal 98605 / 627,56 kg / DEL 100 / leite 30 → NRCFeed → ENTER → passar a Anderson.",
    "optimal → 14,83 / 9,53 / 0,50 kg MN → R$ 35,1059 → 11/11 OK → RationManager 100% MS.",
    "442 testes → integração real até RationManager → dados reais e ciclo diário futuros → perguntas.",
]

QA = [
    (
        "O que é Pesquisa Operacional?",
        "Sophia",
        "É o uso de modelos matemáticos para apoiar decisões sob restrições. Aqui, decidimos as "
        "quantidades dos alimentos que minimizam o custo de uma dieta dentro de limites definidos.",
    ),
    (
        "O que é programação linear?",
        "Sophia",
        "É otimização com função objetivo e restrições lineares nas variáveis. Neste modelo, cada "
        "quantidade aparece multiplicada apenas por coeficientes fixos; não multiplicamos quantidades "
        "desconhecidas entre si.",
    ),
    (
        "Qual é a função objetivo?",
        "Sophia",
        "Minimizar C = soma de preço por quantidade. O preço está em reais por kg de matéria natural e a"
        " quantidade em kg por dia; portanto, o resultado é reais por dia.",
    ),
    (
        "O que são variáveis de decisão?",
        "Sophia",
        "São as quantidades diárias de cada ingrediente, em kg de matéria natural. O solver escolhe "
        "essas quantidades; pesos, preços, composição e metas são dados fixos durante a execução.",
    ),
    (
        "Quais são as restrições?",
        "Sophia",
        "Matéria seca dentro do intervalo definido, mínimos de PB e NEL, proporção de FDN, estoque por "
        "período e inclusão mínima/máxima. O núcleo também aceita mínimos minerais opcionais; eles não "
        "estão ativados nesta demonstração.",
    ),
    (
        "Por que o problema precisa ser linear?",
        "Sophia",
        "Porque escolhemos resolvê-lo como programação linear com linprog. A linearidade permite "
        "otimizar esse modelo com coeficientes fixos. A nutrição real tem relações não lineares que essa"
        " simplificação não representa completamente.",
    ),
    (
        "Como funciona a linearização da FDN?",
        "Sophia",
        "Para matéria seca total positiva, FDN dividida pela MS maior que r equivale a FDN menos r vezes"
        " MS maior ou igual a zero. Como r é fixo, a restrição resultante é linear e equivalente.",
    ),
    (
        "Vocês linearizaram as equações NRC/NASEM?",
        "Sophia",
        "Não. O consumo de MS é calculado antes do LP para um perfil fixo, usando o calculador NRC do "
        "RuFaS. Não transformamos as interações nutricionais completas em uma suposta equação linear.",
    ),
    (
        "O que é um solver?",
        "Sophia",
        "É o software que recebe a função objetivo e as restrições e procura uma solução ótima ou "
        "informa uma falha, como inviabilidade. Nosso código monta o problema e confere o resultado "
        "retornado.",
    ),
    (
        "Qual solver e algoritmo foram utilizados?",
        "Sophia",
        "Usamos scipy.optimize.linprog com method igual a highs. HiGHS resolve o LP; nessa opção a "
        "escolha entre os métodos internos é automática. Não fixamos no código simplex ou pontos "
        "interiores especificamente.",
    ),
    (
        "Como foi feita a integração com o RuFaS?",
        "Anderson",
        "Construímos um Animal real a partir de animal_population.json, calculamos suas exigências NRC, "
        "convertemos objetos NRCFeed em Ingredient, otimizamos no HiGHS, convertemos a dieta para "
        "percentuais de MS e a enviamos ao RationManager, conferindo a oferta no NutritionSupplyCalculator e "
        "NutritionEvaluator. Ainda não aplicamos a dieta automaticamente ao ciclo diário da fazenda.",
    ),
    (
        "Quais são as fontes das exigências nutricionais?",
        "Anderson",
        "Nesta demonstração, somente o consumo de MS é importado do calculador NRC do RuFaS. PB, NEL e "
        "limites de FDN são metas ilustrativas. Não afirmamos que todas as necessidades foram calculadas"
        " pelo NRC ou NASEM.",
    ),
    (
        "O que acontece se não houver solução viável?",
        "Sophia",
        "O módulo retorna infeasible e uma mensagem, sem expor uma dieta nem custo como se fossem "
        "ótimos, e nada é enviado ao RationManager. Também distingue falha do solver e reprovação "
        "na conferência numérica.",
    ),
    (
        "Como é calculado o custo mínimo?",
        "Sophia",
        "O LP minimiza a soma dos preços vezes as quantidades dentro da região viável. Depois "
        "recalculamos a soma na demonstração. O mínimo vale somente para os ingredientes, preços, "
        "estoques e restrições fornecidos.",
    ),
    (
        "Como vocês validaram o programa?",
        "Anderson",
        "Executamos 442 testes dos componentes relacionados, incluindo 42 testes específicos do novo "
        "trabalho. Há casos com solução conhecida, conversões, limites, inviabilidade e integração ponta "
        "a ponta sem mocks com Animal, NRCFeed, RationManager e NutritionSupplyCalculator.",
    ),
    (
        "Qual é a principal contribuição?",
        "Anderson",
        "Uma alternativa linear modular, reproduzível e verificável dentro do RuFaS, com unidades "
        "explícitas, estoques e rastreabilidade. O RuFaS já possuía um otimizador não linear; não "
        "estamos apresentando o primeiro otimizador do sistema.",
    ),
    (
        "Matéria natural e matéria seca são a mesma coisa?",
        "Sophia",
        "Não. Matéria natural inclui água. Multiplicamos kg de matéria natural pela fração de matéria "
        "seca. A composição em base seca precisa dessa conversão antes de entrar nas restrições.",
    ),
    (
        "A proteína bruta equivale à metabolizável? E DE equivale à NEL?",
        "Anderson",
        "Não. PB e proteína metabolizável representam grandezas diferentes; energia digestível e NEL "
        "também. Por isso o adaptador exige parâmetros suplementares explícitos e não faz essas "
        "conversões automaticamente.",
    ),
    (
        "Vocês escolheram os três ingredientes ou o solver?",
        "Anderson",
        "Nesta demonstração curta, nós disponibilizamos três ingredientes e o solver escolhe as "
        "quantidades. Existe também uma busca no catálogo que avalia 300 registros e oferece 185 "
        "candidatos com composição utilizável ao LP.",
    ),
    (
        "Por que não usar os 300 alimentos diretamente?",
        "Anderson",
        "O catálogo de nomes não garante composição disponível. O cruzamento atual exclui 110 registros "
        "sem composição e cinco por MS zero ou categoria fora do cenário. Os motivos são registrados; "
        "dados ausentes não viram zero.",
    ),
    (
        "Houve economia em relação à dieta anterior?",
        "Anderson",
        "Não fizemos uma comparação controlada com dieta de referência válida. Portanto, não "
        "apresentamos percentual de economia. Também não comparamos os custos dos exemplos como "
        "economia, pois seus preços e hipóteses diferem.",
    ),
    (
        "Por que o resultado tem aproximadamente 35 reais, se a tabela soma outro valor arredondado?",
        "Sophia",
        "O cálculo utiliza valores completos, sem arredondar a decisão. As tabelas arredondam apenas "
        "para exibição. O custo interno é 35,1059017708 reais por dia; pequenas diferenças na soma "
        "visual vêm do arredondamento.",
    ),
    (
        "Como o estoque de sete dias entra no modelo?",
        "Sophia",
        "Cada variável é uma quantidade diária constante. Multiplicamos essa quantidade por sete e "
        "limitamos pelo estoque disponível para o animal. O custo retornado permanece diário, não "
        "semanal.",
    ),
    (
        "Essa dieta pode ser fornecida diretamente a uma vaca?",
        "Anderson",
        "A execução valida o modelo matemático demonstrativo. Ainda faltam parâmetros reais, restrições "
        "completas por ingrediente e reavaliação nutricional, inclusive proteína metabolizável, minerais"
        " e resposta produtiva. Não é uma recomendação pronta.",
    ),
    (
        "Como vocês tratam a tolerância numérica?",
        "Sophia",
        "Após resolver, cada restrição é recalculada. A tolerância absoluta padrão é dez elevado a menos"
        " sete na unidade da linha. Valores arredondados do terminal não substituem essa verificação com"
        " precisão completa.",
    ),
    (
        "Existe análise de sensibilidade?",
        "Anderson",
        "A API permite repetir cenários alterando parâmetros. Não entregamos uma análise formal de "
        "sensibilidade ou de preços-sombra. Isso e a comparação econômica controlada são próximos "
        "passos.",
    ),
    (
        "Vocês já executaram a fazenda completa?",
        "Anderson",
        "A evidência desta entrega cobre a execução do LP, adaptadores e testes dos componentes "
        "relacionados. Não é uma execução completa da fazenda, nem prova de integração automática ao "
        "ciclo diário.",
    ),
]
