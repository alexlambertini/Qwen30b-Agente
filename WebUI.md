# WebUI.md — Plano de implantação do Open WebUI

Objetivo: um chat web (estilo ChatGPT/Claude) servido pelo servidor `ia`, com o **Qwen3-Coder-30B** como modelo principal, o **Qwen3-8B** como opção no seletor, pesquisa na web, geração de imagem exibida no próprio chat e os agentes do **ADVOGADO REVISIONAL** selecionáveis. Acesso restrito a quem recebe cadastro (hoje, quem tem a API key).

> Status (11/11): **implantado e testado no servidor, fases 0 a 6 e 8**. Pendente: Fase 7 (trocar o domínio no túnel Cloudflare) e teste de carga da Fase 9. Tudo é reinstalável com `deploy/instalar-servidor.sh`. Ver o Registro no fim.
> Regras que valem para toda a implantação: a API key do llama-server **não muda**; senhas e chaves não vão para o repositório; documentos de cliente ficam só no servidor; arquivos baixados são dados não confiáveis; não rodar benchmark junto com instalação pesada ou geração de imagem (2 CPUs, 7,5 GB de RAM).

---

## 1. Arquitetura

```
Navegador ──HTTPS──► proxy (nginx atual) ──► Open WebUI (container, porta 3000)
                                                │
              ┌─────────────────────────────────┼──────────────────────────┐
              ▼                                 ▼                          ▼
   llama-server 30B (3090, :8081)      llama-server 8B (3060, :8083)   ComfyUI (3060, :8188)
   (chave: a atual, sem mudar)          (seletor, rápido)               imagem 4K + galeria :8189
              │
              ├── SearXNG (container, :8888)  ← pesquisa na web
              └── Servidor de ferramentas do núcleo `revisor` (OpenAPI/MCP, :8890)
                      └── pasta isolada por caso, OCR, PDF, DOCX
```

Componentes novos: Open WebUI, SearXNG, servidor de ferramentas `revisor`, Tesseract (OCR) e LibreOffice (conversão de `.doc`).

## 2. Pré-requisitos e limites

| Item | Situação | Observação |
|---|---|---|
| RAM 7,5 GB / 2 CPUs | apertado | Open WebUI ~0,5–1 GB, SearXNG ~0,2 GB. Embeddings **desligados ou externos** (ver 5.2) |
| Docker | presente (`/usr/bin/docker`) | instalar só se não existir; avisar antes |
| 30B com `parallel 1` | uma resposta por vez | várias pessoas ao mesmo tempo entram em fila; o 8B (16 slots) é a válvula de escape |
| GPU0 (3090) | já caiu do barramento PCIe em 10/11 (Xid 79) | usuário decidiu manter energia máxima; monitorar temperatura (>83 °C) em carga |
| Domínio atual `SEU_DOMINIO` | já serve a API | **não substituir** no início: subir em outra porta/subdomínio e trocar depois de testar |

## 3. Fases

Cada fase termina com um teste de aceitação. Só avançar quando passar.

### Fase 0 — Preparação `[ ]`
- [ ] Benchmark em andamento terminar (não instalar pesado junto).
- [x] `[FEITO]` Docker já presente em `/usr/bin/docker` (80 GB livres em disco). Se ausente, instalaria o Docker Engine (pacote do repositório oficial) e adicionar o usuário ao grupo `docker`.
- [ ] Criar `~/webui/` (dados, `.env`, `docker-compose.yml`). Permissão `700`; `.env` com `600`.
- [ ] Backup da config do nginx antes de qualquer alteração.
- **Aceite:** `docker run --rm hello-world` ok; espaço em disco > 20 GB livres.

### Fase 1 — OCR e conversores `[parcial: OCR feito; faltam LibreOffice e pacotes Python]`
- [x] `[FEITO 10/11]` `apt install tesseract-ocr tesseract-ocr-por poppler-utils`: `tesseract --list-langs` lista `eng`, `osd`, `por`; `pdftotext` e `pdftoppm` instalados.
- [ ] `apt install libreoffice-writer --no-install-recommends` (conversão `.doc` → `.docx`/PDF, em modo headless).
- [ ] No venv do servidor de ferramentas: `pypdf python-docx openpyxl pytesseract Pillow`.
- **Aceite:** `tesseract --list-langs` lista `por`; `soffice --headless --convert-to docx exemplo.doc` gera o arquivo; `revisor doctor` mostra PDF, DOCX, XLSX e OCR disponíveis.

