# Checkpoint 1 Evidence - Observability Logging & PII Scrubbing

## 1. Log Validator Terminal Output (`python scripts/validate_logs.py`)

```text
--- Lab Verification Results ---
Total log records analyzed: 20
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 10
Potential PII leaks detected: 0

--- Grading Scorecard (Estimates) ---
+ [PASSED] Basic JSON schema
+ [PASSED] Correlation ID propagation
+ [PASSED] Log enrichment
+ [PASSED] PII scrubbing

Estimated Score: 100/100
```

## 2. Actual Raw Application Logs from `data/logs.jsonl`

### Raw Line 1 (Redacted Email):
```json
{"service": "api", "payload": {"message_preview": "What is your refund policy? My email is [REDACTED_EMAIL]"}, "event": "request_received", "model": "claude-sonnet-4-5", "feature": "qa", "correlation_id": "req-9404bca2", "env": "dev", "session_id": "s01", "user_id_hash": "2055254ee30a", "level": "info", "ts": "2026-08-11T03:22:11.691596Z"}
```

### Raw Line 9 (Redacted Phone Number):
```json
{"service": "api", "payload": {"message_preview": "Here is my phone [REDACTED_PHONE_VN], what should be logged?"}, "event": "request_received", "model": "claude-sonnet-4-5", "feature": "qa", "correlation_id": "req-34c467e9", "env": "dev", "session_id": "s05", "user_id_hash": "64f6ec689229", "level": "info", "ts": "2026-08-11T03:22:13.115504Z"}
```

### Raw Line 17 (Redacted Credit Card):
```json
{"service": "api", "payload": {"message_preview": "What is the policy for PII and credit card [REDACTED_CREDIT_CARD]?"}, "event": "request_received", "model": "claude-sonnet-4-5", "feature": "qa", "correlation_id": "req-4af60837", "env": "dev", "session_id": "s09", "user_id_hash": "4d14d5d4f719", "level": "info", "ts": "2026-08-11T03:22:13.766154Z"}
```
