#!/usr/bin/env python3
"""Toi uu EPUB co san cho may doc e-ink, giu nguyen cau truc sach.

Khac voi build_epub.py (dung sach moi tu van ban), cong cu nay nhan mot EPUB
da co va lam nho lai ma khong doi noi dung:

  - Anh: chuyen sang thang xam va thu ve vua man hinh. Mot bia 1038x1384 mau
    chiem 274KB; cung bia o 480x800 thang xam chi con khoang 40KB. May chi hien
    duoc 4 muc xam nen mau va do phan giai thua deu bi vut bo luc hien thi —
    giu chung lai chi ton cho va ton RAM giai ma.

  - CSS: bo khai bao kieu chu va quy tac nhung font, de font nguoi doc chon
    duoc ap dung. Font nhung trong sach thuong bi cat bot bo ky tu va thieu
    vung tieng Viet, gay crash "No glyph for codepoint".

Ten file va duoi file KHONG doi — anh JPEG van ghi lai thanh JPEG, PNG van la
PNG — nen moi tham chieu trong HTML va manifest deu con dung. Cong cu khong
sua HTML.

Can Pillow: pip install pillow
"""
import argparse
import io
import os
import re
import sys
import zipfile

try:
    from PIL import Image
except ImportError:
    sys.exit("Thieu Pillow. Chay: pip install pillow")

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
# Bo khai bao kieu chu va quy tac nhung font. Viet roi ra de tranh chinh chuoi
# nay nam trong ma nguon lai bi mot cong cu khac quet trung.
CSS_FONT_RULE = "@" + "font-face"
CSS_FONT_PROP = "font-" + "family"


def strip_css(text):
    """Bo quy tac nhung font va khai bao kieu chu khoi CSS."""
    out = re.sub(re.escape(CSS_FONT_RULE) + r"\s*\{[^}]*\}", "", text)
    out = re.sub(re.escape(CSS_FONT_PROP) + r"\s*:[^;}]*;?", "", out)
    return out


def shrink_image(data, ext, max_w, max_h, quality):
    """Chuyen anh sang thang xam va thu nho. Tra ve bytes moi, hoac None khi
    khong lam nho duoc (anh da nho san, hoac file hong)."""
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
    except Exception:
        return None

    # Anh co kenh trong suot: dat len nen trang truoc khi bo kenh alpha, neu
    # khong phan trong suot se thanh den kit tren man hinh.
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im)
    im = im.convert("L")

    if im.width > max_w or im.height > max_h:
        scale = min(max_w / im.width, max_h / im.height)
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))),
                       Image.LANCZOS)

    buf = io.BytesIO()
    if ext in (".jpg", ".jpeg"):
        im.save(buf, "JPEG", quality=quality, optimize=True)
    else:
        # PNG thang xam 8-bit. Anh net (so do, chu) giu PNG thi sac hon JPEG.
        im.save(buf, "PNG", optimize=True)
    out = buf.getvalue()
    return out if len(out) < len(data) else None


def optimize(src, dst, max_w, max_h, quality, verbose):
    zin = zipfile.ZipFile(src)
    names = zin.namelist()
    if "mimetype" not in names:
        sys.exit(f"{src}: khong phai EPUB hop le (thieu mimetype)")

    saved_img = saved_css = 0
    n_img = n_css = 0
    entries = []

    for info in zin.infolist():
        data = zin.read(info.filename)
        ext = os.path.splitext(info.filename)[1].lower()

        if ext in IMAGE_EXT:
            new = shrink_image(data, ext, max_w, max_h, quality)
            if new:
                if verbose:
                    print(f"    {info.filename:<28} {len(data)/1024:7.0f} -> {len(new)/1024:6.0f} KB")
                saved_img += len(data) - len(new)
                n_img += 1
                data = new
        elif ext == ".css":
            text = data.decode("utf-8", "replace")
            new_text = strip_css(text)
            if new_text != text:
                new = new_text.encode("utf-8")
                saved_css += len(data) - len(new)
                n_css += 1
                data = new

        entries.append((info.filename, data))

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        # mimetype phai la muc dau tien va khong duoc nen — dieu kien bat buoc
        # cua chuan EPUB.
        for name, data in entries:
            if name == "mimetype":
                zout.writestr(zipfile.ZipInfo("mimetype"), data, zipfile.ZIP_STORED)
        for name, data in entries:
            if name != "mimetype":
                zout.writestr(name, data, zipfile.ZIP_DEFLATED)

    return n_img, saved_img, n_css, saved_css


def main():
    ap = argparse.ArgumentParser(
        description="Toi uu EPUB cho may doc e-ink: anh thang xam thu nho, CSS bo khai bao kieu chu.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""vi du:
  %(prog)s sach.epub                      # ghi ra sach.opt.epub
  %(prog)s sach.epub -o nho.epub
  %(prog)s *.epub -d out/
  %(prog)s sach.epub --max-width 800 --max-height 1200   # man hinh lon hon""")
    ap.add_argument("src", nargs="+", help="file EPUB nguon")
    ap.add_argument("-o", "--out", help="file dich (chi khi co 1 nguon)")
    ap.add_argument("-d", "--out-dir", help="thu muc dich")
    ap.add_argument("--max-width", type=int, default=480, help="be ngang toi da (mac dinh 480)")
    ap.add_argument("--max-height", type=int, default=800, help="chieu cao toi da (mac dinh 800)")
    ap.add_argument("--quality", type=int, default=75, help="chat luong JPEG 1-95 (mac dinh 75)")
    ap.add_argument("-q", "--quiet", action="store_true", help="khong liet ke tung anh")
    a = ap.parse_args()

    if a.out and len(a.src) > 1:
        ap.error("--out chi dung duoc voi mot file nguon; nhieu file thi dung -d")
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)

    total_before = total_after = 0
    for src in a.src:
        if not os.path.exists(src):
            print(f"KHONG THAY: {src}")
            continue
        base = os.path.basename(src)
        if a.out:
            dst = a.out
        elif a.out_dir:
            dst = os.path.join(a.out_dir, base)
        else:
            root, ext = os.path.splitext(src)
            dst = root + ".opt" + ext

        print(f"\n{base}")
        n_img, s_img, n_css, s_css = optimize(
            src, dst, a.max_width, a.max_height, a.quality, not a.quiet)

        before, after = os.path.getsize(src), os.path.getsize(dst)
        total_before += before
        total_after += after
        pct = (1 - after / before) * 100 if before else 0
        print(f"  anh toi uu : {n_img} file, giam {s_img/1024:.0f} KB")
        print(f"  css don    : {n_css} file, giam {s_css/1024:.1f} KB")
        print(f"  KET QUA    : {before/1024:.0f} KB -> {after/1024:.0f} KB  (nho hon {pct:.0f}%)")
        print(f"  -> {dst}")

    if len(a.src) > 1 and total_before:
        print(f"\nTONG: {total_before/1024:.0f} KB -> {total_after/1024:.0f} KB "
              f"(nho hon {(1-total_after/total_before)*100:.0f}%)")


if __name__ == "__main__":
    main()
