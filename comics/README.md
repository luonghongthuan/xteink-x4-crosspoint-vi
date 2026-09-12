# Truyện tranh gốc

Truyện tranh **tự sáng tác** cho X4 — nhân vật vẽ bằng code (`comickit.py`),
kịch bản trong `story.py` mỗi truyện. Chạy `python3 story.py` sinh ra thư mục
`pages*/`, rồi đóng thành XTC:

```
python3 story.py
python3 ../../tools/comic2xtc.py --bw pages -o "Ten-truyen.xtc"
```

**Luôn dùng `--bw`** (1-bit): 2-bit cần ~96KB heap, vượt giới hạn ESP32-C3.
Vẽ đúng 480×800 nên chữ luôn to rõ, khác hẳn truyện scan bị co từ 1440px→480px.

Phong cách tối giản (nhân vật hình học, nét đậm) là chủ ý — nó đọc rõ nhất trên
màn hình 4 mức xám, và là nội dung gốc nên không vướng bản quyền.

Bộ 4 truyện đều lấy nhân vật Bé Mây (10 tuổi) và con mèo/chó của em, chữ to,
mỗi truyện khép lại bằng vài câu hỏi để bé suy nghĩ.

## Bé Mây và Con Mèo Biết Đếm (`be-may/`)

10 trang. Một cô bé phát hiện con mèo của mình không hề "biết đếm" — nó chỉ đang
xem con thạch sùng săn muỗi trên trần nhà mỗi đêm. Truyện về quan sát, kiên nhẫn,
và cách nghĩ của người làm khoa học (ghi sổ → tìm quy luật → tự kiểm chứng).

## Chú Chó Đốm Đi Lạc (`cho-dom/`)

7 trang. Chú chó Đốm mê đuổi bướm nên đi lạc, rồi nhờ một con mèo già chỉ cách lần
theo mùi bánh mì nướng quen thuộc mà tìm về nhà. Bài học: khi lạc, đừng hoảng —
tìm thứ mình quen nhất rồi lần theo nó.

## Bí Mật Của Hạt Đậu (`hat-dau/`)

5 trang. Bé Mây gieo một hạt đậu và sốt ruột vì mãi chưa thấy mọc, suýt đào lên.
Con mèo cản lại: cái rễ đang âm thầm lớn dưới đất trước. Bài học về kiên nhẫn —
phần khó nhất xảy ra trước khi mình thấy kết quả.

## Ngày Mưa Của Bé Mây (`ngay-mua/`)

5 trang. Trời mưa hỏng buổi đi chơi, Bé Mây chán nản, rồi tự biến phòng khách
thành biển và cái ghế thành con thuyền. Bài học: một ngày vui hay chán nhiều khi
không do trời, mà do mình quyết định làm gì với nó.
