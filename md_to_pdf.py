# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "markdown-it-py>=3.0",
#     "mdit-py-plugins>=0.4",
#     "pygments>=2.17",
#     "playwright>=1.45",
# ]
# ///
import argparse
import sys
import tempfile
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

PAGE_STYLE = """
@page { margin: 2cm; }
body {
    font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #1f2328;
}
h1, h2 { border-bottom: 1px solid #d1d9e0; padding-bottom: 0.3em; }
h1, h2, h3, h4 { break-after: avoid; }
code {
    font-family: Consolas, "SF Mono", Menlo, monospace;
    font-size: 0.9em;
    background: #f6f8fa;
    padding: 0.15em 0.3em;
    border-radius: 4px;
}
pre { background: #f6f8fa; padding: 1em; border-radius: 6px; overflow-x: auto; break-inside: avoid; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; margin: 1em 0; }
th, td { border: 1px solid #d1d9e0; padding: 0.4em 0.8em; }
th { background: #f6f8fa; }
blockquote { margin: 0; padding: 0 1em; color: #59636e; border-left: 0.25em solid #d1d9e0; }
img { max-width: 100%; }
.task-list-item { list-style: none; }
.task-list-item input { margin-left: -1.4em; }
"""

# Tried in order; the first two reuse an installed browser so no download is needed.
BROWSER_CHANNELS = ["chrome", "msedge", None]


def highlight_code(code: str, language: str, attributes: str) -> str:
    try:
        lexer = get_lexer_by_name(language)
    except ClassNotFound:
        return ""
    return highlight(code, lexer, HtmlFormatter(nowrap=True))


def render_html(markdown_text: str, title: str, base_directory: Path) -> str:
    renderer = (
        MarkdownIt("commonmark", {"highlight": highlight_code, "html": True})
        .enable(["table", "strikethrough"])
        .use(tasklists_plugin)
    )
    body = renderer.render(markdown_text)
    code_style = HtmlFormatter().get_style_defs("pre code")
    # The trailing slash makes relative image paths resolve inside the directory.
    base_href = base_directory.resolve().as_uri() + "/"
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<base href="{base_href}">
<title>{title}</title>
<style>{PAGE_STYLE}{code_style}</style>
</head>
<body>
{body}
</body>
</html>"""


def launch_browser(playwright):
    for channel in BROWSER_CHANNELS:
        try:
            return playwright.chromium.launch(channel=channel)
        except PlaywrightError:
            continue
    sys.exit(
        "No Chromium browser found. Install Chrome or Edge, or run:\n"
        "  uvx playwright install chromium"
    )


def print_to_pdf(html: str, pdf_path: Path) -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        html_path = Path(temporary_directory) / "page.html"
        html_path.write_text(html, encoding="utf-8")
        with sync_playwright() as playwright:
            browser = launch_browser(playwright)
            page = browser.new_page()
            page.goto(html_path.as_uri(), wait_until="networkidle")
            page.pdf(path=str(pdf_path), format="Letter", print_background=True)
            browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Markdown file to PDF.")
    parser.add_argument("markdown_path", type=Path)
    parser.add_argument(
        "-o", "--output", type=Path, help="PDF path (default: next to the input)"
    )
    arguments = parser.parse_args()

    markdown_path: Path = arguments.markdown_path
    if not markdown_path.is_file():
        sys.exit(f"Not a file: {markdown_path}")
    pdf_path: Path = arguments.output or markdown_path.with_suffix(".pdf")

    # utf-8-sig strips the byte order mark many Windows editors add
    markdown_text = markdown_path.read_text(encoding="utf-8-sig")
    html = render_html(markdown_text, markdown_path.stem, markdown_path.parent)
    print_to_pdf(html, pdf_path)
    print(pdf_path)


if __name__ == "__main__":
    main()
