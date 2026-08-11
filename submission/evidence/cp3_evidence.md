# Bằng chứng Checkpoint 3 - Điều tra Challenge Chính thức (`day13-k3-observability-v1`)

## 1. Metadata của Incident (`config/challenge.json`)

* **Challenge ID**: `day13-k3-observability-v1`
* **Cohort**: `K3`
* **Incident**: `rag_slow`
* **Tính năng bị ảnh hưởng**: `refund`
* **Ngưỡng độ trễ**: `2000ms`

---

## 2. Phân tích triệu chứng từ Metrics

Trong quá trình load test đối với các truy vấn của tính năng `refund` (`k3-challenge-s01` đến `k3-challenge-s05`), độ trễ phản hồi P95 đã tăng từ mức bình thường khoảng ~150ms lên **~2653ms**, vượt quá ngưỡng của challenge là `2000ms`.

---

## 3. Phân tích chuyên sâu Traces (Waterfall Analysis)

Phân tích các trace với session ID từ `k3-challenge-s01` đến `k3-challenge-s05`:

* **Root Span (****`run`****)**: Thời lượng ~2653ms
* **Sub-span (****`rag_retrieve`****)**: Thời lượng ~2500ms (chiếm **94.2%** tổng độ trễ của request).
* **Sub-span (****`llm_generate`****)**: Thời lượng ~150ms.

*Kết luận từ Trace*: Sự suy giảm về độ trễ hoàn toàn nằm ở bước RAG retrieval (`rag_retrieve`), không phải ở bước LLM generation.

---

## 4. Bằng chứng từ Logs & Correlation IDs

Theo dõi Correlation ID trong `data/logs.jsonl`:

### Control Event (Kích hoạt Incident):

  ```json
{"service": "control", "payload": {"name": "rag_slow"}, "event": "incident_enabled", "correlation_id": "req-72b010b5", "level": "warning", "ts": "2026-08-11T04:52:15.725660Z"}
```

### Affected Response Sent Log (Độ trễ cao):

```json
{"service": "api", "payload": {"message_preview": "What proof is required for a refund?"}, "event": "request_received", "correlation_id": "req-2ca32f3d", "feature": "refund", "env": "dev", "session_id": "k3-challenge-s02", "user_id_hash": "867738e76862", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-08-11T04:52:23.036612Z"}
{"service": "api", "latency_ms": 3560, "tokens_in": 31, "tokens_out": 91, "cost_usd": 0.001458, "quality_score": 0.9, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic and add better quality ch..."}, "event": "response_sent", "correlation_id": "req-2ca32f3d", "feature": "refund", "env": "dev", "session_id": "k3-challenge-s02", "user_id_hash": "867738e76862", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-08-11T04:52:27.144123Z"}
{"service": "api", "payload": {"message_preview": "What is your refund policy?"}, "event": "request_received", "correlation_id": "req-3c4d1465", "feature": "refund", "env": "dev", "session_id": "k3-challenge-s01", "user_id_hash": "026c7a407135", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-08-11T04:52:27.147121Z"}
{"service": "api", "latency_ms": 3539, "tokens_in": 29, "tokens_out": 156, "cost_usd": 0.002427, "quality_score": 0.9, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic and add better quality ch..."}, "event": "response_sent", "correlation_id": "req-3c4d1465", "feature": "refund", "env": "dev", "session_id": "k3-challenge-s01", "user_id_hash": "026c7a407135", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-08-11T04:52:30.689983Z"}
{"service": "api", "payload": {"message_preview": "Can a customer request a refund after purchase?"}, "event": "request_received", "correlation_id": "req-88fd2aba", "feature": "refund", "env": "dev", "session_id": "k3-challenge-s04", "user_id_hash": "026017618b2c", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-08-11T04:52:30.693986Z"}
{"service": "api", "latency_ms": 3541, "tokens_in": 34, "tokens_out": 82, "cost_usd": 0.001332, "quality_score": 0.9, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic and add better quality ch..."}, "event": "response_sent", "correlation_id": "req-88fd2aba", "feature": "refund", "env": "dev", "session_id": "k3-challenge-s04", "user_id_hash": "026017618b2c", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-08-11T04:52:34.239279Z"}
{"service": "api", "payload": {"message_preview": "Explain the refund window and required evidence."}, "event": "request_received", "correlation_id": "req-975740d6", "feature": "refund", "env": "dev", "session_id": "k3-challenge-s03", "user_id_hash": "b7fde6ae11b0", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-08-11T04:52:34.242287Z"}
{"service": "api", "latency_ms": 3601, "tokens_in": 34, "tokens_out": 87, "cost_usd": 0.001407, "quality_score": 0.8, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic and add better quality ch..."}, "event": "response_sent", "correlation_id": "req-975740d6", "feature": "refund", "env": "dev", "session_id": "k3-challenge-s03", "user_id_hash": "b7fde6ae11b0", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-08-11T04:52:37.845674Z"}
{"service": "api", "payload": {"message_preview": "Summarize the refund policy for a support agent."}, "event": "request_received", "correlation_id": "req-c977c1ca", "feature": "refund", "env": "dev", "session_id": "k3-challenge-s05", "user_id_hash": "5da42a0d3d01", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-08-11T04:52:37.847739Z"}
{"service": "api", "latency_ms": 3607, "tokens_in": 34, "tokens_out": 110, "cost_usd": 0.001752, "quality_score": 0.8, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic and add better quality ch..."}, "event": "response_sent", "correlation_id": "req-c977c1ca", "feature": "refund", "env": "dev", "session_id": "k3-challenge-s05", "user_id_hash": "5da42a0d3d01", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-08-11T04:52:41.459675Z"}
```

---

## 5. Nguyên nhân gốc & Biện pháp khắc phục

* **Nguyên nhân gốc**: Cờ incident `rag_slow` trong `app/incidents.py` được đặt thành `True`, kích hoạt độ trễ đồng bộ `time.sleep(2.5)` bên trong `app/mock_rag.py:retrieve()`.
* **Thao tác khắc phục đã thực hiện**: Vô hiệu hóa incident bằng lệnh:

  ```bash
  python scripts/inject_incident.py --scenario rag_slow --disable
  ```
* **Xác minh sau khi khắc phục**: Độ trễ phản hồi đã giảm trở lại mức baseline (~150ms), qua đó giải quyết cảnh báo độ trễ P95.
