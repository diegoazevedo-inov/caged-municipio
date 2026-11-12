# Protocolo da análise

## Histórico honesto

| Data | O que aconteceu |
|---|---|
| 07/11/2026 | Primeira análise, exploratória, só para Boa Vista/RR, num script de projeto (não publicado). Produziu o ranking por ocupação usado como motivação. |
| 12/11/2026 | Este protocolo foi escrito e o script foi generalizado para UF e município. O critério de conferência com a fonte oficial e as definições abaixo foram fixados **antes** da primeira execução da conferência. |

A análise de 07/11 não foi pré-registrada. O que este pacote garante é que os números publicados saem de um cálculo determinístico, conferido contra a divulgação oficial e auditado de forma independente.

## Perguntas

1. Em cada ocupação (CBO 2002) de um município, quantas admissões, desligamentos e desligamentos a pedido houve numa janela de 12 meses?
2. Que fração dos desligamentos é a pedido do trabalhador?
3. Qual o salário de admissão (mediana e média) por ocupação?

## Definições

| Item | Definição |
|---|---|
| Fonte | Microdados não identificados do Novo CAGED, PDET/MTE (`CAGEDMOV`, `CAGEDFOR`, `CAGEDEXC`) |
| Ajuste | Competência c com ajustes declarados até V = MOV(c) + FOR(f ≤ V, competênciamov = c) − EXC(f ≤ V, competênciamov = c). É o método da divulgação oficial. |
| Admissão | Tipos de movimentação 10, 20, 25, 35, 70, 97 |
| Desligamento | Tipos 31, 32, 33, 40, 43, 45, 50, 60, 80, 90, 98 |
| Desligamento a pedido | Tipo 40 |
| Fora das contagens | Tipo 99 (não identificado) |
| Saldo | Soma de `saldomovimentação` com o sinal do arquivo (+1 MOV e FOR, −1 EXC) |
| Salário de admissão | Só admissões declaradas (MOV e FOR), contrato mensal (unidade 5), sem intermitente, sem aprendiz (categoria 103), valor entre R$ 200 e R$ 50.000 |
| Corte de leitura | Ocupações com menos de 30 movimentações não entram em rankings no texto (ficam na tabela) |

## Conferência com a fonte oficial

A divulgação mensal do MTE traz números por UF, não por município. A conferência é feita na UF, e o município é um recorte das mesmas linhas.

- **Critério, fixado antes da execução:** cada número transcrito em `dados/oficial/*.csv` (com arquivo e página) tem de ser reproduzido com diferença **zero**. Qualquer diferença é investigada e explicada neste arquivo antes de publicar; sem explicação, o pacote não sai.
- **Defeito plantado:** a conferência tem de acusar uma alteração proposital nas linhas extraídas (ver `teste_conferencia.py`).

## Papel do agente de IA

- A análise foi conduzida por um agente de IA (Claude, Anthropic) sob a direção do autor: escrita do script, extração, transcrição dos números oficiais e redação da documentação.
- Nenhum número do texto é produzido pelo modelo; todos saem do script, com registro de execução em `execucoes/` (comando, versões, commit e SHA-256 de entradas e saídas).
- A auditoria é feita por outra sessão, sem acesso à conversa de quem executou (ver `auditoria/`).
- O autor revisa e responde pelo conteúdo.
