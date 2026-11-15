---
name: latex-handbook
description: "Create PDFs and editable Markdown/TeX sources in a compact handbook style using Pandoc and XeLaTeX or Tectonic: Latin Modern fonts, US Letter layout, classic headings, plain tables, and centered page numbers. Use for study-guide layouts, LaTeX handbook formatting, or an explicit latex-handbook invocation."
---

# LaTeX Handbook

## Dependency preflight

Require Python 3.9+, Pandoc, the bundled build helper/template, and readable
input before running the build. A PDF additionally requires XeLaTeX or Tectonic,
the declared TeX packages/transitive dependencies, and Latin Modern fonts.
An offline Tectonic build requires an accessible pre-provisioned local bundle.
Verify the selected toolchain first; if a required component is missing, stop
that build and identify it. Do not auto-install packages or silently downgrade
a PDF request to source-only output. `--tex-only` still needs Pandoc and is
valid only for an explicitly requested source-only build. Missing optional
Poppler tools stop their inspection checks, not a separately viable build.

Use the visual system in [references/style.md](references/style.md) and the packaged LaTeX template. Both are included; no external reference document or screenshots are required.

Use `assets/handbook.latex` as the Pandoc template. It preserves optical-size Latin Modern fonts and the classic article layout. Do not replace it with a Word, HTML-print, or ReportLab workflow. Preserve the user's requested content, structure, and output formats.

## Consistent preamble and title block

`assets/handbook.latex` is the canonical preamble. Reuse it through `scripts/build.py`; do not reconstruct its packages or spacing for each document. Keep its typography and page-layout defaults unless the user requests a change. Use `header-includes` only for additive document features that preserve those defaults.

Read the [preamble and heading contract](references/style.md#preamble-and-heading-contract) when adapting a source or title block. Document-specific title, author, date, and PDF metadata remain variable; historical source content is not a skill default.

## Build

Keep a UTF-8 Markdown source with YAML `title`, optional `author`, and explicit `date`. Use a truthful date and attribution rather than copying the reference metadata. Ordinary Markdown headings, lists, tables, fenced code, quotations, and thematic breaks map to the retained style.

```sh
python3 scripts/build.py /absolute/path/document.md --output-dir /absolute/path/output
```

Paths to this script are relative to this skill's directory. It produces matching `.md`, `.tex`, and `.pdf` files. It uses Pandoc and prefers XeLaTeX, with Tectonic (a XeTeX engine) as the fallback. Pass `--engine xelatex` or `--engine tectonic` to choose explicitly.

Tectonic may download fonts/packages on its first run. For offline builds, pre-provision an appropriate local bundle and pass `--bundle /absolute/path/to/bundle`, or use a complete local XeLaTeX installation. The template and build helper are bundled; the TeX engine, font/package distribution, and Pandoc are not. Do not fetch arbitrary historical bundle URLs automatically.

- Use `--toc` for long reference documents, with `--toc-depth 2` by default. Omit it for short notes. The title and contents share the first page, as in the reference.
- Use `--number-sections` for newly authored numbered manuals. If headings already contain numbers, leave this flag off to avoid duplicate numbering; the original PDF used literal heading numbers.
- Use `---` between major topics only where helpful. It renders as the reference's centered half-width thin rule.
- Keep code lines within the text width, adding line breaks that preserve meaning. Avoid shrinking body text or page margins to fit content.
- Preserve a user's native `.tex` source when supplied; adapt the packaged preamble to it rather than converting through Markdown unnecessarily.

## Verify and deliver

Compile to PDF, check the TeX log for missing glyphs and overfull boxes, and render representative pages with `pdftoppm`. Inspect the title/contents page, a dense body page, and any table/code page. Check fonts with `pdffonts`: expect Latin Modern Roman and Latin Modern Mono. Inspect additional pages when warnings or unusual content justify it.

Fix clipped lines, awkward tables, stranded headings, and ambiguous numbering while preserving the measured design. Standard flowing section breaks are preferred; do not force every section onto its own page. Use the checks above directly; another PDF skill is not required. If page rendering or visual inspection is unavailable, report that verification gap.

Return the requested document and editable source. Explain any missing build dependencies; never claim a PDF was compiled if it was not. The bundled template is the layout contract; do not claim exact reproduction of an unavailable document.

## Dependencies and portability

The template, style specification, and Python 3.9+ standard-library build
wrapper are bundled; no other skill is required. The wrapper requires Pandoc
even with `--tex-only`. PDF compilation additionally requires XeLaTeX or
Tectonic, the template's TeX packages, and Latin Modern fonts. `pdftoppm` and
`pdffonts` are optional Poppler verification tools. For offline compilation,
pre-provision a local TeX distribution/bundle and document its licenses and
checksums; none is currently vendored. Styling instructions can be read without
these binaries, but a PDF cannot honestly be claimed without compilation.

The template directly loads `geometry`, `amsmath`, `amssymb`, `lmodern`,
`iftex`, `unicode-math` (with its font support), `microtype`, `parskip`,
`xcolor`, `longtable`, `booktabs`, `array`, `calc`, `etoolbox`, `graphicx`,
`fancyvrb`, `xurl`, and `hyperref`. Provision their transitive TeX dependencies
as part of the chosen distribution rather than downloading them during a
claimed offline build.
