# Assets and sources

| File | Source | Licence / status |
|---|---|---|
| `assets/brand/logo-*.svg` | Glyph outlines extracted from the brand PDF (`חמו גלמית.pdf`, Canva export). Proportions untouched. | Client brand asset |
| `assets/brand/bag-line.png` | Fine-line bulk-bag illustration embedded in the same PDF (image + alpha mask recombined). | Client brand asset |
| (none) | No photos remain on the page; all imagery is code-drawn. | |
| Inline SVG illustrations | Generated in code by `_build/illus.py`, inlined by `_build/build.py`. | Original work |
| `assets/tex/*.webp` | Procedural paper/grit textures generated with NumPy. | Original work |
| `assets/fonts/NotoSansHebrew-*` (headings, condensed), `Assistant-*` (text), `JetBrainsMono-*` | Google Fonts | SIL Open Font License |

Antidott (Ofir Shavit) is wired into `css/fonts.css` but only loads if licensed webfont files are added; a Canva licence does not cover web embedding.

Archived, no longer used on the page: `_src/archive-img/` (Galmit product photos from galmit.co.il, Canva hero render, Unsplash photos by Heather Green, motomoto sc, Mark Owen Wilkinson Hughes and UZ Creative Services, all Unsplash License).

Rebuild illustrations: `python3 _build/build.py`
