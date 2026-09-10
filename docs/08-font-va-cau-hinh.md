# 08 — Font và cấu hình đọc

## Ba tầng font, đừng nhầm lẫn

Máy dùng font ở ba chỗ khác nhau, và chúng **không phải một**:

| Tầng | Nằm ở đâu | Bộ ký tự | Dùng cho |
|---|---|---|---|
| Font giao diện | Nhúng trong firmware | preset `builtin` | Menu, cài đặt, màn hình ngủ |
| Font đọc mặc định | Nhúng trong firmware | preset `builtin` | Nội dung sách |
| Font tải về | `.fonts/` trên thẻ | preset `latin-ext` + `ipa-chars` | Nội dung sách |

Sự khác biệt quan trọng nhất: **preset `builtin` không có vùng ký hiệu phiên âm quốc tế** (`U+0250–U+02FF`). Font tải về thì có.

Hệ quả thực tế: chữ `/nɪˈɡəʊʃieɪt/` hiện ra ô vuông nếu bạn đọc bằng font mặc định, nhưng hiện đúng nếu bạn chọn một font trong `.fonts/`. Đây là lý do các sách học tiếng Anh trong repo này nên đọc bằng font tải về.

Kiểm chứng bằng chính công cụ của repo firmware:

```bash
cd lib/EpdFont/scripts
python3 fontconvert_sdcard.py --list-presets
```

Cả hai preset đều phủ đủ tiếng Việt (`U+1EA0–U+1EF9`, `ơ ư Ơ Ư`), nên **chữ Việt có dấu không bao giờ là vấn đề** với font chính thức. Chỉ font tuỳ chỉnh của bên thứ ba mới gây lỗi thiếu glyph.

---

## Sáu font nên giữ

Kho font chính thức có 33 họ, nhưng phần lớn dành cho tiếng Ả Rập, Do Thái, Hàn. Với người đọc tiếng Việt và tiếng Anh, sáu họ này là đủ:

| Font | Vì sao |
|---|---|
| **Bitter** | Họ duy nhất được mô tả là *"slab serif designed for e-ink"*. Nét đều nên để lại ít bóng mờ nhất. CrossInk cũng chọn font này làm mặc định. |
| **Literata** | Font của Google Play Books, thiết kế riêng cho màn hình. Được cộng đồng máy đọc sách đánh giá cao nhất trong nhóm serif. |
| **Gentium Book Plus** | SIL làm, cho các ngôn ngữ nhiều dấu. **Dấu chồng hai tầng của tiếng Việt** (ế, ộ, ữ) được vẽ cẩn thận nhất trong cả kho. |
| **Merriweather** | Thiết kế cho đọc dài trên màn hình, thân chữ dày dặn, giữ nét tốt ở cỡ nhỏ. |
| **Atkinson Hyperlegible Next** | Font hỗ trợ thị lực kém: các chữ dễ nhầm (`I l 1`, `O 0`, `rn m`) được vẽ khác nhau rõ rệt. Rất hợp khi **học từ mới** — bạn cần nhìn đúng mặt chữ. |
| **Noto Serif Extended** | Lưới an toàn: phủ Unicode rộng nhất, dùng khi sách có ký tự lạ. |

