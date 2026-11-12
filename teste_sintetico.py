#!/usr/bin/env python3
"""Pipeline completo (extrair -> agregar) sobre arquivos sintéticos no formato do PDET, com resultado calculado à mão.

Uso: python -I teste_sintetico.py   (não baixa nada; roda em segundos)
Sai com 0 se todas as verificações passam.

Cobre o que a conferência oficial (só UF: admissões, desligamentos, saldo) não mede:
desligamento a pedido, recorte por município, os cinco filtros do salário de admissão (unidade mensal,
intermitente, aprendiz, piso e teto), título da CBO, série com e sem ajuste, janela de competências,
sinal do CAGEDEXC, UF filtrada na extração, SHA-256 reprodutível das linhas, aviso de bruto diferente do
manifesto, erro para recorte inexistente, download que falha sem deixar arquivo e .7z corrompido com
mensagem de orientação. O download real fica fora (o teste usa file://); a conferência tem teste próprio.

Dados (janela 202601-202602, UF 14). Município 140010 é o recorte; 140015 compartilha o prefixo 14001.
  MOV 202601  r1  140010 521110 adm  tipo 10  R$ 2.000
              r2  140010 521110 adm  tipo 10  R$ 10.000   (acima de 5.000, abaixo do teto de 50.000)
              r3  140010 521110 desl tipo 40  a pedido
              r4  140010 411005 desl tipo 31
              r5  140010 411005 desl tipo 90
              r6  140010 411005 adm  tipo 97  R$ 1.800
              r7  140015 521110 adm  tipo 10              (outro município, mesmo prefixo)
              r8  130260 (UF 13) adm tipo 10              (outra UF)
              r9  140010 521110 adm  tipo 25  aprendiz (categoria 103), R$ 700: conta, mas fora do salário
  MOV 202602  r10 140010 521110 adm  tipo 20  R$ 3.000
              r11 140010 521110 desl tipo 40  a pedido
              r15 140010 521110 adm  tipo 10  R$ 1.000, intermitente: conta, mas fora do salário
              r16 140010 521110 adm  tipo 10  R$ 2.500, unidade 3 (não mensal): conta, mas fora do salário
              r17 140010 521110 adm  tipo 10  R$ 150, abaixo do piso de 200: conta, mas fora do salário
  FOR 202601  r12 competência 202512 (fora da janela)
  FOR 202602  r13 competência 202601, 140010 411005 adm  tipo 10 R$ 2.500 (fora do prazo: entra só com ajuste)
              r18 competência 202601, 140010 411005 desl tipo 31 (fora do prazo, sem exclusão: separa com e sem ajuste)
  EXC 202601  vazio
  EXC 202602  r14 exclui a admissão r1 (sinal -1)
"""
import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd
import py7zr

sys.path.insert(0, str(Path(__file__).resolve().parent))  # com -I a pasta do script não entra no path
import caged  # noqa: E402

INI, FIM = "202601", "202602"
# ordem diferente de caged.COLS e colunas extras, como no arquivo real
CAB = ["competênciamov", "região", "uf", "município", "seção", "cbo2002ocupação", "categoria",
       "saldomovimentação", "tipomovimentação", "salário", "unidadesaláriocódigo", "indtrabintermitente"]


def lin(comp, uf, mun, cbo, saldo, tipo, sal, cat="101", unidade="5", intermitente="0"):
    return [comp, "1", uf, mun, "G", cbo, cat, saldo, tipo, sal, unidade, intermitente]


