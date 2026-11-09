#!/usr/bin/env python3
"""Teste de carga do chat: N conversas simultaneas. uso: loadtest.py URL KEY [N=20] [MODEL]"""
import json, sys, time, threading, urllib.request
url, key = sys.argv[1].rstrip("/"), sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 20
model = sys.argv[4] if len(sys.argv) > 4 else "qwen3-8b-chat"
PERGUNTAS = ["Oi, quero saber o horario de atendimento de voces.", "Como faco para trocar um produto?",
             "Qual o prazo de entrega para Sao Paulo?", "Meu pedido atrasou, o que fazer?",
             "Voces parcelam no cartao? Em quantas vezes?"]
res = []
def um(i):
    msgs = [{"role": "system", "content": "Voce e um atendente simpatico e objetivo. Responda em portugues, em ate 4 frases."},
            {"role": "user", "content": PERGUNTAS[i % 5]}]
    t0 = time.time(); ttft = None; toks = 0
    try:
        req = urllib.request.Request(url + "/v1/chat/completions", json.dumps(
            {"model": model, "messages": msgs, "stream": True, "max_tokens": 200}).encode(),
            {"Content-Type": "application/json", "Authorization": "Bearer " + key})
        with urllib.request.urlopen(req, timeout=180) as r:
            for line in r:
                if line.startswith(b"data: ") and b"[DONE]" not in line:
                    d = json.loads(line[6:])["choices"][0]["delta"].get("content")
                    if d:
                        toks += 1
                        ttft = ttft or time.time() - t0
        res.append((ttft or 0, toks, time.time() - t0, None))
    except Exception as e:
        res.append((0, 0, time.time() - t0, str(e)[:60]))
ts = [threading.Thread(target=um, args=(i,)) for i in range(n)]
t0 = time.time(); [t.start() for t in ts]; [t.join() for t in ts]
ok = [r for r in res if not r[3]]
print(f"{len(ok)}/{n} ok em {time.time()-t0:.1f}s")
if ok:
    tps = sorted(r[1] / max(r[2] - r[0], 1e-3) for r in ok)
    tf = sorted(r[0] for r in ok)
    print(f"1o token: mediana {tf[len(tf)//2]:.2f}s  pior {tf[-1]:.2f}s | tok/s por pessoa: mediana {tps[len(tps)//2]:.1f}  pior {tps[0]:.1f} | total {sum(r[1] for r in ok)/(time.time()-t0):.0f} tok/s")
for r in res:
    if r[3]: print("erro:", r[3])
