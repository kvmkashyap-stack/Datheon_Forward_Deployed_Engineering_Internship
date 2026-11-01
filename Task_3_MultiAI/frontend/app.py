import io
import json
import requests
import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(
    page_title="MultiAI Enterprise Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom enterprise CSS
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        color: #475569;
        font-size: 1.0rem;
        margin-bottom: 1.5rem;
    }
    .approval-box {
        background-color: #FEF3C7;
        border: 2px solid #F59E0B;
        border-radius: 10px;
        padding: 16px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .stChatMessage {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state initialization
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = "session-001"
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "pending_approval" not in st.session_state:
    st.session_state["pending_approval"] = None

# Sidebar configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=54)
    st.title("MultiAI Control")
    st.caption("Autonomous Enterprise Agent (ERP & CRM)")
    st.divider()

    api_url = st.text_input("Backend API URL", value="http://127.0.0.1:8000")
    
    # Check backend connectivity
    backend_online = False
    gemini_active = False
    try:
        health_resp = requests.get(f"{api_url}/health", timeout=3)
        if health_resp.status_code == 200:
            backend_online = True
            h_data = health_resp.json()
            gemini_active = h_data.get("gemini_configured", False)
            st.success("🟢 Backend Connected", icon="✅")
        else:
            st.warning(f"🟡 Backend Status {health_resp.status_code}")
    except Exception:
        st.error("🔴 Backend Offline (Start FastAPI)")

    # Gemini API Key configuration
    st.subheader("🔑 Gemini Model Config")
    if gemini_active:
        st.caption("✔️ Gemini API is active.")
    else:
        st.caption("ℹ️ Running in resilient parser mode. Enter Gemini API Key to enable generative model:")
    
    new_gemini_key = st.text_input("Gemini API Key", type="password", key="gemini_key_input")
    if st.button("Save API Key", use_container_width=True):
        if new_gemini_key.strip():
            try:
                res = requests.post(f"{api_url}/api/config/gemini_key", json={"api_key": new_gemini_key.strip()}, timeout=5)
                if res.status_code == 200:
                    st.success("API Key updated!")
                    st.rerun()
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Failed to update key: {e}")

    st.divider()
    
    # Role Selection (Safety & RBAC)
    st.subheader("🛡️ Safety & Role RBAC")
    user_role = st.selectbox(
        "Active User Role",
        options=["operator", "admin", "viewer"],
        index=0,
        help="'viewer' can only execute read actions. 'operator' & 'admin' can trigger write operations requiring approval."
    )

    # Session Management
    st.subheader("🧵 Conversation Context")
    thread_id = st.text_input("Thread / Session ID", value=st.session_state["thread_id"])
    if thread_id != st.session_state["thread_id"]:
        st.session_state["thread_id"] = thread_id
        st.session_state["messages"] = []
        st.session_state["pending_approval"] = None
        st.rerun()

    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["pending_approval"] = None
        st.rerun()

    st.divider()
    st.caption("MultiAI Enterprise Agent v2.0")

# Main Page Header
st.markdown('<div class="main-title">MultiAI Enterprise Autonomous Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Orchestrating ERP & CRM workflows with controlled tool use, human-in-the-loop approvals, and audit logging.</div>',
    unsafe_allow_html=True,
)

# Tabs
tab_chat, tab_erp, tab_crm, tab_audit, tab_files = st.tabs([
    "💬 Agent Chat",
    "📦 ERP Inventory",
    "👥 CRM Hub",
    "🛡️ Audit Trail",
    "📂 File Ingestion"
])

# ----------------- TAB 1: Agent Chat -----------------
with tab_chat:
    col_chat, col_info = st.columns([3, 1])

    with col_info:
        st.markdown("##### ⚡ Quick Prompts")
        st.caption("Click to try natural language workflows:")
        
        sample_prompts = [
            "Check inventory for SKU-1001",
            "Check if 50 units of SKU-1006 are available",
            "Look up lead LEAD-501",
            "Update lead LEAD-501 status to qualified",
            "Create high priority ticket for DedSec Solutions regarding optical switch drop"
        ]
        
        for p in sample_prompts:
            if st.button(p, key=f"btn_{p}", use_container_width=True):
                st.session_state["preset_input"] = p
                st.rerun()

    with col_chat:
        # Display chat history
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Display Pending Human Approval card if any
        pending = st.session_state.get("pending_approval")
        if pending:
            st.markdown(
                f"""
                <div class="approval-box">
                    <h4>⚠️ Human Approval Required (Write Operation)</h4>
                    <p>The agent is proposing to execute: <b>{pending['tool_name']}</b></p>
                    <p><b>Parameters:</b></p>
                    <pre>{json.dumps(pending['params'], indent=2)}</pre>
                </div>
                """,
                unsafe_allow_html=True
            )
            col_app, col_rej = st.columns(2)
            with col_app:
                if st.button("✅ Approve & Commit", type="primary", use_container_width=True):
                    try:
                        app_res = requests.post(
                            f"{api_url}/api/agent/approve",
                            json={"thread_id": st.session_state["thread_id"], "approved": True, "user_role": user_role},
                            timeout=15
                        )
                        if app_res.status_code == 200:
                            data = app_res.json()
                            st.session_state["pending_approval"] = None
                            st.session_state["messages"].append({"role": "assistant", "content": data.get("message")})
                            st.rerun()
                        else:
                            st.error(f"Approval failed: {app_res.text}")
                    except Exception as e:
                        st.error(f"Error submitting approval: {e}")

            with col_rej:
                if st.button("❌ Reject Action", type="secondary", use_container_width=True):
                    try:
                        rej_res = requests.post(
                            f"{api_url}/api/agent/approve",
                            json={"thread_id": st.session_state["thread_id"], "approved": False, "user_role": user_role},
                            timeout=15
                        )
                        if rej_res.status_code == 200:
                            data = rej_res.json()
                            st.session_state["pending_approval"] = None
                            st.session_state["messages"].append({"role": "assistant", "content": data.get("message")})
                            st.rerun()
                        else:
                            st.error(f"Rejection failed: {rej_res.text}")
                    except Exception as e:
                        st.error(f"Error submitting rejection: {e}")

        # Chat Input
        preset = st.session_state.pop("preset_input", None)
        user_input = st.chat_input("Ask MultiAI to check stock, look up leads, create tickets...")
        if preset:
            user_input = preset

        if user_input:
            st.session_state["messages"].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            if not backend_online:
                st.error("FastAPI backend is offline. Please make sure the backend is running.")
            else:
                with st.chat_message("assistant"):
                    with st.spinner("MultiAI reasoning & orchestrating tools..."):
                        try:
                            resp = requests.post(
                                f"{api_url}/api/agent/chat",
                                json={
                                    "thread_id": st.session_state["thread_id"],
                                    "message": user_input,
                                    "user_role": user_role
                                },
                                timeout=30
                            )
                            if resp.status_code == 200:
                                data = resp.json()
                                response_text = data.get("response", "")
                                pending_action = data.get("pending_approval")

                                st.markdown(response_text)
                                st.session_state["messages"].append({"role": "assistant", "content": response_text})

                                if pending_action:
                                    st.session_state["pending_approval"] = pending_action
                                    st.rerun()
                            else:
                                err_text = f"Agent error ({resp.status_code}): {resp.text}"
                                st.error(err_text)
                                st.session_state["messages"].append({"role": "assistant", "content": err_text})
                        except Exception as e:
                            st.error(f"Request exception: {str(e)}")

# ----------------- TAB 2: ERP Inventory -----------------
with tab_erp:
    st.subheader("📦 ERP Real-Time Inventory & Resource Database")
    st.caption("Live enterprise database records managed by MultiAI tools.")
    
    if backend_online:
        try:
            inv_resp = requests.get(f"{api_url}/api/erp/inventory", timeout=5)
            if inv_resp.status_code == 200:
                inv_data = inv_resp.json()
                if inv_data:
                    df_inv = pd.DataFrame(inv_data)
                    # Format pricing
                    if "unit_price" in df_inv.columns:
                        df_inv["unit_price"] = df_inv["unit_price"].apply(lambda x: f"${x:,.2f}")
                    st.dataframe(df_inv, use_container_width=True, hide_index=True)
                else:
                    st.info("Inventory table is empty.")
        except Exception as e:
            st.error(f"Failed to fetch ERP inventory: {e}")
    else:
        st.warning("Backend offline.")

# ----------------- TAB 3: CRM Hub -----------------
with tab_crm:
    st.subheader("👥 CRM Customer Leads & Support Tickets")

    col_leads, col_tickets = st.columns(2)

    with col_leads:
        st.markdown("#### 🎯 Customer Leads")
        if backend_online:
            try:
                leads_resp = requests.get(f"{api_url}/api/crm/leads", timeout=5)
                if leads_resp.status_code == 200:
                    leads_data = leads_resp.json()
                    if leads_data:
                        st.dataframe(pd.DataFrame(leads_data), use_container_width=True, hide_index=True)
                    else:
                        st.info("No CRM leads found.")
            except Exception as e:
                st.error(f"Error fetching leads: {e}")

    with col_tickets:
        st.markdown("#### 🎫 Support Tickets")
        if backend_online:
            try:
                tickets_resp = requests.get(f"{api_url}/api/crm/tickets", timeout=5)
                if tickets_resp.status_code == 200:
                    tickets_data = tickets_resp.json()
                    if tickets_data:
                        st.dataframe(pd.DataFrame(tickets_data), use_container_width=True, hide_index=True)
                    else:
                        st.info("No CRM tickets found.")
            except Exception as e:
                st.error(f"Error fetching tickets: {e}")

# ----------------- TAB 4: Audit Trail -----------------
with tab_audit:
    st.subheader("🛡️ Enterprise Audit Logging & Governance")
    st.caption("Tracking requested actions, parameters, human approvals, and execution outcomes.")

    col_audit_ctrl, _ = st.columns([1, 4])
    with col_audit_ctrl:
        if st.button("🔄 Refresh Audit Logs", use_container_width=True):
            st.rerun()

    if backend_online:
        try:
            audit_resp = requests.get(f"{api_url}/api/agent/audit?limit=50", timeout=5)
            if audit_resp.status_code == 200:
                audit_logs = audit_resp.json()
                if audit_logs:
                    df_audit = pd.DataFrame(audit_logs)
                    st.dataframe(df_audit, use_container_width=True, hide_index=True)
                else:
                    st.info("No audit logs recorded yet. Trigger actions in the chat tab to generate audit records.")
        except Exception as e:
            st.error(f"Error loading audit logs: {e}")

# ----------------- TAB 5: File Ingestion -----------------
with tab_files:
    st.subheader("📂 Enterprise File Ingestion Hub")
    st.caption("Upload ERP catalog sheets, CRM CSVs, or contracts for MultiAI processing.")

    uploaded_files = st.file_uploader(
        "Upload files for knowledge ingestion",
        type=["csv", "json", "xlsx", "xls", "txt", "pdf", "xml"],
        accept_multiple_files=True,
        key="file_uploader_tab"
    )

    if uploaded_files:
        if st.button("🚀 Upload Files to Backend", type="primary"):
            if not backend_online:
                st.error("Backend offline.")
            else:
                with st.spinner("Uploading..."):
                    payload = [("files", (f.name, f.getvalue(), f.type or "application/octet-stream")) for f in uploaded_files]
                    try:
                        resp = requests.post(f"{api_url}/api/upload", files=payload, timeout=60)
                        if resp.status_code in (200, 201):
                            st.success("Files uploaded successfully!")
                            st.rerun()
                        else:
                            st.error(f"Upload failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Upload error: {e}")

    st.divider()
    st.markdown("#### Stored Files")
    if backend_online:
        try:
            files_resp = requests.get(f"{api_url}/api/files", timeout=5)
            if files_resp.status_code == 200:
                files_list = files_resp.json()
                if files_list:
                    st.dataframe(pd.DataFrame(files_list), use_container_width=True, hide_index=True)
                else:
                    st.info("No files currently in repository.")
        except Exception as e:
            st.caption(f"Could not load files: {e}")
