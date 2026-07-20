from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
import streamlit as st

from workflows.orchestrator import run_workflow


st.set_page_config(
	page_title="Agentic Medallion Platform",
	page_icon="📊",
	layout="wide",
)

st.markdown(
	"""
	<style>
	.block-container {
		padding-top: 2rem;
		padding-bottom: 2rem;
	}
	.hero {
		padding: 1.2rem 1.4rem;
		border-radius: 20px;
		background: linear-gradient(135deg, #102a43 0%, #0b7285 55%, #f08c00 100%);
		color: white;
		margin-bottom: 1.2rem;
	}
	.metric-card {
		padding: 1rem 1.1rem;
		border-radius: 16px;
		background: #f8fafc;
		border: 1px solid #d9e2ec;
	}
	</style>
	""",
	unsafe_allow_html=True,
)

st.markdown(
	"<div class='hero'><h1>Agentic Medallion Platform</h1><p>Upload a CSV and run the bronze, silver, gold, and reporting agents in one pass.</p></div>",
	unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
dataset_name = st.text_input("Dataset name", value="")

if uploaded_file is not None:
	file_bytes = uploaded_file.getvalue()

	with NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
		temp_file.write(file_bytes)
		temp_file_path = Path(temp_file.name)

	preview_dataframe = pd.read_csv(temp_file_path)
	st.subheader("Preview")
	st.dataframe(preview_dataframe.head(20), use_container_width=True)

	if st.button("Run pipeline", type="primary"):
		with st.spinner("Running agent workflow..."):
			result = run_workflow(str(temp_file_path), dataset_name=dataset_name or None)

		st.success("Pipeline completed")

		col1, col2, col3 = st.columns(3)
		with col1:
			st.markdown(
				f"<div class='metric-card'><strong>Bronze rows</strong><br>{result['bronze']['row_count']}</div>",
				unsafe_allow_html=True,
			)
		with col2:
			st.markdown(
				f"<div class='metric-card'><strong>Silver rows</strong><br>{result['silver']['row_count_after']}</div>",
				unsafe_allow_html=True,
			)
		with col3:
			st.markdown(
				f"<div class='metric-card'><strong>Quality score</strong><br>{result['profile']['quality']['quality_score']}</div>",
				unsafe_allow_html=True,
			)

		st.subheader("Workflow notes")
		for note in result.get("messages", []):
			st.write(f"- {note}")

		st.subheader("Business report")
		st.markdown(result.get("final_report", "No report generated."))

		st.subheader("Profile summary")
		st.json(result.get("profile", {}))

		st.subheader("Bronze preview")
		st.dataframe(pd.DataFrame(result.get("raw_preview", [])), use_container_width=True)

		st.subheader("Silver preview")
		st.dataframe(pd.DataFrame(result.get("cleaned_preview", [])), use_container_width=True)

		st.download_button(
			label="Download markdown report",
			data=result.get("final_report", ""),
			file_name="business_report.md",
			mime="text/markdown",
		)
else:
	st.info("Upload a CSV file to start the pipeline.")
