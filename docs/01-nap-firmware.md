# 01 — Nạp firmware

## Trước tiên: máy bạn có bị khóa USB không?

Từ khoảng tháng 5/2026, một số lô X3/X4 (gần như luôn từ AliExpress/Taobao) xuất
xưởng với **chế độ nạp USB bị vô hiệu hóa vĩnh viễn bằng eFuse**. Trên những máy đó,
cắm vào máy tính sẽ **không hiện cổng serial nào** — cả web installer lẫn esptool
đều vô dụng, và nếu bạn nạp một firmware có OTA hỏng thì **hết đường ra**.

Kiểm tra trước khi làm bất cứ điều gì:

```bash
# macOS
ls /dev/cu.usb*
# Linux
ls /dev/ttyACM*
```

- **Hiện `/dev/cu.usbmodem…`** → máy không bị khóa, cứ yên tâm làm tiếp.
- **Không hiện gì** → máy có thể đang ngủ (bấm nút nguồn cho thức dậy rồi thử lại),
  cáp chỉ để sạc không truyền dữ liệu, hoặc máy bị khóa eFuse. Nếu đúng là khóa,
  dùng Xteink Unlocker tại `crosspointreader.com/#unlock-tool` trước, và **chỉ nạp
  CrossPoint hoặc CrossInk** — các fork khác có thể để lại tình trạng không cứu được.

> X4 **không có chế độ USB mass storage**. Cắm vào máy tính không hiện ổ đĩa là
> chuyện bình thường, không phải hỏng. Nó chỉ hiện ra dưới dạng cổng serial.

---

## Bước 1 — Sao lưu firmware gốc

**Đừng bỏ qua bước này.** Đây là đường lùi duy nhất nếu có chuyện.

```bash
pip install esptool

esptool --port /dev/cu.usbmodem1101 --baud 921600 flash-id      # xem dung lượng flash
esptool --port /dev/cu.usbmodem1101 --baud 921600 \
        read-flash 0 0x1000000 x4-goc-16MB.bin                  # dump toàn bộ 16MB
```

Mất khoảng 4–6 phút. Cất file này ở nơi an toàn.

> **Không đưa file dump này lên mạng.** Nó chứa địa chỉ MAC của máy bạn, và nếu
> firmware cũ từng lưu WiFi thì có cả mật khẩu WiFi trong đó.

## Bước 2 — Xác nhận đúng chip

```bash
esptool --port /dev/cu.usbmodem1101 --baud 115200 chip-id
```

Phải thấy:

```
Chip type: ESP32-C3 (QFN32) (revision v0.4)
Features:  Wi-Fi, BT 5 (LE), Single Core, 160MHz
```

**Nếu thấy `ESP32-S3` thì đó là X4 Pro**, dừng lại — firmware ở đây sẽ không chạy.

## Bước 3 — Nạp

Tải file `.bin` từ mục **Releases** của repo này, rồi:

```bash
esptool --chip esp32c3 --port /dev/cu.usbmodem1101 --baud 921600 \
        write-flash 0x10000 x4-lichAm-APP-0x10000.bin
```

Kết quả đúng phải có dòng:

```
Wrote 5516368 bytes (3755832 compressed) at 0x00010000 in 35.1 seconds
Verifying written data...
Hash of data verified.
Hard resetting via RTS pin...
```

**`Hash of data verified` là dòng quan trọng nhất.** Không có nó thì đừng rút cáp,
chạy lại lệnh.

---

## Hai loại file `.bin` — đừng nhầm

| File | Nạp ở địa chỉ | Khi nào dùng |
|---|---|---|
| `…-APP-0x10000.bin` | `0x10000` | **Bình thường dùng cái này.** Chỉ ghi phần ứng dụng, giữ nguyên bootloader và bảng phân vùng |
| `…-FULL-0x0.bin` | `0x0` | Chỉ khi bootloader hỏng. Ghi đè cả bootloader + bảng phân vùng |

Cách phân biệt nếu bạn quên file nào là file nào — ảnh gộp có magic bảng phân vùng
`aa50` tại offset `0x8000`:

```bash
xxd -s 0x8000 -l 2 file.bin
# aa50  -> ảnh MERGED, nạp tại 0x0
# khác  -> ảnh APP, nạp tại 0x10000
```

Ảnh gộp luôn lớn hơn ảnh app **đúng 65536 byte (0x10000)**.

---

## Cứu máy khi nạp hỏng

Vì X4 dùng USB-Serial/JTAG tích hợp trong chip chứ không phải chip UART rời, bootloader
ROM luôn còn đó. Kể cả khi ứng dụng hỏng hoàn toàn, bạn vẫn nạp lại được:

```bash
# nạp lại bản dump gốc, ghi đè toàn bộ
esptool --chip esp32c3 --port /dev/cu.usbmodem1101 --baud 921600 \
        write-flash 0 x4-goc-16MB.bin
```

Nếu máy không hiện cổng serial nữa: giữ nút nguồn ~10 giây cho tắt hẳn, cắm cáp,
rồi bấm nút nguồn. Một số máy cần bấm Reset rồi giữ Power.
