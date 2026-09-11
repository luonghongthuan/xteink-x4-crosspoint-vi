#!/usr/bin/env python3
"""Chuyen truyen tranh (CBZ / thu muc anh) thanh file XTC cho Xteink X4.

Vi sao XTC chu khong phai EPUB: truyen tranh trong EPUB bat may giai ma
JPEG/PNG tung trang — tren con chip 320KB RAM viec do cham va de can bo nho.
XTC la dinh dang trang RENDER SAN cua chinh firmware: moi trang la bitmap
480x800 dung 4 muc xam cua man hinh, may chi viec chep vao framebuffer.
Lat trang gan nhu tuc thi, ton RAM co dinh ~96KB bat ke truyen dai bao nhieu.

Dac ta format lay truc tiep tu ma nguon firmware (lib/Xtc/Xtc/XtcTypes.h va
XtcReaderActivity.cpp):

  - File:  header 56 byte (magic "XTCH" cho 2-bit) + bang trang 16 byte/trang
           + du lieu trang.
  - Trang: header XTH 22 byte + hai bit-plane, MOI PLANE (w*h+7)/8 byte,
           xep THEO COT tu PHAI sang TRAI (cot luu thu i ung voi x = w-1-i),
           moi byte la 8 diem doc, bit cao nhat la diem tren cung.
  - Gia tri diem = (bit1<<1)|bit2:  0=trang, 1=xam nhat, 2=xam dam, 3=den.

Che do --bw ghi "XTC\\0"/XTG 1-bit (bit 1 = TRANG, theo reader), xep theo HANG, MSB truoc —
file nho hon mot nua, hop truyen net thuan khong co tram (screentone).

Can Pillow: pip install pillow
"""
import argparse
import io
import os
import re
import struct
import sys
import zipfile

try:
    from PIL import Image, ImageFilter, ImageOps
except ImportError:
    sys.exit("Thieu Pillow. Chay: pip install pillow")

W, H = 480, 800
XTCH_MAGIC = 0x48435458  # "XTCH"
XTC_MAGIC = 0x00435458   # "XTC\0"
XTH_MAGIC = 0x00485458   # "XTH\0"
XTG_MAGIC = 0x00475458   # "XTG\0"
FILE_HEADER = 56
PAGE_ENTRY = 16
PAGE_HEADER = 22
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")

# Nguong luong tu 4 muc: diem anh dithered chi mang dung {0,85,170,255}.
LEVELS = (0, 85, 170, 255)


