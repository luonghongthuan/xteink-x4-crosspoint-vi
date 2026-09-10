#!/usr/bin/env python3
"""Sinh hinh nen ngu + overlay trong suot cho Xteink X4 (CrossPoint 1.6.0).

Rang buoc phan cung, doc tu ma nguon firmware:
  - Man hinh 480x800, 4 muc xam. SleepActivity.cpp quantizeOverlayLum() = lum >> 6,
    va Bitmap "native-palette path" anh xa 0 / 85 / 170 / 255 -> muc 0..3.
    => phai dither ve dung 4 gia tri do, khong phai 256.
  - Anh nen toan man hinh: BMP 24-bit, khong nen, de trong /sleep
  - Anh overlay trong suot: BMP 32-bit BGRA (SleepActivity.cpp:187 tu choi bpp != 32),
    de trong /.sleep-overlay
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os, struct

W, H = 480, 800
LEVELS = np.array([0, 85, 170, 255], dtype=np.float64)
OUT = os.path.dirname(os.path.abspath(__file__))
SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SERIF_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"


def floyd_steinberg(arr):
    """Dither anh xam float [0,255] ve 4 muc, lan truyen sai so Floyd-Steinberg."""
    a = arr.astype(np.float64).copy()
    h, w = a.shape
    for y in range(h):
        for x in range(w):
            old = a[y, x]
            new = LEVELS[np.argmin(np.abs(LEVELS - old))]
            a[y, x] = new
            err = old - new
            if x + 1 < w:
                a[y, x + 1] += err * 7 / 16
            if y + 1 < h:
                if x > 0:
                    a[y + 1, x - 1] += err * 3 / 16
                a[y + 1, x] += err * 5 / 16
                if x + 1 < w:
                    a[y + 1, x + 1] += err * 1 / 16
    return np.clip(a, 0, 255).astype(np.uint8)


def save_bmp24(gray_u8, path):
    """BMP 24-bit khong nen (bottom-up), dung cho /sleep."""
    Image.fromarray(gray_u8, mode="L").convert("RGB").save(path, format="BMP")


def save_bmp32_bgra(gray_u8, alpha_u8, path):
    """BMP 32-bit BGRA thu cong: Pillow khong ghi 32-bit co alpha cho BMP.
    Header 54 byte (BITMAPINFOHEADER, BI_RGB), du lieu bottom-up."""
    h, w = gray_u8.shape
    px = np.zeros((h, w, 4), dtype=np.uint8)
    px[..., 0] = gray_u8  # B
    px[..., 1] = gray_u8  # G
    px[..., 2] = gray_u8  # R
    px[..., 3] = alpha_u8  # A
    px = np.flipud(px)  # BMP luu tu duoi len
    data = px.tobytes()
    hdr = struct.pack(
        "<2sIHHIIiiHHIIiiII",
        b"BM", 54 + len(data), 0, 0, 54,
        40, w, h, 1, 32, 0, len(data), 2835, 2835, 0, 0,
    )
    with open(path, "wb") as f:
        f.write(hdr)
        f.write(data)


def linear_gradient_bg(top=255, bottom=225):
    y = np.linspace(top, bottom, H)[:, None]
    return np.repeat(y, W, axis=1)


# ── 1. Trang tren nui ────────────────────────────────────────────────────────
def wall_moon():
    """Nhieu khoang trang, mot khoi den manh — kieu hop e-ink nhat, va hop
    khong khi truyen tien hiep."""
    img = Image.fromarray(linear_gradient_bg(255, 236).astype(np.uint8), "L")
    d = ImageDraw.Draw(img)

    cx, cy, r = W * 0.5, H * 0.34, 96
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255, outline=0, width=3)
    # vet khuyet nhe cho mat trang khong bi phang
    for ox, oy, rr, fl in [(-34, -22, 17, 235), (26, 14, 12, 240), (-8, 38, 9, 238)]:
        d.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], fill=fl)

    # ba lop nui, lop xa nhat nhat nhat
    layers = [(H * 0.60, [(-40, 0), (110, -78), (230, -18), (360, -96), (520, 0)], 200),
              (H * 0.70, [(-40, 0), (90, -104), (215, -34), (330, -122), (520, 0)], 120),
              (H * 0.80, [(-40, 0), (140, -128), (290, -46), (400, -100), (520, 0)], 20)]
    for base, pts, fill in layers:
        poly = [(x, base + dy) for x, dy in pts] + [(W + 40, H + 40), (-40, H + 40)]
        d.polygon(poly, fill=fill)

    # mat nuoc: vai duong ke ngang thua dan
    for i in range(7):
        y = H * 0.855 + i * 15
        inset = 60 + i * 26
        d.line([inset, y, W - inset, y], fill=255, width=2)
    return np.asarray(img).astype(np.float64)


# ── 2. Chong sach (line art) ─────────────────────────────────────────────────
def wall_books():
    img = Image.fromarray(linear_gradient_bg(252, 232).astype(np.uint8), "L")
    d = ImageDraw.Draw(img)
    base_y, x0, x1 = 610, 96, 384
    spines = [(52, 18, 0), (40, 150, 26), (60, 60, 14), (34, 210, 34), (46, 100, 6)]
    y = base_y
    for i, (th, fill, inset) in enumerate(spines):
        y -= th
        left, right = x0 + inset, x1 - inset
        d.rounded_rectangle([left, y, right, y + th - 7], radius=4, fill=fill, outline=0, width=2)
        d.line([left + 16, y + th // 2 - 3, right - 16, y + th // 2 - 3],
               fill=255 if fill < 128 else 90, width=2)
    d.line([x0 - 26, base_y + 5, x1 + 26, base_y + 5], fill=0, width=3)
    for k in range(3):  # bong do thua dan
        d.line([x0 - 26 + k * 9, base_y + 14 + k * 7, x1 + 26 - k * 9, base_y + 14 + k * 7],
               fill=150 + k * 30, width=2)
    return np.asarray(img).astype(np.float64)


# ── 3. Chu toi gian ──────────────────────────────────────────────────────────
def wall_type():
    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)
    d.rectangle([34, 34, W - 35, H - 35], outline=0, width=3)
    d.rectangle([46, 46, W - 47, H - 47], outline=170, width=1)
    f_big = ImageFont.truetype(SERIF_B, 92)
    f_sub = ImageFont.truetype(SERIF, 27)
    for text, font, y, fill in [("Đọc", f_big, 300, 0), ("mở một cánh cửa", f_sub, 430, 60)]:
        bb = d.textbbox((0, 0), text, font=font)
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y), text, font=font, fill=fill)
    d.line([W / 2 - 64, 400, W / 2 + 64, 400], fill=0, width=2)
    return np.asarray(img).astype(np.float64)


# ── 4. Hoa van hinh thoi ─────────────────────────────────────────────────────
def wall_pattern():
    """O tram thua, net rat nhat: du de co ket cau ma khong lam man hinh bi bet
    hay de lai bong mo sau khi thoat ngu."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    p = 80.0  # o lon gap doi ban truoc
    dia = np.abs(((xx / p) % 1) - 0.5) + np.abs(((yy / p) % 1) - 0.5)
    g = np.where(np.abs(dia - 0.5) < 0.030, 170.0, 255.0)  # xam nhat, khong den
    vign = np.clip(1 - (((xx - W / 2) / (W * 0.9)) ** 2 + ((yy - H / 2) / (H * 0.9)) ** 2), 0, 1)
    g = 255 - (255 - g) * (0.45 + 0.55 * vign)

    img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "L")
    d = ImageDraw.Draw(img)
    R = 116
    d.ellipse([W / 2 - R, H / 2 - R, W / 2 + R, H / 2 + R], fill=255)
    d.ellipse([W / 2 - R, H / 2 - R, W / 2 + R, H / 2 + R], outline=0, width=3)
    d.ellipse([W / 2 - R + 11, H / 2 - R + 11, W / 2 + R - 11, H / 2 + R - 11], outline=170, width=1)

    f = ImageFont.truetype(SERIF, 36)
    t = "an nhiên"
    bb = d.textbbox((0, 0), t, font=f)
    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], H / 2 - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f, fill=20)
    return np.asarray(img).astype(np.float64)


