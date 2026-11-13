# Verificação dirigida (rodada 3): `caged-municipio`

- **Objeto:** `<repositório>`, ramo `main`, HEAD `870009a` (7 commits). O parecer verificado é o da rodada 2, sobre `0f42f4c` (`PARECER-a-verificar.md`). Ele é idêntico a `auditoria/rodada-2/VERIFICACAO.md` no repositório (`diff` vazio).
- **Commits novos desde o parecer:** `fdc773b` (testes e textos), `34ebdc3` (download para `.parte`, `.7z` corrompido com mensagem) e `870009a` (registro da rodada 2 e saídas regeradas).
- **Data:** 12/11/2026.
- **Modo:** verificação dirigida, em sessão nova, num clone em pasta temporária (`clone`). Do original, só fiz leituras: `git status`, `git log`, `git fsck`, `git count-objects`, `git rev-list`, `reflog` e uma cópia de `dados/linhas/uf14_202510_202609.csv.gz`, que é ignorado pelo git. Não houve escrita no original, repositório remoto, push, modelo real nem API paga. No fim, `git status` do original continuava limpo, com HEAD em `870009a`.
- **Ambiente:** Python 3.14.4, venv com `requirements.txt` (pandas 3.1.1, py7zr 1.1.4, openpyxl 3.1.5), zlib 1.3.1, curl e pdftotext. Rede: só fontes públicas (`layout.xlsx` do FTP do PDET e o PDF da apresentação no gov.br).
- **Restrição de escopo:** no original, `dados/brutos` é um link simbólico para a pasta de outro projeto do usuário. Não li esse link. Ele não é versionado (`.gitignore`). Não refiz o download completo dos 37 `.7z`, cerca de 620 MB, que a rodada 2 já tinha refeito com o mesmo SHA-256. Os brutos não mudaram desde então: o registro novo `execucoes/20261112T200037-extrair.json` traz `difere_do_manifesto_anterior: []` e as mesmas linhas, `cf8457ce…`. Baixei de novo só o `layout.xlsx` e o PDF oficial.

## Veredito final: **pode ir a público com ressalvas**

As sete ressalvas da rodada 2 foram tratadas. V1, V2, V4, V5, V6 e V7 estão resolvidas. V3 está resolvida em parte: o teste agora pega os defeitos N1, N3, N4 e N5, mas o texto novo passou a dizer que o teste cobre "os cinco filtros do salário (… piso e **teto**)", e o teto só é testado por baixo. A suíte inteira passa, os 14 defeitos plantados da rodada 2 são pegos, a conferência dá 18/18 e as saídas versionadas saem idênticas.

As ressalvas que restam são todas de texto ou de teste. Nenhuma muda um número publicado pelo código atual.

1. **R1. Teto do salário sem teste que o distinga.** `docs/PROTOCOLO.md:36` e `teste_sintetico.py:8-9` dizem que o teste cobre os cinco filtros do salário, incluindo o teto. Tirar o teto (defeito M1) passa pela suíte inteira e muda uma coluna publicada: a média salarial de admissão de Pedreiro (CBO 715210) em Boa Vista passa de 2.535,81 para 2.964,55.
2. **R2 (menor). ".7z corrompido" vai além do que foi testado.** `teste_sintetico.py:11-12` e `auditoria/rodada-2/CORRECOES.md:17` dizem que um `.7z` corrompido gera mensagem de orientação, sem traceback. Isso só vale para o `.7z` truncado. Um `.7z` com bytes corrompidos no meio gera um traceback `_lzma.LZMAError: Corrupt input data`, que o código não trata.
3. **R3 (procedimento). Registrar esta rodada.** `auditoria/README.md:9` dá a rodada 3 como "pendente". É a mesma situação de V5: antes de publicar, a linha precisa trazer o resultado desta verificação.

| Item | Veredito |
|---|---|
| Achados da rodada 2 (V1 a V7, mais G5-5 residual e N8) | 8 resolvidos e 1 resolvido em parte (V3). Ver 1.1 |
| Achados da rodada 1 (19), no commit atual | 18 resolvidos e 1 resolvido em parte (G4-3, pelo mesmo motivo de R1). Sem regressão. Ver 1.2 |
| Suíte de testes e verificação | Passa |
| Histórico | Passa |
| Varredura de dados | Passa |
| Arquivos novos | Passam, com as ressalvas R1 e R2 |
| Afirmações novas além da evidência | R1, R2. As observações O1 a O4 são sem efeito |

