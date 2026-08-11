# Alert Runbook

Mỗi alert trong CP2 được thiết kế theo hướng symptom-based: cảnh báo dựa trên triệu chứng người dùng thấy được hoặc SLO bị ảnh hưởng, không dựa trực tiếp vào tên hàm, module nội bộ hay chi tiết implementation.

## Alert 1

- Tên: high_latency_p95
- Severity: warning
- SLI/SLO liên quan: latency_p95_ms <= 3000ms, target 99.5%
- Điều kiện và thời gian duy trì: latency_p95 > 3000ms trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng thấy chatbot phản hồi chậm, trải nghiệm hỏi đáp bị trễ và có thể bị timeout nếu tình trạng tiếp tục xấu đi.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency, kiểm tra P50/P95/P99 trong 60 phút gần nhất và xác nhận P95 có vượt 3000ms liên tục không.
  2. Mở Langfuse Traces, lọc các trace chậm trong cùng khoảng thời gian, xem waterfall span `run` để biết request chậm ở bước nào.
  3. Đối chiếu log `response_sent.latency_ms` và traffic để xem latency tăng do tải cao, RAG chậm, LLM chậm hay incident/test scenario đang bật.
- Mitigation tạm thời: Giảm tải test, tắt incident nếu đang bật, rollback thay đổi gần nhất liên quan prompt/RAG/model, hoặc chuyển sang cấu hình nhanh hơn nếu có.
- Owner: on-call-engineer

## Alert 2

- Tên: elevated_error_rate
- Severity: critical
- SLI/SLO liên quan: error_rate_pct <= 2%, target 99.0%
- Điều kiện và thời gian duy trì: error_rate_pct > 5 trong 3 phút
- Ảnh hưởng tới người dùng: Một phần người dùng nhận lỗi 5xx, không nhận được câu trả lời hoặc phải thử lại request.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard error, xác nhận error_rate_pct và bảng breakdown error_type để biết lỗi nào đang tăng mạnh.
  2. Mở logs quanh thời điểm alert, tìm event `request_failed` và correlation_id để gom các request lỗi liên quan.
  3. Mở Langfuse trace có cùng correlation_id/session_id nếu có, kiểm tra span `run` và metadata để xác định lỗi xảy ra trước hay sau khi agent xử lý.
- Mitigation tạm thời: Tắt incident `tool_fail` nếu đang bật, rollback release gần nhất, giảm concurrency load test, hoặc trả về fallback response để người dùng không bị lỗi trắng.
- Owner: on-call-engineer

## Alert 3

- Tên: cost_budget_exceeded
- Severity: warning
- SLI/SLO liên quan: daily_cost_usd <= 2.5, target 100.0%
- Điều kiện và thời gian duy trì: daily_cost_usd > 2.5
- Ảnh hưởng tới người dùng: Hệ thống có nguy cơ vượt ngân sách vận hành; nếu không xử lý có thể phải giới hạn tính năng, giảm tần suất request hoặc dừng dịch vụ.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard cost và tokens, kiểm tra `total_cost_usd`, `avg_cost_usd`, `tokens_in_total`, `tokens_out_total` trong cửa sổ gần nhất.
  2. So sánh traffic với cost: nếu traffic không tăng nhưng cost tăng, mở Langfuse trace để tìm request có token/cost bất thường.
  3. Kiểm tra prompt, RAG context và incident `cost_spike` để xem câu trả lời có bị dài bất thường hoặc context đưa vào quá nhiều không.
- Mitigation tạm thời: Tắt incident `cost_spike` nếu đang bật, giảm giới hạn output, rút ngắn prompt/context, tạm thời hạ concurrency load test hoặc đặt rate limit cho endpoint `/chat`.
- Owner: team-lead
