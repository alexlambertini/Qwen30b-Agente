# ADR-0004: memoria carregada via instructions
- **Identificador:** ADR-0004-memoria-via-instructions
- **Data:** 2026-11-04
- **Status:** aprovada

## Contexto
O Plan ignorou `conventions.md` quando so o prompt mandava ler.
## Decisao
`instructions` carrega architecture, conventions e known-issues automaticamente; decisions/tasks sob demanda.
## Consequencias
Arquivos grandes consomem contexto fixo: manter curtos.
