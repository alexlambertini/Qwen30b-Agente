# Validacao final (2026-11-04)
Ambiente de teste: OpenCode v2.1.4 em `ia`; replica instalada tambem na maquina local (v2.0.20). Modelo unico: `qwen/qwen3-coder-30b-a3b` via `https://ia.lambertini.com.br/v1` (98.304 ctx / 8.192 saida, tool_call habilitado).
Legenda: PASS · FAIL · NOT TESTED · INCONCLUSIVE.

## Arquitetura implantada
Repositorio de configuracao + `install.sh` (so config). Provider unico `qwen`; permissoes globais minimas (ssh/scp/sudo/git push = ask; rm -rf = deny) e restricoes POR AGENTE; prompts em `~/.config/opencode/prompts/`; `AGENTS.md` global; memoria-modelo + `qwen-agente-init`; `instructions` carrega a memoria do projeto.

## Agentes, modelos, permissoes
| Agente | Papel | Modelo | Permissoes (aplicadas pelo OpenCode) |
|---|---|---|---|
| build (padrao) | executa | qwen3-coder-30b (unico servidor; sem 2o modelo para trocar) | padrao + ssh/scp/sudo/git push ask, rm -rf deny |
| plan | planeja | idem | edit deny; bash so allowlist de leitura; task so `explore` |
| reviewer (subagent) | revisa | idem | edit deny; bash deny; task so `explore` |
| explore (nativo) | busca | idem | edit deny; bash so leitura (+git read-only) |
Nao criados: Scout (nao existe), Architect/Debugger/Tester/Researcher (ver `05`).

## Resultados por fase
| Fase | Resultado |
|---|---|
| 1 Auditoria | PASS (`00`). Achados: scout inexistente; allow global anulava plan; MCP SearXNG falhando; provider chat com endpoint errado (nao alterado em `ia`) |
| 2 Projeto de permissoes | PASS (`01`) |
| 3 Tres agentes | PASS funcional; qualidade limitada pelo modelo (ver cenarios) |
| 4 Permissoes reais | 17 PASS · 1 PASS/INCONCLUSIVE (T18) em 18 testes (`02`). Uma falha real encontrada e corrigida (plan/reviewer -> general) |
| 5 Pesquisa | webfetch PASS · websearch PASS · SearXNG container PASS (instavel) · MCP SearXNG busca via MCP NOT TESTED conclusivo (`03`) |
| 6 Memoria | estrutura PASS · carga automatica via `instructions` PASS · Cenario E PASS (`04`) |
| 7 Agentes especializados | nenhum criado, justificado (`05`) |
| 8 Checklist | `todowrite` NAO exposto ao modelo -> checklist em `tasks/*.md`. Nativo: NOT TESTED/indisponivel |
| 9 Cenarios | A PASS (plan investigou, estruturou, nao alterou; 1a vez ignorou memoria -> corrigido com `instructions`) · B PASS parcial (implementou e testou, mas **violou escopo**: 3 arquivos extras + tentou `pip install`) · C PASS parcial (reviewer nao editou/nao rodou bash e apontou os arquivos fora do escopo, mas com severidades ruins e sem obter `git diff` real) · D PASS · E PASS |
| Modulo ferramentas | Context7 instalado e testado (contexto +0); LSP/Docker/Semgrep/Playwright/GitHub MCP nao instalados (exigem dependencias locais) (`06`) |

## Atualizacao final (rodada de correcao)
- Instalador: so pede a API key; baixa do GitHub (testado com token, repo privado); instala agentes, permissoes, prompts, memoria-modelo, Context7 e comandos `/feature /implement /review /memoria` (registro dos 4 comandos: PASS via API; execucao ponta a ponta no TUI: NOT TESTED).
- Confirmacao para instalar dependencias (`pip/npm/apt...` = ask): PASS (`permission requested: shell (pip install requests)`).
- Cenario B (re-teste): Build ficou no escopo, manteve pytest, sem arquivos extras, gerou `status.txt`/`diff.patch`: PASS.
- Cenario C (re-teste): Reviewer leu o diff gerado; com prompt mecanico, marcou `NAO` na regra do pytest (caso unittest) e nao gerou falsos alarmes no caso correto: PASS parcial — o parecer final do caso ruim saiu "APROVADO COM RESSALVAS" quando deveria ser REPROVADO (erro do modelo, nao de permissao).
- Alucinacao ao ler arquivo (T5): REGRA 0 + temperatura 0: plan 5/5, reviewer 3/3, build 3/3 (antes ~50% de falha no plan). Suite de permissoes final (instalacao via GitHub): 17 PASS + T5 oscilante antes do ajuste.

## Falhas conhecidas / limitacoes
- KI-001: o 30B-A3B ignora/inventa as vezes (Plan inventou conteudo de arquivo sem chamar `read`; Build criou arquivos fora do escopo; Reviewer classificou mal severidades). Mitigacao: permissoes reais, regras no prompt, revisao humana.
- KI-002: Reviewer depende do modelo chamar `explore` para ver o diff.
- KI-004: allowlist de bash por texto; `sh -c`/`tee`/encadeamentos NOT TESTED.
- Modo nao interativo: o fluxo de aprovacao de "ask" nao foi exercitado.
- Testes feitos so em `ia` (2.1.4) e um smoke test local (2.0.20: plan bloqueado). `curl | bash` a partir do GitHub: NOT TESTED ate o repositorio ficar acessivel.
- Chaves em texto claro na config antiga de `ia` e backups (nao alterado).

## Veredito
Restricoes de permissao: **aprovadas com as ressalvas acima** (nenhuma falha critica aberta). Qualidade de execucao dos agentes: **limitada pelo modelo**; nao considere o fluxo autonomo sem revisao humana. Modulo de ferramentas: **pendente de autorizacao**.
