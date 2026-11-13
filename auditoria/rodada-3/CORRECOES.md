# Rodada 3: correções

Verificação: [`VERIFICACAO.md`](VERIFICACAO.md), sobre o commit `870009a`. O parecer verificado é o da rodada 2 ([`../rodada-2/VERIFICACAO.md`](../rodada-2/VERIFICACAO.md)). Veredito: **pode ir a público com ressalvas**. Restaram R1 a R3; as observações O1 a O4 não pedem correção.

`caged.py` não mudou nesta rodada, e as saídas versionadas e os registros de execução continuam os da rodada 2.

| Achado | Correção | Onde |
|---|---|---|
| R1: teto do salário sem teste | Linha r19: admissão de R$ 60.000 em 521110, que conta no movimento e fica fora do salário. O defeito M1 (sem teto) passa a ser pego. | `teste_sintetico.py`, `docs/PROTOCOLO.md` |
| R2: ".7z corrompido" além do testado | O texto passa a dizer "truncado" e declara que bytes corrompidos no meio do arquivo não são tratados. | `teste_sintetico.py`, `auditoria/rodada-2/CORRECOES.md` |
| R3: rodada 3 sem registro | Esta pasta, com a linha da rodada 3 em `auditoria/README.md`. | `auditoria/` |
| O2: histórico do protocolo cita só a rodada 1 | A linha passa a remeter às rodadas em `auditoria/`. | `docs/PROTOCOLO.md` |
| O3: texto antigo em `rodada-1/CORRECOES.md` | Nota no topo remetendo às revisões da rodada 2. | `auditoria/rodada-1/CORRECOES.md` |

## Evidência

| Verificação | Resultado |
|---|---|
| `teste_sintetico.py` | `TESTE PASSA: 0 falha(s)`, com os valores esperados de 521110 (7 admissões, saldo 5, 9 movimentações) e da série 202602 (5 admissões, saldo 4) refeitos para r19 |
| `auditoria/rodada-3/defeitos_plantados.sh` | D0 sai com 0; D1–D7, N1–N5, N8 e M1 saem com 1, sem exceção. M1 falha em "ocupação 521110" |

A mudança é só no teste. A verificação curta indicada pela rodada 3 (rodar `teste_sintetico.py` e o mutante M1) é a rodada 4.
