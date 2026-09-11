#!/usr/bin/env python3
"""Bo ve truyen tranh toi gian cho e-ink 480x800.

Nhan vat la hinh hoc don gian, ve nhat quan qua cac trang bang toa do goc,
de mot truyen nhieu trang giu cung nhan dang. Xuat PNG xam; comic2xtc.py lo
phan dong goi XTC.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

W, H = 480, 800
FONT_PATH = "/System/Library/Fonts/Supplemental/ChalkboardSE.ttc"
BLACK, WHITE, GRAY1, GRAY2 = 0, 255, 170, 85  # 4 muc man hinh


def font(sz):
    return ImageFont.truetype(FONT_PATH, sz)


class Page:
    def __init__(self):
        self.im = Image.new("L", (W, H), WHITE)
        self.d = ImageDraw.Draw(self.im)

    # ---- khung tranh ----
    def panel(self, x0, y0, x1, y1, fill=WHITE):
        self.d.rectangle([x0, y0, x1, y1], fill=fill, outline=BLACK, width=3)
        return (x0, y0, x1, y1)

    def sky(self, box, shade=GRAY1):
        x0, y0, x1, y1 = box
        self.d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=shade)
        self.d.rectangle([x0, y0, x1, y1], outline=BLACK, width=3)

    # ---- nhan vat: be gai toc ngan, mat cham, than tam giac ----
    def girl(self, cx, cy, s=1.0, mood="smile", arms="down"):
        d = self.d
        r = int(34 * s)
        # toc (vong cung tren dau)
        d.ellipse([cx - r - 4, cy - r - 6, cx + r + 4, cy + r], fill=BLACK)
        # mat
        d.ellipse([cx - r, cy - r + 6, cx + r, cy + r + 6], fill=WHITE, outline=BLACK, width=3)
        ey = cy - 2
        for ex in (cx - 12, cx + 12):
            d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=BLACK)
        # mieng theo tam trang
        if mood == "smile":
            d.arc([cx - 14, cy + 2, cx + 14, cy + 20], 20, 160, fill=BLACK, width=3)
        elif mood == "wow":
            d.ellipse([cx - 7, cy + 8, cx + 7, cy + 22], outline=BLACK, width=3)
        elif mood == "sad":
            d.arc([cx - 14, cy + 14, cx + 14, cy + 30], 200, 340, fill=BLACK, width=3)
        # than: tam giac (vay)
        by = cy + r + 4
        bh = int(120 * s)
        bw = int(60 * s)
        d.polygon([(cx, by), (cx - bw, by + bh), (cx + bw, by + bh)], outline=BLACK, width=3, fill=GRAY1)
        # chan
        d.line([cx - 18, by + bh, cx - 18, by + bh + 26], fill=BLACK, width=4)
        d.line([cx + 18, by + bh, cx + 18, by + bh + 26], fill=BLACK, width=4)
        # tay
        if arms == "up":
            d.line([cx - bw + 20, by + 40, cx - bw - 4, by + 6], fill=BLACK, width=4)
            d.line([cx + bw - 20, by + 40, cx + bw + 4, by + 6], fill=BLACK, width=4)
        else:
            d.line([cx - bw + 20, by + 30, cx - bw - 2, by + 70], fill=BLACK, width=4)
            d.line([cx + bw - 20, by + 30, cx + bw + 2, by + 70], fill=BLACK, width=4)

    # ---- con meo tron ----
    def cat(self, cx, cy, s=1.0):
        d = self.d
        r = int(30 * s)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=BLACK, width=3)
        d.polygon([(cx - r + 4, cy - r + 6), (cx - r - 6, cy - r - 18), (cx - 6, cy - r)], outline=BLACK, width=3, fill=WHITE)
        d.polygon([(cx + r - 4, cy - r + 6), (cx + r + 6, cy - r - 18), (cx + 6, cy - r)], outline=BLACK, width=3, fill=WHITE)
        for ex in (cx - 11, cx + 11):
            d.ellipse([ex - 3, cy - 4, ex + 3, cy + 4], fill=BLACK)
        d.ellipse([cx - 3, cy + 6, cx + 3, cy + 12], fill=BLACK)
        for dy in (0, 5):
            d.line([cx - 6, cy + 9 + dy, cx - 26, cy + 4 + dy], fill=BLACK, width=2)
            d.line([cx + 6, cy + 9 + dy, cx + 26, cy + 4 + dy], fill=BLACK, width=2)

    # ---- bong thoai ----
    def bubble(self, cx, cy, text, tail_to=None, w=190, pad=16, sz=22):
        f = font(sz)
        lines = self._wrap(text, f, w - 2 * pad)
        lh = sz + 6
        bw, bh = w, lh * len(lines) + 2 * pad
        x0, y0 = cx - bw // 2, cy - bh // 2
        self.d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=18, fill=WHITE, outline=BLACK, width=3)
        if tail_to:
            self.d.polygon([(cx - 14, y0 + bh - 2), (cx + 14, y0 + bh - 2), tail_to], fill=WHITE, outline=BLACK, width=3)
            self.d.line([(cx - 14, y0 + bh - 1), (cx + 14, y0 + bh - 1)], fill=WHITE, width=4)
        ty = y0 + pad
        for ln in lines:
            wln = self.d.textbbox((0, 0), ln, font=f)[2]
            self.d.text((cx - wln // 2, ty), ln, fill=BLACK, font=f)
            ty += lh

    def caption(self, box, text, sz=20):
        x0, y0, x1, y1 = box
        f = font(sz)
        self.d.rectangle([x0, y0, x1, y0 + sz + 16], fill=WHITE, outline=BLACK, width=2)
        self.d.text((x0 + 10, y0 + 8), text, fill=BLACK, font=f)

    def narrate(self, x0, y0, text, w=430, sz=20):
        f = font(sz)
        lines = self._wrap(text, f, w)
        ty = y0
        for ln in lines:
            self.d.text((x0, ty), ln, fill=BLACK, font=f)
            ty += sz + 6
        return ty

    def title(self, text, y=40, sz=40):
        f = font(sz)
        w = self.d.textbbox((0, 0), text, font=f)[2]
        self.d.text(((W - w) // 2, y), text, fill=BLACK, font=f)

    def _wrap(self, text, f, maxw):
        out, cur = [], ""
        for word in text.split():
            t = (cur + " " + word).strip()
            if self.d.textbbox((0, 0), t, font=f)[2] <= maxw:
                cur = t
            else:
                if cur:
                    out.append(cur)
                cur = word
        if cur:
            out.append(cur)
        return out

    def save(self, path):
        self.im.save(path)


# ===== Bo sung cho truyen "Be May va Con Meo Biet Dem" =====

def _extend(cls):
    def deco(fn):
        setattr(cls, fn.__name__, fn); return fn
    return deco


@_extend(Page)
def night(self, box):
    """Nen troi dem xam + vai ngoi sao trang."""
    x0, y0, x1, y1 = box
    self.d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=GRAY2)
    import random
    rnd = random.Random(7)
    for _ in range(14):
        sx = rnd.randint(x0 + 12, x1 - 12); sy = rnd.randint(y0 + 10, (y0 + y1) // 2)
        self.d.line([sx - 3, sy, sx + 3, sy], fill=WHITE, width=1)
        self.d.line([sx, sy - 3, sx, sy + 3], fill=WHITE, width=1)
    self.d.rectangle([x0, y0, x1, y1], outline=BLACK, width=3)


@_extend(Page)
def ceiling(self, box):
    """Duong vien tran nha (goc phong tren)."""
    x0, y0, x1, y1 = box
    self.d.line([x0, y0 + 34, x1, y0 + 34], fill=BLACK, width=2)
    self.d.line([x0 + 40, y0, x0 + 8, y0 + 34], fill=BLACK, width=2)
    self.d.line([x1 - 40, y0, x1 - 8, y0 + 34], fill=BLACK, width=2)


def _ell(d, ax, ay, bx, by, **kw):
    d.ellipse([min(ax, bx), min(ay, by), max(ax, bx), max(ay, by)], **kw)


@_extend(Page)
def gecko(self, cx, cy, s=1.0, flip=False):
    """Thach sung: than dai, dau mot dau, duoi cong dau kia."""
    d = self.d; sgn = -1 if flip else 1
    L = int(46 * s)
    _ell(d, cx - L, cy - 9, cx + L, cy + 9, fill=GRAY1, outline=BLACK, width=2)               # than
    _ell(d, cx + sgn * (L - 2), cy - 11, cx + sgn * (L + 22), cy + 9, fill=GRAY1, outline=BLACK, width=2)  # dau
    _ell(d, cx + sgn * (L + 8), cy - 5, cx + sgn * (L + 12), cy - 1, fill=BLACK)              # mat
    # duoi cong o dau doi dien voi dau
    tx = cx - sgn * L
    _arc = [min(tx - 34, tx + 6), cy - 6, max(tx - 34, tx + 6), cy + 40]
    d.arc(_arc, 0, 160, fill=BLACK, width=3)
    for fx in (-L // 2, L // 2):                                                              # chan
        d.line([cx + fx, cy + 7, cx + fx - 10, cy + 22], fill=BLACK, width=2)
        d.line([cx + fx, cy + 7, cx + fx + 10, cy + 22], fill=BLACK, width=2)


@_extend(Page)
def mosquito(self, cx, cy, s=1.0):
    d = self.d; r = int(4 * s)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLACK)
    d.arc([cx - 12, cy - 12, cx + 2, cy + 2], 0, 260, fill=BLACK, width=1)  # canh
    d.arc([cx - 2, cy - 12, cx + 12, cy + 2], 280, 180, fill=BLACK, width=1)
    for a in (0.4, 0, -0.4):                                                # duong bay
        pass


@_extend(Page)
def buzz(self, cx, cy, n):
    """Duong bay ngoan ngoeo cua muoi + cham cuoi."""
    import math
    pts = []
    for i in range(24):
        t = i / 23.0
        pts.append((cx - 60 + int(120 * t), cy + int(14 * math.sin(t * 9))))
    self.d.line(pts, fill=BLACK, width=1)
    self.mosquito(pts[-1][0], pts[-1][1])


@_extend(Page)
def chair(self, x, yfloor, s=1.0):
    d = self.d; w = int(50 * s); h = int(70 * s); bh = int(50 * s)
    d.rectangle([x, yfloor - h, x + w, yfloor - h + 8], fill=GRAY1, outline=BLACK, width=2)  # mat ghe
    d.rectangle([x, yfloor - h - bh, x + 8, yfloor - h + 8], fill=GRAY1, outline=BLACK, width=2)  # lung
    for lx in (x + 2, x + w - 6):                                                            # chan
        d.line([lx, yfloor - h + 8, lx, yfloor], fill=BLACK, width=3)


@_extend(Page)
def tally(self, x0, y0, rows):
    """Trang so tay: moi dong 'Toi N: |||' — rows = list[(nhan, so)]."""
    f = font(20)
    self.d.rectangle([x0, y0, x0 + 300, y0 + 26 * len(rows) + 20], fill=WHITE, outline=BLACK, width=2)
    ty = y0 + 12
    for label, n in rows:
        self.d.text((x0 + 12, ty), label, fill=BLACK, font=f)
        tx = x0 + 150
        for i in range(n):
            self.d.line([tx, ty + 2, tx, ty + 20], fill=BLACK, width=3)
            tx += 10
            if (i + 1) % 5 == 0:  # gach ngang nhom 5
                self.d.line([tx - 52, ty + 11, tx - 2, ty + 4], fill=BLACK, width=2)
                tx += 6
        ty += 26
