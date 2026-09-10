# Xteink X4 — CrossPoint tiếng Việt + Lịch Âm

Bộ công cụ và bản vá để biến chiếc **Xteink X4** thành máy đọc sách tiếng Việt tử tế:
firmware CrossPoint tự build có **Lịch dương + Âm lịch**, script chuyển ảnh sang hình
nền e-ink, và script chia nhỏ truyện dài để máy không bị treo.

```
                    15:57                99%
 Calendar
                September 2026
     Mon Tue Wed Thu  Fri  Sat  Sun
           1   2  ┌3┐   4    5    6
      7    8   9  │10│  11   12   13
     14   15  16  └17┘  18   19   20
     21   22  23   24   25   26   27
     28   29  30

     2026-09-10
     29/07/2026 Âm lịch
     Up/Down: week. OK: Agenda. Hold OK: Today.
```

---

## Mục lục

| Tài liệu | Nội dung |
|---|---|
| [01 — Nạp firmware](docs/01-nap-firmware.md) | Nạp bản dựng sẵn qua USB, kèm cách cứu máy |
| [02 — Build từ source](docs/02-build-tu-source.md) | Tự dựng firmware, kể cả cái bẫy `SCons.Tool.FortranCommon` |
| [03 — Chuẩn bị thẻ nhớ](docs/03-the-nho.md) | Format, cấu trúc thư mục, cấu hình tối ưu cho tiếng Việt |
| [04 — Hình nền e-ink](docs/04-hinh-nen.md) | Vì sao ảnh màu đưa thẳng vào thì bệt, và cách xử lý |
| [05 — Từ điển](docs/05-tu-dien.md) | Cài từ điển StarDict tra ngay trong sách |
| [06 — Khắc phục sự cố](docs/06-su-co.md) | `SD card error`, crash thiếu glyph, thẻ tự rớt |

---

## Phần cứng

| | |
|---|---|
| Máy | Xteink X4 |
| Chip | **ESP32-C3** (RISC-V, 1 nhân 160MHz, 320KB RAM, WiFi **2.4GHz only**) |
| Flash | 16MB, phân vùng app 6.25MB |
| Màn hình | e-ink 480×800, **4 mức xám** (0 / 85 / 170 / 255) |
| USB | USB-Serial/JTAG — **không có USB mass storage**, cắm vào máy tính không hiện ổ đĩa |

> **X4 Pro dùng chip khác (ESP32-S3)** — bản vá và firmware ở đây **không dùng được** cho X4 Pro.

---

## Tính năng thêm vào

### Lịch Âm

Ứng dụng Lịch mới trên màn hình Home, hiển thị lịch dương theo tháng và **quy đổi
âm lịch** cho ngày đang chọn. Thuật toán tính âm lịch viết lại từ đầu trong
[`LunarCalendar.cpp`](patches/0001-lich-am-duong.patch) — dùng thuật toán Hồ Ngọc Đức
(tính điểm sóc và trung khí theo múi giờ UTC+7), không phụ thuộc bảng tra cứng nên
chạy đúng cho mọi năm chứ không chỉ vài chục năm nạp sẵn.

**Tốn 0 byte RAM tĩnh** — chỉ cấp phát khi mở ứng dụng, đóng là trả lại.

Điều khiển:

| Phím | Tác dụng |
|---|---|
| Lên / Xuống | Chuyển tuần |
| Previous / Next | Chuyển tháng |
| OK | Xem Agenda |
| Giữ OK | Nhảy về hôm nay |

Màn hình Home hiển thị luôn ngày âm ngay trên nhãn menu (`Lịch · 29/7`), khỏi phải
mở app mới biết.

### Can chi và ngày hoàng đạo

Màn hình Lịch in thêm ba dòng lịch vạn niên cho ngày đang chọn:

```
Đinh Hợi · Bính Thân · Bính Ngọ      ← can chi ngày · tháng · năm
Chu Tước · Hắc đạo · Bạch Lộ         ← trực thần · chất ngày · tiết khí
Giờ tốt: 01-03 07-09 11-13 13-15 19-21 21-23
```

Toàn bộ là số học số nguyên trên bảng tra `constexpr` nằm ở flash — **0 byte RAM**.
Kiểm chứng bằng các mốc chuẩn: 2000-01-01 phải ra ngày *Mậu Ngọ*, năm 2026 phải là
*Bính Ngọ*, Tết 2026 rơi vào 17/02/2026.

### Thống kê đọc

Đếm số trang, thời gian đọc, số phiên, số sách đọc xong, và **chuỗi ngày đọc liên
tiếp** kèm kỷ lục. Lưu ở `/.crosspoint/reading_stats.json`, ghi xuống thẻ mỗi 25
trang hoặc khi đóng sách — không ghi mỗi lần lật trang, vì làm vậy là nhét một lần
serialize JSON cộng một lần ghi SD vào đường lật trang.

### Màn hình ngủ dạng bảng điều khiển

Thêm chế độ **Dashboard** vào `Settings → Display → Sleep Screen`: ngày dương, ngày
âm, số trang và số phút đọc hôm nay, chuỗi ngày, tổng cộng, và tốc độ đọc trang/phút.

### Làm tươi thông minh

