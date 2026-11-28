

# Evidências experimentais PO-RuFaS

Execução de 27/11/2026 sobre o commit 5bb6775 e alterações locais. O JSON declara dirty=true e versões. O manifesto SHA-256 identifica os arquivos de implementação efetivamente utilizados.

## Reproduzir

Na raiz, com a venv preparada:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m experiments.comparison --repeats 5
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/test_comparison.py tests/test_frontend.py tests/test_biophysical/test_animal/test_ration tests/test_biophysical/test_animal/test_nutrients tests/test_biophysical/test_animal/test_data_types/test_nutrition_data_structures.py -q --junitxml=evidencias/comparacao/testes.xml
```

Os arquivos do diretório de destino são substituídos pela CLI. Use --output com outra pasta para preservar novas rodadas. Para capturar telas, inicie Streamlit e execute `python -m experiments.capture_frontend` em Windows com Edge.

## Artefatos

| Arquivo | Conteúdo |
|---|---|
| resultados.json | Experimentos A/B completos, matriz, controles, versões, requisitos, composição, cada repetição e parecer |
| configuracao.json | Parâmetros dos quatro ingredientes e metadados |
| resumo.csv | Última candidata de cada método e estatísticas de tempo |
| ingredientes.csv | Quantidades por animal e método em MS |
| restricoes.csv | Folgas, limites e satisfação por método |
| tempos.csv | Todas as amostras cronometradas |
| nutricao.csv | Oferta e mínimo P/Ca/MP |
| sensibilidade.json / csv | Reotimizações do preço do milho |
| economico_parcial.json | Cenário híbrido com cotação somente do milho |
| cotacoes.csv | Preço, data, origem e conversões do milho |
| testes.xml / testes_saida.md | JUnit e saída da suíte, 466 aprovados |
| telas/*.png | Capturas reais do navegador |
| demais PNG | Custos, participações, oferta versus exigência, sensibilidade e tempos |
| milho_ifag.png | Boletim público IFAG consultado, com autoria institucional |
| manifesto.json | Hashes dos arquivos Python e commit base |

## Metodologia e interpretação

São dois animais, quatro ingredientes e padrão NRC. Cada método recebe um aquecimento excluído e cinco chamadas medidas sequenciais. A medida usa perf_counter; a avaliação é externa ao cronômetro. Os métodos são executados em ordem fixa, portanto cache e estado térmico podem afetar comparações pequenas. Foram registrados mínimo, máximo e mediana. A máquina é ambiente Windows local; identificadores pessoais foram omitidos.

Experimento A usa a mesma formulação linear em MN. SLSQP usa ponto médio dos limites, Jacobianas analíticas, ftol=1e-9 e maxiter=1000. HiGHS usa opções e inicialização internas. O custo coincide dentro de 1e-6 R$/dia. Uma única rodada pequena não demonstra superioridade geral.

Experimento B usa a chamada original do RuFaS em MS, com faixas nutricionais nativas e limite ajustado por estoque/dias. Suas opções são as padrão da API e SciPy instalada (ftol padrão SLSQP 1e-6 e maxiter 100). O cronômetro também abrange a montagem interna do RationConfig.

Convergência, verificação das restrições a 1e-7 e parecer estrito são registrados separadamente. Os pareceres da formulação nativa podem oscilar entre repetições por resíduos muito pequenos. As candidatas são avaliadas sem arredondamento. O JSON preserva reprovações e os vetores que as produziram.

## Cotação observada

O IFAG reportou milho Goiás a R$54,48/saca na semana 09–13/11, em publicação de 17/11. Foi adotada saca de 60 kg e MS do registro 44 como aproximação. Somente o preço do milho é observado no cenário econômico; os demais permanecem demonstrativos. Fonte e limitações estão nos capítulos de dados e referências. [Publicação primária](https://apoiar.sistemafaeg.org.br/milho/%F0%9F%8C%BD-destaques-semanal-do-mercado-do-milho-em-goias-09-11-a-13-11-ifag/)

[Documentação](../../docs/po_rufas/README.md)



## Tabela da rodada arquivada

| Animal | Method | R$/day | MS kg/day | Median s | Approved runs |
|---|---|---:|---:|---:|---|
|98605|A_HiGHS|35.341621|22.231580|0.001492|5/5|
|98605|A_SLSQP|35.341621|22.231580|0.000480|5/5|
|98605|B_SLSQP_native|32.780122|19.623015|0.043852|0/5|
|93785|A_HiGHS|35.247992|22.701315|0.001629|5/5|
|93785|A_SLSQP|35.247992|22.701315|0.000493|5/5|
|93785|B_SLSQP_native|33.394562|21.828456|0.043272|1/5|
