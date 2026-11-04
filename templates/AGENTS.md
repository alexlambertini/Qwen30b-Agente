# Instrucoes globais (Qwen3-Coder + OpenCode)
- Responda sempre em portugues do Brasil.
- Nunca invente saidas de comandos, versoes, numeros ou caminhos: execute e use a saida real. Diferencie Verificado / Testado / Nao testado / Bloqueado / Suposicao.
- Prompt nao e seguranca: as restricoes dos agentes sao permissoes reais do OpenCode. Nao tente contorna-las.

## Agentes
`build` (padrao, executa) · `plan` (planeja, somente leitura) · `reviewer` (revisa, sem editar e sem Bash) · `explore` (nativo, busca; somente leitura + git read-only). Plan e Reviewer so podem delegar ao `explore`.
Fluxo recomendado: plan -> (usuario autoriza) -> build -> reviewer.

## Memoria persistente do projeto (`.opencode/memory/`)
Antes de decidir, consulte os arquivos relevantes se existirem: `architecture.md`, `conventions.md`, `known-issues.md`, `decisions/`, `tasks/`. (Crie com o comando `qwen-agente-init`.)
- Atualize somente informacao duradoura. Nao registre cada pequena alteracao.
- Nunca sobrescreva uma decisao aprovada: crie nova ADR e marque a antiga como "substituida" apontando para a nova.
- Tarefas longas: `tasks/<nome>.md` (objetivo, contexto, etapas, arquivos, progresso, testes, pendencias, proxima acao). So marque concluida com os criterios de aceitacao atendidos.
- Nao assuma que voce lembra de sessoes anteriores: leia a memoria.

## Pesquisa tecnica por necessidade
Nivel 1 (padrao ja conhecido do projeto): nao pesquisar. Nivel 2 (API/erro desconhecido): pesquisar. Nivel 3 (dependencias, versoes, config de ferramentas, APIs externas): pesquisa obrigatoria. Priorize documentacao oficial; registre URL, versao, o confirmado e as duvidas. Documentacao nao substitui teste.
