# Testes e validação
[Sumário](README.md)

A suíte relevante de referência tem **969 testes aprovados**, preservando os 954 anteriores e acrescentando 15 regressões de usabilidade. Isso não significa execução de todos os testes existentes no RuFaS ou validação clínica de dietas.

## Comando completo da suíte de referência

Execute na raiz com o Python instalado para esta fonte:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/test_usability.py tests/test_annual.py tests/test_comparison.py tests/test_frontend.py tests/test_dynamic_convergence.py tests/test_biophysical/test_animal/test_ration tests/test_biophysical/test_animal/test_nutrients tests/test_biophysical/test_animal/test_data_types/test_nutrition_data_structures.py tests/test_biophysical/test_animal/test_herd_manager tests/test_biophysical/test_animal/test_pen tests/test_simulation_engine.py tests/test_biophysical/test_feed_storage/test_feed_manager.py -q
```

## Cobertura

- Soluções conhecidas, unidades MN/MS, composição, parâmetros, limites e inviabilidade.
- Mínimos absorvíveis, critérios nativos e gordura abaixo/no/acima do teto, com tolerância numérica.
- Inicialização anormal do suplemento, região de confiança, melhoria do custo e conservação da melhor candidata.
- Tetos totais Ca/P abaixo/no/acima, limites de inclusão e arredondamento do Pen.
- Categorias/transições, exclusivo sem SLSQP, consumo, compras e pequenos lotes reais sem criar massa.
- Execução exclusiva real de 365 dias em subprocesso, com verificação de estoques, categorias, transições e tetos.
- AppTest com chamadas reais, comparações e processos isolados do frontend.

O ajuste final das opções anuais exercita as duas comparações, inclusive a exclusiva, sem remover a verificação do backend. A reprodução em cópia isolada é documentada no [relatório de publicação](../../evidencias/publicacao/README.md).

## Evidências e histórico

A rodada atual passou 969 casos em 362,68 s; a verificação direcionada final passou 33 casos. [XML, logs e capturas](../../evidencias/frontend_final/README.md). A reprodução isolada anterior validou a base de 954, sem atribuir a ela os 15 casos novos.

Os XML [testes_finais](../../evidencias/correcao_dinamica/testes_finais.xml) e [testes_verificacao](../../evidencias/correcao_dinamica/testes_verificacao.xml) registram 954 aprovações. Os tempos 128,87 s e 11.233,60 s pertencem a execuções sem controle equivalente de ambiente e não são benchmarks.

| Etapa histórica | Contagem |
|---|---:|
| Gordura e indicadores | 462 |
| Experimento comparativo | 466 |
| Primeira integração anual | 937 |
| Correção dinâmica | 954 |
| Usabilidade final | 969 |

As saídas antigas e falhas intermediárias foram preservadas. Não se relaxaram testes para ocultar falhas. [Registro consolidado](VALIDACAO.md).
