
import os

import httpx
import streamlit as st

API_BASE_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Enterprise RAG",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Enterprise RAG Assistant")
st.caption(
    "Upload agreements, retrieve relevant clauses, and ask questions "
    "with source-page citations."
)

upload_tab, query_tab = st.tabs(["Upload PDF", "Ask a question"])

with upload_tab:
    st.subheader("Ingest a document")

    st.warning(
        "Local demo upload controls: only upload documents you are authorized "
        "to process. In a deployed application, restrict this operation to "
        "authenticated administrators."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        accept_multiple_files=False,
    )

    tenant_id = st.selectbox(
        "Document tenant",
        options=["tenant-alpha", "tenant-beta"],
    )

    classification = st.selectbox(
        "Document classification",
        options=["public", "internal", "confidential", "restricted"],
        index=1,
    )

    if st.button("Upload and index PDF", type="primary"):
        if uploaded_file is None:
            st.error("Choose a PDF file first.")
        else:
            try:
                with st.spinner("Extracting text and indexing document..."):
                    response = httpx.post(
                        f"{API_BASE_URL}/upload",
                        data={
                            "tenant_id": tenant_id,
                            "classification": classification,
                        },
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                "application/pdf",
                            )
                        },
                        timeout=180.0,
                    )

                if response.is_success:
                    result = response.json()
                    st.success("PDF ingested successfully!")
                    st.write(f"**File:** {result['source']}")
                    st.write(f"**Pages extracted:** {result['pages_extracted']}")
                    st.write(f"**Chunks created:** {result['chunks_created']}")
                    st.write(f"**Chunks indexed:** {result['chunks_indexed']}")
                else:
                    st.error(
                        f"Upload failed ({response.status_code}): "
                        f"{response.text}"
                    )

            except httpx.HTTPError as exc:
                st.error(
                    "Could not reach the FastAPI backend. "
                    "Make sure the backend is running. "
                    f"Details: {exc}"
                )

with query_tab:
    st.subheader("Ask your documents")

    user_id = st.selectbox(
        "Demo user / clearance",
        options=[
            "demo-public",
            "demo-internal",
            "demo-confidential",
            "demo-restricted",
            "demo-other-tenant",
        ],
        index=1,
    )

    question = st.text_area(
        "Your question",
        placeholder="What are the termination conditions in the agreement?",
        max_chars=4000,
    )

    if st.button("Ask", type="primary"):
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            try:
                with st.spinner("Searching authorized documents and generating an answer..."):
                    response = httpx.post(
                        f"{API_BASE_URL}/query",
                        json={
                            "user_id": user_id,
                            "question": question.strip(),
                        },
                        timeout=180.0,
                    )

                if response.is_success:
                    result = response.json()

                    st.markdown("### Answer")
                    st.write(result["answer"])

                    st.caption(
                        f"Retrieved chunks: {result['retrieved_chunks']}"
                    )

                    st.markdown("### Source pages")
                    citations = result.get("citations", [])

                    if citations:
                        for citation in citations:
                            st.write(
                                f"- **{citation['source']}** — "
                                f"Page {citation['page']}"
                            )
                    else:
                        st.info("No source citations were returned.")
                else:
                    st.error(
                        f"Query failed ({response.status_code}): "
                        f"{response.text}"
                    )

            except httpx.HTTPError as exc:
                st.error(
                    "Could not reach the FastAPI backend. "
                    "Make sure the backend is running. "
                    f"Details: {exc}"
                )
