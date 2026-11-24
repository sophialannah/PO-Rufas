# Checklist de apresentação

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

## Validação técnica registrada

- [x] Solver executado novamente e custo reconferido.
- [x] 11/11 verificações satisfeitas na demonstração.
- [x] 442 testes relacionados aprovados, incluindo 42 específicos.
- [x] Dados ilustrativos identificados em slides, terminal e roteiro.
- [x] Quatro slides gerados, com nomes completos e notas de fala.
- [x] Cronograma de 300 segundos de apresentação + 300 segundos de arguição = 600 segundos.
- [x] BAT e modo automático preparados para o Windows.
- [x] Integração descrita como adaptador; sem alegação de ciclo diário completo.
- [x] Sem percentual de economia inventado e sem comparação de cenários incompatíveis.

## Antes de apresentar — verificar manualmente

- [ ] Abrir o PPTX no computador e projetor que serão usados; conferir fontes e proporção 16:9.
- [ ] Consultar `evidencias/verificacao_powerpoint.json` para conferir abertura e exportação automáticas.
- [ ] Ensaiar a dupla com cronômetro: slide 1 até 00:45; slide 2 até 01:45; slide 3 até 03:00.
- [ ] Ensaiar demo até 04:25, conclusão até 05:00, perguntas separadas até 10:00.
- [ ] Executar o BAT com `--auto` antes da aula; depois deixá-lo aguardando Enter nas entradas.
- [ ] Deixar somente PowerPoint e terminal necessários à apresentação; testar Alt+Tab.
- [ ] Usar fonte de terminal legível e largura suficiente para as tabelas.
- [ ] Fechar notificações e conectar o carregador.
- [ ] Guardar PPTX, PDF/prévias e cópia das evidências localmente para uso sem internet.
- [ ] Estudar os cartões e pelo menos as perguntas prioritárias.

Os itens manuais não foram marcados como concluídos: não houve ensaio oral da dupla nem teste do projetor.
Se ocorrer falha ao vivo, identificar a saída de contingência como execução anterior, nunca como execução ao vivo.


## Integração comprovada nesta versão

Integração comprovada: Animal 98605 construído de animal_population.json → cálculo NRC → lista NRCFeed/Ingredient → HiGHS → percentuais MS → RationManager → FeedInRation → NutritionSupplyCalculator e NutritionEvaluator. DEL 100, leite 30 kg/dia assumido. DMI calculada; PB/NEL/FDN externas; déficit diagnóstico de P absorvível (-6,68 g/dia) sem suplemento mineral no LP. O ciclo diário da fazenda não foi executado. Demo: demonstracao_integrada.bat. 5 minutos de apresentação + 5 minutos adicionais de perguntas.

Resultado: R$ 35,1059/dia. Relatório: [integração real](../docs/integracao_real_rufas.md).
