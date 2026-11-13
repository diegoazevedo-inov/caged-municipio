# Verificação dirigida (rodada 4): `caged-municipio`

- **Objeto:** `<repositório>`, ramo `main`, HEAD `6cd9caf` (8 commits). O parecer verificado é o da rodada 3, sobre `870009a` (`PARECER-a-verificar.md`). Ele é idêntico a `auditoria/rodada-3/VERIFICACAO.md` no repositório (`diff` vazio).
- **Commit novo desde o parecer:** só `6cd9caf` ("Auditoria rodada 3: teto do salário testado (r19, M1), .7z truncado no texto, registro da rodada"). São 9 arquivos, 284 linhas inseridas e 9 removidas. `caged.py`, `README.md`, `CITATION.cff`, `dados/` e `execucoes/` não mudaram (`git diff --stat 870009a HEAD` vazio para esses caminhos).
- **Data:** 12/11/2026.
- **Modo:** verificação dirigida, em sessão nova, num clone em pasta temporária. No original, só fiz leituras: `git status`, `git log`, `git fsck`, `git count-objects`, `git rev-list`, `reflog`, `for-each-ref`, `ls-files` e uma cópia de `dados/linhas/uf14_202510_202609.csv.gz`, que é ignorado pelo git. Não houve escrita no original, repositório remoto, push, modelo real nem API paga. No fim, `git status` do original continuava limpo, com HEAD em `6cd9caf`.
- **Ambiente:** Python 3.14.4, venv novo com `requirements.txt` (pandas 3.1.1, py7zr 1.1.4, openpyxl 3.1.5) e curl. Rede: só fontes públicas (PyPI e o `layout.xlsx` do FTP do PDET).
- **Restrição de escopo:** no original, `dados/brutos` é um link simbólico para a pasta de outro projeto do usuário. Não li esse link. Ele não é versionado (`.gitignore`). Não refiz o download dos 37 `.7z`. Como `caged.py` e os registros não mudaram desde a rodada 3, a extração não precisava ser refeita. O `.csv.gz` copiado tem o mesmo SHA-256 dos registros (`cf8457ce…`). Baixei de novo o `layout.xlsx`, com SHA-256 `0490f7ef…`, igual ao do manifesto.

## Veredito final: **pode ir a público com ressalvas**

As três ressalvas da rodada 3 foram tratadas. **R1, R2 e R3 estão resolvidas.** O achado G4-3 da rodada 1, que estava resolvido em parte pelo mesmo motivo de R1, também ficou resolvido. A suíte inteira passa. Os 14 defeitos plantados do script da rodada 3 (D1 a D7, N1 a N5, N8 e M1) são pegos sem exceção. A conferência dá 18/18, e as saídas versionadas saem idênticas.

Resta só uma ressalva, e ela é de procedimento:

1. **P1 (procedimento). Registrar esta rodada.** `auditoria/README.md:10` dá a rodada 4 como "pendente". Antes de publicar, essa linha precisa trazer o resultado desta verificação, e esta verificação tem de ser copiada para `auditoria/rodada-4/`. Esse registro não muda código nem número. Por isso não precisa de nova verificação, ao contrário de R1 na rodada 3.

Ficam duas observações sem efeito no veredito (O5 e O6, seção 7). Nenhuma delas é afirmação falsa, e corrigi-las é opcional.

| Item | Veredito |
|---|---|
| Achados da rodada 3 (R1, R2, R3) | 3 resolvidos. Ver 1.1 |
| Observações da rodada 3 (O1 a O4) | O2 e O3 foram tratadas, com texto correto. O1 e O4 não pediam correção e continuam válidas. Ver 1.2 |
| Achados das rodadas 1 e 2, no commit atual | Sem regressão. G4-3 passa de "resolvido em parte" a "resolvido". Ver 1.3 |
| Suíte de testes e verificação | Passa |
| Histórico | Passa |
| Varredura de dados | Passa |
| Arquivos novos e alterados | Passam |
| Afirmações novas além da evidência | Nenhuma que mereça ressalva. As observações O5 e O6 são sem efeito |