### Fase 2 — Open WebUI básico `[ ]`
- [ ] `docker-compose.yml` com a imagem **com versão fixada** (nunca `latest`), volume em `~/webui/data`, porta `127.0.0.1:3000`.
- [ ] Variáveis: `OPENAI_API_BASE_URL=http://SEU_SERVIDOR:8081/v1`, `OPENAI_API_KEY` (a chave atual, só no `.env`), `ENABLE_SIGNUP=false`, `DEFAULT_USER_ROLE=pending`, `WEBUI_SECRET_KEY` aleatória, `ENABLE_OLLAMA_API=false`.
- [ ] Segundo endpoint para o 8B: `http://SEU_SERVIDOR:8083/v1` (mesma chave, se a atual valer nele).
- [ ] Criar o usuário administrador (o primeiro cadastro vira admin) e fechar o cadastro.
- [ ] Ajustar timeout de resposta e `ctx` por modelo (30B: 98304; 8B: 57344).
- **Aceite:** o chat responde com o 30B e com o 8B; o seletor lista os dois; `/api` exige login; cadastro novo é recusado.

### Fase 3 — Pesquisa na web (SearXNG) `[ ]`
- [ ] Container SearXNG em `127.0.0.1:8888`, formato JSON habilitado, motores gerais + jurídicos (sem rastreamento).
- [ ] Open WebUI: `ENABLE_RAG_WEB_SEARCH=true`, `RAG_WEB_SEARCH_ENGINE=searxng`, `SEARXNG_QUERY_URL=http://searxng:8080/search?q=<query>&format=json`, `RAG_WEB_SEARCH_RESULT_COUNT=5`.
- **Aceite:** pergunta sobre fato recente retorna resposta com fontes (links); desligar a internet do contêiner faz o modelo declarar que não pesquisou, sem inventar.

### Fase 4 — Imagem no chat (ComfyUI) `[ ]`
- [ ] Open WebUI: `ENABLE_IMAGE_GENERATION=true`, `IMAGE_GENERATION_ENGINE=comfyui`, `COMFYUI_BASE_URL=http://SEU_SERVIDOR:8188`.
- [ ] Exportar o workflow atual do `qwen-imagem` em formato API e colar em `COMFYUI_WORKFLOW`, com os nós de prompt/tamanho/seed mapeados.
- [ ] Tamanho padrão 4K (3840×2160) conforme pedido anterior; permitir opção menor (1024×1024) para teste.
- [ ] Mostrar a imagem no chat **e** o link de download da galeria `:8189` (`https://.../galeria/...`) na mesma resposta (instrução no prompt do modelo e/ou pequena função de pós-processamento).
- [ ] Limitar a uma imagem por vez (fila) — ComfyUI e coder disputam a RAM; **não gerar imagem durante benchmark**.
- **Aceite:** "gere uma imagem de ..." exibe a imagem inline e entrega o link; o arquivo existe em `~/IA/output`; o chat não trava durante a geração.

### Fase 5 — Servidor de ferramentas do núcleo `revisor` `[ ]`
Cópia adaptada do repositório `advogado-revisional`, **sem alterar o repositório original** até decidirmos o pull request.
- [ ] Serviço (FastAPI ou MCP via `mcpo`) com endpoints: `analisar`, `calcular`, `amortizar`, `encargos`, `fontes`, `relatorio`, `doctor`, `selftest`.
- [ ] **Pasta de caso isolada**: cada caso em `~/casos/<id>/`; caminhos recebidos são resolvidos e **rejeitados se saírem dessa pasta** (sem `..`, sem links simbólicos para fora).
- [ ] **Sem shell e sem código montado em string**: chamar as funções Python do pacote `revisor` diretamente, ou `subprocess` com lista de argumentos e `shell=False`; **sem variáveis de ambiente vindas do modelo**.
- [ ] Executar como usuário sem privilégios, `systemd` com `ProtectSystem=strict`, `ReadWritePaths` só na pasta dos casos, `PrivateTmp`, `NoNewPrivileges`, memória máxima (1 GB).
- [ ] Entrada de arquivo: PDF, DOCX, XLSX, CSV, TXT; `.doc` convertido com LibreOffice; PDF escaneado vai por OCR (`por`); limite de tamanho (ex.: 50 MB) e de páginas.
- [ ] Autenticação do servidor de ferramentas por chave própria (arquivo `600`), escutando só em `127.0.0.1`.
- **Aceite:** `revisor selftest` e `tests/` passam; teste de travessia (`../../etc/passwd`) é recusado; contrato de exemplo (`exemplos/contrato-exemplo.txt`) gera `estudo.json` e relatório; PDF escaneado e `.doc` de teste são lidos.