# ── Overlay trong suot (de len trang dang doc) ───────────────────────────────
def overlay_vignette():
    """Vien toi mo dan o 4 canh — trang sach van doc duoc o giua."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    ex = np.clip((np.abs(xx - W / 2) - W * 0.30) / (W * 0.20), 0, 1)
    ey = np.clip((np.abs(yy - H / 2) - H * 0.32) / (H * 0.18), 0, 1)
    a = np.clip(np.maximum(ex, ey) ** 1.6, 0, 1) * 190
    return np.zeros((H, W)), a


def overlay_band():
    """Dai mo duoi chan trang + duong ke manh."""
    gray = np.full((H, W), 255.0)
    alpha = np.zeros((H, W))
    top = int(H * 0.845)
    gray[top:, :] = 30
    alpha[top:, :] = 150
    ramp = np.linspace(0, 150, 44)[:, None]
    alpha[top - 44:top, :] = ramp
    gray[top - 44:top, :] = 30
    img = Image.fromarray(np.zeros((H, W), np.uint8), "L")
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(SERIF, 30)
    t = "tạm nghỉ"
    bb = d.textbbox((0, 0), t, font=f)
    tx, ty = (W - (bb[2] - bb[0])) / 2 - bb[0], top + 34
    d.text((tx, ty), t, font=f, fill=255)
    mask = np.asarray(img).astype(np.float64)
    gray = np.where(mask > 60, 255.0, gray)
    alpha = np.maximum(alpha, mask * 0.95)
    return gray, alpha


if __name__ == "__main__":
    walls = {
        "01-trang-nui.bmp": wall_moon,
        "02-chong-sach.bmp": wall_books,
        "03-doc.bmp": wall_type,
        "04-hoa-van.bmp": wall_pattern,
    }
    for name, fn in walls.items():
        g = floyd_steinberg(fn())
        p = os.path.join(OUT, "sleep", name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        save_bmp24(g, p)
        print(f"  {name:<20} {os.path.getsize(p)/1024:7.0f} KB  {len(np.unique(g))} muc xam")

    overs = {"01-vien-mo.bmp": overlay_vignette, "02-dai-chan-trang.bmp": overlay_band}
    for name, fn in overs.items():
        g, a = fn()
        g = floyd_steinberg(g)
        p = os.path.join(OUT, "sleep-overlay", name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        save_bmp32_bgra(g, np.clip(a, 0, 255).astype(np.uint8), p)
        print(f"  {name:<20} {os.path.getsize(p)/1024:7.0f} KB  32-bit BGRA")
