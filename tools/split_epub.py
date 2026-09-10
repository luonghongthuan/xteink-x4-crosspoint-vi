#!/usr/bin/env python3
"""Chia EPUB lon thanh nhieu tap cho Xteink X3/X4 (ESP32-C3, RAM 320KB).

Vi sao can: truyen dai kieu tien hiep (2000+ chuong) lam may het RAM khi lap chi
muc — spine va toc.ncx qua lon de giu trong bo nho. Chia nho ra thi moi tap co
chi muc vua phai, may mo duoc binh thuong.

Ngoai viec chia, script con:
  - Bo @font-face va font-family khoi CSS, de may dung font rieng cua no
    (font nhung trong sach thuong thieu glyph tieng Viet -> crash).
  - Thu nho anh bia ve dung 800px chieu cao.
  - Sinh content.opf va toc.ncx hop le cho tung tap, kem metadata series
    de may xep dung thu tu.
"""
import argparse
import html
import os
import re
import shutil
import sys
import tempfile
import zipfile
from xml.sax.saxutils import escape

CONTAINER = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
    '<rootfiles><rootfile full-path="content.opf" '
    'media-type="application/oebps-package+xml"/></rootfiles></container>'
)


def read_epub(path, workdir):
    """Giai nen EPUB, tra ve (thu muc goc noi dung, noi dung OPF)."""
    with zipfile.ZipFile(path) as z:
        z.extractall(workdir)
    cpath = os.path.join(workdir, "META-INF", "container.xml")
    if not os.path.exists(cpath):
        sys.exit("Khong tim thay META-INF/container.xml — file nay khong phai EPUB hop le")
    m = re.search(r'full-path="([^"]+)"', open(cpath, encoding="utf-8").read())
    if not m:
        sys.exit("container.xml khong khai bao rootfile")
    opf_rel = m.group(1)
    opf_path = os.path.join(workdir, opf_rel)
    base = os.path.dirname(opf_path)
    return base, open(opf_path, encoding="utf-8", errors="replace").read()


def parse_opf(opf):
    """Rut manifest, spine va metadata tu content.opf."""
    manifest = {}
    for m in re.finditer(r"<item\b([^>]*)>", opf):
        attrs = dict(re.findall(r'(\w[\w:-]*)="([^"]*)"', m.group(1)))
        if "id" in attrs and "href" in attrs:
            manifest[attrs["id"]] = (attrs["href"], attrs.get("media-type", ""))
    spine = re.findall(r'<itemref[^>]*idref="([^"]+)"', opf)

    def meta(tag):
        m = re.search(rf"<dc:{tag}[^>]*>(.*?)</dc:{tag}>", opf, re.S)
        return html.unescape(m.group(1).strip()) if m else ""

    cover_id = ""
    m = re.search(r'<meta[^>]*name="cover"[^>]*content="([^"]+)"', opf)
    if m:
        cover_id = m.group(1)
    return manifest, spine, meta("title"), meta("creator"), cover_id


def parse_ncx(base, manifest):
    """Doc tieu de chuong tu toc.ncx (href -> tieu de)."""
    ncx_href = next((h for h, mt in manifest.values()
                     if mt == "application/x-dtbncx+xml" or h.endswith(".ncx")), None)
    if not ncx_href:
        return {}
    p = os.path.join(base, ncx_href)
    if not os.path.exists(p):
        return {}
    ncx = open(p, encoding="utf-8", errors="replace").read()
    titles = {}
    for m in re.finditer(
        r"<navPoint[^>]*>\s*<navLabel>\s*<text>(.*?)</text>\s*</navLabel>\s*"
        r'<content[^>]*src="([^"]+)"', ncx, re.S):
        titles[m.group(2).split("#")[0]] = html.unescape(m.group(1).strip())
    return titles


def clean_css(base, manifest, strip_fonts=True):
    """Doc CSS, bo @font-face de may dung font rieng."""
    out = {}
    for href, mt in manifest.values():
        if mt != "text/css" and not href.endswith(".css"):
            continue
        p = os.path.join(base, href)
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8", errors="replace").read()
        if strip_fonts:
            t = re.sub(r"@font-face\s*\{[^}]*\}", "", t)
            t = re.sub(r"font-family\s*:[^;}]*;", "", t)
        out[href] = t
    return out


def shrink_cover(src, dst, height=800):
    """Thu nho bia ve `height` px. Dung Pillow neu co, khong thi chep nguyen."""
    try:
        from PIL import Image
        im = Image.open(src)
        if im.height > height:
            im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
        im.convert("RGB").save(dst, "JPEG", quality=70, optimize=True)
        return True
    except Exception:
        shutil.copy(src, dst)
        return False


def build_volume(out_path, vtitle, author, series, index, parts, titles,
                 base, css, cover_href):
    items, refs, navs = [], [], []
    for k, (cid, href) in enumerate(parts):
        items.append(f'<item id="{cid}" href="{escape(href)}" '
                     f'media-type="application/xhtml+xml"/>')
        refs.append(f'<itemref idref="{cid}"/>')
        lbl = escape(titles.get(href, href))
        navs.append(f'<navPoint id="{cid}" playOrder="{k+1}"><navLabel><text>{lbl}'
                    f'</text></navLabel><content src="{escape(href)}"/></navPoint>')

    css_items = "\n".join(
        f'<item id="css{i}" href="{escape(h)}" media-type="text/css"/>'
        for i, h in enumerate(css))
    cover_item = (f'<item id="cover" href="cover.jpg" media-type="image/jpeg"/>'
                  if cover_href else "")
    cover_meta = '<meta name="cover" content="cover"/>' if cover_href else ""

    opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