### Fase 6 — Modelos (agentes) no seletor `[ ]`
Cada agente vira um **Modelo personalizado** do Open WebUI (modelo base + prompt + ferramentas + parâmetros). Prompts versionados neste repositório em `webui/modelos/*.json` para importar/exportar.

| Modelo no seletor | Base | Ferramentas | Observações |
|---|---|---|---|
| Qwen 30B (geral) | 30B | pesquisa na web, imagem | prompt com o método do `build.md` adaptado a conversa (passos, pesquisa automática, anti-loop) |
| Qwen 8B (rápido) | 8B | pesquisa na web, imagem | **mesmo método**, versão enxuta para 8B (ver Fase 8) |
| Advogado Revisional | 30B | núcleo `revisor` + pesquisa | conduz as 12 etapas, mostra `[ETAPA n/12]`, pendências e próximo passo |
| Revisor: Extração / Cálculo / Auditoria / Encargos / Relatório | 30B | núcleo `revisor` | uso isolado de cada especialista |
| Revisor: Jurídico | 30B | pesquisa na web (só fontes oficiais) + `fontes` | nunca inventa precedente: tribunal, processo, relator, data, tese e link, ou `JURISPRUDÊNCIA NÃO LOCALIZADA NA PESQUISA REALIZADA.` |
| Revisor: Anti-alucinação | 30B | nenhuma | último filtro antes da entrega |

- [ ] **Context7** (documentação de bibliotecas): ligar o MCP remoto `https://mcp.context7.com/mcp` como ferramenta nos modelos gerais (30B e 8B). Já está ativo no OpenCode (`templates/opencode.json.tpl`). Sem chave = limite gratuito; se o usuário fornecer chave, vai só no `.env`.
- [ ] Comandos `/revisor:*` viram **Prompts salvos** (`/iniciar`, `/analisar`, `/auditar`, `/pesquisar`, `/relatorio`).
- [ ] Skills do repositório entram como trecho de prompt de cada modelo.
- [ ] **Limite conhecido:** o Open WebUI não delega entre agentes como o `task` do OpenCode. O "Advogado Revisional" chama as ferramentas na ordem; os especialistas ficam à disposição para escolha manual.
- [ ] Ferramentas de execução de comando/arquivo **não** são ligadas ao modelo geral; só ao agente jurídico, e só via servidor de ferramentas restrito.
- **Aceite:** os modelos aparecem no seletor; um caso de exemplo roda do upload ao relatório com `[ETAPA]` visível; dado ausente aparece como sentinela, nunca como zero.

### Fase 7 — Rede, HTTPS e acesso `[ ]`
- [ ] Novo `server` no nginx (ex.: `chat.SEU_DOMINIO` ou `/chat/`) com HTTPS, `proxy_read_timeout` alto, WebSocket habilitado, limite de upload (50 MB).
- [ ] Bloquear acesso à porta 3000 por fora (só `127.0.0.1`).
- [ ] Usuários: o admin cria as contas; papel `user` para os demais; ferramentas sensíveis restritas por grupo.
- [ ] **Decidido pelo usuário (10/11):** ao final, `SEU_DOMINIO` passa a abrir o Open WebUI no lugar da tela embutida do llama-server; o caminho `/v1` continua indo para o llama-server (OpenCode e API key sem mudança). O domínio hoje é servido por túnel Cloudflare (dockflare), não por nginx. Fazer a troca só depois do teste completo e avisar antes.
- **Aceite:** acesso externo por HTTPS funciona; `curl` sem login não vê nada; a API do modelo continua protegida pela mesma chave.

