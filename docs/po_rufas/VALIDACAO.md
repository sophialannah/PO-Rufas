# Validação vigente e histórico

Base Git 5bb6775, branch fix/validacao-nutricional-rufas, com alterações locais identificadas nos manifestos. Documentação consolidada em 27/11/2026.

## Estado oficial

**954 testes aprovados**, preservando os 937 anteriores e acrescentando 17 regressões da correção dinâmica. [Comando e cobertura](11-testes.md). Os XML oficiais [testes_finais](../../evidencias/correcao_dinamica/testes_finais.xml) e [testes_verificacao](../../evidencias/correcao_dinamica/testes_verificacao.xml) permanecem preservados.

O cenário controlado executou 365 dias nas três estratégias. A exclusiva registrou 1.002 chamadas HiGHS, zero SLSQP/fallback, 959 formulações convergentes e 43 soluções viáveis sem convergência. Os 998 curral-dias adultos passaram na avaliação nativa e nos tetos totais Ca/P do HiGHS.

SLSQP: 2.319,34875854 UM; HiGHS exclusivo: 2.316,45106770 UM; redução de 0,1249355%. Leite: 140.223,666523 kg em ambos. Preços demonstrativos; sem certificado de ótimo global ou superioridade econômica universal.

## Escopo dos bezerros

Cada estratégia tem 252 curral-dias de bezerros não aprovados. A auditoria reconfirmou FDN total, FDN de forragem, gordura e também MP/DMI entre os campos não aprovados. Há limitações da aplicação de indicadores comuns de novilhas à rotina láctea e inconsistências de grandezas no contrato local. [Investigação](05-restricoes.md) e [auditoria estruturada](../../evidencias/publicacao/bezerros_auditoria.json).

Nenhuma reprovação foi ocultada ou transformada em aprovação. A contagem adulta não representa 100% de adequação nutricional do rebanho.

## Reprodução para publicação

O [relatório de publicação](../../evidencias/publicacao/README.md) registra o inventário candidato, exclusões, dependências, reprodução em diretório isolado sem .git, comandos, testes e capturas finais. As mudanças desta etapa são documentais, seleção/comparação no frontend e tolerância da proveniência à ausência de metadados Git; o solver não foi reformulado.

A comparação exclusiva no frontend é exercitada por processos reais, incluindo ausência de SLSQP. A nova venv da cópia isolada não reutiliza os pacotes da venv original.

## Histórico preservado

| Etapa | Resultado registrado | Origem |
|---|---|---|
| Gordura/indicadores e documentação inicial | 462 testes | Primeira documentação técnica |
| Experimento A/B | 466 testes | evidencias/comparacao |
| Primeira integração anual híbrida | 937 testes; aumento de custo de 9,05% | evidencias/anual |
| Correção de formulação/convergência | 954 testes; redução de 0,1249355% | evidencias/correcao_dinamica |

O aumento histórico concentrado no primeiro dia foi corrigido sem excluir o dia. Falhas intermediárias, arquivos antigos e suas avaliações foram preservados. As cópias documentais pré-consolidação estão em [manifesto histórico](../../evidencias/publicacao/historico_documental/manifesto.json).

Os tempos 128,87 s e 11.233,60 s das duas rodadas de 954 não são comparados como benchmark. A checagem direcionada de 206 testes é sobreposta, sem somá-la à contagem oficial. A validação computacional não substitui validação nutricional, produtiva e econômica externa.
