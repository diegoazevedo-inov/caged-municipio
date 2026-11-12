# Rodada 1: correções

Parecer: [`PARECER.md`](PARECER.md), sobre o commit `e5ee630`. Veredito: **não pode**, com um bloqueio (G5-1) e ressalvas. As correções estão no commit `4c82547`. As saídas foram regeradas com esse código (registros `execucoes/20261112T182954-extrair.json`, `…T183003-conferir.json` e `…T183004-agregar.json`).

## Achado por achado

| Achado | Correção | Onde |
|---|---|---|
| **G5-1** (bloqueio): auditoria declarada como feita | A rodada fica registrada nesta pasta (briefing, parecer, correções). O README, o protocolo e o CITATION passam a remeter a `auditoria/`, onde está o estado de cada rodada. | `README.md`, `docs/PROTOCOLO.md`, `CITATION.cff`, `auditoria/README.md` |
| G4-1: desligamento a pedido sem teste | `teste_sintetico.py` roda o pipeline completo sobre `.7z` sintéticos e compara cada valor com o resultado calculado à mão, incluindo dois desligamentos tipo 40. | `teste_sintetico.py` |
| G4-2: recorte municipal sem teste | O teste inclui o município 140015, que tem o mesmo prefixo de 5 dígitos do recorte 140010, e uma linha de outra UF. | idem |
| G4-3: tabela por ocupação sem teste; corte de 30 sem objeto | O teste confere título, salário mediano e médio (com valor entre 5.000 e 50.000 e aprendiz excluído) e `pct_a_pedido`. O protocolo define o corte de leitura como regra para rankings em textos derivados e aponta a coluna `movimentacoes`. | `teste_sintetico.py`, `docs/PROTOCOLO.md` |
| G4-4: o teste existente não exercita `extrair` | O teste sintético passa por `extrair` (tipos de arquivo, sinal do EXC, filtro de UF e de janela). O alcance de `teste_conferencia.py` está no docstring. | `teste_sintetico.py`, `teste_conferencia.py` |
| G4-5: SHA-256 do `.csv.gz` não reprodutível | As linhas são gravadas com `mtime=0` no cabeçalho gzip. O teste sintético extrai duas vezes, com mais de 1 s de intervalo, e compara os SHA-256. | `caged.py` (`GZIP`), `teste_sintetico.py` |
| G4-6: recorte inexistente sai com 0 | `carregar` sai com erro quando o recorte não tem linhas. Coberto pelo teste. | `caged.py` |
| G4-7: brutos sem conferência contra o manifesto | `extrair` compara os SHA-256 com o manifesto existente antes de sobrescrever, avisa e guarda a lista em `difere_do_manifesto_anterior`. O README orienta `git diff --stat dados/saidas/`. | `caged.py`, `README.md` |
| G5-2: 18 transcrições ≠ 18 verificações | O README declara 16 valores distintos, 15 deles independentes. | `README.md` |
| G5-3: rótulo do saldo de 09/2026 na p. 31 | A linha 13 de `dados/oficial/novo-caged-2026-09-uf14.csv` passa a usar o rótulo da fonte, "ajustes declarados até 202609". A conferência continua 18/18. | CSV oficial |
| G5-4: "número a número" além do conferido | O texto passa a dizer conferência dos números da UF. O município e os indicadores por ocupação são verificados pelo teste sintético, não contra fonte. | `README.md`, `CITATION.cff`, `docs/PROTOCOLO.md` |
| G5-5: "fixado antes" sem prova | Fica apresentado como declaração do autor; o histórico do git não prova a ordem. | `README.md`, `docs/PROTOCOLO.md` |
| G5-6: openpyxl fora do registro | `registrar` grava `openpyxl`. | `caged.py` |
| G5-7: campo `inicio` com o horário do fim | `inicio` é o horário do começo do processo; o campo `fim` foi acrescentado. | `caged.py` |
| G5-8: CBOs sem título | Os oito códigos estão listados nas limitações do README. | `README.md` |
| G5-9: título promete rotatividade | Título e resumo dizem o que é medido: movimentação e desligamentos a pedido por ocupação. As limitações explicam por que não há taxa de rotatividade. | `README.md`, `CITATION.cff` |
| G7-1 a G7-3: tom do histórico | O histórico vira uma tabela de etapas, sem adjetivo, sem citar artefato não publicado e sem a frase de garantia. | `docs/PROTOCOLO.md` |

## Evidência

Saídas com o código `4c82547`:

| Verificação | Resultado |
|---|---|
| `caged.py conferir` | `PASSA: 18 de 18`, saída 0 |
| `caged.py agregar --recorte mun:140010` | 49.067 / 45.836 / 3.231 / 16.894 / 935, como antes |
| `caged.py agregar --recorte mun:149999` | erro, saída 1 |
| `teste_conferencia.py` | `real -> saída 0 \| defeito -> saída 1`, `TESTE PASSA` |
| `teste_sintetico.py` | `TESTE PASSA: 0 falha(s)` |
| `auditoria/rodada-1/defeitos_plantados.sh` | D0 sai com 0; D1 a D7 saem com 1, sem exceção |
| `git diff` das saídas versionadas | manifesto, série e ocupações idênticos; na conferência muda só o rótulo da linha de 09/2026 (G5-3) |

Defeitos plantados contra o teste sintético (D1 a D6 são os do parecer; D7 desfaz a correção de G4-5):

| # | Defeito | Verificações que falham |
|---|---|---|
| D1 | `A_PEDIDO = 41` | série 202601, série 202602, ocupação 521110 |
| D2 | teto salarial 5.000 | ocupação 521110 |
| D3 | município por prefixo de 5 dígitos | série 202601, ocupação 521110 |
| D4 | tipo 90 fora de `DESLIGAMENTO` | série 202601, ocupação 411005 |
| D5 | colunas do layout trocadas | ocupação 521110, ocupação 411005 |
| D6 | sinal do EXC +1 | série 202601, ocupação 521110 |
| D7 | gzip com horário no cabeçalho | SHA-256 das linhas igual em duas extrações |

As correções mudam código e testes. Por isso há uma verificação dirigida (rodada 2) antes de publicar.
