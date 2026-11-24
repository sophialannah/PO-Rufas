# Demonstração ao vivo — 85 segundos

**Integrantes:** Sophia Lannah Beatriz Ferreira de Sousa e Anderson Alberto da Costa Silva.

## Comando principal

No PowerShell do Antigravity, a partir da raiz do projeto:

```powershell
.\apresentacao\demonstracao_solver.bat
```

Alternativa direta:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m apresentacao.demo_solver
```

O BAT localiza a raiz a partir de sua própria pasta e usa `.venv\Scripts\python.exe`.
Execute no terminal já aberto, não por duplo clique: assim a saída permanece visível.
Não execute `activate_this.py` nem edite arquivos dentro da `.venv`.
O ambiente deve estar preparado antes da aula; não faça instalações durante os cinco minutos.

## Preparação antes de iniciar o cronômetro

1. Abra o PowerPoint no slide 1 e deixe o terminal como única outra janela da demonstração.
2. Amplie o terminal, aumente a fonte e use pelo menos 100 colunas e cerca de 32 linhas visíveis.
3. Execute uma vez ` .\apresentacao\demonstracao_solver.bat --auto` para aquecer os imports e validar o ambiente.
4. Execute novamente sem `--auto`. O programa mostra as entradas e espera Enter **antes de chamar o solver**.
5. Volte aos slides. Ao terminar o slide 3, use Alt+Tab; as entradas já estarão na tela.

Preparar as entradas antes da contagem não pré-calcula a solução: `optimize_diet` é chamado somente após Enter.

## Divisão da fala

| Relógio geral | Ação |
|---|---|
| 03:00–03:35 | Sophia mostra o perfil, os três ingredientes, preços, estoques e metas. Pressiona Enter. |
| 03:35–04:25 | Anderson explica as quantidades, custo e 11/11 verificações. |
| 04:25 | Alt+Tab para os slides; avançar ao slide 4. |

Transição: “Vou executar o solver agora. Anderson, explique o resultado.”
Resultado esperado: `optimal`, custo aproximado de R$ 34,9978/dia; todos os checks verdadeiros.
A soma usa quantidades completas; a tabela arredonda apenas para apresentação.

## O que é real e o que é ilustrativo

O programa executa o solver real; não lê uma dieta pronta do JSON. Reutiliza `example_inputs()` e
`optimize_diet()` existentes. A composição vem da biblioteca NRC do RuFaS e a MS do seu calculador NRC.
Os preços, estoques, NEL por ingrediente e metas suplementares são didáticos. Minerais opcionais não são ativados.
A demonstração recebe um perfil, não instancia nem executa uma fazenda inteira.

## Registro e contingência

Cada execução grava `apresentacao/evidencias/demo_resultado.json` e substitui o registro anterior.
O registro consolidado usado para criar os slides fica em `apresentacao/evidencias/base_slides.json`.

Se houver falha, não tente depurar durante a fala. Informe que a execução ao vivo falhou,
retorne ao slide 4 e identifique o resultado como **execução previamente validada**.
`evidencias/demo_terminal.md` guarda a saída real anterior. Não a apresente como uma execução ao vivo.
Se o PowerPoint não abrir, use `apresentacao_rufas_5min.pdf`, quando disponível, ou as prévias PNG.
Não acrescente uma segunda demo ou uma instalação ao cronograma.

## Dependências

Para a demo: as dependências originais do projeto e Python 3.12 ou 3.13.
Para recriar o PowerPoint: `python-pptx==1.0.2` (instalado apenas no ambiente de preparação).
Não é necessário python-pptx no computador que apenas abrirá o PPTX.
