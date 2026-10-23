"""Render the documentation's static SVG diagrams without external dependencies."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def card(x: int, y: int, width: int, height: int, lines: list[str], fill: str = '#eef5ff') -> str:
    """Draw a labeled card with centered, explicit line breaks."""
    start = y + height / 2 - (len(lines) - 1) * 12 + 6
    labels = ''.join(
        f'<text x="{x + width / 2}" y="{start + index * 24}">{escape(line)}</text>'
        for index, line in enumerate(lines)
    )
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="12" fill="{fill}"/>{labels}'


def arrow(path: str) -> str:
    return f'<path d="{path}" marker-end="url(#arrow)"/>'


def write_svg(name: str, title: str, height: int, edges: list[str], cards: list[str]):
    """Write a standalone diagram; the Python layout is its editable source."""
    document = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1020 {height}" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#4b6178"/></marker></defs>
<style>text {{font:17px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;text-anchor:middle;fill:#172a3a}} rect {{stroke:#b5c6d7;stroke-width:1.5}} path {{fill:none;stroke:#4b6178;stroke-width:2}}</style>
<rect width="1020" height="{height}" fill="#ffffff" style="stroke:none"/>
{''.join(edges)}
{''.join(cards)}
</svg>
'''
    (ROOT / name).write_text(document)


def main():
    write_svg('conversation-flow.svg', 'From captured sources to inspectable records and evidence-backed assistant work', 800, [
        arrow('M 250 115 L 250 135 L 510 135 L 510 155'),
        arrow('M 770 115 L 770 135 L 510 135 L 510 155'),
        arrow('M 510 230 L 510 270'),
        arrow('M 510 345 L 510 370 L 180 370 L 180 400'),
        arrow('M 510 345 L 510 400'),
        arrow('M 510 345 L 510 370 L 840 370 L 840 400'),
        arrow('M 510 490 L 510 545'),
        arrow('M 510 625 L 510 680'),
        arrow('M 180 625 L 180 720 L 370 720'),
        arrow('M 650 720 L 700 720'),
    ], [
        card(40, 35, 420, 80, ['Available local Codex history']),
        card(560, 35, 420, 80, ['Exports and normalized', 'desktop captures']),
        card(300, 155, 420, 75, ['Import adapters', 'Visible messages and metadata']),
        card(300, 270, 420, 75, ['SQLite records and revisions'], '#eaf6ee'),
        card(40, 400, 280, 90, ['Readable JSON', 'and Markdown archive']),
        card(370, 400, 280, 90, ['Search and', 'passage indexes']),
        card(700, 400, 280, 90, ['Generated indexes', 'and HTML views']),
        card(370, 545, 280, 80, ['Candidate passages', 'with source locations']),
        card(40, 545, 280, 80, ['Current project files']),
        card(370, 680, 280, 80, ['Active assistant', 'reads and interprets'], '#fff4df'),
        card(700, 680, 280, 80, ['Source-linked briefing', 'or authorized outcome'], '#eaf6ee'),
    ])
    write_svg('shared-workspace.svg', 'People and active assistants access the same visible local workspace', 560, [
        arrow('M 220 115 L 220 165'),
        arrow('M 800 115 L 800 165'),
        arrow('M 220 250 L 220 280 L 430 280 L 430 310'),
        arrow('M 800 250 L 800 280 L 590 280 L 590 310'),
        arrow('M 510 395 L 510 445'),
    ], [
        card(70, 35, 300, 80, ['Person']),
        card(650, 35, 300, 80, ['Active assistant']),
        card(70, 165, 300, 85, ['Local browser app', 'Readable files / CLI']),
        card(650, 165, 300, 85, ['Files / CLI', 'Workspace skills']),
        card(300, 310, 420, 85, ['Shared local workspace'], '#eaf6ee'),
        card(180, 445, 660, 80, ['Chats, projects, memory, skills,', 'and operating records']),
    ])


if __name__ == '__main__':
    main()
