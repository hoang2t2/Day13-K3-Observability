from __future__ import annotations

import json
from pathlib import Path
from fastapi.testclient import TestClient

from app import logging_config
from app.main import app
from scripts import validate_logs


def test_correlation_id_and_enrichment_and_pii(monkeypatch, tmp_path: Path, capsys) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        # Request 1: Custom header correlation ID and PII message (email + phone + credit card)
        res1 = client.post(
            "/chat",
            headers={"x-request-id": "req-custom123"},
            json={
                "user_id": "u_test_user",
                "session_id": "s_test_session_1",
                "feature": "qa",
                "message": "Contact user@example.com or 0901234567 card 4111 2222 3333 4444",
            },
        )
        assert res1.status_code == 200
        assert res1.headers["x-request-id"] == "req-custom123"
        assert "x-response-time-ms" in res1.headers
        assert res1.json()["correlation_id"] == "req-custom123"

        # Request 2: Auto-generated correlation ID
        res2 = client.post(
            "/chat",
            json={
                "user_id": "u_test_user_2",
                "session_id": "s_test_session_2",
                "feature": "summary",
                "message": "Hello world message without PII",
            },
        )
        assert res2.status_code == 200
        generated_cid = res2.headers["x-request-id"]
        assert generated_cid.startswith("req-")
        assert generated_cid != "req-custom123"

    # Verify log contents
    log_lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(log_lines) >= 4  # request_received & response_sent for both requests

    records = [json.loads(line) for line in log_lines if line.strip()]

    for rec in records:
        if rec.get("service") == "api":
            assert "correlation_id" in rec and rec["correlation_id"] != "MISSING"
            assert "user_id_hash" in rec
            assert "session_id" in rec
            assert "feature" in rec
            assert "model" in rec
            assert "env" in rec

    # Verify PII scrubbing in logs
    raw_logs = log_path.read_text(encoding="utf-8")
    assert "user@example.com" not in raw_logs
    assert "0901234567" not in raw_logs
    assert "4111 2222 3333 4444" not in raw_logs
    assert "[REDACTED_EMAIL]" in raw_logs
    assert "[REDACTED_PHONE_VN]" in raw_logs
    assert "[REDACTED_CREDIT_CARD]" in raw_logs

    # Run validator on these logs
    monkeypatch.setattr(validate_logs, "LOG_PATH", log_path)
    validate_logs.main()

    output = capsys.readouterr().out
    assert "Estimated Score: 100/100" in output