def natural_key(name):
    """'p2.jpg' dung truoc 'p10.jpg' — thu tu trang phai theo so, khong theo chuoi."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def collect_pages(src):
    """Tra ve danh sach (ten, bytes anh) theo thu tu doc."""
    if os.path.isdir(src):
        names = [n for n in os.listdir(src) if n.lower().endswith(IMAGE_EXT) and not n.startswith(".")]
        names.sort(key=natural_key)
        return [(n, open(os.path.join(src, n), "rb").read()) for n in names]
    if src.lower().endswith((".cbz", ".zip")):
        z = zipfile.ZipFile(src)
        names = [n for n in z.namelist()
                 if n.lower().endswith(IMAGE_EXT) and not os.path.basename(n).startswith(("._", "."))]
        names.sort(key=natural_key)
        return [(n, z.read(n)) for n in names]
    if src.lower().endswith(IMAGE_EXT):
        return [(os.path.basename(src), open(src, "rb").read())]
    sys.exit(f"Khong biet doc: {src} (nhan CBZ/ZIP, thu muc anh, hoac anh le)")


def prepare(im, sharp):
    """Xam + tu can tuong phan + vua khung 480x800 tren nen trang."""
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im)
    im = im.convert("L")
    # Scan truyen hay xam xin; cat 1% hai dau histogram keo lai trang/den that.
    im = ImageOps.autocontrast(im, cutoff=1)
    scale = min(W / im.width, H / im.height)
    nw, nh = max(1, round(im.width * scale)), max(1, round(im.height * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    if sharp > 0:
        im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=int(sharp * 100), threshold=2))
    page = Image.new("L", (W, H), 255)
    page.paste(im, ((W - nw) // 2, (H - nh) // 2))
    return page


def dither(im, levels):
    """Floyd-Steinberg ve `levels` muc xam deu nhau. Tra ve bytes gia tri gray."""
    px = bytearray(im.tobytes())
    err = [0.0] * (W + 2)
    nxt = [0.0] * (W + 2)
    out = bytearray(W * H)
    step = 255 / (levels - 1)
    for y in range(H):
        row = y * W
        cur, err = err, nxt
        nxt = [0.0] * (W + 2)
        for x in range(W):
            old = px[row + x] + cur[x + 1]
            q = min(levels - 1, max(0, int(old / step + 0.5)))
            new = q * step
            out[row + x] = int(new + 0.5)
            e = old - new
            cur[x + 2] += e * 7 / 16
            nxt[x] += e * 3 / 16
            nxt[x + 1] += e * 5 / 16
            nxt[x + 2] += e * 1 / 16
        err = cur
        err, nxt = nxt, err  # giu dung hang loi cho dong ke tiep
    return bytes(out)


def pack_xth(gray):
    """Gray {0,85,170,255} -> hai bit-plane theo dac ta renderer.

    pv = 3 - gray//85  (0=trang..3=den); cot luu thu i la x = W-1-i;
    100 byte moi cot moi plane; bit 7-(y%8) la diem y trong byte y//8.
    """
    col_bytes = (H + 7) // 8
    plane_size = (W * H + 7) // 8
    p1 = bytearray(plane_size)
    p2 = bytearray(plane_size)
    for i in range(W):
        x = W - 1 - i
        base = i * col_bytes
        for y in range(H):
            pv = 3 - gray[y * W + x] // 85
            if pv:
                bit = 1 << (7 - (y & 7))
                off = base + (y >> 3)
                if pv & 2:
                    p1[off] |= bit
                if pv & 1:
                    p2[off] |= bit
    return bytes(p1) + bytes(p2)


def pack_xtg(gray):
    """Gray {0,255} -> 1-bit theo hang, MSB truoc.

    Reader dat isBlack = !bit (XtcReaderActivity.cpp): bit 1 = TRANG, bit 0 = DEN.
    Nen SET bit o diem trang, de o 0 cho diem den."""
    row_bytes = (W + 7) // 8
    out = bytearray(row_bytes * H)
    for y in range(H):
        base = y * row_bytes
        row = y * W
        for x in range(W):
            if gray[row + x] >= 128:  # diem trang -> bit 1
                out[base + (x >> 3)] |= 1 << (7 - (x & 7))
    return bytes(out)


def build_xtc(pages_raw, out_path, bw, sharp, split_wide, rtl, quiet):
    blobs = []
    for idx, (name, data) in enumerate(pages_raw, 1):
        try:
            im = Image.open(io.BytesIO(data))
            im.load()
        except Exception as e:
            print(f"  BO QUA {name}: {e}")
            continue
        halves = [im]
        if split_wide and im.width > im.height:
            mid = im.width // 2
            left, right = im.crop((0, 0, mid, im.height)), im.crop((mid, 0, im.width, im.height))
            # Manga doc phai-sang-trai: nua PHAI la trang truoc.
            halves = [right, left] if rtl else [left, right]
        for half in halves:
            page = prepare(half, sharp)
            if bw:
                blobs.append(pack_xtg(dither(page, 2)))
            else:
                blobs.append(pack_xth(dither(page, 4)))
        if not quiet:
            print(f"  trang {idx}/{len(pages_raw)}: {name}" + (" (tach doi)" if len(halves) == 2 else ""))

    if not blobs:
        sys.exit("Khong co trang nao dung duoc")

    n = len(blobs)
    page_magic = XTG_MAGIC if bw else XTH_MAGIC
    file_magic = XTC_MAGIC if bw else XTCH_MAGIC
    data_start = FILE_HEADER + PAGE_ENTRY * n

    with open(out_path, "wb") as f:
        f.write(struct.pack("<IBBHBBBBIQQQQII",
                            file_magic, 1, 0, n,
                            0,          # readDirection (reader hien bo qua)
                            0, 0, 0,    # metadata / thumbnails / chapters
                            1,          # currentPage (1-based)
                            0,          # metadataOffset
                            FILE_HEADER,  # pageTableOffset
                            data_start,   # dataOffset
                            0,            # thumbOffset
                            0, 0))        # chapterOffset + padding
        off = data_start
        for blob in blobs:
            f.write(struct.pack("<QIHH", off, PAGE_HEADER + len(blob), W, H))
            off += PAGE_HEADER + len(blob)
        for blob in blobs:
            f.write(struct.pack("<IHHBBIQ", page_magic, W, H, 0, 0, len(blob), 0))
            f.write(blob)
    return n, os.path.getsize(out_path)


def main():
    ap = argparse.ArgumentParser(
        description="Chuyen truyen tranh (CBZ/thu muc anh) thanh XTC render san cho Xteink X4.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""vi du:
  %(prog)s Doraemon-tap-01.cbz
  %(prog)s thu-muc-anh/ -o "Truyen.xtc"
  %(prog)s manga.cbz --split-wide --rtl      # trang doi cua manga, doc phai->trai
  %(prog)s line-art.cbz --bw                 # net thuan: 1-bit, file nho mot nua

Che do mac dinh (2-bit) giu duoc tram xam cua truyen. Chep file .xtc vao
thu muc book/ tren the — may nhan no nhu mot cuon sach binh thuong.""")
    ap.add_argument("src", nargs="+", help="file .cbz/.zip, thu muc anh, hoac anh le")
    ap.add_argument("-o", "--out", help="file .xtc dich (chi khi co 1 nguon)")
    ap.add_argument("-d", "--out-dir", default=".", help="thu muc dich (mac dinh: .)")
    ap.add_argument("--bw", action="store_true", help="1-bit trang/den (XTG) — cho net thuan")
    ap.add_argument("--sharp", type=float, default=0.6, help="do net 0..2 (mac dinh 0.6)")
    ap.add_argument("--split-wide", action="store_true", help="tach trang ngang thanh hai trang doc")
    ap.add_argument("--rtl", action="store_true", help="khi tach trang doi: nua phai truoc (manga)")
    ap.add_argument("-q", "--quiet", action="store_true")
    a = ap.parse_args()

    if a.out and len(a.src) > 1:
        ap.error("--out chi dung voi mot nguon; nhieu nguon dung -d")
    os.makedirs(a.out_dir, exist_ok=True)

    for src in a.src:
        pages = collect_pages(src)
        base = os.path.splitext(os.path.basename(src.rstrip("/")))[0]
        out = a.out or os.path.join(a.out_dir, base + ".xtc")
        print(f"{base}: {len(pages)} anh nguon")
        n, size = build_xtc(pages, out, a.bw, a.sharp, a.split_wide, a.rtl, a.quiet)
        print(f"  -> {out}: {n} trang, {size / 1048576:.1f} MB "
              f"({'1-bit' if a.bw else '2-bit, 4 muc xam'})")


if __name__ == "__main__":
    main()
