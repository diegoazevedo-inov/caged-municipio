#!/usr/bin/env python3
"""Defeito plantado: a conferência tem de acusar uma linha alterada nas linhas extraídas.

Uso: python -I teste_conferencia.py   (precisa de  caged.py extrair --uf 14 --ini 202510 --fim 202609)
Sai com 0 se a conferência PASSA nos dados reais e NÃO PASSA nos dados com defeito.
"""
import argparse
import shutil
import sys
import tempfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))  # com -I a pasta do script não entra no path
import caged  # noqa: E402

INI, FIM, UF = "202510", "202609", "14"
OFICIAL = caged.RAIZ / "dados" / "oficial" / "novo-caged-2026-09-uf14.csv"


def rodar_conferencia(dir_linhas: Path, tmp: Path) -> int:
    caged.LINHAS, caged.SAIDAS, caged.EXECUCOES = dir_linhas, tmp / "saidas", tmp / "execucoes"
    caged.SAIDAS.mkdir(exist_ok=True)
    caged.RAIZ = tmp  # registros relativos à pasta temporária
    try:
        caged.conferir(argparse.Namespace(oficial=str(OFICIAL), ini=INI, fim=FIM))
    except SystemExit as e:
        return e.code
    return 0


def main():
    original = caged.arq_linhas(UF, INI, FIM)
    if not original.exists():
        sys.exit(f"faltam as linhas: rode  caged.py extrair --uf {UF} --ini {INI} --fim {FIM}")
    raiz_real = caged.RAIZ
    resultados = {}
    for caso in ("real", "defeito"):
        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / "linhas").mkdir()
            destino = tmp / "linhas" / original.name
            if caso == "real":
                shutil.copy(original, destino)
            else:
                d = pd.read_csv(original, dtype=str)
                # defeito: uma admissão de março/2026 vira desligamento (muda saldo e contagens)
                i = d.index[(d["arquivo_tipo"] == "MOV") & (d["competênciamov"] == "202603")
                            & (d["saldomovimentação"] == "1")][0]
                d.loc[i, "saldomovimentação"] = "-1"
                d.loc[i, "tipomovimentação"] = "31"
                d.to_csv(destino, index=False)
            print(f"\n===== caso: {caso} =====")
            resultados[caso] = rodar_conferencia(tmp / "linhas", tmp)
        finally:
            caged.RAIZ = raiz_real
            shutil.rmtree(tmp)
    ok = resultados["real"] == 0 and resultados["defeito"] == 1
    print(f"\nreal -> saída {resultados['real']} | defeito -> saída {resultados['defeito']}")
    print("TESTE PASSA: a conferência aceita os dados reais e acusa o defeito" if ok
          else "TESTE FALHA: a conferência não separa dado real de dado com defeito")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
