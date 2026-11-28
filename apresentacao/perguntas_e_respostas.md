# Perguntas e respostas — versão vigente

## Qual é a contribuição?
Integrar programação linear sequencial/HiGHS ao ciclo diário FULL_FARM do RuFaS NRC, preservando o LP estático e o método SLSQP original. O exclusivo completou o cenário de 365 dias sem SLSQP.

## Os dois modelos são lineares?
O LP estático tem coeficientes fixos. O dinâmico resolve LPs locais sequenciais sobre funções nutricionais nativas não lineares. Cada LP pode ter ótimo global para sua matriz; isso não certifica ótimo global do problema original.

## Quais são as variáveis e unidades?
Estático: kg MN/animal/dia, preço por kg MN. Contrato dinâmico nativo: kg MS/animal/dia, preço por kg MS; o adaptador converte para o núcleo. As composições %MS são convertidas explicitamente.

## Como se evita parar cedo?
A rotina continua além da primeira aprovação, considera melhoria do custo e viabilidade original, ajusta a região local e conserva a melhor candidata. O orçamento e a estagnação são informados.

## O que significam 959 e 43?
959 formulações atingiram o critério de convergência. Outras 43 conservaram candidatas viáveis sem convergência: 42 por estagnação e uma pelo limite de iterações. Não são apresentadas como ótimos globais.

## A dieta é aplicada à fazenda e ao estoque?
Sim, na simulação anual: Pen aplica a formulação e FeedManager realiza atendimento e baixa física. O LP estático isolado não executa todo o ciclo.

## Como as categorias são tratadas?
Growing usa equações nativas de novilhas; close_up inclui secas/pré-parto; lac_cow usa as funções de lactação. Bezerros usam rotina própria, sem chamada ao otimizador. O agrupamento misto não teve validação anual própria.

## O exclusivo usa fallback?
Não. Em falha, interrompe e registra o motivo. Houve zero SLSQP nas 1.002 formulações HiGHS da evidência anual exclusiva.

## Por que Ca/P têm dois tipos de regra?
Requisitos absorvíveis NRC 2001 são mínimos; tetos NRC 2005 limitam concentração total na MS. Não são a mesma grandeza. A política controlada é igual para ambos os solvers.

## Todos os animais foram aprovados?
Não. Houve 998 curral-dias adultos aprovados no HiGHS e 252 registros de bezerros não aprovados em cada estratégia. Indicadores adultos de FDN/gordura e contratos locais MP/DMI limitam a interpretação desses registros. Não alteramos o avaliador para eliminá-los.

## Qual foi a economia?
Redução de 0,1249355%: SLSQP 2.319,34875854 UM versus HiGHS 2.316,45106770 UM. Preços demonstrativos e cenário específico; não há vantagem econômica universal comprovada.

## Por que o leite foi igual?
O modelo original usa curva de lactação e equações de crescimento que não respondem genericamente a toda mudança de dieta. A oferta participa de outros cálculos, mas os estados iguais observados não provam equivalência fisiológica.

## Como reproduzir?
Instalar na fonte com Python 3.12, constraints-po-rufas.txt, projeto dev e frontend/requirements.txt. Executar exemplos, comparação e annual exclusivo em pasta nova. A reprodução foi feita em cópia sem .git e venv nova. Ver [publicação](../evidencias/publicacao/README.md).

## Quais testes e limites?
969 testes de referência, incluindo o ano exclusivo e frontend real. Não é a suíte inteira do RuFaS nem certificação clínica. Permanecem limitações de coeficientes minerais, resposta produtiva, preços completos, bezerros e generalização de cenários.

## O resultado +9,05% ainda vale?
É histórico, anterior à correção do primeiro dia e da convergência. Foi preservado e explicado; o resultado oficial controlado vigente é redução de 0,1249355%.
