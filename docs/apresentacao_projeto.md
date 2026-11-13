# Roteiro de apresentação do PO-Rufas

[Voltar ao README](../README.md) · [Documentação técnica](otimizador_linear.md)

## 1. Explique a contribuição

“O RuFaS já simula fazendas leiteiras e possui formulação não linear de rações.
Meu trabalho acrescenta uma alternativa de programação linear, com custo mínimo,
estoques, restrições explícitas e verificação dos resultados.”

Mostre `linear_diet.py`: `Ingredient`, `AnimalProfile`, `DietRequirements` e `optimize_diet`.
As quantidades são as variáveis de decisão; o custo diário é a função objetivo.

## 2. Apresente as entradas e unidades

Mostre `linear_diet_example.py` para explicar uma lista de três ingredientes e um perfil
animal. Depois mostre `linear_diet_catalog.py` para explicar a ampliação automática.

Distinga matéria natural de matéria seca. A composição vem das tabelas do RuFaS;
preços, estoques e NEL dos exemplos são demonstrativos. Somente a estimativa de consumo
de MS é importada diretamente das exigências do calculador NRC nesses exemplos.

## 3. Execute a busca no catálogo

Na raiz do projeto, no PowerShell:

```powershell
.\.venv\Scripts\python.exe -m RUFAS.biophysical.animal.ration.linear_diet_catalog --demo --seed 42
```

Mostre no terminal o perfil da vaca, os 300 registros avaliados, os 185 candidatos,
os ingredientes escolhidos, o custo e as 375 verificações satisfeitas.

Abra `output/catalog_diet/result.json`. Explique os campos:

| Campo | O que demonstrar |
|---|---|
| `animal` | Perfil e metas do cenário |
| `catalog_audit` | Todos os registros e motivos das exclusões |
| `ingredients` | Composição, parâmetros e origem |
| `result.quantities_kg_day` | Quantidades em matéria natural, inclusive zeros |
| `result.ration_kg_dm_day` | Quantidades em matéria seca para integração |
| `result.checks` | Atendimento de cada restrição |

“O solver escolheu as quantidades entre todos os candidatos. Não escolhemos os três
alimentos finais previamente. O mínimo encontrado vale para este cenário e suas hipóteses.”

## 4. Mostre a integração e a validação

Abra `linear_diet_adapter.py`: ele recebe objetos RuFaS e converte unidades.
O resultado é compatível com as estruturas de rações, mas não é aplicado automaticamente
à simulação diária. A integração completa ainda é uma etapa futura.

Execute os testes específicos:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_biophysical/test_animal/test_ration/test_linear_diet.py tests/test_biophysical/test_animal/test_ration/test_linear_diet_catalog.py -q
```

Há testes de solução conhecida, conversões, estoques, inviabilidade, falsa solução ótima,
integração com objetos reais, auditoria e reprodutibilidade.

## 5. Delimite a conclusão

A entrega demonstra formulação matemática, execução e integração de dados.
Não demonstra uma recomendação alimentar pronta, lucro máximo ou economia observada.
As dietas dos exemplos usam parâmetros diferentes: comparar apenas seus custos não
é uma avaliação econômica controlada.

Para avançar, substitua as hipóteses por parâmetros documentados, complemente as restrições
nutricionais e reavalie a oferta com o modelo completo do RuFaS. Depois compare cenários
mantendo o animal e os demais parâmetros iguais.