---

## 1. Achado por achado

Os números de linha são do commit `870009a`.

### 1.1 Achados da rodada 2

| Achado | Situação | Evidência |
|---|---|---|
| **V1**: "16 valores distintos" | **Resolvido** | `README.md:21` diz: "Há 17 valores distintos, porque o saldo de 09/2026 (1.068) aparece nas páginas 31 e 43." Pelo `pandas`, o CSV oficial tem 18 linhas e `nunique` = 17, e só 1.068 se repete (linhas 13 e 19 do CSV). As dependências aritméticas descritas conferem: 109 + 354 + 730 + 376 + 203 + 195 + 388 + 391 + 1.068 = 3.814, 42.095 − 38.281 = 3.814 e 5.060 − 3.992 = 1.068. `auditoria/rodada-1/CORRECOES.md:17` ainda diz "16", mas é o registro histórico da rodada 1, e a correção está em `auditoria/rodada-2/CORRECOES.md:11` (ver O3) |
| **V2**: rótulo de 09/2026 na p. 31 | **Resolvido** | `dados/oficial/novo-caged-2026-09-uf14.csv:13` voltou a "sem ajuste". O mesmo vale para `dados/saidas/conferencia_novo-caged-2026-09-uf14.csv:13`, regerado. A nota está explicada em `dados/oficial/FONTES.md:10` e em `README.md:21`. No PDF baixado de novo (SHA-256 `063267f6…`, igual ao de `FONTES.md`), a p. 31 tem a nota "*De setembro de 2025 a agosto de 2026, consideram-se ajustes declarados até o mês de setembro de 2026", conferida com `pdftotext`. A conferência dá 18/18 e muda só o rótulo da linha (`git diff 0f42f4c HEAD -- dados/saidas`: 1 linha). Ver O1 |
| **V3**: salário e "sem ajuste" sem teste | **Resolvido em parte** | Linhas novas em `teste_sintetico.py:75-77` (intermitente, unidade 3, R$ 150) e `:81` (r18, desligamento FOR sem exclusão). Os valores esperados em `:89-96` conferem com o meu cálculo à mão, linha a linha (seção 3). N1, N3, N4 e N5 agora são pegos (seção 2). **Falta:** o teto. Ver R1 |
| **V4**: "pipeline completo" | **Resolvido** | `README.md:7` diz "teste da extração e da agregação", e `docs/PROTOCOLO.md:36` diz "roda a extração e a agregação … Ficam fora dele o download e a conferência". `teste_sintetico.py:2` ainda diz "Pipeline completo (extrair -> agregar)", mas o parêntese delimita o alcance, como a rodada 2 já tinha aceitado. `CITATION.cff:4` diz "teste do pipeline", sem "completo" |
| **V5**: rodada 2 sem registro | **Resolvido** | `auditoria/README.md:8` traz a rodada 2 com o commit `0f42f4c`, um link para `rodada-2/VERIFICACAO.md` (idêntico ao parecer verificado) e o veredito correto. A pasta `auditoria/rodada-2/` tem `briefing.txt`, `VERIFICACAO.md`, `CORRECOES.md` e `defeitos_plantados.sh`. A rodada 3 aparece como pendente (`:9`). Ver R3 |
| **V6**: SHA-256 do gzip e zlib | **Resolvido** | `README.md:51` diz: "na mesma versão da zlib (verificado com a zlib 1.3.1) … nesse caso, compare o CSV descompactado". Regravei as linhas a partir do conteúdo descompactado, com `caged.GZIP` e o mesmo nome de arquivo: deu de novo `cf8457ce…`, com o conteúdo `378236b9…`. Os bytes 4 a 7 do cabeçalho valem `0 0 0 0` (`od`). Ver O4 |
| **V7**: download interrompido deixa `.7z` truncado | **Resolvido** (código). O texto sobre corrupção vai além: ver R2 | `caged.py:109-121` (`baixar_url`): grava em `.parte`, apaga na falha, sai com mensagem e renomeia só quando dá certo. `caged.py:135-139`: trata `Bad7zFile`. Fiz duas simulações com um servidor HTTP local que anuncia 100.000 bytes. (a) A conexão cai em 40.000: curl sai com 18, a mensagem é "falha ao baixar … rode o comando de novo", saída 1, e não sobra nenhum arquivo. (b) O processo é morto (SIGKILL) no meio da transferência: sobra só `CAGEDMOV209901.7z.parte` (36.864 bytes), e a chamada seguinte não reaproveita nada, porque o nome final não existe. A mesma simulação (b) com o mutante M2 (sem `.parte`) deixa o `.7z` truncado com o nome final, e ele seria reaproveitado. O teste automático não distingue os dois casos (M2 passa), e essa limitação está declarada com precisão em `auditoria/rodada-2/CORRECOES.md:46` |
| **G5-5 residual** | **Resolvido** | `docs/PROTOCOLO.md:35`: "**Critério, fixado antes da execução (declaração do autor):**" |
| **N8**: aviso do manifesto sem teste | **Resolvido** | `teste_sintetico.py:134-144` altera o SHA-256 de `CAGEDFOR202602.7z` no manifesto, extrai de novo e confere a lista `difere_do_manifesto_anterior`. O mutante N8 é pego, com falha em "aviso de bruto diferente do manifesto" |

