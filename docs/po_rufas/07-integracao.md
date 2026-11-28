# Integração diária com RuFaS
[Sumário](README.md)

O fluxo dinâmico vigente executa FULL_FARM durante 365 dias, com atualização de requisitos, formulação, operações animais, consumo e baixa de estoque reais. O LP estático permanece um caminho independente que termina na avaliação da dieta, sem realizar sozinho essas operações de fazenda.

## Ciclo e ponto de substituição

SimulationEngine coordena campo, colheitas, planejamento alimentar, animais, atendimento de pedidos, dejetos, relatórios e avanço do tempo. O cenário validado reformula a cada dia. HerdManager configura a instância ration_optimizer de cada Pen; Pen._attempt_formulation chama o método correspondente e aplica seu resultado no contrato nativo em kg MS.

As estratégias são SLSQP controlado, HiGHS híbrido ampliado e HiGHS exclusivo. O exclusivo interrompe em falha, sem SLSQP. Growing usa a seleção nativa de novilhas; close_up inclui vacas secas e novilhas de pré-parto; lac_cow usa as linhas de lactação. O agrupamento misto possui teste de seleção, sem validação anual própria.

## Consumo e estoques

FeedManager calcula disponibilidade, realiza compras e retira os alimentos. O observador diário registra efetivamente fornecido, comprado, inventário e custo. A alocação estática de estoque por animal não é confundida com esse inventário físico dinâmico.

As três execuções controladas iniciaram com os mesmos 26 animais efetivos, semente 42, clima de 2013, alimentos, preços e manejo. As transições de categoria ocorreram no simulador. O exclusivo teve 365 chamadas growing, 272 close_up e 365 lac_cow, totalizando 1.002 aceitas e zero SLSQP.

## Ramo de bezerros

CALF é encaminhado a use_user_defined_ration. CalfRationManager calcula ingestão/requisitos próprios; Pen registra avaliação comum de novilhas. Não há chamada ao otimizador a substituir nesse ramo. Seu funcionamento original não é contado como fallback.

Os 252 curral-dias de bezerros não aprovados ficam separados dos 998 curral-dias adultos aprovados no HiGHS. Há problemas de aplicabilidade e contratos de grandezas nesse relatório comum; [a investigação](05-restricoes.md) não elimina nem oculta as reprovações.

## Oferta e resposta biológica

Pen transfere nutrition_supply para previous_nutrition_supply e calcula a oferta nova. Animal utiliza dados da dieta anterior em cálculos subsequentes; digestão/excreção também recebem oferta. Entretanto, a curva de Wood recebe DEL e parâmetros de lactação, e as equações de crescimento usam metas e estado fisiológico. Dietas diferentes não implicam automaticamente leite/peso diferentes nessa implementação.

O leite e os estados biológicos registrados iguais nas estratégias foram observados. O modelo não foi alterado para criar diferenças. Isso limita a interpretação de equivalência biológica, mesmo com integração operacional comprovada.
