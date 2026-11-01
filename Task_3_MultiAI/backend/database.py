import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "multiai.db"

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables for ERP, CRM, Audit, and Idempotency."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # ERP Inventory Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                sku TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity >= 0),
                unit_price REAL NOT NULL,
                warehouse_location TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CRM Leads Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                lead_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                company TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('new', 'contacted', 'qualified', 'proposal', 'won', 'lost')),
                score INTEGER DEFAULT 50,
                assigned_to TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CRM Support Tickets Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
                status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Audit Logs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                user_role TEXT DEFAULT 'operator',
                action TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                params TEXT NOT NULL,
                required_approval BOOLEAN NOT NULL DEFAULT 0,
                approval_status TEXT NOT NULL,
                result TEXT,
                error TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Idempotency Records Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS idempotency_records (
                idempotency_key TEXT PRIMARY KEY,
                action TEXT NOT NULL,
                params_hash TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        seed_data(cursor, conn)

def seed_data(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    """Seed initial realistic enterprise records if tables are empty."""
    cursor.execute("SELECT COUNT(*) FROM inventory")
    if cursor.fetchone()[0] == 0:
        inventory_items = [
            ("SKU-1001", "Industrial Server Rack 42U", "Hardware", 18, 1250.00, "Warehouse-North-A1"),
            ("SKU-1002", "Fiber Optic Transceiver 10G", "Networking", 145, 85.00, "Warehouse-North-B3"),
            ("SKU-1003", "Managed L3 Switch 48-Port", "Networking", 32, 640.00, "Warehouse-South-C2"),
            ("SKU-1004", "UPS Backup Power 3000VA", "Power", 9, 890.00, "Warehouse-East-D1"),
            ("SKU-1005", "Cat6A Shielded Cable 1000ft", "Cabling", 60, 160.00, "Warehouse-South-A4"),
            ("SKU-1006", "Enterprise NVMe SSD 3.84TB", "Storage", 75, 420.00, "Warehouse-North-E2"),
        ]
        cursor.executemany(
            "INSERT INTO inventory (sku, product_name, category, quantity, unit_price, warehouse_location) VALUES (?, ?, ?, ?, ?, ?)",
            inventory_items
        )

    cursor.execute("SELECT COUNT(*) FROM leads")
    if cursor.fetchone()[0] == 0:
        sample_leads = [
            ("LEAD-501", "Elena Vance", "elena.vance@blackmesa.org", "Black Mesa Tech", "new", 70, "Sarah Chen", "Expressed interest in full server rack overhaul."),
            ("LEAD-502", "Marcus Holloway", "marcus@dedsec.io", "DedSec Solutions", "contacted", 85, "Alex Rivera", "Evaluating 10G transceivers and switches."),
            ("LEAD-503", "David Sarif", "d.sarif@sarifind.com", "Sarif Industries", "qualified", 90, "Sarah Chen", "Requested pricing quote for 50 enterprise NVMe drives."),
            ("LEAD-504", "Naomi Nagata", "naomi@beltersystems.net", "Ceres Logistics", "proposal", 95, "Alex Rivera", "Proposal under executive review."),
        ]
        cursor.executemany(
            "INSERT INTO leads (lead_id, customer_name, email, company, status, score, assigned_to, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            sample_leads
        )

    cursor.execute("SELECT COUNT(*) FROM tickets")
    if cursor.fetchone()[0] == 0:
        sample_tickets = [
            ("TICK-801", "Transceiver compatibility failure", "Client experiencing packet drop on optical links.", "DedSec Solutions", "high", "open"),
            ("TICK-802", "Delayed shipment inquiry", "Checking dispatch ETA for order #4492.", "Sarif Industries", "medium", "in_progress"),
        ]
        cursor.executemany(
            "INSERT INTO tickets (ticket_id, title, description, customer_name, priority, status) VALUES (?, ?, ?, ?, ?, ?)",
            sample_tickets
        )

    conn.commit()

# Initialize DB on load
init_db()
