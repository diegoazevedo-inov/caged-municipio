# Verificação dirigida (rodada 2): `caged-municipio`

- **Objeto:** `<repositório>`, ramo `main`, HEAD `0f42f4c` (4 commits). O parecer verificado é o da rodada 1, sobre `e5ee630` (`PARECER-a-verificar.md`, idêntico a `auditoria/rodada-1/PARECER.md` no repositório; `diff` vazio).
- **Data:** 12/11/2026.
- **Modo:** verificação dirigida, em sessão nova. Trabalhei num clone em pasta temporária (`clone`) e numa cópia dele (`clone2`). O original foi só lido: `git status`, `git log`, `git fsck`, `git count-objects`, `reflog` e uma cópia do `dados/linhas/uf14_202510_202609.csv.gz`, que é ignorado pelo git. Não houve escrita no original, repositório remoto, push, modelo real nem API paga.
- **Ambiente:** Python 3.14.4 e venv com `requirements.txt` (pandas 3.1.1, py7zr 1.1.4, openpyxl 3.1.5), zlib 1.3.1, curl e pdftotext. Rede: FTP do PDET/MTE e gov.br, ambos públicos.
- **Restrição de escopo:** no original, `dados/brutos` é um link simbólico para a pasta de outro projeto do usuário. Ele fica fora do escopo autorizado e não foi lido. Os brutos foram baixados de novo da fonte pública, dentro do clone. O link não é versionado (`.gitignore`, `git status --ignored`), então não chega ao público.

## Veredito final: **pode ir a público com ressalvas**

O bloqueio da rodada 1 (G5-1) está resolvido. A afirmação de auditoria agora remete a `auditoria/`, onde a rodada 1 está registrada com o veredito "não pode" e a rodada 2 aparece como pendente. O núcleo técnico continua de pé. A reextração completa, com os 37 arquivos baixados de novo do PDET, deu o mesmo SHA-256 das linhas registrado no repositório (`cf8457ce…`) e manifesto idêntico. A conferência dá 18/18, as saídas versionadas saem idênticas, o teste sintético passa e os 7 defeitos de `defeitos_plantados.sh` são pegos, como `CORRECOES.md` diz.

Nenhum achado abaixo impede a publicação sozinho. As ressalvas são:

1. **V1.** Conta errada introduzida pela correção de G5-2. O README diz "16 valores distintos", mas são 17 (`README.md:21`).
2. **V2.** A correção de G5-3 trocou um rótulo que a fonte sustentava por outro que a nota de rodapé da p. 31 não sustenta. O achado G5-3 da rodada 1 estava errado. O efeito numérico é nulo.
3. **V3.** O texto novo diz que "o salário" e "os indicadores por ocupação" são verificados pelo teste sintético. Três dos cinco filtros salariais e a série "sem ajuste" não são: os defeitos N1, N3, N4 e N5 passam pela suíte inteira e mudam colunas publicadas.
4. **V4.** "Pipeline completo" vai além do que o teste sintético cobre.
5. **V5.** `auditoria/README.md` precisa registrar esta verificação antes da publicação, porque a linha da rodada 2 diz "pendente".
6. **V6 e V7 (menores).** SHA-256 do `.csv.gz` dependente da zlib, e download interrompido que deixa um `.7z` truncado e trava o `extrair` seguinte.

Correções sugeridas no fim. Se alguma delas mudar código ou número (por exemplo, testes novos para V3), ela passa por nova verificação. Ajustes só de texto em V1, V2, V4 e V5 não mudam número.

| Item | Veredito |
|---|---|
| Achados da rodada 1 (19) | 15 resolvidos (incluindo o bloqueio G5-1), 3 resolvidos em parte (G4-3, G5-2, G5-5) e 1 não resolvido porque a premissa do achado estava errada (G5-3). Ver tabela |
| Suíte de testes e verificação | Passa |
| Histórico | Passa |
| Varredura de dados | Passa |
| Arquivos novos | Passam, com as ressalvas V1, V3 e V4 |
| Afirmações novas | V1 a V4, V6 |
| Reprodução a partir da fonte | Passa (V7 é de robustez) |

