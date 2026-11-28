> HISTORICAL DOCUMENT: previous static-only release. Current documentation: [PO-RuFaS](README.md).

# PO-Rufas — Otimização linear de dietas

Projeto acadêmico de **Pesquisa Operacional aplicada à alimentação de bovinos leiteiros**, desenvolvido em Python dentro do [RuFaS](https://github.com/RuminantFarmSystems/RuFaS).

O módulo encontra uma dieta de **custo mínimo para um animal por execução**, com programação linear (`scipy.optimize.linprog`, HiGHS), restrições nutricionais, estoques e limites de inclusão. Cada restrição é verificada após a solução.

> **Estado atual:** núcleo funcional, adaptadores RuFaS, exemplos e testes. Os exemplos usam preços e parâmetros nutricionais suplementares demonstrativos. O ótimo matemático não comprova adequação nutricional completa para aplicação na fazenda.

## Documentação

- [Apresentação de 5 minutos: PowerPoint, falas da dupla e demonstração](../../apresentacao/README.md)
- [Modelo matemático, unidades, fontes e limitações](../../docs/otimizador_linear.md)
- [Roteiro de apresentação ao professor](../../docs/apresentacao_projeto.md)
- [Apresentação original do RuFaS](../../docs/README_RuFaS_original.md)

## Instalação no Windows

Requisito: **Python 3.12 ou 3.13**, conforme `pyproject.toml`. Execute no PowerShell, na raiz do repositório:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Se a `.venv` já está preparada, pule a instalação. Não é necessário ativar o ambiente. No IDE, selecione `.venv\Scripts\python.exe` como interpretador.

## Executar o otimizador

### Busca no catálogo completo

```powershell
.\.venv\Scripts\python.exe -m RUFAS.biophysical.animal.ration.linear_diet_catalog --demo --seed 42
```

O programa avalia os 300 registros do catálogo, cruza a composição NRC/NASEM e otimiza simultaneamente as quantidades de todos os candidatos:

| Resultado da auditoria | Registros |
|---|---:|
| Candidatos com composição utilizável | 185 |
| Sem composição nas tabelas consultadas | 110 |
| Excluídos por MS zero ou categoria fora do cenário | 5 |

“Candidato” indica aprovação no filtro de dados/categoria, não aptidão nutricional ou sanitária certificada. NRC tem prioridade quando o ID aparece nas duas bibliotecas.

Com semente 42: vaca de **661 kg, DEL 94 e 28 kg de leite/dia**, custo demonstrativo de aproximadamente **R$ 23,5276/dia**. A combinação encontrada contém alfafa, silagem de mistura de gramíneas/leguminosas e farelo de soja por expeller.

Trocar `--seed` altera **a vaca e os parâmetros demonstrativos dos alimentos**. A diferença de custo entre sementes não representa apenas o efeito do perfil animal.

### Exemplo didático com três alimentos

```powershell
.\.venv\Scripts\python.exe -m RUFAS.biophysical.animal.ration.linear_diet_example
```

Usa alfafa, milho e soja para uma vaca de 650 kg, DEL 100 e 30 kg de leite/dia. Custo demonstrativo: **R$ 34,9978/dia**. Os preços e parâmetros diferem dos usados no catálogo; os dois custos não comprovam uma economia entre dietas comparáveis.

## Resultados e entradas próprias

| Execução | Arquivo gerado |
|---|---|
| Catálogo: perfil, auditoria e solução | `output/catalog_diet/result.json` |
| Catálogo: parâmetros editáveis | `output/catalog_diet/parameters.csv` |
| Exemplo com três alimentos | `output/linear_diet_example.json` |

O JSON inclui as quantidades, inclusive zeros, e a verificação das restrições. `output/linear_diet_cow_2.json`, quando presente, é um resultado anterior de uma execução pontual, não o resultado da busca no catálogo.

As execuções substituem os arquivos no destino escolhido. Use `--output-dir output/meu_cenario` para separar cenários. Os resultados são gerados localmente e ignorados pelo Git.

Para substituir os parâmetros simulados, gere o CSV demonstrativo, copie-o e edite valores e fontes:

```powershell
Copy-Item output/catalog_diet/parameters.csv input/meus_parametros.csv
.\.venv\Scripts\python.exe -m RUFAS.biophysical.animal.ration.linear_diet_catalog --parameters input/meus_parametros.csv --seed 42 --cp-min 3.5 --nel-min 34 --output-dir output/meu_cenario
```

`3.5` e `34` são exemplos de argumentos em kg PB/dia e Mcal NEL/dia, não recomendações. Defina metas fundamentadas para o perfil. O modo `--parameters` continua gerando a vaca pela semente; não importa um animal do CSV.

Preserve uma linha por candidato. Estoque, mínimo e máximo iguais a zero representam indisponibilidade. Os parâmetros do CSV são em base de **matéria seca**; o adaptador converte para a base de decisão em **matéria natural**.

## Organização do projeto

A arquitetura original foi preservada. O trabalho acadêmico está concentrado nestes arquivos:

| Caminho | Responsabilidade |
|---|---|
| `RUFAS/biophysical/animal/ration/linear_diet.py` | Dados, formulação linear e verificação |
| `RUFAS/biophysical/animal/ration/linear_diet_adapter.py` | Conversão dos objetos e unidades RuFaS |
| `RUFAS/biophysical/animal/ration/linear_diet_example.py` | Exemplo com três alimentos |
| `RUFAS/biophysical/animal/ration/linear_diet_catalog.py` | Catálogo completo, CSV e cenário reproduzível |
| `input/data/feed/` | Catálogo e bibliotecas de composição |
| `tests/test_biophysical/test_animal/test_ration/test_linear_diet.py` | Testes do núcleo e integração |
| `tests/test_biophysical/test_animal/test_ration/test_linear_diet_catalog.py` | Testes do catálogo e parâmetros |
| `docs/otimizador_linear.md` | Documentação técnica e científica |
| `docs/apresentacao_projeto.md` | Roteiro de demonstração |
| `output/` | Resultados gerados, não versionados |

`main.py` continua sendo a entrada da simulação original. O arquivo `linear_diet.py` define o núcleo e não imprime uma demonstração ao ser executado sozinho.

## Modelo e integração

A variável `x_i` representa kg de matéria natural do ingrediente i por dia. O objetivo é minimizar `Σ preço_i × x_i`, sujeito a MS, PB, NEL, FDN, minerais opcionais, inclusão e estoque por período.

A integração reutiliza `Feed`, `NutritionRequirements`, `Animal`, o calculador NRC e a composição dos alimentos. O resultado também disponibiliza **kg MS/dia**, compatíveis com as estruturas de ração do RuFaS.

O RuFaS já possui um otimizador **não linear**, em `ration_optimizer.py`. Este projeto acrescenta uma alternativa linear com coeficientes fixos; não substitui o modelo existente nem aplica automaticamente a dieta ao ciclo diário da fazenda.

## Testes

Testes específicos do trabalho:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_biophysical/test_animal/test_ration/test_linear_diet.py tests/test_biophysical/test_animal/test_ration/test_linear_diet_catalog.py -q
```

Verificação ampliada dos componentes relacionados:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_biophysical/test_animal/test_ration tests/test_biophysical/test_animal/test_nutrients tests/test_biophysical/test_animal/test_data_types/test_nutrition_data_structures.py -q
```

Última execução registrada da verificação ampliada: **433 testes aprovados**. Isso não equivale à execução de toda a suíte ou de uma fazenda completa.

## Limitações e próximos passos

- Apenas o consumo de MS é importado diretamente das exigências calculadas nos exemplos. PB, NEL e limites de FDN suplementares são hipóteses explícitas.
- NEL não é energia digestível; proteína bruta não é proteína metabolizável. Não há conversões automáticas entre essas grandezas.
- Preços e estoques demonstrativos não são cotações ou disponibilidade observada.
- Restrições por ingrediente, excessos minerais, toxicidade e resposta produtiva não estão completamente representados.
- Próximas etapas: parâmetros documentados, reavaliação nutricional completa, integração diária e comparação de cenários econômicos.

## Problemas comuns

| Situação | Como resolver |
|---|---|
| `python` abre a Microsoft Store ou usa outro ambiente | Use `.\.venv\Scripts\python.exe`. |
| `No module named RUFAS` ou dependências ausentes | Instale na raiz com o mesmo interpretador usado na execução. |
| Executar o núcleo não mostra resultados | Execute `linear_diet_example` ou `linear_diet_catalog`. |
| Resultado `infeasible` | Confira exigências, estoques e limites; não é uma solução ótima. |
| Custo muda ao trocar a semente | Os preços e estoques demonstrativos também são sorteados. |

## Origem e licença

Este repositório deriva do **RuFaS**, desenvolvido pela equipe Ruminant Farm Systems. A autoria do simulador e dos modelos existentes permanece com seus autores. O projeto declara licença **GPL-3.0-only** em `pyproject.toml`.

Consulte a [apresentação original](../../docs/README_RuFaS_original.md), a [documentação científica local](../../docs/scientific/) e a [documentação oficial](https://ruminantfarmsystems.github.io/RuFaS/). Referências e materiais acadêmicos estão detalhados na [documentação do otimizador](../../docs/otimizador_linear.md).
