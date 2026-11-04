# Qwen30b-Agente

Ambiente de agentes para o **OpenCode** ligado a um servidor remoto com **Qwen3-Coder-30B-A3B**.
O instalador copia **somente configuracao** (nao instala modelo nem o OpenCode).

## Instalar (qualquer maquina)
```bash
curl -fsSL https://raw.githubusercontent.com/alexlambertini/Qwen30b-Agente/main/install.sh | bash
```
Ele pergunta o endereco do servidor (padrao `https://ia.lambertini.com.br/v1`), a **API key** (oculta) e, opcionalmente, a URL de um SearXNG.
Nao interativo:
```bash
curl -fsSL https://raw.githubusercontent.com/alexlambertini/Qwen30b-Agente/main/install.sh | bash -s -- --yes --url https://ia.lambertini.com.br/v1 --key SUA_CHAVE [--searxng http://127.0.0.1:8888]
```
A chave e testada no servidor antes de gravar; a config anterior vai para `~/.config/opencode/backup-AAAAMMDD-HHMMSS/`. O `opencode.json` fica com permissao 600. A chave nunca esta no repositorio.

## O que e instalado (`~/.config/opencode`)
| Agente | Papel | Restricao (aplicada pelo OpenCode, nao pelo prompt) |
|---|---|---|
| `build` | desenvolve | `ssh`/`scp`/`sudo`/`git push` pedem confirmacao; `rm -rf` negado |
| `plan` | investiga e planeja | sem edicao; bash so com allowlist de leitura (`ls cat grep git log/diff...`) |
| `reviewer` | revisao independente | sem edicao e sem bash |
| `explore` (nativo) | busca | sem edicao e sem bash (inclusive quando chamado por outro agente) |

Tambem: `AGENTS.md` global, `prompts/` completos (fluxo, limites, criterios de conclusao, formato de entrega, niveis de pesquisa), `memory-template/` e o comando `qwen-agente-init`, que cria `.opencode/memory/` no projeto (architecture, conventions, known-issues, decisions/, tasks/). A memoria do projeto e carregada automaticamente (`instructions`).

Plan e Reviewer so podem delegar ao `explore` (delegar ao `general` foi uma brecha real, corrigida: ver `reports/02`).

## Testar as permissoes
`tests/permissions.sh` (usa o servidor de verdade). Relatorios em `reports/` (00 auditoria · 01 permissoes · 02 testes · 03 pesquisa · 04 memoria · 05 agentes · 06 inventario de ferramentas · FINAL-VALIDATION).

## Importante
Neste OpenCode, um `permission: { edit: allow }` **global** e aplicado *depois* da regra de cada agente e anularia o `plan` somente leitura. Por isso o `opencode.json` aqui nao tem allow global; restricoes ficam por agente.
