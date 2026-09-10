#!/usr/bin/env python3
"""Chuyen anh chup mau -> hinh nen ngu Xteink X4 (480x800, 4 muc xam).

Vi sao phai lam nhieu buoc the nay: man hinh chi co 4 muc xam (firmware
SleepActivity.cpp quantizeOverlayLum = lum >> 6 -> 0/85/170/255). Neu chi
chuyen thang sang xam roi dither, mat nguoi se bet thanh mot mang trang hoac
mot mang den. Nen phai keo tuong phan CUC BO truoc (CLAHE) de tung khuon mat
tu co dai sang rieng, roi moi dither.

Thu tu: xam -> CLAHE -> unsharp -> cat khung -> thu nho -> S-curve -> dither.
"""
import numpy as np
from PIL import Image, ImageFilter
import os, sys

W, H = 480, 800
LEVELS = np.array([0, 85, 170, 255], dtype=np.float64)


def to_gray(img):
    a = np.asarray(img.convert("RGB"), dtype=np.float64)
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def clahe(g, tiles=(8, 6), clip=2.5, bins=256):
    """Contrast Limited Adaptive Histogram Equalization.

    Chia anh thanh luoi o, can bang histogram tung o (co gioi han clip de khong
    khuech dai nhieu), roi noi suy song tuyen tinh giua cac o de khong bi ranh o.
    """
    h, w = g.shape
    ty, tx = tiles[1], tiles[0]
    th, tw = int(np.ceil(h / ty)), int(np.ceil(w / tx))
    maps = np.zeros((ty, tx, bins), dtype=np.float64)

    for i in range(ty):
        for j in range(tx):
            blk = g[i * th:(i + 1) * th, j * tw:(j + 1) * tw]
            if blk.size == 0:
                maps[i, j] = np.arange(bins)
                continue
            hist, _ = np.histogram(blk, bins=bins, range=(0, 255))
            limit = max(1.0, clip * blk.size / bins)
            excess = np.maximum(hist - limit, 0).sum()
            hist = np.minimum(hist, limit) + excess / bins  # phan bo lai phan bi cat
            cdf = np.cumsum(hist)
            cdf = (cdf - cdf[0]) / max(cdf[-1] - cdf[0], 1e-9) * 255.0
            maps[i, j] = cdf

    # toa do tam moi o, de noi suy
    cy = (np.arange(ty) + 0.5) * th
    cx = (np.arange(tx) + 0.5) * tw
    yy = np.arange(h)[:, None]
    xx = np.arange(w)[None, :]

    iy = np.clip(np.searchsorted(cy, yy.ravel()) - 1, 0, ty - 2)
    ix = np.clip(np.searchsorted(cx, xx.ravel()) - 1, 0, tx - 2)
    fy = np.clip((yy.ravel() - cy[iy]) / (cy[iy + 1] - cy[iy]), 0, 1)[:, None]
    fx = np.clip((xx.ravel() - cx[ix]) / (cx[ix + 1] - cx[ix]), 0, 1)[None, :]

    idx = np.clip(g.astype(np.int32), 0, bins - 1)
    r0 = maps[iy][:, ix]            # (h, w, bins) -> lay theo o tren-trai
    def take(a, b):
        return np.take_along_axis(maps[np.ix_(a, b)], idx[..., None], axis=2)[..., 0]

    q11 = take(iy, ix)
    q12 = take(iy, ix + 1)
    q21 = take(iy + 1, ix)
    q22 = take(iy + 1, ix + 1)
    top = q11 * (1 - fx) + q12 * fx
    bot = q21 * (1 - fx) + q22 * fx
    return top * (1 - fy) + bot * fy


def unsharp(g, radius=2.2, amount=0.85):
    im = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "L")
    blur = np.asarray(im.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float64)
    return g + amount * (g - blur)


def s_curve(g, strength=0.30):
    """Keo sang len sang, toi xuong toi — bu lai viec chi con 4 muc."""
    x = g / 255.0
    y = x + strength * np.sin(2 * np.pi * x) / (2 * np.pi) * -1
    y = np.clip(y, 0, 1)
    return y * 255.0


def crop_resize(g, focal_x=0.5, focal_y=0.5):
    h, w = g.shape
    target = W / H  # 0.6
    if w / h > target:                       # anh rong hon khung -> cat be ngang
        nw = int(round(h * target))
        x0 = int(round((w - nw) * np.clip(focal_x, 0, 1)))
        x0 = max(0, min(x0, w - nw))
        g = g[:, x0:x0 + nw]
    else:                                    # anh cao hon khung -> cat bot chieu cao
        nh = int(round(w / target))
        y0 = int(round((h - nh) * np.clip(focal_y, 0, 1)))
        y0 = max(0, min(y0, h - nh))
        g = g[y0:y0 + nh, :]
    im = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "L")
    return np.asarray(im.resize((W, H), Image.LANCZOS), dtype=np.float64)