ARQUIVOS = {
    ("MOV", "202601"): [
        lin("202601", "14", "140010", "521110", "1", "10", "2000,00"),
        lin("202601", "14", "140010", "521110", "1", "10", "10000,00"),
        lin("202601", "14", "140010", "521110", "-1", "40", "2000,00"),
        lin("202601", "14", "140010", "411005", "-1", "31", "1800,00"),
        lin("202601", "14", "140010", "411005", "-1", "90", "1800,00"),
        lin("202601", "14", "140010", "411005", "1", "97", "1800,00"),
        lin("202601", "14", "140015", "521110", "1", "10", "1500,00"),
        lin("202601", "13", "130260", "521110", "1", "10", "1500,00"),
        lin("202601", "14", "140010", "521110", "1", "25", "700,00", cat="103"),
    ],
    ("MOV", "202602"): [
        lin("202602", "14", "140010", "521110", "1", "20", "3000,00"),
        lin("202602", "14", "140010", "521110", "-1", "40", "3000,00"),
        lin("202602", "14", "140010", "521110", "1", "10", "1000,00", intermitente="1"),
        lin("202602", "14", "140010", "521110", "1", "10", "2500,00", unidade="3"),
        lin("202602", "14", "140010", "521110", "1", "10", "150,00"),
    ],
    ("FOR", "202601"): [lin("202512", "14", "140010", "521110", "1", "10", "2000,00")],
    ("FOR", "202602"): [lin("202601", "14", "140010", "411005", "1", "10", "2500,00"),
                        lin("202601", "14", "140010", "411005", "-1", "31", "2500,00")],
    ("EXC", "202601"): [],
    ("EXC", "202602"): [lin("202601", "14", "140010", "521110", "1", "10", "2000,00")],
}
TITULOS = {"411005": "Auxiliar de Escritorio, em Geral", "521110": "Vendedor de Comercio Varejista",
           "999999": "Não Identificado"}

# resultado esperado, calculado à mão a partir da tabela do docstring
SERIE = {  # competência: admissões, desligamentos, saldo, a pedido, adm sem ajuste, desl sem ajuste, saldo sem ajuste
    "202601": (4, 4, 0, 1, 4, 3, 1),   # adm r1 r2 r6 r9 r13 -r14; desl r3 r4 r5 r18; sem ajuste: só MOV
    "202602": (4, 1, 3, 1, 4, 1, 3),   # adm r10 r15 r16 r17; desl r11
}
OCUPACOES = {  # cbo: título, adm, desl, saldo, a pedido, % a pedido, mediana, média, movimentações
    "521110": ("Vendedor de Comercio Varejista", 6, 2, 4, 2, 100.0, 3000.0, 5000.0, 8),  # sal: r1 r2 r10
    "411005": ("Auxiliar de Escritorio, em Geral", 2, 3, -1, 0, 0.0, 2150.0, 2150.0, 5),  # sal: r6 r13
}


def montar_brutos(brutos: Path):
    brutos.mkdir(parents=True)
    for (tipo, comp), linhas in ARQUIVOS.items():
        txt_dir = Path(tempfile.mkdtemp())
        txt = txt_dir / f"CAGED{tipo}{comp}.txt"
        pd.DataFrame(linhas, columns=CAB).to_csv(txt, sep=";", index=False)
        with py7zr.SevenZipFile(brutos / f"CAGED{tipo}{comp}.7z", "w") as z:
            z.write(txt, txt.name)
        shutil.rmtree(txt_dir)
    with pd.ExcelWriter(brutos / "layout.xlsx") as w:
        pd.DataFrame({"Código": list(TITULOS), "Descrição": list(TITULOS.values())}).to_excel(
            w, sheet_name="cbo2002ocupação", index=False)


