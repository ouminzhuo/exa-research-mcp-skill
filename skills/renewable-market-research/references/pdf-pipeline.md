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

If these scripts are absent, choose an available renderer such as Pandoc, Playwright HTML print, WeasyPrint, ReportLab, or a repository-native pipeline. On Windows native, run each step directly from PowerShell with `py -3 script.py` or `node script.js`; do not require `make.sh` or Bash.

## Chinese Font Handling

ReportLab/HTML renderers may fail with Chinese glyphs unless fonts are explicitly configured. On Windows, use fonts such as:

```json
{
  "font_display_rl": "SimHei",
  "font_body_rl": "SimSun",
  "font_body_b_rl": "SimHei",
  "font_paths": {
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
