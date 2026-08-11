# Checkpoint 3 Evidence - Official Challenge Investigation (`day13-k3-observability-v1`)

## 1. Incident Metadata (`config/challenge.json`)

- **Challenge ID**: `day13-k3-observability-v1`
- **Cohort**: `K3`
- **Incident**: `rag_slow`
- **Affected Feature**: `refund`
- **Latency Threshold**: `2000ms`

---

## 2. Metrics Symptom Analysis

During load test on the `refund` feature queries (`k3-challenge-s01` to `k3-challenge-s05`), the P95 response latency jumped from normal ~150ms to **~2653ms**, breaching the challenge threshold of `2000ms`.

---

## 3. Traces Deep Dive (Waterfall Analysis)

Analyzing traces for session IDs `k3-challenge-s01` through `k3-challenge-s05`:
- **Root Span (`run`)**: Duration ~2653ms
- **Sub-span (`rag_retrieve`)**: Duration ~2500ms (accounting for **94.2%** of total request latency).
- **Sub-span (`llm_generate`)**: Duration ~150ms.

*Conclusion from Trace*: The latency degradation is isolated entirely within the RAG retrieval step (`rag_retrieve`), not the LLM generation step.

---

## 4. Log Evidence & Correlation IDs

Correlation ID tracking in `data/logs.jsonl`:

### Control Event (Incident Activation):
```json
{"service": "control", "payload": {"name": "rag_slow"}, "event": "incident_enabled", "correlation_id": "req-d49dbe6b", "level": "warning", "ts": "2026-08-11T05:33:05.983925Z"}
```

### Affected Response Sent Log (High Latency):
```json
{"service": "api", "latency_ms": 2653, "tokens_in": 34, "tokens_out": 151, "cost_usd": 0.002367, "quality_score": 0.8, "payload": {"answer_preview": "Starter answer..."}, "event": "response_sent", "user_id_hash": "5da42a0d3d01", "correlation_id": "req-606b5f17", "session_id": "k3-challenge-s05", "model": "claude-sonnet-4-5", "env": "dev", "feature": "refund", "level": "info", "ts": "2026-08-11T05:33:16.940079Z"}
```

---

## 5. Root Cause & Mitigation

- **Root Cause**: The `rag_slow` incident flag in `app/incidents.py` was set to `True`, triggering a synchronous `time.sleep(2.5)` delay inside `app/mock_rag.py:retrieve()`.
- **Fix Action Executed**: Disabled the incident via command:
  ```bash
  python scripts/inject_incident.py --scenario rag_slow --disable
  ```
- **Post-Fix Verification**: Response latency dropped back to baseline (~150ms), resolving the P95 latency alert.
