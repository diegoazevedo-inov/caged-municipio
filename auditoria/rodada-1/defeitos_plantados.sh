#!/usr/bin/env bash
# Planta cada defeito da rodada 1 (D1-D6 do parecer, D7 do achado G4-5) numa cópia de caged.py
# e roda teste_sintetico.py. Esperado: D0 (sem defeito) sai com 0; D1-D7 saem com 1.
# Uso, na raiz do repositório:  PYTHON=.venv/bin/python bash auditoria/rodada-1/defeitos_plantados.sh
set -u
PY=${PYTHON:-python3}
RAIZ=$(cd "$(dirname "$0")/../.." && pwd)
declare -A M=(
  [D1]='s/^A_PEDIDO = 40$/A_PEDIDO = 41/'
  [D2]='s/between(200, 50_000)/between(200, 5_000)/'
  [D3]='s/d\[d\["município"\] == codigo\]/d[d["município"].str[:5] == codigo[:5]]/'
  [D4]='s/^DESLIGAMENTO = {31, 32, 33, 40, 43, 45, 50, 60, 80, 90, 98}$/DESLIGAMENTO = {31, 32, 33, 40, 43, 45, 50, 60, 80, 98}/'
  [D5]='s/cbo.columns = \["cbo2002ocupação", "titulo"\]/cbo = cbo.iloc[:, ::-1]; cbo.columns = ["cbo2002ocupação", "titulo"]/'
  [D6]='s/("EXC", -1)/("EXC", 1)/'
  [D7]='s/compression=GZIP)/)/'
)
erros=0
for d in D0 D1 D2 D3 D4 D5 D6 D7; do
  w=$(mktemp -d)
  cp "$RAIZ/caged.py" "$RAIZ/teste_sintetico.py" "$w/"
  if [ "$d" != D0 ]; then
    sed -i "${M[$d]}" "$w/caged.py"
    if cmp -s "$RAIZ/caged.py" "$w/caged.py"; then echo "$d: o defeito não se aplicou"; erros=1; rm -rf "$w"; continue; fi
  fi
  "$PY" -I "$w/teste_sintetico.py" > "$w/log" 2>&1; rc=$?
  esperado=$([ "$d" = D0 ] && echo 0 || echo 1)
  falhas=$(grep '^FALHA' "$w/log" | cut -d: -f1 | sed 's/FALHA //' | paste -sd ';')
  excecao=$(grep -c Traceback "$w/log")
  echo "$d: saída $rc (esperado $esperado) | verificações que falharam: ${falhas:-nenhuma} | exceções: $excecao"
  [ "$rc" = "$esperado" ] && [ "$excecao" = 0 ] || erros=1
  rm -rf "$w"
done
echo; [ $erros = 0 ] && echo "DEFEITOS: todos pegos pelo teste, sem exceção" || echo "DEFEITOS: algum não foi pego"
exit $erros
