#!/usr/bin/env python3
"""Bí Mật Của Hạt Đậu — Bé Mây học kiên nhẫn, chữ to."""
import os
from comickit import Page
OUT=os.path.join(os.path.dirname(__file__),"pages3"); os.makedirs(OUT,exist_ok=True)
pages=[]
def save(p,n): path=os.path.join(OUT,f"{n:02d}.png"); p.save(path); pages.append(path)

p=Page()
p.bigtitle("Bí Mật Của",y=48,sz=38); p.bigtitle("Hạt Đậu",y=104,sz=38)
p.panel(30,175,450,560); p.sun(370,240,s=0.7); p.girl(220,370,s=1.1,mood="wow")
# hat dau trong tay
p.d.ellipse([180,360,210,385],fill=200,outline=0,width=2)
p.emote(250,290,"q")
p.bubble(300,220,"Cô giáo cho mình một hạt đậu. Trồng đi là mọc cây!",w=270,sz=18,tail_to=(220,320))
p.narrate(35,585,"Bé Mây gieo hạt vào chậu đất, tưới nước, rồi ngồi chờ. "
                 "Em chờ... và chờ...",sz=22)
save(p,1)

p=Page()
p.caption((30,25,450,25),"Ngày thứ nhất")
p.panel(30,70,450,300); p.girl(140,190,s=0.9,mood="smile")
# chau dat
p.d.rectangle([300,210,380,270],fill=200,outline=0,width=3)
p.bubble(300,120,"Chưa có gì cả. Mai chắc mọc!",w=220,sz=19,tail_to=(160,180))
p.caption((30,340,450,340),"Ngày thứ ba")
p.panel(30,385,450,615); p.girl(140,505,s=0.9,mood="sad")
p.d.rectangle([300,525,380,585],fill=200,outline=0,width=3)
p.emote(180,430,"sweat")
p.bubble(300,435,"Vẫn chưa gì hết! Hay là hạt hỏng?",w=230,sz=18,tail_to=(160,490))
p.narrate(35,640,"Bé Mây thất vọng. Em định đào hạt lên xem thử.",sz=22)
save(p,2)

p=Page()
p.panel(30,50,450,430); p.girl(240,240,s=1.1,mood="wow")
p.cat(360,300,s=0.9)
p.bubble(230,110,"Khoan! Đừng đào lên. Cây đang lớn ở nơi cậu không thấy đâu.",w=300,sz=17,tail_to=(340,250))
p.narrate(35,460,"Con mèo Đốm cản lại. \"Dưới đất,\" mèo nói, \"cái rễ đang "
                 "âm thầm mọc trước. Phần mình thấy được là phần cuối cùng.\"",sz=21)
save(p,3)

p=Page()
p.caption((30,25,450,25),"Ngày thứ bảy")
p.panel(30,70,450,470); p.sun(90,140,s=0.6); p.girl(150,300,s=1.0,mood="wow")
p.d.rectangle([300,320,380,390],fill=200,outline=0,width=3)
# mam xanh nho
p.d.line([340,320,340,290],fill=0,width=3); p.d.ellipse([330,278,350,296],fill=170,outline=0,width=2)
p.emote(200,220,"excl"); p.emote(250,230,"star")
p.bubble(230,130,"Một cái mầm! Nó nhú lên thật rồi!",w=250,sz=19,tail_to=(180,250))
p.narrate(35,500,"Một mầm xanh tí xíu nhú khỏi mặt đất. Suốt bảy ngày, "
                 "cái rễ đã lặng lẽ làm việc dưới lòng đất.",sz=21)
save(p,4)

p=Page()
p.bigtitle("Điều Mây hiểu",y=44,sz=30)
p.panel(30,100,450,400); p.girl(180,240,s=1.0,mood="smile")
p.tree(340,370,s=0.7)
p.narrate(35,430,"Có những thứ lớn lên mà mình không nhìn thấy ngay. Không "
                 "phải nó lười — nó đang chuẩn bị.",sz=22)
p.narrate(35,540,"Giống như tập đàn, học chữ, hay làm bạn với ai đó: phần "
                 "khó nhất xảy ra trước khi mình thấy kết quả.",sz=21)
p.d.rounded_rectangle([30,660,450,780],radius=14,outline=0,width=3)
p.narrate(48,682,"• Vì sao Bé Mây suýt đào hạt lên? Nếu em đào, chuyện gì "
                 "xảy ra? Em có việc gì đang \"mọc rễ\" mà chưa thấy kết quả không?",w=380,sz=18)
save(p,5)
print(f"story3: {len(pages)} trang")
