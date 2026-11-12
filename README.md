# Novo CAGED por município: movimentação e desligamentos a pedido por ocupação

Admissões, desligamentos, desligamentos a pedido e salário de admissão por ocupação (CBO 2002) num município brasileiro, calculados a partir dos microdados não identificados do Novo CAGED (PDET/MTE). O pacote tem:

- cálculo determinístico pelo mesmo método de ajuste da divulgação oficial;
- conferência dos números da UF contra a publicação do Ministério do Trabalho e Emprego;
- teste da extração e da agregação sobre dados sintéticos com resultado calculado à mão (recorte municipal, a pedido, filtros do salário, título da CBO, série com e sem ajuste);
- registro de cada execução (comando, versões, commit, SHA-256 de entradas e saídas);
- auditoria independente em sessões separadas, com briefing, parecer e correções em `auditoria/`.

O caso aplicado é Boa Vista (RR), de outubro de 2025 a setembro de 2026. Para analisar outro município da mesma UF, basta trocar o código; para outra UF, é preciso extrair as linhas dela antes.

## Conferência com a fonte oficial

A divulgação mensal do MTE traz números por unidade da federação, e a conferência é feita nesse nível: admissões, desligamentos e saldo de Roraima. O município sai das mesmas linhas, mas não há número oficial municipal para comparar. O recorte e os indicadores por ocupação são verificados por `teste_sintetico.py`, com as ressalvas de alcance de [`docs/PROTOCOLO.md`](docs/PROTOCOLO.md).

| Recorte | Números publicados conferidos | Iguais | Fonte |
|---|---|---|---|
| Roraima (UF 14) | 18 transcrições: saldo mensal de 10/2025 a 09/2026 (p. 31), acumulado de 2026 com admissões, desligamentos e saldo (p. 34) e setembro sem ajuste (p. 43) | 18, diferença zero | Apresentação Novo CAGED setembro/2026 |

As 18 transcrições não são 18 verificações independentes. Há 17 valores distintos, porque o saldo de 09/2026 (1.068) aparece nas páginas 31 e 43. Há também dependências aritméticas: o saldo acumulado de 2026 é a soma dos saldos mensais e, nas páginas 34 e 43, o saldo é admissões menos desligamentos. Na p. 31, o ajuste vale de 09/2025 a 08/2026, e o mês final aparece sem ajuste (nota de rodapé da página).

O critério de diferença zero foi fixado pelo autor antes da primeira execução da conferência. Essa ordem é uma declaração do autor: o histórico do git não a prova. `teste_conferencia.py` planta um defeito nas linhas extraídas e confirma que a conferência o acusa.

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

Requisitos: Python 3.11 ou mais novo e `curl`. Versões usadas no registro: Python 3.14.4, pandas 3.1.1, py7zr 1.1.4, openpyxl 3.1.5 (`requirements.txt`). Só a versão 3.14.4 do Python foi testada.

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -I teste_sintetico.py                                        # segundos, sem download
.venv/bin/python -I caged.py extrair  --uf 14 --ini 202510 --fim 202609     # baixa os .7z e o layout se faltarem (cerca de 620 MB)
.venv/bin/python -I caged.py conferir --oficial dados/oficial/novo-caged-2026-09-uf14.csv --ini 202510 --fim 202609
.venv/bin/python -I caged.py agregar  --recorte mun:140010 --ini 202510 --fim 202609
.venv/bin/python -I teste_conferencia.py
git diff --stat dados/saidas/                                                 # vazio = mesmos brutos e mesmos resultados
```

Os arquivos brutos não são redistribuídos. `dados/saidas/manifesto_202510_202609.csv` lista o endereço, o tamanho e o SHA-256 de cada um. O `extrair` avisa (e guarda no registro) quando um arquivo baixado difere do manifesto existente, o que acontece se o PDET republicar o arquivo. As linhas extraídas são gravadas sem horário no cabeçalho gzip, então o mesmo conteúdo dá o mesmo SHA-256 na mesma versão da zlib (verificado com a zlib 1.3.1). Outra implementação de deflate pode gerar bytes diferentes para o mesmo conteúdo; nesse caso, compare o CSV descompactado.

## Método

Definições, critério de conferência e histórico em [`docs/PROTOCOLO.md`](docs/PROTOCOLO.md). Fontes oficiais e seus SHA-256 em [`dados/oficial/FONTES.md`](dados/oficial/FONTES.md).

**Uso de IA.** A análise foi conduzida por um agente de IA sob a direção do autor. Nenhum número vem do modelo: todos saem do script, com registro em `execucoes/`. A auditoria é feita em sessões separadas, sem acesso ao trabalho de quem executou. As rodadas, os pareceres e as correções estão em [`auditoria/`](auditoria/README.md).

## Limitações

- O Novo CAGED registra movimentações de vínculos formais (CLT); não mede vagas abertas nem o trabalho informal.
- Não há estoque de vínculos por ocupação no CAGED (isso vem da RAIS), por isso não se calcula taxa de rotatividade. O único percentual da tabela, `pct_a_pedido`, é a fração dos desligamentos que foram a pedido.
- Os números de um mês ainda recebem declarações fora do prazo; a janela é sempre a dos ajustes declarados até o mês final.
- Oito CBOs da tabela de Boa Vista ficam sem título, porque os códigos não constam da aba `cbo2002ocupação` do layout oficial: 142140, 142360, 322140, 322715, 423115, 514335, 519325 e 519330.

## Licença e citação

Código e documentação sob Apache-2.0. Os microdados são do Ministério do Trabalho e Emprego. Para citar, veja `CITATION.cff`.
