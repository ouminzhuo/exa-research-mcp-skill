# Report and PDF Pipeline

## Full Report

Default target: 10-12 pages or equivalent MD depth.

Recommended sections:

1. Executive summary
2. Market size, project pipeline, and confirmed/all-phase capacity
3. National plans, auctions, tariffs, and policy framework
4. Project-by-project pipeline table
5. Developer and sponsor landscape
6. Financing structure by IFI/commercial/source
7. Technology, OEM, EPC, grid, and storage analysis
8. Environmental/social/ESIA and community issues
9. Carbon markets, I-REC, CBAM, and green-hydrogen outlook
10. Chinese company matrix and participation opportunities
11. Regional benchmark comparison
12. Risks, gaps, and update plan
13. Source and confidence appendix

## Lite Report

Default target: 3-4 pages or concise MD.

Purpose: a polished delivery summary with enough structure to be useful while reserving deeper internal analysis for the full report.

Include:

- Cover/title and short executive summary
- Policy/planning snapshot
- In-construction/signed/project pipeline essentials
- Forecast and opportunity summary
- Key risks and caveats

Reduce or omit:

- project-level ROI and detailed sponsor financial model
- full Chinese company matrix
- detailed turbine/module/battery specifications
- carbon/hydrogen/CBAM deep analysis
- ESIA and community-impact details unless material to the client decision
- regional benchmark deep dive

If operational projects are excluded from the lite version, still summarize total operational capacity and state the filtering rule.

## Report Format Requirements

Default final package:

1. Markdown (`.md`) remains the source-of-truth authoring format because it is easy to review, diff, cite, and reuse.
2. HTML (`.html`) is the layout-control format for table alignment, typography, page breaks, and print styles.
3. PDF (`.pdf`) should normally be rendered from the controlled HTML file, not directly from raw Markdown.

Recommended fonts:

- Chinese: `Microsoft YaHei`, `微软雅黑`, fallback `SimHei`, `SimSun`, sans-serif.
- English/Latin: `Times New Roman`, Times, serif.
- Tables may use the same family but must define explicit `font-family`, `font-size`, `line-height`, `border-collapse`, widths, and page-break behavior.

## Markdown-to-HTML-to-PDF Decision

Prefer option 2: **write Markdown first, convert to controlled HTML, then render PDF from HTML**.

Why:

- Markdown is easier for research agents to edit, review, cite, and compare in git.
- HTML gives stronger control over table alignment, fonts, page breaks, headers, footers, captions, and print CSS.
- The same Markdown can generate both internal reports and lighter delivery versions.
- Review gates can be applied to Markdown before layout polishing.

Use option 1, direct HTML authoring, only when:

- the report is a highly designed executive deck,
- complex layout cannot be represented cleanly in Markdown,
- the HTML template is stable and the writer can preserve citations and evidence IDs, or
- final visual fidelity is more important than text-review simplicity.

Recommended pipeline:

```text
{slug}-report.md
  -> markdown-to-html renderer with controlled template/CSS
  -> {slug}-report.html
  -> browser/Playwright/WeasyPrint/Pandoc HTML print
  -> {slug}-report.pdf
```

CSS baseline:

```css
body {
  font-family: "Times New Roman", "Microsoft YaHei", "微软雅黑", serif;
}
:lang(zh), .zh {
  font-family: "Microsoft YaHei", "微软雅黑", "SimHei", sans-serif;
}
:lang(en), .en {
  font-family: "Times New Roman", Times, serif;
}
table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  page-break-inside: auto;
}
th, td {
  border: 1px solid #d0d7de;
  padding: 6px 8px;
  vertical-align: top;
  word-break: break-word;
}
tr {
  page-break-inside: avoid;
}
```

## MD-to-PDF Pipeline

Use the local project pipeline if present. A proven pipeline can be:

```text
source.md
  -> reformat_parse.py -> content.json
  -> palette.py -> tokens.json
  -> render_body.py -> body.pdf
  -> cover.py -> cover.html
  -> render_cover.js -> cover.pdf
  -> merge.py -> final.pdf
```

If these scripts are absent, choose an available renderer such as Pandoc, Playwright HTML print, WeasyPrint, ReportLab, or a repository-native pipeline. Prefer HTML-to-PDF rendering when table alignment and typography matter. On Windows native, run each step directly from PowerShell with `py -3 script.py` or `node script.js`; do not require `make.sh` or Bash.

## Chinese and English Font Handling

ReportLab/HTML renderers may fail with Chinese glyphs unless fonts are explicitly configured. For final report output, prefer Microsoft YaHei for Chinese and Times New Roman for English/Latin text. On Windows, use fonts such as:

```json
{
  "font_display_rl": "Microsoft YaHei",
  "font_body_rl": "Microsoft YaHei",
  "font_english_rl": "Times New Roman",
  "font_paths": {
    "Microsoft YaHei": "C:/Windows/Fonts/msyh.ttc",
    "SimSun": "C:/Windows/Fonts/simsun.ttc",
    "SimHei": "C:/Windows/Fonts/simhei.ttf"
  }
}
```

On Linux/macOS, detect available CJK fonts and update the renderer tokens accordingly. If PDF layout becomes unreliable, deliver the MD files and explain that MD is the source of truth.

## Validation

- Confirm full and lite MD files exist and are non-empty.
- Confirm PDFs exist only if rendering was requested and the PDF stack is available. On Windows, also confirm the renderer can access configured CJK fonts.
- Open or inspect PDF metadata/size when possible.
- Record skipped PDF rendering in `index.json` with the environment reason.
