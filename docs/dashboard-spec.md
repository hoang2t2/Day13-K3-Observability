# Dashboard Spec

Contract có thể kiểm tra bằng máy nằm tại `config/dashboard.yaml`. Hướng dẫn dựng và kiểm tra runtime nằm tại [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md).

## Cấu hình chung

- Công cụ sử dụng: mô tả dashboard bằng spec trong file này; có thể dựng lại bằng Langfuse, Grafana, Streamlit, notebook hoặc công cụ tương đương.
- Nguồn dữ liệu chuẩn theo `DASHBOARD_SETUP.md`: `data/logs.jsonl`.
- Nguồn kiểm tra nhanh runtime: endpoint `/metrics`.
- Khoảng thời gian mặc định: 60 phút.
- Refresh: 30 giây.
- SLO/threshold: hiển thị rõ theo `config/dashboard.yaml` và `config/slo.yaml`.
- Lưu ý: trường `query` trong `config/dashboard.yaml` là pseudocode mô tả phép tính, không phải câu lệnh bắt buộc copy nguyên vào mọi công cụ.

## Snapshot runtime hiện tại

Kết quả lấy từ lệnh:

```bash
curl http://localhost:8000/metrics | python -m json.tool
```

```json
{
  "traffic": 20,
  "latency_p50": 2164.0,
  "latency_p95": 2173.0,
  "latency_p99": 2173.0,
  "avg_cost_usd": 0.002,
  "total_cost_usd": 0.0405,
  "tokens_in_total": 660,
  "tokens_out_total": 2570,
  "error_rate_pct": 0.0,
  "error_breakdown": {},
  "quality_avg": 0.88
}
```

## Mapping dữ liệu

| Panel | Event/field trong `data/logs.jsonl` | Metric runtime từ `/metrics` | Phép tổng hợp |
|---|---|---|---|
| Latency | `response_sent.latency_ms` | `latency_p50`, `latency_p95`, `latency_p99` | P50, P95, P99 |
| Traffic | `request_received` | `traffic` | count, request/phút |
| Errors | `request_received`, `request_failed`, `error_type` | `error_rate_pct`, `error_breakdown` | error rate và breakdown |
| Cost | `response_sent.cost_usd` | `total_cost_usd`, `avg_cost_usd` | tổng theo phút và toàn cửa sổ |
| Tokens | `response_sent.tokens_in`, `response_sent.tokens_out` | `tokens_in_total`, `tokens_out_total` | tổng theo từng field |
| Quality | `response_sent.quality_score` | `quality_avg` | mean |

## Dashboard Panels

| # | Nhóm | Panel | Source chuẩn | Đơn vị | Giá trị hiện tại | Visualization | Threshold/SLO |
|---|---|---|---|---|---:|---|---|
| 1 | Latency | Latency percentiles | `response_sent.latency_ms` | ms | P50 2164.0, P95 2173.0, P99 2173.0 | Line hoặc Single Value | P95 <= 3000ms |
| 2 | Traffic | Request traffic | `request_received` | requests/min | 20 requests | Counter hoặc QPS gauge | rate_per_minute >= 1 |
| 3 | Errors | Error rate and breakdown | `request_received`, `request_failed`, `error_type` | percent | 0.0% | Gauge + breakdown table | error_rate_pct <= 2% |
| 4 | Cost | Cost over time | `response_sent.cost_usd` | USD | total 0.0405, avg 0.002 | Single Value hoặc Line | total <= 2.5 USD |
| 5 | Tokens | Input and output tokens | `response_sent.tokens_in`, `response_sent.tokens_out` | tokens | in 660, out 2570 | Bar hoặc Single Value | tokens/window <= 50000 |
| 6 | Quality | Quality proxy | `response_sent.quality_score` | score 0-1 | 0.88 | Gauge hoặc Single Value | mean >= 0.75 |

## Đánh giá theo snapshot

- Latency: P95 hiện tại 2173.0ms, đạt SLO vì thấp hơn ngưỡng 3000ms.
- Traffic: đã có 20 requests từ load test, đủ dữ liệu để hiển thị traffic.
- Errors: error_rate_pct hiện tại 0.0%, đạt SLO vì thấp hơn ngưỡng 2%.
- Cost: total_cost_usd hiện tại 0.0405 USD, thấp hơn ngưỡng 2.5 USD.
- Tokens: tổng input/output hiện tại là 3230 tokens, thấp hơn ngưỡng 50000 tokens/window.
- Quality: quality_avg hiện tại 0.88, đạt SLO vì cao hơn ngưỡng 0.75.

## Cách dựng dashboard

1. Chạy API với `.env` hiện tại.
2. Chạy load test để tạo dữ liệu baseline:

```bash
python scripts/load_test.py --concurrency 5
```

3. Dùng `data/logs.jsonl` làm nguồn chuẩn để dựng đúng 6 panel ở trên.
4. Đặt tên panel, đơn vị, time range và threshold giống contract.
5. Chạy validator:

```bash
python scripts/validate_dashboard.py
```

Validator chỉ kiểm tra cấu trúc contract. Evidence runtime vẫn cần ảnh dashboard hoặc spec đã điền đủ.

## Evidence cần chụp

- Screenshot dashboard/spec có đủ 6 panel, time range, đơn vị và threshold.
- Screenshot hoặc text output của `python scripts/validate_dashboard.py`.
- Nếu dựng dashboard bằng tool thật, lưu ảnh vào `submission/evidence/cp2-dashboard.png`.
- Nếu chỉ dùng spec, lưu ảnh hoặc dẫn file `docs/dashboard-spec.md` trong báo cáo.