---

## 1. Achado por achado

Os números de linha são do commit `6cd9caf`.

### 1.1 Ressalvas da rodada 3

| Achado | Situação | Evidência |
|---|---|---|
| **R1**: teto do salário sem teste que o distinga | **Resolvido** | Linha nova em `teste_sintetico.py:79`: `lin("202602", "14", "140010", "521110", "1", "10", "60000,00")`. Ela está descrita no docstring em `:29` ("r19 … R$ 60.000, acima do teto de 50.000: conta, mas fora do salário"). Os valores esperados foram refeitos em `:93` (série 202602: `(5, 1, 4, 1, 5, 1, 4)`) e `:96` (521110: 7 admissões, saldo 5, 9 movimentações, mediana 3.000 e média 5.000 inalteradas). Refiz o cálculo à mão (seção 3) e ele confere. O mutante M1 (`between(200, 10**12)`) agora **é pego**, com falha em "ocupação 521110": obtido mediana 6.500 e média 18.750, esperado 3.000 e 5.000. Com isso, `docs/PROTOCOLO.md:36` ("os cinco filtros do salário (unidade mensal, intermitente, aprendiz, piso e teto)") e `teste_sintetico.py:8-9` passam a ser verdadeiros: tirar qualquer um dos cinco filtros faz o teste falhar (N3, N4, M1, D2/N5 e o filtro de aprendiz, que r9 cobre). Sobre o alcance do valor exato do corte, ver O5 |
| **R2**: ".7z corrompido" vai além do testado | **Resolvido** (limitação declarada com precisão) | `teste_sintetico.py:11-12` diz ".7z truncado com mensagem de orientação (só truncado: bytes corrompidos no meio não são tratados)". `auditoria/rodada-2/CORRECOES.md:17` diz "Um `.7z` truncado gera mensagem com orientação, não traceback (corrigido na rodada 3: antes dizia "corrompido")". Reproduzi a limitação com o código atual, que não mudou: gerei um `.7z` de 543.931 bytes no formato do PDET e inverti 64 bytes no byte 181.310, sem truncar. `ler_uf` terminou com `_lzma.LZMAError: Corrupt input data`, não tratado, exatamente como o texto agora declara. `git grep -i corromp HEAD` fora dos pareceres só acha esses textos corrigidos e a mensagem de `caged.py:139`, que é emitida justamente para o caso tratado (`Bad7zFile`). A mensagem do commit `34ebdc3` ainda diz ".7z corrompido", mas ela é histórico imutável sem reescrita, e o texto vigente está correto |
| **R3**: registrar a rodada 3 | **Resolvido** | `auditoria/README.md:9` traz a rodada 3 com o commit `870009a`, um link para `rodada-3/VERIFICACAO.md` (idêntico ao parecer verificado, `diff` vazio) e o veredito "pode ir a público com ressalvas: 3 ressalvas (R1–R3), nenhuma muda número publicado". Isso é fiel ao parecer ("Nenhuma muda um número publicado pelo código atual"). A pasta `auditoria/rodada-3/` tem `briefing.txt`, `VERIFICACAO.md`, `CORRECOES.md` e `defeitos_plantados.sh`. A rodada 4 aparece como pendente (`:10`). Ver P1 |

### 1.2 Observações da rodada 3

| Observação | Situação | Evidência |
|---|---|---|
| O1: "sem ajuste" na p. 31 é inferência | Sem mudança, como esperado | `dados/oficial/FONTES.md` e `README.md` não mudaram. A formulação precisa continua em `FONTES.md:10` |
| O2: histórico do protocolo cita só a rodada 1 | **Tratada** | `docs/PROTOCOLO.md:9`: "Auditoria independente: rodada completa e verificações dirigidas, com as correções de cada uma (ver `auditoria/`)". É correto e não afirma mais do que existe |
| O3: texto antigo em `rodada-1/CORRECOES.md` | **Tratada** | `auditoria/rodada-1/CORRECOES.md:3` tem uma nota que remete às revisões da rodada 2 ("são 17" e "volta a 'sem ajuste'"). As duas coisas conferem com V1 e V2. Ver O6 |
| O4: nome do arquivo no cabeçalho gzip | Sem mudança, como esperado | `README.md` não mudou, e a afirmação continua válida para quem usa o script. O `.csv.gz` copiado tem SHA-256 `cf8457ce…` |

