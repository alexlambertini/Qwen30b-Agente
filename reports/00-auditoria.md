# Fase 1 — Auditoria (somente leitura)

Data: 2026-11-04 · Máquina auditada: `ia` (lambertini@ia) · Máquina destino da réplica: máquina local (esta)

Legenda: **Verificado** (evidência objetiva) · **Testado** · **Não testado** · **Bloqueado** · **Suposição**

## 1. Estado atual — `ia`

| Item | Status | Evidência |
|---|---|---|
| OpenCode instalado | Verificado | `~/.opencode/bin/opencode --version` → `opencode v2.1.4` (`opencode2` é wrapper `exec opencode`). Não está no PATH padrão. |
| Config global | Verificado | `~/.config/opencode/opencode.json` (4416 B, 03/nov) + `AGENTS.md`, `cli.json`, `agents/` (11 `.md`) |
| Agentes em `~/.opencode/agents/` | Verificado | `crewai.md`, `operator.md` (root:root, 12 KB), `programador.md` (root:root, 33 KB) |
| Config local de projeto | Verificado | Nenhum `opencode.json` no home; nenhum `skills/` nem `commands/` em `~/.config/opencode` |
| Pasta `reports/` | Verificado | Não existia (criada só nesta máquina local para este relatório) |
| Schema | Verificado | `$schema: https://opencode.ai/config.json`; `cli.json` usa `https://opencode.ai/v2/cli.json` |
| `debug config` | Verificado | Normaliza `permission` → lista `permissions[{action,resource,effect}]` (formato interno v2) |

### Agentes (via `opencode debug agents`)
- **Nativos**: `build`, `plan`, `explore` (subagent), `general` (subagent), e ocultos `compaction`, `summary`, `title`. **`scout` não existe** (confirmado).
- **Customizados presentes**: `auditor`, `coder`, `debugger`, `depurador`, `documentador`, `pesquisador`, `planejador`, `refatorador`, `revisor`, `testador`, `operator`, `programador`, `crewai`, `chat`.
- **Redundância**: há muitos agentes (PT e EN duplicados: `debugger`/`depurador`, `planejador`/`plan`, `revisor`≈futuro Reviewer). Vários referenciam provider `leve` e modelo `local/qwen3-30b-a3b`, que **não existem** em `opencode models`.

### Modelos (`opencode models` filtrado)
`local/qwen3-coder-30b-a3b`, `ollama/qwen3:8b`, `ollama/qwen2.5-coder:1.5b(-base)`, `chat/qwen3-8b-chat`.
Os valores de contexto/saída/tool_call do prompt batem com o JSON (exceto `ollama` output = **4096**, não informado no briefing). `ollama` aparece com 2 modelos extras não configurados explicitamente.

### Serviços
| Endpoint | Resultado |
|---|---|
| `<IP-TAILSCALE>:8081` (llama-server, modelo principal) | Sem chave → **401**; com a chave da config → **200** (Testado) |
| `127.0.0.1:11434` (ollama) | **200** (Testado) |
| `<IP-TAILSCALE>:8083` (chat) | llama-server escutando, mas **só no IP Tailscale**; a config aponta `127.0.0.1:8083` → curl **000** (Verificado: **config incorreta**) |
| SearXNG `127.0.0.1:8888` (docker, up 34h) | HTML 200 em 2,9 s; JSON 200 em 4,6 s mas **0 resultados** (`duckduckgo` e `wikidata` em timeout) |
| MCP `searxng` (`opencode mcp list`) | **`✗ failed: Request timed out`** (Testado). `mcp-searxng@2.10.0` existe no npm. |

Tool calling real dos modelos: **Não testado** (apenas declarado na config).

## 2. Problemas encontrados

