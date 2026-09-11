#!/usr/bin/env python3
"""Be May va Con Meo Biet Dem — 10 trang, xuat PNG 480x800."""
import os
from comickit import Page

OUT = os.path.join(os.path.dirname(__file__), "pages")
os.makedirs(OUT, exist_ok=True)
pages = []


def save(p, n):
    path = os.path.join(OUT, f"{n:02d}.png")
    p.save(path)
    pages.append(path)


# ── 1 · bìa + mở ──
p = Page()
p.title("Bé Mây và", y=26, sz=32)
p.title("Con Mèo Biết Đếm", y=66, sz=32)
p.panel(25, 120, 455, 450)
p.girl(175, 240, s=1.1, mood="smile")
p.cat(345, 330, s=1.2)
p.bubble(300, 178, "Mèo ơi, sao tối nào cậu cũng nhìn lên trần thế?", tail_to=(342, 280), w=260, sz=18)
p.narrate(30, 470, "Bé Mây mười tuổi. Con mèo của em tên Đốm, và Đốm có một "
                   "thói quen rất lạ.", sz=20)
p.narrate(30, 560, "Mỗi tối, nó ngồi thật im, ngước lên trần nhà, rồi kêu "
                   "\"meo\" vài tiếng. Rồi thôi.", sz=20)
p.panel(25, 660, 455, 775)
p.cat(110, 718, s=1.0)
p.bubble(320, 715, "Meo... meo... meo!", w=210, sz=22)
save(p, 1)

# ── 2 · số meo khác nhau mỗi tối ──
p = Page()
p.caption((25, 25, 455, 25), "Tối thứ Hai")
p.panel(25, 70, 455, 300)
p.cat(240, 190, s=1.1)
p.bubble(240, 110, "Meo, meo, meo.", w=190, sz=20)
p.narrate(35, 320, "Ba tiếng. Mây đếm được ba tiếng.", sz=20)
p.caption((25, 380, 455, 380), "Tối thứ Ba")
p.panel(25, 425, 455, 640)
p.cat(240, 540, s=1.1)
p.bubble(240, 470, "Meo, meo, meo, meo, meo.", w=250, sz=19)
p.narrate(35, 660, "Năm tiếng! Sao hôm nay lại năm?", sz=20)
p.narrate(35, 710, "Mây bắt đầu thấy tò mò.", sz=20)
save(p, 2)

# ── 3 · ghi sổ ──
p = Page()
p.title("Mây quyết định ghi lại", y=26, sz=24)
p.panel(25, 70, 455, 330)
p.girl(120, 200, s=0.95, mood="smile", arms="down")
# cuon so trong tay
p.d.rectangle([210, 205, 320, 285], fill=255, outline=0, width=3)
p.d.line([265, 205, 265, 285], fill=0, width=1)
p.bubble(330, 130, "Mỗi tối mình sẽ viết vào sổ. Xem có quy luật không!", tail_to=(150, 250), w=250, sz=17)
p.narrate(35, 350, "Và Mây làm đúng như thế. Suốt một tuần, tối nào em cũng "
                   "ngồi cạnh Đốm, lắng nghe, và gạch vào sổ.", sz=20)
p.tally(90, 470, [("Thứ Hai:", 3), ("Thứ Ba:", 5), ("Thứ Tư:", 2),
                  ("Thứ Năm:", 4), ("Thứ Sáu:", 6)])
save(p, 3)

# ── 4 · nhìn lại sổ, bối rối ──
p = Page()
p.panel(25, 30, 455, 300)
p.girl(240, 150, s=1.0, mood="sad")
p.bubble(240, 60, "Ba, năm, hai, bốn, sáu... Chẳng theo thứ tự gì cả!", w=300, sz=17)
p.narrate(35, 320, "Không phải nhiều dần. Không phải ít dần. Các con số cứ "
                   "nhảy lung tung.", sz=20)
p.narrate(35, 420, "Mây gần như bỏ cuộc. Nhưng rồi em nghĩ:", sz=20)
p.panel(25, 490, 455, 720)
p.girl(240, 600, s=1.0, mood="wow")
p.bubble(240, 520, "Khoan đã. Đốm nhìn LÊN TRẦN. Vậy trên đó có gì?", w=310, sz=17)
save(p, 4)

# ── 5 · leo ghế nhìn lên ──
p = Page()
p.title("Mây bắc ghế, trèo lên nhìn", y=26, sz=23)
box = p.panel(25, 70, 455, 470)
p.ceiling(box)
p.chair(150, 430, s=1.4)
p.girl(175, 250, s=0.9, mood="wow", arms="up")
# cho toi tren tran: mot cham + dau ?
p.d.text((340, 120), "?", fill=0)
p.gecko(360, 130, s=0.8)
p.bubble(300, 210, "Có... có con gì bé tí trên kia!", tail_to=(210, 250), w=230, sz=17)
p.narrate(35, 490, "Nấp trong góc tối của trần nhà là một con thạch sùng nhỏ. "
                   "Ban ngày nó trốn. Ban đêm nó mới ra.", sz=20)
