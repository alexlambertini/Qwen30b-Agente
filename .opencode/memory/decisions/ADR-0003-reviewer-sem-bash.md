# ADR-0003: Reviewer sem Bash; diff via explore
- **Identificador:** ADR-0003-reviewer-sem-bash
- **Data:** 2026-11-04
- **Status:** aprovada

## Contexto
Requisito: Reviewer nao executa Bash, mas precisa de diff/historico.
## Decisao
Reviewer sem bash; usa `explore` (allowlist git status/log/diff/show/blame) como unico canal.
## Consequencias
Risco KI-002: o modelo nem sempre chama o explore.
