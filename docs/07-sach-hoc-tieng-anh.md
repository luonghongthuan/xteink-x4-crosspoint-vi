# 07 — Sách học tiếng Anh

Repo kèm năm cuốn EPUB tự soạn, đặt trong [`books/`](../books/) dưới dạng văn bản thuần và dựng ra `.epub` bằng [`tools/build_epub.py`](../tools/build_epub.py).

| Sách | Nội dung |
|---|---|
| **Tiếng Anh Giao tiếp Công việc** | 10 chương theo tình huống: chào hỏi, họp, email, gọi điện, thuyết trình, đàm phán, báo cáo, góp ý, phỏng vấn, giữ quan hệ |
| **Tiếng Anh Du lịch** | 7 chương: sân bay, khách sạn, nhà hàng, đi lại, mua sắm, khẩn cấp, trò chuyện |
| **Tiếng Anh cho Dân IT** | 8 chương: standup, code review, báo lỗi, kiến trúc, vận hành, phỏng vấn kỹ thuật, viết tài liệu, từ viết tắt |
| **English Short Stories** | 5 truyện ngắn nguyên tác trình độ B1–B2, kèm chú giải và câu hỏi |
| **IT Deep Dives** | 5 bài kỹ thuật chuyên sâu bằng tiếng Anh: độ trễ, HTTP, idempotency, caching, chất lượng mã |

Mỗi chương gồm bảng từ vựng có phiên âm và nghĩa tiếng Việt, mẫu câu, và hội thoại mẫu.

> Phiên âm dùng ký hiệu quốc tế, cần font tải về mới hiện đúng. Chọn Literata hoặc Gentium Book Plus — xem [08 — Font](08-font-va-cau-hinh.md#ba-tầng-font-đừng-nhầm-lẫn).

## Dựng lại

```bash
pip install pillow          # chỉ cần cho split_epub, build_epub không cần gì
python3 tools/build_epub.py books/*.book -d out/
```

Sách sinh ra khoảng 10–22 KB mỗi cuốn.

---

## Tự soạn sách riêng

Định dạng nguồn là văn bản thuần, dễ sửa bằng bất kỳ trình soạn thảo nào.

### Phần đầu

```
@title: Tên sách
@author: Tác giả
@lang: vi
```

### Chương và mục

```
# Chương 1 — Tên chương

Đoạn văn thường viết thẳng, mỗi đoạn một dòng.

## Mục con
### Mục nhỏ hơn

- gạch đầu dòng
- gạch đầu dòng nữa

> Câu trích dẫn hoặc ghi chú quan trọng

---
```

Trong đoạn văn dùng được `**đậm**` và `*nghiêng*`.

### Bảng từ vựng

```
@vocab
negotiate | /nɪˈɡəʊʃieɪt/ | đàm phán | We need to negotiate the terms.
leverage | /ˈliːvərɪdʒ/ | đòn bẩy | Volume gives us leverage.
@end
```

Bốn cột: từ, phiên âm, nghĩa, câu ví dụ. Cột phiên âm để trống được — chỉ cần giữ dấu `|`.

### Hội thoại

```
@dialog
Linh: Hi, I don't think we've met.
David: David. Good to meet you.
@end
```

Tên người nói tự động in đậm nếu dài không quá 12 ký tự.

---

## Vì sao không dùng Calibre

Calibre và pandoc sinh EPUB cho màn hình màu. Ba thứ chúng thêm vào đều gây hại trên X4:

**Font nhúng trong sách.** Đây là nguyên nhân phổ biến nhất của crash `No glyph for codepoint` — font nhúng thường bị cắt bớt bộ ký tự và thiếu vùng tiếng Việt. Máy gặp chữ không có glyph rồi panic.

**CSS nhiều tầng.** Mỗi luật CSS phải được xử lý khi dựng chỉ mục trang. Sách có stylesheet vài chục KB khiến lần mở đầu tiên lâu hơn đáng kể.

**Ảnh nền và ảnh trang trí.** Màn hình 4 mức xám không thể hiện chúng, nhưng máy vẫn phải nạp và giải mã, tốn RAM trên con chip chỉ có 320KB.

Công cụ ở đây sinh sách chỉ có `h1/h2/h3/p/ul/blockquote/table` và **một bảng CSS 775 byte không khai báo kiểu chữ**, để font người đọc chọn được áp dụng.

> Có một chi tiết nhỏ đáng biết: chú thích trong bảng CSS cố tình **không nhắc tên** thuộc tính kiểu chữ hay quy tắc nhúng font. Các công cụ dọn font nhúng (kể cả `split_epub.py` trong repo này) tìm chúng bằng biểu thức chính quy vốn không phân biệt được đâu là chú thích — một chú thích nhắc tới chúng sẽ bị cắt nhầm cùng với đoạn CSS phía sau.

## Kiểm tra sách vừa dựng

```bash
python3 tools/split_epub.py out/01-business-english.epub -d /tmp/check --volumes 2
```

Nếu `split_epub.py` đọc được và liệt kê đúng số chương với tiêu đề, sách hợp lệ.
