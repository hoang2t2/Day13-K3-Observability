# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số traces: 10 traces CP2 tạo bằng `python scripts/load_test.py` (10/10 request trả về HTTP 200, latency khoảng 2159-2186ms)
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: `docs/dashboard-spec.md` (dashboard spec đủ 6 nhóm chỉ số: Latency, Traffic, Error, Cost, Tokens, Quality)

## 3. Logging và tracing

- Evidence correlation ID: [cp1_evidence.md](file:///d:/code/aithucchien/Day13-K3-Observability/submission/evidence/cp1_evidence.md)
- Evidence PII redaction: [cp1_evidence.md](file:///d:/code/aithucchien/Day13-K3-Observability/submission/evidence/cp1_evidence.md)
- Evidence trace waterfall: cần bổ sung ảnh chụp Langfuse trace waterfall vào `submission/evidence/` sau khi mở Langfuse Dashboard
- Giải thích một span đáng chú ý: span cha `run` trong Langfuse thể hiện thời gian xử lý toàn bộ lời gọi `/chat`; dữ liệu load test cho thấy mỗi request mất khoảng 2.16-2.19 giây, nằm dưới SLO latency P95 3000ms

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ - 6/6 panel có trong dashboard contract
- Evidence dashboard: `docs/dashboard-spec.md`; cần bổ sung ảnh dashboard vào `submission/evidence/` nếu dựng dashboard trên Langfuse/Grafana
- SLO đã chọn và lý do: `latency_p95_ms <= 3000ms` để đảm bảo phản hồi chat dưới 3 giây; `error_rate_pct <= 2%` để giữ ổn định trải nghiệm người dùng; `daily_cost_usd <= 2.5` để kiểm soát ngân sách; `quality_score_avg >= 0.75` để theo dõi chất lượng câu trả lời
- Alert rules và runbook: đã cấu hình 3 alert symptom-based trong `config/alert_rules.yaml`: `high_latency_p95`, `elevated_error_rate`, `cost_budget_exceeded`; runbook xử lý tương ứng đã điền trong `docs/alerts.md`

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
