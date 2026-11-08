# Assets and sources

| File | Source | Licence / status |
|---|---|---|
| `assets/brand/logo-*.svg` | Glyph outlines extracted from the brand PDF (`חמו גלמית.pdf`, Canva export). Proportions untouched. | Client brand asset |
| `assets/brand/bag-line.png` | Fine-line bulk-bag illustration embedded in the same PDF (image + alpha mask recombined). | Client brand asset |
| Inline SVG illustrations | Generated in code by `_build/illus.py`, inlined by `_build/build.py`. | Original work |
| `assets/tex/*.webp` | Procedural paper/grit textures generated with NumPy. | Original work |
| `assets/fonts/NotoSansHebrew-*` (headings, condensed), `Assistant-*` (text), `JetBrainsMono-*` | Google Fonts | SIL Open Font License |

Antidott (Ofir Shavit) is wired into `css/fonts.css` but only loads if licensed webfont files are added; a Canva licence does not cover web embedding.

Archived, no longer used on the page: `_src/archive-img/` (Galmit product photos from galmit.co.il, Canva hero render, Unsplash photos by Heather Green, motomoto sc, Mark Owen Wilkinson Hughes and UZ Creative Services, all Unsplash License).

Rebuild illustrations: `python3 _build/build.py`

## Client logos (`assets/clients/`)

Status: Client logos, used with Galmit's client's permission per site owner. Originals in `_src/clients-raw/`. Each output is single-colour ink `#1f1a16` on transparent, trimmed, max 400x120 (white knock-outs kept transparent).

| File | Company | Source |
|---|---|---|
| `shtibel.png` | שטיבל טחנות קמח (Stybel flour mills) | https://stybel.co.il/app/uploads/2025/04/black_logo.svg (official site header) |
| `israel-post.png` | דואר ישראל | https://upload.wikimedia.org/wikipedia/he/6/6d/DoarIsrael.svg (Hebrew Wikipedia, fair-use logo file) |
| `amber.png` | אמבר מכון תערובת (ambar.co.il) | https://ambar.co.il/wp-content/themes/blankslate/images/ambar_logo.svg (official site header; yellow stripes knocked out) |
| `asam-hagalil.png` | אסם הגליל, מכון תערובת של מושבי הגליל (Goren) | https://www.ba-e.co.il/wp-content/uploads/2020/07/אסם_הגליל_לוגו-removebg-preview.png (client-logo page of a consultancy; 366x107 original, contact text cropped off) |
| `osem-nestle.png` | אסם (Osem-Nestlé), fallback only, not the client | https://upload.wikimedia.org/wikipedia/he/2/22/Osem_Logo.svg (glow halo removed) |
| `tadmir.png` | קבוצת תדמיר (Tadmir feed mill) | https://www.tadmir.co.il/sites/default/files/logo.svg (official site header) |
| `mifratz.png` | טחנות קמח מפרץ, Haifa | https://www.licard.co.il/upload/imgsiconsupload/67a9fd380bc2b.png (company's digital business card; Man bakery mark cropped off) |
| `agrical.png` | אגריקל (Agrekal growing media, Moshav HaBonim) | https://www.agrekal.co.il/images/agrekal_logo.png (official site header) |

Not found: טחנת קמח רות/רוט (Kiryat Gat, no website or logo online) and גרעיני חממה (Facebook-only chain "גרעיני עפולה חממה"; no verifiable logo). Ask the client for these files.

## Stock photos (v2, 2026-11-08)

All from Unsplash (Unsplash License), graded to one warm low-saturation look by `_build/photos.py`. Originals in `_src/photo-src/` (gitignored).

| File | Unsplash photo |
|---|---|
| `assets/photo/hero-*` | photo-1777432048471-d6fae85832f9 (bulk bags stacked outdoors) |
| `assets/photo/warehouse-*` | photo-1710141530542-f792450e736e (warehouse of stacked white bags) |

| `assets/brand/pashut-yarok.webp` | Pashut Yarok logo (logo-2026.png from ~/Developer/pashut-yarok), links to pashutyarok.co.il | Partner brand asset |
