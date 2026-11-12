#!/usr/bin/env bash
# Planta cada defeito numa cópia de caged.py e roda teste_sintetico.py.
# D1-D6: parecer da rodada 1; D7: desfaz a correção de G4-5; N1-N5 e N8: verificação da rodada 2
# (N6 e N7 não entram: os tipos 70 e 99 não ocorrem nos dados, e o defeito não muda nenhuma saída).
# Esperado: D0 (sem defeito) sai com 0; todos os outros saem com 1, sem exceção.
# Uso, na raiz do repositório:  PYTHON=.venv/bin/python bash auditoria/rodada-2/defeitos_plantados.sh
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
  [N1]='s/^        return d\[d\["arquivo_tipo"\] == "MOV"\]$/        return d/'
  [N2]='s/^    return d\[d\["arquivo_comp"\] <= v\]$/    return d[d["arquivo_tipo"] == "MOV"]/'
  [N3]='s/ \& (x\["indtrabintermitente"\] != "1")//'
  [N4]='s/(x\["unidadesaláriocódigo"\] == "5")/(x["unidadesaláriocódigo"] == x["unidadesaláriocódigo"])/'
  [N5]='s/between(200, 50_000)/between(0, 50_000)/'
  [N8]='s/^    difere = \[r\.arquivo .*$/    difere = []/'
)
erros=0
for d in D0 D1 D2 D3 D4 D5 D6 D7 N1 N2 N3 N4 N5 N8; do
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
