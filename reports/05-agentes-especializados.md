# Fase 7 — Agentes especializados (avaliacao; nenhum criado)

Base: build, plan, reviewer + `explore` nativo, validados. Modelo unico disponivel para todos: `qwen3-coder-30b-a3b` (98k contexto).

| Candidato | 1 Problema | 2 Por que os atuais nao resolvem | 3 Modelo | 4 Ferramentas | 5 Permissoes | 6 Validacao | 7 Custo | Decisao |
|---|---|---|---|---|---|---|---|---|
| Architect | desenho arquitetural | `plan` ja investiga/propoe e tem fluxo de alternativas+riscos | mesmo 30B | read/grep + explore | somente leitura | comparar planos | prompt extra, sobreposicao com plan | **NAO criar** (redundante) |
| Debugger | investigar falhas | `build` roda comandos/testes e corrige; `plan` investiga | mesmo 30B | shell | exigiria shell sem edicao (hoje inexistente) | caso de bug real | agente com shell sem edicao precisa de allowlist fragil | **NAO criar agora**; reavaliar se houver demanda recorrente |
| Tester | estrategia/execucao de testes | `build` executa testes; `plan` define testes | mesmo 30B | shell/edit | igual build | cobertura | sobreposicao | **NAO criar** |
| Researcher | pesquisa tecnica | `webfetch` e `websearch` nativos em plan/build/reviewer; SearXNG MCP ainda sem teste conclusivo | mesmo 30B | webfetch/websearch | somente leitura | consulta com URL/versao verificaveis | contexto + um agente a mais para um modelo que ja ignora instrucoes | **NAO criar**; reavaliar quando Context7/SearXNG estiverem validados |

Criterio aplicado: so criar agente com beneficio comprovavel. Nenhum candidato demonstrou ganho que os tres essenciais + `explore` nao entreguem. Mais agentes tambem aumentam a superficie de delegacao (a brecha `plan -> general` mostra o risco).
