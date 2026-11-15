# Handbook visual specification

This specification and the bundled template define the layout. The numeric
measurements below describe typography, not an external document that must be
retrieved. No personal source document, authorship metadata, or reference
screenshots are distributed or required.

| Element | Specification | Evidence / interpretation |
| --- | --- | --- |
| Paper | US Letter, 612 × 792 PDF points | Exact PDF media box |
| Layout | Single column; 0.65-inch margins | Left 46.8 pt, right 565.2 pt; normal first baseline 56.762 pt |
| Body | Latin Modern Roman, nominal TeX 10 pt | LMRoman10-Regular; PDF size 9.9626 pt (TeX points differ from PDF points) |
| Leading | Nominal 12 TeX pt | Successive baselines approximately 11.955 PDF pt |
| Paragraphs | Justified, no first-line indent, about 6 TeX pt paragraph gap | Baseline gap approximately 17.933 PDF pt; microtype protrusion visible |
| Title | Centered regular serif, nominal 17.28 TeX pt | LMRoman17-Regular, 17.2154 PDF pt; article LARGE size |
| Author/date | Centered regular serif, nominal 12 TeX pt | LMRoman12-Regular, 11.9552 PDF pt |
| Heading 1 | Bold serif, nominal 14.4 TeX pt | LMRoman12-Bold, 14.3462 PDF pt; article section |
| Heading 2 | Bold serif, nominal 12 TeX pt | LMRoman12-Bold, 11.9552 PDF pt; article subsection |
| Heading 3 | Bold serif, nominal 10 TeX pt | Body-size bold, classic article hierarchy |
| Code | Latin Modern Mono, nominal 10 TeX pt, unboxed | LMMono10-Regular/Italic and LMMonoLt10-Bold |
| Contents | Bold top-level entries; inset regular second-level entries with dot leaders and page numbers | Begins below title; two visible levels |
| Lists | Compact, about 25 TeX pt text indentation | Markers around x=58.974; text around x=71.706 PDF pt |
| Quotations | Plain serif inset about 25 TeX pt each side | No box, tint, decorative bar, or forced italics |
| Tables | Plain body-size serif, horizontal rules only | booktabs rules 0.8/0.5 TeX pt; longtable continuation |
| Thematic break | Centered half text width, 0.5 TeX pt black rule | x=176.4 to435.6 PDF pt; thickness 0.4981 PDF pt |
| Footer | Centered Arabic page number, body-size serif, no header | Baseline y=775.088 PDF pt; article plain style, 30 TeX pt footskip |
| Color | Black on white; unobtrusive clickable links | No branding, banners, colored headings, or cover graphics |

Retain optical-size Latin Modern selection: forcing every element to lmroman10-regular.otf changes the title and headings. The packaged template loads lmodern and unicode-math without replacing their main fonts.

These are typography defaults, not a prescribed outline. Adapt content and depth to the task. For languages outside Latin Modern's glyph coverage, identify any required font fallback instead of silently replacing the whole typeface.

## Preamble and heading contract

The canonical source is `../assets/handbook.latex`. It contains the complete reusable preamble: the 10 pt Letter article and 0.65-inch geometry, optical-size Latin Modern setup, XeTeX requirement, microtype protrusion, zero paragraph indentation, `6pt plus 2pt minus 1pt` paragraph spacing, plain centered page numbers, `30pt` footskip, hidden Unicode links, `3em` emergency stretch, compact-list helpers, and the longtable compatibility patch. Preserve these settings and the supporting math, table, graphics, code, and URL packages.

- **Title block:** Use the template's standard `\maketitle`. Supply the document title through YAML `title`, with optional `author` and an explicit, truthful `date`. An omitted author yields `\author{}`; retain the standard title-block spacing rather than collapsing it. A speaker may be recorded in the metadata bullets without being assigned authorship of the notes.
- **PDF metadata:** Derive `pdftitle` and `pdfauthor` from those document fields and retain `pdfcreator={LaTeX via Pandoc}`. Do not hardcode a past document's title or date into the template.
- **Heading hierarchy:** Preserve source heading levels: Markdown H1 maps to `\section`, H2 to `\subsection`, and H3 to `\subsubsection`. Move a note's leading title into YAML and omit that duplicate body heading. Do not automatically promote the remaining headings.
- **Numbering:** Leave automatic section numbering off for short notes and headings that already contain literal numbers. The template uses `\setcounter{secnumdepth}{-\maxdimen}` unless `--number-sections` is explicitly selected.
- **Metadata bullets and lists:** When the source has metadata bullets near the top, retain them immediately below the title block, using bold labels and ordinary compact lists. Preserve nested bullet relationships; normalize Markdown indentation to four spaces per nesting level when needed for Pandoc. Do not turn the metadata into a decorative panel or impose a content-specific outline on other documents.

## Verification

Validate the current toolchain using synthetic content that exercises a title,
contents, three heading levels, paragraphs, lists, code, long tables, quotes,
equations, thematic breaks, and flowing page breaks. Check compilation logs
and visually inspect representative pages. Record actual tool versions and
results for that run; historical successful builds do not prove that the
current machine is configured.
