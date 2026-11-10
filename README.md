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

## Pre-requisitos do usuario
Apenas: **OpenCode** instalado e acesso ao servidor do **Qwen** (a API key). Nada de Node, Docker ou Python e exigido pelo instalador (Python so e usado se existir). Sem OpenCode: `... | bash -s -- --install-opencode`.

## Workflow pronto (comandos)
`/feature <demanda>` (plan: investiga e planeja, pede aprovacao) -> `/implement` (build: executa o plano aprovado e grava `.opencode/review/status.txt` + `diff.patch`) -> `/review <escopo>` (reviewer: le o diff real, tabela de conformidade com `conventions.md`, parecer). `/memoria` cria/atualiza `.opencode/memory/` do projeto a partir do codigo real.
Pesquisa **automatica** (o agente pesquisa sozinho quando o assunto depende de versao, data, API incerta ou erro desconhecido): `websearch` e `webfetch` nativos + **Context7** (documentacao atualizada de bibliotecas, MCP remoto, sem instalar nada local).

## O que e instalado (`~/.config/opencode`)
| Agente | Papel | Restricao (aplicada pelo OpenCode, nao pelo prompt) |
|---|---|---|
| `build` | desenvolve | `ssh`/`scp`/`sudo`/`git push` pedem confirmacao; `rm -rf` negado |
| `plan` | investiga e planeja | sem edicao; bash so com allowlist de leitura (`ls cat grep git log/diff...`) |
| `reviewer` | revisao independente | sem edicao e sem bash |
| `explore` (nativo) | busca | sem edicao e sem bash (inclusive quando chamado por outro agente) |

Tambem: `AGENTS.md` global, `prompts/` completos (fluxo, limites, criterios de conclusao, formato de entrega, niveis de pesquisa), `memory-template/` e o comando `qwen-agente-init`, que cria `.opencode/memory/` no projeto (architecture, conventions, known-issues, decisions/, tasks/). A memoria do projeto e carregada automaticamente (`instructions`).

Plan e Reviewer so podem delegar ao `explore` (delegar ao `general` foi uma brecha real, corrigida: ver `reports/02`).

## Testar
- **Permissoes:** `tests/permissions.sh` (usa o servidor de verdade).
- **Qualidade de programacao:** `bench/run.sh` roda 13 tarefas (bug, feature em varios arquivos, debug, refatoracao, JS assincrono, pesquisa web, convencoes) e confere cada uma com um verificador oculto. Para medir uma mudanca nos templates SEM instalar: `bench/mkconf.sh /tmp/cfg && bench/run.sh -x /tmp/cfg`. Use `-n 3` para repetir (o modelo varia entre rodadas).
- Relatorios em `reports/` (00 auditoria · 01 permissoes · 02 testes · 03 pesquisa · 04 memoria · 05 agentes · 06 inventario de ferramentas · 07 benchmark e ajuste do modelo · FINAL-VALIDATION).

## Ajuste do modelo (o que realmente chega ao servidor)
- A `temperature` posta no agente NAO e enviada pelo OpenCode a provedores OpenAI-compativeis. O sampler fica em `provider.qwen.models.*.options` (temperature 0.3, top_p 0.8, top_k 20, repeat_penalty 1.05), que vai no corpo de cada requisicao.
- `steps` por agente limita as iteracoes (trava de loop); `experimental.todo` expoe a lista de tarefas `todowrite`.
- O prompt do agente SUBSTITUI o prompt padrao do OpenCode: tudo o que o modelo sabe sobre como trabalhar esta em `templates/prompts/`.

## Importante
Neste OpenCode, um `permission: { edit: allow }` **global** e aplicado *depois* da regra de cada agente e anularia o `plan` somente leitura. Por isso o `opencode.json` aqui nao tem allow global; restricoes ficam por agente.

## Atualizar / instalar no Windows

- **Linux/macOS:** rodar o `install.sh` de novo **atualiza** a instalacao existente: guarda o que havia em `~/.config/opencode/backup-DATA`, mantem URL, chave e ComfyUI que voce nao informar e substitui prompts, agentes e comandos pelos novos. Para trocar um valor, informe-o (`--url`, `--key`, `--comfyui`).
- **Windows:** baixe `dist/qwen-agente-setup.exe` e de duplo clique (pergunta URL, chave e ComfyUI) ou rode `qwen-agente-setup.exe --key SUA_CHAVE --comfyui http://100.94.64.97:8188`. Tambem atualiza sem perguntar de novo, com backup. A config fica em `%USERPROFILE%\.config\opencode`. Precisa do OpenCode e, para `/imagine`, do Python 3. Para regerar o exe: `windows/build.sh` (requer Go).