save(p, 5)

# ── 6 · thạch sùng bắt muỗi ──
p = Page()
p.caption((25, 25, 455, 25), "Và đây là điều Đốm vẫn xem mỗi tối:")
box = p.panel(25, 70, 455, 470)
p.night(box)
p.ceiling(box)
p.gecko(150, 150, s=1.1)
p.buzz(300, 200, 1)
p.mosquito(360, 250)
p.mosquito(400, 180)
p.bubble(300, 380, "Con thạch sùng đang săn muỗi!", w=260, sz=18)
p.narrate(35, 490, "Mỗi lần nó đớp trúng một con muỗi, con mèo Đốm lại kêu "
                   "một tiếng \"meo\" — như đang reo hò cổ vũ.", sz=20)
save(p, 6)

# ── 7 · khớp con số ──
p = Page()
p.title("Thế là mọi thứ khớp!", y=26, sz=25)
p.panel(25, 75, 230, 300)
p.gecko(120, 150, s=0.9)
p.mosquito(90, 230); p.mosquito(140, 245); p.mosquito(115, 265)
p.caption((40, 250, 215, 250), "3 con muỗi")
p.panel(250, 75, 455, 300)
p.cat(350, 165, s=1.0)
p.bubble(350, 250, "Meo meo meo", w=150, sz=17)
p.narrate(35, 320, "Ba con muỗi bị bắt — ba tiếng meo. Tối nào nhiều muỗi, "
                   "Đốm kêu nhiều. Tối nào ít muỗi, Đốm kêu ít.", sz=20)
p.narrate(35, 430, "Con mèo không hề biết đếm.", sz=22)
p.narrate(35, 490, "Nó chỉ đang xem \"tivi\" của riêng mình — và Mây đã ngồi "
                   "đủ lâu để xem cùng nó.", sz=20)
save(p, 7)

# ── 8 · hai đứa cùng xem ──
p = Page()
box = p.panel(25, 40, 455, 420)
p.night(box)
p.ceiling(box)
p.gecko(360, 130, s=0.9, flip=True)
p.girl(150, 300, s=0.95, mood="smile", arms="up")
p.cat(280, 340, s=1.0)
p.bubble(300, 90, "Đêm nay có bốn con muỗi đấy, Đốm!", w=250, sz=17)
p.narrate(35, 445, "Từ đó, mỗi tối Mây ngồi cạnh Đốm, cùng ngước lên trần.", sz=20)
p.narrate(35, 520, "Có tối một con muỗi. Có tối cả chục con.", sz=20)
p.panel(25, 590, 455, 775)
p.cat(115, 690, s=1.0)
p.bubble(320, 685, "Meo... meo... meo... meo!", w=230, sz=19)
save(p, 8)

# ── 9 · bài học ──
p = Page()
p.title("Điều Mây học được", y=40, sz=28)
p.panel(25, 100, 455, 340)
p.girl(240, 220, s=1.05, mood="smile")
p.narrate(35, 370, "Bí mật không nằm ở con mèo.", sz=22)
p.narrate(35, 430, "Nó nằm ở chỗ Mây chịu ngồi thật im, và nhìn — đủ lâu để "
                   "thấy thứ mà ai vội vàng cũng bỏ lỡ.", sz=20)
p.narrate(35, 560, "Con thạch sùng vẫn ở đó từ trước. Chỉ là chưa ai chịu "
                   "ngước lên.", sz=20)
save(p, 9)

# ── 10 · câu hỏi mở ──
p = Page()
p.title("Nghĩ thêm nhé", y=40, sz=28)
p.d.rounded_rectangle([30, 110, 450, 560], radius=16, outline=0, width=3)
p.narrate(55, 140, "• Vì sao ban đầu các con số làm Mây bối rối? Điều gì "
                   "khiến em không bỏ cuộc?", w=360, sz=20)
p.narrate(55, 250, "• Mây đã làm gì giống một nhà khoa học? (Gợi ý: em có "
                   "một cuốn sổ.)", w=360, sz=20)
p.narrate(55, 360, "• Ở nhà em, có \"con thạch sùng\" nào mà chưa ai chịu "
                   "ngước lên nhìn không?", w=360, sz=20)
p.narrate(55, 480, "Tối nay, thử ngồi im và quan sát một thứ trong năm phút "
                   "xem sao.", w=360, sz=20)
p.girl(240, 640, s=1.0, mood="smile", arms="up")
p.title("Hết", y=740, sz=26)
save(p, 10)

print(f"da ve {len(pages)} trang")