def floyd_steinberg(arr):
    a = arr.astype(np.float64).copy()
    h, w = a.shape
    for y in range(h):
        row = a[y]
        for x in range(w):
            old = row[x]
            new = LEVELS[np.argmin(np.abs(LEVELS - old))]
            row[x] = new
            err = old - new
            if x + 1 < w:
                row[x + 1] += err * 7 / 16
            if y + 1 < h:
                nxt = a[y + 1]
                if x > 0:
                    nxt[x - 1] += err * 3 / 16
                nxt[x] += err * 5 / 16
                if x + 1 < w:
                    nxt[x + 1] += err * 1 / 16
    return np.clip(a, 0, 255).astype(np.uint8)


def pre_crop(g, left=0.0, right=0.0, top=0.0, bottom=0.0):
    """Cat thô theo ti le truoc khi xu ly — dung de bo watermark hoac vien thua."""
    h, w = g.shape
    return g[int(h * top):h - int(h * bottom), int(w * left):w - int(w * right)]


def convert(src, dst, focal_x=0.5, focal_y=0.5, clip=2.5, sharp=0.85, scurve=0.30, pre=None):
    g = to_gray(Image.open(src))
    if pre:
        g = pre_crop(g, **pre)
    g = clahe(g, clip=clip)
    g = unsharp(g, amount=sharp)
    g = crop_resize(g, focal_x, focal_y)
    g = s_curve(g, scurve)
    d = floyd_steinberg(g)
    Image.fromarray(d, "L").convert("RGB").save(dst, format="BMP")
    return d




def main():
    import argparse
    ap = argparse.ArgumentParser(
        description="Chuyen anh sang hinh nen ngu Xteink X3/X4 (480x800, 4 muc xam).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""vi du:
  %(prog)s anh.jpg
  %(prog)s anh.jpg -o nen.bmp --focal-x 0.7
  %(prog)s *.jpg -d sleep/ --clip 3.0 --sharp 1.0
  %(prog)s anh.jpg --pre-top 0.05 --pre-bottom 0.08   # cat bo watermark

meo chinh:
  --focal-x   0=sat trai, 1=sat phai. Dung khi anh ngang bi cat mat nguoi.
  --clip      Cao hon = tuong phan cuc bo manh hon, mat ro hon nhung nhieu hon.
  --scurve    Cao hon = do tuong phan tong the manh hon.""")
    ap.add_argument("src", nargs="+", help="anh nguon (jpg/png/...)")
    ap.add_argument("-o", "--out", help="file dich (chi khi co 1 anh nguon)")
    ap.add_argument("-d", "--out-dir", default=".", help="thu muc dich (mac dinh: .)")
    ap.add_argument("--focal-x", type=float, default=0.5, help="tam cat ngang 0..1 (mac dinh 0.5)")
    ap.add_argument("--focal-y", type=float, default=0.5, help="tam cat doc 0..1 (mac dinh 0.5)")
    ap.add_argument("--clip", type=float, default=2.5, help="gioi han CLAHE (mac dinh 2.5)")
    ap.add_argument("--sharp", type=float, default=0.85, help="do net unsharp (mac dinh 0.85)")
    ap.add_argument("--scurve", type=float, default=0.30, help="do cong S-curve (mac dinh 0.30)")
    for e in ("left", "right", "top", "bottom"):
        ap.add_argument(f"--pre-{e}", type=float, default=0.0,
                        help=f"cat tho {e} theo ti le 0..1 truoc khi xu ly")
    a = ap.parse_args()

    if a.out and len(a.src) > 1:
        ap.error("--out chi dung duoc khi co dung 1 anh nguon; nhieu anh thi dung -d")

    pre = {k: getattr(a, f"pre_{k}") for k in ("left", "right", "top", "bottom")}
    pre = pre if any(pre.values()) else None
    os.makedirs(a.out_dir, exist_ok=True)

    for src in a.src:
        dst = a.out or os.path.join(
            a.out_dir, os.path.splitext(os.path.basename(src))[0] + ".bmp")
        d = convert(src, dst, a.focal_x, a.focal_y, a.clip, a.sharp, a.scurve, pre)
        print(f"{os.path.basename(dst):<28} {os.path.getsize(dst)/1024:6.0f} KB  "
              f"muc xam={sorted(np.unique(d).tolist())}")


if __name__ == "__main__":
    main()
