import json
from pathlib import Path
import pandas as pd
import streamlit as st

# Cấu hình trang
st.set_page_config(page_title="Day 13 AI Observability", layout="wide")
st.title("Day 13 AI Observability Dashboard")

DATA_PATH = Path("data/logs.jsonl")

@st.cache_data(ttl=30)
def load_data():
    if not DATA_PATH.exists():
        return pd.DataFrame()
    
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]
        
    if not records:
        return pd.DataFrame()
        
    df = pd.json_normalize(records)
    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"])
    return df

df = load_data()

if df.empty:
    st.warning("Chưa có dữ liệu. Vui lòng chạy load test trước.")
    st.stop()

# Lọc các sự kiện
df_req = df[df["event"] == "request_received"]
df_res = df[df["event"] == "response_sent"]
df_fail = df[df["event"] == "request_failed"]

# Bắt đầu vẽ 6 panel
col1, col2, col3 = st.columns(3)

# Panel 1: Latency
with col1:
    st.subheader("1. Latency Percentiles")
    if not df_res.empty and "latency_ms" in df_res.columns:
        latencies = df_res["latency_ms"].dropna()
        p50 = latencies.quantile(0.5)
        p95 = latencies.quantile(0.95)
        p99 = latencies.quantile(0.99)
        st.metric(label="P95 Latency (SLO <= 3000ms)", value=f"{p95:.1f} ms")
        st.write(f"**P50:** {p50:.1f} ms | **P99:** {p99:.1f} ms")
    else:
        st.write("No data")

# Panel 2: Traffic
with col2:
    st.subheader("2. Request Traffic")
    if not df_req.empty:
        total_reqs = len(df_req)
        st.metric(label="Requests count", value=f"{total_reqs}")
        if "ts" in df_req.columns:
            ts_min = df_req["ts"].min()
            ts_max = df_req["ts"].max()
            duration_minutes = (ts_max - ts_min).total_seconds() / 60.0
            duration_minutes = max(duration_minutes, 1.0) # avoid division by zero or too small
            rate = total_reqs / duration_minutes
            st.write(f"**Rate:** {rate:.1f} req/min (SLO >= 1)")
    else:
        st.write("No data")

# Panel 3: Errors
with col3:
    st.subheader("3. Error Rate & Breakdown")
    if not df_req.empty or not df_fail.empty:
        total_requests = len(df_req) + len(df_fail)
        total_errors = len(df_fail)
        error_rate = (total_errors / total_requests) * 100 if total_requests > 0 else 0
        st.metric(label="Error Rate (SLO <= 2%)", value=f"{error_rate:.2f}%")
        if not df_fail.empty and "error_type" in df_fail.columns:
            st.write(df_fail["error_type"].value_counts())
        else:
            st.write("0 Errors")
    else:
        st.write("No data")

col4, col5, col6 = st.columns(3)

# Panel 4: Cost
with col4:
    st.subheader("4. Cost Over Time")
    if not df_res.empty and "cost_usd" in df_res.columns:
        total_cost = df_res["cost_usd"].sum()
        avg_cost = df_res["cost_usd"].mean()
        st.metric(label="Total Cost (SLO <= 2.5$)", value=f"${total_cost:.4f}")
        st.write(f"**Avg Cost / Req:** ${avg_cost:.4f}")
    else:
        st.write("No data")

# Panel 5: Tokens
with col5:
    st.subheader("5. Tokens Input / Output")
    if not df_res.empty:
        total_in = df_res["tokens_in"].sum() if "tokens_in" in df_res.columns else 0
        total_out = df_res["tokens_out"].sum() if "tokens_out" in df_res.columns else 0
        total_tokens = total_in + total_out
        st.metric(label="Total Tokens (SLO <= 50,000)", value=f"{total_tokens:,.0f}")
        st.write(f"**In:** {total_in:,.0f} | **Out:** {total_out:,.0f}")
    else:
        st.write("No data")

# Panel 6: Quality
with col6:
    st.subheader("6. Quality Proxy")
    if not df_res.empty and "quality_score" in df_res.columns:
        mean_quality = df_res["quality_score"].mean()
        st.metric(label="Mean Quality Score (SLO >= 0.75)", value=f"{mean_quality:.2f}")
    else:
        st.write("No data")

st.markdown("---")
st.write("Data source: `data/logs.jsonl` | Refresh: 30s | Window: 60m")
