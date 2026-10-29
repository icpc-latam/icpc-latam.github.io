# icpclatam.org — site estático (recuperado)

Site do **ICPC Latin America** (www.icpclatam.org). O Google Sites original foi perdido e este site
foi reconstruído a partir das capturas do Wayback Machine (jan–jun 2026) e depois atualizado com dados
do ScoreLatam e da Maratona SBC. É HTML/CSS puro: basta enviar esta pasta para qualquer hospedagem estática
(nginx, GitHub Pages, Netlify…). Nenhum build é necessário para publicar.

As URLs espelham o site antigo: `/regionals/lar2025/`, `/championships/lac2026/`, `/masters/masters2024/`, …

> Vocabulário: **LAC** = Latin American Championship = **PdA** (Programadores de América) · **LAR** = Latin American
> Regionals = **LATAM** (no ScoreLatam) · **CCL** = times "café com leite" (fora de competição).

## Como atualizar o site

Os `index.html` são **gerados** — não edite à mão (serão sobrescritos). Todo o conteúdo está em `tools/build.py`.

```bash
python3 tools/fetch_results.py   # (opcional) baixa placares + fotos do ScoreLatam → tools/results.json, assets/img/teams/
python3 tools/build.py           # regenera todas as páginas, sitemap.xml, robots.txt, 404.html
python3 tools/check_links.py     # confere links/arquivos locais (deve terminar com "problems: 0")
python3 -m http.server 8765      # pré-visualizar em http://localhost:8765/
```

`fetch_results.py` precisa de Pillow (`PIL`) para redimensionar as fotos (720 px, WebP).

### Tarefas comuns
| Quero… | Onde mexer |
|---|---|
| Mudar o banner amarelo do topo | `BANNER` em `tools/build.py` |
| Eventos "Upcoming/Latest" e notícias da home | `page_home()` |
| Preencher a LAR 2026 (times, transmissões, resultados) | `page_lar2026()` |
| Preencher a LAC 2027 (site, times qualificados) | `page_lac2027()` |
| Publicar resultados de uma edição nova | incluir em `EDITIONS` (`fetch_results.py`), rodar o fetch, usar `results_table(...)`/`winner_block(...)` na página |
| Nova página/edição | criar `page_xxx()`, registrar em `build_pages()`, em `NAV` e nas listas de edições (`page_regionals`/`page_championships`/`page_masters`) |
| Logos de patrocinadores | colocar `assets/img/sponsors/{jetbrains,huawei,icpc-foundation}.{svg,png}` (são usados automaticamente) |
| PDFs | colocar em `assets/docs/` e usar `pdf(page, "arquivo.pdf", "rótulo")` |

## Estado atual (14/out/2026)

Páginas: Home, News (Archive), Regionals (LAR2026, LAR2025, LAR2024, LARs1996-2023), Championships (LAC2027, LAC2026,
LAC2025, LAC2024), Masters (2019–2024), Training, History, Contact. Resultados completos de LAC2024-2026 e LAR2024-2025;
relatórios por edição (History e páginas LAC/LAR). Fotos de times vêm do ScoreLatam. MOJ (moj.naquadah.com.br) está em
Training (Online Judges e Contest Tools) e na notícia da home como novo sistema de gerência de contests do LATAM. As páginas LAR2026 e LAC2027 têm
seção "Systems" com Maratona Linux (wiki: github.com/maratona-linux/maratona-linux/wiki) e o convite para os times testarem a imagem da competição
(guia "How to Test the Competition System"). O PDF `LAR2025 - Rules.pdf` também são as regras do LAC 2026 (linkado em LAR2025 e LAC2026). O PDF de regras 2026-27 contém as regras da LAR 2026 e a promoção ao LAC 2027 (linkado nas duas páginas).

A página Regionals tem a seção "Regional & National Websites" (links dos 6 regionais e dos países por sub-região; dados em `WEBSITES`
no `tools/build.py`). Já tem Brasil, México, Chile, Bolívia, Argentina e Colômbia; os demais países estão como `TBA`.

### Pendências conhecidas
- **Sites nacionais** sem link (TBA): Costa Rica, El Salvador, Guatemala, Nicaragua, Panamá, Antígua e Barbuda, Cuba, República Dominicana, Granada, Haiti,
  Jamaica, Porto Rico, Trinidad e Tobago, Ilhas Virgens (EUA), Venezuela, Equador, Paraguai, Peru e Uruguai. Peça ao usuário ou aos diretores regionais.
  Confirmar também a região do Equador (Sul ou Norte).
- **LAR 2026** (6–7 nov 2026; competição sáb. 7/nov, live no canal @MaratonaSBC): faltam times registrados, transmissões dos outros
  países e resultados (`TBA`/`TBD`). **LAC 2027** (13–17 jul 2027, Monterrey, México): faltam site oficial, times qualificados, resultados.
- **Masters**: sem página para a edição #6 (fev/2025) nem para 2026.
- **Não recuperável** do arquivo (imagens do Google Sites nunca foram arquivadas): logos de patrocinadores, fotos de notícias,
  pódios dos Masters, fotos de contato, logos de camps de treinamento. Hoje: bandeiras (flagcdn.com, PNG local), iniciais/medalhas/cartões.
- Datas suspeitas herdadas do original (não alteradas): notícias WF46/47/48 na home ("April 19/20, 2024"; Astana foi em set/2024).
- Numeração derivada: LAR2026 = edição #31, LAC2027 = edição #4. Notícia do MOJ datada "October 2026".
- Dois PDFs têm ~28 MB (`PdA2024 - Teams stats.pdf`, `ICPC Latam stats until PdA2024.pdf`): alguns hosts têm limite (ex.: Cloudflare Pages 25 MiB).
- URLs canônicas/sitemap assumem `https://www.icpclatam.org/` (`SITE_URL` em `build.py`).

## O que foi feito (histórico)

1. **Recuperação** (Wayback): baixadas as 19 páginas do site antigo (Google Sites) + home; extraídos textos, links (removendo prefixos do
   Wayback e redirecionadores `google.com/url?q=`), 10 PDFs (direto do Google Drive) e vídeos do YouTube. Logo (mapa) e foto dos campeões
   do PdA2024 recuperados de capturas antigas. Visual recriado (preto/branco + amarelo `#FEC009`, fonte Lato, títulos `icpc.latam->pagina()`).
2. **Gerador estático** `tools/build.py` com layout único (cabeçalho, menu, rodapé social) e páginas mirando as URLs antigas.
   Typos corrigidos: Maters, Agentina, Openning, judgding, Azerbaiyán; "March , 17." → "March 17, 2025".
3. **Resultados** via ScoreLatam (`tools/fetch_results.py` → `tools/results.json`): LAC2024-26, LAR2024-25 (top 10-13, melhores por região,
   times promovidos) + relatórios da Maratona SBC (sede, nº de times, Final Mundial).
4. **Atualizações de 2026**: páginas LAR2026 e LAC2027, regras de promoção 2026-27 (PDF), MOJ em Training + notícia, home com cards de
   eventos, fotos de times, hero com foto, sitemap/robots/404/OG.

Detalhes técnicos e armadilhas: veja `CLAUDE.md`.
