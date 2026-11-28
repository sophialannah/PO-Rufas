# Revisão final e candidato à publicação — PO-RuFaS

Branch: **fix/validacao-nutricional-rufas**. Base Git: 5bb6775a4797f7c445bcfa025c3121aa2fb3bc96, acrescida das alterações locais inventariadas. Nenhum staging, commit, push ou merge foi executado.

## Escopo concluído

A documentação principal foi consolidada por reescrita, removendo contradições entre versões. README raiz, frontend, índice, 14 capítulos, VALIDACAO e documentação da apresentação descrevem a versão vigente. Os textos anteriores foram preservados em [historico_documental/manifesto.json](historico_documental/manifesto.json). Slides e geradores anteriores permanecem históricos; o deck novo é [apresentacao_po_rufas_final.pptx](../../apresentacao/apresentacao_po_rufas_final.pptx).

O solver e o avaliador nutricional não foram reformulados nesta etapa. Os ajustes de código se limitam às cinco opções/comparações e separação visual dos bezerros no frontend, registro de proveniência sem .git e ferramentas de auditoria/reprodução. O teste anual da interface agora exercita ambas as comparações com processos reais.

## Resultados oficiais preservados

| Indicador | SLSQP controlado | HiGHS exclusivo |
|---|---:|---:|
| Dias | 365 | 365 |
| Consumo valorizado | 2.319,34875854 UM | 2.316,45106770 UM |
| Leite | 140.223,666523 kg | 140.223,666523 kg |
| Formulações HiGHS | 0 | 1.002 |
| Chamadas SLSQP | 1.002 | 0 |
| Curral-dias adultos aprovados | 362 | 998 |
| Curral-dias de bezerros não aprovados | 252 | 252 |

Redução de custo **0,1249355%**, com preços demonstrativos. HiGHS: **959 convergentes e 43 viáveis sem convergência**, sem certificado de ótimo global não linear ou superioridade econômica universal. O híbrido ampliado reproduziu os valores do exclusivo sem fallback nesse cenário.

Os diretórios oficiais e seus XML permanecem em [correcao_dinamica](../correcao_dinamica/README.md). A revisão não reescreveu contabilização econômica nem substituiu seus resultados por valores fixos.

## Bezerros: investigação adicional

[bezerros_auditoria.json](bezerros_auditoria.json) e [bezerros_criterios.csv](bezerros_criterios.csv) reconfirmam 252 registros não aprovados em cada estratégia. Os campos FDN total, FDN de forragem e gordura aparecem em todos; também MP e DMI, omitidos no resumo externo inicial.

O ramo CALF não chama RationOptimizer. CalfRationManager estima ingestão/requisitos próprios; o Pen aplica ração prescrita e o relatório usa os indicadores comuns de novilhas. FDN mínima adulta, FDN de forragem e teto adulto de gordura não constituem critérios automaticamente transferíveis à alimentação láctea de um pré-ruminante.

No primeiro dia, o registro tem 3 kg MS, FDN zero e gordura 0,507 kg; a margem de gordura é −9,9 p.p. Não se conclui adequação da dieta a partir dessa explicação. O ramo CALF ainda atribui me_intake ao campo metabolizable_protein e usa zeros/TODO para Ca/P, além da diferença entre DMI estimada e prescrita. São inconsistências e limites para auditoria científica posterior, sem mudanças no avaliador nesta etapa.

Assim, os 998 curral-dias adultos aprovados não representam aprovação de todo o rebanho. [Investigação completa e fontes](../../docs/po_rufas/05-restricoes.md).

## Instalação e reprodução isoladas

Foi preparada uma cópia fora da pasta original e sem .git, incluindo o estado local candidato. Foi criada **venv nova**, sem reutilizar os pacotes instalados da original. A instalação usou pyproject.toml, frontend/requirements.txt e constraints-po-rufas.txt; pip check retornou **No broken requirements found**.

Nessa cópia foram executados:

| Verificação | Resultado |
|---|---|
| Instalação independente | Concluída; pip check sem conflitos |
| LP estático | Executado pelo módulo linear_diet_example |
| Comparação experimental | Cinco repetições, animais 98605/93785, A/B reais |
| Ano exclusivo | 365 dias; 2.316,451067700519 UM; 1.002 aceites HiGHS; zero SLSQP |
| Suíte relevante completa | **954 aprovados em 147,68 s** |
| Frontend | AppTest real com as duas comparações; servidor Streamlit para capturas |

O ano exclusivo reproduziu o custo e o leite oficiais. Os metadados informam commit/dirty indisponíveis na fonte sem .git, em vez de depender do repositório da máquina original. O manifesto de exportação preserva a base e os hashes.

Os logs, XML e summaries sanitizados desta etapa ficam neste diretório e no subdiretório reproducao. Caminhos absolutos locais e o nome da máquina não são necessários à publicação.

### Comandos

