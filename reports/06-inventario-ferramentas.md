# Modulo adicional — inventario de ferramentas (somente leitura)

Data: 2026-11-04 · Maquina inspecionada: `ia` (OpenCode v2.1.4, node v26.13, npm 11.20, Docker 29.8.1, 4 CPU / 7,5 GiB RAM).
**Nada foi instalado nem alterado.** Este documento e a tabela de decisao; aguarda autorizacao.

## Evidencias coletadas
| Item | Evidencia |
|---|---|
| Schema v2.1.4 (`https://opencode.ai/config.json`) | tem chaves `lsp` (bool ou objeto: "Enable built-in language servers or configure server overrides"), `mcp` (com `timeout.startup/catalog/execution`), `websearch`, `skills`, `commands`, `tools`, `formatter`, `instructions` |
| Ferramentas nativas ja usadas com sucesso | `read`, `glob`, `grep`, `edit`, `write`, `shell`, `webfetch`, `subagent`, `question`, `execute`; **`websearch` nativo** retornou resultados reais (primeira URL: npmjs.com/@tobioffice/mcp-searxng) |
| `todowrite` | existe no binario, mas o modelo informou que nao esta no catalogo e se recusou a chamar -> **nao exposto** |
| SearXNG (MCP, ja configurado) | container up; agora 10 resultados e rede ok no container (antes: timeout de engines -> **instavel**). MCP carrega e expoe `searxng_web_search` (visto na saida do modelo); o resultado da busca via MCP veio `null` em 2 tentativas -> **uso nao confirmado** |
| Servidores LSP no PATH | pyright-langserver, typescript-language-server, gopls, rust-analyzer, clangd, jdtls: **todos ausentes** |
| Semgrep | ausente (CLI e imagem Docker) |
| Playwright / navegador | ausente (`~/.cache/ms-playwright` nao existe; sem chromium/chrome) |
| Docker | 29.8.1 funcionando; usuario esta no grupo `docker` (**equivale a root no host**) |
| npm | `@upstash/context7-mcp` 4.5.0 · `@playwright/mcp` 0.0.84 · `@modelcontextprotocol/server-github` 2025.4.8 **DEPRECADO** ("no longer supported") |
| Rede | `mcp.context7.com/mcp` responde 405 a GET (endpoint existe); `api.githubcopilot.com/mcp/` responde 401 (exige autenticacao) |

## Tabela de decisao
Consumo de contexto: **NAO MEDIDO** (exige instalar; sem isso qualquer numero seria suposicao). Contexto do modelo = 98.304 tokens, e cada MCP adiciona o schema de todas as suas ferramentas a cada requisicao; o modelo ja usa ~5-6 mil tokens so de base.

| Ferramenta | Problema que resolve | Beneficio esperado | Compatibilidade | Contexto | Permissoes necessarias | Prioridade | Decisao recomendada |
|---|---|---|---|---|---|---|---|
| **websearch nativo** | busca web geral | ja funciona, zero instalacao | Verificado (v2.1.4) | baixo (ferramenta nativa) | allow para build/plan/reviewer (somente leitura) | alta | **Usar ja** (nada a instalar). Obs.: a consulta sai para um servico externo — nao enviar segredos |
| **SearXNG (MCP)** | busca privada/auto-hospedada | independente de terceiros | Verificado que inicia; **uso nao confirmado**; engines ja falharam antes | medio (3 ferramentas) | somente leitura | media | **Manter opcional** (ja e opcional no instalador). Antes: confirmar um resultado real via MCP e estabilizar engines |
| **LSP nativo** | definicoes, referencias, diagnosticos | revisao e planejamento mais precisos que grep | Config `lsp` existe no schema; **servidores nao instalados**; comportamento nao testado | baixo/medio | leitura (Plan/Reviewer podem usar) | media | **Testar primeiro** `lsp: true` + 1 servidor (ex.: pyright ou typescript-language-server) em ambiente isolado; instalar so se demonstrar ganho |
| **Context7** | docs atualizadas de bibliotecas (Nivel 2/3 de pesquisa) | reduz alucinacao de API; mais confiavel que busca generica | npm 4.5.0 nao deprecado; endpoint remoto existe; precisa node (ok) e idealmente API key (nao verificado) | medio (2 ferramentas: resolve-id + get-docs; retornos de docs grandes consomem contexto) | somente leitura; liberar a Plan/Build/Reviewer | **alta** | **Recomendado instalar** (apos autorizacao), em modo remoto/npx, medir tokens e testar com o 30B |
| **Docker** | testes isolados / sandbox | rodar testes sem tocar o host | funciona (29.8.1) | nenhum (e so shell) | **Build apenas**, com `ask` para `docker *`; grupo docker = root no host | media | **Nao e MCP: usar via shell do Build** com confirmacao. Nao conceder a Plan/Reviewer |
| **Semgrep** | analise estatica/seguranca | achados objetivos para o Reviewer | ausente; precisaria instalar CLI (pip/pipx/docker); Reviewer nao tem Bash -> so via MCP ou arquivo de resultado gerado pelo Build | medio/alto se MCP | executa processo (nao e "somente leitura" pura) | media-baixa | **Adiar**: rodar via Build (`docker run semgrep`) e salvar relatorio que o Reviewer le. Nao dar execucao ao Reviewer |
| **Playwright** | testes reais de UI | validar interfaces web | `@playwright/mcp` 0.0.84; exige navegador (~centenas de MB), RAM limitada (7,5 GiB, 4 CPU) | **alto** (muitas ferramentas, snapshots de pagina grandes) | automatiza navegador = acao externa; apenas Build, com ask | baixa | **Nao instalar agora**: so ha beneficio em projetos com UI; custo de contexto alto para um modelo de 98k |
| **GitHub MCP** | issues, PRs, codigo, CI | contexto de repositorio | **`@modelcontextprotocol/server-github` esta DEPRECADO**; alternativa oficial remota (`api.githubcopilot.com/mcp/`, 401 sem token) ou `github/github-mcp-server` — **nao verificados** | alto (dezenas de ferramentas) | exige token; **somente leitura** (escopo minimo) ate autorizacao | baixa | **Nao instalar**. Se necessario: servidor oficial, token fine-grained somente leitura, so para Plan/Reviewer; reavaliar apos Context7 |

## Regras aplicadas na proposta
- Nenhuma ferramenta redundante: `websearch` nativo cobre busca geral; Docker e shell; Semgrep via Build + arquivo.
- Reviewer: nenhuma ferramenta de edicao/execucao. Plan: nenhuma ferramenta que altere o projeto. Qualquer MCP novo entra com `allow` somente nas ferramentas de leitura e `deny` nas demais, por agente.
- Cada integracao aprovada passara pelos 7 testes (instalar/iniciar, listar ferramentas, consulta real, validar, medir contexto, permissoes, limitacoes) em ambiente isolado antes de entrar no instalador.

## Sequencia sugerida (apos sua autorizacao)
1. Context7 (isolado em `/tmp`, medir tokens com e sem MCP, testar Plan/Build/Reviewer, testar permissoes).
2. LSP nativo com um servidor.
3. Estabilizar/confirmar SearXNG via MCP.
4. Docker/Semgrep como fluxo do Build (sem nova integracao). GitHub MCP e Playwright: apenas se surgir necessidade real.
