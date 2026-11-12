# Parecer de auditoria independente: `caged-municipio`

- **Objeto:** `<repositório>`, ramo `main`, HEAD `e5ee630` (2 commits).
- **Data:** 12/11/2026.
- **Modo:** auditoria completa, em sessão nova. Trabalho feito num clone em pasta temporária. O original foi apenas lido: `git status`, `git fsck` e `reflog`, além do SHA-256 do `.csv.gz` ignorado. Não houve escrita no original, repositório remoto, push nem API paga.
- **Ambiente:** Python 3.14.4, pip com `requirements.txt` (pandas 3.1.1, py7zr 1.1.4, openpyxl 3.1.5), curl. Rede: FTP do PDET/MTE e gov.br, ambos públicos.

## Veredito final: **não pode** no estado atual (`e5ee630`)

Há um bloqueio, e a correção é pequena: o README, o protocolo e o `CITATION.cff` afirmam que a auditoria independente **foi feita e está documentada em `auditoria/`**, mas `auditoria/README.md:7` diz "ainda não realizada" (achado G5-1). Corrigido isso (por exemplo, registrando este parecer e as correções em `auditoria/`, ou trocando o tempo verbal), e confirmado numa verificação dirigida, o veredito passa a **"pode ir a público com ressalvas"**. As ressalvas são os demais achados de G4, G5 e G7. Nenhum deles impede a publicação sozinho.

O núcleo técnico se sustenta. A reprodução num clone limpo regerou byte a byte todos os artefatos versionados, a conferência dá 18/18 contra a fonte oficial, e os SHA-256 e as páginas dos PDFs do MTE conferem.

| Gate | Veredito |
|---|---|
| 1. Histórico | **Passa** |
| 2. Dados | **Passa** |
| 3. Reprodução | **Passa** |
| 4. Régua | **Passa com ressalvas** |
| 5. Afirmações | **Não passa** (G5-1). Demais achados são ressalvas |
| 6. Justiça | **Não se aplica** |
| 7. Tom | **Passa com ressalvas** |

---

## Gate 1: histórico. **Passa**

Evidência:
- `git log --all`: 2 commits, `9321b30` (inicial, 14 arquivos) e `e5ee630` (+5 arquivos). Há um só ramo (`main`), sem tags nem stash.
- Nenhum arquivo do commit inicial foi removido depois: os 14 continuam em HEAD.
- No original, `git fsck --unreachable --no-reflogs` não deu saída. `git count-objects -v` mostra 31 objetos soltos, e `git rev-list --objects --all | wc -l` dá 31: todos são alcançáveis. O reflog só tem os 2 commits.
- O autor dos commits é `Diego <diego@example.com>`, um e-mail de exemplo, não pessoal.

Observação (não é achado): o `manifesto_202510_202609.csv` do commit inicial não tem a linha do `layout.xlsx`, que o código de `9321b30` já grava (`caged.py:183-186`). Ou seja, as saídas do commit inicial vieram de uma versão anterior do script, que não está no histórico. A versão em HEAD foi regerada e registrada com o código `9321b30` (`execucoes/20261112T153630-extrair.json`), e as saídas de HEAD têm o mesmo SHA-256 dos registros. Não sobra resíduo.

## Gate 2: dados. **Passa**

Evidência:
- Procurei, em todos os commits (`git grep` sobre `git rev-list --all`), caminhos pessoais (`/home`, `/tmp`), e-mail, token, senha, chave, cliente, clínica, paciente e nomes de sistemas privados. Só aparecem a menção declarada a "Claude, Anthropic" (`docs/PROTOCOLO.md:41`) e dois títulos oficiais da CBO com "Clínica[s]" (`ocupacoes_…csv:84` e `:213`). Nenhum dos dois é dado privado.
- Os registros em `execucoes/` usam caminhos relativos (`caged.py:81-85`). Nenhum caminho absoluto foi versionado.
- Os microdados brutos e as linhas extraídas não são versionados (`.gitignore`). As tabelas versionadas agregam por CBO num município, a partir de microdados públicos e não identificados que já trazem município, CBO e salário por linha. A agregação não expõe nada além da fonte.
- O nome e o ORCID em `CITATION.cff:9-11` são a autoria declarada, publicada de propósito.

Sem achados. A menção a um "script de projeto (não publicado)" (`docs/PROTOCOLO.md:7`) não identifica sistema nenhum. Ela é tratada em G7, como bastidor.

