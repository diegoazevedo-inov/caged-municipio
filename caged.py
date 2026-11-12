#!/usr/bin/env python3
"""Análise reprodutível do Novo CAGED (microdados não identificados, PDET/MTE) por UF ou município.

Método (o mesmo da divulgação oficial do Novo CAGED):
  competência c "com ajustes declarados até V" =
      CAGEDMOV(c)
    + linhas de CAGEDFOR(f), f <= V, com competênciamov = c   (declaradas fora do prazo)
    - linhas de CAGEDEXC(f), f <= V, com competênciamov = c   (exclusões)
  competência c "sem ajuste" = CAGEDMOV(c).

Comandos:
  extrair   --uf 14 --ini 202510 --fim 202609
            lê os .7z do PDET (baixa se faltar), guarda as linhas da UF e o manifesto (SHA-256 de cada arquivo)
  agregar   --recorte uf:14 | mun:140010 --ini 202510 --fim 202609
            série mensal (com e sem ajuste) e tabela por ocupação (CBO 2002)
  conferir  --oficial dados/oficial/novo-caged-2026-09-uf14.csv --ini 202510 --fim 202609
            compara com os números publicados; sai com 1 se algum divergir

Cada execução grava um registro em execucoes/ (comando, versões, commit, SHA-256 de entradas e saídas).
"""
import argparse
import datetime as dt
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
import py7zr

RAIZ = Path(__file__).resolve().parent
BRUTOS = RAIZ / "dados" / "brutos"
LINHAS = RAIZ / "dados" / "linhas"
SAIDAS = RAIZ / "dados" / "saidas"
EXECUCOES = RAIZ / "execucoes"
FTP = "ftp://ftp.mtps.gov.br/pdet/microdados/NOVO%20CAGED"
# o servidor FTP do PDET nomeia em latin-1: "Layout Não-identificado Novo Caged Movimentação.xlsx"
URL_LAYOUT = f"{FTP}/Layout%20N%E3o-identificado%20Novo%20Caged%20Movimenta%E7%E3o.xlsx"

ADMISSAO = {10, 20, 25, 35, 70, 97}
DESLIGAMENTO = {31, 32, 33, 40, 43, 45, 50, 60, 80, 90, 98}
A_PEDIDO = 40
COLS = ["competênciamov", "uf", "município", "cbo2002ocupação", "saldomovimentação",
        "tipomovimentação", "salário", "unidadesaláriocódigo", "categoria", "indtrabintermitente"]
TIPOS = (("MOV", 1), ("FOR", 1), ("EXC", -1))


# ---------- utilidades ----------
def competencias(ini: str, fim: str):
    a, m = int(ini[:4]), int(ini[4:])
    while f"{a}{m:02d}" <= fim:
        yield f"{a}{m:02d}"
        m += 1
        if m == 13:
            a, m = a + 1, 1


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def commit() -> str:
    try:
        r = subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, check=True)
        sujo = subprocess.run(["git", "-C", str(RAIZ), "status", "--porcelain", "--", "caged.py"],
                              capture_output=True, text=True).stdout.strip()
        return r.stdout.strip() + ("+alterado" if sujo else "")
    except Exception:
        return "sem-git"


def rel(p: Path) -> str:
    try:
        return str(Path(p).relative_to(RAIZ))
    except ValueError:
        return Path(p).name


def registrar(comando: str, args: dict, entradas: list, saidas: list, resultado):
    EXECUCOES.mkdir(exist_ok=True)
    agora = dt.datetime.now().astimezone()
    reg = {
        "comando": comando, "argumentos": args, "inicio": agora.isoformat(timespec="seconds"),
        "commit": commit(), "python": platform.python_version(), "pandas": pd.__version__,
        "py7zr": py7zr.__version__,
        "entradas": {rel(p): sha256(p) for p in entradas},
        "saidas": {rel(p): sha256(p) for p in saidas},
        "resultado": resultado,
    }
    arq = EXECUCOES / f"{agora:%Y%m%dT%H%M%S}-{comando}.json"
    arq.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"registro: {rel(arq)}")


def baixar(tipo: str, comp: str) -> Path:
    destino = BRUTOS / f"CAGED{tipo}{comp}.7z"
    if not destino.exists() or destino.stat().st_size == 0:
        BRUTOS.mkdir(parents=True, exist_ok=True)
        url = f"{FTP}/{comp[:4]}/{comp}/CAGED{tipo}{comp}.7z"
        subprocess.run(["curl", "-sS", "--fail", "--retry", "3", "-o", str(destino), url], check=True)
    return destino


def baixar_layout() -> Path:
    destino = BRUTOS / "layout.xlsx"
    if not destino.exists() or destino.stat().st_size == 0:
        BRUTOS.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-sS", "--fail", "--retry", "3", "-o", str(destino), URL_LAYOUT], check=True)
    return destino