---

## 1. Achado por achado

Os números de linha são do commit `0f42f4c`.

| Achado | Situação | Evidência |
|---|---|---|
| **G5-1** (bloqueio): auditoria declarada como feita | **Resolvido** | `README.md:9` ("auditoria independente em sessões separadas, com briefing, parecer e correções em `auditoria/`"), `README.md:57`, `docs/PROTOCOLO.md:9` e `:43`, `CITATION.cff:4` ("auditoria independente documentada"). `auditoria/README.md:7` registra a rodada 1 com "não pode: 1 bloqueio (G5-1) e 18 ressalvas", e `:8` a rodada 2 como "pendente". A pasta contém `briefing.txt`, `PARECER.md` (idêntico ao parecer verificado) e `CORRECOES.md`. Nenhum texto afirma mais que isso. Ver V5 |
| G4-1: desligamento a pedido sem teste | **Resolvido** | `teste_sintetico.py:56,66` (dois tipos 40) e `:78-83` (esperado). O defeito D1 (`A_PEDIDO = 41`) é pego, com falha em "série 202601; série 202602; ocupação 521110". A ausência de fonte oficial está declarada em `README.md:15` e `docs/PROTOCOLO.md:36` |
| G4-2: recorte municipal sem teste | **Resolvido** | `teste_sintetico.py:60` (município 140015, mesmo prefixo de 5 dígitos) e `:61` (UF 13). D3 (filtro por prefixo) é pego, com falha em "série 202601; ocupação 521110" |
| G4-3: tabela por ocupação sem teste; corte de 30 sem objeto | **Resolvido em parte** | O título (D5), o teto de 50.000 (D2), a exclusão do aprendiz (`teste_sintetico.py:62`) e `pct_a_pedido` são testados. O corte de leitura virou uma regra declarada para textos derivados (`docs/PROTOCOLO.md:29`). **Falta:** os filtros de unidade salarial 5, de intermitente e o piso de R$ 200 não são exercitados, porque todas as linhas sintéticas têm unidade `"5"`, intermitente `"0"` e salário ≥ 700 (`teste_sintetico.py:48-49`). Os defeitos N3, N4 e N5 passam pela suíte inteira e mudam colunas salariais publicadas (seção 3). Ver V3 |
| G4-4: o teste existente não exercita `extrair` | **Resolvido** | `teste_sintetico.py:117-125` chama `caged.extrair`. D6 (sinal do EXC) agora é pego sem precisar baixar nada. O alcance está no docstring (`teste_conferencia.py:6-7`). O download (`baixar`) continua fora de qualquer teste, o que é razoável para um teste offline |
| G4-5: SHA-256 do `.csv.gz` não reprodutível | **Resolvido** | `caged.py:52` (`GZIP = {"method": "gzip", "mtime": 0}`) e `:197`. O cabeçalho do `.csv.gz` do original tem os bytes 4 a 7 iguais a `0 0 0 0` (`od`). O SHA-256 do conteúdo descompactado é `378236b9…`, igual ao da rodada 1. O teste sintético compara duas extrações separadas por mais de 1 s (`:121-125`), e D7 é pego. A reextração com brutos baixados de novo deu `cf8457ce…`, o mesmo SHA-256 registrado em `execucoes/20261112T182954-extrair.json` (seção 2.2). Ver também a nota de zlib em V6 |
| G4-6: recorte inexistente sai com 0 | **Resolvido** | `caged.py:156-157`. `agregar --recorte mun:149999` dá "recorte mun:149999 sem nenhuma linha…" e sai com 1. Também é coberto pelo teste (`teste_sintetico.py:147-152`) |
| G4-7: brutos sem conferência contra o manifesto | **Resolvido** (declarado com precisão) | `caged.py:200` e `:206-214`, `README.md:48` e `:51`. Teste manual: alterei o SHA-256 de `CAGEDFOR202602.7z` no manifesto sintético e rodei `extrair` de novo. A saída foi "ATENÇÃO: CAGEDFOR202602.7z difere do manifesto anterior", e o registro gravou `difere_do_manifesto_anterior: ['CAGEDFOR202602.7z']`. O comando continua saindo com 0, e o README diz "avisa", o que é exato. Nenhum teste automático cobre o aviso: o defeito N8 (`difere = []`) passa pelo teste sintético |
| G5-2: 18 transcrições ≠ 18 verificações | **Resolvido em parte** | A dependência está declarada (`README.md:21`), mas a conta está errada. Ver V1 |
| G5-3: rótulo do saldo de 09/2026 na p. 31 | **Não resolvido: o achado estava errado e a correção piorou a precisão** | Ver V2. Efeito numérico nulo: a conferência dá 18/18 com o rótulo novo (reexecutada) e dava 18/18 com o antigo |
| G5-4: "número a número" além do conferido | **Resolvido** | `README.md:6` ("conferência dos números da UF"), `README.md:15`, `CITATION.cff:4` e `docs/PROTOCOLO.md:36` |
| G5-5: "fixado antes" sem prova | **Resolvido em parte** | `README.md:23` e `docs/PROTOCOLO.md:8` trazem a ressalva ("declaração do autor; o histórico do git não prova a ordem"). Mas `docs/PROTOCOLO.md:35` continua com "**Critério, fixado antes da execução:**", sem a ressalva. A ressalva está três linhas acima, na mesma página, então o defeito é pequeno |
| G5-6: openpyxl fora do registro | **Resolvido** | `caged.py:32` e `:99`. `execucoes/20261112T182954-extrair.json` traz `"openpyxl": "3.1.5"`, e os registros desta verificação também |
| G5-7: `inicio` com o horário do fim | **Resolvido** | `caged.py:53` (`INICIO` na importação do módulo) e `:97`. O registro `20261112T182954-extrair.json` tem `inicio` 18:28:55 e `fim` 18:29:54. Na linha de comando, a importação coincide com o começo do processo |
| G5-8: CBOs sem título | **Resolvido** | `README.md:64` lista 142140, 142360, 322140, 322715, 423115, 514335, 519325 e 519330. Conferido na tabela: são exatamente os 8 códigos com `titulo` vazio, nas linhas 210, 258, 353, 421, 457, 458, 512 e 757 |
| G5-9: título promete rotatividade | **Resolvido** | `README.md:1` e `:3`, `CITATION.cff:3-4` e `:14`. `README.md:62` explica por que não há taxa de rotatividade e diz que `pct_a_pedido` é o único percentual. Não sobra "rotatividade" fora da auditoria e dessa limitação (`grep`) |
| G7-1: "Histórico honesto" | **Resolvido** | `docs/PROTOCOLO.md:3`: "## Histórico" |
| G7-2: bastidor no histórico | **Resolvido** | `docs/PROTOCOLO.md:7`: "Análise exploratória de Boa Vista/RR com as mesmas fontes, não pré-registrada." Não cita mais script não publicado nem ranking |
| G7-3: "O que este pacote garante" | **Resolvido** | A frase foi removida. `grep -i garant` não acha nada fora da auditoria |