### 1.2 Achados da rodada 1, no commit atual

| Achado | Situação | Evidência |
|---|---|---|
| G5-1 (bloqueio): auditoria declarada | **Resolvido** | `README.md:9` e `:57`, `docs/PROTOCOLO.md:43` e `CITATION.cff:4` remetem a `auditoria/`, onde as rodadas 1 e 2 estão registradas (`auditoria/README.md:7-8`). Nenhum texto afirma mais que isso |
| G4-1: a pedido | **Resolvido** | O D1 é pego, com falha em "série 202601; série 202602; ocupação 521110" |
| G4-2: recorte municipal | **Resolvido** | O D3 é pego, com falha em "série 202601; ocupação 521110" |
| G4-3: tabela por ocupação | **Resolvido em parte** | Unidade, intermitente, aprendiz e piso agora estão cobertos (N3, N4 e N5 pegos). O teto só é testado por baixo, com D2 (teto de 5.000) pego, mas M1 (sem teto) não. Ver R1 |
| G4-4: o teste não exercita `extrair` | **Resolvido** | `teste_sintetico.py:126-142` chama `caged.extrair`, e `:174-185` exercita `baixar_url` com `file://`. O download real fica de fora, como `teste_sintetico.py:12` declara |
| G4-5: SHA-256 do `.csv.gz` | **Resolvido** | O D7 é pego. Ver V6 |
| G4-6: recorte inexistente | **Resolvido** | `agregar --recorte mun:149999` dá "recorte mun:149999 sem nenhuma linha…" e sai com 1 |
| G4-7: brutos contra o manifesto | **Resolvido** | Agora há teste automático. Ver N8 |
| G5-2: 18 ≠ 18 independentes | **Resolvido** | Ver V1 |
| G5-3: rótulo da p. 31 | **Resolvido** | A premissa do achado estava errada (rodada 2), e o rótulo voltou ao que a fonte sustenta. Ver V2 |
| G5-4: "número a número" | **Resolvido** | `README.md:6` e `:15`, `docs/PROTOCOLO.md:36` |
| G5-5: "fixado antes" | **Resolvido** | `README.md:23` e `docs/PROTOCOLO.md:8` e `:35` |
| G5-6: openpyxl no registro | **Resolvido** | `caged.py:99`. Os registros novos trazem `"openpyxl": "3.1.5"` |
| G5-7: `inicio` | **Resolvido** | `caged.py:53` e `:97`. Em `20261112T200037-extrair.json`, `inicio` é 19:59:35 e `fim` é 20:00:37 |
| G5-8: CBOs sem título | **Resolvido** | `README.md:64`. A tabela versionada não mudou desde a rodada 2 (`git diff 0f42f4c HEAD` vazio nesse arquivo) |
| G5-9: título e rotatividade | **Resolvido** | `README.md:1`, `:62` e `CITATION.cff:3` |
| G7-1: "Histórico honesto" | **Resolvido** | `docs/PROTOCOLO.md:3` |
| G7-2: bastidor no histórico | **Resolvido** | `docs/PROTOCOLO.md:7` |
| G7-3: "garante" | **Resolvido** | `git grep -i garant HEAD` só acha ocorrências dentro de `auditoria/` |

## 2. Suíte de testes e de verificação

Comandos rodados em `clone`, com o `.csv.gz` copiado do original (SHA-256 `cf8457ce…`, igual ao dos registros `execucoes/20261112T195851-conferir.json`, `…195852-agregar.json` e `…200037-extrair.json`) e o `layout.xlsx` baixado de novo (SHA-256 `0490f7ef…`, igual ao do manifesto).

