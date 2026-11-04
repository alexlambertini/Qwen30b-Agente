# Arquitetura — Qwen30b-Agente
Ultima verificacao: 2026-11-04

## Visao geral
Repositorio de CONFIGURACAO (nao contem modelo): instalador bash que escreve `~/.config/opencode/` ligando o OpenCode a um servidor remoto OpenAI-compativel com Qwen3-Coder-30B-A3B (llama.cpp), padrao `https://ia.lambertini.com.br/v1`.

## Componentes
| Componente | Caminho | Responsabilidade |
|---|---|---|
| Instalador | `install.sh` | pergunta URL/chave, valida no servidor (`/models`), faz backup, renderiza `opencode.json`, copia prompts/AGENTS/memoria, cria `qwen-agente-init` |
| Template de config | `templates/opencode.json.tpl` | provider `qwen`, permissoes globais e por agente, `instructions` da memoria; placeholders `__BASE_URL__`/`__API_KEY__` |
| Prompts | `templates/prompts/{build,plan,reviewer}.md` | comportamento (NAO e seguranca) |
| Memoria-modelo | `templates/memory/` | copiada para `.opencode/memory/` do projeto |
| Testes | `tests/permissions.sh` | testes reais de permissoes/delegacao |
| Relatorios | `reports/` | auditoria, permissoes, testes, pesquisa, memoria, agentes, inventario, validacao |

## Fluxo
`install.sh` -> valida servidor -> backup -> instala em `~/.config/opencode` -> usuario roda `opencode` -> agentes: plan (planeja) -> usuario autoriza -> build -> reviewer.

## Dependencias
bash, curl, tar, python3 (opcional, fallback sed). OpenCode instalado a parte (testado v2.0.20 e v2.1.4).