## 2. Suíte de testes e de verificação

### 2.1 Comandos

Feitos em `clone2`, com o `.csv.gz` copiado do original. O SHA-256 da cópia é `cf8457ce…`, o mesmo das entradas de `execucoes/20261112T183003-conferir.json` e `…T183004-agregar.json`.

| Comando | Resultado |
|---|---|
| `teste_sintetico.py` | `TESTE PASSA: 0 falha(s)`, saída 0, cerca de 3 s, sem download |
| `PYTHON=.venv/bin/python bash auditoria/rodada-1/defeitos_plantados.sh` | D0 sai com 0, D1 a D7 saem com 1, sem traceback. As verificações que falham são **idênticas** às da tabela de `CORRECOES.md:41-51`. Saída final: `DEFEITOS: todos pegos pelo teste, sem exceção` |
| `caged.py conferir …` | `PASSA: 18 de 18`, saída 0 |
| `caged.py agregar --recorte mun:140010 …` | `{admissoes: 49067, desligamentos: 45836, saldo: 3231, deslig_a_pedido: 16894, ocupacoes: 935}`, saída 0 |
| `caged.py agregar --recorte mun:149999 …` | erro com mensagem, saída 1 |
| `caged.py agregar --recorte mun:130260 …` | "faltam as linhas: rode extrair --uf 13 …", saída 1 |
| `teste_conferencia.py` | `real -> saída 0 \| defeito -> saída 1`, `TESTE PASSA` |
| `git diff --stat dados/saidas/` | **vazio**. O layout baixado tem SHA-256 `0490f7ef…`, igual ao manifesto |

