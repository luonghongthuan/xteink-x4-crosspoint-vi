# 04 — Hình nền e-ink

## Quy cách

| | |
|---|---|
| Kích thước | **480 × 800** |
| Định dạng | BMP không nén (24-bit hoặc 1-bit đều được) |
| Thư mục | `sleep/` — ảnh nền ngủ · `.sleep-overlay/` — ảnh trong suốt chồng lên trang sách |

Màn hình chỉ hiển thị được **4 mức xám**. Firmware lượng tử hóa bằng phép dịch bit:

```c
// SleepActivity.cpp
quantizeOverlayLum(lum) = lum >> 6      // 0..255 -> 0,1,2,3 -> 0, 85, 170, 255
```

Nghĩa là mọi giá trị xám đều bị ép về đúng 4 mức: **0, 85, 170, 255**. Ảnh của bạn
có 256 mức hay 16 triệu màu cũng vậy thôi.

---

## Vì sao không thể chuyển thẳng

Cách làm ngây thơ — chuyển sang xám rồi lượng tử hóa — cho kết quả tệ với ảnh chụp
người. Da mặt thường nằm gọn trong một khoảng sáng hẹp, nên cả khuôn mặt rơi vào
**cùng một mức xám** và bệt thành một mảng trắng hoặc một mảng đen. Mắt, mũi, miệng
biến mất.

Quy trình trong [`tools/photo2eink.py`](../tools/photo2eink.py) gồm 6 bước:

```
xám → CLAHE → unsharp → cắt khung → thu nhỏ → S-curve → dither
```

### CLAHE — bước quan trọng nhất

**Contrast Limited Adaptive Histogram Equalization.** Thay vì kéo tương phản cho
toàn ảnh, nó chia ảnh thành lưới ô (mặc định 8×6) và cân bằng histogram **từng ô
riêng**. Nhờ vậy mỗi khuôn mặt tự có dải sáng riêng, không bị nền sáng hay tối kéo theo.

Hai chi tiết khiến nó dùng được:

- **Giới hạn clip** — cắt bớt các đỉnh histogram rồi phân bố lại phần thừa. Không có
  bước này, vùng phẳng như bầu trời sẽ bị khuếch đại nhiễu thành hạt lấm tấm.
- **Nội suy song tuyến tính** giữa các ô — không có bước này, ranh giới ô hiện rõ
  thành lưới ô vuông trên ảnh.

Script tự cài CLAHE bằng numpy, không cần OpenCV.

### Floyd–Steinberg

Sau khi đã kéo tương phản mới dither. Sai số của mỗi điểm ảnh được đẩy sang các
điểm lân cận theo tỉ lệ 7/16, 3/16, 5/16, 1/16 — mắt người nhìn từ xa sẽ thấy các
mức xám trung gian không thực sự tồn tại.

---

## Dùng

```bash
pip install pillow numpy

python3 tools/photo2eink.py anh.jpg                    # ra anh.bmp
python3 tools/photo2eink.py anh.jpg -o nen.bmp
python3 tools/photo2eink.py *.jpg -d sleep/
```

### Chỉnh khung cắt

Màn hình tỉ lệ 3:5 (480/800 = 0.6), rất hẹp so với ảnh chụp thông thường. Ảnh 4:3
hay 3:4 sẽ bị cắt bớt hai bên.

```bash
python3 tools/photo2eink.py anh.jpg --focal-x 0.8      # người lệch phải trong ảnh
python3 tools/photo2eink.py anh.jpg --focal-y 0.3      # ưu tiên phần trên
```

`--focal-x 0` là sát trái, `1` là sát phải. Với **ảnh ngang** thì tham số này rất
quan trọng — cắt từ 1976px xuống 889px là mất hơn nửa khung hình, mặc định cắt giữa
thường chặt mất người ở rìa.

### Cắt bỏ watermark

Điện thoại hay đóng dấu ở góc dưới (kiểu `vivo X Fold5 | ZEISS`):

```bash
python3 tools/photo2eink.py anh.jpg --pre-bottom 0.06
```

Cắt thô 6% chiều cao từ dưới lên **trước khi** xử lý. Làm vậy còn tiện: khung chặt
hơn thì mặt người to hơn.

### Tinh chỉnh

| Tham số | Mặc định | Tăng lên thì |
|---|---|---|
| `--clip` | 2.5 | Tương phản cục bộ mạnh hơn, mặt rõ hơn nhưng nhiễu hơn |
| `--sharp` | 0.85 | Nét hơn, quá tay thì viền bị quầng |
| `--scurve` | 0.30 | Tương phản tổng thể mạnh hơn, dễ mất chi tiết vùng sáng |

Ảnh chụp trong nhà thiếu sáng thường hợp với `--clip 3.0 --sharp 1.0`.

---

## Chọn ảnh nào cho dễ ăn

Chỉ có 4 mức xám nên ảnh càng đơn giản càng đẹp:

- **Mặt to, chiếm nhiều khung hình** — ảnh chụp cả nhóm từ xa thì mặt chỉ còn vài
  chục điểm ảnh, dither xong không nhận ra ai.
- **Nền đơn giản** — nền lộn xộn biến thành nhiễu.
- **Ánh sáng đều trên mặt** — ngược sáng mạnh thì CLAHE cũng khó cứu.

## Ảnh overlay trong suốt

Từ CrossPoint 1.6.0, thư mục `.sleep-overlay/` nhận PNG/BMP có nền trong suốt. Máy
sẽ chồng ảnh đó **lên trang sách đang đọc** thay vì thay thế hoàn toàn — nhìn khá đẹp.

Dùng PNG có alpha, phần muốn nhìn xuyên qua để trong suốt hoàn toàn.