| Comando | Resultado |
|---|---|
| `python -I teste_sintetico.py` | `TESTE PASSA: 0 falha(s)`, 14 verificações, saída 0, cerca de 2 s, sem download. `git status` limpo depois |
| `PYTHON=… bash auditoria/rodada-2/defeitos_plantados.sh` | D0 sai com 0. D1 a D7, N1 a N5 e N8 saem com 1, sem traceback. As verificações que falham são **idênticas** às de `auditoria/rodada-2/CORRECOES.md:37-42`. Saída final: `DEFEITOS: todos pegos pelo teste, sem exceção` |
| `bash auditoria/rodada-1/defeitos_plantados.sh` | Também passa: `todos pegos` |
| `caged.py conferir …` | `PASSA: 18 de 18`, saída 0. A linha de 09/2026 da p. 31 aparece com "sem ajuste" |
| `caged.py agregar --recorte mun:140010 …` | `{admissoes: 49067, desligamentos: 45836, saldo: 3231, deslig_a_pedido: 16894, ocupacoes: 935}`, saída 0. Confere com `README.md:29-33` |
| `caged.py agregar --recorte mun:149999 …` | Mensagem de erro, saída 1 |
| `python -I teste_conferencia.py` | `real -> saída 0 \| defeito -> saída 1`, `TESTE PASSA` |
| `git diff --stat dados/saidas/` | **Vazio** |
| SHA-256 das 4 saídas versionadas | Iguais aos campos `saidas` dos registros de `34ebdc3` (conferência `3f3dd749…`, série `91426483…`, ocupações `fb327ddc…`, manifesto `00e8a288…`) |

**Defeitos novos plantados nesta rodada** (`sed` numa cópia de `caged.py`, com a suíte rodada sobre a cópia):

| # | Defeito | `teste_sintetico.py` | Efeito |
|---|---|---|---|
| M1 | Teto do salário retirado: `between(200, 10**12)` (`caged.py:244`) | **não pega** | Muda uma célula publicada em Boa Vista: `715210,Pedreiro`, `salario_medio_admissao` de 2535.81 para 2964.55. Há 22 linhas com salário acima de 50.000 no município. A mediana não muda em nenhuma ocupação |
| M2 | Sem `.parte`: grava direto no destino (`caged.py:115`) | não pega | Na queda de conexão, o `unlink` da falha apaga o arquivo de qualquer jeito. Na morte do processo, sobra o `.7z` truncado com o nome final. Limitação declarada em `CORRECOES.md:46` |
| M3 | Sem `parte.unlink` na falha (`caged.py:118`) | não pega | Nos testes, o curl não cria o arquivo quando a fonte não existe. Na queda simulada, o curl sai com 18 e deixaria o `.parte`, que o comando seguinte sobrescreve, porque não tem o nome final. Sem efeito em resultado |
| M4 | Aceita arquivo de tamanho 0 (`caged.py:112`) | não pega | Comportamento anterior às correções, fora do alcance declarado |
| M5 | Não trata `Bad7zFile` (`caged.py:138`) | pega (traceback, saída 1) | — |

O script e os logs ficaram na pasta temporária (seção 8).

## 3. Conferência à mão do teste sintético

- **Série 202601, com ajuste.** Admissões: r1, r2, r6, r9 (MOV) e r13 (FOR), menos r14 (EXC), dá 4. Desligamentos: r3, r4, r5 e r18, dá 4. Saldo: 0. A pedido: 1 (r3). **Sem ajuste**, só MOV: 4 admissões, 3 desligamentos e saldo 1. O esperado é `(4, 4, 0, 1, 4, 3, 1)` (`teste_sintetico.py:90`). r18 separa com e sem ajuste nos desligamentos. Por isso N1, que usa todas as linhas no "sem ajuste", passa a dar 4 desligamentos e é pego.
- **Série 202602.** Admissões: r10, r15, r16 e r17. Desligamento: r11. O esperado é `(4, 1, 3, 1, 4, 1, 3)` (`:91`).
- **Ocupação 521110.** Admissões: r1, r2, r9, r10, r15, r16 e r17, menos r14, dá 6. Desligamentos: 2. Saldo: 4. A pedido: 2, ou 100%. Movimentações: 8. O salário entra só com r1 (2.000), r2 (10.000) e r10 (3.000), o que dá mediana 3.000 e média 5.000. Com N3, N4 ou N5, entraria mais uma linha (1.000, 2.500 ou 150), e a mediana mudaria para 2.500, 2.750 ou 2.500.
- **Ocupação 411005.** Admissões: r6 e r13. Desligamentos: r4, r5 e r18. Saldo: −1. Salário de r6 (1.800) e r13 (2.500): mediana e média de 2.150.
- **Lacuna do teto.** O maior salário sintético é 10.000 (r2). Isso prova que o teto não está abaixo de 10.000 (D2 pego), mas não que ele exista: nenhuma linha passa de 50.000.

