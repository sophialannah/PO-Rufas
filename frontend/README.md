# Frontend PO-RuFaS

Aplicação Streamlit local com sete áreas, ligada aos módulos Python do projeto. Mantém o LP estático e a simulação dinâmica anual; os resultados exibidos vêm do backend.

## Instalação

Na raiz, com Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -c constraints-po-rufas.txt -e ".[dev]" -r frontend/requirements.txt
.\frontend\iniciar_frontend.bat
```

Alternativa: `python -X utf8 -m streamlit run frontend/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false`. Abra http://127.0.0.1:8501. Use o mesmo interpretador da instalação; Ctrl+C encerra o servidor. Para venv uv sem pip: `uv pip install --python .venv/Scripts/python.exe -c constraints-po-rufas.txt -e ".[dev]" -r frontend/requirements.txt`.

## Áreas existentes

| Área | Funcionamento |
|---|---|
| Visão geral | Perfil, catálogo e fluxo operacional |
| Animal | Estado da população e hipóteses da demonstração estática |
| Ingredientes | Composição NRC de leitura; preços, estoques, NEL e limites editáveis |
| Otimização | Horizonte, metas estáticas e mínimos absorvíveis opcionais P/Ca |
| Resultados | Dieta MN/MS, custo, checks matemáticos, parecer e downloads |
| Cenários | Reotimização e experimentos A/B HiGHS/SLSQP |
| Simulação anual | Processos FULL_FARM isolados, progresso e séries reais |

No LP estático, a referência 98605 sem mínimos minerais permanece aproximadamente R$35,1059/dia e reprova por P absorvível. Isso não é o resultado anual. Para suplementação, selecione 231, informe os [parâmetros](../docs/po_rufas/03-dados.md), ative P/Ca e execute. NASEM permanece diagnóstico independente.

## Seleção anual

Escolha Simulação dinâmica integrada e uma das cinco opções:

1. **SLSQP nativo controlado** — requisitos NRC e tetos minerais da comparação.
2. **HiGHS híbrido ampliado** — categorias adultas suportadas, com fallback explícito conforme política.
3. **HiGHS exclusivo** — sem fallback SLSQP; falhas interrompem a execução.
4. **Comparação SLSQP versus HiGHS híbrido** — processos separados com as mesmas entradas.
5. **Comparação SLSQP versus HiGHS exclusivo** — referência e exclusivo isolados; exclusivo com política fail.

Configure duração 1–365, semente, meta de vacas, intervalo, ingredientes e parâmetros econômicos. O cenário usa NRC, clima de 2013 e preços demonstrativos UM/kg MS. Os resultados ficam em `output/annual_ui/<UUID>/`, sem substituir os anteriores. Política mineral padrão: `nrc2005_mtl`.

O progresso mostra dias efetivamente concluídos. Consulte custos, leite, consumo, inventário, minerais totais/absorvíveis, requisitos e convergência. O seletor de dia abre o JSON com iterações, resíduos e motivos. A comparação econômica exige resultados concluídos do mesmo grupo.

Os gráficos de aprovação adulta excluem bezerros, mostrados separadamente. Na evidência oficial há 998 curral-dias adultos aprovados no HiGHS e 252 registros de bezerros não aprovados em cada estratégia. Não se declara aprovação do rebanho inteiro. [Aplicabilidade dos indicadores](../docs/po_rufas/05-restricoes.md).

## Arquitetura e validação

O serviço estático usa lock e restauração de configurações temporárias/RNG. A área anual inicia subprocessos com configurações e estados próprios. FeedManager executa compras e baixa; o observador não faz segunda dedução. Entradas originais e resultados históricos são preservados.

Referência: **954 testes aprovados**, incluindo AppTest com processos reais. [Validação](../docs/po_rufas/VALIDACAO.md) · [Manual com telas finais](../docs/po_rufas/12-manual.md) · [Reprodução isolada](../evidencias/publicacao/README.md).
