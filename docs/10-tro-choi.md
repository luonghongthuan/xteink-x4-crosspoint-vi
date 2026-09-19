# 10 — Trò chơi: Cờ vua & 2048

Bản build này thêm hai trò chơi điều khiển bằng nút vào menu chính, ngay dưới
**Lịch**. Cả hai vẽ đúng ở độ phân giải màn hình, chạy trọn trong RAM của ESP32-C3,
không cần mạng.

## Cờ vua

Máy cờ tự viết (`lib/Chess`), không dùng thư viện ngoài. Đã kiểm thử luật bằng
phép đếm nước đi (perft) khớp số chuẩn quốc tế — xem `test/chess_native`.

Menu **Cờ vua** có:

- **Chơi với máy: Dễ / Vừa / Khó** — máy nghĩ sâu dần theo thời gian (mức Khó tới
  6 nước, tối đa ~5 giây). Mức Dễ cố tình thỉnh thoảng đi hớ để bé có cửa thắng.
- **Giải thế cờ: chiếu hết 1 nước** — 16 thế, đi sai máy báo và hoàn nước.
- **Luật chơi & hướng dẫn** — 14 trang song ngữ cho bé, kèm bàn cờ minh hoạ có
  chấm đen ở những ô quân được chọn đi được (do chính máy cờ tính ra).

Máy chơi đúng luật đầy đủ: nhập thành, bắt tốt qua đường, phong cấp (tự phong Hậu),
chiếu / chiếu hết / hết nước đi, và các luật hoà (50 nước, lặp thế cờ 3 lần, không
đủ quân chiếu hết).

**Điều khiển:** 4 nút mũi tên di con trỏ, **Chọn** nhấc quân rồi đặt (ô đi được
hiện chấm đen), **Quay lại** bỏ chọn hoặc mở menu tạm dừng (Chơi tiếp · Gợi ý
nước đi · Đi lại · Ván mới · Thoát).

## 2048

Gộp các ô cùng số cho tới khi ra 2048. Ô càng lớn nền càng đậm, số to màu trắng
nổi trên nền đậm cho dễ đọc trên e-ink. Có điểm hiện tại và điểm cao nhất trong
phiên. Hết nước đi bấm **Chọn** chơi lại; **Quay lại** để thoát. Toàn bộ ván cờ
gói trong 16 ô, không cấp phát bộ nhớ động.

**Điều khiển:** 4 nút mũi tên để trượt các ô.

## Chi phí bộ nhớ

- Flash: +~35KB cho cả hai trò.
- RAM tĩnh: không đổi (vẫn ~20%). Cờ vua cấp ~8KB heap khi mở màn hình (bộ nhớ
  tìm kiếm + nhật ký ván để "đi lại"), trả lại khi thoát. 2048 không cấp heap.
- Đo trên máy: sau khi vào/thoát trò chơi, heap trống vẫn ~87KB.

## Dựng lại từ nguồn

Áp `patches/0002-tro-choi.patch` lên cây nguồn CrossPoint (đã áp
`0001-lich-am-duong.patch` trước), rồi nối các chuỗi trong
`patches/0002-tro-choi-strings.txt` vào cuối hai file
`lib/I18n/translations/english.yaml` và `vietnamese.yaml`. Build env `default`
theo `docs/02-build-tu-source.md`.

> Trên máy dev này chỉ build được env `default` (có Bluetooth). Không build
> `gh_release`: nó tắt Bluetooth khiến trình quản lý component của pioarduino cắt
> các đường include `bt/` khỏi framework, làm hỏng NimBLE ở lần build sau.
