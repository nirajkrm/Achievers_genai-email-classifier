import streamlit as st
import os
import json
import tempfile
import asyncio
from typing import Dict, Any
from orchestrator import process_email

# Configure page
st.set_page_config(
    page_title="GenAI Email Classifier",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS theme if available
if os.path.exists("ui_theme.css"):
    with open("ui_theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Main app
st.title("GenAI Email Classifier & Field Extractor")
st.markdown("Classify servicing emails, extract financial fields, detect duplicates, and auto-route using LLMs.")

uploaded_files = st.file_uploader(
    "Upload emails or documents (.eml, .pdf, .docx, .txt)",
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
            try:
                output = asyncio.run(process_email(tmp.name, email_id))
                results.append((email_id, output))
            except Exception as e:
                results.append((email_id, {'error': str(e)}))

    for email_id, data in results:
        if 'error' in data:
            st.error(f"Failed to process {email_id}: {data['error']}")
            continue
            
        st.header(f"Email ID: {email_id}")
        
        # Basic Info
        col1, col2, col3 = st.columns(3)
        col1.metric("From", data.get("from", "unknown"))
        col2.metric("To", data.get("to", "unknown"))
        col3.metric("Date", data.get("date", "unknown"))
        st.markdown(f"**Subject**: {data.get('subject', 'N/A')}")
        
        # Classification Data (matches CLI output structure)
        classification = data.get("classification", {})
        primary_request = classification.get("primary_request", {})
        
        st.subheader("Classification")
        cols = st.columns(3)
        cols[0].markdown(f"**Type**: `{primary_request.get('request_type', 'N/A')}`")
        cols[1].markdown(f"**Subtype**: `{primary_request.get('sub_request_type', 'N/A')}`")
        
        priority = primary_request.get('priority', 'N/A')
        priority_color = "red" if priority == "High" else "orange" if priority == "Medium" else "green"
        cols[2].markdown(f"**Priority**: <span style='color:{priority_color}'>{priority}</span>", unsafe_allow_html=True)
        
        st.markdown(f"**Intent**: {primary_request.get('primary_intent', 'N/A')}")
        st.markdown(f"**Confidence**: {primary_request.get('confidence', 'N/A')}%")
        
        with st.expander("Classification Details"):
            st.json(classification)
        
        # Team Assignment
        assigned_team = data.get("assigned_team", "General Servicing Team")
        st.success(f"**Assigned Team**: {assigned_team}")
        
        # Extracted Fields (matches CLI output structure)
        if data.get("extracted_fields"):
            st.subheader("Extracted Fields")
            st.json(data["extracted_fields"])
        
        # Deduplication (matches CLI output structure)
        dup_data = data.get("duplication", {})
        st.subheader("Deduplication Check")
        if dup_data.get("is_duplicate", False):
            st.error("Potential duplicate detected")
            st.json(dup_data)
        else:
            st.success("Unique request")
        
        # Raw Output (matches CLI exactly)
        with st.expander("Complete Output (matches CLI format)"):
            st.json(data)
        
        # Download
        json_bytes = json.dumps(data, indent=2).encode("utf-8")
        st.download_button(
            label="Download JSON Output",
            data=json_bytes,
            file_name=f"{email_id}_output.json",
            mime="application/json"
        )
        
        st.markdown("---")
else:
    st.info("Upload one or more email/document files and click 'Process Files' to begin.")