### Fase 8 — Prompt do 8B (método do 30B) `[ ]`
- [ ] Adaptar `templates/prompts/build.md` para conversa e para 8B: instruções mais curtas, menos passos obrigatórios, exemplos explícitos, pesquisa automática quando faltar fato, regra anti-loop (não repetir a mesma ferramenta/consulta mais de 2 vezes).
- [ ] Rodar um conjunto pequeno de perguntas e tarefas comparando 8B puro × 8B com o prompt.
- **Aceite:** melhora medida no conjunto (sem regressão em velocidade de primeiro token: meta ≤ 3 s com 10–20 usuários).

### Fase 9 — Validação final e entrega `[ ]`
- [ ] Teste de carga do chat (`deploy/loadtest.py`, 20 simultâneas) — só com o servidor ocioso.
- [ ] Teste de ponta a ponta: login → pergunta com pesquisa → imagem → upload de PDF/Word/escaneado → caso do Advogado Revisional → relatório.
- [ ] Backup automático dos dados do Open WebUI (`~/webui/data`) e dos casos.
- [ ] README atualizado (`SEU_SERVIDOR`, sem senhas) e commit **só quando o usuário pedir**.

## 4. Segurança (checklist)

- [ ] `ENABLE_SIGNUP=false`; admin com senha forte; 2º fator se disponível.
- [ ] Chave da API só em `.env` (`600`); nada no repositório; `grep` por senhas antes de qualquer commit.
- [ ] Servidor de ferramentas: pasta isolada, sem shell, sem env livre, usuário sem privilégios, serviço restrito.
- [ ] Documentos de cliente nunca vão para repositório nem para serviços externos; SearXNG não recebe o conteúdo dos documentos, só termos de busca que o modelo montar (instrução explícita no prompt jurídico para **não** colocar nomes, CPFs ou valores de cliente na busca).
- [ ] Imagens de contêineres com versão fixada; atualizações planejadas, não automáticas.
- [ ] Monitorar a 3090 (temperatura e Xid) — `/var/log/gpu-monitor.csv`.

## 5. Decisões e riscos em aberto

1. **Embeddings/RAG do Open WebUI:** o modelo de embeddings padrão consome CPU/RAM. Opções: desligar RAG local e usar só extração de texto do arquivo (recomendado para começar), ou rodar um embedding pequeno na 3060 que sobrar.
2. **Fila do 30B (`parallel 1`):** se o uso crescer, avaliar `parallel 2` com contexto menor.
3. **Pull request no repositório `advogado-revisional`** com as correções de segurança e formato OpenCode × cópia adaptada local: pendente de decisão do usuário.
4. **Qualidade jurídica:** o 30B pesquisa e resume bem, mas o relatório sempre precisa de revisão por advogado habilitado; o sistema não emite parecer.
5. **Estabilidade da 3090:** nova queda exige reiniciar o servidor e, possivelmente, revisar cabos/temperatura.

## 6. Ordem de execução

`Fase 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9`. Fases 1 e 2 podem andar juntas; 4 e 8 não rodam durante benchmark ou teste de carga.

## 7. Registro

