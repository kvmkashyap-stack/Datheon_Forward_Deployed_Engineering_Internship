import os
from pathlib import Path
from dotenv import load_dotenv

# Base directories
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()

# Google / Gemini API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or GOOGLE_API_KEY

# Ensure both env variables are set if either exists
if GOOGLE_API_KEY and not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = GOOGLE_API_KEY
if GEMINI_API_KEY and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# Configuration limits
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Allowed extensions for enterprise ERP/CRM data & documents
ALLOWED_EXTENSIONS = {
    ".csv", ".json", ".xlsx", ".xls", ".txt", ".pdf", ".xml"
}
