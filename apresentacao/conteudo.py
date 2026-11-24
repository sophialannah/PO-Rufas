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
        "O programa recebe o perfil da vaca, a composição dos alimentos, os preços, estoques e metas nutricionais. "
        "Reutilizamos a biblioteca de alimentos e o calculador NRC do RuFaS para estimar o consumo de matéria seca. "
        "Os adaptadores convertem as unidades e entregam os dados ao otimizador. A saída contém a dieta "
        "e sua verificação. "
        "A aplicação automática ao ciclo diário da fazenda ainda não foi implementada. "
        "Essa separação permite conferir cada entrada antes de resolver: o perfil descreve o animal; "
        "a composição informa o que cada alimento fornece; preços e estoques definem o cenário econômico. "
        "O adaptador compatibiliza matéria natural e matéria seca, evitando misturar bases de cálculo. "
        "Neste exemplo, proteína, energia e limites de fibra são metas ilustrativas explícitas. "
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
        "Esta vaca tem 650 quilos, 100 dias em lactação e produz 30 quilos de leite por dia. "
        "Aqui estão alfafa, milho e soja, com seus preços e estoques. "
        "A matéria seca vem do calculador do RuFaS; preços e metas suplementares são ilustrativos. "
        "Vou executar o solver agora. Anderson, explique o resultado.",
    ),
    (
        "Demonstração — resultado",
        ANDERSON,
        50,
        "O solver retornou status ótimo. A dieta contém aproximadamente 15,91 quilos de alfafa, "
        "9,10 de milho e 0,18 de soja, em matéria natural por dia. "
        "O custo é aproximadamente 35 reais por dia. "
        "As onze verificações foram satisfeitas, incluindo nutrientes, estoques e inclusão. "
        "Conferimos também o custo multiplicando cada quantidade pelo respectivo preço. "
        "A solução fornece aproximadamente 22,55 quilos de matéria seca, 3,6 quilos de proteína bruta "
        "e 35 megacalorias de energia líquida. As onze verificações incluem cinco nutricionais "
        "e seis de estoque e inclusão. A tabela arredonda os números apenas para exibição. "
        "Esse é o mínimo para as opções e hipóteses informadas, não uma recomendação nutricional pronta.",
    ),
    (
        "Slide 4 — conclusão",
        ANDERSON,
        35,
        "Entregamos um núcleo executável, com conversões de unidades e verificação das restrições. "
        "A validação executou 433 testes dos componentes relacionados, todos aprovados. "
        "A contribuição é uma alternativa linear integrada aos dados do RuFaS. "
        "O próximo passo é substituir as hipóteses demonstrativas e ampliar a validação nutricional. "
        "Ainda precisamos incorporar o resultado ao ciclo diário da simulação e investigar cenários "
        "com dados econômicos documentados. Não demonstramos um percentual de economia em fazenda. "
        "Encerramos os cinco minutos de apresentação e iniciamos os cinco minutos de perguntas.",
    ),
]

CARDS = [
    "Problema → quantidades → custo mínimo → módulo linear → demonstração identificada.",
    "Animal + ingredientes + preços/estoques → adaptadores → SciPy/HiGHS → dieta. MS: RuFaS. Sem ciclo diário.",
    "x = kg MN/dia; p = R$/kg MN; min Σpx; MS/PB/NEL/FDN; estoque/inclusão; coeficientes fixos.",
    "650 kg / DEL 100 / leite 30 → tabela de entradas → sintéticos identificados → ENTER → passar a Anderson.",
    "optimal → 15,91 / 9,10 / 0,18 kg MN → R$ 34,9978 → 11/11 OK → mínimo do cenário.",
    "433 testes → contribuição linear → parâmetros reais e validação completa → perguntas.",
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
        "Usamos objetos Feed e NutritionRequirements, biblioteca de composição e calculador NRC "
        "existentes. Há um adaptador de Animal e saída em kg de MS compatível com rações. Ainda não "
        "aplicamos a dieta automaticamente à simulação diária.",
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
        "ótimos. Também distingue falha do solver e reprovação da solução na conferência numérica.",
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
        "Executamos 433 testes dos componentes relacionados, incluindo 33 testes específicos do novo "
        "trabalho. Há casos com solução conhecida, conversões, limites, inviabilidade e integração. O "
        "exemplo também confere as onze restrições após o solver.",
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
        "para exibição. O custo interno é 34,9977736422 reais por dia; pequenas diferenças na soma "
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
