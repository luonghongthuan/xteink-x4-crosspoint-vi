# 02 — Build firmware từ source

## Cái bẫy lớn nhất: phải dùng đúng bản PlatformIO

Dự án này **không build được bằng PlatformIO bản chuẩn từ PyPI**. Nếu bạn `pip install
platformio` rồi chạy, sau khoảng 7 phút biên dịch nó sẽ chết ở khâu link:

```
*** [.pio/build/default/firmware.elf] ModuleNotFoundError: No module named 'SCons.Tool.FortranCommon'
========================= [FAILED] Took 452.60 seconds =========================
```

**Nguyên nhân:** PlatformIO tự tạo virtualenv riêng và cài SCons mới nhất vào đó.
SCons đã **bỏ module `SCons.Tool.FortranCommon` từ bản 4.9**, nhưng trình build
ESP-IDF vẫn tham chiếu tới nó.

**Cách sửa:** dùng bản fork **pioarduino** — nó ghim SCons ở phiên bản tương thích.

```bash
python3 -m venv pioard-venv
./pioard-venv/bin/pip install --upgrade pip
./pioard-venv/bin/pip install \
  "https://github.com/pioarduino/platformio-core/archive/refs/tags/v6.1.19.zip"
./pioard-venv/bin/pio --version    # phải ra: PlatformIO Core, version 6.1.19
```

---

## Chuẩn bị

```bash
git clone -b develop https://github.com/crosspoint-reader/crosspoint-reader.git
cd crosspoint-reader
```

Cần thêm `cmake` (macOS: `brew install cmake`, hoặc `pip install cmake==3.31.6`).

## Áp bản vá Lịch Âm

```bash
git apply /duong/dan/toi/patches/0001-lich-am-duong.patch
git status --short      # phải thấy 9 file M và 4 file mới
```

## Build

```bash
./pioard-venv/bin/pio run -e default
```

**Lần đầu mất khoảng 15–20 phút** (phải tải toolchain RISC-V và biên dịch toàn bộ
ESP-IDF). Các lần sau có cache nên chỉ khoảng **25–35 giây**.

Kết quả đúng:

```
RAM:   [==        ]  17.3% (used 56608 bytes from 327680 bytes)
Flash: [========  ]  83.7% (used 5486587 bytes from 6553600 bytes)
========================= [SUCCESS] Took 33.84 seconds =========================
```

Sản phẩm nằm ở `.pio/build/default/`:

| File | Nạp tại | Ghi chú |
|---|---|---|
| `firmware.bin` | `0x10000` | Ảnh ứng dụng — bình thường dùng cái này |
| `firmware.factory.bin` | `0x0` | Ảnh gộp cả bootloader + bảng phân vùng |
| `bootloader.bin` | `0x0` | |
| `partitions.bin` | `0x8000` | |

---

## Để mắt tới dung lượng

Phân vùng app chỉ có **6.25MB** và bản dựng đã dùng **83.7%**. Còn khoảng 1MB.
Thêm tính năng lớn (font mới, thư viện nặng) là tràn. Khi tràn, build sẽ báo lỗi
`section ... will not fit in region`.

RAM còn thoải mái hơn (17.3% của 320KB), nhưng nhớ rằng **WiFi bật lên ăn thêm
khoảng 50KB** — và mbedTLS cần heap liên tục để bắt tay TLS. Đây chính là lý do
CrossPet gặp lỗi OTA: font CJK nạp sẵn chiếm hết heap, không đủ chỗ cho TLS.

## Kiểm tra bản dựng có đúng phần mình sửa không

Chuỗi ASCII thì grep được thẳng:

```bash
strings -a .pio/build/default/firmware.bin | grep -w Lunar
```

Nhưng **chuỗi tiếng Việt sẽ không tìm thấy** — hai lý do: `strings` mặc định chỉ
quét ASCII, và bảng dịch trong firmware bị nén. Đừng hoảng khi grep `"Âm lịch"`
ra 0 kết quả; cách kiểm tra thật là nạp vào máy rồi mở ứng dụng lên xem.

## So sánh file để chắc mình nạp đúng cái vừa build

Rất dễ nhầm giữa nhiều bản dựng. Luôn đối chiếu hash:

```bash
shasum -a 256 .pio/build/default/firmware.bin
shasum -a 256 file-ban-dinh-nap.bin
```

Hai dòng phải trùng nhau.
