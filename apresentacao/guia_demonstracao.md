# Demonstração por terminal

Execute na raiz com o Python da venv:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m RUFAS.biophysical.animal.ration.linear_diet_example
.\.venv\Scripts\python.exe -X utf8 -m experiments.comparison --repeats 5 --output output/comparacao_demo
.\.venv\Scripts\python.exe -X utf8 -m experiments.annual --days 1 --strategy linear_highs_exclusive --output output/demo_exclusiva_1
```

O primeiro comando é o LP estático. O segundo executa A/B. O terceiro executa um dia real FULL_FARM, sem fallback SLSQP. Identifique a duração; para o ano, use --days 365 e outra pasta nova.

A evidência oficial anual contém 2.316,45106770 UM, 1.002 formulações HiGHS e zero chamadas SLSQP. Não substitua esse resultado por uma execução curta. Mostre o summary e o diário efetivos.

Os BATs demonstracao_integrada e demonstracao_solver permanecem como referências estáticas; não executam sozinhos o ano dinâmico. [Guia web](guia_demonstracao_web.md) · [Resultados e limites](resultados_validados.md).