## 4. Histórico

- `git log --all`: 7 commits (`9321b30`, `e5ee630`, `4c82547`, `0f42f4c`, `fdc773b`, `34ebdc3`, `870009a`) e um só ramo (`main`), sem tags, stash nem remoto.
- No original, `git fsck --unreachable --no-reflogs --full` não deu saída (código 0). `git count-objects -v` mostra 91 objetos soltos e 0 em pack, e `git rev-list --objects --all | wc -l` dá 91: todos são alcançáveis.
- O reflog tem os 7 commits. `fdc773b` e `34ebdc3` entraram por `pull --ff-only` a partir de um clone numa pasta temporária local. O caminho dessa pasta aparece só no reflog local, que não vai para clones nem para push. Ele não está em nenhum objeto versionado (varredura abaixo).
- Autor e committer de todos os commits: `Diego <diego@example.com>`, com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, coerente com `docs/PROTOCOLO.md:41`. As mensagens de `fdc773b` e `34ebdc3` descrevem as mudanças em termos técnicos, sem eco de conversa.
- Nenhum arquivo foi removido nos commits novos. Todos os 33 arquivos versionados têm modo 100644.
- Ordem dos registros de `34ebdc3`: `conferir` (19:58:51) e `agregar` (19:58:52) rodaram antes de `extrair` (20:00:37). Não há incoerência, porque as três execuções registram o mesmo SHA-256 das linhas (`cf8457ce…`) e o `extrair` não acusou diferença no manifesto.

## 5. Varredura de dados

