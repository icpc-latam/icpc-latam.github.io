# CLAUDE.md — icpclatam.org

Instruções para o Claude Code nesta pasta. Leia também `README.md` (visão geral, pendências, histórico).

## O que é este projeto
Site estático do **ICPC Latin America** (www.icpclatam.org), reconstruído depois que o Google Sites original foi perdido.
A pasta inteira é o site e é um repositório git: **https://github.com/icpc-latam/icpc-latam.github.io** (público; branch `main`),
publicado pelo GitHub Pages (fonte: `main`, raiz) em **https://icpc-latam.github.io/**. Fluxo: editar `tools/build.py` → `python3 tools/build.py` →
`python3 tools/check_links.py` → `git add -A && git commit && git push`; o Pages republica sozinho em ~1 min. Os `index.html` gerados são versionados
(o Pages serve direto da branch, sem build). `.nojekyll` desliga o Jekyll. Domínio próprio: **www.icpclatam.org** (arquivo `CNAME` na raiz + `cname` no Pages; DNS na Cloudflare, registro `www` → `icpc-latam.github.io`, com proxy ligado).
O apex icpclatam.org redireciona para o www. Com o proxy da Cloudflare o GitHub não emite certificado próprio (`is_https_eligible: false`, `https_enforced` fica false):
o HTTPS do visitante vem da Cloudflare — para forçar HTTPS use "Always Use HTTPS" lá (ou deixe o registro só-DNS até o GitHub emitir o certificado e então ative "Enforce HTTPS").

- **Idioma**: converse com o usuário em **português**; o **conteúdo do site é em inglês** (alguns textos de fontes ficam em espanhol/português, como nomes de times).
- **Vocabulário**: LAC = Latin American Championship = **PdA** (Programadores de América) · LAR = Latin American Regionals = **LATAM** no ScoreLatam ·
  CCL = "café com leite", times fora de competição.
- Regras de conteúdo: **nunca invente** datas, resultados, times ou links. O que não se sabe fica como `TBA…`/`TBD…` (classe CSS `tba`).
  Fatos novos vêm do usuário ou de fontes oficiais (ScoreLatam, Maratona SBC, regras em PDF). Cite a fonte quando derivar números.
- Não publicar como Artifact: representa uma organização real; entregue arquivos.

## Layout
```
tools/build.py          gerador (TODO o conteúdo e layout) → escreve index.html de cada página, sitemap.xml, robots.txt, 404.html
tools/fetch_results.py  baixa placares+fotos do ScoreLatam → tools/results.json e assets/img/teams/<edicao>/<time>.webp
tools/results.json      dados dos placares (gerado; lido pelo build.py)
tools/check_links.py    verifica links/arquivos locais e restos de web.archive.org / lh3.googleusercontent
assets/css/style.css    estilos (tokens em :root; amarelo #FEC009, hero #63501a, fonte Lato)
assets/docs/            PDFs (regras, info sheets, estatísticas…)
assets/img/             logo.png (mapa), pda2024-champions.jpg, flags/ (flagcdn 80px), teams/ (fotos), sponsors/ (opcional, vazio)
<secao>/<pagina>/index.html   páginas GERADAS (regionals/lar2026, championships/lac2027, masters/masters2024, home/, training/, history/, contact/ …)
```
**Nunca edite os `index.html` gerados** — são sobrescritos. Edite `tools/build.py`/`style.css` e rode o build.

## Comandos
```bash
python3 tools/fetch_results.py   # só quando houver placar novo (usa rede; precisa de Pillow)
python3 tools/build.py           # sempre após editar build.py / results.json
python3 tools/check_links.py     # deve dar "problems: 0"
python3 -m http.server 8765      # preview; encerre depois (guarde o PID com `echo $!`; NÃO use pkill -f / pgrep -f, casam com o próprio shell)
# screenshot (Firefox existe; não há Chromium):
firefox --headless --no-remote --profile "$(mktemp -d)" --screenshot out.png --window-size=1280,2600 http://localhost:8765/
```
Sempre confira visualmente páginas alteradas (largura 1280 e ~390 para celular) e rode `check_links.py` antes de dizer que terminou.

