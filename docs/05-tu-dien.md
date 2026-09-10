# 05 — Từ điển

CrossPoint đọc từ điển định dạng **StarDict**. Cài rồi thì đang đọc sách, giữ nút
lâu trên một từ là tra được nghĩa ngay, không phải thoát ra.

## Cấu trúc thư mục

Mỗi bộ từ điển là một thư mục con trong `.dictionaries/`:

```
XTEINK/
└── .dictionaries/
    ├── vi-vi/
    │   ├── vi-vi.ifo         bắt buộc — file mô tả
    │   ├── vi-vi.idx         bắt buộc — chỉ mục
    │   ├── vi-vi.dict        nội dung (hoặc .dict.dz nếu nén)
    │   └── vi-vi.syn         tùy chọn — từ đồng nghĩa (hỗ trợ từ 1.6.0)
    ├── en-vi/
    └── vi-en/
```

Firmware chấp nhận cả `.dict` lẫn `.dict.dz` (bản nén dictzip). Nếu thiếu thì báo:

```
%s has no .dict or .dict.dz
```

**Tên file phải trùng tên thư mục.** Thư mục `en-vi/` thì các file phải là
`en-vi.ifo`, `en-vi.idx`, `en-vi.dict`.

## Kiểm tra một bộ từ điển

```bash
cat .dictionaries/vi-vi/vi-vi.ifo
```

Phải thấy đại loại:

```
StarDict's dict ifo file
version=2.4.2
wordcount=39885
idxfilesize=699299
bookname=Từ điển Tiếng Việt
sametypesequence=m
```

Nếu `idxfilesize` không khớp kích thước thật của file `.idx`, từ điển sẽ không nạp
được. Kiểm tra:

```bash
ls -l .dictionaries/vi-vi/vi-vi.idx
```

## Tìm từ điển ở đâu

Từ điển StarDict tiếng Việt tìm được trên các kho mã nguồn mở. Ba bộ đáng có:

| Bộ | Dùng khi |
|---|---|
| **vi-vi** | Đọc sách tiếng Việt, gặp từ Hán Việt hoặc từ cổ |
| **en-vi** | Đọc sách tiếng Anh |
| **vi-en** | Tra ngược |

Đọc truyện tiên hiệp thì **vi-vi rất đáng giá** — thể loại này dày đặc từ Hán Việt.

## Định dạng HTML

Từ 1.6.0, phần nghĩa có HTML sẽ được render bằng chính engine EPUB thay vì hiện ra
dạng thẻ thô. Từ điển có định dạng đẹp giờ hiển thị đúng.

## Gán phím tra từ

Trong `settings.json`:

```json
{ "longPressMenuFunction": 2 }
```

Bảng giá trị: `0=KOSync  1=Bookmark  2=Dictionary  3=Reader Menu  4=Disabled`

Đặt `2` là giữ nút lâu sẽ mở tra từ.