## Gate 3: reprodução. **Passa**

Rodei os 4 comandos do README (`README.md:39-43`) no clone limpo, sem nada em cache:

| Comando | Resultado |
|---|---|
| `pip install -r requirements.txt` | ok |
| `caged.py extrair --uf 14 --ini 202510 --fim 202609` | ok. Baixou 36 `.7z` + layout (613,8 MiB; o README diz "cerca de 620 MB"). Levou 59 min 22 s de relógio, quase todo em download (1 min de CPU) |
| `caged.py conferir …` | `PASSA: 18 de 18`, saída 0 |
| `caged.py agregar --recorte mun:140010 …` | totais `{admissoes: 49067, desligamentos: 45836, saldo: 3231, deslig_a_pedido: 16894, ocupacoes: 935}` |
| `teste_conferencia.py` | `real -> saída 0 \| defeito -> saída 1`, `TESTE PASSA` |

Depois da execução, `git diff` ficou **vazio**. Manifesto (SHA-256 e tamanho dos 37 arquivos), série mensal, tabela de ocupações e conferência saíram idênticos aos versionados. O conteúdo descompactado de `dados/linhas/uf14_202510_202609.csv.gz` também é idêntico ao do original (`378236b9…`).

Testei também `mun:140002`, `uf:14` e o código de outra UF (`mun:130260`). Este último responde com uma mensagem clara pedindo o `extrair` da UF 13.

Não testei o requisito "Python 3.11 ou mais novo" (`README.md:36`) em 3.11, só em 3.14.4.

## Gate 4: régua. **Passa com ressalvas**

A suíte é `conferir`, que compara 18 números com a publicação oficial, mais `teste_conferencia.py`, que planta um defeito nas linhas extraídas. As duas rodam e passam (G3).

### Defeitos plantados (diferentes do defeito do teste existente)

| # | Defeito em `caged.py` | `teste_conferencia.py` | `conferir` | Efeito nas saídas |
|---|---|---|---|---|
| D1 | `A_PEDIDO = 41` em vez de 40 (`:46`) | **não pega** (saída 0) | **não pega** (18/18) | `deslig_a_pedido` vai de 16.894 a 0. A série e a tabela mudam |
| D2 | teto salarial de 50.000 para 5.000 (`:214`) | **não pega** | **não pega** | medianas e médias salariais mudam |
| D3 | filtro de município por prefixo de 5 dígitos (`:150`) | **não pega** | **não pega** | Boa Vista passa a ter 50.147 admissões e 947 ocupações |
| D4 | tipo 90 retirado de `DESLIGAMENTO` (`:45`) | **pega** (saída 1) | **pega** (2 divergências) | desligamentos 45.330 |
| D5 | colunas do layout trocadas no merge de títulos (`:223`) | **não pega** | **não pega** | coluna `titulo` errada |
| D6 | sinal do `CAGEDEXC` +1 em vez de −1 (`:49`) | **não pega** com as linhas já extraídas | **pega** depois de rodar `extrair` de novo (11 divergências) | só depois de rodar `extrair` de novo |

Resultado: a régua pega defeitos que alteram admissões, desligamentos e saldo **da UF**: D4, e D6 com o pipeline completo. Ela não pega defeitos nos indicadores do resultado publicado do caso (D1, D2, D3, D5).

### Requisitos que os testes não medem de verdade

