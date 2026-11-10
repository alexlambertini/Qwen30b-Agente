#!/usr/bin/env python3
"""Mede tok/s de geracao e de prompt. uso: speedtest.py URL KEY"""
import json, sys, time, urllib.request
url, key = sys.argv[1].rstrip("/"), sys.argv[2]
def run(msg, n):
    t0 = time.time(); first = None; k = 0
    req = urllib.request.Request(url + "/v1/chat/completions", json.dumps({"model": "x", "messages": [{"role": "user", "content": msg}], "stream": True, "max_tokens": n, "temperature": 0}).encode(), {"Content-Type": "application/json", "Authorization": "Bearer " + key})
    for line in urllib.request.urlopen(req, timeout=600):
        if line.startswith(b"data: ") and b"[DONE]" not in line:
            d = json.loads(line[6:])["choices"][0]["delta"].get("content")
            if d: k += 1; first = first or time.time()
    return first - t0, k / max(time.time() - first, 1e-3)
for i in range(3): ttft, tps = run("Escreva uma funcao Python que implementa uma LRU cache com testes unittest.", 400); print(f"gen: 1o token {ttft:.2f}s, {tps:.1f} tok/s")
ttft, _ = run("Resuma: " + ("lorem ipsum dolor sit amet " * 1500), 8); print(f"prompt ~9k tokens: 1o token em {ttft:.1f}s")
