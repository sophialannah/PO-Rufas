# Execução: demo_terminal

Comando: `.\.venv\Scripts\python.exe -X utf8 -m apresentacao.demo_solver --auto`

Código de saída: 0; duração: 1.638 s.

```text
PO-RUFAS | DEMONSTRAÇÃO REAL DO SOLVER | 1 vaca, dieta diária por 7 dias
Composição: biblioteca RuFaS. Preços, estoques, NEL e metas PB/FDN: ilustrativos.
Vaca: 650 kg | DEL 100 | leite 30 kg/dia
Leite: gordura 3.8% | proteína verdadeira 3.2%
MN = matéria natural; MS = matéria seca; PB = proteína bruta; FDN = fibra.
ENTRADAS                 R$/kg MN  Estoque kg MN  Máx. kg MN/dia
Alfafa (farinha)           1.2642       166.1130         17.7187
Milho (moagem media)       1.5858       113.5074         11.3507
Farelo de soja             2.5060        67.0391          6.7039
MS = 22.5453 kg/dia (RuFaS/NRC); PB >= 3.6 kg/dia;
NEL >= 35.0 Mcal/dia; FDN = 28–40% da MS; inclusões mínimas = zero.

RESULTADO CALCULADO AGORA: optimal | scipy.optimize.linprog(method='highs')
Ingrediente                kg MN/dia   kg MS/dia      R$/dia
Alfafa (farinha)             15.9119     14.3685     20.1158
Milho (moagem media)          9.0957      8.0133     14.4239
Farelo de soja                0.1828      0.1636      0.4580
CUSTO MÍNIMO DO CENÁRIO: R$ 34.9978/dia
MS 22.5453 kg | PB 3.6000 kg | NEL 35.0000 Mcal
FDN 6.7546 kg = 29.96% da MS
11/11 verificações OK: nutrientes, inclusão e estoques.
Custo reconferido por soma preço × quantidade. Chamada do solver: 0.004 s.
Ótimo deste modelo demonstrativo; não é validação nutricional completa.
Registro completo: apresentacao/evidencias/demo_resultado.json


```
