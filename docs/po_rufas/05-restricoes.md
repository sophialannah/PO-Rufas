# Restrições, parecer nutricional e bezerros
[Sumário](README.md)

A versão vigente distingue checks matemáticos do LP, viabilidade das funções nativas e aprovação do NutritionEvaluator. Um status de solver não substitui os outros resultados.

## Estático versus dinâmico

| Critério | LP estático | Modelo dinâmico NRC |
|---|---|---|
| MS | Consumo fixado na integração | Faixa nativa da categoria |
| Proteína | PB mínima externa | MP inferior/superior nativas |
| Energia | NEL fixa externa | Funções nativas de energia selecionadas por categoria |
| FDN total | Faixa externa | Limites nativos |
| FDN de forragem/gordura | Avaliação posterior | Restrições nativas |
| Ca/P absorvíveis | Mínimos opcionais | Mínimos nativos recalculados |
| Ca/P totais máximos | Não acrescentados automaticamente ao LP estático | Política explícita NRC 2005 igualmente aplicada aos solvers controlados |
| Estoque | Alocação por horizonte | Limites de formulação e gestão física pelo FeedManager |

O avaliador usa deltas não negativos para mínimos, zero quando MP/FDN/MS ficam na faixa e margem de gordura máxima ≥−10⁻⁹ p.p. A correção histórica de gordura deixou de exigir igualdade ao máximo; não se alteraram os dados para obter aprovação.

As candidatas dinâmicas são verificadas após arredondamento de seis casas, igual ao Pen, exigindo resíduos não negativos nas funções originais. A margem matemática de arredondamento não modifica a oferta nutricional. O SLSQP pode convergir e reprovar por resíduos muito pequenos; eles continuam registrados.

## Bezerros: contagem e aplicabilidade

A auditoria dos três diários oficiais encontrou **252 curral-dias de bezerros, todos não aprovados, em cada estratégia**. As contagens de campos não aprovados são:

| Campo do relatório comum | Ocorrências por estratégia |
|---|---:|
| FDN total | 252 |
| FDN de forragem | 252 |
| Gordura | 252 |
| Proteína metabolizável | 252 |
| Matéria seca | 252 |

Um curral-dia pode reprovar em vários campos; não se somam essas ocorrências como novos dias. [JSON e CSV da auditoria](../../evidencias/publicacao/bezerros_auditoria.json).

O HerdManager encaminha CALF a use_user_defined_ration, sem chamar RationOptimizer. Há dois níveis: CalfRationManager estima ingestão e requisitos individuais de leite/concentrado inicial; o Pen aplica a ração prescrita para o curral e a submete à avaliação comum de novilhas.

FDN mínima adulta e FDN mínima de forragem não devem ser transplantadas automaticamente à dieta total de leite/concentrado de um pré-ruminante. A concentração de gordura da alimentação láctea também não tem a mesma interpretação do teto adulto de extrato etéreo. NRC 2001 possui um capítulo próprio para bezerros, e a referência científica diferencia fases de desenvolvimento e fontes de alimento.

Isso **não transforma os registros em aprovados**. No primeiro dia, o diário tem MS=3 kg, FDN fornecida=0 e gordura=0,507 kg, ou 16,9% MS; os deltas são −25 p.p. FDN total, −15 p.p. FDN de forragem e −9,9 p.p. de margem de gordura. O zero de FDN é saída dos dados/cálculos locais, não prova de ausência física de fibra em todo produto comercial.

Há ainda inconsistências que exigem auditoria própria: o construtor de NutritionRequirements do ramo CALF atribui calf_intake["me_intake"] ao campo metabolizable_protein, enquanto o avaliador espera uma grandeza proteica; os requisitos Ca/P são zeros com TODO nativo. A DMI estimada individualmente também difere da ração prescrita de 3 kg MS. Esses contratos não permitem interpretar o parecer comum como certificação específica de bezerros.

Nenhum avaliador, limiar ou dieta de bezerro foi alterado nesta preparação. A conclusão correta é: **998 curral-dias adultos aprovados no HiGHS, com 252 registros de bezerros não aprovados e escopo científico limitado**, sem aprovação de todo o rebanho. [Fontes](14-referencias.md) · [Integração](07-integracao.md).
