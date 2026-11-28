# Apresentação acadêmica vigente — PO-RuFaS

**Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.** Quatro slides, cinco minutos de exposição/demonstração e cinco minutos adicionais de perguntas.

O tema central é a integração dinâmica de 365 dias, com programação linear sequencial no RuFaS NRC. O LP estático de coeficientes fixos continua como exemplo e estudo complementar. A aplicação já realiza o ciclo diário e a baixa real de estoque.

## Material vigente

- [PowerPoint final](apresentacao_po_rufas_final.pptx).
- [Roteiro completo e cronograma](roteiro_completo.md).
- [Fala de Sophia](roteiro_sophia.md) e [fala de Anderson](roteiro_anderson.md).
- [Guia da demonstração web](guia_demonstracao_web.md) e [alternativa terminal](guia_demonstracao.md).
- [Resultados oficiais](resultados_validados.md), [cartões](cartoes_consulta.md), [perguntas](perguntas_e_respostas.md), [arguição](simulacao_arguicao.md) e [checklist](checklist_apresentacao.md).

## Números para apresentar

365 dias; SLSQP controlado 2.319,34875854 UM; HiGHS exclusivo 2.316,45106770 UM; redução demonstrativa 0,1249355%; leite 140.223,666523 kg em ambos; 1.002 formulações HiGHS e zero SLSQP no exclusivo; 959 convergentes e 43 viáveis sem convergência; 998 curral-dias adultos aprovados; 954 testes.

Sempre informar os **252 curral-dias de bezerros não aprovados em cada estratégia** e as limitações dos indicadores comuns. Não dizer que todo o rebanho foi aprovado, que o ótimo não linear é global ou que há vantagem econômica universal.

## Executar e gerar

Na raiz: `frontend/iniciar_frontend.bat`. Na área anual, escolher Comparação SLSQP versus HiGHS exclusivo. Uma execução curta ao vivo deve ser identificada como curta; o resultado oficial de 365 dias vem das evidências já registradas.

Para gerar novamente o deck final, instale as dependências opcionais e escolha um nome novo:

```powershell
.\.venv\Scripts\python.exe -m pip install -c constraints-po-rufas.txt -r apresentacao/requirements.in
.\.venv\Scripts\python.exe -m apresentacao.gerar_versao_final --output output/apresentacao_revisada.pptx
```

Os arquivos apresentacao_rufas_5min.pptx/.pdf, geradores antigos e prévias são **históricos**, preservados sem representar a versão vigente. Não execute os geradores históricos para recriar estes novos roteiros. As cópias textuais anteriores estão no [manifesto documental](../evidencias/publicacao/historico_documental/manifesto.json).

[Manual completo](../docs/po_rufas/12-manual.md) · [Evidências oficiais](../evidencias/correcao_dinamica/README.md) · [Preparação para publicação](../evidencias/publicacao/README.md).
