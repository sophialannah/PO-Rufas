

# Simulação dinâmica anual — evidências

A execução usa o motor FULL_FARM real do RuFaS, com campos, clima, armazenamento, compras, currais, alimentação, reprodução e evolução animal. O cenário tem início em 2013:1 e termina em 2013:365. A semente é 42, padrão NRC e reformulação diária. São unidades monetárias demonstrativas (UM); os preços originais baratos do cenário não são cotações de mercado.

## Execuções

Foram concluídos testes nativos de 1, 7, 30 e 365 dias e testes híbridos nas mesmas durações. Os registros de confirmação anual estão em confirmacao. As primeiras rodadas também foram preservadas. Os nomes dos diretórios distinguem os experimentos.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m experiments.annual --days 365 --strategy native_slsqp --output output/minha_execucao/nativa
.\.venv\Scripts\python.exe -X utf8 -m experiments.annual --days 365 --strategy linear_highs --output output/minha_execucao/hibrida
.\.venv\Scripts\python.exe -X utf8 -m experiments.annual_report --root evidencias/anual/confirmacao
```

Escolha diretórios novos. O runner se recusa a reutilizar uma pasta existente. As configurações de entrada copiadas, dados efetivos validados, estado inicial, diário JSONL, progresso e resumo ficam em cada execução. A interface também cria subdiretórios UUID e processos independentes.

## O que é simulado

A população é amostrada pelo HerdFactory original, com alvo de 10 vacas, 8 bezerros, 2 novilhas I, 2 novilhas II, 5 novilhas próximas ao parto e mercado de reposição de 5.000 animais. Os números efetivos podem diferir do alvo por arredondamento das frações e eventos do simulador. A configuração validada e o estado inicial são arquivados.

O cenário de exemplo original utiliza NASEM e alimentos 301/302 sem composição NRC. A cópia experimental muda para NRC, retira esses IDs e acrescenta os alimentos NRC 1, 167 e 231 com preços explícitos. As categorias adultas têm as listas adaptadas; bezerros mantêm 202/216. Os intervalos e o teto de tentativas são iguais nas duas estratégias. Nenhuma trajetória é pré-calculada.

O estado e o clima originais são usados, e o FeedManager recebe colheitas, planeja compras e efetua deduções. O observador registra os valores retornados pela dedução original, sem executar outra baixa de estoque. Custo estimado das dietas usa preço de referência por kg MS de cada alimento efetivamente fornecido, incluindo equivalência de reposição para forragens próprias. Despesa de compra é o acréscimo físico de estoque comprado multiplicado pelo preço. Essas duas grandezas permanecem distintas.

## Estratégias e contagens

native_slsqp chama o método original. linear_highs utiliza o módulo da dupla dentro da chamada de formulação do curral para vacas em lactação NRC. Constrói aproximações afins das 14 restrições nativas, resolve com optimize_diet/HiGHS e avalia a candidata nas funções não lineares e no NutritionEvaluator. O procedimento é sequencial e pode fazer até 20 LPs; o primeiro candidato que passa nas verificações é aceito. Esse critério busca uma dieta viável de custo minimizado na aproximação corrente, sem certificação de ótimo global do problema biológico.

A partida vem da rotina nativa. As derivadas são diferenças finitas com passo 1e-4 kg MS, raio local de 5 kg MS por ingrediente e margem de 1e-4 na unidade de cada restrição. As variáveis do LP permanecem em MN. PB/NEL mínimas demonstrativas não são transferidas ao ano; as restrições de MP e energia vêm das funções nativas atualizadas. Os campos individuais ausentes no portador do perfil não participam do cálculo.

Categorias sem suporte usam o SLSQP com motivo explícito. Falha do LP ou rejeição do candidato também pode acionar fallback nativo. A política fail permite interromper o caminho incompatível. Os logs mostram tentativas, LPs, requisitos, candidatas, resíduos e motivos. Bezerros seguem seu fluxo original de ração, sem reivindicação de formulação HiGHS.

## Resultado da primeira rodada completa

| Indicador | Nativa | Híbrida |
|---|---:|---:|
| Dias completos |365|365|
| Custo estimado consumido (UM) |2.319,219171|2.529,218830|
| Despesa de compra (UM) |2.323,081042|2.533,080737|
| Leite total (kg) |140.223,666523|140.223,666523|
| Animal-dias |9.173|9.173|
| UM por animal-dia |0,252831|0,275724|
| UM por kg leite |0,016539|0,018037|
| Tentativas HiGHS |0|365|
| Aceites HiGHS |0|352|
| Tentativas SLSQP |1.002|650|
| Uso nativo por categoria incompatível |0|637|
| Fallback após tentativa HiGHS |0|13|

A economia calculada como 100 × (custo nativo − híbrido)/custo nativo foi **−9,054757%**, portanto houve aumento de custo neste cenário. Os totais biológicos iguais foram observados, sem fixar trajetórias ou resultados. Houve 49 transições de categoria em cada trajetória registrada. O parecer depende do curral e do dia; consulte os deltas, sem inferir que todo o ano foi aprovado. A avaliação adulta não certifica os registros de bezerros.

## Auditoria e defeitos recuperados

A primeira tentativa NRC falhou pelos IDs 301/302. Foram preparados novos arquivos de cenário compatíveis. A execução anual expôs um erro existente em HerdManager: uma transição encaminhava o mapa de categorias à seleção de alimentos, em vez da lista da categoria. A correção usa get_ration_feeds(animal_combination). O teste que antes reproduzia essa chamada incorreta foi transformado em regressão da seleção correta.

A revisão original candidata é d471c742eadc2e37b76545d0d0f0d10b6c9ef763, a última revisão dev anterior ao primeiro commit local. Dos 981 caminhos compartilhados, 974 blobs coincidem com a importação inicial, inclusive todas as fontes RUFAS compartilhadas. A identidade exata da clonagem não é provada pela ancestralidade, perdida na importação inicial. Ausências incluem arquivos de licença, um helper e filtros de saída; nenhum deles precisou ser transplantado para executar o motor e os registros desta experiência. Consulte os JSON de auditoria. Não há submódulos declarados nem configuração Git LFS identificada.

## Arquivos e limites

- daily.jsonl contém um registro por dia, dietas, requisitos/ofertas, critérios, estados animais, consumo, estoque e proveniência dos formuladores.
- initial_state.json contém a fotografia inicial da confirmação.
- effective_inputs.json contém as entradas efetivas após validação.
- summary.json contém métricas anuais e contagens.
- CSV e gráficos são derivados dos diários pelo annual_report.
- Os JUnit e saídas registram os testes relevantes, incluindo os casos estáticos anteriores.
- As evidências de 1/7/30 dias ficam no relatório progressivo e nas saídas originais output/annual.

A comparação é experimental, com preços demonstrativos, rebanho pequeno e estratégia híbrida. Permanecem o refinamento da aproximação e de sua otimalidade, validação nutricional/biológica ampla e cenários econômicos de campo. O modo NASEM continua apenas diagnóstico no fluxo estático.



## Confirmação e testes finais

A rodada em confirmacao completou novamente 365 dias para cada estratégia, reproduzindo os totais econômicos e biológicos acima. As duas fotografias iniciais são iguais, com 26 animais. Os estados posteriores foram produzidos pelo simulador.

A suíte final retornou **937 passed in 123.52s**, com todos os 466 testes anteriores incluídos. O teste de navegação e lançamento anual cria dois processos reais de um dia. O teste de reprodutibilidade executa dois dias em processos distintos e confere estados, consumo, custos e chamada HiGHS. Após o ajuste de rótulo de progresso, os cinco casos anuais passaram novamente.

Nos registros adultos da confirmação, o nativo teve 344 currais-dia aprovados e 654 reprovados. O híbrido teve 517 e 481, respectivamente. Os dados completos devem ser usados para avaliar cada dia e nutriente. Não se conclui adequação do ano inteiro.

Pen atribui a oferta aos animais em set_animal_nutritional_supply e atualiza previous_nutrition_supply em suas rotinas. Os requisitos subsequentes consultam essa estrutura conforme o modelo original. O leite total igual observado não foi imposto pelo experimento.

As entradas iniciais eram validadas pelo esquema InputManager; alguns números abaixo dos mínimos foram substituídos por padrões nativos. Na confirmação, o gerador passou a informar diretamente esses mesmos valores efetivos (8 bezerros, 5 novilhas próximas ao parto, 5.000 reposições), evitando a correção silenciosa do cenário. Isso preservou a população e os resultados. effective_inputs.json registra o que realmente foi utilizado.

Não foram usados os filtros gráficos antigos do TaskManager para produzir as séries, pois os diários observados são suficientes. A execução usa o mesmo SimulationEngine e módulos do cenário FULL_FARM, sem executar trajetórias estáticas. As rotinas de validação cruzada específicas do task de exemplo não foram adicionadas ao runner; a validação dos arquivos utiliza o esquema nativo.
