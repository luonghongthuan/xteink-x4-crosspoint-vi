# 07 — Sách tự soạn

Repo kèm **11 cuốn EPUB** tự soạn, đặt trong [`books/`](../books/) dưới dạng văn bản thuần và dựng ra `.epub` bằng [`tools/build_epub.py`](../tools/build_epub.py).

## Sách học tiếng Anh cho người lớn

| Sách | Nội dung |
|---|---|
| **Tiếng Anh Giao tiếp Công việc** | 10 chương theo tình huống: chào hỏi, họp, email, gọi điện, thuyết trình, đàm phán, báo cáo, góp ý, phỏng vấn, giữ quan hệ |
| **Tiếng Anh Du lịch** | 7 chương: sân bay, khách sạn, nhà hàng, đi lại, mua sắm, khẩn cấp, trò chuyện |
| **Tiếng Anh cho Dân IT** | 8 chương: standup, code review, báo lỗi, kiến trúc, vận hành, phỏng vấn kỹ thuật, viết tài liệu, từ viết tắt |
| **English Short Stories** | 5 truyện ngắn nguyên tác trình độ B1–B2, kèm chú giải và câu hỏi |
| **IT Deep Dives** | 5 bài kỹ thuật chuyên sâu bằng tiếng Anh: độ trễ, HTTP, idempotency, caching, chất lượng mã |

Mỗi chương gồm bảng từ vựng có phiên âm và nghĩa tiếng Việt, mẫu câu, và hội thoại mẫu.

> Phiên âm dùng ký hiệu quốc tế, cần font tải về mới hiện đúng. Chọn Literata hoặc Gentium Book Plus — xem [08 — Font](08-font-va-cau-hinh.md#ba-tầng-font-đừng-nhầm-lẫn).

## Sách cho thiếu nhi (10–12 tuổi)

| Sách | Nội dung |
|---|---|
| **Chuyện Của Những Đứa Trẻ Không Chịu Ngồi Yên** | 6 truyện ngắn nguyên tác, nhân vật chính là các bạn nhỏ tò mò và bướng bỉnh. Mỗi truyện kèm câu hỏi suy nghĩ. |
| **Những Điều Kỳ Lạ Mà Có Thật** | Khoa học khám phá: con sam máu xanh, ếch đóng băng, kiến đếm bước chân, kim loại tan trong lòng bàn tay, cây biết đếm. Kèm 4 thí nghiệm làm được ở nhà. |
| **Những Người Việt Đáng Nhớ** | 12 danh nhân và anh hùng: Hai Bà Trưng, Bà Triệu, Ngô Quyền, Trần Hưng Đạo, Nguyễn Trãi, Quang Trung, Chu Văn An, Lê Quý Đôn, Tôn Thất Tùng, Lương Định Của, Nguyễn Thị Định. |
| **Người Bắt Đầu Từ Số Không** | Chuyện doanh nhân: Bạch Thái Bưởi, Mary Kay Ash, Andrew Carnegie, anh em Wright. Có một chương riêng về **những điều sách vở thường bỏ qua**. |
| **Reading Time** | 8 bài luyện đọc hiểu tiếng Anh trình độ A2, kèm từ mới và câu hỏi. |
| **Flyers — Từ vựng và Mẫu câu ôn thi** | Ôn Cambridge A2 Flyers: 60 từ theo 6 chủ đề, mẫu câu ngữ pháp, mẹo làm từng phần thi, kế hoạch ôn 30 ngày. |

Ba điểm đáng chú ý trong nhóm sách thiếu nhi:

**Không tô hồng.** Sách doanh nhân có hẳn một chương nói rằng ta chỉ nghe chuyện người thành công vì người thất bại không được viết sách, rằng may mắn có vai trò lớn hơn ta tưởng, và rằng Carnegie xây 2.500 thư viện nhưng công nhân trong nhà máy của ông thì làm việc rất khổ.

**Dạy nghi ngờ.** Chuyện "ông Sanders bị từ chối 1009 lần" được kể kèm ghi chú rằng con số ấy không có bằng chứng chắc chắn. Thí nghiệm nến hút nước được kể kèm giải thích rằng **lời giải thích phổ biến của nó là sai**.

**Nhân vật nữ chiếm phần lớn** trong tập truyện ngắn và xuất hiện đều trong sách danh nhân — vì sách soạn cho một bạn gái 10 tuổi.


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
