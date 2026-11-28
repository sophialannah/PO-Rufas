> Registro de uma etapa anterior. Para o estado operacional e resultados reconferidos, consulte a [documentacao consolidada](../docs/po_rufas/README.md). Os numeros historicos deste arquivo foram preservados.

# Apresentação acadêmica — PO-Rufas

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

**Exatamente quatro slides, 5 minutos de exposição e demonstração + 5 minutos adicionais de perguntas.**
**Total: 10 minutos.**

Abra [apresentacao_rufas_5min.pptx](apresentacao_rufas_5min.pptx).
Leia o [roteiro completo](roteiro_completo.md) e o [guia da demonstração no navegador](guia_demonstracao_web.md).
Use os [cartões](cartoes_consulta.md) para ensaiar e o [banco de perguntas](perguntas_e_respostas.md) para estudar.
Arguição: [simulação de cinco minutos](simulacao_arguicao.md).
Falas individuais: [Sophia](roteiro_sophia.md) e [Anderson](roteiro_anderson.md).

Na raiz do projeto, execute `.\frontend\iniciar_frontend.bat`. Consulte o [guia de instalação do frontend](../frontend/README.md).

Como alternativa, execute `.\apresentacao\demonstracao_integrada.bat`. Pressione Enter para executar o solver e devolver a dieta ao `RationManager`. [Guia do terminal](guia_demonstracao.md).
A demonstração anterior (sem retorno ao `RationManager`) permanece em `demonstracao_solver.bat`.
A busca no catálogo permanece disponível como apoio (`linear_diet_catalog`).

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

## Revisão técnica final — 24/11/2026

A revisão posterior passou em 437 testes. Os 433 citados nos slides pertencem à validação histórica registrada. O custo da demo permanece R$ 34,9978/dia. TDN=0,65 corrige o cálculo intermediário de MP, que não é restrição do LP. Somente DMI é importada como exigência; PB, NEL e FDN suplementares continuam externas. A integração nutricional não está completa nem certificada pelo NASEM.

Leia a [revisão final](../docs/revisao_final_otimizador.md). Exemplo rastreável adicional: `python -m RUFAS.biophysical.animal.ration.linear_diet_workflow`. Preserve cinco minutos de apresentação e cinco adicionais de perguntas; use esse relatório como apoio à arguição.

## Demonstração integrada atual

Use `.\apresentacao\demonstracao_integrada.bat`: Animal 98605 (`Animal`) → NRC → lista `NRCFeed`/`Ingredient` → HiGHS → percentuais MS → `RationManager` → `NutritionSupplyCalculator` e `NutritionEvaluator`. Custo R$ 35,1059/dia; **442 testes aprovados** (42 específicos). A demo anterior permanece disponível em `demonstracao_solver.bat`. Veja [integração real](../docs/integracao_real_rufas.md). Após regenerar os materiais históricos com `gerar_materiais.py`, execute `atualizar_integracao.py` e exporte novamente o PDF no PowerPoint.