### 2.2 Reextração completa a partir da fonte pública

Feita em `clone`, sem nada em cache, com o código de HEAD (`0f42f4c`):

- **1ª tentativa:** 33 arquivos baixados em 59 min 28 s. No 34º, `CAGEDMOV202609.7z`, o curl falhou com `(56) Recv failure: Tempo esgotado para conexão`, e o processo saiu com 1. Ficou em `dados/brutos/` um arquivo truncado de 38.862.848 bytes, contra 49.478.375 no manifesto.
- **2ª tentativa, com o truncado no lugar:** `baixar()` (`caged.py:109-115`) aceita qualquer arquivo não vazio, então não baixa de novo. O `extrair` para com `py7zr.exceptions.Bad7zFile: next header size 114 exceeds the archive size`. Não sai resultado errado, mas o usuário recebe um traceback sem orientação (V7).
- **3ª tentativa, depois de apagar o truncado:** baixou o arquivo que faltava e rodou em 4 min 3 s, saída 0. Brutos: 37 arquivos, 643.625.674 bytes (613,8 MiB; o README diz "cerca de 620 MB"). Registro `execucoes/20261112T195536-extrair.json`: commit `0f42f4c`, `linhas: 105024`, `difere_do_manifesto_anterior: []`.
- **Linhas extraídas:** SHA-256 `cf8457ce9821e838…`, **igual** ao registrado pelo autor (`20261112T182954-extrair.json`) e ao `.csv.gz` do original. O conteúdo descompactado dá `378236b9…`, o mesmo valor da rodada 1. Isso confirma G4-5 com dados reais, em duas execuções separadas por cerca de 1 h 25 min.
- **`git diff --stat dados/saidas/` depois de `extrair`, `conferir` e `agregar`:** vazio. O manifesto (SHA-256 e tamanho dos 37 arquivos) é idêntico ao versionado, então o PDET não republicou nenhum arquivo.
- Com essas linhas, `conferir` sai com 0 (18/18), `agregar mun:140010` dá os mesmos totais e `teste_conferencia.py` passa.

### 2.3 Fonte oficial

Baixei `apresentacao-setembro-de-2026.pdf` do endereço em `dados/oficial/FONTES.md`. O SHA-256 é `063267f6…`, como registrado. Os 18 valores de `dados/oficial/novo-caged-2026-09-uf14.csv` conferem com o texto das p. 31, 34 e 43 (`pdftotext -layout`).

## 3. Defeitos novos plantados (diferentes de D1 a D7)

Cada defeito foi aplicado por `sed` numa cópia de `caged.py`. O efeito nas saídas reais foi medido rodando `agregar mun:140010` da cópia sobre as linhas reais e comparando as colunas numéricas com as tabelas versionadas. A cópia sem defeito reproduz as tabelas versionadas sem nenhuma diferença.