<dc:title>{escape(vtitle)}</dc:title>
<dc:creator opf:role="aut">{escape(author)}</dc:creator>
<dc:language>vi</dc:language>
<dc:identifier id="BookId">urn:uuid:vol-{index:03d}-{abs(hash(series)) % 10**8}</dc:identifier>
<meta name="calibre:series" content="{escape(series)}"/>
<meta name="calibre:series_index" content="{index}"/>
{cover_meta}
</metadata>
<manifest>
<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
{cover_item}
{css_items}
{chr(10).join(items)}
</manifest>
<spine toc="ncx">
{chr(10).join(refs)}
</spine>
</package>'''

    ncx = f'''<?xml version="1.0" encoding="utf-8"?>
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
<head><meta content="urn:uuid:vol-{index:03d}" name="dtb:uid"/>
<meta content="1" name="dtb:depth"/></head>
<docTitle><text>{escape(vtitle)}</text></docTitle>
<navMap>
{chr(10).join(navs)}
</navMap></ncx>'''

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", CONTAINER)
        z.writestr("content.opf", opf)
        z.writestr("toc.ncx", ncx)
        if cover_href:
            z.write(cover_href, "cover.jpg")
        for href, text in css.items():
            z.writestr(href, text)
        for cid, href in parts:
            src = os.path.join(base, href)
            if os.path.exists(src):
                z.write(src, href)


def main():
    ap = argparse.ArgumentParser(
        description="Chia EPUB lon thanh nhieu tap cho Xteink X3/X4.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""vi du:
  %(prog)s truyen.epub                        # chia thanh 10 tap
  %(prog)s truyen.epub --volumes 20           # chia thanh 20 tap
  %(prog)s truyen.epub --chapters 250         # moi tap 250 chuong
  %(prog)s truyen.epub -d /Volumes/XTEINK/book/Tien\\ Hiep/""")
    ap.add_argument("src", help="file EPUB nguon")
    ap.add_argument("-d", "--out-dir", default="out", help="thu muc dich (mac dinh: out)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--volumes", type=int, help="chia thanh bao nhieu tap (mac dinh 10)")
    g.add_argument("--chapters", type=int, help="moi tap bao nhieu chuong")
    ap.add_argument("--title", help="ten bo truyen (mac dinh: lay tu EPUB)")
    ap.add_argument("--author", help="tac gia (mac dinh: lay tu EPUB)")
    ap.add_argument("--keep-fonts", action="store_true",
                    help="giu @font-face trong CSS (mac dinh bo di)")
    a = ap.parse_args()

    if not os.path.exists(a.src):
        sys.exit(f"Khong thay file: {a.src}")

    work = tempfile.mkdtemp(prefix="split_epub_")
    try:
        base, opf = read_epub(a.src, work)
        manifest, spine, title, author, cover_id = parse_opf(opf)
        titles = parse_ncx(base, manifest)

        series = a.title or title or os.path.splitext(os.path.basename(a.src))[0]
        author = a.author or author or "?"

        chapters = [(i, manifest[i][0]) for i in spine
                    if i in manifest and "html" in manifest[i][1].lower()]
        if not chapters:
            sys.exit("Khong doc duoc chuong nao tu spine")

        if a.chapters:
            per = a.chapters
            nvol = (len(chapters) + per - 1) // per
        else:
            nvol = a.volumes or 10
            per = (len(chapters) + nvol - 1) // nvol

        print(f'"{series}" — {author}')
        print(f"{len(chapters)} chuong, tieu de doc duoc {len(titles)}")
        print(f"chia thanh {nvol} tap, moi tap ~{per} chuong\n")

        os.makedirs(a.out_dir, exist_ok=True)
        css = clean_css(base, manifest, strip_fonts=not a.keep_fonts)
        if css:
            print(f"CSS: {len(css)} file"
                  f"{'' if a.keep_fonts else ', da bo @font-face'}")

        cover = ""
        if cover_id and cover_id in manifest:
            csrc = os.path.join(base, manifest[cover_id][0])
            if os.path.exists(csrc):
                cover = os.path.join(work, "cover.jpg")
                used_pil = shrink_cover(csrc, cover)
                print(f"bia: {os.path.getsize(csrc)/1024:.0f} KB -> "
                      f"{os.path.getsize(cover)/1024:.0f} KB"
                      f"{'' if used_pil else ' (khong co Pillow, chep nguyen)'}")
        print()

        total = 0
        for v in range(nvol):
            part = chapters[v * per:(v + 1) * per]
            if not part:
                continue
            n = v + 1
            vtitle = f"{series} - Tập {n:02d}"
            out_path = os.path.join(a.out_dir, f"{vtitle}.epub")
            build_volume(out_path, vtitle, author, series, n, part, titles,
                         base, css, cover)
            size = os.path.getsize(out_path)
            total += size
            first = titles.get(part[0][1], "?")
            last = titles.get(part[-1][1], "?")
            print(f"Tập {n:02d}: {len(part):>4} chương | {size/1048576:5.1f} MB")
            print(f"         {first}  →  {last}")

        print(f"\n{nvol} tập, tổng {total/1048576:.1f} MB "
              f"(gốc {os.path.getsize(a.src)/1048576:.1f} MB)")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
