# Rodada 2: correções

Verificação: [`VERIFICACAO.md`](VERIFICACAO.md), sobre o commit `0f42f4c`. O parecer verificado é o da rodada 1 ([`../rodada-1/PARECER.md`](../rodada-1/PARECER.md)). Veredito: **pode ir a público com ressalvas**. O bloqueio G5-1 está resolvido, e a reextração completa a partir do PDET reproduziu o SHA-256 das linhas e o manifesto.

As correções estão nos commits `fdc773b` e `34ebdc3`. As saídas foram regeradas com `34ebdc3` (registros `execucoes/20261112T195851-conferir.json`, `…T195852-agregar.json` e `…T200037-extrair.json`).

## Achado por achado

| Achado | Correção | Onde |
|---|---|---|
| V1 (G5-2 em parte): "16 valores distintos" | São 17 valores distintos, porque o saldo de 09/2026 aparece nas p. 31 e 43. As dependências aritméticas são descritas sem nova contagem. | `README.md` |
| V2 (G5-3 estava errado) | A nota de rodapé da p. 31 limita o ajuste a 09/2025–08/2026 (conferido no PDF, SHA-256 `063267f6…`). O saldo de 09/2026 dessa página volta a "sem ajuste". A nota está registrada em `FONTES.md` e no README. Conferência 18/18. | `dados/oficial/novo-caged-2026-09-uf14.csv:13`, `dados/oficial/FONTES.md`, `README.md` |
| V3 (G4-3 em parte): filtros do salário e série sem ajuste sem teste | O teste sintético ganhou uma admissão intermitente, uma com unidade 3, uma de R$ 150 e um desligamento fora do prazo sem exclusão, que separa com e sem ajuste. N1, N3, N4 e N5 passam a ser pegos. | `teste_sintetico.py` |
| V4: "pipeline completo" | Passa a ser "extração e agregação". O protocolo diz o que fica fora (download real e conferência, que tem teste próprio). | `README.md`, `docs/PROTOCOLO.md` |
| V5: rodada 2 sem registro | Esta pasta, com a linha da rodada 2 em `auditoria/README.md`. | `auditoria/` |
| V6: SHA-256 do gzip e zlib | O README restringe a afirmação à mesma versão da zlib (1.3.1 verificada) e orienta comparar o CSV descompactado. | `README.md` |
| V7: download interrompido deixa `.7z` truncado | O download vai para `<arquivo>.parte` e só recebe o nome final se o curl terminar com sucesso; na falha, o `.parte` é apagado e o comando sai com mensagem. Um `.7z` corrompido gera mensagem com orientação, não traceback. | `caged.py` (`baixar_url`, `ler_uf`), `teste_sintetico.py`, `README.md` |
| G5-5 residual | "Critério, fixado antes da execução (declaração do autor)". | `docs/PROTOCOLO.md` |
| N8: aviso do manifesto sem teste automático | O teste altera o SHA-256 de um arquivo no manifesto, extrai de novo e confere `difere_do_manifesto_anterior`. | `teste_sintetico.py` |

## Evidência

| Verificação | Resultado |
|---|---|
| `caged.py extrair` | linhas com SHA-256 `cf8457ce…`, igual ao da rodada 1 e ao da reextração do auditor; `difere_do_manifesto_anterior: []` |
| `caged.py conferir` | `PASSA: 18 de 18`, saída 0 |
| `caged.py agregar --recorte mun:140010` | 49.067 / 45.836 / 3.231 / 16.894 / 935 |
| `teste_conferencia.py` | `TESTE PASSA` |
| `teste_sintetico.py` | `TESTE PASSA: 0 falha(s)`, 14 verificações |
| `auditoria/rodada-2/defeitos_plantados.sh` | D0 sai com 0; D1–D7, N1–N5 e N8 saem com 1, sem exceção |
| `git diff` das saídas versionadas | manifesto, série e ocupações idênticos; na conferência muda só o rótulo da linha de 09/2026 (V2) |

Defeitos novos contra o teste sintético:

| # | Defeito | Verificações que falham |
|---|---|---|
| N1 | "sem ajuste" com todas as linhas | série 202601 |
| N2 | "com ajuste" só com MOV | série 202601, ocupação 521110, ocupação 411005 |
| N3 | sem o filtro de intermitente | ocupação 521110 |
| N4 | sem o filtro de unidade 5 | ocupação 521110 |
| N5 | piso salarial 0 | ocupação 521110 |
| N8 | `comparar_manifesto` nunca acusa | aviso de bruto diferente do manifesto |

N6 e N7 ficam fora porque os tipos 70 e 99 não ocorrem na UF 14 na janela, e esses defeitos não mudam nenhuma saída.

**Limite do teste de V7.** O teste confirma que um download que falha não deixa arquivo (fonte `file://` inexistente) e que um `.7z` truncado gera a mensagem de orientação. Ele não simula uma transferência interrompida no meio; nesse caso, a garantia vem da renomeação só depois do sucesso do curl.

As correções mudam código e testes. Por isso há nova verificação dirigida (rodada 3) antes de publicar.
