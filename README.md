# Novo CAGED por município: análise reprodutível e conferida

Rotatividade por ocupação (CBO 2002) num município brasileiro, a partir dos microdados não identificados do Novo CAGED (PDET/MTE), com:

- cálculo determinístico pelo mesmo método de ajuste da divulgação oficial;
- conferência número a número contra a publicação do Ministério do Trabalho e Emprego;
- registro de cada execução (comando, versões, commit, SHA-256 de entradas e saídas);
- auditoria independente documentada em `auditoria/`.

O caso aplicado é Boa Vista (RR), de outubro de 2025 a setembro de 2026. Qualquer município pode ser analisado trocando o código.

## Conferência com a fonte oficial

A divulgação mensal do MTE traz números por unidade da federação. A conferência é feita na UF; o município é um recorte das mesmas linhas.

| Recorte | Números publicados conferidos | Iguais | Fonte |
|---|---|---|---|
| Roraima (UF 14) | 18: saldo mensal de 10/2025 a 09/2026, acumulado de 2026 (admissões, desligamentos, saldo) e setembro sem ajuste | 18, diferença zero | Apresentação Novo CAGED setembro/2026, p. 31, 34 e 43 |

O critério (diferença zero) foi fixado antes da primeira execução. `teste_conferencia.py` planta um defeito nas linhas extraídas e confirma que a conferência o acusa.

## Resultado do caso (Boa Vista, 10/2025 a 09/2026, com ajustes até 09/2026)

| Indicador | Valor |
|---|---|
| Admissões | 49.067 |
| Desligamentos | 45.836 |
| Saldo | 3.231 |
| Desligamentos a pedido | 16.894 (36,9% dos desligamentos) |
| Ocupações com movimento | 935 |

Tabelas completas em `dados/saidas/`: `ocupacoes_mun140010_202510_202609.csv` e `serie_mensal_mun140010_202510_202609.csv`.

## Como reproduzir

Requisitos: Python 3.11 ou mais novo e `curl`. Versões usadas no registro: Python 3.14.4, pandas 3.1.1, py7zr 1.1.4, openpyxl 3.1.5 (`requirements.txt`).

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -I caged.py extrair  --uf 14 --ini 202510 --fim 202609     # baixa os .7z e o layout se faltarem (cerca de 620 MB)
.venv/bin/python -I caged.py conferir --oficial dados/oficial/novo-caged-2026-09-uf14.csv --ini 202510 --fim 202609
.venv/bin/python -I caged.py agregar  --recorte mun:140010 --ini 202510 --fim 202609
.venv/bin/python -I teste_conferencia.py
```

Os arquivos brutos não são redistribuídos. `dados/saidas/manifesto_202510_202609.csv` lista o endereço, o tamanho e o SHA-256 de cada um, para conferir que são os mesmos.

## Método

Definições, critério de conferência e histórico em [`docs/PROTOCOLO.md`](docs/PROTOCOLO.md). Fontes oficiais e seus SHA-256 em [`dados/oficial/FONTES.md`](dados/oficial/FONTES.md).

**Uso de IA.** A análise foi conduzida por um agente de IA sob a direção do autor. Nenhum número vem do modelo: todos saem do script, com registro em `execucoes/`. A auditoria foi feita em sessão separada, sem acesso ao trabalho de quem executou.

## Limitações

- O Novo CAGED registra movimentações de vínculos formais (CLT); não mede vagas abertas nem o trabalho informal.
- Não há estoque de vínculos por ocupação no CAGED (isso vem da RAIS); as taxas aqui são relativas às movimentações.
- Os números de um mês ainda recebem declarações fora do prazo; a janela é sempre a dos ajustes declarados até o mês final.

## Licença e citação

Código e documentação sob Apache-2.0. Os microdados são do Ministério do Trabalho e Emprego. Para citar, veja `CITATION.cff`.
