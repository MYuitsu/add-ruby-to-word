# Thêm Ruby (Hiragana) cho Kanji trong Word Document

Chương trình này giúp bạn tự động thêm ruby (hiragana) cho các chữ kanji trong file Word dựa trên dictionary đã định nghĩa sẵn.

## Cài đặt

1. Cài đặt Python (phiên bản 3.6 trở lên)
2. Cài đặt thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## Cách sử dụng

### Bước 1: Chuẩn bị file

- Đặt file Word cần xử lý vào thư mục và đổi tên thành `input.docx`
- Chỉnh sửa file `dictionary.json` để thêm các cặp kanji-hiragana mong muốn

### Bước 2: Chạy chương trình

#### Phiên bản đơn giản (khuyến nghị):
```bash
python add_ruby_simple.py
```

Phiên bản này sẽ thêm hiragana vào sau kanji với format: `kanji(hiragana)`

#### Phiên bản ruby element:
```bash
python add_ruby.py
```

Phiên bản này cố gắng tạo ruby element thực sự trong Word (có thể không hoạt động với tất cả phiên bản Word).

### Bước 3: Kiểm tra kết quả

File output sẽ được lưu với tên `output_with_ruby.docx`

## Định dạng Dictionary

File `dictionary.json` có cấu trúc:

```json
{
  "kanji": "hiragana",
  "日本": "にほん",
  "学校": "がっこう"
}
```

## Ví dụ

Input: `私は日本の学校で勉強しています。`

Output (phiên bản simple): `私は日本(にほん)の学校(がっこう)で勉強(べんきょう)しています。`

## Lưu ý

- Chương trình sẽ thay thế từ dài nhất trước để tránh xung đột
- Hỗ trợ cả text trong paragraph và table
- Font được set thành MS Gothic để hiển thị tiếng Nhật tốt hơn
- Có thể mở rộng dictionary bằng cách thêm các cặp kanji-hiragana mới
