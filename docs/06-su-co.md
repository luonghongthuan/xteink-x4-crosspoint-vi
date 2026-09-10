# 06 — Khắc phục sự cố

## Máy báo `SD card error`

Xếp theo thứ tự nên thử:

### 1. Rác macOS trên thẻ

Thủ phạm phổ biến nhất. Xem [03 — Thẻ nhớ](03-the-nho.md#tắt-spotlight-macos--bắt-buộc).

```bash
find /Volumes/XTEINK -name '._*' -delete
rm -rf /Volumes/XTEINK/.Spotlight-V100 /Volumes/XTEINK/.Trashes /Volumes/XTEINK/.fseventsd
mdutil -i off /Volumes/XTEINK
```

### 2. Thẻ vừa cắm qua điện thoại Android

Android tự tạo `Alarms/`, `DCIM/`, `LOST.DIR/`, `Android/`… CrossPoint không thích
mớ này. Xóa đi hoặc format lại.

### 3. Bảng thư mục FAT hỏng

Rút thẻ lúc chưa eject có thể làm hỏng bảng thư mục theo kiểu **`fsck` không phát
hiện được**. Dấu hiệu: `ls` hiện tên file nhưng mở thì báo không tồn tại.

```bash
$ ls "Trinh Thám/"
ls: Án Mạng Mười Một Chữ.epub: No such file or directory
Phía Sau Nghi Can X.epub
```

Đây là **entry thư mục ma** — tên còn trong bảng nhưng chuỗi cluster đã đứt. Đã thử
`rsync`, `ditto`, đường dẫn byte thô, cả 4 tổ hợp chuẩn hóa NFC/NFD — không cách nào
đọc được. Trong khi đó `diskutil repairVolume` vẫn báo:

```
** Phase 3 - Checking for Orphan Clusters
File system check exit code is 0
```

Nghĩa là **`fsck` báo sạch không có nghĩa là thẻ ổn.**

**Cách xử lý:** những file đó mất hẳn, chấp nhận. Format lại thẻ để dựng bảng FAT mới:

```bash
diskutil eraseDisk FAT32 XTEINK MBRFormat /dev/disk4
```

### 4. Thẻ hỏng thật

Nếu sau khi format vẫn báo lỗi, hoặc thẻ **tự ngắt kết nối** khi đang đọc, thì là
hỏng vật lý. Đổi thẻ.

Dấu hiệu nhận biết trên macOS — khe báo không có thẻ dù thẻ vẫn cắm:

```bash
system_profiler SPCardReaderDataType | grep "Link Width"
# Link Width: Off   -> khe đang trống
```

---

## Máy crash khi đọc sách tiếng Việt

Xem `crash_report.txt` ở gốc thẻ:

```
CrossPoint version: 1.3.0
Panic reason: assert failed: xTaskPriorityDisinherit tasks.c:5156

Last logs:
[ERR] [GFX] No glyph for codepoint 7897   -> ộ
[ERR] [GFX] No glyph for codepoint 7853   -> ậ
[ERR] [GFX] No glyph for codepoint 7901   -> ờ
[ERR] [GFX] No glyph for codepoint 7885   -> ọ
```

**Nguyên nhân:** font đang chọn thiếu glyph tiếng Việt. Các mã 7853–7901 nằm trong
khối Latin Extended Additional (U+1EA0–U+1EF9) — vùng chứa nguyên âm có dấu chồng
hai tầng của tiếng Việt. Nhiều font phương Tây không có.

**Cách sửa:** đổi sang font phủ đủ tiếng Việt, trong `Settings → Reader → Font`:

- **Noto Serif Extended** — "Extended" nghĩa là phủ Unicode mở rộng
- **Gentium Book Plus** — SIL làm, thiết kế riêng cho ngôn ngữ nhiều dấu
- **Noto Sans Extended** — nếu thích font không chân

Tránh các font chỉ có bộ Latin cơ bản.

---

## Thư viện hiện số sách gấp đôi

Mỗi cuốn có thêm một bản sao không mở được. Đó là file AppleDouble `._TenSach.epub`
do macOS sinh ra. CrossPoint đếm cả chúng.

```bash
find /Volumes/XTEINK -name '._*' -delete
```

---

## Truyện dài làm máy treo

Truyện 2000+ chương làm X4 hết RAM khi lập chỉ mục. Chia nhỏ ra:

```bash
python3 tools/split_epub.py truyen.epub -d out/ --chapters 250
```

---

## OTA update báo lỗi

Trên ESP32-C3, sau khi bật WiFi chỉ còn khoảng 46KB heap. Nếu đang nạp font ngoài
(nhất là font CJK), sẽ không đủ chỗ cho mbedTLS bắt tay TLS — kết nối được rồi ngắt
ngay lập tức.

Cách xử lý: đổi về font mặc định, thoát khỏi sách đang đọc, rồi mới cập nhật.

---

## Cổng serial không hiện

```bash
ls /dev/cu.usb*     # macOS
```

Theo thứ tự:

1. **Máy đang ngủ** — bấm nút nguồn cho thức dậy.
2. **Cáp chỉ để sạc** — đổi cáp có truyền dữ liệu.
3. **Máy bị khóa eFuse** — một số lô hàng xám vô hiệu hóa nạp USB vĩnh viễn. Xem
   [01 — Nạp firmware](01-nap-firmware.md#trước-tiên-máy-bạn-có-bị-khóa-usb-không).

---

## Nạp hỏng, máy không lên

Bootloader ROM của ESP32-C3 nằm trong chip, không xóa được. Luôn nạp lại được:

```bash
esptool --chip esp32c3 --port /dev/cu.usbmodem1101 --baud 921600 \
        write-flash 0 x4-goc-16MB.bin
```

Đây là lý do phải dump firmware gốc **trước khi** nghịch.