Fiz `git grep -I -i -E` em todos os commits (`git rev-list --all`), exceto `LICENSE`, e também nas mensagens de commit (`git log --all --format=%B`). Procurei: `/home`, `/tmp/`, `/Users`, `C:\`, `diego`, `gmail`, `hotmail`, `outlook.`, e-mails, `token`, `senha`, `password`, `passwd`, `secret`, `api_key`, `chave`, `bearer`, chave privada, `ghp_`, `gho_`, `github_pat`, `sk-`, `AKIA`, `xoxb-`, `cliente`, `clínica`/`clinica`, `paciente`, `cpf`, `telefone`, `whatsapp`, `scratchpad`, o nome da pasta para onde aponta o link `dados/brutos`, o nome do projeto que aparece no reflog e nomes de provedores. Ocorrências:

- `auditoria/rodada-1/briefing.txt:7` e `auditoria/rodada-2/briefing.txt:5`: as palavras "cliente, clínica, paciente" no texto do critério.
- `auditoria/rodada-1/PARECER.md:32`, `:39` e `:155-158`: o e-mail de exemplo e `…/scratchpad/…`, com o prefixo trocado por marcador.
- `auditoria/rodada-2/VERIFICACAO.md:119`, `:125-132`: citações das varreduras anteriores.
- `docs/PROTOCOLO.md:41`: "Claude, Anthropic", a declaração de método.
- `dados/saidas/ocupacoes_…csv`: títulos oficiais da CBO ("Clinica[s]", "Secretari…", "Chaveiro", "Gerente de Clientes Especiais"). É nomenclatura pública.
- Mensagens de commit: nenhuma ocorrência.

Nenhum segredo, caminho pessoal, nome de cliente, clínica ou paciente. Os arquivos novos da rodada 2 usam os marcadores `<repositório>`, `<pasta da auditoria>` e `<pasta temporária da sessão do auditor>`, como anuncia `auditoria/README.md:11`. O nome e o ORCID em `CITATION.cff:7-9` são a autoria declarada.

## 6. Arquivos novos desde o parecer

| Arquivo | Situação |
|---|---|
| `teste_sintetico.py` (alterado) | Os valores esperados conferem com o cálculo à mão (seção 3). Isola as pastas numa pasta temporária e não suja o repositório. Lacunas: R1 (teto) e M2 (`.parte`, declarado). O docstring (`:11-12`) exagera em "corrompido" (R2) |
| `caged.py` (alterado) | `baixar_url` faz o que o README diz, como mostram as simulações (a) e (b) em V7. `ler_uf` só trata `Bad7zFile` (R2). Não há outra mudança de lógica: o `git diff 0f42f4c HEAD -- caged.py` se limita a `baixar_url`, `baixar`, `baixar_layout` e `ler_uf` |
| `auditoria/rodada-2/defeitos_plantados.sh` | Funciona e confere com `CORRECOES.md`. Verifica se cada `sed` se aplicou (`cmp`), roda com `-I` e conta tracebacks. O comentário sobre N6 e N7 (`:4`) é coerente com a rodada 2 |
| `auditoria/rodada-2/CORRECOES.md` | Cada linha da tabela de evidência foi reproduzida (`:25-31` e `:37-42`). A linha de V7 (`:17`) diz "Um `.7z` corrompido gera mensagem com orientação, não traceback", o que é mais amplo que o testado (R2). O "Limite do teste de V7" (`:46`) está correto e foi confirmado por M2 |
| `auditoria/rodada-2/VERIFICACAO.md` | Idêntico ao parecer verificado (`diff` vazio) |
| `auditoria/rodada-2/briefing.txt` | Instrução com os caminhos trocados por marcadores. Nada sensível |
| `auditoria/README.md` | A linha da rodada 2 está correta. A rodada 3 aparece como pendente (R3) |
| `dados/oficial/FONTES.md`, `novo-caged-…csv` e `dados/saidas/conferencia_…csv` | Só o rótulo da linha 13 mudou, mais a explicação da nota de rodapé. Ver V2 e O1 |
| `execucoes/20261112T195851-conferir.json`, `…195852-agregar.json` e `…200037-extrair.json` | Commit `34ebdc3` sem `+alterado`. As versões batem com o venv. Os SHA-256 das saídas batem com os arquivos de HEAD (seção 2) |

## 7. Afirmações novas além da evidência

### R1. "Os cinco filtros do salário (… piso e teto)"

- `docs/PROTOCOLO.md:36`: "O teste cobre os cinco filtros do salário".
- `teste_sintetico.py:8-9`: "os cinco filtros do salário de admissão (unidade mensal, intermitente, aprendiz, piso e teto)".
- `README.md:7`: "filtros do salário". É menos específico, mas pelo contexto inclui os cinco.

Nenhuma linha sintética tem salário acima de R$ 50.000, então nenhuma verificação falha se o teto sumir (M1). Em Boa Vista, M1 muda `salario_medio_admissao` de Pedreiro (715210), de 2.535,81 para 2.964,55. `auditoria/rodada-2/CORRECOES.md:13` descreve as linhas acrescentadas sem dizer que o teto foi testado, o que é exato. Há duas correções possíveis. A primeira é acrescentar ao teste uma admissão acima de 50.000, por exemplo R$ 60.000 em 521110, que fica fora do salário. Isso muda o teste e pede nova verificação, mas é uma linha só e os valores esperados de salário não mudam. A segunda é restringir o texto, por exemplo: "o teto é testado só contra um corte baixo demais".

### R2 (menor). "`.7z` corrompido gera mensagem com orientação, não traceback"

- `auditoria/rodada-2/CORRECOES.md:17`: "Um `.7z` corrompido gera mensagem com orientação, não traceback."
- `teste_sintetico.py:11-12`: ".7z corrompido com mensagem de orientação".

O teste (`teste_sintetico.py:187-196`) e o tratamento (`caged.py:138`) cobrem o `.7z` **truncado**, que é o caso de V7: o cabeçalho do 7z fica no fim do arquivo, e py7zr levanta `Bad7zFile`. Gerei um `.7z` válido de 682.287 bytes no formato do PDET e inverti 64 bytes a um terço do arquivo, sem truncar. `ler_uf` terminou com a exceção não tratada `_lzma.LZMAError: Corrupt input data`. O efeito é pequeno: não sai resultado errado, só um traceback sem orientação. O README não faz essa afirmação. A correção mais simples é trocar "corrompido" por "truncado" nos dois textos. A alternativa é tratar também `lzma.LZMAError` e as exceções de CRC do py7zr, o que muda código.

### Observações sem efeito (não exigem correção)

- **O1.** `README.md:21` diz que, na p. 31, "o mês final aparece sem ajuste (nota de rodapé da página)". A nota diz só que o ajuste vale de 09/2025 a 08/2026. Que 09/2026 está sem ajuste é uma inferência por exclusão. Ela é coerente com o valor (1.068, igual ao da p. 43, "DADOS SEM AJUSTES") e com o método: o FOR de competências até 202609 não contém linhas de 202609. `dados/oficial/FONTES.md:10` formula isso com precisão ("por isso … está transcrito como 'sem ajuste'").
- **O2.** O histórico de `docs/PROTOCOLO.md:9` cita só a rodada 1 ("ver `auditoria/`"). Não é afirmação falsa, porque a tabela de rodadas está em `auditoria/README.md`.
- **O3.** `auditoria/rodada-1/CORRECOES.md:17-18` mantém "16 valores distintos" e o rótulo antigo. É o registro histórico da rodada 1, e `auditoria/README.md:11` diz que os textos das rodadas são os originais. A correção está em `auditoria/rodada-2/CORRECOES.md:11-12`. Se quiserem evitar que um leitor pare no texto antigo, basta uma nota de uma linha remetendo à rodada 2.
- **O4.** O cabeçalho gzip também guarda o nome do arquivo (campo FNAME, `uf14_202510_202609.csv`). O mesmo conteúdo gravado com outro nome dá outro SHA-256. Como o nome é fixado por `arq_linhas`, a afirmação de `README.md:51` vale para quem usa o script.

## 8. O que continua sustentado

- A afirmação de auditoria, agora com as rodadas 1 e 2 registradas.
- A conferência 18/18 com diferença zero, reexecutada, e o CSV oficial conferido com o PDF, cujo SHA-256 confere.
- A tabela de resultado (`README.md:27-33`), idêntica à saída reexecutada, e as saídas versionadas idênticas.
- A reprodutibilidade do `.csv.gz`, confirmada de novo regravando o conteúdo (`cf8457ce…`).
- O mecanismo `.parte`, confirmado por simulação de queda e de morte do processo.
- Todas as linhas das tabelas de evidência de `auditoria/rodada-2/CORRECOES.md`.

## 9. Correções sugeridas

| Prioridade | Item | Onde | Muda número/código? |
|---|---|---|---|
| Ressalva | R1: testar o teto com uma admissão acima de 50.000, ou restringir o texto | `teste_sintetico.py:8-9` e dados, `docs/PROTOCOLO.md:36` | Teste, se for pelo teste (pede nova verificação dirigida, curta). Nenhum número publicado muda |
| Ressalva | R3: registrar esta rodada | `auditoria/README.md:9`, `auditoria/rodada-3/` | Não |
| Menor | R2: "corrompido" → "truncado", ou tratar `LZMAError`/CRC | `teste_sintetico.py:11`, `auditoria/rodada-2/CORRECOES.md:17` (ou `caged.py:138`) | Só texto, se for pelo texto |
| Opcional | O2 e O3: histórico do protocolo e nota em `rodada-1/CORRECOES.md` | `docs/PROTOCOLO.md:9`, `auditoria/rodada-1/CORRECOES.md` | Não |

Se R1 e R2 forem corrigidos só no texto, e R3 for feito, o pacote fica sem ressalva conhecida. Se R1 for corrigido por teste, a mudança precisa passar por uma verificação curta: rodar `teste_sintetico.py` e o mutante M1.

## 10. Evidência guardada nesta verificação

Fica fora do repositório auditado, na pasta temporária da sessão (`<pasta temporária da sessão do auditor>`):

- `scripts/mutantes3.sh` (M1 a M5), `scripts/interrompido.py` (queda de conexão), `scripts/morto.py` (processo morto no meio do download) e `scripts/corrompido.py` (`.7z` com bytes corrompidos);
- `mut/M1…M5/` (`caged.py`, `diff.txt`, `sint.log`) e `clone_m1/`, onde está o efeito de M1 nas saídas reais;
- `logs/sint.log`, `logs/defeitos_r2.log`, `logs/real.log`, `logs/mutantes3.log`, `logs/interrompido.log`, `logs/morto.log`, `logs/corrompido.log` e `logs/varredura.txt`;
- `pdfs/apresentacao.pdf` e `pdfs/p31.txt`, e `regrava/uf14_202510_202609.csv.gz` (o teste de V6).
