# 09 — Điều khiển lật trang Bluetooth

X4 dùng chip **ESP32-C3**, vốn có sẵn **BT 5 (LE)**. Firmware gốc không bật, nhưng SDK đã có sẵn thư viện `BleKeyboardHost` — một BLE HID **host** hoàn chỉnh (vai trò central). Bản vá trong repo này chỉ bật nó lên và nối vào phần đọc sách.

Kết quả: mua một chiếc remote lật trang Bluetooth rẻ tiền, ghép đôi một lần, rồi nằm đọc mà không phải với tay bấm nút.

---

## Chi phí thật, đo trên bản dựng

| | Trước | Sau | Chênh |
|---|---|---|---|
| Flash | 84,2% | **87,9%** | +237 KB |
| RAM tĩnh | 17,3% | **20,0%** | +8,9 KB |

Còn khoảng **792 KB flash trống**.

> Có một cái bẫy khi đo. Lần build đầu, tôi chỉ thêm cờ và thư viện NimBLE mà chưa có dòng code nào gọi tới — kết quả ra +28 KB, nghe rất rẻ. Con số đó **sai**: trình liên kết vứt bỏ gần hết NimBLE vì không ai tham chiếu. Chỉ khi nối thật vào vòng lặp chính mới hiện ra con số +237 KB. Đo một tính năng chưa được gọi thì không đo được gì.

Ngoài phần tĩnh, NimBLE còn chiếm **vài chục KB heap** khi đang chạy. Vì thế mã ở đây gọi `end()` chứ không phải `disconnect()` khi bạn tắt Bluetooth — `end()` trả RAM về heap, thứ mà giải nén EPUB cần.

So sánh: CrossPet cũng có bản BLE, nhưng họ phải **tắt ảnh và CSS** mới đủ chỗ. Bản này không phải hy sinh gì.

---

## Bật và ghép đôi

**1.** `Settings → System → Bluetooth` → bật

**2.** `Settings → System → Điều khiển lật trang`

**3.** Đưa remote vào chế độ ghép đôi (thường là giữ nút nguồn tới khi đèn nháy)

**4.** Chờ máy quét xong, chọn thiết bị, bấm **Confirm**

Ghép đôi được lưu vào NVS, nên **lần sau máy tự kết nối** khi bật Bluetooth. Màn hình này chỉ cần vào một lần cho mỗi remote.

Ký hiệu trong danh sách:

- `*` — đã ghép đôi trước đó
- `>` — đang kết nối
- không dấu — thiết bị mới quét thấy

Muốn xoá một thiết bị đã ghép: chọn nó rồi **giữ Confirm**, nhãn nút đổi thành *Xoá?*, bấm Confirm lần nữa.

---

## Phím nào lật trang

Các hãng remote không thống nhất phím gửi đi, nên bản vá nhận cả họ:

| Hướng | Phím chấp nhận |
|---|---|
| **Trang sau** | Right · Down · PageDown · Enter · Space · `n` |
| **Trang trước** | Left · Up · PageUp · Backspace · `p` |

Nhận rộng thế này không tốn gì, mà tránh được cảnh mua remote về rồi phát hiện nó gửi `Down` trong khi máy chỉ chờ `PageDown`.

---

## Chọn remote thế nào

Điều **bắt buộc**: remote phải là **Bluetooth Low Energy (BLE)**, không phải Bluetooth Classic.

ESP32-C3 **không có radio Bluetooth Classic** — đây là giới hạn phần cứng, không sửa bằng firmware được. Thư viện ghi rõ điều này trong phần đầu mã nguồn.

Cách nhận biết khi mua:

- Ghi **BLE**, **Bluetooth 4.0+**, hoặc **"dùng cho iPad/Kindle"** → gần như chắc chắn dùng được
- Ghi **Bluetooth 3.0** hoặc chỉ ghi "Bluetooth" chung chung → có thể là Classic, rủi ro
- Remote bán cho máy đọc sách nói chung đều là BLE HID keyboard, nên hợp

---

## Bluetooth và WiFi loại trừ nhau — firmware tự enforcing

ESP32-C3 chỉ có **một bộ radio 2.4GHz** dùng chung, và heap chỉ 234KB. Đo trên máy
thật: bật Bluetooth khi stack WiFi còn thường trực làm heap tụt từ 43KB xuống
**9KB**, và lần cấp phát kế tiếp — kể cả chỉ để vẽ màn hình kết quả — gọi `abort()`
và máy khởi động lại.

Nên bản vá không để hai thứ cùng sống:

- **Bật Bluetooth** → firmware tắt WiFi trước (`WiFi.disconnect(true)` + `WIFI_OFF`),
  rồi mới khởi động NimBLE. Nếu heap đang phân mảnh (vừa đọc sách xong, cache font
  còn giữ), nó từ chối bật và ghi log lý do.
- **Mở bất kỳ màn hình nào dùng WiFi** (WiFi, chuyển file, OPDS, KOReader, OTA, tải
  font, đồng bộ giờ) → firmware gọi `blepage::suspendForWifi()`: tắt NimBLE, trả heap
  về, và **tắt luôn toggle Bluetooth** (ghi xuống thẻ).

Hệ quả cần biết: sau một phiên WiFi, Bluetooth ở trạng thái tắt. Muốn dùng remote
lại thì bật lại toggle — máy sẽ tắt WiFi phiên đó. Không dùng được cả hai cùng lúc,
bao giờ cũng vậy, trên phần cứng này.

---

## Nếu không ghép được

**Không thấy thiết bị nào** — kiểm tra remote đã vào chế độ ghép đôi chưa (đèn phải nháy, không phải sáng liên tục). Máy quét 6 giây mỗi lần vào màn hình; thoát ra vào lại để quét tiếp.

**Thấy nhưng kết nối thất bại** — dòng trạng thái trên cùng sẽ hiện lý do. Thường là remote đã ghép với máy khác; xoá ghép đôi ở máy kia trước.

**Ghép được nhưng không lật trang** — remote có thể gửi phím ngoài danh sách trên. Danh sách nằm trong `src/util/BlePageTurner.cpp`, hàm `isNextKey` và `isPrevKey`; thêm phím của bạn vào rồi dựng lại.

**Máy chậm hẳn sau khi bật** — tắt Bluetooth đi. Radio dùng chung với WiFi, và NimBLE giữ heap.