### 1.3 Achados das rodadas 1 e 2, no commit atual

`caged.py`, `README.md`, `CITATION.cff`, `dados/` e `execucoes/` estão idênticos aos de `870009a`, onde a rodada 3 deu esses achados como resolvidos. As alterações de `6cd9caf` são só no teste, no protocolo e em `auditoria/`. A situação de cada achado se mantém, com uma melhora:

- **G4-3 (tabela por ocupação):** passa de **resolvido em parte** a **resolvido**. O teto agora é testado por cima (M1 pego) e por baixo (D2 pego).
- **V3 (rodada 2, salário e "sem ajuste" sem teste):** passa a estar **resolvido** pelo mesmo motivo.
- **Demais achados** (G5-1, G4-1, G4-2, G4-4 a G4-7, G5-2 a G5-9, G7-1 a G7-3, V1, V2, V4 a V7, G5-5 residual e N8): continuam **resolvidos**. Os defeitos plantados que os representam (D1 a D7, N1 a N5 e N8) são todos pegos (seção 2). `G5-5` continua em `docs/PROTOCOLO.md:8` e `:35`. A referência ao script de defeitos em `docs/PROTOCOLO.md:37` foi atualizada para `auditoria/rodada-3/defeitos_plantados.sh`, que existe e funciona.

## 2. Suíte de testes e de verificação

Rodei os comandos no clone. Para o teste com dados reais, copiei o `.csv.gz` do original e baixei de novo o `layout.xlsx`.

| Comando | Resultado |
|---|---|
| `python -I teste_sintetico.py` | `TESTE PASSA: 0 falha(s)`, 14 verificações, saída 0, sem download. Agregação sintética: `totais (com ajustes): {admissoes: 9, desligamentos: 5, saldo: 4, deslig_a_pedido: 2, ocupacoes: 2}`. `git status` limpo depois |
| `PYTHON=… bash auditoria/rodada-3/defeitos_plantados.sh` | D0 sai com 0. D1 a D7, N1 a N5, N8 e **M1** saem com 1, com 0 exceção. M1 falha em "ocupação 521110", como diz `auditoria/rodada-3/CORRECOES.md:20`. Saída final: `DEFEITOS: todos pegos pelo teste, sem exceção`, código 0 |
| `bash auditoria/rodada-2/defeitos_plantados.sh` | `todos pegos`, código 0 |
| `bash auditoria/rodada-1/defeitos_plantados.sh` | `todos pegos`, código 0 |
| `caged.py conferir --oficial dados/oficial/novo-caged-2026-09-uf14.csv --ini 202510 --fim 202609` | `PASSA: 18 de 18 números iguais aos publicados`, saída 0 |
| `caged.py agregar --recorte mun:140010 --ini 202510 --fim 202609` | `{admissoes: 49067, desligamentos: 45836, saldo: 3231, deslig_a_pedido: 16894, ocupacoes: 935}`, saída 0. Confere com o `README.md` |
| `caged.py agregar --recorte mun:149999 …` | "recorte mun:149999 sem nenhuma linha…", saída 1 |
| `python -I teste_conferencia.py` | `real -> saída 0 \| defeito -> saída 1`, `TESTE PASSA` |
| `git diff --stat` depois das execuções | **Vazio** (só os registros novos em `execucoes/`, não versionados) |
| SHA-256 das 4 saídas versionadas | Iguais aos dos registros: conferência `3f3dd749…`, série `91426483…`, ocupações `fb327ddc…`, manifesto `00e8a288…` |

**Variantes do corte salarial plantadas nesta rodada** (`sed` numa cópia de `caged.py`, com a suíte rodada sobre a cópia e o efeito medido com os dados reais):

