# PO-RuFaS | Otimização Inteligente de Dietas

Aplicação local do projeto acadêmico de Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

## Executar no Windows

Use a `.venv` do projeto, com Python 3.12 ou 3.13 e as dependências do RuFaS descritas no `pyproject.toml`.
Instale a dependência da interface uma vez, com o ambiente preparado:

```powershell
.\.venv\Scripts\python.exe -m pip install -r frontend/requirements.txt
```

Se a `.venv` foi criada com uv e não tem pip, use `uv pip install --python .venv/Scripts/python.exe -r frontend/requirements.txt`
ou, com um pip disponível fora da venv, `pip --python .venv/Scripts/python.exe install -r frontend/requirements.txt`.

```powershell
.\frontend\iniciar_frontend.bat
```

Comando equivalente a partir da raiz:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m streamlit run frontend/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Abra [PO-RuFaS local](http://127.0.0.1:8501). Para outra porta, passe `--server.port 8502` e acesse a URL impressa pelo Streamlit.

## Demonstração

Abra **Animal** para conferir o perfil 98605 e a prévia NRC. Em **Ingredientes**, consulte composição e valores de cenário em matéria natural. Em **Otimização**, mantenha sete dias e clique em **Executar otimização**. Em **Resultados**, confira o custo diário, as restrições, a dieta e o parecer nativo. **Cenários** recalcula uma base e uma variação de preço, estoque ou limite de inclusão.

No cenário padrão, a regressão esperada é `optimal`, R$ 35,1059/dia, 11/11 verificações e parecer nativo **Não aprovada**, com déficit de fósforo absorvível de 6,68 g/dia. A aplicação recalcula esses valores. O [roteiro acadêmico](../apresentacao/roteiro_completo.md) inclui a alternativa por terminal.

Para reotimizar com minerais, adicione uma fonte do catálogo em **Ingredientes**, informe seus parâmetros e marque **Exigir fósforo e cálcio absorvíveis no LP (NRC 2001)**. A opção de diagnóstico NASEM calcula a exigência de fósforo em separado. [Parâmetros para reproduzir os cenários e documentação científica](../docs/fosforo_nasem_2021.md)

## Dados, unidades e execução

A aplicação oferece vacas Holandesas em lactação da população do repositório e ingredientes elegíveis com composição NRC. Peso, dias em lactação e paridade vêm do arquivo de população. Produção de leite, composição do leite, ambiente e metas suplementares são hipóteses identificadas na interface. A prévia NRC usa os alimentos da demonstração. A execução registra os requisitos do conjunto efetivamente selecionado. Valores de NEL, preços, estoques e limites de inclusão devem ser preenchidos para ingredientes adicionais.

O serviço converte os parâmetros de matéria natural para os campos esperados por `NRCFeed`. A integração existente chama `ingredient_from_feed` e `optimize_diet` (SciPy/HiGHS). A saída verificada passa à configuração em % MS do `RationManager` e retorna em kg MS/dia para `FeedInRation`, `NutritionSupplyCalculator` e `NutritionEvaluator`. O LP fixa a matéria seca calculada pelo NRC e aplica metas externas de PB, NEL e FDN. O diagnóstico nativo cobre os critérios efetivamente avaliados. Simulação diária, baixa de estoque, NASEM e outras categorias ficam fora do fluxo integrado.

A interface mantém parâmetros editáveis e resultados por sessão. O cache guarda apenas dados serializáveis. Um lock no serviço serializa as chamadas que usam as configurações temporárias de classe e o RNG. O contexto da demonstração restaura o estado mesmo após falhas. A integração da dieta usa subclasses por chamada. As entradas originais são somente leitura e as saídas são baixadas pelo navegador em CSV, JSON ou Markdown.

## Testes

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/test_frontend.py tests/test_biophysical/test_animal/test_ration tests/test_biophysical/test_animal/test_nutrients tests/test_biophysical/test_animal/test_data_types/test_nutrition_data_structures.py -q
```


## Simulação anual integrada

A sétima área, Simulação anual, inicia o motor FULL_FARM em processos isolados. Selecione duração, estratégia, semente, meta de vacas, intervalo, ingredientes adultos e parâmetros econômicos. O progresso usa os dias realmente concluídos. A estratégia linear é híbrida, com uso nativo/fallback explícito. Resultados anteriores ficam em output/annual_ui.

O cenário é NRC experimental com clima de 2013. Os preços são unidades monetárias demonstrativas por kg MS. [Manual e resultados anuais](../docs/po_rufas/12-manual.md) · [Evidências](../evidencias/anual/README.md)




## Estratégias dinâmicas corrigidas

Na aba anual, `native_slsqp` é a referência controlada; `linear_highs_all` é o híbrido ampliado; `linear_highs_exclusive` interrompe em falha e nunca executa SLSQP. `linear_highs` preserva a cobertura de lactação da integração anterior. O runner aplica igualmente a política explícita NRC 2005 aos modelos e mantém requisitos NRC 2001.

Além das séries existentes, a interface apresenta minerais por curral/categoria, requisitos absorvíveis, totais/tetos, avaliações e formulações com estado de convergência/encerramento. A execução exclusiva completou o cenário anual documentado; não é certificação geral de adequação nutricional nem de ótimo global. Consulte [a rodada corrigida](../evidencias/correcao_dinamica/README.md).