def main():
    tmp = Path(tempfile.mkdtemp())
    falhas = []

    def checar(nome, obtido, esperado):
        ok = obtido == esperado
        print(f"{'ok   ' if ok else 'FALHA'} {nome}: obtido {obtido}" + ("" if ok else f", esperado {esperado}"))
        if not ok:
            falhas.append(nome)

    try:
        caged.RAIZ, caged.BRUTOS = tmp, tmp / "dados" / "brutos"
        caged.LINHAS, caged.SAIDAS, caged.EXECUCOES = tmp / "linhas", tmp / "saidas", tmp / "execucoes"
        montar_brutos(caged.BRUTOS)

        ext = argparse.Namespace(uf="14", ini=INI, fim=FIM)
        caged.extrair(ext)
        linhas = pd.read_csv(caged.arq_linhas("14", INI, FIM), dtype=str)
        checar("só a UF 14 nas linhas extraídas", sorted(linhas["uf"].unique()), ["14"])
        checar("competência fora da janela descartada", sorted(linhas["competênciamov"].unique()), [INI, FIM])
        h1 = hashlib.sha256(caged.arq_linhas("14", INI, FIM).read_bytes()).hexdigest()
        # bruto "republicado": o manifesto anterior passa a ter outro SHA-256 para um arquivo
        man = caged.SAIDAS / f"manifesto_{INI}_{FIM}.csv"
        m = pd.read_csv(man, dtype=str)
        m.loc[m["arquivo"] == "CAGEDFOR202602.7z", "sha256"] = "0" * 64
        m.to_csv(man, index=False)
        time.sleep(1.1)  # o cabeçalho gzip guarda o horário em segundos
        caged.extrair(ext)
        h2 = hashlib.sha256(caged.arq_linhas("14", INI, FIM).read_bytes()).hexdigest()
        checar("SHA-256 das linhas igual em duas extrações", h1 == h2, True)
        reg = json.loads(sorted(caged.EXECUCOES.glob("*-extrair.json"))[-1].read_text(encoding="utf-8"))
        checar("aviso de bruto diferente do manifesto", reg["resultado"]["difere_do_manifesto_anterior"],
               ["CAGEDFOR202602.7z"])

        caged.agregar(argparse.Namespace(recorte="mun:140010", ini=INI, fim=FIM))
        s = pd.read_csv(caged.SAIDAS / f"serie_mensal_mun140010_{INI}_{FIM}.csv", dtype={"competencia": str})
        cols = ["admissoes", "desligamentos", "saldo", "deslig_a_pedido",
                "admissoes_sem_ajuste", "desligamentos_sem_ajuste", "saldo_sem_ajuste"]
        for r in s.itertuples():
            checar(f"série {r.competencia}", tuple(int(getattr(r, c)) for c in cols), SERIE.get(r.competencia))
        checar("competências na série", sorted(s["competencia"]), sorted(SERIE))

        o = pd.read_csv(caged.SAIDAS / f"ocupacoes_mun140010_{INI}_{FIM}.csv", dtype={"cbo2002": str})
        cols = ["titulo", "admissoes", "desligamentos", "saldo", "deslig_a_pedido", "pct_a_pedido",
                "salario_mediano_admissao", "salario_medio_admissao", "movimentacoes"]
        def valor(c, v):
            if pd.isna(v):
                return None
            return v if c == "titulo" else float(v) if c.startswith(("pct", "salario")) else int(v)
        for r in o.itertuples():
            obtido = tuple(valor(c, getattr(r, c)) for c in cols)
            checar(f"ocupação {r.cbo2002}", obtido, OCUPACOES.get(r.cbo2002))
        checar("ocupações na tabela", sorted(o["cbo2002"]), sorted(OCUPACOES))

        try:
            caged.agregar(argparse.Namespace(recorte="mun:149999", ini=INI, fim=FIM))
            codigo = 0
        except SystemExit as e:
            codigo = 0 if e.code in (None, 0) else 1
        checar("recorte inexistente sai com erro", codigo, 1)

        # download: sucesso copia, falha não deixa arquivo com o nome final nem .parte
        origem = tmp / "origem.bin"
        origem.write_bytes(b"conteudo")
        ok = caged.baixar_url(origem.as_uri(), caged.BRUTOS / "baixado.bin")
        checar("download bem-sucedido grava o arquivo", ok.read_bytes(), b"conteudo")
        try:
            caged.baixar_url((tmp / "nao-existe.bin").as_uri(), caged.BRUTOS / "falhou.bin")
            codigo = 0
        except SystemExit as e:
            codigo = 0 if e.code in (None, 0) else 1
        sobras = sorted(p.name for p in caged.BRUTOS.glob("falhou.bin*"))
        checar("download que falha sai com erro e não deixa arquivo", (codigo, sobras), (1, []))

        # .7z truncado: mensagem de orientação, não traceback
        bom = caged.BRUTOS / "CAGEDMOV202601.7z"
        truncado = caged.BRUTOS / "CAGEDMOV209901.7z"
        truncado.write_bytes(bom.read_bytes()[: bom.stat().st_size // 2])
        try:
            caged.ler_uf(truncado, "14")
            msg = ""
        except SystemExit as e:
            msg = str(e.code)
        checar("7z truncado orienta apagar e baixar de novo", "apague o arquivo" in msg, True)
    finally:
        shutil.rmtree(tmp)

    print(f"\n{'TESTE PASSA' if not falhas else 'TESTE FALHA'}: {len(falhas)} falha(s)")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