- **G4-1. O indicador central não é conferido.** O README se apresenta como análise de "rotatividade por ocupação" (`README.md:3`), e o resultado destacado inclui "Desligamentos a pedido 16.894 (36,9%)" (`README.md:29`). Nada no repositório confere o tipo 40 contra uma fonte nem testa essa contagem (D1).
- **G4-2. O recorte municipal não é testado.** A conferência é só na UF (declarado em `README.md:14`). O filtro de município (`caged.py:149-150`) não tem teste nenhum (D3). A frase "o município é um recorte das mesmas linhas" é verdadeira, mas um defeito no próprio recorte passa sem ser visto.
- **G4-3. A tabela por ocupação não é testada:** salário (D2), título da CBO (D5), `pct_a_pedido`. O "corte de leitura" de 30 movimentações (`docs/PROTOCOLO.md:30`) não tem implementação nem objeto: não há ranking no texto. 673 das 935 linhas da tabela ficam abaixo desse corte.
- **G4-4. `teste_conferencia.py` só exercita `conferir` sobre linhas já extraídas.** Defeitos em `extrair` (`TIPOS`, `ler_uf`, filtro de janela) só aparecem quando o pipeline inteiro roda de novo (D6). Isso não está dito.
- **G4-5. O SHA-256 das linhas extraídas não é reprodutível.** `caged.py:190` grava `.csv.gz` com o horário no cabeçalho gzip. O registro original traz `cb38e039…` e a reexecução deu `aa104687…`, com conteúdo idêntico. A rastreabilidade por hash prometida em `README.md:7` falha justamente para a entrada de `conferir` e `agregar`. Gravar com `mtime` fixo resolve.
- **G4-6. Recorte inexistente sai sem erro.** `agregar --recorte mun:149999` produz arquivos vazios e sai com 0.
- **G4-7. Nenhum comando confere os brutos baixados contra o manifesto versionado.** `baixar()` (`caged.py:104-110`) aceita qualquer arquivo não vazio, e `extrair` sobrescreve o manifesto. A conferência citada em `README.md:46` depende de o usuário rodar `git diff`. Funciona, mas o README não diz.

## Gate 5: afirmações. **Não passa**

### Bloqueio

- **G5-1. A auditoria aparece como feita sem estar.**
  - `README.md:8`: "auditoria independente documentada em `auditoria/`"
  - `README.md:52`: "A auditoria foi feita em sessão separada…"
  - `docs/PROTOCOLO.md:10`: "…conferido contra a divulgação oficial e auditado de forma independente."
  - `CITATION.cff:4`: "…registro de cada execução e auditoria independente."

  `auditoria/README.md:7` registra "ainda não realizada", e não há briefing nem parecer na pasta. É uma afirmação contrária à evidência do próprio repositório. Correção: registrar a rodada em `auditoria/` (briefing, este parecer, correções), ou escrever no futuro até isso existir.

### Conferido e sustentado

- Os 18 valores de `dados/oficial/novo-caged-2026-09-uf14.csv` batem com `apresentacao-setembro-de-2026.pdf`: p. 31 (saldos de Roraima de 2025/10 a 2026/09), p. 34 (42.095 / 38.281 / 3.814) e p. 43 (5.060 / 3.992 / 1.068). Baixei os PDFs dos endereços de `dados/oficial/FONTES.md`, e os SHA-256 (`063267f6…`, `2c404cb4…`) conferem.
- Conferência 18/18 com diferença zero: reexecutada (G3).
- Tabela de resultado (`README.md:24-30`): 49.067, 45.836 e 3.231 conferem com a soma da série mensal e com a da tabela de ocupações. 16.894 / 45.836 = 36,86%, ou seja, 36,9%. A tabela tem 935 linhas, todas com movimentação maior que zero. A série tem saldo igual a admissões menos desligamentos em todos os meses.
- O "registro de cada execução" (`README.md:7`) existe para as saídas de HEAD, com SHA-256 iguais aos arquivos.
- "Qualquer município pode ser analisado trocando o código" (`README.md:10`): funciona para outro município da UF extraída (`mun:140002`). Para outra UF, exige um `extrair` dela, como a mensagem de erro informa.
- Limitações (`README.md:56-58`): corretas e coerentes com o método.

### Ressalvas