| # | Defeito | `teste_sintetico.py` | Efeito nas saídas reais de Boa Vista |
|---|---|---|---|
| M1 | Sem teto: `between(200, 10**12)` | **pega** | (rodada 3) Pedreiro 715210, média de 2.535,81 para 2.964,55 |
| T70 | Teto em 70.000 | **pega** | — |
| T55 | Teto em 55.000 | não pega | Nenhum: `git diff` vazio |
| TB | Teto exclusivo: `inclusive="left"` | não pega | Nenhum: `git diff` vazio |
| T20 | Teto em 20.000 | não pega | Muda 6 linhas de `ocupacoes_…csv`, por exemplo Administrador (252105), média de 4.201,80 para 3.967,15, e Diretor de Relações de Trabalho (123210), salário de 25.821,66 para vazio. Ver O5 |
| P1000 | Piso em 1.000 | não pega | Não medido. É a mesma natureza de T20, já presente desde a rodada 2 |

Os scripts e os logs ficaram na pasta temporária (seção 8).

## 3. Conferência à mão do teste sintético (o que mudou)

- **Série 202602.** Admissões MOV: r10, r15, r16, r17 e **r19**, dá 5. Desligamento: r11 (tipo 40, a pedido), dá 1. Saldo: 4. A pedido: 1. Como só há MOV em 202602, o "sem ajuste" é igual: 5, 1 e 4. O esperado é `(5, 1, 4, 1, 5, 1, 4)` (`teste_sintetico.py:93`). Confere.
- **Ocupação 521110.** Admissões: r1, r2, r9, r10, r15, r16, r17 e **r19**, menos r14, dá 7. Desligamentos: r3 e r11, dá 2. Saldo: 5. A pedido: 2, ou 100%. Movimentações: 9. O salário continua só com r1 (2.000), r2 (10.000) e r10 (3.000): mediana 3.000 e média 5.000. Com M1, entra também r19: com {2.000, 3.000, 10.000, 60.000}, a mediana é 6.500 e a média é 18.750, que são exatamente os valores obtidos pelo mutante.
- **Série 202601 e ocupação 411005:** não mudaram, e os valores conferidos na rodada 3 seguem válidos.
- **Totais sintéticos:** 4 + 5 = 9 admissões, 4 + 1 = 5 desligamentos, saldo 4 e 2 desligamentos a pedido. Batem com a saída da agregação.

## 4. Histórico

