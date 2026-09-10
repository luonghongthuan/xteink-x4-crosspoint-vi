# 03 — Chuẩn bị thẻ nhớ

## Format

CrossPoint đọc **FAT32** ổn định nhất. Thẻ 32GB trở xuống nên format FAT32; thẻ lớn
hơn Windows/macOS hay mặc định exFAT — nên ép về FAT32.

```bash
# macOS
diskutil list                                    # tìm đúng số hiệu đĩa!
diskutil unmountDisk /dev/disk4
diskutil eraseDisk FAT32 XTEINK MBRFormat /dev/disk4
```

```bash
# Linux
sudo mkfs.vfat -F 32 -n XTEINK /dev/sdX1
```

> Kiểm tra ba lần số hiệu đĩa. `eraseDisk` nhầm ổ là mất sạch dữ liệu.

## Tắt Spotlight (macOS) — bắt buộc

macOS tự rải file rác lên thẻ. Đây là **nguyên nhân thường gặp nhất** khiến X4 báo
`SD card error`, và cũng làm thư viện sách hiển thị sai.

```bash
mdutil -i off /Volumes/XTEINK
mdutil -E /Volumes/XTEINK
```

Sau **mỗi lần** chép file vào thẻ từ macOS, dọn rác:

```bash
find /Volumes/XTEINK -name '._*'      -delete
find /Volumes/XTEINK -name '.DS_Store' -delete
rm -rf /Volumes/XTEINK/.Spotlight-V100 /Volumes/XTEINK/.Trashes /Volumes/XTEINK/.fseventsd
```

**Vì sao quan trọng:** macOS tạo file "AppleDouble" `._TenSach.epub` bên cạnh mỗi
`TenSach.epub`. CrossPoint đếm cả chúng, nên **thư viện 95 cuốn sẽ hiện thành 190
cuốn**, mỗi cuốn có một bản sao rỗng không mở được.

## Chép sách từ macOS — dùng `ditto`, đừng dùng `rsync`

`rsync` và `cp` gặp lỗi với tên file tiếng Việt có dấu trên FAT32 do macOS trả về
tên ở dạng NFD (tách dấu) nhưng tra ngược lại không ra:

```
rsync: "Xa Ngoài Kia Nơi Loài Tôm Hát.epub": could not stat: No such file or directory
```

`ditto` xử lý đúng:

```bash
ditto /nguon/book /Volumes/XTEINK/book
```

---

## Cấu trúc thư mục

```
XTEINK/
├── book/                     sách, chia thư mục con tùy ý
│   ├── Tiên Hiệp/
│   └── Tiểu Thuyết/
├── sleep/                    hình nền ngủ (BMP 480×800)
├── .sleep-overlay/           ảnh overlay trong suốt (PNG/BMP) — mới từ 1.6.0
├── .fonts/                   font tải về, mỗi họ một thư mục
├── .dictionaries/            từ điển StarDict
└── .crosspoint/
    ├── settings.json         cấu hình — firmware đọc trực tiếp file này
    ├── wifi.json             mạng WiFi đã lưu
    ├── recent.json           sách gần đây
    ├── state.json            đang đọc cuốn nào
    └── epub_<hash>/          cache chỉ mục + ảnh bìa từng cuốn
```

> `settings.bin` (41 byte) là **định dạng cũ**, không chứa nổi 60 tuỳ chọn.
> Firmware đọc `settings.json`. Cứ sửa file JSON.

---

## Cấu hình tối ưu cho tiếng Việt

Ghi vào `.crosspoint/settings.json`. Bốn giá trị quan trọng nhất:

| Khóa | Đặt | Vì sao |
|---|---|---|
| `lineSpacing` | `2` (Wide) | Tiếng Việt có dấu chồng hai tầng (ộ, ầ, ữ, ể). Để `0` (Tight) là dấu bị cắt hoặc dính vào dòng trên |
| `paragraphAlignment` | `1` (Left) | Tiếng Việt không ngắt từ được. Để `0` (Justify) sẽ tạo khoảng trắng rỗ giữa các chữ |
| `hyphenationEnabled` | `0` | Ngắt từ tiếng Việt cho kết quả sai |
| `clockUtcOffsetQ` | `28` | Đơn vị là **phần tư giờ**: 7 × 4 = 28 cho UTC+7 |

Bảng giá trị các enum (rút ra bằng cách đọc thứ tự chuỗi trong firmware):

```
lineSpacing         0=Tight   1=Normal   2=Wide     3=Extra Wide
paragraphAlignment  0=Justify 1=Left     2=Center   3=Right
refreshFrequency    0=1 trang 1=5 trang  2=10 trang 3=15 trang  4=30 trang
statusBar*          0=Never   1=In Reader 2=Always
```

Vài tuỳ chọn khác đáng đổi:

```json
{
  "refreshFrequency": 1,          // 5 trang refresh 1 lần — ít bóng mờ hơn
  "extraParagraphSpacing": 1,     // tách đoạn rõ
  "screenMargin": 6,
  "textAntiAliasing": 1,
  "fadingFix": 1,
  "statusBarClock": 1,
  "statusBarBattery": 1,
  "language": "VI"
}
```

---

## Đặt sẵn WiFi

Gõ mật khẩu WiFi bằng nút bấm trên màn hình e-ink rất cực. Tạo sẵn
`.crosspoint/wifi.json` là máy tự nối khi khởi động.

Mật khẩu **không lưu dạng thô** — nó được XOR với địa chỉ MAC của máy rồi mã hóa
base64. Nghĩa là **file này chỉ dùng được cho đúng máy đó**, và bạn phải biết MAC.

```bash
esptool --port /dev/cu.usbmodem1101 chip-id | grep MAC
```

```python
import base64, zlib, json

MAC = bytes.fromhex("aabbccddeeff")     # thay bằng MAC máy bạn

def obf(pw):
    raw = pw.encode()
    return base64.b64encode(bytes(b ^ MAC[i % 6] for i, b in enumerate(raw))).decode()

nets = [("TenWifi", "MatKhau")]
doc = {
    "lastConnectedSsid": nets[0][0],
    "credentials": [
        {"ssid": s, "password_obf": obf(p), "password_len": len(p),
         "password_crc32": zlib.crc32(p.encode()) & 0xFFFFFFFF}
        for s, p in nets
    ],
}
open("wifi.json", "w").write(json.dumps(doc, separators=(",", ":")))
```

> X4 dùng ESP32-C3 nên **chỉ bắt được WiFi 2.4GHz**. Mạng 5GHz máy sẽ không thấy.

> Cách che giấu này chỉ chống nhìn lướt, **không phải mã hóa**. Ai có file và biết
> MAC là giải ra mật khẩu trong vài giây. Đừng đưa `wifi.json` lên GitHub.

---

## Tháo thẻ an toàn

**Luôn eject bằng lệnh trước khi rút.** Rút nóng lúc hệ thống đang ghi sẽ làm hỏng
bảng thư mục FAT — và kiểu hỏng đó `fsck` không phát hiện được (xem
[06 — Khắc phục sự cố](06-su-co.md)).

```bash
sync
diskutil eject /dev/disk4          # macOS
umount /mnt/sd && sync             # Linux
```
