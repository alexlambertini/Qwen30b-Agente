# Problemas conhecidos
## Abertos
| ID | Descricao | Evidencia | Impacto | Workaround |
|---|---|---|---|---|
| KI-001 | Modelo 30B-A3B as vezes ignora instrucoes de prompt (ex.: Plan inventou conteudo de arquivo sem chamar `read`; Build criou 3 arquivos fora do escopo) | `reports/02`, cenarios B/C | qualidade, nao seguranca | permissoes reais + prompts com regras anti-invencao + revisao |
| KI-002 | Reviewer nao tem Bash; `git diff` so via subagente `explore` e o modelo nem sempre o chama | cenario C | parecer pode nao ver o diff real | pedir ao Build para salvar o diff em arquivo / chamar `explore` explicitamente |
| KI-003 | SearXNG em `ia` instavel (engines com timeout) e MCP sem resultado confirmado | `reports/03` | pesquisa MCP nao confiavel | usar `websearch`/`webfetch` nativos |
| KI-004 | Allowlist de bash do Plan/explore e por padrao de texto; encadeamentos (`sh -c`, pipes com tee) nao testados exaustivamente | `reports/01` | possivel brecha | manter allowlist so de leitura; isolamento externo para risco maior |
| KI-006 | `temperature` definida no agente NAO e enviada ao servidor (requisicao capturada so tem model/stream/max_completion_tokens) | `reports/07` | modelo rodava com a temperatura padrao do llama-server (0.7) | sampler em `provider.models.*.options` e `agent.*.options` (chegam no corpo da requisicao) |
| KI-007 | `opencode run` sem `</dev/null` fica esperando stdin em sessao sem TTY | `reports/07` | scripts travam ate o timeout | sempre redirecionar stdin |
## Resolvidos
| ID | Solucao | Data |
|---|---|---|
| KI-005 | `todowrite` passa a ser exposto com `experimental.todo: true` | 2026-11-09 |
| KI-000 | Brecha plan/reviewer -> `general` (edit/shell liberados) fechada com `task` deny exceto `explore` (T11/T12) | 2026-11-04 |
