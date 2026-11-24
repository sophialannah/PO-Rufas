# Apresentação acadêmica — PO-Rufas

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

**Exatamente quatro slides, 5 minutos de exposição e demonstração + 5 minutos adicionais de perguntas.**
**Total: 10 minutos.**

Abra [apresentacao_rufas_5min.pptx](apresentacao_rufas_5min.pptx).
Leia o [roteiro completo](roteiro_completo.md) e o [guia da demonstração](guia_demonstracao.md).
Use os [cartões](cartoes_consulta.md) para ensaiar e o [banco de perguntas](perguntas_e_respostas.md) para estudar.
Arguição: [simulação de cinco minutos](simulacao_arguicao.md).
Falas individuais: [Sophia](roteiro_sophia.md) e [Anderson](roteiro_anderson.md).

```powershell
.\apresentacao\demonstracao_solver.bat
```

O terminal mostra as entradas; Enter inicia uma nova chamada do solver. A apresentação escolhe
o exemplo de três ingredientes para caber no tempo. A busca no catálogo permanece disponível como apoio.

Resultados: [relatório técnico](resultados_validados.md). Preparação: [checklist](checklist_apresentacao.md).
As saídas em `evidencias/` documentam execuções reais; os parâmetros ilustrativos continuam identificados.

## Recriar os materiais

Dependências opcionais de autoria e verificação:

```powershell
.\.venv\Scripts\python.exe -m pip install -r apresentacao/requirements.in
```

Os registros versionados omitem caminhos pessoais e o nome da máquina; os resultados numéricos são preservados.

Na raiz do repositório, com o ambiente preparado e `python-pptx==1.0.2` instalado:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m apresentacao.validar_projeto
.\.venv\Scripts\python.exe -X utf8 -m apresentacao.gerar_materiais
```

A regeneração substitui os arquivos gerados e atualiza a base de resultados dos slides.
`conteudo.py` centraliza as falas e perguntas; `gerar_materiais.py` cria o PowerPoint e os guias.
O solver e as equações continuam nos módulos originais do projeto.
A entrega é acompanhada no [PR #6](https://github.com/sophialannah/PO-Rufas/pull/6).
