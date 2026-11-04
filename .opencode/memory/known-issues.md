# Problemas conhecidos
## Abertos
| ID | Descricao | Evidencia | Impacto | Workaround |
|---|---|---|---|---|
| KI-001 | Modelo 30B-A3B as vezes ignora instrucoes de prompt (ex.: Plan inventou conteudo de arquivo sem chamar `read`; Build criou 3 arquivos fora do escopo) | `reports/02`, cenarios B/C | qualidade, nao seguranca | permissoes reais + prompts com regras anti-invencao + revisao |
| KI-002 | Reviewer nao tem Bash; `git diff` so via subagente `explore` e o modelo nem sempre o chama | cenario C | parecer pode nao ver o diff real | pedir ao Build para salvar o diff em arquivo / chamar `explore` explicitamente |
| KI-003 | SearXNG em `ia` instavel (engines com timeout) e MCP sem resultado confirmado | `reports/03` | pesquisa MCP nao confiavel | usar `websearch`/`webfetch` nativos |
| KI-004 | Allowlist de bash do Plan/explore e por padrao de texto; encadeamentos (`sh -c`, pipes com tee) nao testados exaustivamente | `reports/01` | possivel brecha | manter allowlist so de leitura; isolamento externo para risco maior |
| KI-005 | `todowrite` nao exposto na v2.1.4 | `reports/04` | sem checklist nativo | `tasks/*.md` |
## Resolvidos
| ID | Solucao | Data |
|---|---|---|
| KI-000 | Brecha plan/reviewer -> `general` (edit/shell liberados) fechada com `task` deny exceto `explore` (T11/T12) | 2026-11-04 |
