# Memoria do projeto (`.opencode/memory/`)
Fonte de verdade para agentes entre sessoes. Curta, atual e verificavel.
| Arquivo | Conteudo | Quem atualiza |
|---|---|---|
| architecture.md | visao geral, componentes, fluxos, dependencias | build (apos mudanca estrutural) |
| conventions.md | padroes de codigo, nomes, testes, regras | build/usuario |
| known-issues.md | problemas, limitacoes, workarounds, riscos | build/reviewer (via build) |
| decisions/ADR-NNNN-*.md | uma decisao por arquivo (nunca apagar) | build apos aprovacao |
| tasks/<nome>.md | estado de tarefas longas | build, a cada etapa |
Regras: registrar so o duradouro; remover o que ficou falso; citar arquivo/comando que comprova; marcar "Suposicao" quando nao verificado.