def ler_uf(arq7z: Path, uf: str) -> pd.DataFrame:
    tmp = Path(tempfile.mkdtemp())
    try:
        with py7zr.SevenZipFile(arq7z) as z:
            z.extractall(tmp)
        txt = next(tmp.rglob("*.txt"))
        partes = []
        for ch in pd.read_csv(txt, sep=";", dtype=str, chunksize=500_000, usecols=lambda c: c in COLS,
                              encoding="utf-8", encoding_errors="replace"):
            ch = ch[ch["uf"] == uf]
            if len(ch):
                partes.append(ch)
        return pd.concat(partes) if partes else pd.DataFrame(columns=COLS)
    finally:
        shutil.rmtree(tmp)


def arq_linhas(uf: str, ini: str, fim: str) -> Path:
    return LINHAS / f"uf{uf}_{ini}_{fim}.csv.gz"


def carregar(recorte: str, ini: str, fim: str) -> pd.DataFrame:
    tipo, codigo = recorte.split(":")
    uf = codigo if tipo == "uf" else codigo[:2]
    p = arq_linhas(uf, ini, fim)
    if not p.exists():
        sys.exit(f"faltam as linhas: rode  extrair --uf {uf} --ini {ini} --fim {fim}")
    d = pd.read_csv(p, dtype=str)
    if tipo == "mun":
        d = d[d["município"] == codigo]
    d["sinal"] = d["sinal"].astype(int)
    d["tipo"] = d["tipomovimentação"].astype(int)
    d["adm"] = d["tipo"].isin(ADMISSAO) * d["sinal"]
    d["desl"] = d["tipo"].isin(DESLIGAMENTO) * d["sinal"]
    d["pedido"] = (d["tipo"] == A_PEDIDO) * d["sinal"]
    d["saldo"] = pd.to_numeric(d["saldomovimentação"], errors="raise").astype(int) * d["sinal"]
    return d, p


def filtrar_ajuste(d: pd.DataFrame, ajuste: str) -> pd.DataFrame:
    """'sem ajuste' = só CAGEDMOV; 'ajustes declarados até V' = MOV + FOR - EXC com arquivo <= V."""
    if ajuste == "sem ajuste":
        return d[d["arquivo_tipo"] == "MOV"]
    v = ajuste.split()[-1]
    return d[d["arquivo_comp"] <= v]


# ---------- comandos ----------
def extrair(a):
    janela = list(competencias(a.ini, a.fim))
    blocos, manifesto, entradas = [], [], []
    for comp in janela:
        for tipo, sinal in TIPOS:
            p = baixar(tipo, comp)
            df = ler_uf(p, a.uf)
            df = df[df["competênciamov"].isin(janela)].copy()
            df["sinal"], df["arquivo_tipo"], df["arquivo_comp"] = sinal, tipo, comp
            blocos.append(df)
            manifesto.append({"arquivo": p.name, "url": f"{FTP}/{comp[:4]}/{comp}/{p.name}",
                              "bytes": p.stat().st_size, "sha256": sha256(p), "linhas_uf": len(df)})
            entradas.append(p)
            print(f"{p.name}: {len(df)} linhas da UF {a.uf} na janela", flush=True)
    lay = baixar_layout()
    manifesto.append({"arquivo": lay.name, "url": URL_LAYOUT, "bytes": lay.stat().st_size,
                      "sha256": sha256(lay), "linhas_uf": ""})
    entradas.append(lay)
    LINHAS.mkdir(parents=True, exist_ok=True)
    SAIDAS.mkdir(parents=True, exist_ok=True)
    out = arq_linhas(a.uf, a.ini, a.fim)
    pd.concat(blocos, ignore_index=True).to_csv(out, index=False)
    man = SAIDAS / f"manifesto_{a.ini}_{a.fim}.csv"
    pd.DataFrame(manifesto).to_csv(man, index=False)
    registrar("extrair", vars(a), entradas, [out, man], {"linhas": int(sum(len(b) for b in blocos))})


