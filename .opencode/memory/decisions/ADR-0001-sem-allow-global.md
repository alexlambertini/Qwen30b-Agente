# ADR-0001: sem allow global de edit/bash
- **Identificador:** ADR-0001-sem-allow-global
- **Data:** 2026-11-04
- **Status:** aprovada

## Contexto
Em `opencode debug agents` a regra global `allow edit *` aparece DEPOIS do `deny edit *` do plan nativo.
## Alternativas
1. Manter allow global e confiar no prompt. 2. Remover allow global e declarar restricoes por agente.
## Decisao
Opcao 2: global so com ask/deny perigosos (ssh, scp, sudo, git push, rm -rf).
## Consequencias
Plan/reviewer/explore dependem de regras proprias (testadas em T1-T13).
