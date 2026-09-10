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

[`patches/0001-lich-am-duong.patch`](patches/0001-lich-am-duong.patch) — 612 dòng
thêm mới qua 13 file, áp lên nhánh `develop` của
[crosspoint-reader](https://github.com/crosspoint-reader/crosspoint-reader).

```bash
git clone -b develop https://github.com/crosspoint-reader/crosspoint-reader.git
cd crosspoint-reader
git apply ../patches/0001-lich-am-duong.patch
```

| File | Vai trò |
|---|---|
| `src/util/LunarCalendar.{cpp,h}` | Thuật toán quy đổi âm lịch |
| `src/activities/util/CalendarActivity.{cpp,h}` | Màn hình Lịch |
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
