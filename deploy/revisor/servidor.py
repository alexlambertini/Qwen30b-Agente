"""Servidor de ferramentas do ADVOGADO REVISIONAL para o Open WebUI (OpenAPI).

Expoe o nucleo deterministico `revisor` (github.com/alexlambertini/advogado-revisional)
como ferramentas HTTP. Regras de seguranca:
  - nenhum shell: o nucleo e chamado com lista de argumentos (shell=False);
  - nenhuma variavel de ambiente vinda do modelo;
  - todo caminho e resolvido DENTRO da pasta do caso (sem '..', sem link para fora);
  - autenticacao por chave (Bearer) lida de arquivo com permissao 600.

Variaveis de ambiente (definidas pelo servico, nunca pelo modelo):
  REVISOR_NUCLEO   pasta do repositorio advogado-revisional (contem src/revisor)
  REVISOR_CASOS    pasta onde ficam os casos
  REVISOR_UPLOADS  pasta de uploads do Open WebUI (somente leitura)
  REVISOR_CHAVE    arquivo com a chave de acesso
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

NUCLEO = Path(os.environ["REVISOR_NUCLEO"]).resolve()
CASOS = Path(os.environ["REVISOR_CASOS"]).resolve()
UPLOADS = Path(os.environ.get("REVISOR_UPLOADS", "/nonexistent")).resolve()
CHAVE = Path(os.environ["REVISOR_CHAVE"]).read_text().strip()

EXT_OK = {".pdf", ".docx", ".doc", ".xlsx", ".csv", ".txt", ".md", ".json", ".png", ".jpg", ".jpeg"}
MAX_BYTES = 50 * 1024 * 1024
MAX_SAIDA = 24000          # caracteres devolvidos ao modelo por chamada
JANELA_UPLOAD_H = 24       # so importa uploads recentes do chat

app = FastAPI(
    generate_unique_id_function=lambda rota: rota.name,   # nome da ferramenta = nome da funcao
    title="Advogado Revisional",
    version="1.0.0",
    description="Nucleo deterministico de analise revisional de contratos bancarios: "
                "extrai dados com fonte, recalcula, audita e gera relatorio. "
                "Os numeros vem SEMPRE destas ferramentas, nunca do modelo.",
)


def auth(request: Request) -> None:
    h = request.headers.get("authorization", "")
    if not (h.startswith("Bearer ") and h[7:].strip() == CHAVE):
        raise HTTPException(status_code=401, detail="chave invalida")


def _slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9_-]+", "-", t).strip("-").lower()
    if not t:
        raise HTTPException(400, "identificador de caso vazio")
    return t[:60]


def _caso(caso: str, criar: bool = False) -> Path:
    p = (CASOS / _slug(caso)).resolve()
    if p.parent != CASOS:
        raise HTTPException(400, "caso invalido")
    if criar:
        for sub in ("documentos", "saida"):
            (p / sub).mkdir(parents=True, exist_ok=True)
    elif not p.is_dir():
        raise HTTPException(404, f"caso '{_slug(caso)}' nao existe; crie com /casos")
    return p


def _nome_seguro(nome: str) -> str:
    base = Path(nome).name
    base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode()
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base).lstrip(".")
    if not base or Path(base).suffix.lower() not in EXT_OK:
        raise HTTPException(400, f"tipo de arquivo nao aceito: {nome!r} (aceitos: {sorted(EXT_OK)})")
    return base[:120]


def _revisor(args: List[str], cwd: Path, timeout: int = 600) -> str:
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "PYTHONPATH": str(NUCLEO / "src"),
           "LANG": "C.UTF-8", "HOME": str(CASOS)}
    try:
        r = subprocess.run([sys.executable, "-I", "-c",
                            "import sys; sys.path.insert(0, sys.argv.pop(1)); "
                            "from revisor.cli import main; sys.exit(main(sys.argv[1:]))",
                            str(NUCLEO / "src"), *args],
                           cwd=str(cwd), env=env, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "o nucleo demorou demais")
    saida = (r.stdout or "").strip()
    if r.returncode != 0:
        saida = (saida + "\n" if saida else "") + f"[nucleo saiu com codigo {r.returncode}] " + (r.stderr or "").strip()[-2000:]
    return saida


def _cortar(texto: str, inicio: int = 0) -> dict:
    parte = texto[inicio:inicio + MAX_SAIDA]
    resto = len(texto) - (inicio + len(parte))
    d = {"texto": parte}
    if resto > 0:
        d["continua_em"] = inicio + len(parte)
        d["aviso"] = f"saida truncada: faltam {resto} caracteres; chame de novo com inicio={inicio + len(parte)}"
    return d


def _converter_doc(pasta: Path) -> List[str]:
    """Converte .doc (Word antigo) para .docx com o LibreOffice, sem shell."""
    avisos = []
    soffice = shutil.which("soffice")
    for doc in sorted(pasta.glob("*.doc")):
        if doc.with_suffix(".docx").exists():
            continue
        if not soffice:
            avisos.append(f"{doc.name}: LibreOffice ausente, .doc nao convertido")
            continue
        try:
            subprocess.run([soffice, "--headless", "--convert-to", "docx", "--outdir", str(pasta), str(doc)],
                           cwd=str(pasta), capture_output=True, timeout=180,
                           env={"PATH": "/usr/bin:/bin", "HOME": str(pasta.parent / "saida")})
        except subprocess.TimeoutExpired:
            avisos.append(f"{doc.name}: conversao demorou demais")
        if not doc.with_suffix(".docx").exists():
            avisos.append(f"{doc.name}: falha ao converter para .docx")
    return avisos


def _ocr_pdfs(pasta: Path, max_paginas: int = 80) -> List[str]:
    """PDF escaneado (sem camada de texto): OCR em portugues, gravado como <nome>.ocr.txt ao lado."""
    avisos = []
    amb = {"PATH": "/usr/bin:/bin", "HOME": str(pasta.parent / "saida"), "OMP_THREAD_LIMIT": "1"}
    for pdf in sorted(pasta.glob("*.pdf")):
        alvo = pdf.with_name(pdf.stem + ".ocr.txt")
        if alvo.exists():
            continue
        try:
            txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True,
                                 timeout=120, env=amb).stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            txt = ""
        if len(txt.strip()) >= 200:
            continue                      # tem texto de verdade: o nucleo le direto
        tmp = pasta.parent / "saida" / ("ocr-" + pdf.stem)
        shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir(parents=True)
        try:
            subprocess.run(["pdftoppm", "-r", "200", "-gray", "-png", "-l", str(max_paginas), str(pdf), str(tmp / "p")],
                           capture_output=True, timeout=600, env=amb)
            partes = []
            for i, img in enumerate(sorted(tmp.glob("p*.png")), 1):
                r = subprocess.run(["tesseract", str(img), "stdout", "-l", "por"], capture_output=True, text=True,
                                   timeout=180, env=amb)
                partes.append(f"[PAGINA {i} - OCR]\n{r.stdout.strip()}")
            texto = "\n\n\f".join(partes)
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            texto = ""; avisos.append(f"{pdf.name}: OCR falhou ({type(e).__name__})")
        shutil.rmtree(tmp, ignore_errors=True)
        if len(texto.strip()) >= 50:
            alvo.write_text(texto, encoding="utf-8")
            avisos.append(f"{pdf.name}: PDF escaneado, texto obtido por OCR ({len(partes)} pagina(s)) em {alvo.name}. "
                          "OCR pode errar digitos: CONFIRA no original todo numero vindo deste arquivo.")
        elif not any(pdf.name in a for a in avisos):
            avisos.append(f"{pdf.name}: sem texto e o OCR nao reconheceu nada")
    return avisos


# ------------------------------------------------------------------ casos
class NovoCaso(BaseModel):
    referencia: str = Field(..., description="Referencia do caso, ex.: PROC-0001 ou nome curto do cliente")


@app.post("/casos", dependencies=[Depends(auth)], summary="Cria (ou reabre) a pasta de um caso")
def criar_caso(d: NovoCaso):
    p = _caso(d.referencia, criar=True)
    return {"caso": p.name, "documentos": sorted(x.name for x in (p / "documentos").iterdir())}


@app.get("/casos", dependencies=[Depends(auth)], summary="Lista os casos existentes e seus documentos")
def listar_casos():
    out = []
    for p in sorted(CASOS.iterdir()) if CASOS.is_dir() else []:
        if p.is_dir() and (p / "documentos").is_dir():
            out.append({"caso": p.name,
                        "documentos": sorted(x.name for x in (p / "documentos").iterdir()),
                        "tem_estudo": (p / "estudo.json").exists(),
                        "tem_relatorio": (p / "saida" / "relatorio.md").exists()})
    return {"casos": out}


class Importar(BaseModel):
    caso: str = Field(..., description="Identificador do caso")
    nome_arquivo: str = Field(..., description="Nome do arquivo que o usuario anexou no chat, ex.: contrato.pdf")


@app.post("/documentos/importar", dependencies=[Depends(auth)],
          summary="Copia para o caso um arquivo que o usuario anexou no chat (PDF, DOCX, DOC, XLSX, CSV, TXT, imagem)")
def importar_documento(d: Importar):
    p = _caso(d.caso, criar=True)
    alvo = _nome_seguro(d.nome_arquivo)
    if not UPLOADS.is_dir():
        raise HTTPException(500, "pasta de uploads do chat indisponivel")
    limite = time.time() - JANELA_UPLOAD_H * 3600
    candidatos = []
    for f in UPLOADS.iterdir():
        if not f.is_file() or f.is_symlink() or f.stat().st_mtime < limite:
            continue
        original = f.name.split("_", 1)[1] if "_" in f.name else f.name   # <uuid>_<nome>
        try:
            if _nome_seguro(original) == alvo:
                candidatos.append(f)
        except HTTPException:
            continue
    if not candidatos:
        raise HTTPException(404, f"nenhum anexo recente chamado {d.nome_arquivo!r}; peca ao usuario para anexar o arquivo no chat")
    origem = max(candidatos, key=lambda f: f.stat().st_mtime)
    if origem.stat().st_size > MAX_BYTES:
        raise HTTPException(413, "arquivo maior que 50 MB")
    destino = p / "documentos" / alvo
    shutil.copyfile(origem, destino)
    return {"caso": p.name, "importado": alvo, "bytes": destino.stat().st_size,
            "documentos": sorted(x.name for x in (p / "documentos").iterdir())}


class Texto(BaseModel):
    caso: str
    nome_arquivo: str = Field(..., description="Nome com extensao .txt, ex.: contrato.txt")
    conteudo: str = Field(..., description="Texto integral do documento, copiado sem alterar nada")


@app.post("/documentos/texto", dependencies=[Depends(auth)],
          summary="Grava no caso um documento em texto puro (use so quando nao houver arquivo anexado)")
def gravar_texto(d: Texto):
    p = _caso(d.caso, criar=True)
    nome = _nome_seguro(d.nome_arquivo)
    if Path(nome).suffix.lower() not in {".txt", ".md", ".csv"}:
        raise HTTPException(400, "use extensao .txt, .md ou .csv")
    if len(d.conteudo.encode()) > 5 * 1024 * 1024:
        raise HTTPException(413, "texto grande demais")
    (p / "documentos" / nome).write_text(d.conteudo, encoding="utf-8")
    return {"caso": p.name, "gravado": nome}


# ------------------------------------------------------------------ analise
class Analisar(BaseModel):
    caso: str
    responsavel: Optional[str] = Field(None, description="Nome do advogado responsavel (opcional)")


@app.post("/analisar", dependencies=[Depends(auth)],
          summary="Le todos os documentos do caso, extrai dados com fonte, recalcula e audita. Gera o estudo.")
def analisar(d: Analisar):
    p = _caso(d.caso)
    avisos = _converter_doc(p / "documentos")
    avisos += _ocr_pdfs(p / "documentos")
    args = ["analisar", "--pasta", "documentos", "--saida", "estudo.json", "--referencia", p.name]
    if d.responsavel:
        args += ["--responsavel", d.responsavel[:120]]
    if (p / "estudo.json").exists():
        (p / "estudo.json").replace(p / "estudo.anterior.json")
    r = _cortar(_revisor(args, p))
    if avisos:
        r["avisos_leitura"] = avisos
    return r


class Relatorio(BaseModel):
    caso: str
    forcar: bool = Field(False, description="So com ordem expressa do advogado: gera mesmo com bloqueios da auditoria interna")
    inicio: int = Field(0, description="Posicao inicial do texto, para continuar uma saida truncada")


@app.post("/relatorio", dependencies=[Depends(auth)],
          summary="Gera o relatorio de 20 secoes apos a auditoria interna de 10 checks (bloqueia se reprovar)")
def relatorio(d: Relatorio):
    p = _caso(d.caso)
    if not (p / "estudo.json").exists():
        raise HTTPException(409, "rode /analisar antes do relatorio")
    saida = p / "saida" / "relatorio.md"
    if d.inicio == 0:
        args = ["relatorio", "--estudo", "estudo.json", "--saida", "saida/relatorio.md"]
        if d.forcar:
            args.append("--forcar")
        msg = _revisor(args, p)
        if not saida.exists():
            return {"bloqueado": True, "texto": msg[-MAX_SAIDA:]}
    if not saida.exists():
        raise HTTPException(404, "relatorio ainda nao gerado")
    return _cortar(saida.read_text(encoding="utf-8"), max(0, d.inicio))


# ------------------------------------------------------------------ calculos isolados
class Equivalencia(BaseModel):
    taxa: str = Field(..., description="ex.: 2,0 (percentual ao mes)")
    para: str = Field(..., description="unidade de destino, ex.: anual-efetiva")


@app.post("/calcular/equivalencia", dependencies=[Depends(auth)], summary="Converte taxa entre unidades")
def calcular_equivalencia(d: Equivalencia):
    return _cortar(_revisor(["calcular", "equivalencia", "--taxa", d.taxa, "--para", d.para], CASOS, 60))


class NominalEfetiva(BaseModel):
    taxa: str
    periodos: int = 12


@app.post("/calcular/nominal-efetiva", dependencies=[Depends(auth)], summary="Taxa nominal para efetiva")
def calcular_nominal_efetiva(d: NominalEfetiva):
    return _cortar(_revisor(["calcular", "nominal-efetiva", "--taxa", d.taxa, "--periodos", str(d.periodos)], CASOS, 60))


class Cet(BaseModel):
    custo_total: str
    valor_liberado: str
    quantidade: int


@app.post("/calcular/cet", dependencies=[Depends(auth)], summary="Custo efetivo total")
def calcular_cet(d: Cet):
    return _cortar(_revisor(["calcular", "cet", "--custo-total", d.custo_total, "--valor-liberado", d.valor_liberado,
                             "--quantidade", str(d.quantidade)], CASOS, 60))


class TaxaImplicita(BaseModel):
    pv: str = Field(..., description="valor financiado")
    parcela: str
    quantidade: int
    antecipada: bool = False


@app.post("/calcular/taxa-implicita", dependencies=[Depends(auth)], summary="Recupera a taxa a partir da parcela")
def calcular_taxa_implicita(d: TaxaImplicita):
    a = ["calcular", "taxa-implicita", "--pv", d.pv, "--parcela", d.parcela, "--quantidade", str(d.quantidade)]
    if d.antecipada:
        a.append("--antecipada")
    return _cortar(_revisor(a, CASOS, 60))


class Amortizar(BaseModel):
    pv: str
    taxa: str = Field(..., description="taxa mensal, ex.: 2,0")
    quantidade: int
    sistema: str = Field("price", description="price ou sac")
    inicio: int = 0


@app.post("/amortizar", dependencies=[Depends(auth)], summary="Gera tabela Price ou SAC")
def amortizar(d: Amortizar):
    if d.sistema not in ("price", "sac"):
        raise HTTPException(400, "sistema deve ser price ou sac")
    return _cortar(_revisor(["amortizar", "--pv", d.pv, "--taxa", d.taxa, "--quantidade", str(d.quantidade),
                             "--sistema", d.sistema], CASOS, 60), max(0, d.inicio))


class Encargos(BaseModel):
    saldo: Optional[str] = None
    taxa_remuneratoria: Optional[str] = None
    juros_mora: Optional[str] = None
    multa: Optional[str] = None
    comissao_diaria: Optional[str] = None
    dias_atraso: Optional[int] = None


@app.post("/encargos", dependencies=[Depends(auth)], summary="Audita mora, multa, comissao de permanencia e tarifas")
def encargos(d: Encargos):
    a = ["encargos"]
    for flag, v in (("--saldo", d.saldo), ("--taxa-remuneratoria", d.taxa_remuneratoria), ("--juros-mora", d.juros_mora),
                    ("--multa", d.multa), ("--comissao-diaria", d.comissao_diaria),
                    ("--dias-atraso", None if d.dias_atraso is None else str(d.dias_atraso))):
        if v is not None:
            a += [flag, v]
    return _cortar(_revisor(a, CASOS, 60))


class Fontes(BaseModel):
    tipo: str = Field(..., description="jurisprudencia, legislacao ou taxas")
    topicos: List[str] = Field(default_factory=list, description="ex.: ['comissao de permanencia', 'capitalizacao de juros']")
    modalidade: Optional[str] = None


@app.post("/fontes", dependencies=[Depends(auth)],
          summary="Monta o PLANO de consulta a fontes oficiais (nao pesquisa sozinho; use a pesquisa na web para executar)")
def fontes(d: Fontes):
    if d.tipo not in ("jurisprudencia", "legislacao", "taxas"):
        raise HTTPException(400, "tipo invalido")
    a = ["fontes", "--tipo", d.tipo, "--offline"]
    for t in d.topicos[:12]:
        a += ["--topico", t[:120]]
    if d.modalidade:
        a += ["--modalidade", d.modalidade[:80]]
    return _cortar(_revisor(a, CASOS, 60))


@app.get("/saude", include_in_schema=False, summary="Diagnostico do nucleo (formatos de arquivo disponiveis)")
def saude():
    return {"ok": True}