| # | Defeito em `caged.py` | `teste_sintetico.py` | `conferir` (dados reais) | Efeito nas saídas publicadas de Boa Vista |
|---|---|---|---|---|
| N1 | "sem ajuste" passa a usar todas as linhas, não só MOV (`:170`) | **não pega** | **não pega** (18/18) | colunas `*_sem_ajuste` da série mudam: admissões em 11 meses, desligamentos em 11, saldo em 10 |
| N2 | série "com ajuste" passa a usar só MOV (`:172`) | pega (ocupações 521110 e 411005) | — | — |
| N3 | sem o filtro de intermitente (`:234`) | **não pega** | não se aplica | mediana muda em 2 ocupações e média em 9 |
| N4 | sem o filtro de unidade salarial 5 (`:234`) | **não pega** | não se aplica | mediana muda em 44 ocupações e média em 81 |
| N5 | piso salarial de 200 para 0 (`:235`) | **não pega** | não se aplica | mediana muda em 19 ocupações e média em 53 |
| N6 | tipo 70 fora de `ADMISSAO` (`:45`) | não pega | não pega | nenhum: o tipo 70 não ocorre na UF 14 na janela |
| N7 | tipo 99 dentro de `DESLIGAMENTO` (`:46`) | não pega | não pega | nenhum: o tipo 99 não ocorre na UF 14 na janela |
| N8 | `comparar_manifesto` nunca acusa diferença (`:211`) | **não pega** | não se aplica | nenhum nas tabelas. Some o aviso de G4-7 |

Leitura dos resultados:
- N6 e N7 são equivalentes nestes dados. Os tipos presentes na UF 14 são 31, 32, 33, 35, 40, 43, 50, 60, 90, 97 e 98, então esses defeitos não são lacunas com consequência.
- N1 escapa das duas réguas. No teste sintético, a admissão fora do prazo (r13, +1) e a exclusão (r14, −1) se anulam na competência 202601, e as colunas com e sem ajuste ficam iguais (`teste_sintetico.py:78`: `(4, 3, 1, 1, 4, 3, 1)`). Na conferência, o único número "sem ajuste" é o do mês final (p. 43), em que com e sem ajuste coincidem. Em Boa Vista, 202609 dá 4654/3642/1012 nas duas versões. O caminho "sem ajuste" (`caged.py:9` e `:169-170`) não tem verificação que o distinga do "com ajuste".
- N3, N4 e N5 mudam colunas publicadas e passam pela suíte inteira (V3).

## 4. Histórico