- **G5-2. Os "18 números" não são 18 verificações independentes** (`README.md:18`). O saldo de 09/2026 entra duas vezes: `novo-caged-…csv:13` (p. 31) e `:19` (p. 43). O saldo acumulado de 2026 (3.814, linha 16) é a soma dos 9 saldos mensais já conferidos. Restam 16 números distintos e 15 independentes. Basta dizer isso no texto.
- **G5-3. Rótulo de ajuste na p. 31.** A linha 13 do CSV oficial marca o saldo de 09/2026 como "sem ajuste", mas a p. 31 é "dados com ajustes declarados até setembro de 2026". Para o mês final os dois coincidem numericamente, e o resultado não muda. Só a transcrição diverge do rótulo da fonte.
- **G5-4. "Conferência número a número"** (`README.md:6`, `CITATION.cff:4`) cobre só admissões, desligamentos e saldo da UF. Os números do caso (município, a pedido, salário) não são conferidos contra fonte (G4-1 a G4-3). A tabela do README delimita isso, mas o resumo e o CITATION não.
- **G5-5. "Fixado antes da primeira execução"** (`README.md:20`, `docs/PROTOCOLO.md:8` e `:36`) é declaração sem prova possível no repositório. O critério e o CSV oficial já estão no commit inicial, e a data do git não prova anterioridade. Sugestão: apresentar como declaração do autor, não como fato verificável.
- **G5-6.** `README.md:36` lista "openpyxl 3.1.5" entre as "versões usadas no registro", mas `registrar()` (`caged.py:91-98`) não grava a versão do openpyxl. Ela está fixada só em `requirements.txt`.
- **G5-7.** O campo `"inicio"` dos registros (`caged.py:90-92`) é preenchido no fim da execução. No `extrair` reexecutado, ele marca 16:48:44 para um processo que começou às 15:49. O nome do campo está errado.
- **G5-8. Títulos ausentes.** Oito CBOs da tabela não têm título (`ocupacoes_mun140010_202510_202609.csv`, linhas 210, 258, 353, 421, 457, 458, 512 e 757), porque os códigos não existem na aba `cbo2002ocupação` do layout oficial (conferido no `layout.xlsx`, 2.778 códigos). A documentação não menciona isso.
- **G5-9. Título fora do medido.** "Rotatividade por ocupação" (`README.md:3`, `CITATION.cff:4`) promete uma medida que o repositório não calcula: não há taxa de rotatividade, e `README.md:57` admite que não há estoque. A frase "as taxas aqui são relativas às movimentações" também não tem objeto, porque a única taxa calculada é `pct_a_pedido`. Sugestão: "movimentação e desligamentos a pedido por ocupação".

Não há novidade alegada sem sustentação nem texto que soe como ataque a terceiros.

## Gate 6: justiça. **Não se aplica**

O repositório não compara opções, métodos nem ferramentas.

## Gate 7: tom. **Passa com ressalvas**

- **G7-1.** `docs/PROTOCOLO.md:3`, "## Histórico honesto": o adjetivo é defesa. Sugestão: "Histórico".
- **G7-2.** `docs/PROTOCOLO.md:7-8`: diário de construção e bastidor ("num script de projeto (não publicado). Produziu o ranking por ocupação usado como motivação"; "Este protocolo foi escrito e o script foi generalizado…"). O texto cita um artefato privado e um ranking que não estão no repositório. Para referência técnica basta registrar que houve uma análise exploratória prévia, não pré-registrada, e em que data.
- **G7-3.** `docs/PROTOCOLO.md:10`, "O que este pacote garante é que…": tom de defesa, e a frase inclui a afirmação de auditoria de G5-1.
- `README.md` e o restante de `docs/PROTOCOLO.md` são impessoais e técnicos. A seção "Uso de IA" (`README.md:52`, `docs/PROTOCOLO.md:39-44`) é uma declaração de método adequada (fora a frase de G5-1). Não há eco de conversa nos arquivos nem nas mensagens de commit.

---

## Resumo das correções

| Prioridade | Achado | Arquivo:linha |
|---|---|---|
| Bloqueia | G5-1: auditoria declarada como feita | `README.md:8`, `README.md:52`, `docs/PROTOCOLO.md:10`, `CITATION.cff:4`, `auditoria/README.md:7` |
| Ressalva | G4-1 a G4-3: indicador a pedido, recorte municipal e tabela de ocupações sem teste | `caged.py:46`, `:149-150`, `:209-229` |
| Ressalva | G4-5: hash do `.csv.gz` não reprodutível | `caged.py:190` |
| Ressalva | G5-2, G5-4, G5-9: alcance da conferência e do título | `README.md:3`, `:6`, `:18`, `CITATION.cff:4` |
| Ressalva | G5-3, G5-5 a G5-8 | ver itens |
| Ressalva | G7-1 a G7-3: tom do histórico | `docs/PROTOCOLO.md:3-10` |
| Menor | G4-4, G4-6, G4-7 | ver itens |

Correções que mudam código ou número (G4-5, e testes novos para G4-1 a G4-3) pedem nova verificação.

## Evidência guardada nesta auditoria

Fica fora do repositório auditado, na pasta temporária da sessão:
- log da reprodução: `…/scratchpad/repro.log`;
- mutantes e logs: `…/scratchpad/mut/d0…d6/` (`teste.log`, `conf.log`, `agr.log`);
- script dos mutantes: `…/scratchpad/scripts/mutante.sh`;
- PDFs oficiais baixados: `…/scratchpad/pdfs/`.

O prefixo `…` é `<pasta temporária da sessão do auditor>`.
