# 07 - Benchmark e ajuste do modelo

Objetivo: tirar o maximo do Qwen3-Coder-30B-A3B (Q4_K_M, 3090) em programacao, sem trocar de modelo.

## Metodo de medida
- `bench/run.sh`: cada tarefa roda no OpenCode real; o verificador fica **fora** do diretorio de trabalho (o agente nao ve o gabarito).
- Config isolada por `bench/mkconf.sh` (nao toca a instalacao). 7 tarefas dificeis x 3 rodadas.
- Armadilhas descobertas (ja corrigidas): `opencode run` trava sem `</dev/null` e `--standalone`; gerar imagem durante o benchmark causa `ECONNRESET` (2 CPUs e 7,5 GB de RAM); o servidor tem 1 slot, entao nada pode competir com o benchmark.

## O que chega ao modelo (capturado com um servidor falso)
- `temperature` do agente **nao e enviada**; so `provider.qwen.models.*.options` vai no corpo. Sampler final: temperature 0.3, top_p 0.8, top_k 20, repeat_penalty 1.05.
- O prompt do agente **substitui** o prompt base do OpenCode (system ~13-15 mil caracteres com AGENTS.md).

## Falhas observadas e correcao
| Falha | Causa observada | Correcao no `build.md` |
|---|---|---|
| t13: escrevia `Account.transfer(dst, amount)` em vez da funcao `transfer(src, dst, amount)` | copiava o estilo vizinho (metodos) e afirmava "funcao" no resumo | linha obrigatoria `CONTRATO:` com a assinatura como codigo; funcao no fim do arquivo, `def` na coluna 0; `grep "^def nome("` logo apos editar |
| t13: sem type hints | copiava a assinatura literal do pedido | exemplo do contrato com tipos: o pedido da nomes e ordem, as convencoes acrescentam os tipos |
| t9: alternava edicoes entre codigo e teste, criava 6 scripts avulsos, testes com relogio real | tentativa e erro em vez de calculo | recalcular o valor esperado a mao a partir do pedido; 2 correcoes sem sucesso = reescrever a funcao; proibido arquivo de teste extra; usar o relogio injetado |
| t8: respondia "versao mais recente" de memoria (inventada) | pesquisa so numa secao tardia do prompt | regra de pesquisa na **REGRA 0** (primeira acao = `websearch`) |
| t12: testes em arquivos avulsos | criava arquivo novo | testes no arquivo existente do modulo |

Resultado da bateria final (3 rodadas): t7 2/3, t8 3/3, t9 1/3, t10 2/3, t11 2/3, t12 2/3, t13 3/3 = **15/21** (config antiga: 15/21). Uma rodada intermediaria da config atual fez 16/21: a variacao entre rodadas e de 1 a 2 tarefas, entao so diferencas maiores que isso contam. Ganho solido: t13 (0/3 para 3/3) e t8 estavel.

## Modelos e quantizacao
- Q4_K_M (18,6 GB) cabe inteiro na 3090: ~90 tok/s, 3,4 s para 9 mil tokens de prompt.
- Q5_K_M (21,7 GB) dividido com a 3060 nº 2 nao chegou a subir em 7,5 min (carga lenta do arquivo com 7,5 GB de RAM) e ocuparia a placa do ComfyUI. Decisao: manter Q4_K_M.

## Agente web
Ver README secao 8. Tarefas `w1-landing`, `w2-fixpage`, `w3-form` com verificador de conteudo mais `qwen-layout`. Falha corrigida: o prompt chamava `qwen-layout` sem caminho e `~/.local/bin` nao estava no PATH, entao o agente ficava sem verificacao; verificadores ficaram tolerantes a acentos e ao idioma dos identificadores.

Resultado final do agente web: w1 3/3, w2 4/4, w3 4/4 (11/11), todas com `LAYOUT OK`. Outras correcoes: o `qwen-layout` marcava o padrao `.sr-only` (-9999px) como fora da tela (falso positivo, ignorado agora); o modelo declarava contraste 3.98 como "aceitavel" (prompt agora exige `LAYOUT OK` como unica condicao de entrega).

## Chat para varias pessoas
Qwen3-8B, 16 slots, 3584 tokens por conversa. 20 conversas simultaneas: 20/20 em 11,6 s, 1o token mediana 2,2 s, ~7,7 tok/s por pessoa, ~77 tok/s total (medido com o download de um modelo rodando ao mesmo tempo; pode melhorar).
