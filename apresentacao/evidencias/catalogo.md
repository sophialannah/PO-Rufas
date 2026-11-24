# Execução: catalogo

Comando: `.\.venv\Scripts\python.exe -X utf8 -m RUFAS.biophysical.animal.ration.linear_diet_catalog --demo --seed 42 --output-dir apresentacao/evidencias/catalogo`

Código de saída: 0; duração: 1.671 s.

```text
Cenario de PL: metas suplementares nao validam exigencias nutricionais completas.
Precos/estoques/NEL: SIMULADOS
Catalogo avaliado: 300; candidatos: 185; excluidos: 115
Vaca: 661.0 kg; DEL 94; leite 28.0 kg/dia
Status: optimal Optimization terminated successfully. (HiGHS Status 7: Optimal)
ID | alimento | kg MN/dia | kg MS/dia | R$/dia
1 | ALFALFA - Meal | 8.5806 | 7.7482 | 7.2423
97 | GRASS-Legume MIXTURES Pr. GR.Â  (17-22% Hcel.) - Silage, mid-maturity | 16.3282 | 7.2661 | 6.5496
164 | SOYBEAN - Meal, expellers | 7.1816 | 6.4347 | 9.7357
Custo minimo do cenario: R$ 23.5276/dia
Totais: {'DM_kg': 21.448992528823947, 'CP_kg': 5.74575279319616, 'NEL_Mcal': 33.24593841967712, 'NDF_kg': 8.579597011529579}
Restricoes atendidas: 375/375
Arquivos: apresentacao\evidencias\catalogo


```