- `git log --all`: 8 commits (`9321b30`, `e5ee630`, `4c82547`, `0f42f4c`, `fdc773b`, `34ebdc3`, `870009a`, `6cd9caf`) e um só ramo (`refs/heads/main`), sem tags, stash nem remoto.
- No original, `git fsck --unreachable --no-reflogs --full` não deu saída (código 0). `git count-objects -v` mostra 106 objetos soltos, 0 em pack e `garbage: 0`, e `git rev-list --objects --all | wc -l` dá 106: todos são alcançáveis.
- O reflog é o mesmo da rodada 3 mais `6cd9caf` (commit direto). O caminho da pasta temporária do `pull --ff-only` de `34ebdc3` continua só no reflog local, que não vai para clones nem para push.
- Autor e committer de todos os commits: `Diego <diego@example.com>`. Todas as mensagens trazem `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, coerente com `docs/PROTOCOLO.md:41`. A mensagem de `6cd9caf` descreve a mudança em termos técnicos e não exagera: o teto foi testado, "truncado" está no texto e a rodada foi registrada.
- Nenhum arquivo foi removido em `6cd9caf`. Os 37 arquivos versionados têm modo 100644. Os ignorados no original (`__pycache__/`, `dados/brutos`, `dados/linhas/` e os 2 PDFs) não entram no repositório.

## 5. Varredura de dados

Fiz `git grep -I -i -E` em todos os commits (`git rev-list --all`), exceto `LICENSE`, e também nas mensagens de commit (`git log --all --format=%B`). Procurei: `/home`, `/tmp/`, `/Users`, `C:\`, `diego`, `gmail`, `hotmail`, `outlook.`, qualquer e-mail, `token`, `senha`, `password`, `passwd`, `secret`, `api_key`, `chave`, `bearer`, chave privada, `ghp_`, `gho_`, `github_pat`, `sk-`, `AKIA`, `xoxb-`/`xoxp-`, `client`, `clínica`/`clinica`, `paciente`, `cpf`, `telefone`, `whatsapp`, `scratchpad`, o nome do projeto para onde aponta o link `dados/brutos` e nomes de provedores. Ocorrências, todas já conhecidas ou equivalentes às da rodada 3:

- `auditoria/rodada-1/briefing.txt:7`, `auditoria/rodada-2/briefing.txt:5` e **`auditoria/rodada-3/briefing.txt:5`** (novo): as palavras "cliente, clínica, paciente" no texto do critério.
- `auditoria/rodada-1/PARECER.md:32`, `:39` e `:155-158`: o e-mail de exemplo e `…/scratchpad/…`, com o prefixo trocado por marcador.
- `auditoria/rodada-2/VERIFICACAO.md:119`, `:125-132` e **`auditoria/rodada-3/VERIFICACAO.md:115`, `:121-130`** (novo): citações das varreduras anteriores.
- `docs/PROTOCOLO.md:41`: "Claude, Anthropic", a declaração de método.
- `dados/saidas/ocupacoes_…csv`: títulos oficiais da CBO. É nomenclatura pública.
- Mensagens de commit: só a linha `Co-Authored-By` com `noreply@anthropic.com`.

Nenhum segredo, caminho pessoal, nome de cliente, clínica ou paciente. Os arquivos novos de `auditoria/rodada-3/` usam os marcadores `<repositório>`, `<pasta da auditoria>` e `<pasta temporária da sessão do auditor>`, sem caminho absoluto. O nome e o ORCID em `CITATION.cff` são a autoria declarada e não mudaram.

## 6. Arquivos novos e alterados desde o parecer

| Arquivo | Situação |
|---|---|
| `teste_sintetico.py` (alterado) | A linha r19 e os valores esperados conferem com o cálculo à mão (seção 3). O docstring (`:11-12`) agora declara o limite do `.7z` com precisão. A linha 12 ficou mais longa que as demais, o que é só cosmético |
| `docs/PROTOCOLO.md` (alterado) | `:9`, ver O2. `:36` enumera os cinco filtros, o que agora é sustentado (R1). `:37` aponta para o script da rodada 3, que existe e funciona |
| `auditoria/README.md` (alterado) | A linha da rodada 3 está correta (R3). A rodada 4 aparece como pendente (P1). Ver O6 sobre `:12` |
| `auditoria/rodada-1/CORRECOES.md` (alterado) | A nota do topo (`:3`) está correta. Ver O3 e O6 |
| `auditoria/rodada-2/CORRECOES.md` (alterado) | `:17` corrigido e marcado como tal. Ver R2 e O6 |
| `auditoria/rodada-3/CORRECOES.md` (novo) | Reproduzi cada afirmação. "`caged.py` não mudou nesta rodada, e as saídas versionadas e os registros de execução continuam os da rodada 2" (`:5`): o `git diff 870009a HEAD` é vazio para esses caminhos. A tabela de evidência (`:19-20`): `TESTE PASSA`, os valores 7, 5, 9 e 5, 4, e "M1 falha em 'ocupação 521110'" conferem com as minhas execuções. "A mudança é só no teste" (`:22`): no código, sim. O restante são textos e registro |
| `auditoria/rodada-3/VERIFICACAO.md` (novo) | Idêntico ao parecer verificado (`diff` vazio) |
| `auditoria/rodada-3/briefing.txt` (novo) | Mesmo texto do briefing desta rodada, com os caminhos trocados por marcadores. Nada sensível |
| `auditoria/rodada-3/defeitos_plantados.sh` (novo) | Funciona: verifica se cada `sed` se aplicou (`cmp`), roda com `-I` e conta tracebacks. Inclui todos os defeitos das rodadas anteriores mais M1. O comentário sobre N6 e N7 (`:5`) continua coerente com a rodada 2 |

## 7. Afirmações novas além da evidência

Nenhuma afirmação nova introduzida pelas correções vai além da evidência a ponto de pedir ressalva. Registro duas observações sem efeito no veredito.

### O5. "Cobre o teto": a existência do corte está testada, o valor exato não

`docs/PROTOCOLO.md:36` e `teste_sintetico.py:8-9` dizem que o teste cobre o piso e o teto. Isso é verdade no sentido em que a rodada 3 cobrou: retirar o filtro faz o teste falhar (M1 pego). Mas o teste localiza o corte só dentro de um intervalo. O teto pode estar em qualquer ponto de [10.000; 60.000), entre r2 (incluído) e r19 (excluído), e o piso em qualquer ponto de (150; 1.800], entre r17 (excluído) e o menor salário incluído. Um teto de 20.000 (T20) passa pela suíte e mudaria 6 linhas publicadas. Um teto de 55.000 ou exclusivo em 50.000 não muda nenhuma saída real. Essa granularidade é a mesma que a rodada 3 aceitou para o piso (N5 pego, e só isso). O valor 50.000 está escrito no código (`caged.py:244`) e no protocolo (`docs/PROTOCOLO.md:28`), e nenhum texto diz que o teste fixa o valor exato. Se quiserem fechar a lacuna, bastam duas linhas sintéticas de admissão, por exemplo R$ 49.000 (incluída) e R$ 199 (excluída). Isso mudaria os valores esperados de salário e pediria uma nova verificação curta, então é opcional.

### O6. "O restante é o texto original" e os `CORRECOES.md` editados

`auditoria/README.md:12` diz que, nos arquivos das rodadas, só os caminhos foram trocados e "o restante é o texto original". Nesta rodada, `rodada-1/CORRECOES.md` ganhou uma nota (`:3`), e `rodada-2/CORRECOES.md:17` foi reescrito. As duas mudanças estão marcadas no próprio texto: a nota em bloco de citação e "(corrigido na rodada 3: antes dizia "corrompido")". Os pareceres dos auditores (`PARECER.md` e `VERIFICACAO.md`) seguem intactos, e o `git log` mostra o texto anterior. Por isso, nenhum leitor é enganado. Para a frase ficar literal, basta acrescentar a ela "exceto notas marcadas, acrescentadas em rodadas posteriores aos `CORRECOES.md`". É opcional.

## 8. Evidência guardada nesta verificação

Fica fora do repositório auditado, na pasta temporária da sessão (`<pasta temporária da sessão do auditor>`):

- `logs/sint.log`, `logs/defeitos_r3.log`, `logs/defeitos_r2.log`, `logs/defeitos_r1.log`, `logs/real.log` (agregar, recorte inexistente e `teste_conferencia.py`), `logs/conferir.log` e `logs/corrompido.log`;
- `mut/M1`, `mut/T20`, `mut/T55`, `mut/T70`, `mut/TB` e `mut/P1000` (`caged.py` e `sint.log`), mais `real_T20/`, `real_T55/` e `real_TB/` (clones com as saídas reais regeradas pelos mutantes);
- `scripts/corrompido.py`, o `.7z` com 64 bytes invertidos, que reproduz o `LZMAError`.

## 9. O que fazer antes de publicar

| Prioridade | Item | Onde | Muda número/código? |
|---|---|---|---|
| Ressalva (procedimento) | P1: registrar esta rodada (copiar este arquivo para `auditoria/rodada-4/VERIFICACAO.md`, com os caminhos trocados por marcadores, e preencher a linha da rodada 4) | `auditoria/README.md:10`, `auditoria/rodada-4/` | Não. Não pede nova verificação |
| Opcional | O6: precisar a frase sobre o texto original | `auditoria/README.md:12` | Não |
| Opcional | O5: fixar o valor dos cortes com linhas em R$ 49.000 e R$ 199 | `teste_sintetico.py` | Teste (pediria verificação curta). Nenhum número publicado muda |

Com P1 feito, o pacote fica sem ressalva conhecida.