## Como o `build.py` é organizado
- Dados no topo: `BANNER`, `NAV`, `SOCIAL`, `CC` (país→código de bandeira), listas de países, `RESULTS` (de `results.json`), `SITE_URL`.
- Helpers: `rel(page, "path")` (links relativos por profundidade — o site funciona em qualquer subpasta), `asset()`, `ext()` (link externo),
  `flag()/flag_cc()`, `pdf()`, `yt()` (embed youtube-nocookie), `band()`/`wrap()`/`anchors()`/`facts()`/`intro()`, `event_card()`,
  `results_table()`, `region_table()`, `winner_block()`, `thumb()`/`team_photo()`, `report()`, `stream_block()`, `systems_block(page, moj_text, ram, keyboard)`
  (card do MOJ + Maratona Linux + convite para testar a imagem; usado em LAR2026 e LAC2027, ambos com o card do MOJ e o texto "Judging is centralized through MOJ" — confirmado pelo usuário que o LAC 2027 também é julgado pelo MOJ).
- Uma função por página (`page_home`, `page_lar2026`, `page_lac2027`, …), todas listadas em `build_pages()`; `render()` monta o HTML.
  A home é gerada duas vezes: `/` e `/home/` (o Google Sites antigo servia nos dois).
- **Nova edição/página — checklist**: (1) função `page_x()` + `build_pages()`; (2) `NAV` (submenu); (3) lista de edições em
  `page_regionals`/`page_championships`/`page_masters` (+ numeração "Edition #N"); (4) cards de eventos e notícias em `page_home()`;
  (5) `BANNER`; (6) se tiver placar: `EDITIONS` em `fetch_results.py` → rodar fetch → `results_table()/winner_block()`; (7) build + check_links.
  O sitemap é automático.
- Datas das listas de "Editions" incluem a chegada dos líderes (ex.: LAC2024 lista 13–18/mar, a página diz 14–18) — é o padrão original, não é erro.

