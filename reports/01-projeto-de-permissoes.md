# Projeto de permissoes
Implementado em `templates/opencode.json.tpl`. Resumo:
- Global: `bash`: `ssh/scp/sudo/git push *` = ask, `rm -rf *` = deny. **Sem** `edit`/`bash *` allow global (sobrescreveria `plan`).
- build: padrao do OpenCode + regras globais.
- plan: `edit` deny; `bash` `*`=deny e allowlist (ls, cat, head, tail, grep, rg, find, wc, pwd, git status/log/diff/show).
- reviewer (subagent): `edit` deny, `bash` deny.
- explore (nativo): `edit` deny, `bash` deny — fecha a delegacao.
Limites: allowlist por padrao de texto nao entende encadeamento; mantenha comandos permitidos somente-leitura. Resultados em FINAL-VALIDATION.md.
