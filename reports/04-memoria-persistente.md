# Fase 6 — Memoria persistente

## Estrutura (adaptada ao que a v2.1.4 suporta)
`.opencode/memory/` no PROJETO (criada por `qwen-agente-init`, a partir de `~/.config/opencode/memory-template/`):
`README.md`, `architecture.md`, `conventions.md`, `known-issues.md`, `decisions/_TEMPLATE.md`, `tasks/_TEMPLATE.md`.
Agentes/prompts/skills/commands NAO foram duplicados por projeto: prompts ficam globais em `~/.config/opencode/prompts/`. `skills/` e `commands/` nao foram criados (nenhum beneficio comprovado; schema tem as chaves `skills`/`commands`, nao testadas).

## Como os agentes usam a memoria
1. **Carga automatica**: `opencode.json` tem `instructions: [.opencode/memory/architecture.md, conventions.md, known-issues.md]`. Teste: Plan respondeu corretamente (pytest, `python3 -m pytest -q`, ValueError) SOMENTE com o conteudo carregado, sem abrir o arquivo -> **PASS**. Projeto sem memoria: nao quebra -> **PASS**. (Antes disso, so com o prompt mandando ler, o Plan **ignorou** `conventions.md` — por isso a carga automatica.)
2. `decisions/` e `tasks/` NAO sao carregados automaticamente (crescem); os prompts mandam consultar quando relevante. O modelo pode esquecer -> risco registrado.
3. Regras no `AGENTS.md` global e `memory/README.md`: registrar so o duradouro; nunca sobrescrever ADR aprovada (criar nova e marcar a antiga "substituida"); nao assumir memoria entre sessoes.

## Cenario E (recuperacao de contexto)
Tarefa `tasks/migracao.md` com "Codigo de retomada = ZEBRA-4417". Sessao NOVA do build leu o arquivo, gravou `resultado.txt` = `ZEBRA-4417` e marcou "Status: concluida" -> **PASS**. Ressalva: o modelo fez voltas desnecessarias (worktree/git init) antes de ler a tarefa.

## Dogfood
O proprio repositorio tem `.opencode/memory/` preenchida (arquitetura, convencoes, problemas conhecidos, ADR-0001..0004).

## Limitacoes
- Checklist nativo `todowrite`: aparece no binario, mas NAO esta exposto ao modelo (ele informou que nao esta no catalogo) -> continuidade apenas por `tasks/*.md` com `- [ ]`/`- [x]`.
- Nao ha compactacao de memoria automatica; a curadoria e responsabilidade do build/usuario.