| Data | Fase | O que foi feito | Resultado |
|---|---|---|---|
| 10/11 | 0 | Docker e SearXNG (`:8888`) já existiam; 80 GB livres | ok |
| 10/11 | 1 | Tesseract `por`, poppler, LibreOffice (`libreoffice-writer-nogui`), venv com pypdf/python-docx/openpyxl/pytesseract | `revisor doctor`: PDF, DOCX, XLSX e OCR disponíveis |
| 10/11 | 2 | Open WebUI **v0.13.3** em `127.0.0.1:3000` (`deploy/webui/`), admin criado, cadastro fechado, 30B e 8B ligados | chat responde; `/api` exige login |
| 10/11 | 3 | Pesquisa via SearXNG, ligada por padrão nos modelos | pergunta de fato recente respondeu certo, com fonte |
| 11/11 | 4 | Imagem pelo ComfyUI (RealVisXL + RealESRGAN, 3840×2160) | imagem aparece no chat; ~4 min por imagem (ampliação 4K); arquivo em `~/IA/output/webui_*.png` |
| 10/11 | 5 | Servidor de ferramentas `revisor` (`deploy/revisor/`, `:8890`, serviço `systemd --user` + linger) | 78 testes do núcleo ok; sem chave = 401; travessia de caminho contida; PDF, `.doc` e PDF escaneado (OCR) lidos |
| 10/11 | 6 | 12 modelos no seletor (`webui/configurar.py`): Qwen 30B, Qwen 8B, Advogado Revisional + 7 revisores; Context7 (MCP); subagentes ligados | pela interface: taxa implícita 1,44% vinda do núcleo; contrato PDF anexado → caso criado, extraído e auditado |
| 11/11 | 8 | Prompt do 8B | ver limitação abaixo |
| 11/11 | — | `deploy/instalar-servidor.sh` (tudo de uma vez, idempotente), `deploy/backup.sh`, `deploy/restaurar.sh` | instalador rodado de ponta a ponta; backup de 12 MB gerado |

### O que mudou em relação ao plano

- **Open WebUI 0.13 tem subagentes e MCP nativos.** O "Advogado Revisional" tem os 7 revisores cadastrados como subagentes (`meta.subagents`), então a delegação existe. Não foi medido o quanto o 30B delega sozinho; o fluxo testado usa as ferramentas do núcleo direto.
- **As ferramentas do modelo são anexadas pela interface**, não pela API: uma chamada crua a `/api/chat/completions` sem `tool_ids` deixa o modelo sem ferramentas (e ele inventa número). Testes automáticos devem ir pela interface (`~/webui/ui.py`, Playwright) ou mandar `tool_ids`.
- **Ferramentas embutidas cortadas por modelo** (`meta.builtinTools`): todas ligadas somam ~8.000 tokens em cada mensagem. Ficam só hora, arquivos e, conforme o modelo, pesquisa, imagem e subagentes.
- **O 8B é chat puro, sem ferramentas.** O `llama-chat` divide 57.344 tokens em 16 vagas = **3.584 tokens por conversa**; não cabem as ferramentas nem resultados de busca. Para dar pesquisa/imagem ao 8B é preciso reduzir as vagas (ex.: 4 × 14.336) em `deploy/apply-chat.sh` — decisão do usuário, porque troca capacidade simultânea por contexto.
- **PDF escaneado:** o núcleo `revisor` não aciona OCR sozinho em PDF sem texto. O servidor de ferramentas detecta (menos de 200 caracteres no `pdftotext`) e gera `<nome>.ocr.txt` com Tesseract, avisando para conferir os números no original.
- **Anexos do chat chegam ao núcleo por `importar_documento`**, que copia de `~/webui/data/uploads` pelo nome do arquivo (só anexos das últimas 24 h). Limitação: usuários diferentes com arquivos de mesmo nome podem colidir; hoje todos os usuários são de confiança.
- **Embeddings:** mesmo com `BYPASS_EMBEDDING_AND_RETRIEVAL=true` o contêiner baixa o modelo `all-MiniLM-L6-v2` na primeira subida (uso de RAM do contêiner: ~750 MB).
- **Domínio:** `SEU_DOMINIO` não está nas regras do Dockflare; a rota foi criada no painel da Cloudflare. A troca da Fase 7 precisa de duas regras no túnel, nesta ordem: `SEU_DOMINIO` com caminho `^/v1` → `http://SEU_SERVIDOR:8081`; `SEU_DOMINIO` (resto) → `http://127.0.0.1:3000` (ou `http://open-webui:8080` se o contêiner entrar na rede `cloudflare-net`).

### Achados no repositório `advogado-revisional` (não corrigidos lá)

- `numero_parcelas` é formatado como dinheiro no resumo do `analisar` (`R$ 48,00`).
- `ler_pdf` não cai para OCR quando o PDF não tem texto (existe `ocr_de_pdf`, mas não é chamado nesse caminho).
- Agentes/tools do bundle `.opencode/` fora do formato do OpenCode e `revisor_arquivo.ts`/`revisor_cli.ts` com os problemas de segurança já relatados.
