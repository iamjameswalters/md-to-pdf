# md-to-pdf

Render a Markdown file to PDF using your installed Chrome or Edge.

```
md-to-pdf notes.md                # writes notes.pdf next to notes.md
md-to-pdf notes.md -o out.pdf     # writes out.pdf
```

Supports CommonMark plus tables, strikethrough, task lists, syntax-highlighted code blocks, and relative image paths.

## Two ways to run it

[uv](https://docs.astral.sh/uv/getting-started/installation/) is recommended in either case.

### 1. Install as a tool (recommended)

Clone the repository. From this directory, run:

```
uv tool install . --force
```

This puts `md-to-pdf` on your PATH. Run it from anywhere.

The install is a copy, not a link. After editing `md_to_pdf.py` or pulling a new version of the repository, run `uv tool install . --force` again to pick up the change.

### 2. Run the script directly

If you don't want to install this and just run the script, you can:

```
uv run md_to_pdf.py notes.md
```

uv reads the [dependency list from the comment block](https://peps.python.org/pep-0723/) at the top of `md_to_pdf.py` and builds a throwaway environment for it. 

## Browser

The PDF is printed by a real browser through Playwright. It tries, in order:

1. Google Chrome
2. Microsoft Edge
3. Playwright's own Chromium

If neither Chrome nor Edge is installed, download Playwright's Chromium once:

```
uvx playwright install chromium
```

## Changing dependencies

Dependencies are listed in two places:

- the comment block at the top of `md_to_pdf.py` (used by `uv run`)
- `pyproject.toml` (used by `uv tool install`)

Keep them in sync.
