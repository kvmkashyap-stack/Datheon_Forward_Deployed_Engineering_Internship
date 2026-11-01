import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, File, HTTPException, UploadFile, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB, UPLOAD_DIR
from backend.database import get_db_connection, init_db
from backend.agent.graph import run_agent_workflow, process_human_approval, SESSION_STORE
from backend.safety.audit import get_audit_logs

# Initialize DB tables on startup
init_db()

app = FastAPI(
    title="MultiAI Enterprise Backend",
    description="MultiAI: Autonomous Enterprise Agent for ERP & CRM Workflows with Human Approval Gates",
    version="2.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------- Pydantic Schemas ---------------------

class FileMetadata(BaseModel):
    filename: str
    size_bytes: int
    size_readable: str
    extension: str
    uploaded_at: str

class AgentChatRequest(BaseModel):
    thread_id: str = "default-session"
    message: str
    user_role: str = "operator"

class HumanApprovalRequest(BaseModel):
    thread_id: str
    approved: bool
    user_role: str = "operator"

class ApiKeyUpdateRequest(BaseModel):
    api_key: str


# --------------------- System & Health ---------------------

def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def get_safe_filename(original_name: str) -> str:
    return Path(original_name).name

@app.get("/")
def root():
    return {
        "service": "MultiAI Enterprise Agent Backend",
        "status": "online",
        "version": "2.0.0",
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
        "endpoints": {
            "chat": "POST /api/agent/chat",
            "approve_action": "POST /api/agent/approve",
            "audit_logs": "GET /api/agent/audit",
            "erp_inventory": "GET /api/erp/inventory",
            "crm_leads": "GET /api/crm/leads",
            "crm_tickets": "GET /api/crm/tickets",
            "upload_files": "POST /api/upload",
            "list_files": "GET /api/files",
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": len(SESSION_STORE),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    }

@app.post("/api/config/gemini_key")
def configure_gemini_key(req: ApiKeyUpdateRequest):
    key = req.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API Key cannot be empty.")
    os.environ["GEMINI_API_KEY"] = key
    os.environ["GOOGLE_API_KEY"] = key
    return {"status": "success", "message": "Gemini API key configured successfully."}


# --------------------- Agent Workflow Endpoints ---------------------

@app.post("/api/agent/chat")
def agent_chat(req: AgentChatRequest):
    """Send natural language instruction to MultiAI agent."""
    try:
        result = run_agent_workflow(
            thread_id=req.thread_id,
            user_input=req.message,
            user_role=req.user_role
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/approve")
def approve_pending_action(req: HumanApprovalRequest):
    """Human-in-the-Loop decision for pending write operations."""
    try:
        result = process_human_approval(
            thread_id=req.thread_id,
            approved=req.approved,
            user_role=req.user_role
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/session/{thread_id}")
def get_session_status(thread_id: str):
    """Retrieve conversation messages and pending approval state for a thread."""
    session = SESSION_STORE.get(thread_id)
    if not session:
        return {"thread_id": thread_id, "messages": [], "pending_action": None}
    
    formatted_msgs = []
    for m in session.get("messages", []):
        formatted_msgs.append({
            "type": m.__class__.__name__,
            "content": m.content
        })

    return {
        "thread_id": thread_id,
        "user_role": session.get("user_role"),
        "pending_action": session.get("pending_action"),
        "messages": formatted_msgs
    }

@app.get("/api/agent/audit")
def list_audit_logs(limit: int = 50, thread_id: Optional[str] = None):
    """Retrieve audit events tracking requested actions, approvals, and outcomes."""
    return get_audit_logs(limit=limit, thread_id=thread_id)


# --------------------- ERP & CRM Live Query Endpoints ---------------------

@app.get("/api/erp/inventory")
def get_inventory():
    """Retrieve live ERP inventory items from SQLite database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory ORDER BY sku ASC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@app.get("/api/crm/leads")
def get_leads():
    """Retrieve live CRM leads from SQLite database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@app.get("/api/crm/tickets")
def get_tickets():
    """Retrieve live CRM support tickets from SQLite database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


# --------------------- File Ingestion Endpoints ---------------------

@app.post("/api/upload", status_code=status.HTTP_201_CREATED)
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload enterprise files (CSV, JSON, PDF, TXT, Excel)."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    uploaded_results = []
    errors = []

    for file in files:
        safe_name = get_safe_filename(file.filename)
        file_ext = Path(safe_name).suffix.lower()

        if file_ext not in ALLOWED_EXTENSIONS:
            errors.append({
                "filename": safe_name,
                "error": f"Unsupported extension '{file_ext}'. Allowed: {sorted(list(ALLOWED_EXTENSIONS))}"
            })
            continue

        dest_path = UPLOAD_DIR / safe_name

        try:
            total_size = 0
            with dest_path.open("wb") as buffer:
                while chunk := await file.read(1024 * 1024):
                    total_size += len(chunk)
                    if total_size > MAX_FILE_SIZE_BYTES:
                        dest_path.unlink(missing_ok=True)
                        raise HTTPException(
                            status_code=413,
                            detail=f"File '{safe_name}' exceeds maximum allowed size of {MAX_FILE_SIZE_MB}MB."
                        )
                    buffer.write(chunk)

            stat = dest_path.stat()
            uploaded_results.append({
                "filename": safe_name,
                "size_bytes": stat.st_size,
                "size_readable": format_file_size(stat.st_size),
                "extension": file_ext,
                "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "status": "success"
            })
        except HTTPException:
            raise
        except Exception as e:
            dest_path.unlink(missing_ok=True)
            errors.append({"filename": safe_name, "error": str(e)})

    return {
        "message": f"Processed {len(files)} file(s).",
        "uploaded": uploaded_results,
        "failed": errors
    }

@app.get("/api/files", response_model=List[FileMetadata])
def list_uploaded_files():
    results = []
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            results.append(
                FileMetadata(
                    filename=file_path.name,
                    size_bytes=stat.st_size,
                    size_readable=format_file_size(stat.st_size),
                    extension=file_path.suffix.lower(),
                    uploaded_at=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                )
            )
    results.sort(key=lambda x: x.uploaded_at, reverse=True)
    return results

@app.get("/api/files/{filename}")
def download_file(filename: str):
    safe_name = get_safe_filename(filename)
    file_path = UPLOAD_DIR / safe_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path=file_path, filename=safe_name)

@app.get("/api/files/{filename}/preview")
def preview_file(filename: str, max_lines: int = 50):
    safe_name = get_safe_filename(filename)
    file_path = UPLOAD_DIR / safe_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")

    ext = file_path.suffix.lower()
    if ext not in {".csv", ".json", ".txt", ".xml"}:
        return {
            "filename": safe_name,
            "previewable": False,
            "message": f"Preview not supported for binary file type '{ext}'."
        }

    try:
        lines = []
        with file_path.open("r", encoding="utf-8", errors="replace") as f:
            for _ in range(max_lines):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
        return {
            "filename": safe_name,
            "previewable": True,
            "content": "".join(lines),
            "lines_shown": len(lines)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file preview: {str(e)}")

@app.delete("/api/files/{filename}")
def delete_file(filename: str):
    safe_name = get_safe_filename(filename)
    file_path = UPLOAD_DIR / safe_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    try:
        file_path.unlink()
        return {"status": "success", "message": f"File '{safe_name}' deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
