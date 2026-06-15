# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 2A202600824_LeQuocAnh
- [REPO_URL]: https://github.com/QuocAnh-0710/2A202600824_LeQuocAnh_Day13
- [MEMBERS]:
  - Member A: Le Quoc Anh | Role: Logging & PII
  - Member B: Le Quoc Anh | Role: Tracing & Enrichment
  - Member C: Le Quoc Anh | Role: SLO & Alerts
  - Member D: Le Quoc Anh | Role: Load Test & Dashboard
  - Member E: Le Quoc Anh | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: _(chụp từ Langfuse UI → Traces sau khi chạy load_test.py)_
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [TOTAL_TRACES_COUNT] : 
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: ảnh trong file docs/screenshots
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: _(chụp màn hình log cho thấy `[REDACTED_EMAIL]` hoặc `[REDACTED_PHONE_VN]` thay vì giá trị thật)_
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: _(chụp màn hình Langfuse UI → một trace → tab Timeline/Waterfall)_
- [TRACE_WATERFALL_EXPLANATION]: The `agent-run` trace contains two child spans: `rag-retrieve` (vector store lookup) and `llm-generate` (generation, marked as type=generation). During a `rag_slow` incident, the `rag-retrieve` span expands to ~2500ms, making it immediately visible which step caused the latency spike without reading any log lines.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: _(chụp màn hình dashboard 6 panels từ Langfuse hoặc Grafana)_
- [SLO_TABLE]:

| SLI | Target | Window | Current Value |
|---|---|---|---|
| Latency P95 | &lt; 3000ms | 28d | 150ms |
| Error Rate | &lt; 2% | 28d | 0% |
| Cost Budget | &lt; $2.5/day | 1d | $0.0646 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: _(chụp màn hình config/alert_rules.yaml trong editor)_
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Latency P95 spiked above 2500ms on `/chat` requests. The `response_sent` log showed `latency_ms` values consistently above 2500. The `/metrics` endpoint confirmed `latency_p95` breached the 3000ms SLO threshold.
- [ROOT_CAUSE_PROVED_BY]: Langfuse trace waterfall for any request during the incident shows the `rag-retrieve` child span taking ~2500ms while `llm-generate` remains at ~150ms, confirming the bottleneck is in the retrieval layer, not the LLM. Log line: `{"event": "response_sent", "latency_ms": 2650, "correlation_id": "req-xxxxxxxx"}`.
- [FIX_ACTION]: Disabled the incident toggle via `POST /incidents/rag_slow/disable`. In production this maps to: switch to a fallback retrieval source or increase timeout threshold while the vector store recovers.
- [PREVENTIVE_MEASURE]: Add a P95 latency alert (`high_latency_p95` in `config/alert_rules.yaml`) that triggers at 5000ms for 30 minutes. Add a per-span timeout on `rag-retrieve` so a slow vector store does not cascade to the full request. Monitor the `rag-retrieve` span duration independently as a separate SLI.

---

## 5. Individual Contributions & Evidence

### Le Quoc Anh
- [TASKS_COMPLETED]: Implemented all TODO items: (1) Correlation ID middleware — clear contextvars, generate `req-<8hex>` ID, bind to structlog and response headers; (2) Log enrichment — `bind_contextvars` with `user_id_hash`, `session_id`, `feature`, `model`, `env` on every `/chat` request; (3) PII scrubbing pipeline — registered `scrub_event` processor in structlog, added `passport` and `vn_address` regex patterns; (4) Langfuse tracing — `load_dotenv()` before import, `capture_input=False` on `@observe` to avoid leaking raw args, explicit scrubbed input/output on trace, nested spans for `rag-retrieve` and `llm-generate`, flush on shutdown.
- [EVIDENCE_LINK]: https://github.com/QuocAnh-0710/2A202600824_LeQuocAnh_Day13/commits/main

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Token cost is estimated per-request in `agent.py::_estimate_cost()` using Sonnet pricing ($3/M input, $15/M output) and exposed via `GET /metrics → avg_cost_usd`. The `cost_spike` incident toggle multiplies output tokens ×4 to simulate a runaway generation, testable with `python scripts/inject_incident.py --scenario cost_spike`.
- [BONUS_AUDIT_LOGS]: `AUDIT_LOG_PATH=data/audit.jsonl` is configured in `.env`. The path is available for teams to write separate audit events (e.g., PII access, admin actions) independently of the main log stream.
- [BONUS_CUSTOM_METRIC]: `quality_score` is computed heuristically per response (RAG doc match + answer length + keyword overlap − PII penalty) and tracked in `QUALITY_SCORES` list. Exposed as `quality_avg` in `GET /metrics` and attached to every Langfuse trace observation as `output.quality_score`.
