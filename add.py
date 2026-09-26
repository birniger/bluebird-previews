#!/usr/bin/env python3
"""Add a design as the next option and put it live.

    python3 add.py ~/Downloads/index.html

Copies the page to option_<N>/index.html, gives it the neutral title
"Bluebird Snowsports", rebuilds the list page at the site root, then commits
and pushes. GitHub Pages takes about a minute to update.
"""
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://birniger.github.io/bluebird-previews/"
TITLE = "Bluebird Snowsports"


def options():
    found = [p for p in ROOT.glob("option_*") if p.name[7:].isdigit()]
    return sorted(found, key=lambda p: int(p.name[7:]))


def neutral_title(page: Path):
    text = page.read_text(encoding="utf-8")
    # Claude Design bundles carry the title twice: in the page and, escaped, in the packed template.
    text = re.sub(r"<title>.*?(</title>|<\\u002Ftitle>)", lambda m: "<title>" + TITLE + m.group(1), text)
    page.write_text(text, encoding="utf-8")


def build_index():
    items = "\n".join(
        f'    <li><a href="{p.name}/">Option {p.name[7:]}</a></li>' for p in options()
    )
    page = (ROOT / "index.template.html").read_text(encoding="utf-8")
    (ROOT / "index.html").write_text(page.replace("<!-- options -->", items), encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]).expanduser()
    if not src.is_file():
        sys.exit(f"Not a file: {src}")
    n = int(options()[-1].name[7:]) + 1 if options() else 1
    folder = ROOT / f"option_{n}"
    folder.mkdir()
    shutil.copyfile(src, folder / "index.html")
    neutral_title(folder / "index.html")
    build_index()
    git = lambda *a: subprocess.run(["git", "-C", str(ROOT), *a], check=True)
    git("add", "-A")
    git("commit", "-q", "-m", f"Add option {n}")
    git("push", "-q")
    print(f"Live in about a minute: {SITE}option_{n}/")


if __name__ == "__main__":
    if sys.argv[1:] == ["--index"]:
        build_index()
    else:
        main()
