# streamlit_app.py

import streamlit as st
import os
import json
import tempfile
from orchestrator import process_email
import asyncio

# Must be the first Streamlit command
st.set_page_config(
    page_title="GenAI Email Classifier",
    layout="wide"
)

# Now we can safely apply custom CSS
with open("ui_theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("GenAI Email Classifier & Field Extractor")
st.markdown("Classify servicing emails, extract financial fields, and detect duplicates — all in one sleek interface powered by LLMs")

uploaded_files = st.file_uploader(
    "Upload email or document files (.eml, .pdf, .docx, .txt)",
    type=["eml", "pdf", "docx", "txt"],
    accept_multiple_files=True
)

if st.button("Process Files") and uploaded_files:
    st.info("Processing started...")

    results = []
    for file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.name) as tmp:
            tmp.write(file.getvalue())
            tmp.flush()
            email_id = os.path.splitext(file.name)[0]
            output = asyncio.run(process_email(tmp.name, email_id))
            results.append((email_id, output))

    for email_id, data in results:
        st.subheader(f"Processed Output: {email_id}")
        st.json(data)

        json_bytes = json.dumps(data, indent=2).encode("utf-8")
        st.download_button(
            label="Download JSON",
            data=json_bytes,
            file_name=f"{email_id}_output.json",
            mime="application/json"
        )
else:
    st.markdown("*Drop your files above and hit 'Process Files' to begin...*")
