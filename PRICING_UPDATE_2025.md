# 🚀 OpenAI Pricing Update - Tháng 7/2025

## 💰 BẢNG GIÁ MỚI NHẤT

### 🔥 **Models được RECOMMEND cho dịch thuật:**

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Ưu điểm | Nhược điểm |
|-------|---------------------|----------------------|---------|------------|
| **🌟 gpt-4.1-mini** | $0.40 | $1.60 | ⭐ **BEST CHOICE** - Cân bằng hoàn hảo | - |
| **⚡ gpt-4.1-nano** | $0.10 | $0.40 | RẺ NHẤT, nhanh nhất | Chất lượng thấp hơn |
| **🧠 gpt-4.1** | $2.00 | $8.00 | Chất lượng cao nhất | Đắt nhất |

### 📊 **So sánh với models cũ:**

| Model (Legacy) | Input (per 1K tokens) | Output (per 1K tokens) | Status |
|----------------|---------------------|----------------------|--------|
| gpt-3.5-turbo | $0.0015 | $0.002 | ⚠️ Legacy |
| gpt-4 | $0.03 | $0.06 | ⚠️ Legacy |
| gpt-4-turbo | $0.01 | $0.03 | ⚠️ Legacy |

## 🎯 **Ước tính chi phí cho dịch thuật:**

### Ví dụ: 1000 đoạn văn tiếng Nhật (trung bình 50 tokens/đoạn)

```
Input: 1000 đoạn × 50 tokens = 50,000 tokens = 0.05M tokens
Output: ~25,000 tokens = 0.025M tokens (ước tính)
```

| Model | Chi phí Input | Chi phí Output | **Tổng** |
|-------|--------------|----------------|----------|
| **gpt-4.1-mini** | $0.02 | $0.04 | **$0.06** ⭐ |
| **gpt-4.1-nano** | $0.005 | $0.01 | **$0.015** 💰 |
| **gpt-4.1** | $0.10 | $0.20 | **$0.30** 🧠 |
| gpt-3.5-turbo | $0.075 | $0.05 | $0.125 |

## 🔧 **Cấu hình được đề xuất:**

### 1. **Dự án cá nhân / Test:**
```python
model = "gpt-4.1-nano"  # Rẻ nhất: $0.10/$0.40 per 1M
```

### 2. **Dự án thương mại / Chất lượng cao:**
```python
model = "gpt-4.1-mini"  # Cân bằng: $0.40/$1.60 per 1M
```

### 3. **Dự án quan trọng / Chất lượng tối đa:**
```python
model = "gpt-4.1"       # Tốt nhất: $2.00/$8.00 per 1M
```

## ⚡ **Tối ưu hóa chi phí:**

### 1. **Batch Processing** (đã implement):
- Gộp 15 đoạn/request → Tiết kiệm 90% API calls
- Smart batching theo context length

### 2. **Cache System** (đã implement):
- Không dịch lại đoạn đã có
- Chia sẻ cache giữa projects

### 3. **Model Selection Strategy:**
```python
# Chiến lược thông minh
if document_importance == "high":
    model = "gpt-4.1"
elif document_size > 10000:
    model = "gpt-4.1-mini"  # Cân bằng cho doc lớn
else:
    model = "gpt-4.1-nano"  # Rẻ cho doc nhỏ
```

## 📈 **Hiệu suất so với Gemini:**

| Metric | Gemini (Free) | GPT-4.1-nano | GPT-4.1-mini | GPT-4.1 |
|--------|---------------|-------------|-------------|---------|
| **Chi phí** | $0 (có hạn) | ~$0.015/1000 đoạn | ~$0.06/1000 đoạn | ~$0.30/1000 đoạn |
| **Tốc độ** | 15 đoạn/phút | 900+ đoạn/phút | 900+ đoạn/phút | 600+ đoạn/phút |
| **Chất lượng** | 7/10 | 8/10 | 9/10 | 10/10 |
| **Giới hạn** | 50 đoạn/ngày | Unlimited | Unlimited | Unlimited |

## 🎯 **Khuyến nghị cuối cùng:**

### ✅ **CHỌN gpt-4.1-mini** nếu:
- Cần chất lượng dịch thuật tốt
- Có ngân sách vừa phải
- Xử lý tài liệu lớn thường xuyên
- **Cost: ~$0.06 cho 1000 đoạn**

### ✅ **CHỌN gpt-4.1-nano** nếu:
- Ngân sách eo hẹp
- Chỉ cần chất lượng acceptable
- Test hoặc prototype
- **Cost: ~$0.015 cho 1000 đoạn**

### ✅ **CHỌN gpt-4.1** nếu:
- Dự án quan trọng
- Cần chất lượng tuyệt đối
- Có ngân sách thoải mái
- **Cost: ~$0.30 cho 1000 đoạn**

## 🛠️ **Update Instructions:**

1. **Cập nhật config:**
```bash
# Sửa file config_chatgpt.py
model = "gpt-4.1-mini"  # Hoặc model khác
```

2. **Test với model mới:**
```bash
python demo_comparison.py
```

3. **Monitor cost:**
- Script sẽ hiển thị real-time cost
- Check usage tại: https://platform.openai.com/usage

---

**📝 Note:** Pricing có thể thay đổi. Check latest tại: https://openai.com/api/pricing/
