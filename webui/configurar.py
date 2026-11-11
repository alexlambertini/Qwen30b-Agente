#!/usr/bin/env python3
"""Configura o Open WebUI (>= 0.13) pela API: servidores de ferramentas, subagentes e modelos do seletor.

uso (no servidor):  python3 webui/configurar.py [--url http://127.0.0.1:3000]
Le o token do admin em ~/webui/.token e a chave do servidor de ferramentas em ~/revisor/chave.
Nao contem segredos. Pode ser rodado de novo: atualiza o que ja existe.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
HOME = Path.home()
ap = argparse.ArgumentParser()
ap.add_argument("--url", default="http://127.0.0.1:3000")
ap.add_argument("--revisor-url", default=None, help="URL do servidor de ferramentas (padrao: IP do Tailscale, porta 8890)")
ap.add_argument("--base-30b", default="qwen3-coder-30b-a3b")
ap.add_argument("--base-8b", default="qwen3-8b-chat")
ap.add_argument("--comfyui", default=None, help="URL do ComfyUI (padrao: IP do Tailscale, porta 8188)")
ap.add_argument("--galeria", default=None, help="URL da galeria de imagens (padrao: IP do Tailscale, porta 8189)")
ap.add_argument("--sem-4k", action="store_true", help="imagem na resolucao nativa, sem ampliar para 4K")
A = ap.parse_args()
TOKEN = (HOME / "webui/.token").read_text().strip()


def api(metodo, caminho, corpo=None):
    req = urllib.request.Request(A.url + caminho, method=metodo,
                                 data=None if corpo is None else json.dumps(corpo).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            t = r.read().decode()
            return json.loads(t) if t.strip() else None
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ERRO {metodo} {caminho}: {e.code} {e.read().decode()[:400]}")


PUBLICO = [{"principal_type": "user", "principal_id": "*", "permission": "read"}]

# ---------------------------------------------------------------- 0. conexoes dos modelos (valem sobre o .env depois da 1a subida)
host = "http://" + subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True).stdout.split()[0]
env = dict(l.strip().split("=", 1) for l in (HOME / "webui/.env").read_text().splitlines() if "=" in l and not l.startswith("#"))
urls = env["OPENAI_API_BASE_URLS"].split(";"); chaves = env["OPENAI_API_KEYS"].split(";")
api("POST", "/openai/config/update", {"ENABLE_OPENAI_API": True, "OPENAI_API_BASE_URLS": urls, "OPENAI_API_KEYS": chaves,
                                      "OPENAI_API_CONFIGS": {str(i): {"enable": True} for i in range(len(urls))}})
print("modelos base:", urls)

# ---------------------------------------------------------------- 1. servidores de ferramentas
ip = A.revisor_url or host + ":8890"
chave = (HOME / "revisor/chave").read_text().strip()
servidores = [
    {"url": ip, "path": "openapi.json", "type": "openapi", "auth_type": "bearer", "key": chave,
     "config": {"enable": True, "access_grants": PUBLICO},
     "info": {"id": "revisor", "name": "Advogado Revisional (nucleo)",
              "description": "Extracao, calculo, auditoria e relatorio de contratos bancarios"}},
    {"url": "https://mcp.context7.com/mcp", "path": "", "type": "mcp", "auth_type": "none", "key": "",
     "config": {"enable": True, "access_grants": PUBLICO},
     "info": {"id": "context7", "name": "Context7", "description": "Documentacao atualizada de bibliotecas e frameworks"}},
]
atuais = api("GET", "/api/v1/configs/tool_servers")["TOOL_SERVER_CONNECTIONS"] or []
ids = {s["info"]["id"] for s in servidores}
resto = [c for c in atuais if (c.get("info") or {}).get("id") not in ids]
api("POST", "/api/v1/configs/tool_servers", {"TOOL_SERVER_CONNECTIONS": resto + servidores})
print("ferramentas:", [c["info"]["id"] for c in servidores])

# ---------------------------------------------------------------- 2. subagentes
sub = api("GET", "/api/v1/configs/subagents")
sub.update({"ENABLE_SUBAGENTS": True, "SUBAGENTS_BACKGROUND_ENABLED": False, "SUBAGENTS_MAX_CONCURRENT": 1})
api("POST", "/api/v1/configs/subagents", sub)
print("subagentes: ligados (1 por vez: o 30B atende uma resposta de cada vez)")

# ---------------------------------------------------------------- 3. modelos
GALERIA = A.galeria or ip.rsplit(":", 1)[0] + ":8189"


def prompt(nome):
    return (RAIZ / "modelos" / nome).read_text().replace("{{GALERIA}}", GALERIA)


REGRAS_REVISOR = re.search(r"REGRAS INEGOCIAVEIS.*?(?=\nFLUXO)", prompt("advogado-revisional.md"), re.S).group(0)
AGENTES = HOME / "revisor/nucleo/.opencode/agents"


def especialista(arquivo):
    corpo = (AGENTES / arquivo).read_text()
    corpo = re.sub(r"^---.*?---\s*", "", corpo, count=1, flags=re.S)
    corpo = corpo.replace("revisor_cli", "as ferramentas do nucleo").replace("revisor_fontes", "a ferramenta `fontes` e a pesquisa na web")
    return ("Voce e um especialista do ADVOGADO REVISIONAL (apoio tecnico; nao emite parecer). Responda em portugues do Brasil, "
            "tecnico e seco. Voce NAO faz conta de cabeca: todo numero vem das ferramentas do nucleo chamadas nesta conversa.\n\n"
            + REGRAS_REVISOR + "\n\n" + corpo.strip() + "\n\nANTI-LOOP: nao repita a mesma ferramenta com os mesmos argumentos.")


TODAS_EMBUTIDAS = ("time", "user_input", "files", "knowledge", "chats", "subagents", "memory", "web_search", "image_generation",
                   "code_interpreter", "notes", "channels", "skills", "tools", "tasks", "automations", "calendar", "notifications")


def modelo(id_, nome, base, sistema, desc, ferramentas=(), web=True, imagem=True, subagentes=(), temp=None, simples=False):
    """simples=True: chat puro, sem nenhuma ferramenta (para modelo com contexto curto por vaga, como o 8B em 16 slots)."""
    meta = {"description": desc, "toolIds": list(ferramentas), "profile_image_url": "/static/favicon.png",
            "capabilities": {"vision": False, "file_upload": True, "web_search": web, "image_generation": imagem,
                             "code_interpreter": False, "citations": True, "status_updates": True, "usage": True},
            "defaultFeatureIds": (["web_search"] if web else []) + (["image_generation"] if imagem else [])}
    # so as ferramentas embutidas que o modelo usa: cada definicao a mais gasta contexto em TODA mensagem
    ligadas = {"time", "files"} | ({"web_search"} if web else set()) | ({"image_generation"} if imagem else set()) | ({"subagents"} if subagentes else set())
    meta["builtinTools"] = {k: (k in ligadas and not simples) for k in TODAS_EMBUTIDAS}
    if simples:
        meta["capabilities"].update({"builtin_tools": False, "web_search": False, "image_generation": False, "file_upload": False})
        meta["defaultFeatureIds"] = []
    if subagentes:
        meta["subagents"] = {"model_ids": list(subagentes)}
    params = {"system": sistema, "function_calling": "default" if simples else "native"}
    if temp is not None:
        params["temperature"] = temp
    corpo = {"id": id_, "base_model_id": base, "name": nome, "meta": meta, "params": params,
             "access_grants": PUBLICO, "is_active": True}
    try:
        req_ok = api("POST", "/api/v1/models/create", corpo)
    except SystemExit:
        req_ok = api("POST", f"/api/v1/models/model/update?id={id_}", corpo)
    print("modelo:", id_, "ok" if req_ok else "?")


REV = ["server:revisor"]
C7 = ["server:mcp:context7"]
ESPEC = [
    ("revisor-extracao", "Revisor: Extracao", "revisor-extracao.md", "Extrai os dados do contrato com fonte e nivel de confianca", REV, False),
    ("revisor-calculo", "Revisor: Calculo", "revisor-calculo.md", "Price, SAC, equivalencias, CET e taxa implicita", REV, False),
    ("revisor-auditoria", "Revisor: Auditoria", "revisor-auditoria.md", "Confere parcelas, taxas, encargos e evolucao", REV, False),
    ("revisor-encargos", "Revisor: Encargos", "revisor-encargos.md", "Mora, multa, comissao de permanencia e tarifas", REV, False),
    ("revisor-juridico", "Revisor: Juridico", "revisor-juridico.md", "Legislacao e jurisprudencia so em fonte oficial", REV, True),
    ("revisor-relatorio", "Revisor: Relatorio", "revisor-relatorio.md", "Gera o relatorio de 20 secoes apos a auditoria interna", REV, False),
    ("revisor-antialucinacao", "Revisor: Anti-alucinacao", "revisor-antialucinacao.md", "Revisa o texto final contra as regras anti-alucinacao", [], False),
]
for id_, nome, arq, desc, ferr, web in ESPEC:
    modelo(id_, nome, A.base_30b, especialista(arq), desc, ferr, web=web, imagem=False, temp=0.2)

modelo("advogado-revisional", "Advogado Revisional", A.base_30b, prompt("advogado-revisional.md"),
       "Conduz a analise revisional de contrato bancario em 12 etapas (anexe o contrato em PDF ou Word)",
       REV, web=True, imagem=False, subagentes=[e[0] for e in ESPEC], temp=0.2)
modelo("qwen-30b", "Qwen 30B", A.base_30b, prompt("geral-30b.md"),
       "Modelo principal: programacao, pesquisa na web, documentacao e imagem", C7, temp=0.4)
modelo("qwen-8b", "Qwen 8B (rapido)", A.base_8b, prompt("rapido-8b.md"),
       "Chat rapido, sem ferramentas (contexto curto); para pesquisa, imagem, arquivos e tarefas dificeis use o Qwen 30B",
       [], temp=0.5, simples=True)
# ---------------------------------------------------------------- 4. ordem e modelo inicial do seletor
ordem = ["qwen-30b", "qwen-8b", "advogado-revisional"] + [e[0] for e in ESPEC] + [A.base_30b, A.base_8b]
cfg = api("GET", "/api/v1/configs/models")
cfg.update({"DEFAULT_MODELS": "qwen-30b", "DEFAULT_PINNED_MODELS": "qwen-30b,qwen-8b,advogado-revisional", "MODEL_ORDER_LIST": ordem})
api("POST", "/api/v1/configs/models", cfg)
print("seletor: inicial = qwen-30b; ordem definida")
# ---------------------------------------------------------------- 5. imagem no chat (ComfyUI, SDXL + ampliacao 4K)
comfy = A.comfyui or ip.rsplit(":", 1)[0] + ":8188"


def opcoes(no, campo):
    try:
        d = json.load(urllib.request.urlopen(f"{comfy}/object_info/{no}", timeout=15))
        v = d[no]["input"]["required"][campo]
        return v[1]["options"] if v[0] == "COMBO" else v[0]
    except Exception as e:
        print(f"imagem: ComfyUI indisponivel em {comfy} ({e}); etapa pulada")
        return None


ckpts = opcoes("CheckpointLoaderSimple", "ckpt_name")
if ckpts:
    ckpt = next((c for c in ckpts if "realvis" in c.lower()), ckpts[0])
    ups = [] if A.sem_4k else (opcoes("UpscaleModelLoader", "model_name") or [])
    g = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": "blurry, low quality, lowres, jpeg artifacts, watermark, signature, text, deformed, bad anatomy, extra fingers"}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 1344, "height": 768, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"seed": 0, "steps": 28, "cfg": 6.0, "sampler_name": "dpmpp_2m", "scheduler": "karras",
                                                   "denoise": 1.0, "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
    }
    final = ["6", 0]
    if ups:
        g["7"] = {"class_type": "UpscaleModelLoader", "inputs": {"model_name": ups[0]}}
        g["8"] = {"class_type": "ImageUpscaleWithModel", "inputs": {"upscale_model": ["7", 0], "image": ["6", 0]}}
        g["9"] = {"class_type": "ImageScale", "inputs": {"image": ["8", 0], "upscale_method": "lanczos", "width": 3840, "height": 2160, "crop": "center"}}
        final = ["9", 0]
    g["10"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": "webui", "images": final}}
    img = api("GET", "/api/v1/images/config")
    img.update({"ENABLE_IMAGE_GENERATION": True, "ENABLE_IMAGE_PROMPT_GENERATION": False, "IMAGE_GENERATION_ENGINE": "comfyui",
                "IMAGE_GENERATION_MODEL": ckpt, "IMAGE_SIZE": "1344x768", "IMAGE_STEPS": 28,
                "COMFYUI_BASE_URL": comfy, "COMFYUI_WORKFLOW": json.dumps(g),
                "COMFYUI_WORKFLOW_NODES": [
                    {"type": "prompt", "key": "text", "node_ids": ["2"]},
                    {"type": "model", "key": "ckpt_name", "node_ids": ["1"]},
                    {"type": "width", "key": "width", "node_ids": ["4"]},
                    {"type": "height", "key": "height", "node_ids": ["4"]},
                    {"type": "steps", "key": "steps", "node_ids": ["5"]},
                    {"type": "seed", "key": "seed", "node_ids": ["5"]}]})
    api("POST", "/api/v1/images/config/update", img)
    print(f"imagem: ComfyUI {comfy}, modelo {ckpt}, " + (f"ampliada para 3840x2160 com {ups[0]}" if ups else "1344x768 (sem modelo de upscale)"))
print("pronto")
