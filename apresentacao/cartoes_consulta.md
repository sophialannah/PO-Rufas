# Cartões de consulta

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

**Slide 1 — projeto — 45s — Sophia**

Problema → quantidades → custo mínimo → módulo linear → demonstração identificada.

**Slide 2 — arquitetura — 60s — Anderson**

Animal + ingredientes + preços/estoques → adaptadores → SciPy/HiGHS → dieta. MS: RuFaS. Sem ciclo diário.

**Slide 3 — modelo — 75s — Sophia**

x = kg MN/dia; p = R$/kg MN; min Σpx; MS/PB/NEL/FDN; estoque/inclusão; coeficientes fixos.

**Demonstração — entradas — 35s — Sophia**

627,56 kg / DEL 100 / leite 30 → tabela de entradas → sintéticos identificados → ENTER → passar a Anderson.

**Demonstração — resultado — 50s — Anderson**

optimal → 14,83 / 9,53 / 0,50 kg MN → R$ 35,1059 → 11/11 OK → mínimo do cenário.

**Slide 4 — conclusão — 35s — Anderson**

442 testes → contribuição linear → parâmetros reais e validação completa → perguntas.

**05:00: encerrar a apresentação e iniciar perguntas. 10:00: encerrar a arguição.**

Números-chave: 627,56 kg; DEL 100; leite 30 kg/dia; MS 22,2316; PB mínima 3,6; NEL mínima 35; FDN 28–40%; R$ 35,1059/dia; 11 verificações; 442 testes.


## Integração comprovada nesta versão

Integração comprovada: Animal 98605 construído de animal_population.json → cálculo NRC → lista NRCFeed/Ingredient → HiGHS → percentuais MS → RationManager → FeedInRation → NutritionSupplyCalculator e NutritionEvaluator. DEL 100, leite 30 kg/dia assumido. DMI calculada; PB/NEL/FDN externas; déficit diagnóstico de P absorvível (-6,68 g/dia) sem suplemento mineral no LP. O ciclo diário da fazenda não foi executado. Demo: demonstracao_integrada.bat. 5 minutos de apresentação + 5 minutos adicionais de perguntas.

Resultado: R$ 35,1059/dia. Relatório: [integração real](../docs/integracao_real_rufas.md).