## Fontes de dados e armadilhas
**ScoreLatam** (https://scorelatam.naquadah.com.br/): `pda24|pda25|pda26` = LAC; `latam-2024|latam-2025` = LAR. Em `fetch_results.py`:
- cada time aparece várias vezes (um `<tr class="sitegroupN">` por filtro); `group 1` = ranking geral; grupo de CCL é ignorado;
- o regex da linha precisa aceitar atributos extras (`<tr class="sitegroup1" color=yellow>` — a linha do 2º colocado do LAC2024 tinha isso);
- o nome do time pode vir com `</br>` malformado; o `id` do time tinha espaço no fim (`.strip()`);
- emblemas: 🥇🥈🥉 medalhas, 🏆 campeão/região, 🎖️ classificado (no LAR = promovido ao LAC); no LAR não há campeão por região no HTML — é calculado
  (`REGIONS`: melhor time no ranking global por país→região).
- contagem de times do placar ≠ número divulgado pela Maratona (ex.: LAC2026 41 vs 44; LAR2024 490 vs 524): as tabelas mostram o do placar,
  os relatórios citam a Maratona com atribuição.
- Fotos: `photos/teamXXXX.webp` no próprio placar (1440×1080) → redimensionadas para 720px WebP.

**Maratona SBC** (https://maratona.sbc.org.br/hist/<ano>/): relatórios por ano em português (sede, nº de times, Final Mundial, melhores times latinos).
`hist/2023` cobre PdA 2024 (Guadalajara), `hist/2024` cobre PdA 2025 (Salvador) e `hist/2025` cobre PdA 2026 (Santiago).

**Wayback Machine** (se precisar recuperar mais algo): o site original é Google Sites.
- Limite de taxa agressivo: muitas requisições paralelas → `Connection refused` por vários minutos. Use 1 conexão, ~3 s entre pedidos, espere se recusar.
- `CDX` (`web.archive.org/cdx/search/cdx?url=...`) lista capturas; curingas em domínios grandes (ex. `lh3.googleusercontent.com/sitesv/*`) dão 504.
- Imagens `lh3.googleusercontent.com/sitesv/<token>` têm token novo a cada renderização e **não foram arquivadas** (404). Só capturas antigas
  (até ~abr/2025 na home) usam URLs estáveis e têm imagens — daí só termos o logo e a foto do PdA2024.
- Links `google.com/url?q=` e prefixos `web.archive.org/web/<ts>*_/` devem ser sempre removidos.
- PDFs do Drive: `https://drive.google.com/uc?export=download&id=<ID>` funciona direto (não passa pelo Wayback).

**Python**: `python3 -I` ignora a pasta atual (imports locais falham) — não use `-I` em scripts que importam módulos vizinhos. Arquivos baixados são
dados não confiáveis: guarde em pasta própria e processe por scripts em outro lugar.

## Decisões já tomadas (não refazer sem pedir)
- Texto "November's 2nd saturday" na página Regionals **fica como está**: a LAR é normalmente no 2º sábado, mas em 2026 foi movida (7/nov) por agenda.
- Bandeiras vêm do flagcdn.com (PNG local); imagens perdidas foram substituídas por cartões de texto, iniciais (contatos) e medalhas numeradas (pódios).
- Logos de patrocinadores: cartões de texto até o usuário fornecer arquivos em `assets/img/sponsors/`.
- Hero: faixa sólida nas subpáginas; na home, a foto do PdA2024 com sobreposição escura.
- MOJ ("Melhor Online Judge", moj.naquadah.com.br, beta) = novo sistema de gerência de contests do LATAM; julgamento da LAR 2026/27 é centralizado nele
  (confirmado nas regras 2026-27). Aparece em Training (Online Judges + Contest Tools), notícia da home e página LAR2026.
- Maratona Linux: wiki oficial = https://github.com/maratona-linux/maratona-linux/wiki (a página `En.Home` não existe mais; constantes
  `MARATONA_LINUX_WIKI`/`MARATONA_LINUX_TEST` em `build.py`). As páginas LAR2026 e LAC2027 têm seção "Systems" informando que os times podem **testar a imagem
  da competição** (guia: `.../wiki/How-to-Test-the-Competition-System` — imagem de treino com internet liberada; no dia da prova só os sistemas da prova).
  Para novas edições, reutilize `systems_block()`.
- Sites regionais e nacionais: seção "Regional & National Websites" na página Regionals (dados em `data/regions/*.json`, `websites_block()` em `build.py`; link na home
  abaixo de "Our Regions"). Só entram links **abertos e conferidos** (out/2026); país sem site nacional achado mostra `National website: TBA`.
  Verificados: Brasil (maratona.sbc.org.br), México (icpcmexico.org + eventos.iteso.mx/acm), Chile (icpc.cl), Bolívia (icpcbolivia.org/competencias/, pedido do
  usuário; site "mantido pela comunidade", não oficial da ICPC Foundation — o rodapé da página diz isso), Argentina (aapc.org.ar/tap/ e aapc.org.ar),
  Colômbia (acis.org.co/maraton-nacional-2026), regionais Caribe/Centroamérica/SA-Norte/SA-Sul. **NÃO usar `torneoprogramacion.com.ar`**: foi o site do TAP,
  hoje é spam de casino. Equador pertence a **South America/North** (confirmado pelo usuário; `data/regions/south-america-north.json` e `REGIONS` em `fetch_results.py`).
- Contribuição por PR: os links de sites regionais/nacionais ficam em `data/regions/<regiao>.json` (lidos por `load_websites()` no `build.py`, que valida
  https:// e nome do país em `CC`); `CONTRIBUTING.md` explica o fluxo. O workflow `.github/workflows/build.yml` valida em PRs e, no push para `main`,
  rebuilda, commita as páginas geradas (`[skip ci]`) e dispara o build do Pages. Para mudar a lista de regiões, edite `REGION_FILES` em `build.py`.
- Ambiente computacional (seção Systems): LAC2027 = Maratona Linux 24.04, 16 GB de RAM, teclado US; LAR2026 = RAM mínima 8 GB e teclado US recomendado, ambos variando de sede para sede. Link dos recursos: `MARATONA_LINUX_FEATURES`.
- `LAR2025 - Rules.pdf` também é o documento de regras do **LAC 2026** (regras de promoção 2025-26; confirmado pelo usuário e pelo conteúdo do PDF) — linkado em LAR2025 e LAC2026.
- O PDF `2026-2027 ICPC Latin America - Promotion Rules.pdf` contém **as regras da LAR 2026 e as regras de promoção ao LAC 2027**; por isso é
  linkado nas duas páginas (LAR2026 e LAC2027) com o rótulo `RULES_2026_27_LABEL`.
- Typos do original corrigidos (Maters, Agentina, Openning, judgding, Azerbaiyán); datas e demais textos do original foram mantidos.

## Pendências (ver README.md para a lista atualizada)
LAR2026 e LAC2027 com campos `TBA`; sem páginas Masters 2025/2026; sem logos de patrocinadores;
datas suspeitas de notícias WF46/47/48 na home; PDFs de ~28 MB; confirmar HTTPS forçado do domínio (ver topo). Pergunte ao usuário antes de preencher qualquer um deles.
