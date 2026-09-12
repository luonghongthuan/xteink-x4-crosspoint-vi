#!/usr/bin/env python3
"""Chú Chó Đốm Đi Lạc — truyện vui cho bé, chữ to."""
import os
from comickit import Page

OUT = os.path.join(os.path.dirname(__file__), "pages2")
os.makedirs(OUT, exist_ok=True)
pages = []
def save(p, n): path=os.path.join(OUT,f"{n:02d}.png"); p.save(path); pages.append(path)

# ── 1 · bìa ──
p = Page()
p.bigtitle("Chú Chó Đốm", y=54, sz=40)
p.bigtitle("Đi Lạc", y=110, sz=40)
p.panel(30, 180, 450, 560)
p.sun(370, 250, s=0.8)
p.tree(90, 540, s=1.0)
p.girl(180, 380, s=1.0, mood="smile")
p.dog(300, 430, s=1.2, mood="happy")
p.emote(320, 370, "heart")
p.narrate(35, 590, "Bé Mây có một chú chó tên Đốm. Đốm rất ngoan — chỉ có "
                   "một tật: nó mê đuổi bướm tới mức quên cả đường về.", sz=22)
save(p, 1)

# ── 2 · đuổi bướm ──
p = Page()
p.panel(30, 40, 450, 420)
p.dog(160, 250, s=1.1, mood="happy")
p.emote(200, 180, "burst")
# con buom (dung bird lam vat bay)
p.bird(330, 150, s=0.7)
p.bubble(300, 90, "Gâu! Đợi tớ với, bướm ơi!", w=250, sz=22, tail_to=(200,200))
p.narrate(35, 450, "Một buổi chiều, Đốm thấy con bướm đẹp nhất đời. Nó đuổi "
                   "theo, băng qua vườn, qua cầu, qua chợ...", sz=22)
p.narrate(35, 580, "...và khi ngẩng lên, Đốm chẳng biết mình đang ở đâu nữa.", sz=22)
save(p, 2)

# ── 3 · lạc, sợ ──
p = Page()
p.panel(30, 60, 450, 440)
p.dog(240, 260, s=1.3, mood="sad")
p.emote(290, 150, "sweat")
p.emote(200, 160, "q")
p.bubble(240, 110, "Ơ... nhà mình đâu rồi?", w=230, sz=22)
p.narrate(35, 470, "Trời bắt đầu tối. Đốm ngồi bên gốc cây, tai cụp xuống. "
                   "Nó nhớ Bé Mây quá.", sz=22)
p.tree(360, 430, s=0.9)
save(p, 3)

# ── 4 · gặp mèo ──
p = Page()
p.caption((30, 25, 450, 25), "Bỗng có tiếng meo...")
p.panel(30, 70, 450, 450)
p.dog(150, 300, s=1.1, mood="sad")
p.cat(330, 280, s=1.2)
p.bubble(300, 130, "Cậu bị lạc à? Tớ ngửi thấy mùi lo lắng.", w=270, sz=20, tail_to=(330,230))
p.narrate(35, 480, "Một con mèo già bước ra. Mèo biết mọi ngóc ngách trong "
                   "phố — vì mèo đi lang thang cả đời.", sz=22)
save(p, 4)

# ── 5 · mèo giúp ──
p = Page()
p.panel(30, 40, 450, 300)
p.cat(140, 170, s=1.0)
p.bubble(310, 130, "Nhà cậu có mùi bánh mì nướng, đúng không? Đi theo mũi tớ!", w=280, sz=18, tail_to=(160,180))
p.narrate(35, 330, "Mèo nói đúng! Mỗi sáng mẹ Bé Mây đều nướng bánh mì. Đốm "
                   "hít thật sâu...", sz=22)
p.panel(30, 440, 450, 720)
p.dog(150, 580, s=1.1, mood="happy")
p.emote(200, 500, "excl")
p.bubble(320, 520, "Tớ ngửi thấy rồi! Hướng này!", w=230, sz=19)
save(p, 5)

# ── 6 · về nhà ──
p = Page()
p.panel(30, 50, 450, 470)
p.sun(90, 130, s=0.6)
p.girl(310, 300, s=1.1, mood="wow")
p.dog(180, 350, s=1.2, mood="happy")
p.emote(250, 250, "heart")
p.emote(150, 260, "star")
p.bubble(240, 120, "ĐỐM! Cậu về rồi!", w=230, sz=24, tail_to=(300,220))
p.narrate(35, 500, "Bé Mây chạy ùa ra ôm chầm lấy Đốm. Còn con mèo già thì "
                   "đứng nhìn một lúc, rồi lặng lẽ đi tiếp.", sz=22)
save(p, 6)

# ── 7 · kết + câu hỏi ──
p = Page()
p.bigtitle("Từ hôm đó...", y=40, sz=32)
p.panel(30, 100, 450, 420)
p.girl(160, 260, s=1.0, mood="smile")
p.dog(300, 300, s=1.1, mood="happy")
p.cat(390, 320, s=0.8)
p.narrate(35, 450, "...mỗi chiều Bé Mây để một bát cơm nhỏ ngoài cửa cho "
                   "con mèo già. Và Đốm thì học được một điều:", sz=22)
p.narrate(35, 580, "khi lạc đường, đừng hoảng — hãy tìm thứ mình quen thuộc "
                   "nhất, rồi lần theo nó.", sz=22)
p.d.rounded_rectangle([30, 680, 450, 780], radius=14, outline=0, width=3)
p.narrate(48, 700, "• Đốm tìm đường về bằng cách nào? Em có ngửi được mùi "
                   "nhà mình không?", w=380, sz=19)
save(p, 7)

print(f"da ve {len(pages)} trang")
