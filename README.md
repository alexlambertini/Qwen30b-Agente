# Qwen30b-Agente

Ambiente de agentes para o **[OpenCode](https://opencode.ai)** ligado a um servidor proprio com **Qwen3-Coder-30B-A3B**: programa, pesquisa na web sozinho, gera imagens (inclusive 4K), cria e valida layouts web, e atende chat para varias pessoas ao mesmo tempo.

O instalador copia **somente configuracao** (agentes, prompts, comandos, scripts). Nao instala modelo nem o OpenCode (a menos que voce peca com `--install-opencode`).

## Sumario
1. [Instalar e atualizar](#1-instalar-e-atualizar)
2. [Uso rapido](#2-uso-rapido)
3. [Agentes e comandos](#3-agentes-e-comandos)
4. [Programar (build)](#4-programar-build)
5. [Workflow feature, implement e review](#5-workflow-feature--implement--review)
6. [Pesquisa automatica](#6-pesquisa-automatica)
7. [Imagens (@imagem, /imagine, 4K)](#7-imagens-imagem-imagine-4k)
8. [Layout web (@web, /web, qwen-layout)](#8-layout-web-web-web-qwen-layout)
9. [Memoria do projeto](#9-memoria-do-projeto)
10. [Servidor: placas, servicos e chat](#10-servidor-placas-servicos-e-chat)
11. [Qualidade: benchmark](#11-qualidade-benchmark)
12. [Ajuste do modelo](#12-ajuste-do-modelo)
13. [Seguranca e permissoes](#13-seguranca-e-permissoes)
14. [Problemas comuns](#14-problemas-comuns)
15. [Estrutura do repositorio](#15-estrutura-do-repositorio)

---

## 1. Instalar e atualizar

Pre-requisitos do usuario: **OpenCode** instalado e a **API key** do servidor Qwen. Para imagens e layout: **Python 3** (e, para o layout, Playwright; ver secao 8).

### Linux e macOS
```bash
curl -fsSL https://raw.githubusercontent.com/alexlambertini/Qwen30b-Agente/main/install.sh | bash
```
Pergunta o endereco do servidor (padrao `https://ia.lambertini.com.br/v1`) e a **API key** (oculta). Nao interativo, com todas as opcoes:
```bash
curl -fsSL https://raw.githubusercontent.com/alexlambertini/Qwen30b-Agente/main/install.sh | bash -s -- --yes \
  --url https://SEU_SERVIDOR/v1 --key SUA_CHAVE \
  --comfyui http://SEU_SERVIDOR:8188 \
  [--searxng http://127.0.0.1:8888] [--install-opencode]
```
| Opcao | Para que serve |
|---|---|
| `--url` | endereco da API do Qwen (termina em `/v1`) |
| `--key` | API key (testada no servidor antes de gravar) |
| `--comfyui` | endereco do ComfyUI para `/imagine` (a galeria usa o mesmo host na porta 8189) |
| `--searxng` | SearXNG proprio para pesquisa (opcional; o `websearch` nativo ja funciona) |
| `--install-opencode` | instala o OpenCode pelo instalador oficial |
| `--dir` | instala em outra pasta (testes) |
| `--yes` | nao pergunta nada |

### Windows
Baixe **`dist/qwen-agente-setup.exe`** e de duplo clique. Ele pergunta URL, chave e ComfyUI. Ou pela linha de comando:
```bat
qwen-agente-setup.exe --key SUA_CHAVE --url https://SEU_SERVIDOR/v1 --comfyui http://SEU_SERVIDOR:8188
```
A configuracao vai para `%USERPROFILE%\.config\opencode` e os scripts para `%USERPROFILE%\.local\bin` (colocado no PATH do usuario). Precisa do OpenCode e, para `/imagine` e `/web`, de **Python 3**. Para regerar o exe: `windows/build.sh` (requer Go).

### Atualizar (rodar de novo)
Rodar o instalador de novo **atualiza** a instalacao existente, sem perguntar nada:
- guarda o que havia em `~/.config/opencode/backup-AAAAMMDD-HHMMSS/` (config, prompts, `comfyui.url`);
- **mantem** URL, chave e ComfyUI que voce nao informar;
- substitui prompts, agentes, comandos e scripts pelos novos.

Para trocar um valor, informe-o (`--url`, `--key`, `--comfyui`). O `opencode.json` fica com permissao 600 e a chave nunca esta no repositorio.

---

## 2. Uso rapido
```bash
cd meu-projeto
opencode                       # abre o OpenCode (agente build por padrao)
qwen-agente-init               # (uma vez) cria .opencode/memory/ do projeto
```
Dentro do OpenCode:
| Quero... | Faca |
|---|---|
| programar, corrigir bug, criar testes | escreva o pedido normalmente (agente `build`) |
| planejar antes de mexer | `/feature <demanda>` e depois `/implement` e `/review` |
| gerar uma imagem | `/imagine um tucano na floresta 4k` |
| criar/ajustar uma pagina web | `/web landing page responsiva do cafe X` (ou Tab ate `web`) |
| ensinar o projeto ao agente | `/memoria` |
| trocar de agente | Tab (primarios) ou `@imagem`, `@explore` no texto |

---

## 3. Agentes e comandos

| Agente | Papel | Restricao (aplicada pelo OpenCode, nao so pelo prompt) |
|---|---|---|
| `build` | programa: le, edita, roda e confere (padrao) | `ssh`/`scp`/`sudo`/`git push`/instalar pacote pedem confirmacao; `rm -rf` negado |
| `web` | especialista em layout e front-end, com verificacao automatica | igual ao `build` |
| `plan` | investiga e planeja | sem edicao; bash so de leitura (`ls`, `cat`, `grep`, `git log/diff`...) |
| `reviewer` | revisao independente do diff | sem edicao e sem bash |
| `imagem` | gera imagens no ComfyUI | so pode rodar `qwen-imagem`; sem edicao |
| `explore` | busca ampla no codigo | sem edicao e sem bash |

| Comando | O que faz |
|---|---|
| `/feature <demanda>` | `plan` investiga, propoe plano e espera sua aprovacao |
| `/implement` | `build` executa o plano aprovado e grava `.opencode/review/status.txt` e `diff.patch` |
| `/review <escopo>` | `reviewer` le o diff real e confere com as convencoes do projeto |
| `/imagine <descricao> [4k]` | gera a imagem e devolve o **link para baixar** |
| `/web <pedido>` | agente `web`: cria/corrige pagina e valida o layout |
| `/memoria` | cria/atualiza `.opencode/memory/` a partir do codigo real |

`plan` e `reviewer` so podem delegar ao `explore` (delegar ao `general` foi uma brecha real, corrigida: ver `reports/02`).

---

## 4. Programar (build)
O `build` segue um **metodo fixo**: entender, escrever a linha `CONTRATO:` (assinaturas e textos literais do pedido, mais as regras de `conventions.md`), investigar, reproduzir o bug, planejar (com `todowrite` se tiver 3+ etapas), implementar, testar no arquivo de teste que ja existe, revisar o proprio `git diff` e entregar com **Resumo, Requisitos, Arquivos, Verificacao e Pendencias**.

Dicas para tirar o maximo:
- **Seja literal** nos nomes: "funcao `transfer(src, dst, amount)`" gera funcao de modulo; "metodo" gera metodo.
- **Diga como testar** se o projeto for incomum; senao ele descobre pelo README/`package.json`/testes.
- **Pedidos grandes** viram lista de tarefas sozinho; peca `/feature` se quiser aprovar o plano antes.
- Ele **nunca** enfraquece nem apaga teste para passar, e para depois de 3 falhas iguais descrevendo o bloqueio (anti-loop).
- Rode o `/memoria` uma vez por projeto: as convencoes que ele aprende ali sao obrigatorias nas proximas tarefas.

## 5. Workflow feature -> implement -> review
```
/feature adicionar exportacao CSV do relatorio    # plan: investiga, mostra plano, pede aprovacao
(voce aprova ou ajusta)
/implement                                        # build: executa, roda testes, grava diff.patch
/review src/relatorio                             # reviewer: tabela de conformidade + parecer
```

## 6. Pesquisa automatica
O agente **pesquisa sozinho, sem pedir permissao**, quando:
- o pedido depende de algo que muda (versao "mais recente", data, preco, "hoje");
- vai usar biblioteca/API/flag que nao conhece com certeza (usa **Context7** para a documentacao atualizada e confere a versao instalada);
- um erro persiste depois de uma tentativa de correcao (busca a mensagem exata);
- vai instalar ou configurar uma ferramenta.

Ferramentas: `websearch` e `webfetch` nativos, mais Context7 (MCP remoto, nada local). Ele informa a URL usada. Nao pesquisa o que esta no proprio repositorio.

---

## 7. Imagens (@imagem, /imagine, 4K)
Geradas pelo **ComfyUI** (SDXL, modelo RealVisXL fotorealista por padrao).
```text
/imagine banner 16:9 de um cafe aconchegante ao amanhecer, estilo ilustracao
/imagine retrato fotorealista de um engenheiro, 9:16, 4k
```
O agente traduz para um prompt em ingles bem montado e chama `qwen-imagem`. A resposta traz sempre a linha **`LINK PARA BAIXAR: http://.../arquivo.png`**: a imagem fica na **galeria web** do servidor (porta 8189), abre no navegador e baixa direto.

Uso direto, sem o agente:
```bash
qwen-imagem "a red apple on a wooden table, photorealistic" --formato 1:1 --saida maca.png
qwen-imagem "cyberpunk city at night" --4k --formato 16:9
```
| Opcao | Descricao |
|---|---|
| `--formato` | `16:9` (padrao), `9:16`, `1:1`, `4:3`, `3:4` |
| `--4k` | gera na resolucao nativa e amplia 4x (RealESRGAN), saindo em 3840x2160 (16:9) ou 4096 no lado maior; demora ~7 min |
| `--modelo sd_xl_base` | ilustracao/arte (o padrao `RealVis` e fotorealista) |
| `--negativo`, `--seed`, `--passos`, `--cfg` | ajuste fino; `--seed` repete uma imagem |
| `--saida` | copia local do arquivo (a copia na galeria sempre existe) |

Enderecos (nessa ordem): `$COMFYUI_URL`, `~/.config/opencode/comfyui.url` (gravado pelo instalador) ou `http://127.0.0.1:8188`. A galeria: `$QWEN_GALERIA_URL`, `~/.config/opencode/galeria.url` ou o mesmo host do ComfyUI na porta 8189. Tempo tipico: 1,5 a 5 min (HD) e ~7 min (4K). O modelo **nao enxerga** a imagem; so garante que foi gerada. O SDXL nao escreve texto legivel dentro da imagem.

---

## 8. Layout web (@web, /web, qwen-layout)
O Qwen3-Coder **nao enxerga imagens**. Para ser bom em layout ele usa o **`qwen-layout`**, que abre a pagina num Chromium headless em **375, 768 e 1440 px** e entrega um relatorio que o modelo consegue ler:

rolagem horizontal · elementos fora da tela · texto cortado · contraste (WCAG AA) · alvos de toque < 44 px · fonte < 12 px · imagens sem `alt` ou quebradas · campos sem `<label>` · `h1` ausente/duplicado · `lang`, `viewport`, `title`, `<main>` · erros de console e de rede.

O agente `web` escreve, roda o `qwen-layout`, corrige **na origem** cada linha do relatorio e repete ate imprimir `LAYOUT OK`. Metodo: CONTRATO, tokens de design em `:root` (cores, espacamento, tipografia, modo escuro), HTML semantico, CSS mobile-first com Grid/Flexbox, verificacao em loop, capturas de tela, revisao do diff. Para imagens do site ele chama o `qwen-imagem`.
```text
/web landing page do cafe "Cafe Aurora" com cardapio de 3 itens e formulario de contato
/web corrija o index.html: quebra no celular e tem problemas de acessibilidade
```
Uso direto:
```bash
qwen-layout index.html                 # relatorio; codigo de saida 0 = limpo
qwen-layout http://localhost:3000      # pagina rodando
qwen-layout index.html --shots /tmp/s  # tambem salva layout-375/768/1440.png
qwen-layout index.html --json
```
**Instalar o Playwright** (uma vez, na maquina que roda o agente):
```bash
python3 -m venv ~/pw-venv && ~/pw-venv/bin/pip install playwright && ~/pw-venv/bin/playwright install chromium
sudo ~/pw-venv/bin/playwright install-deps chromium     # bibliotecas do sistema (Linux)
```
O script usa `~/pw-venv` sozinho. A **estetica** (se ficou bonito) continua sendo sua avaliacao: confira as capturas.

---

## 9. Memoria do projeto
`qwen-agente-init` cria `.opencode/memory/` (`architecture.md`, `conventions.md`, `known-issues.md`, `decisions/`, `tasks/`). Ela e carregada automaticamente em toda sessao. `/memoria` preenche a partir do codigo real. Cada regra de `conventions.md` e **obrigatoria** para o agente e entra no `CONTRATO:` de cada tarefa.

---

## 10. Servidor: placas, servicos e chat
Distribuicao usada (3 placas):
| Placa | Servico | Uso |
|---|---|---|
| RTX 3090 24 GB | `llama-opencode` (porta 8081) | **Qwen3-Coder-30B-A3B Q4_K_M**, contexto 98304, ~90 tok/s |
| RTX 3060 12 GB (1) | `llama-chat` (porta 8083) | **Qwen3-8B** com **16 slots paralelos** para atendimento |
| RTX 3060 12 GB (2) | `comfyui` (8188) + galeria (8189) | imagens, 4K e Playwright |

**Chat para varias pessoas:** `deploy/llama-chat.service.tpl` configura 16 slots (contexto total 57344, 3584 tokens por conversa) com batching continuo. Medido com 20 conversas simultaneas: 20/20 completas em ~12 s, 1o token mediana 2,2 s, ~7,7 tok/s por pessoa (velocidade de leitura) e ~77 tok/s no total. Aplicar (no servidor, com sudo; faz backup e volta atras se nao subir):
```bash
deploy/apply-chat.sh
python3 deploy/loadtest.py http://HOST:8083 CHAVE 20     # teste de carga
```
Medir o modelo de codigo: `python3 deploy/speedtest.py http://HOST:8081 CHAVE`. `deploy/apply-coder.sh q5|q4` troca a quantizacao (Q5_K_M nao compensou: carrega em mais de 7 min no servidor de 7,5 GB de RAM e ocuparia a placa do ComfyUI; ficou o Q4_K_M).

---

## 11. Qualidade: benchmark
`bench/run.sh` roda tarefas no OpenCode de verdade e confere cada uma com um **verificador oculto** (o agente nao le o gabarito).
```bash
bench/mkconf.sh /tmp/cfg                      # config de teste a partir dos templates (nao toca na sua)
bench/run.sh -x /tmp/cfg -n 3                 # 13 tarefas de programacao x3 rodadas
bench/run.sh -x /tmp/cfg -n 3 -a web w1-landing w2-fixpage w3-form   # tarefas web com o agente web
```
`BENCH_TIMEOUT` (padrao 300 s) e `BENCH_OUT` ajustam o limite e a pasta dos logs. Sempre use `-n 3` ou mais: o modelo varia 1 a 2 tarefas entre rodadas.

Resultado (7 tarefas dificeis x 3 rodadas, mesmo modelo):
| Tarefa | Config antiga | Config atual |
|---|---|---|
| t7 varios arquivos | 3/3 | 2/3 |
| t8 pesquisa na web | 3/3 | 3/3 |
| t9 limite de taxa | 2/3 | 1/3 |
| t10 arquivo grande | 3/3 | 2/3 |
| t11 fila assincrona (JS) | 2/3 | 2/3 |
| t12 estado compartilhado | 2/3 | 2/3 |
| t13 convencoes do projeto | 0/3 | **3/3** |
| **Total** | **15/21** | **15/21** |

O ganho comprovado e em **t13** (funcao de modulo com type hints e convencoes: 0/3 para 3/3, 6/6 isolado) e na **pesquisa** (nao responde mais de memoria). A nota geral ficou igual dentro da variacao. 

Agente **web** (3 tarefas: landing page do zero, pagina quebrada, formulario acessivel): **11/11** (w1 3/3, w2 4/4, w3 4/4), todas terminando com `LAYOUT OK` no `qwen-layout`. Na primeira tentativa o resultado foi pior por causa de erros meus (prompt sem o caminho do script e verificadores estritos demais), que foram corrigidos e documentados no `reports/07`.

Detalhes e a historia dos ajustes em `reports/07-benchmark-e-ajuste.md`. Outros testes: `tests/permissions.sh` (permissoes com o servidor de verdade).

## 12. Ajuste do modelo
- A `temperature` posta no agente **nao** e enviada pelo OpenCode a provedores OpenAI-compativeis. O sampler fica em `provider.qwen.models.*.options` (temperature 0.3, top_p 0.8, top_k 20, repeat_penalty 1.05), que vai no corpo de cada requisicao.
- `steps` por agente limita iteracoes (trava de loop): build 80, plan 40, reviewer 30, imagem 8.
- `experimental.todo` expoe a lista de tarefas (`todowrite`).
- O prompt do agente **substitui** o prompt padrao do OpenCode: tudo o que o modelo sabe sobre como trabalhar esta em `templates/prompts/`.
- Para o `opencode run` em scripts use `--standalone` e `</dev/null` (sem isso ele trava esperando stdin).

## 13. Seguranca e permissoes
- Restricoes por agente sao aplicadas pelo OpenCode (nao dependem do prompt). Neste OpenCode, um `permission: { edit: allow }` **global** anularia o `plan` somente leitura, por isso o `opencode.json` nao tem allow global.
- `ssh`, `scp`, `sudo`, `git push` e instalacao de dependencias pedem confirmacao; `rm -rf` e negado. Nao use `opencode run --auto` com essas regras: ele aprovaria os `ask`.
- A API key fica so no `~/.config/opencode/opencode.json` (permissao 600). Nao ha chave nem senha no repositorio. O endereco da galeria e do ComfyUI deve ficar em rede privada (VPN/Tailscale).

## 14. Problemas comuns
| Sintoma | Causa e solucao |
|---|---|
| `Servidor recusou a chave (HTTP 401)` | chave errada; nada foi alterado, rode de novo com a chave certa |
| `opencode run` trava sem terminal | use `--standalone` e `</dev/null` |
| `ComfyUI inacessivel` | defina `COMFYUI_URL` ou rode o instalador com `--comfyui` |
| `/imagine` demora | normal: 1,5 a 7 min; `--4k` e o mais lento |
| `qwen-layout`: Chromium nao iniciou | falta `playwright install-deps chromium` (Linux) |
| `qwen-layout: command not found` | use `~/.local/bin/qwen-layout` ou ponha `~/.local/bin` no PATH |
| resposta lenta com varias geracoes ao mesmo tempo | o modelo de codigo tem 1 slot; chat e imagem estao em outras placas |
| `Transport: ECONNRESET` | servidor sem RAM/CPU (2 CPUs, 7,5 GB): nao rode benchmark junto com geracao de imagem |

## 15. Estrutura do repositorio
```
install.sh                 instalador Linux/macOS (atualiza se ja existir)
dist/qwen-agente-setup.exe instalador Windows (gerado por windows/build.sh)
windows/                   fonte do instalador Windows (Go)
templates/
  opencode.json.tpl        config: agentes, comandos, sampler, permissoes
  prompts/                 build, web, plan, reviewer, imagem
  bin/                     qwen-imagem, qwen-layout
  memory/ AGENTS.md        modelo de memoria e regras globais
bench/                     benchmark (run.sh, mkconf.sh, tasks/)
deploy/                    chat paralelo, troca de quantizacao, testes de carga/velocidade
tests/                     testes de permissao
reports/                   auditoria, permissoes, pesquisa, memoria, agentes, benchmark
```
