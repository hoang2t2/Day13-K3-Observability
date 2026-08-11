# Checkpoint 2 Evidence - Prompt Versioning & Dashboard Validation

## 1. Dashboard Validator Output (`python scripts/validate_dashboard.py`)

```text
HỢP LỆ: 6/6 panel có trong dashboard contract.
```

### Dashboard Panels Specification & Rules (`config/dashboard.yaml`)
- **Panel 1: Latency Percentiles**: Aggregations `P50, P95, P99` | Unit: `ms` | Threshold P95 <= 3000ms.
- **Panel 2: Request Traffic**: Event `request_received` | Count & rate per minute | Threshold >= 1 req/min.
- **Panel 3: Error Rate & Breakdown**: Events `request_received`, `request_failed` | Threshold error rate <= 2%.
- **Panel 4: Cost Over Time**: Event `response_sent.cost_usd` | Total & Avg cost | Threshold total cost <= $2.5.
- **Panel 5: Input & Output Tokens**: Event `response_sent.tokens_in/tokens_out` | Total tokens <= 50,000.
- **Panel 6: Quality Proxy**: Event `response_sent.quality_score` | Mean quality score >= 0.75.

---

## 2. Prompt Versioning & Managed Prompts (`day13-chat`)

- **Prompt Name**: `day13-chat`
- **Prompt Template Contract**:
  ```text
  Feature={{feature}}
  Docs={{docs}}
  Question={{message}}
  ```

### Prompt Versions & Labels Setup:
1. **Version 1 (Baseline)**:
   - Labels: `baseline`, `production`
   - Content: Standard default prompt template.
   - Trace Version Metadata: `prompt_name=day13-chat`, `prompt_label=baseline`, `prompt_version=1`.
2. **Version 2 (Candidate)**:
   - Label: `candidate`
   - Content: Candidate version with updated response guidance.
   - Trace Version Metadata: `prompt_name=day13-chat`, `prompt_label=candidate`, `prompt_version=2`.

### Production Rollback Verification:
- **Operation**: Label `production` updated from `version 1` to `version 2` for candidate testing.
- **Rollback Operation**: Label `production` successfully rolled back from `version 2` to `version 1`.
- **Trace Output Verification**: Request traces reflect updated `prompt_version` and `prompt_label` metadata corresponding to active label.
