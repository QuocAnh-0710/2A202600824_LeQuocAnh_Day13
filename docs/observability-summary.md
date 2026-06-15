# Tóm tắt Lab Day 13 — Observability

---

## Observability là gì?

> "Khả năng nhìn vào bên trong hệ thống đang chạy mà không cần đoán mò"

Hình dung hệ thống AI như một **chiếc xe hơi**:
- **Logs** = hộp đen ghi lại mọi sự kiện
- **Traces** = GPS theo dõi từng chặng đường
- **Metrics** = đồng hồ tốc độ, nhiên liệu, nhiệt độ

---

## 3 trụ cột chính

### 1. Logs — "Chuyện gì đã xảy ra?"

```
Request vào → ghi log → Request ra
```

Log tốt phải có **đủ 4 thứ**:

| Thứ | Ví dụ | Tại sao cần |
|---|---|---|
| Timestamp | `2026-06-15T07:43:43Z` | Biết khi nào xảy ra |
| Correlation ID | `req-a3f7b2c1` | Ghép log của cùng 1 request |
| Context | `user_id_hash`, `feature` | Biết ai, làm gì |
| Không có PII | `[REDACTED_EMAIL]` | Bảo mật dữ liệu |

**Correlation ID** quan trọng nhất — không có nó, 100 request đồng thời = log lẫn lộn, không debug được.

---

### 2. Traces — "Bước nào chậm?"

```
chat-response (300ms)
├── rag-retrieve   (10ms)   ← tìm tài liệu
└── llm-generate   (150ms)  ← gọi AI
```

Khi có sự cố `rag_slow`:
```
chat-response (2700ms)
├── rag-retrieve   (2500ms) ← ĐÂY LÀ VẤN ĐỀ 🔴
└── llm-generate   (150ms)  ← bình thường ✅
```

Không có trace → chỉ biết "hệ thống chậm", không biết **chỗ nào** chậm.

---

### 3. Metrics — "Hệ thống có ổn không?"

| Metric | Ngưỡng SLO | Ý nghĩa |
|---|---|---|
| Latency P95 | < 3000ms | 95% request phải nhanh hơn 3s |
| Error Rate | < 2% | Tối đa 2% request bị lỗi |
| Cost/day | < $2.5 | Không cháy túi |
| Quality Score | > 0.75 | Câu trả lời đủ tốt |

---

## Những gì đã implement trong lab

```
Request → Middleware → API → Agent → LLM
             │           │      │
        Gán req ID   Ghi log  Ghi trace
        (req-xxxx)   đầy đủ   Langfuse
                      context
                     + scrub PII
```

### Middleware (middleware.py)
- Tạo `req-a3f7b2c1` cho mỗi request
- Gán vào **mọi log** trong request đó tự động
- Trả về trong response header

### Log Enrichment (main.py)
- Mỗi log tự động có: `user_id_hash`, `session_id`, `feature`, `model`, `env`
- Dùng `bind_contextvars()` — bind 1 lần, dùng ở khắp nơi

### PII Scrubbing (pii.py + logging_config.py)
```
"email là test@gmail.com"
        ↓  scrub_event chạy tự động
"email là [REDACTED_EMAIL]"
```
Các pattern đã chặn: email, SĐT VN, CCCD, thẻ tín dụng, hộ chiếu, địa chỉ VN

### Langfuse Tracing (tracing.py + agent.py)
- `@observe()` → tự động tạo span
- `capture_input=False` → không lộ raw args vào trace
- Set input/output thủ công với dữ liệu đã scrub

---

## Quy trình debug khi có sự cố

```
Alert kêu → Mở Metrics → Thấy latency tăng
                ↓
           Mở Traces → Tìm request chậm
                ↓
        Xem Waterfall → Thấy rag-retrieve = 2500ms
                ↓
           Mở Logs → Lọc theo correlation_id
                ↓
        Tắt incident → POST /incidents/rag_slow/disable
                ↓
           Viết Runbook → Phòng tránh lần sau
```

---

## 1 câu nhớ mãi

> **Metrics** cho biết *có vấn đề*, **Traces** cho biết *vấn đề ở đâu*, **Logs** cho biết *tại sao*.
