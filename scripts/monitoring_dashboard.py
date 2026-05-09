#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.cache import CacheManager
from shared.repository import JsonCacheRepository
from scheduler import build_scheduler, register_example_jobs, scheduler_summary

st.set_page_config(page_title="Scheduler y repos monitor", layout="wide")
st.title("Scheduler y repos monitor")

cache = CacheManager()
metrics_path = cache.metrics_path()

scheduler = build_scheduler()
register_example_jobs(scheduler)
jobs_df = pd.DataFrame(scheduler_summary(scheduler))

repo_rows = []
for sport in ["tenis", "futbol", "basket"]:
    repo = JsonCacheRepository(sport=sport, cache=cache)
    fixtures = repo.list_fixtures()
    meta = repo.get_snapshot_meta()
    repo_rows.append({
        "sport": sport,
        "records": len(fixtures),
        "generated_at": meta.get("generated_at"),
        "source": meta.get("source"),
        "payload_hash": meta.get("payload_hash"),
    })
repo_df = pd.DataFrame(repo_rows)

if metrics_path.exists():
    rows = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics_df = pd.DataFrame(rows)
else:
    metrics_df = pd.DataFrame(columns=["timestamp", "sport", "status", "cache_status", "latency_ms", "records", "job_id"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Jobs cargados", int(len(jobs_df)))
c2.metric("Repos monitoreados", int(len(repo_df)))
c3.metric("Eventos metricados", int(len(metrics_df)))
c4.metric("Latencia media ms", round(float(metrics_df["latency_ms"].mean()), 2) if not metrics_df.empty else 0.0)

st.subheader("Jobs del scheduler")
if jobs_df.empty:
    st.warning("Sin jobs")
else:
    st.dataframe(jobs_df, use_container_width=True)

st.subheader("Estado de repositorios")
st.dataframe(repo_df, use_container_width=True)

st.subheader("Métricas recientes")
if metrics_df.empty:
    st.info("Todavía no hay métricas")
else:
    metrics_df["timestamp"] = pd.to_datetime(metrics_df["timestamp"], utc=True)
    st.dataframe(metrics_df.sort_values("timestamp", ascending=False).head(100), use_container_width=True)
    st.subheader("Latencia")
    st.line_chart(metrics_df.set_index("timestamp")[["latency_ms"]])
