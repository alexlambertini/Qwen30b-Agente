# Projeto de permissoes
Implementado em `templates/opencode.json.tpl`. Resumo:
- Global: `bash`: `ssh/scp/sudo/git push *` = ask, `rm -rf *` = deny. **Sem** `edit`/`bash *` allow global (sobrescreveria `plan`).
- build: padrao do OpenCode + regras globais.
- plan: `edit` deny; `bash` `*`=deny e allowlist (ls, cat, head, tail, grep, rg, find, wc, pwd, git status/log/diff/show).
- reviewer (subagent): `edit` deny, `bash` deny.
- explore (nativo): `edit` deny, `bash` deny — fecha a delegacao.
Limites: allowlist por padrao de texto nao entende encadeamento; mantenha comandos permitidos somente-leitura. Resultados em FINAL-VALIDATION.md.

## Atualizacao apos testes reais (ver 02)
- `permission.task = {"*":"deny","explore":"allow"}` em plan e reviewer (brecha `general`).
- `explore`: `edit` deny e bash allowlist de leitura incluindo `git status/log/diff/show/blame` (canal do Reviewer para diff).
- Modelo por agente: todos usam `qwen3-coder-30b-a3b` (unico servidor configurado no instalador); `small_model` tambem.
- Reviewer: sem edit, sem bash, sem criar arquivos (T6-T9).
