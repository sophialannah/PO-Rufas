# PO-RuFaS — otimização de dietas integrada ao RuFaS

Projeto acadêmico de Pesquisa Operacional de **Sophia Lannah Beatriz Ferreira de Sousa** e **Anderson Alberto da Costa Silva**, desenvolvido sobre o simulador [RuFaS](https://github.com/RuminantFarmSystems/RuFaS).

A versão vigente oferece um **LP estático de coeficientes fixos** e um **modelo dinâmico de programação linear sequencial**, resolvido pelo HiGHS dentro do ciclo diário FULL_FARM. A integração dinâmica foi validada por 365 dias no cenário NRC, com formulação, evolução dos animais, compras, consumo e baixa real de estoque pelo FeedManager.

## Resultados oficiais do cenário controlado

| Indicador — 365 dias | SLSQP nativo controlado | HiGHS exclusivo |
|---|---:|---:|
| Valor dos alimentos efetivamente consumidos | 2.319,34875854 UM | 2.316,45106770 UM |
| Produção de leite | 140.223,666523 kg | 140.223,666523 kg |
| Formulações HiGHS aceitas | 0 | 1.002 |
| Chamadas SLSQP | 1.002 | 0 |
| Curral-dias adultos aprovados | 362 | 998 |

A redução de custo foi **0,1249355%**. Das 1.002 formulações HiGHS, **959 atingiram o critério de convergência**; **43 conservaram soluções viáveis sem convergência** (42 por estagnação e uma pelo limite de iterações). Os preços são **demonstrativos**, em UM/kg MS. O resultado não certifica ótimo global não linear ou superioridade econômica universal.

A validação computacional de referência tem **969 testes aprovados**. Os 998 curral-dias aprovados são de **currais adultos**. Há **252 curral-dias de bezerros não aprovados em cada estratégia**, registrados separadamente sob um fluxo próprio de alimentação e com limitações na aplicabilidade dos indicadores comuns. Não há afirmação de aprovação nutricional de todo o rebanho.

[Resultados, diários e XML oficiais](evidencias/correcao_dinamica/README.md) · [Documentação em 14 capítulos](docs/po_rufas/README.md) · [Revisão para publicação](evidencias/publicacao/README.md)

## Instalação e execução

Python 3.12 foi usado na validação; o projeto declara suporte a Python 3.12/3.13. Execute na raiz de uma cópia do repositório:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -c constraints-po-rufas.txt -e ".[dev]" -r frontend/requirements.txt
.\.venv\Scripts\python.exe -X utf8 -m streamlit run frontend/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Abra http://127.0.0.1:8501. O BAT `frontend/iniciar_frontend.bat` permanece disponível. O arquivo `constraints-po-rufas.txt` registra versões do ambiente PO-RuFaS; `constraints-release.txt` pertence a uma versão upstream anterior e não deve ser combinado com os requisitos atuais sem análise.

## Funcionalidades e modos

- Seleção de animais e alimentos NRC, edição de preços, estoques e limites.
- LP estático com MS, PB, NEL, FDN e mínimos absorvíveis de P/Ca obrigatórios na interface NRC; backend preservado para regressões históricas e avaliação nativa posterior.
- Comparação experimental A (mesmo LP, HiGHS/SLSQP) e B (formulações estática/nativa distintas).
- Simulação anual: SLSQP controlado, HiGHS híbrido ampliado, HiGHS exclusivo e comparações controladas entre eles.
- Progresso real, custos diários/acumulados, consumo, compras, estoques, minerais, convergência e critérios por categoria.
- Diagnóstico complementar de fósforo NASEM 2021 em configurações avançadas, desativado por padrão e sem interferir na otimização NRC.
- Exportação CSV/JSON/Markdown e capturas reais para o [manual](docs/po_rufas/12-manual.md).

O modo exclusivo não executa fallback SLSQP; uma falha interrompe a execução e fica registrada. Os bezerros não passam pelo RationOptimizer e não são contabilizados como fallback.

## Dois modelos matemáticos

| Aspecto | LP estático | Modelo dinâmico sequencial |
|---|---|---|
| Decisão principal | kg MN/animal/dia | kg MS/animal/dia no contrato nativo, convertido no adaptador |
| Requisitos | Fixos durante uma resolução; PB/NEL suplementares explícitas | Recalculados por curral/dia no RuFaS |
| Restrições | Linhas de coeficientes fixos | Linearizações locais das funções nativas, verificadas no modelo original |
| Estoque | Alocação estática por horizonte | Compras, colheitas, consumo e inventário nativos |
| Conclusão de otimalidade | Ótimo do LP informado, quando verificado | Heurística local, sem certificado de ótimo global não linear |

A política dinâmica `nrc2005_mtl` acrescenta tetos **totais** de Ca/P segundo NRC 2005, igualmente aos dois solvers controlados. Os requisitos **absorvíveis** continuam NRC 2001. Consulte [modelagem](docs/po_rufas/04-modelagem.md) e [limitações](docs/po_rufas/13-limitacoes.md).

## Reprodução por terminal

Use diretórios novos para as simulações:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m RUFAS.biophysical.animal.ration.linear_diet_example
.\.venv\Scripts\python.exe -X utf8 -m experiments.comparison --repeats 5 --output output/comparacao_nova
.\.venv\Scripts\python.exe -X utf8 -m experiments.annual --days 365 --strategy linear_highs_exclusive --output output/exclusivo_novo
```

[Comando completo da suíte de 969 testes](docs/po_rufas/11-testes.md) · [Procedimento de reprodução isolada](evidencias/publicacao/README.md)

## Organização e histórico

`RUFAS/` contém o motor e os otimizadores; `frontend/` a aplicação; `experiments/` os executores e relatórios; `tests/` os testes e fixtures; `input/` os dados; `docs/po_rufas/` a documentação vigente; `apresentacao/` os roteiros; `evidencias/` as provas de execução. `output/`, ambientes virtuais e caches são locais e ignorados.

As contagens 462/466/937 e o aumento de custo de 9,05% pertencem a etapas **históricas**, anteriores à correção da inicialização e convergência. São preservadas nos respectivos relatórios e nas [cópias documentais anteriores à consolidação](evidencias/publicacao/historico_documental/manifesto.json), sem representar os resultados vigentes. [Histórico das validações](docs/po_rufas/VALIDACAO.md).

## Autoria, licença e limites

O RuFaS, suas bibliotecas e modelos originais permanecem atribuídos aos autores originais. O projeto declara GPL-3.0-only em `pyproject.toml`; [COPYING.txt](COPYING.txt) e [COPYING.LESSER.txt](COPYING.LESSER.txt) foram recuperados da revisão upstream auditada. [Referências e atribuição](docs/po_rufas/14-referencias.md).

A validação cobre o cenário NRC e as três categorias adultas nele ativas. Não estabelece validação universal de NASEM, agrupamentos alternativos ou alimentação de bezerros. A resposta produtiva à dieta e os coeficientes minerais locais têm limitações. Não houve alteração do avaliador para eliminar reprovações nem modificação artificial de dados para produzir economia.
