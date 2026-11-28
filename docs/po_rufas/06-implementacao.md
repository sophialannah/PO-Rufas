# Implementação computacional
[Sumário](README.md)

Python, SciPy/HiGHS, NumPy e Pandas compõem o backend; Streamlit fornece a interface local. Python 3.12 foi validado; 3.13 está no intervalo declarado pelo projeto. As versões fixadas estão em constraints-po-rufas.txt.

## Responsabilidades

| Caminho | Papel |
|---|---|
| frontend/app.py, service.py, results.py | Sete áreas, entradas e resultados estáticos |
| frontend/annual.py | Cinco opções anuais, processos separados e relatórios reais |
| RUFAS/biophysical/animal/ration/linear_diet.py | LP estático, linhas adicionais e checks |
| linear_diet_adapter.py, linear_diet_integration.py | Unidades, requisitos, RationManager e avaliação |
| dynamic_linear_optimizer.py | Programação linear sequencial e despacho por instância |
| mineral_limits.py | Tetos totais NRC 2005 e diagnóstico mineral |
| HerdManager e Pen | Categorias, requisitos e aplicação da formulação |
| FeedManager | Compras, colheitas, baixa e inventário |
| experiments/comparison.py | Experimentos A/B e medições |
| experiments/annual.py | Runner FULL_FARM e diários |
| experiments/convergence_report.py | Relatório oficial da correção |
| experiments/calf_report.py | Auditoria de registros de bezerros, somente leitura |
| experiments/publication.py | Inventário/exportação isolada, sem staging ou commit |
| experiments/provenance.py | Proveniência também em fonte exportada sem .git |

## Configuração dinâmica

optimizer_strategy aceita native_slsqp, linear_highs_all e linear_highs_exclusive; linear_highs conserva a cobertura histórica de lactação pela CLI. optimizer_fallback define native_slsqp/fail, mas o exclusivo impõe fail. optimizer_mineral_policy=nrc2005_mtl ativa os tetos, mesmo com a flag de eventos desligada. O runner e as comparações da interface usam essa política.

A classe base RationOptimizer foi preservada. O padrão fora da configuração explícita continua nativo. O adaptador registra LPs, raios, limites locais/físicos, resíduos, avaliação, custo e motivo de encerramento.

## Isolamento e falhas

O fluxo estático serializa configurações temporárias com lock e restaura classes/RNG. O anual usa um subprocesso por estratégia, com UUID e pasta nova. RecordedSimulation observa as deduções/compras nativas, sem executar outra baixa. Falhas aparecem no summary e nos logs; o exclusivo não chama SLSQP silenciosamente.

A correção do FeedManager retira massa real de pequenos lotes numa segunda passagem antes de declarar falta. Preserva a primeira passagem e sua tolerância operacional. Não cria alimento.

## Proveniência de uma cópia publicada

Executar um arquivo-fonte exportado não deve exigir o diretório .git da máquina do autor. Sem Git, os relatórios marcam commit/dirty como indisponíveis, sem inventar uma revisão; PUBLICATION_MANIFEST.json registra a origem e os hashes do candidato. Isso é suporte à reprodução da fonte e não modifica o modelo nutricional.