- `git log --all`: 4 commits (`9321b30`, `e5ee630`, `4c82547`, `0f42f4c`) e um só ramo (`main`), sem tags, stash nem remoto.
- Nenhum arquivo de `9321b30` ou de `e5ee630` foi removido depois: todos continuam em HEAD.
- No original, `git fsck --unreachable --no-reflogs --full` não deu saída. `git count-objects -v` mostra 61 objetos soltos e 0 em pack, e `git rev-list --objects --all | wc -l` dá 61: todos são alcançáveis. O reflog tem só os 4 commits.
- Autor e committer de todos os commits: `Diego <diego@example.com>`. As mensagens têm `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, coerente com o uso de IA declarado. A mensagem de `4c82547` resume as correções em termos técnicos, sem eco de conversa.
- Os registros novos (`execucoes/20261112T182954-extrair.json`, `…183003-conferir.json`, `…183004-agregar.json`) gravam o commit `4c82547` sem `+alterado`, e os SHA-256 das saídas batem com os arquivos de HEAD.
- Todos os arquivos versionados têm modo 100644. `defeitos_plantados.sh` é chamado com `bash`, como o README e o próprio script indicam.

## 5. Varredura de dados

Fiz `git grep -i` em todos os commits (`git rev-list --all`), exceto `LICENSE`, procurando `/home`, `/tmp`, `/Users`, `C:\`, `diego`, `gmail`, e-mails, `token`, `senha`, `password`, `secret`, `api_key`, `chave`, `bearer`, chaves privadas, `ghp_`, `sk-`, `cliente`, `clínica`/`clinica`, `paciente`, o nome da pasta de outro projeto para onde aponta o link de `dados/brutos`, `scratchpad` e nomes de provedores. Ocorrências:
- `auditoria/rodada-1/briefing.txt:7`: a palavra "cliente, clínica, paciente" no texto do critério do gate 2.
- `auditoria/rodada-1/PARECER.md:155-158`: `…/scratchpad/…`, com o prefixo trocado por `<pasta temporária da sessão do auditor>` (`:160`), sem caminho absoluto.
- `auditoria/rodada-1/PARECER.md:32` e `:39`: citações do e-mail de exemplo e da varredura anterior.
- `dados/saidas/ocupacoes_…csv`: títulos oficiais da CBO ("Clinica[s]", "Secretari…", "Chaveiro", "Gerente de Clientes Especiais"). São nomenclatura pública.
- `docs/PROTOCOLO.md:41`: "Claude, Anthropic", a declaração de método.

Nenhum segredo, caminho pessoal, nome de cliente, clínica ou paciente. O nome e o ORCID em `CITATION.cff:7-9` são a autoria declarada. A troca de caminhos absolutos por marcadores, anunciada em `auditoria/README.md:10`, está feita: não há `/home` nem `/tmp` em nenhum arquivo versionado.

## 6. Arquivos novos desde o parecer

| Arquivo | Situação |
|---|---|
| `teste_sintetico.py` | Os valores esperados conferem com o cálculo à mão a partir do docstring. Refiz série e ocupações linha a linha. Isola `RAIZ`, `BRUTOS`, `LINHAS`, `SAIDAS` e `EXECUCOES` numa pasta temporária e não suja o repositório (`git status` limpo depois da execução). Lacunas: V3 (N1, N3, N4, N5) e V4. Observação de método, sem defeito: a admissão r1, excluída por r14, continua no cálculo do salário (`:82`, "sal: r1 r2 r10"), porque o salário usa só linhas com sinal +1. É coerente com a definição do protocolo ("Só admissões declaradas (MOV e FOR)", `docs/PROTOCOLO.md:28`) |
| `auditoria/rodada-1/defeitos_plantados.sh` | Funciona e confere com `CORRECOES.md`. Verifica se o `sed` se aplicou (`:23`) e conta tracebacks |
| `auditoria/rodada-1/CORRECOES.md` | A tabela de evidência foi reproduzida. Descreve G4-3 com precisão ("valor entre 5.000 e 50.000 e aprendiz excluído"), mais estreito que o README e o protocolo (V3). A linha de G5-3 herda o erro da rodada 1 (V2) e a de G5-2 herda a conta errada (V1) |
| `auditoria/rodada-1/PARECER.md` | Idêntico ao parecer verificado (`diff` vazio) |
| `auditoria/rodada-1/briefing.txt` | Texto de instrução com caminhos trocados por marcadores. Nada sensível |
| `auditoria/README.md` | Correto quanto à rodada 1 ("18 ressalvas" confere: 7 em G4, 8 em G5 e 3 em G7). `:3` anuncia que "a verificação dirigida" fica ali, e `:8` a dá como pendente (V5) |
| `execucoes/20261112T18*.json` | Ver seção 4 |

## 7. Afirmações novas além da evidência

### V1. Contagem de valores distintos (`README.md:21`)

O texto diz: "Restam 16 valores distintos, 15 deles independentes." O CSV oficial tem 18 linhas e **17** valores numericamente distintos (`pandas.nunique` = 17). Só o 1.068 se repete, nas linhas 13 e 19. Tirando o acumulado de 2026 (3.814 = soma dos saldos mensais de 202601 a 202609, o que conferi), sobram 16 valores. O número veio da rodada 1, que errou a conta. A correção copiou o erro. Ele subestima o alcance, mas é um número público errado. Sugestão: "17 valores distintos; 16 descontando o acumulado de 2026, que é a soma dos saldos mensais". Ou então só descrever as dependências, sem contagem: o saldo também é admissões menos desligamentos nas p. 34 e 43, o que reduz ainda mais a contagem, conforme o critério.

### V2. Rótulo de 09/2026 na p. 31 (`dados/oficial/novo-caged-2026-09-uf14.csv:13`)

A p. 31 da apresentação tem a nota "*De setembro de 2025 a agosto de 2026, consideram-se ajustes declarados até o mês de setembro de 2026." (`pdftotext`). A coluna 2026/09 fica fora do período ajustado. O rótulo original, "sem ajuste", estava de acordo com a fonte. O achado G5-3 da rodada 1 leu só o título "(DADOS COM AJUSTES)" e estava errado. A correção trocou o rótulo para "ajustes declarados até 202609", e a mudança se propagou para `dados/saidas/conferencia_…csv:13` e para `CORRECOES.md:18`. Pelo método do script os dois valores coincidem no mês final (1.068), então nenhum número muda. Sugestão: voltar para "sem ajuste", ou manter e explicar a nota de rodapé. Isso também deixa a linha 13 claramente igual à linha 19 (p. 43), como V1 já supõe.

### V3. "O salário" e "os indicadores por ocupação" verificados pelo teste sintético

- `README.md:15`: "O recorte e os indicadores por ocupação são verificados por `teste_sintetico.py`."
- `README.md:7`: "(recorte municipal, a pedido, salário, título da CBO)".
- `docs/PROTOCOLO.md:36`: "O recorte municipal, o desligamento a pedido, o salário e o título da CBO … são verificados por `teste_sintetico.py`".
- `teste_sintetico.py:7-9`: "Cobre … salário de admissão".

Dos cinco critérios do salário (`docs/PROTOCOLO.md:28`, `caged.py:234-235`), o teste exercita dois: o teto e o aprendiz. Unidade 5, intermitente e piso de R$ 200 não têm linha sintética que os distinga. N3, N4 e N5 passam pela suíte e mudam a mediana de 2 a 44 ocupações e a média de 9 a 81. A série sem ajuste (N1) também passa. Sugestão: acrescentar ao teste uma admissão intermitente, uma com unidade diferente de 5, uma abaixo de R$ 200 e um FOR sem EXC correspondente (ou um EXC sem FOR) numa competência, para separar com e sem ajuste. A alternativa é restringir o texto ao que é testado, como `CORRECOES.md:12` já faz. Teste novo muda código e pede nova verificação.

### V4. "Pipeline completo"

`README.md:7` e `docs/PROTOCOLO.md:36` falam em "teste do pipeline completo". O teste cobre `extrair → agregar` (`teste_sintetico.py:2` diz isso com precisão). O download (`baixar`) e o `conferir` ficam de fora. O `conferir` é coberto à parte por `teste_conferencia.py`. Sugestão: "pipeline de extração e agregação".

### V5. Estado da auditoria em `auditoria/README.md`

`:3` diz que a pasta guarda "a verificação dirigida", e `:8` a dá como "pendente". Não é uma afirmação falsa hoje, mas publicar nesse estado deixa a rodada 2 sem registro. Sugestão: registrar esta verificação em `auditoria/rodada-2/` e atualizar a linha 8 com o resultado, como foi feito com a rodada 1.

### V6 (menor). SHA-256 do `.csv.gz` entre plataformas

`README.md:51` diz: "o mesmo conteúdo dá o mesmo SHA-256". Com `mtime` 0 isso vale para a mesma implementação de deflate. Outra zlib, como a zlib-ng usada em algumas distribuições do Python, pode comprimir o mesmo conteúdo em bytes diferentes. Verifiquei só nesta máquina (zlib 1.3.1). Sugestão: "na mesma versão da zlib", ou registrar também o SHA-256 do CSV descompactado.

### V7 (menor, robustez). Download interrompido

Ver seção 2.2. `baixar()` e `baixar_layout()` (`caged.py:109-123`) gravam direto no destino e só testam se o arquivo existe e não está vazio. Uma queda de rede deixa um `.7z` truncado, e o `extrair` seguinte para com `Bad7zFile` até alguém apagar o arquivo. Não é uma afirmação falsa: o README não promete retomada. Mas o download de cerca de 1 h torna a queda provável, e eu passei por isso nesta verificação. O aviso de manifesto de G4-7 não ajuda aqui, porque a leitura do `.7z` falha antes da comparação.

## 8. O que continua sustentado

- A afirmação de auditoria, agora com o estado de cada rodada registrado.
- Reprodução completa a partir da fonte pública: mesmo SHA-256 das linhas e o mesmo manifesto.
- Conferência 18/18 com diferença zero, reexecutada. Os valores do CSV oficial conferem com o PDF, cujo SHA-256 também confere.
- A tabela de resultado (`README.md:27-33`) é idêntica à saída reexecutada.
- Os 8 CBOs sem título, o alcance da conferência (UF), a limitação sobre rotatividade e "Só a versão 3.14.4 do Python foi testada" (`README.md:39`).
- `CORRECOES.md:27-51`: cada linha da tabela de evidência foi reproduzida.

## 9. Correções sugeridas

| Prioridade | Item | Onde | Muda número/código? |
|---|---|---|---|
| Ressalva | V3: testar unidade, intermitente, piso e "sem ajuste", ou restringir o texto | `teste_sintetico.py`, `README.md:7,15`, `docs/PROTOCOLO.md:36` | sim, se for por teste (pede nova verificação) |
| Ressalva | V1: 17 distintos / 16 | `README.md:21`, `CORRECOES.md:17` | só texto |
| Ressalva | V2: rótulo de 09/2026 na p. 31 | `dados/oficial/novo-caged-2026-09-uf14.csv:13`, `dados/saidas/conferencia_…csv:13` (regerar) | rótulo, sem efeito no valor |
| Ressalva | V5: registrar a rodada 2 | `auditoria/README.md:3,8` | não |
| Menor | V4: "pipeline completo" | `README.md:7`, `docs/PROTOCOLO.md:36` | não |
| Menor | G5-5 residual | `docs/PROTOCOLO.md:35` | não |
| Menor | V6: zlib | `README.md:51` | não |
| Menor | V7: download interrompido deixa `.7z` truncado. Baixar para arquivo temporário e renomear só com sucesso, ou dizer no README que é preciso apagar o arquivo | `caged.py:109-123`, `README.md:44` | sim, se for no código |
| Menor | aviso de manifesto sem teste automático (N8) | `teste_sintetico.py` | sim, se for por teste |

## 10. Evidência guardada nesta verificação

Fica fora do repositório auditado, na pasta temporária da sessão (`<pasta temporária da sessão do auditor>`):
- `scripts/mutantes.sh` (N1 a N8), `scripts/efeito.py`, `scripts/efeito_agregar.py` e `scripts/manifesto.py`;
- `mut/N1…N8/` (`caged.py`, `diff.txt`, `sint.log`) e `mut/conf_*/conf.log`;
- `logs/clone2_comandos.log`, `logs/extrair.log` (1ª tentativa), `logs/extrair_parcial.log` (2ª) e `logs/extrair2.log` (3ª);
- `parcial_CAGEDMOV202609.7z` (o arquivo truncado) e `clone/execucoes/20261112T195536-extrair.json`;
- `pdfs/apresentacao.pdf` e `pdfs/p31.txt`.
