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
| Otimização | Horizonte, metas estáticas e mínimos absorvíveis obrigatórios P/Ca no fluxo NRC |
| Resultados | Dieta MN/MS, custo, checks matemáticos, parecer e downloads |
| Cenários | Reotimização e experimentos A/B HiGHS/SLSQP |
| Simulação anual | Processos FULL_FARM isolados, progresso e séries reais |

Na interface estática, os mínimos de fósforo e cálcio absorvíveis estão sempre ativos no fluxo NRC 2001. Com os três alimentos iniciais, o caso 98605 fica inviável por fósforo; para suplementação, selecione 231, informe os [parâmetros](../docs/po_rufas/03-dados.md) e execute. Não se acrescenta suplemento automaticamente. A referência sem mínimos (R$35,1059/dia, reprovada por P absorvível) permanece disponível no backend para regressão histórica, sem alterar seus resultados experimentais.

O diagnóstico complementar de fósforo NASEM 2021 fica em **Configurações avançadas**, recolhidas inicialmente, e vem desativado. Ele calcula uma exigência em separado e **não interfere na otimização NRC 2001**.

## Seleção e edição de ingredientes

A seleção múltipla aceita ingredientes elegíveis do catálogo NRC. Composição, energia digestível/NDT e limites disponíveis são lidos das fontes originais; os limites são convertidos de kg MS para kg MN. Energia digestível não é transformada em NEL. Preço, estoque e NEL sem fonte ficam em branco, com lista dos campos obrigatórios pendentes.

Os campos editáveis ficam à esquerda da tabela, e os dados de composição são de leitura. As edições são preservadas ao adicionar, remover ou voltar a selecionar ingredientes. Um limite amplo do catálogo não é recomendação nutricional de inclusão.

**Carregar cenário demonstrativo validado (4 ingredientes)** lê os parâmetros publicados em `evidencias/comparacao/configuracao.json`, incluindo o fosfato bicálcico 231. São hipóteses demonstrativas identificadas, sem criação de novos preços, estoques ou valores energéticos. O botão carrega os ingredientes; animal e metas permanecem nos respectivos controles.

Uma execução inviável explica o conflito e orienta a revisar dados/alimentos. Nenhum alimento é acrescentado automaticamente e os mínimos NRC não são retirados.

## Seleção anual

Escolha Simulação dinâmica integrada e uma das cinco opções:

1. **SLSQP nativo controlado** — requisitos NRC e tetos minerais da comparação.
2. **HiGHS híbrido ampliado** — categorias adultas suportadas, com fallback explícito conforme política.
3. **HiGHS exclusivo** — sem fallback SLSQP; falhas interrompem a execução.
4. **Comparação SLSQP versus HiGHS híbrido** — processos separados com as mesmas entradas.
5. **Comparação SLSQP versus HiGHS exclusivo** — referência e exclusivo isolados; exclusivo com política fail.

Configure duração 1–365, semente, meta de vacas, intervalo, ingredientes e parâmetros econômicos. O cenário usa NRC, clima de 2013 e preços demonstrativos UM/kg MS. Os resultados ficam em `output/annual_ui/<UUID>/`, sem substituir os anteriores. Política mineral padrão: `nrc2005_mtl`.

O progresso mostra dias efetivamente concluídos. Consulte custos, leite, consumo, inventário, minerais totais/absorvíveis, requisitos e convergência. O seletor de dia abre o JSON com iterações, resíduos e motivos. A comparação econômica exige resultados concluídos do mesmo grupo.

## Resultados anuais já calculados e cartões econômicos

Em **Resultados anuais já calculados**, escolha a comparação controlada ou o histórico anterior à correção e clique **Carregar resultados anuais das evidências**. Esse caminho é somente leitura e não inicia subprocessos. Ele fica disponível sem iniciar o modo dinâmico. Resultados carregados são identificados como evidências arquivadas; novas simulações têm identificação e grupo próprios.

Os cartões mostram custos RuFaS/PO-RuFaS, diferença absoluta, percentual e estratégia mais econômica, calculada a partir dos valores reais. Percentual = 100 × (RuFaS − PO) / RuFaS: pode ser positivo, negativo ou zero; com referência zero, não é definido. Não se misturam grupos históricos e novas entradas para criar uma comparação.

Tabelas e séries usam nomes em português brasileiro, como RuFaS original, PO-RuFaS híbrido/exclusivo e Custo alimentar estimado. O JSON técnico conserva os identificadores originais para auditoria. A comparação estática B também mostra cartões, com ressalva de que as formulações são diferentes.

## Desempenho da exibição

Os resumos ficam disponíveis sem ler os diários completos. **Carregar séries diárias e detalhes desta execução** solicita essa leitura explicitamente. O cache considera caminho, modificação em nanossegundos, tamanho e dias concluídos; novas linhas invalidam a entrada. Nenhuma precisão numérica ou linha de resultado é removida.

Uma medição local com três amostras do diário oficial de 365 dias (21.883.947 bytes) observou medianas de 0,8996 s na leitura/decodificação sem cache e 0,2215 s com cache; a leitura só do resumo ficou em 0,00065 s. Os objetos decodificados foram comparados e eram iguais. Esses números medem a leitura da interface, não a velocidade do solver ou uma nova simulação, e não são um benchmark universal. Logs da verificação local ficam em `output/usability_performance.json`.

Uma investigação futura da simulação nova deve medir separadamente inicialização, funções nutricionais, formulações e gravação de traços antes de propor mudanças. Esta etapa não altera Jacobianos, tolerâncias, iterações, equações ou paralelismo do backend; as estratégias continuam em processos isolados como antes.

Os gráficos de aprovação adulta excluem bezerros, mostrados separadamente. Na evidência oficial há 998 curral-dias adultos aprovados no HiGHS e 252 registros de bezerros não aprovados em cada estratégia. Não se declara aprovação do rebanho inteiro. [Aplicabilidade dos indicadores](../docs/po_rufas/05-restricoes.md).

## Arquitetura e validação

O serviço estático usa lock e restauração de configurações temporárias/RNG. A área anual inicia subprocessos com configurações e estados próprios. FeedManager executa compras e baixa; o observador não faz segunda dedução. Entradas originais e resultados históricos são preservados.

Referência científica publicada: **954 testes aprovados**, incluindo AppTest com processos reais. Esta revisão de usabilidade preservou esses casos e acrescentou **15 regressões**, com **969 aprovados em 362,68 s** na suíte relevante. Os testes direcionados finais também passaram (33 casos), incluindo os detalhes históricos e os cartões da comparação estática. [Logs e XML versionados](../evidencias/frontend_final/README.md). As evidências científicas publicadas permanecem inalteradas. [Validação](../docs/po_rufas/VALIDACAO.md) · [Manual com capturas da versão publicada](../docs/po_rufas/12-manual.md) · [Reprodução isolada](../evidencias/publicacao/README.md).
