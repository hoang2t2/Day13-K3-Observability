# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: 404NotFound
- Repository URL: https://github.com/hoang2t2/Day13-K3-Observability
- Commit SHA cuối: 69c73d08de5437faca512c7186880fd89f625a8a
- Thành viên và vai trò:
  - Đoàn Vũ Hoàng: Middleware, gán Correlation ID, Enrichment logs
  - Sùng A Khua: Cấu hình Langfuse, thiết lập SLO/Alert Rules, viết tài liệu Alert Runbook
  - Đàm Vinh Quang: Thiết kế Dashboard Spec, thực hiện load test, quản lý Challenge/Practice Incident (CP3) và tổng hợp báo cáo nhóm.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số traces: 10+ traces (44 correlation IDs recorded trong `data/logs.jsonl`)
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: [dashboard.yaml](../config/dashboard.yaml) & [scripts/dashboard.py](../scripts/dashboard.py)

## 3. Logging và tracing

- Evidence correlation ID: [cp1_evidence.md](evidence/cp1_evidence.md)
- Evidence PII redaction: [cp1_evidence.md](evidence/cp1_evidence.md)
- Evidence trace waterfall: [trace-detail.png](evidence/trace-detail.png) & [totaltrace.png](evidence/totaltrace.png)
- Giải thích một span đáng chú ý: Span `rag_retrieve` trong `app/agent.py` và `app/mock_rag.py`. Khi xảy ra sự cố `rag_slow`, span `rag_retrieve` bị trì hoãn 2500ms (`time.sleep(2.5)`), chiếm hơn 94% tổng latency (~2653ms) của request `run`. Điều này giúp khoanh vùng chính xác điểm nghẽn nằm ở lớp Vector Database / RAG Search chứ không phải do LLM Generation.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: `v1` (labels: `baseline`, `production`)
- Version/label candidate: `v2` (labels: `candidate`)
- Trace ID của mỗi version:
  - Baseline (v1): `tr-base-001` (dùng prompt version 1 với label `baseline`)
  - Candidate (v2): `tr-cand-002` (dùng prompt version 2 với label `candidate`)
- Bằng chứng đổi label hoặc rollback: Chi tiết bằng chứng tại [cp2_evidence.md](evidence/cp2_evidence.md) và hướng dẫn tại [PROMPT_VERSIONING.md](../docs/PROMPT_VERSIONING.md) — Gắn label `production` sang Version 2 để chạy thử nghiệm, kiểm tra trace metadata, sau đó thực hiện rollback thành công label `production` về Version 1.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ (6/6 panel trong contract, xem [cp2_evidence.md](evidence/cp2_evidence.md))
- Evidence dashboard: Cấu hình [dashboard.yaml](../config/dashboard.yaml) và Streamlit UI trong [scripts/dashboard.py](../scripts/dashboard.py)
- SLO đã chọn và lý do:
  - Latency P95 <= 3000ms (Target 99.5%): Đảm bảo trải nghiệm phản hồi mượt mà cho người dùng cuối.
  - Error Rate <= 2% (Target 99.0%): Giữ hệ thống chatbot ổn định và giảm thiểu các lỗi 5xx.
  - Daily Cost <= $2.5 (Target 100.0%): Kiểm soát ngân sách chi phí gọi API LLM.
  - Quality Score Average >= 0.75 (Target 95.0%): Đảm bảo câu trả lời từ RAG có độ chính xác và chất lượng cao.
- Alert rules và runbook: Cấu hình alert rules tại [alert_rules.yaml](../config/alert_rules.yaml) và tài liệu xử lý sự cố chi tiết tại [alerts.md](../docs/alerts.md).

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`
- Triệu chứng từ metrics: P95 Latency tăng vọt lên ~2653ms cho các query thuộc feature `refund` (vượt ngưỡng `latency_threshold_ms` 2000ms trong [challenge.json](../config/challenge.json)). Xem bằng chứng tại [cp3_evidence.md](evidence/cp3_evidence.md).
- Trace ID liên quan: Sessions `k3-challenge-s01` tới `k3-challenge-s05` (các correlation IDs: `req-606b5f17`, `req-09a1f9bd`, `req-f8fc1406`, `req-ce0356a0`, `req-d9ecc2ff`).
- Log line/correlation ID liên quan:
  - Control incident log: `{"service": "control", "payload": {"name": "rag_slow"}, "event": "incident_enabled", "correlation_id": "req-d49dbe6b", "level": "warning", "ts": "2026-08-11T05:33:05.983925Z"}`
  - API response log: `{"service": "api", "latency_ms": 2653, "tokens_in": 34, "tokens_out": 151, "cost_usd": 0.002367, "quality_score": 0.8, "payload": {"answer_preview": "..."}, "event": "response_sent", "user_id_hash": "5da42a0d3d01", "correlation_id": "req-606b5f17", "session_id": "k3-challenge-s05", "model": "claude-sonnet-4-5", "env": "dev", "feature": "refund", "level": "info", "ts": "2026-08-11T05:33:16.940079Z"}`
- Root cause: Incident `rag_slow` bị bật trong `STATE`, kích hoạt `time.sleep(2.5)` tại hàm `retrieve()` trong `app/mock_rag.py`.
- Fix action: Tắt incident `rag_slow` bằng cách chạy `python scripts/inject_incident.py --disable` (gửi POST request đến `/incidents/rag_slow/disable`).
- Preventive measure:
  - Thiết lập alert `high_latency_p95` theo dõi P95 latency liên tục.
  - Phân tách metrics và trace spans chi tiết cho bước Vector Search (`rag_retrieve`) và LLM Completion để phát hiện nghẽn cơ sở dữ liệu nhanh chóng.
  - Cấu hình timeout và circuit breaker cho dịch vụ retrieval.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Đoàn Vũ Hoàng | Middleware, gán Correlation ID, Enrichment logs & PII Redaction | [`f732ae4`](https://github.com/hoang2t2/Day13-K3-Observability/commit/f732ae4) | Hiểu rõ cách trích xuất, lan truyền correlation ID xuyên suốt request lifecycle và che chắn dữ liệu nhạy cảm PII trong log. |
| Sùng A Khua | Cấu hình Langfuse, thiết lập SLO/Alert Rules, viết tài liệu Alert Runbook | [`495ad43`](https://github.com/hoang2t2/Day13-K3-Observability/commit/495ad43), [`69c73d0`](https://github.com/hoang2t2/Day13-K3-Observability/commit/69c73d0) | Thành thạo cách kết nối tracing từ Langfuse, định nghĩa SLO/SLI phù hợp với symptom-based alerting và xây dựng runbook. |
| Đàm Vinh Quang | Thiết kế Dashboard Spec, thực hiện load test, quản lý Challenge/Practice Incident (CP3) và tổng hợp báo cáo nhóm | [`cd84f4f`](https://github.com/hoang2t2/Day13-K3-Observability/commit/cd84f4f) | Hiểu cách trực quan hóa 6 nhóm chỉ số trên Dashboard contract, thực thi load test để phát hiện anomaly và quy trình triage incident bằng Traces & Logs. |
