#!/usr/bin/env python3
"""Ngày Mưa Của Bé Mây — sáng tạo khi buồn chán, chữ to."""
import os
from comickit import Page
OUT=os.path.join(os.path.dirname(__file__),"pages4"); os.makedirs(OUT,exist_ok=True)
pages=[]
def save(p,n): path=os.path.join(OUT,f"{n:02d}.png"); p.save(path); pages.append(path)

def rain(pg,box):
    x0,y0,x1,y1=box
    import random; r=random.Random(3)
    for _ in range(40):
        x=r.randint(x0+8,x1-8); y=r.randint(y0+8,y1-40)
        pg.d.line([x,y,x-4,y+12],fill=0,width=1)

p=Page()
p.bigtitle("Ngày Mưa",y=52,sz=40); p.bigtitle("Của Bé Mây",y=108,sz=36)
b=p.panel(30,180,450,520); rain(p,(30,180,450,520))
p.girl(240,360,s=1.1,mood="sad"); p.emote(300,260,"sweat")
p.bubble(240,240,"Mưa suốt! Không đi chơi được...",w=250,sz=19)
p.narrate(35,545,"Mây đã hẹn đi công viên. Nhưng trời mưa cả ngày. Em ngồi "
                 "bên cửa sổ, chán nản nhìn ra.",sz=22)
save(p,1)

p=Page()
p.panel(30,50,450,290); p.girl(140,170,s=0.9,mood="sad")
p.cat(340,210,s=1.0)
p.bubble(300,120,"Buồn à? Hay là mình biến phòng khách thành... cái gì đó?",w=270,sz=17,tail_to=(320,170))
p.narrate(35,320,"Con mèo Đốm nghiêng đầu. \"Trời cho cậu một ngày ở trong "
                 "nhà. Cậu định phí nó, hay dùng nó?\"",sz=21)
p.panel(30,470,450,720); p.girl(240,600,s=1.0,mood="wow"); p.emote(300,510,"excl")
p.bubble(240,505,"Mình biết rồi!",w=180,sz=22)
save(p,2)

p=Page()
p.bigtitle("Và thế là...",y=36,sz=28)
p.panel(30,90,450,420)
# phao/le: ghe lam thuyen
p.d.polygon([(120,340),(320,340),(290,270),(150,270)],fill=170,outline=0,width=3)
p.girl(220,230,s=0.9,mood="smile",arms="up")
p.emote(160,180,"star"); p.emote(300,190,"star")
p.bubble(330,140,"Cái ghế là con thuyền! Sàn nhà là biển!",w=230,sz=17)
p.narrate(35,450,"Bé Mây lật ghế thành thuyền, trải chăn làm sóng, gấp giấy "
                 "làm buồm. Con mèo Đốm làm thuyền trưởng.",sz=21)
save(p,3)

p=Page()
p.panel(30,50,450,470)
p.girl(160,280,s=1.0,mood="smile",arms="up"); p.cat(320,300,s=1.0)
p.emote(120,190,"heart"); p.emote(360,200,"star"); p.emote(240,160,"burst")
p.bubble(240,120,"Đất liền phía trước! Bám chắc nhé thuyền trưởng Đốm!",w=290,sz=17)
p.narrate(35,500,"Cả buổi chiều trôi qua nhanh như chớp. Khi mẹ gọi ăn cơm, "
                 "Mây còn tiếc chưa muốn \"cập bến\".",sz=21)
save(p,4)

p=Page()
p.bigtitle("Buổi tối",y=40,sz=32)
b=p.panel(30,100,450,420); rain(p,(30,100,450,420))
p.girl(240,270,s=1.0,mood="smile")
p.bubble(240,160,"Hóa ra ngày mưa cũng vui ghê!",w=240,sz=19)
p.narrate(35,450,"Ngoài trời vẫn mưa. Nhưng Mây không còn thấy chán nữa.",sz=22)
p.narrate(35,540,"Em nhận ra: một ngày chán hay vui, đôi khi không do trời "
                 "— mà do mình quyết định làm gì với nó.",sz=21)
p.d.rounded_rectangle([30,660,450,780],radius=14,outline=0,width=3)
p.narrate(48,682,"• Lần gần nhất em thấy chán, em đã làm gì? Có trò chơi nào "
                 "em tự nghĩ ra từ đồ vật quanh nhà không?",w=380,sz=18)
save(p,5)
print(f"story4: {len(pages)} trang")
