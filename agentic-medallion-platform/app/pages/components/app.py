from __future__ import annotations

import pandas as pd
import streamlit as st


def render_summary_cards(metrics: list[tuple[str, str]]) -> None:
	columns = st.columns(len(metrics)) if metrics else []
	for column, (label, value) in zip(columns, metrics):
		with column:
			st.markdown(
				f"<div style='padding:1rem;border-radius:16px;background:#f8fafc;border:1px solid #d9e2ec;'><strong>{label}</strong><br>{value}</div>",
				unsafe_allow_html=True,
			)


def render_dataframe(title: str, dataframe: pd.DataFrame) -> None:
	st.subheader(title)
	st.dataframe(dataframe, use_container_width=True)