def agregar(a):
    d, entrada = carregar(a.recorte, a.ini, a.fim)
    nome = a.recorte.replace(":", "")
    ajustado = filtrar_ajuste(d, f"ajustes declarados até {a.fim}")
    serie = ajustado.groupby("competênciamov")[["adm", "desl", "saldo", "pedido"]].sum()
    serie.columns = ["admissoes", "desligamentos", "saldo", "deslig_a_pedido"]
    sem = filtrar_ajuste(d, "sem ajuste").groupby("competênciamov")[["adm", "desl", "saldo"]].sum()
    serie[["admissoes_sem_ajuste", "desligamentos_sem_ajuste", "saldo_sem_ajuste"]] = sem
    serie.index.name = "competencia"
    s_out = SAIDAS / f"serie_mensal_{nome}_{a.ini}_{a.fim}.csv"
    serie.to_csv(s_out)

    # tabela por ocupação (dados com ajustes até o fim da janela)
    x = ajustado.copy()
    x["sal"] = pd.to_numeric(x["salário"].str.replace(",", ".", regex=False), errors="coerce")
    # salário só de contrato mensal (unidade 5), sem intermitente e sem aprendiz (categoria 103),
    # entre 200 e 50.000 para descartar erro de digitação
    x["sal_ok"] = ((x["unidadesaláriocódigo"] == "5") & (x["indtrabintermitente"] != "1")
                   & (x["categoria"] != "103") & x["sal"].between(200, 50_000))
    adm_sal = x[x["tipo"].isin(ADMISSAO) & (x["sinal"] == 1) & x["sal_ok"]]
    g = x.groupby("cbo2002ocupação").agg(admissoes=("adm", "sum"), desligamentos=("desl", "sum"),
                                         deslig_a_pedido=("pedido", "sum"), saldo=("saldo", "sum"))
    g["salario_mediano_admissao"] = adm_sal.groupby("cbo2002ocupação")["sal"].median().round(2)
    g["salario_medio_admissao"] = adm_sal.groupby("cbo2002ocupação")["sal"].mean().round(2)
    g["movimentacoes"] = g["admissoes"] + g["desligamentos"]
    g["pct_a_pedido"] = (100 * g["deslig_a_pedido"] / g["desligamentos"].where(g["desligamentos"] > 0)).round(1)
    cbo = pd.read_excel(baixar_layout(), sheet_name="cbo2002ocupação", dtype=str)
    cbo.columns = ["cbo2002ocupação", "titulo"]
    g = g.reset_index().merge(cbo, on="cbo2002ocupação", how="left").rename(columns={"cbo2002ocupação": "cbo2002"})
    g = g[["cbo2002", "titulo", "admissoes", "desligamentos", "saldo", "deslig_a_pedido", "pct_a_pedido",
           "salario_mediano_admissao", "salario_medio_admissao", "movimentacoes"]]
    g = g.sort_values(["deslig_a_pedido", "cbo2002"], ascending=[False, True])
    o_out = SAIDAS / f"ocupacoes_{nome}_{a.ini}_{a.fim}.csv"
    g.to_csv(o_out, index=False)
    tot = {k: int(serie[k].sum()) for k in ["admissoes", "desligamentos", "saldo", "deslig_a_pedido"]}
    tot["ocupacoes"] = len(g)
    print(serie.to_string(), "\n\ntotais (com ajustes):", tot)
    registrar("agregar", vars(a), [entrada], [s_out, o_out], tot)


def conferir(a):
    of = pd.read_csv(a.oficial, dtype={"periodo_ini": str, "periodo_fim": str})
    linhas, falhas = [], 0
    cache = {}
    for _, r in of.iterrows():
        if r.recorte not in cache:
            cache[r.recorte] = carregar(r.recorte, a.ini, a.fim)
        d, _ = cache[r.recorte]
        x = filtrar_ajuste(d, r.ajuste)
        x = x[(x["competênciamov"] >= r.periodo_ini) & (x["competênciamov"] <= r.periodo_fim)]
        col = {"admissoes": "adm", "desligamentos": "desl", "saldo": "saldo"}[r.indicador]
        calc = int(x[col].sum())
        dif = calc - int(r.valor)
        falhas += dif != 0
        linhas.append({"recorte": r.recorte, "periodo": f"{r.periodo_ini}-{r.periodo_fim}",
                       "indicador": r.indicador, "ajuste": r.ajuste, "oficial": int(r.valor),
                       "calculado": calc, "diferenca": dif, "fonte": f"{r.arquivo} p.{r.pagina}"})
    t = pd.DataFrame(linhas)
    print(t.to_string(index=False))
    veredito = "PASSA" if falhas == 0 else f"NÃO PASSA ({falhas} de {len(t)} divergem)"
    print(f"\n{veredito}: {len(t) - falhas} de {len(t)} números iguais aos publicados")
    out = SAIDAS / f"conferencia_{Path(a.oficial).stem}.csv"
    t.to_csv(out, index=False)
    entradas = [Path(a.oficial).absolute()] + [p for _, p in cache.values()]
    registrar("conferir", vars(a), entradas, [out], {"veredito": veredito, "iguais": len(t) - falhas, "total": len(t)})
    sys.exit(0 if falhas == 0 else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nome in ("extrair", "agregar", "conferir"):
        s = sub.add_parser(nome)
        s.add_argument("--ini", required=True)
        s.add_argument("--fim", required=True)
        if nome == "extrair":
            s.add_argument("--uf", required=True)
        if nome == "agregar":
            s.add_argument("--recorte", required=True, help="uf:14 ou mun:140010")
        if nome == "conferir":
            s.add_argument("--oficial", required=True)
    a = ap.parse_args()
    {"extrair": extrair, "agregar": agregar, "conferir": conferir}[a.cmd](a)


if __name__ == "__main__":
    main()
