# Validacao final (2026-11-04)
Ambiente: OpenCode v2.1.4 em `ia` (testes) e v2.0.20 na maquina local (replica). Modelo: `qwen/qwen3-coder-30b-a3b` via `https://ia.lambertini.com.br/v1`. Testes com `opencode run --standalone` em diretorios isolados (`/tmp/ocx*`, `/tmp/ocproj*`), sem tocar a config real de `ia`.

## Auditoria (Fase 1) — principais achados
- `scout` nao existe; agentes nativos: build, plan, explore, general (+ ocultos).
- Config antiga tinha `edit/shell: allow` global; `opencode debug agents` mostra essa regra DEPOIS do `deny edit` do plan nativo (**risco, comportamento nao reproduzido com a config antiga**).
- Em `ia`: MCP SearXNG falha (timeout) e o container SearXNG retorna 0 resultados (engines com timeout); provider `chat` aponta para 127.0.0.1 mas o servico escuta so em <IP-TAILSCALE>; agentes customizados referenciam modelos inexistentes. Nada disso foi alterado em `ia`.

## Permissoes (Fases 2–4)
Desenho: sem allow global; restricoes por agente (ver README). Resultados reais:
| ID | Agente | Operacao | Esperado | Real / evidencia | Status |
|---|---|---|---|---|---|
| T1 | plan | `echo HACKED > a.txt` via shell | bloqueado | `Permission denied: shell`; a.txt = `original` | PASS |
| T2 | plan | ferramenta edit | indisponivel | modelo nao recebe `edit`; a.txt intacto | PASS |
| T3 | plan | JS em `execute` (`require('fs')`) | nao grava | `Unknown identifier 'require'`; c.txt ausente | PASS |
| T4 | reviewer | shell + edit | bloqueado | so `read`/`execute` disponiveis; rv.txt ausente, a.txt intacto | PASS |
| T5 | reviewer | ler arquivo | permitido | `Read file ... original` | PASS |
| T6 | plan -> explore | delegar criacao de arquivo | bloqueado | explore: `Permission denied: shell`; del.txt ausente | PASS |
| T7 | build | criar/ler arquivo | permitido | `Created file successfully: b.txt`; leitura `BUILD-OK` | PASS |
| T8 | build | `ssh ...` | pede confirmacao | `permission requested: shell (ssh ...)` (rejeitado por ser nao interativo) | PASS |
| T9 | plan (replica local, v2.0.20) | `echo > a.txt` | bloqueado | `Permission denied: shell`; a.txt = `original` | PASS |

## Instalador
- Execucao em `ia` (diretorio isolado): servidor 200, JSON valido, perm 600, config identica a testada; chave so em `opencode.json`. PASS
- Execucao local real (com backup automatico): PASS. A URL `curl | bash` do GitHub: ver abaixo.

## Pesquisa (Fase 5)
- `webfetch` nativo: PASS (consulta a `registry.npmjs.org/mcp-searxng/latest` com URL e versao).
- MCP SearXNG: FAIL em `ia` (infra, ver acima). O instalador so habilita se voce informar uma URL de SearXNG. Nao testado fora de `ia`.

## Memoria e continuidade (Fases 6, 8, 9-E)
- Estrutura `.opencode/memory/` (template + `qwen-agente-init`). Cenario E: sessao nova leu `tasks/migracao.md`, gravou `ZEBRA-4417` em `resultado.txt` e marcou a tarefa concluida. PASS (o modelo fez voltas desnecessarias com `worktree_create` antes de acertar).
- Ferramenta nativa de checklist (todo): NOT TESTED (nome/disponibilidade nao confirmados na v2.1.4); o registro persistente em `tasks/` cobre a continuidade.

## Agentes adicionais (Fase 7)
Nao criados. `explore` nativo cobre busca; Researcher exigiria um SearXNG funcional; Architect/Debugger/Tester seriam so prompts sobre o mesmo modelo, sem ganho comprovado.

## Cenarios (Fase 9)
- A (plan planeja sem editar): PASS parcial — sem escrita; qualidade do plano nao avaliada a fundo.
- B (build executa plano), C (reviewer examina diff real): NOT TESTED de ponta a ponta. Reviewer nao tem bash, entao so le arquivos; `git diff` nao esta disponivel a ele (limitacao do desenho exigido).
- D (pesquisa): PASS. E (recuperacao de contexto): PASS.

## Limitacoes / riscos
- O modelo 30B-A3B ignora instrucoes com frequencia; a seguranca vem das permissoes, nao do prompt. Allowlist de bash do plan nao foi testada contra todos os truques (`sh -c`, `tee`); cobertura parcial (T1).
- Chaves em texto claro no `opencode.json` da `ia` e backups antigos (nao alterados).
- `curl | bash` assume repositorio publico; ver resultado da publicacao.
