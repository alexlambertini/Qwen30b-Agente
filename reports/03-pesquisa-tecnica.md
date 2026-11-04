# Fase 5 — Sistema de pesquisa tecnica (2026-11-04, OpenCode v2.1.4 em `ia`)

## Inventario (verificado antes de decidir)
| Ferramenta | Existe? | Teste real | Resultado |
|---|---|---|---|
| `webfetch` nativo | sim | build buscou `https://registry.npmjs.org/mcp-searxng/latest` | **PASS** — retornou JSON do registro; versao `2.10.0` (confere com `npm view mcp-searxng version` = 2.10.0) |
| `websearch` nativo | sim (chave `websearch` no schema; ferramenta chamada pelo modelo) | consulta "mcp-searxng npm" | **PASS** — resultados reais; 1a URL `https://www.npmjs.com/package/@tobioffice/mcp-searxng`. Observacao: e um pacote DIFERENTE de `mcp-searxng` (nao confundir); servico externo |
| SearXNG (container) | sim, porta 8888 | `/search?format=json` | **PASS agora** (10 resultados, 0 engines com falha). Antes (mesmo dia) 0 resultados e engines em timeout -> **instavel** |
| MCP `mcp-searxng` | sim (npm 2.10.0, nao deprecado) | carregado via instalador `--searxng` | inicia e o modelo enxerga `searxng_web_search` e `web_url_read`; **resultado da busca via MCP nao confirmado** (retorno `null` em 2 tentativas) -> **NOT TESTED (conclusivo)** |
| `opencode mcp list` | existe | `✗ searxng failed: Request timed out` na config antiga (1a execucao, `npx -y` a frio) | **FAIL** (com config global antiga). Na config isolada: "No MCP servers configured" (o comando fala com o servico em segundo plano, nao com a config isolada) |

## Decisao
- Nao foi criado agente Researcher: `webfetch` + `websearch` nativos cobrem; Plan/Build/Reviewer ja tem as regras dos 3 niveis de pesquisa nos prompts. Ver `05-agentes-especializados.md`.
- SearXNG fica **opcional** no instalador (`--searxng URL`). Nao recomendado como unica fonte enquanto nao houver teste conclusivo.
- Nenhuma ferramenta nova instalada. Proximos candidatos (Context7, LSP etc.) em `06-inventario-ferramentas.md`, aguardando autorizacao.

## Regra de pesquisa (implementada nos prompts)
Nivel 1: nao pesquisar · Nivel 2: pesquisar fonte oficial · Nivel 3 (dependencias, versoes, config de ferramentas, APIs externas): obrigatorio, registrando URL, versao, confirmado e duvidas.
Cenario D (pesquisa de versao): PASS — o build consultou o registro e citou URL e versao reais. Limite: nao ha teste de que o modelo SEMPRE pesquisa no Nivel 3 (o 30B ignora instrucoes as vezes).
