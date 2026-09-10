#!/usr/bin/env python3
"""Dung EPUB toi uu cho may doc sach e-ink tu file van ban don gian.

Vi sao khong dung Calibre hay pandoc: chung sinh EPUB cho man hinh mau, nhet
@font-face, CSS nhieu tang va anh nen. Tren X4 (man 480x800, 4 muc xam, RAM
320KB) nhung thu do lam cham hoac hong hien thi:

  - @font-face buoc may nap font nhung trong sach, thuong thieu glyph tieng Viet
    -> crash "No glyph for codepoint".
  - CSS phuc tap lam tang thoi gian dung chi muc trang.
  - Anh nen an RAM ma man hinh 4 muc xam khong the hien.

Sach dung o day chi co the h1/h2/p/ul/table va mot bang CSS duy nhat khong khai
bao font-family, de may dung font nguoi dung chon.

Dinh dang nguon (xem vocab/*.book):

    @title: Ten sach
    @author: Tac gia
    @lang: en

    # Chuong 1 — Ten chuong
    Doan van thuong.

    ## Muc con
    - gach dau dong

    @vocab
    word | /ipa/ | nghia tieng Viet | cau vi du
    @end

    @dialog
    A: Cau thoai
    B: Cau thoai
    @end

    > Cau trich dan hoac ghi chu
"""
import argparse
import html
import os
import re
import sys
import zipfile

# The stylesheet deliberately declares no typeface and embeds no font: the reader
# picks the face, and a font embedded in the book is the usual cause of the
# "No glyph for codepoint" crash on Vietnamese text.
#
# The comment says this in prose rather than naming the CSS at-rule and property,
# because tooling that strips embedded fonts (split_epub.py included) matches
# those names with a regex that does not know what a comment is — a comment
# mentioning them gets partly eaten along with the rule it warns about.
CSS = """\
body { margin: 0; padding: 0; text-align: left; }
h1 { font-size: 1.35em; margin: 0 0 0.8em 0; text-align: left; }
h2 { font-size: 1.12em; margin: 1.4em 0 0.5em 0; }
h3 { font-size: 1.0em; margin: 1.1em 0 0.4em 0; }
p  { margin: 0 0 0.7em 0; line-height: 1.5; }
ul, ol { margin: 0 0 0.8em 1.1em; padding: 0; }
li { margin: 0 0 0.35em 0; line-height: 1.45; }
blockquote { margin: 0.8em 0; padding: 0 0 0 0.8em; border-left: 2px solid #000; }
table { width: 100%; border-collapse: collapse; margin: 0 0 0.9em 0; }
td { vertical-align: top; padding: 0.25em 0.3em 0.25em 0; }
.w  { font-weight: bold; }
.ipa { font-size: 0.85em; }
.vi { }
.ex { font-style: italic; font-size: 0.92em; }
.sp { font-weight: bold; }
hr { border: none; border-top: 1px solid #000; margin: 1.2em 0; }
"""

CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>"""


def esc(text):
    return html.escape(text, quote=False)


def inline(text):
    """**dam** va *nghieng* -> the HTML. Escape truoc de khong lot the la."""
    out = esc(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    out = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", out)
    return out


class Chapter:
    def __init__(self, title):
        self.title = title
        self.parts = []


def parse(path):
    meta = {"title": "Untitled", "author": "", "lang": "en"}
    chapters = []
    cur = None
    mode = None      # None | vocab | dialog | list
    buf = []

    def flush_list():
        nonlocal buf
        if buf and cur:
            cur.parts.append(("ul", buf))
        buf = []

    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        stripped = line.strip()

        if mode in ("vocab", "dialog"):
            if stripped == "@end":
                cur.parts.append((mode, buf))
                buf, mode = [], None
            elif stripped:
                buf.append(stripped)
            continue

        if stripped.startswith("@") and ":" in stripped and cur is None:
            key, _, val = stripped[1:].partition(":")
            meta[key.strip()] = val.strip()
            continue

        if stripped in ("@vocab", "@dialog"):
            flush_list()
            mode = stripped[1:]
            buf = []
            continue

        if stripped.startswith("# "):
            flush_list()
            cur = Chapter(stripped[2:].strip())
            chapters.append(cur)
            continue

        if cur is None:
            continue

        if stripped.startswith("### "):
            flush_list()
            cur.parts.append(("h3", stripped[4:].strip()))
        elif stripped.startswith("## "):
            flush_list()
            cur.parts.append(("h2", stripped[3:].strip()))
        elif stripped.startswith("> "):
            flush_list()
            cur.parts.append(("quote", stripped[2:].strip()))
        elif stripped.startswith("- "):
            buf.append(stripped[2:].strip())
        elif stripped == "---":
            flush_list()
            cur.parts.append(("hr", ""))
        elif stripped == "":
            flush_list()
        else:
            flush_list()
            cur.parts.append(("p", stripped))

    flush_list()
    if mode and buf and cur:
        cur.parts.append((mode, buf))
    return meta, chapters


def render_vocab(rows):
    """Moi tu mot hang bang: tu + phien am, nghia, vi du."""
    out = ["<table>"]
    for row in rows:
        f = [c.strip() for c in row.split("|")]
        while len(f) < 4:
            f.append("")
        word, ipa, vi, ex = f[0], f[1], f[2], f[3]
        cell = f'<span class="w">{esc(word)}</span>'
        if ipa:
            cell += f' <span class="ipa">{esc(ipa)}</span>'
        if vi:
            cell += f'<br/><span class="vi">{esc(vi)}</span>'
        if ex:
            cell += f'<br/><span class="ex">{esc(ex)}</span>'
        out.append(f"<tr><td>{cell}</td></tr>")
    out.append("</table>")
    return "\n".join(out)


def render_dialog(lines):
    out = []
    for ln in lines:
        speaker, sep, rest = ln.partition(":")
        if sep and len(speaker) <= 12:
            out.append(f'<p><span class="sp">{esc(speaker)}:</span> {inline(rest.strip())}</p>')
        else:
            out.append(f"<p>{inline(ln)}</p>")
    return "\n".join(out)


def render_chapter(ch):
    body = [f"<h1>{esc(ch.title)}</h1>"]
    for kind, val in ch.parts:
        if kind == "p":
            body.append(f"<p>{inline(val)}</p>")
        elif kind == "h2":
            body.append(f"<h2>{esc(val)}</h2>")
        elif kind == "h3":
            body.append(f"<h3>{esc(val)}</h3>")
        elif kind == "quote":
            body.append(f"<blockquote><p>{inline(val)}</p></blockquote>")
        elif kind == "hr":
            body.append("<hr/>")
        elif kind == "ul":
            items = "".join(f"<li>{inline(i)}</li>" for i in val)
            body.append(f"<ul>{items}</ul>")
        elif kind == "vocab":
            body.append(render_vocab(val))
        elif kind == "dialog":
            body.append(render_dialog(val))
    return "\n".join(body)


XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><meta charset="utf-8"/><title>{title}</title>
<link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
{body}
</body></html>"""


def build(src, out_path):
    meta, chapters = parse(src)
    if not chapters:
        sys.exit(f"{src}: khong tim thay chuong nao (dong bat dau bang '# ')")

    items, refs, navs = [], [], []
    files = {}
    for i, ch in enumerate(chapters, 1):
        name = f"ch{i:02d}.xhtml"
        files[name] = XHTML.format(title=esc(ch.title), body=render_chapter(ch))
        items.append(f'<item id="c{i}" href="{name}" media-type="application/xhtml+xml"/>')
        refs.append(f'<itemref idref="c{i}"/>')
        navs.append(f'<navPoint id="c{i}" playOrder="{i}"><navLabel><text>{esc(ch.title)}'
                    f'</text></navLabel><content src="{name}"/></navPoint>')

    uid = f"urn:uuid:{abs(hash(meta['title'])) % 10**12:012d}"
    opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
<dc:title>{esc(meta['title'])}</dc:title>
<dc:creator opf:role="aut">{esc(meta.get('author', ''))}</dc:creator>
<dc:language>{esc(meta.get('lang', 'en'))}</dc:language>
<dc:identifier id="BookId">{uid}</dc:identifier>
</metadata>
<manifest>
<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
<item id="css" href="style.css" media-type="text/css"/>
{chr(10).join(items)}
</manifest>
<spine toc="ncx">
{chr(10).join(refs)}
</spine>
</package>"""

    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
<head><meta content="{uid}" name="dtb:uid"/><meta content="1" name="dtb:depth"/></head>
<docTitle><text>{esc(meta['title'])}</text></docTitle>
<navMap>
{chr(10).join(navs)}
</navMap></ncx>"""

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", CONTAINER)
        z.writestr("content.opf", opf)
        z.writestr("toc.ncx", ncx)
        z.writestr("style.css", CSS)
        for name, text in files.items():
            z.writestr(name, text)

    return meta, chapters, os.path.getsize(out_path)


def main():
    ap = argparse.ArgumentParser(description="Dung EPUB toi uu cho may doc e-ink.")
    ap.add_argument("src", nargs="+", help="file nguon .book")
    ap.add_argument("-d", "--out-dir", default="out", help="thu muc dich")
    a = ap.parse_args()

    for src in a.src:
        base = os.path.splitext(os.path.basename(src))[0]
        out = os.path.join(a.out_dir, base + ".epub")
        meta, chapters, size = build(src, out)
        print(f"{meta['title']}")
        print(f"  {len(chapters)} chương · {size/1024:.0f} KB · {out}")


if __name__ == "__main__":
    main()