Bật ở `Settings → Display`. Chu kỳ làm tươi mặc định đếm số trang cào bằng — một
trang đầu chương chỉ có ba dòng bị tính ngang một trang đặc chữ. Nhưng bóng mờ bám
theo **lượng mực**, không theo số lần lật.

Chế độ này đo độ phủ mực của trang sắp hiện (đếm bit bằng `__builtin_popcount` trên
framebuffer 48KB, vài chục micro giây so với refresh tính bằng giây) rồi trừ ngân
sách 1–3 bậc tùy độ dày. Trang đặc chữ được dọn sớm hơn, trang thưa thì không phí.

Không tốn thêm RAM: đo trực tiếp trên framebuffer đang có, không giữ khung trước để
so sánh — làm vậy sẽ mất thêm 48KB, đúng thứ chế độ một-buffer sinh ra để tiết kiệm.

### Đồng bộ giờ tự động

`HalClock` được mở rộng để đồng bộ NTP ngay khi có WiFi, đặt sẵn múi giờ **UTC+7**.
Không phải chỉnh giờ bằng tay trên màn hình e-ink.

---

## Bắt đầu nhanh

```bash
git clone https://github.com/luonghongthuan/xteink-x4-crosspoint-vi.git
cd xteink-x4-crosspoint-vi

# 1. Nạp firmware dựng sẵn (tải .bin từ mục Releases)
pip install esptool
esptool --chip esp32c3 --port /dev/cu.usbmodem1101 --baud 921600 \
        write-flash 0x10000 x4-lichAm-APP-0x10000.bin

# 2. Chuyển ảnh thành hình nền ngủ
pip install pillow numpy
python3 tools/photo2eink.py anh.jpg -d sleep/

# 3. Chia truyện dài thành nhiều tập
python3 tools/split_epub.py truyen.epub -d out/
```

Chi tiết từng bước ở [docs/](docs/).

---

## Công cụ

### `tools/photo2eink.py`

Chuyển ảnh chụp màu sang BMP 480×800, 4 mức xám.

Màn hình chỉ có 4 mức xám. Nếu chuyển thẳng sang xám rồi dither, khuôn mặt sẽ bệt
thành một mảng trắng hoặc một mảng đen. Script này kéo **tương phản cục bộ** trước
(CLAHE tự cài bằng numpy, có nội suy song tuyến tính để không bị rằn ô), rồi mới
dither Floyd–Steinberg.

```bash
python3 tools/photo2eink.py anh.jpg                       # mặc định
python3 tools/photo2eink.py anh.jpg --focal-x 0.8         # ảnh ngang, người lệch phải
python3 tools/photo2eink.py anh.jpg --pre-bottom 0.06     # cắt bỏ watermark
python3 tools/photo2eink.py *.jpg -d sleep/ --clip 3.0    # tương phản mạnh hơn
```

### `tools/make_wallpapers.py`

Sinh hình nền hình học dựng sẵn (đã tối ưu cho 4 mức xám, không cần ảnh nguồn).

### `tools/split_epub.py`

Chia EPUB lớn thành nhiều tập. Truyện dài kiểu *Phàm Nhân Tu Tiên* (2400+ chương)
làm X4 hết RAM khi lập chỉ mục. Script chia theo số chương, giữ nguyên bìa (nén lại
cho nhẹ), sinh `content.opf` và `toc.ncx` hợp lệ cho từng tập.

```bash
python3 tools/split_epub.py truyen.epub -d out/ --chapters 250
```

---

## Bản vá

[`patches/0001-lich-am-duong.patch`](patches/0001-lich-am-duong.patch) — 1.209 dòng
thêm mới qua 28 file, áp lên nhánh `develop` của
[crosspoint-reader](https://github.com/crosspoint-reader/crosspoint-reader).

```bash
git clone -b develop https://github.com/crosspoint-reader/crosspoint-reader.git
cd crosspoint-reader
git apply ../patches/0001-lich-am-duong.patch
```

| File | Vai trò |
|---|---|
| `src/util/LunarCalendar.{cpp,h}` | Thuật toán quy đổi âm lịch, tiết khí |
| `src/util/CanChi.{cpp,h}` | Can chi, trực thần, giờ hoàng đạo |
| `src/activities/util/CalendarActivity.{cpp,h}` | Màn hình Lịch |
| `src/ReadingStats.{cpp,h}` | Thống kê đọc và chuỗi ngày |
| `src/activities/boot_sleep/SleepActivity.*` | Màn hình ngủ Dashboard |
| `src/activities/reader/ReaderUtils.h` | Làm tươi theo lượng mực, đếm trang |
| `lib/GfxRenderer/GfxRenderer.*` | `inkCoverage()` — đo độ phủ mực |
| `lib/hal/HalClock.{cpp,h}` | Đồng bộ NTP, múi giờ UTC+7 |
| `src/activities/ActivityManager.*`, `HomeActivity.*` | Đăng ký ứng dụng vào Home |
| `lib/I18n/translations/*.yaml` | Chuỗi tiếng Việt và tiếng Anh |

---

## Giấy phép

MIT, theo đúng giấy phép của [CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader)
mà dự án này vá lên.

## Ghi nhận

- [CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader) — firmware gốc
- Thuật toán âm lịch theo phương pháp của **Hồ Ngọc Đức**