1. **MCP SearXNG não opera.** Falha por timeout na inicialização (`npx -y` a cada start) e o próprio SearXNG está sem resultados (engines com timeout, provável falta de saída de rede/DNS no container). *Pesquisa técnica não está funcional.*
2. **Endpoint do modelo de atendimento** (`chat`) aponta para loopback, mas o serviço escuta no IP `<IP-TAILSCALE>`. O agente `chat` não funciona.
3. **Agentes quebrados/redundantes**: referências a provider `leve` e modelo `qwen3-30b-a3b` inexistentes; `operator.md` e `programador.md` pertencem a root (não editáveis sem sudo) e somam ~45 KB de prompt.
4. **Permissões atuais são permissivas**: `edit`/`webfetch`/`bash *` = allow; só `ssh`, `scp`, `sudo`, `git push` = ask e `rm -rf *` = deny. O briefing exige Plan/Reviewer read-only — isso hoje só está em prompts de agentes custom (`revisor`: `edit deny`), **Não testado**.
5. **Chaves de API em texto claro** no `opencode.json` (redigidas neste relatório) e backups `.bak*` espalhados (≥10) com a mesma exposição.
6. **`AGENTS.md` global** instrui "NUNCA peça senha… a chave SSH já existe", o que conflita com a política de `ssh = ask` e é específico da máquina `ia`.
7. **Sem `skills/`, `commands/`, `.opencode/memory/`.**

## 3. Máquina local (destino da réplica) — diferenças

| Item | `ia` | Local |
|---|---|---|
| OpenCode | **v2.1.4** | **v2.0.20** (desatualizado — o briefing é para 2.1.4) |
| `opencode.json` | Verificado | Praticamente idêntico ao de `ia` (mesmos providers, permission, agentes build/chat, MCP) |
| Agentes custom | 14 | 11 (`auditor… testador`, `qwen3-instruct`, `seo-engineer`, `dev.md`) |
| Ollama `127.0.0.1:11434` | 200 | **000** (não roda) |
| SearXNG `127.0.0.1:8888` | up (sem resultados) | **000** (não roda) |
| Modelo principal `<IP-TAILSCALE>:8081` | 200 com chave | 401 sem chave (**Não testado** com chave) |
| `~/.ssh/config` | existe | **não existe** |
| Docker/llama.cpp locais | sim | **Não verificado** |

## 4. Recomendações / arquitetura alvo
- Mantém-se: providers `local`/`ollama`/`chat`, modelos, limites, compaction, bloco `permission` atual (base para o Build).
- Corrigir: baseURL de `chat` (`<IP-TAILSCALE>:8083` em `ia`), MCP SearXNG (pré-instalar `mcp-searxng` e arrumar rede dos engines), remover agentes quebrados.
- Criar apenas **build, plan (nativo, endurecer), reviewer**; usar `explore` nativo; sem Scout.
- Permissões reais (`permission` por agente) em vez de prompt; testar delegação via `task`.
- Replicar em dois passos: (a) atualizar o OpenCode local 2.0.20 → 2.1.4 (`opencode upgrade`, requer sua autorização); (b) aplicar a mesma configuração, ajustando endpoints locais, pois Ollama/SearXNG não existem nesta máquina.

## 5. Plano da Fase 2 (projeto de permissões — nada implementado ainda)
1. Ler `opencode debug agents` de `build`/`plan`/`explore` na v2.1.4 para ver as permissões nativas reais.
2. Propor `permission` por agente em `reports/01-projeto-de-permissoes.md`: Build (atual + `external_directory: ask`, `rm`/`dd`/`mkfs`/`chmod -R` ask), Plan (`edit: deny`, bash só leitura via allowlist: `git log/diff/status`, `ls`, `cat`, `grep`; `task` só para `explore`), Reviewer (`edit: deny`, `bash: deny`, `webfetch` allow, `task` só `explore`).
3. Definir modelo por agente (principal para Build/Plan/Reviewer; `qwen3:8b` apenas para title/summary), com justificativa.
4. Listar riscos: o modelo local (30B-A3B) pode ignorar prompts; só permissões valem. Bash allowlist de Plan precisa ser testado contra `sh -c`, redirecionamentos e `tee`.
5. Aguardar autorização antes de qualquer alteração; backup do `opencode.json` antes (com timestamp).

## 6. Não alterado
Nenhum arquivo foi modificado em `ia`. Apenas leitura e chamadas HTTP de diagnóstico. Este arquivo é o único criado (na máquina local).
