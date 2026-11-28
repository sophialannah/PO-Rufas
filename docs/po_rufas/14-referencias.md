# Referências, autoria e glossário
[Sumário](README.md)

## Fontes científicas e computacionais

- **NRC 2001. Nutrient Requirements of Dairy Cattle**, 7ª edição. [DOI 10.17226/9825](https://doi.org/10.17226/9825). Base declarada do modo NRC; consumo, energia, proteína, minerais e capítulo 10 específico de bezerros. A implementação local não equivale à conferência integral de todas as equações do livro.
- **NRC 2005. Mineral Tolerance of Animals**, 2ª edição. [Publicação e DOI 10.17226/11309](https://www.nationalacademies.org/publications/11309). Origem dos tetos de tolerância total Ca/P; não são metas de consumo.
- **NASEM 2021. Nutrient Requirements of Dairy Cattle**, 8ª edição. [DOI 10.17226/25806](https://doi.org/10.17226/25806); [Minerals](https://www.ncbi.nlm.nih.gov/books/NBK600600/) e [Nutrient Requirements of the Young Calf](https://www.ncbi.nlm.nih.gov/books/NBK600606/). O capítulo de bezerros distingue fases de desenvolvimento e fontes alimentares. Foi consultado como contexto científico para a aplicabilidade dos indicadores, sem substituir equações NRC por NASEM nesta revisão.
- **SciPy**, documentação oficial: [linprog/HiGHS](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html) e [minimize/SLSQP](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html).
- **RuFaS**, [código original](https://github.com/RuminantFarmSystems/RuFaS) e [documentação](https://ruminantfarmsystems.github.io/RuFaS/). Os contratos executados foram inspecionados em SimulationEngine, HerdManager, Pen, CalfRationManager, Animal e NutritionEvaluator.

## Bases econômicas parciais

- [CEPEA, indicador de milho](https://cepea.org.br/br/indicador/milho.aspx), valor datado de 04/09/2026: 70,93 R$/saca de 60 kg; licença CEPEA CC BY-NC 4.0. Conversões e lacunas no cenário comercial parcial da correção.
- [IFAG, semana 09–13/11/2026](https://apoiar.sistemafaeg.org.br/milho/%F0%9F%8C%BD-destaques-semanal-do-mercado-do-milho-em-goias-09-11-a-13-11-ifag/), publicação de 17/11/2026, 54,48 R$/saca. Pertence ao experimento estático parcial anterior, separado dos preços anuais.

Essas cotações não cobrem todos os alimentos, frete, processamento e volumosos. A redução oficial de 0,1249355% usa preços demonstrativos, não um orçamento comercial completo.

## Autoria, licença e proveniência

A contribuição acadêmica é de Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva. Os modelos, bibliotecas e simulador originais permanecem atribuídos aos autores RuFaS.

O projeto declara GPL-3.0-only em pyproject.toml. [COPYING.txt](../../COPYING.txt) e [COPYING.LESSER.txt](../../COPYING.LESSER.txt) foram recuperados da revisão candidata [d471c742](https://github.com/RuminantFarmSystems/RuFaS/tree/d471c742eadc2e37b76545d0d0f0d10b6c9ef763), com hashes de blobs conferidos. Há alta correspondência com a importação inicial, sem prova de ancestralidade exata. [FORKING.md](../../FORKING.md) · [Documentação original](../README_RuFaS_original.md).

Outros ausentes upstream foram inspecionados e mantidos como cópias de auditoria, sem instalar CI ou código arbitrariamente. A organização externa consultada no histórico não transfere autoria. As referências científicas não fornecem certificação automática de dietas ou do código.

## Glossário

| Sigla | Significado |
|---|---|
| PO / LP / PL | Pesquisa Operacional / programação linear |
| SLP | Programação linear sequencial |
| NRC / NASEM | Organizações das referências nutricionais |
| MN / MS / DMI | Matéria natural / matéria seca / ingestão de MS |
| PB / CP / MP | Proteína bruta / crude protein / proteína metabolizável |
| FDN / NDF | Fibra em detergente neutro |
| NEL / DE / ME | Energia líquida de lactação / digestível / metabolizável |
| EE / DEL | Extrato etéreo / dias em lactação |
| Ca / P / p.p. | Cálcio / fósforo / pontos percentuais |
| MTL | Maximum tolerable level, teto de tolerância |
| UM | Unidade monetária demonstrativa do cenário anual |
| SLSQP | Sequential Least Squares Programming |
