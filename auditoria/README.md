# Auditoria independente

Cada rodada é feita numa sessão nova, sem acesso ao trabalho de quem executou. Quem executa não audita. Aqui ficam o briefing, o parecer, as correções feitas em resposta a cada achado e a verificação dirigida.

| Rodada | Data | Tipo | Commit auditado | Parecer | Resultado |
|---|---|---|---|---|---|
| 1 | 12/11/2026 | completa (7 gates) | `e5ee630` | [`rodada-1/PARECER.md`](rodada-1/PARECER.md) | não pode: 1 bloqueio (G5-1) e 18 ressalvas. Correções em [`rodada-1/CORRECOES.md`](rodada-1/CORRECOES.md) |
| 2 | 12/11/2026 | verificação dirigida das correções da rodada 1, com reextração completa do PDET | `0f42f4c` | [`rodada-2/VERIFICACAO.md`](rodada-2/VERIFICACAO.md) | pode ir a público com ressalvas: bloqueio resolvido, 7 ressalvas (V1–V7). Correções em [`rodada-2/CORRECOES.md`](rodada-2/CORRECOES.md) |
| 3 | 12/11/2026 | verificação dirigida das correções da rodada 2 | `870009a` | [`rodada-3/VERIFICACAO.md`](rodada-3/VERIFICACAO.md) | pode ir a público com ressalvas: 3 ressalvas (R1–R3), nenhuma muda número publicado. Correções em [`rodada-3/CORRECOES.md`](rodada-3/CORRECOES.md) |
| 4 | 12/11/2026 | verificação dirigida das correções da rodada 3 | `6cd9caf` | [`rodada-4/VERIFICACAO.md`](rodada-4/VERIFICACAO.md) | pode ir a público com ressalvas: R1–R3 resolvidas; resta só registrar a rodada (P1), feito em [`rodada-4/CORRECOES.md`](rodada-4/CORRECOES.md), sem mudança de código ou número |

Nos arquivos das rodadas, os caminhos absolutos da máquina foram trocados por `<repositório>`, `<pasta da auditoria>` e `<pasta temporária da sessão do auditor>`. O restante é o texto original. Nos `CORRECOES.md`, que são do executor, notas acrescentadas em rodadas posteriores estão marcadas no próprio texto; os pareceres dos auditores não foram alterados.