Na raiz da cópia:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -c constraints-po-rufas.txt -e ".[dev]" -r frontend/requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -X utf8 -m RUFAS.biophysical.animal.ration.linear_diet_example
.\.venv\Scripts\python.exe -X utf8 -m experiments.comparison --repeats 5 --output output/repro_comparacao
.\.venv\Scripts\python.exe -X utf8 -m experiments.annual --days 365 --strategy linear_highs_exclusive --output output/repro_exclusivo
.\.venv\Scripts\python.exe -X utf8 -m streamlit run frontend/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

[Comando completo de testes](../../docs/po_rufas/11-testes.md). O exportador experiments.publication cria uma cópia isolada nova; nunca faz staging ou commit. Use diretórios novos para preservar execuções.

## Frontend e telas

Há cinco escolhas explícitas: SLSQP controlado; híbrido ampliado; exclusivo; comparação SLSQP/híbrido; comparação SLSQP/exclusivo. No exclusivo, o aviso informa ausência de fallback e fixa fail. A métrica compara somente pares concluídos do mesmo UUID.

[Manual e telas finais](../../docs/po_rufas/12-manual.md). As capturas são do frontend real da cópia isolada. O manifesto de telas identifica a duração, sem apresentar um dia como ano completo.

## Conteúdo candidato ao GitHub

[candidato_arquivos.csv](candidato_arquivos.csv) e [candidato_inventario.json](candidato_inventario.json) listam os arquivos do estado candidato, tamanhos e hashes. Os dois catálogos não contêm o próprio hash para evitar referência circular. O inventário não equivale a staging nem aprovação de publicação.

Incluem-se código e dados RuFaS, módulos estáticos/dinâmicos, comparações, fixtures, testes, frontend, documentação, apresentação vigente, evidências definitivas e intermediárias relevantes e licenças. O [índice de execuções](../indice_execucoes.csv) classifica as pastas sem renomear ou perder rastreabilidade. Todos os registros científicos anteriores foram preservados.

Devem permanecer ignorados: .venv/.venv-python e outros ambientes, __pycache__, .pyc, caches pytest/mypy/ruff, .env/credenciais, output temporário, builds e o HISTORICO_DESENVOLVIMENTO.md pessoal. O histórico pessoal continua no disco, sem ser dependência da ciência publicada. As exceções .txt permitem versionar COPYING/COPYING.LESSER, constraints-po-rufas e textos científicos arquivados.

O maior arquivo candidato já pertence aos dados upstream: input/data/end_to_end_testing/open_lot/e2e_json_animal_filter.json, aproximadamente **88,53 MiB**, abaixo do limite de 100 MiB por arquivo, mas acima do patamar usual de aviso de 50 MiB. Os diários finais têm aproximadamente 20,9 MiB cada. Nenhum arquivo foi descartado para reduzir volume; o inventário permite revisar o peso da entrega antes de aprová-la. Uma migração futura de dados grandes para armazenamento externo/LFS exigiria decisão própria e não foi feita automaticamente.

O diff e os não versionados foram revisados. A auditoria busca padrões de credenciais sem imprimir valores, rejeita caches/arquivos gerados no candidato e verifica limites de tamanho. Isso não substitui revisão humana de segredos.

Dois arquivos históricos continham caminhos locais: docs/revisao_final_otimizador.md e correcao_dinamica/testes.xml. Os originais integrais foram preservados em output/publication_private_originals, ignorado, e somente os caminhos foram saneados nas versões publicáveis. [Hashes e escopo do saneamento](saneamento_caminhos.json); nenhum resultado científico foi alterado. [Lista de alterações e novos arquivos](arquivos_alterados.csv) e [auditoria Git](auditoria_git.json) complementam o inventário completo.

## Inconsistências documentais corrigidas

- Contagens 462/466/937 ficaram no histórico; a referência atual é 954.
- A integração diária e a baixa física de estoque são descritas como implementadas.
- A cobertura atual inclui as categorias adultas efetivamente chamadas, não apenas lactação.
- Os tetos totais minerais dinâmicos estão explícitos e separados dos requisitos absorvíveis.
- O aumento histórico de 9,05% foi separado da redução controlada vigente.
- LP estático fixo e programação linear sequencial dinâmica têm modelos próprios.
- A aprovação adulta foi separada dos bezerros e dos limites do avaliador.
- Os roteiros/slides vigentes usam os resultados controlados e as ressalvas científicas.

## Limitações e revisão solicitada

A validação cobre o cenário NRC e três categorias ativas. Permanecem 43 soluções viáveis sem convergência, ausência de ótimo global não linear, coeficientes minerais genéricos, resposta produtiva limitada, agrupamentos sem ano próprio e inadequação/inconsistências no relatório de bezerros. Preços comerciais completos não foram verificados. Python 3.12 foi exercitado; 3.13 está apenas no intervalo declarado.

**Sugestão de commit:** `docs: consolida versão acadêmica e valida reprodução isolada do PO-RuFaS`.

O conjunto inclui alterações locais anteriores, identificadas no inventário/diff; revisar o escopo completo antes de criar o commit. **Nenhum commit, push ou merge foi executado.**