Tải từ [crosspoint-fonts](https://github.com/crosspoint-reader/crosspoint-fonts/releases) — mỗi họ có 4 cỡ (12/14/16/18), đặt vào `.fonts/<TênHọ>/`.

```
.fonts/
├── Bitter/
│   ├── Bitter_12.cpfont
│   ├── Bitter_14.cpfont
│   ├── Bitter_16.cpfont
│   └── Bitter_18.cpfont
├── Literata/
└── ...
```

Kiểm tra file tải về đúng định dạng:

```bash
head -c 6 Bitter_14.cpfont      # phải in ra: CPFONT
```

## Vì sao nên bỏ bớt

Trên thẻ 64GB thì 38MB font không đáng kể — **lý do bỏ bớt không phải dung lượng**. Là vì:

- Máy quét thư mục `.fonts/` lúc khởi động. Ít họ thì khởi động nhanh hơn.
- Menu chọn font ngắn lại, đỡ phải cuộn qua 16 mục để tới font mình dùng.
- Font đơn cách (IBM Plex Mono, Source Code Pro) vô dụng cho đọc văn xuôi.

Bỏ 11 họ, giữ 6, giảm từ 38MB xuống 17MB.

---

## Cấu hình đọc tối ưu

Ghi vào `.crosspoint/settings.json`:

```json
{
  "sdFontFamilyName": "Bitter",
  "fontPointSize": 14,
  "lineSpacing": 2,
  "paragraphAlignment": 1,
  "hyphenationEnabled": 0,
  "extraParagraphSpacing": 1,
  "screenMargin": 7,
  "textAntiAliasing": 1,
  "fadingFix": 1,
  "smartRefresh": 1,
  "refreshFrequency": 2
}
```

### Vì sao từng giá trị

**`lineSpacing: 2` (Wide)** — thứ quan trọng nhất cho tiếng Việt. Dấu chồng hai tầng cần chỗ phía trên chữ; để `0` (Tight) thì dấu bị cắt hoặc dính vào dòng trên.

**`paragraphAlignment: 1` (Left)** — tiếng Việt không ngắt từ được. Chọn Justify thì máy phải giãn khoảng trắng giữa các chữ để căn đều hai bên, tạo ra những "dòng sông" trắng chạy dọc trang.

**`hyphenationEnabled: 0`** — cùng lý do. Thuật toán ngắt từ không có luật tiếng Việt, ngắt sai chỗ.

**`fontPointSize: 14`** — với màn 480×800 và lề 7, cỡ 14 cho khoảng 38–42 ký tự một dòng. Đây là khoảng dễ đọc nhất; dòng dài hơn 70 ký tự khiến mắt khó tìm dòng kế tiếp.

**`refreshFrequency: 2` (10 trang) kèm `smartRefresh: 1`** — hai giá trị này phải chọn cùng nhau. Làm tươi thông minh trừ ngân sách 1–3 bậc tuỳ độ dày chữ, nên đặt ngân sách 10 sẽ cho khoảng thực tế 4–10 trang.

> Nếu đặt `refreshFrequency: 1` (5 trang) cùng với `smartRefresh`, một trang đặc chữ tiêu 3 bậc sẽ khiến máy làm tươi sau mỗi 2 trang — màn hình chớp liên tục. Đây là cái bẫy dễ mắc khi bật cả hai.

### Bảng giá trị enum

```
lineSpacing         0=Tight   1=Normal    2=Wide      3=Extra Wide
paragraphAlignment  0=Justify 1=Left      2=Center    3=Right
refreshFrequency    0=1 trang 1=5 trang   2=10 trang  3=15  4=30  5=Never
statusBar*          0=Never   1=In Reader 2=Always
sleepScreen         2=Custom  8=Dashboard 9=Từ vựng   10=Ảnh + Từ vựng
```

---

## Chọn font theo việc đang làm

Không có font tốt nhất cho mọi thứ. Đổi theo nội dung:

| Đang đọc | Font | Lý do |
|---|---|---|
| Truyện dài tiếng Việt | **Bitter** hoặc **Literata** | Đọc hàng giờ, cần nét bền và ít bóng mờ |
| Sách nhiều dấu, thơ, chữ Nôm | **Gentium Book Plus** | Dấu vẽ chuẩn nhất |
| Sách học tiếng Anh có phiên âm | **Literata** hoặc **Gentium** | Có vùng ký hiệu phiên âm |
| Học từ mới, mắt mỏi | **Atkinson Hyperlegible Next** | Chữ dễ nhầm được vẽ khác hẳn nhau |
| Ngoài trời nắng | Cỡ **16** thay vì 14 | Tương phản thực tế giảm khi có ánh sáng chói |

Đổi font làm **mất cache dựng trang** của mọi sách — lần mở kế tiếp sẽ lâu hơn vài giây trong khi máy dựng lại chỉ mục. Đó là chuyện bình thường, không phải lỗi.
