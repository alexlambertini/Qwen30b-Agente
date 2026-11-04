# ADR-0002: Plan e Reviewer so delegam ao explore
- **Identificador:** ADR-0002-task-somente-explore
- **Data:** 2026-11-04
- **Status:** aprovada

## Contexto
Teste real: Plan delegou ao `general` e o arquivo foi criado (brecha).
## Decisao
`permission.task = {"*":"deny","explore":"allow"}` em plan e reviewer; `explore` com edit deny e bash so de leitura.
## Consequencias
T11/T12 bloqueados (`Permission denied: subagent`). Qualquer agente novo precisa de teste de delegacao.
