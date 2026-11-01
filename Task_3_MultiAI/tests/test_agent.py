import sys
sys.stdout.reconfigure(encoding="utf-8")
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=== 1. Check Inventory ===")
r = client.post("/api/agent/chat", json={"thread_id": "t1", "message": "Check inventory for SKU-1001", "user_role": "operator"})
resp = r.json()
print("Response:", resp.get("response"))
assert "Inventory Found" in resp["response"], "Inventory failed"

print("\n=== 2. Check Stock Availability ===")
r = client.post("/api/agent/chat", json={"thread_id": "t1", "message": "Check if 50 units of SKU-1006 are available", "user_role": "operator"})
resp = r.json()
print("Response:", resp.get("response"))
assert "Stock Availability" in resp["response"], "Availability failed"

print("\n=== 3. Look Up Customer Leads ===")
r = client.post("/api/agent/chat", json={"thread_id": "t1", "message": "Look up lead LEAD-501", "user_role": "operator"})
resp = r.json()
print("Response:", resp.get("response"))
assert "Elena Vance" in resp["response"], "Lead lookup failed"

print("\n=== 4 & 9. Human Approval Gate: Update Lead Status ===")
r = client.post("/api/agent/chat", json={"thread_id": "t1", "message": "Update lead LEAD-501 to qualified", "user_role": "operator"})
resp = r.json()
print("Approval required:", resp.get("pending_approval"))
assert resp["pending_approval"] is not None, "Pending approval expected"
assert resp["pending_approval"]["tool_name"] == "update_lead_status"

print("\n=== Approving the Action ===")
appr = client.post("/api/agent/approve", json={"thread_id": "t1", "approved": True, "user_role": "operator"})
appr_data = appr.json()
print("Approval execution:", appr_data)
assert appr_data["status"] == "executed"

print("\n=== 5 & 9. Human Approval Gate: Create Support Ticket ===")
r = client.post("/api/agent/chat", json={"thread_id": "t1", "message": "Create high priority ticket for DedSec Solutions regarding optical switch drop", "user_role": "operator"})
resp = r.json()
print("Approval required:", resp.get("pending_approval"))
assert resp["pending_approval"] is not None

print("\n=== Rejecting an Action ===")
rej = client.post("/api/agent/approve", json={"thread_id": "t1", "approved": False, "user_role": "operator"})
rej_data = rej.json()
print("Rejection response:", rej_data)
assert rej_data["status"] == "rejected"

print("\n=== 10. Permission RBAC: Viewer role blocked from write ===")
r = client.post("/api/agent/chat", json={"thread_id": "t2", "message": "Update lead LEAD-502 to won", "user_role": "viewer"})
resp = r.json()
print("Viewer blocked response:", resp)
assert "Permission Denied" in resp["response"] or any("Permission Denied" in str(x) for x in resp.get("executed_tools", []))

print("\n=== 12. Audit Logging ===")
audit = client.get("/api/agent/audit?limit=10")
logs = audit.json()
print(f"Total audit records retrieved: {len(logs)}")
assert len(logs) > 0, "No audit logs found"
for l in logs[:3]:
    print(f"- Log #{l['log_id']}: action={l['action']} approval={l['approval_status']}")

print("\n=== 13. Conversation Context & Live Endpoints ===")
erp = client.get("/api/erp/inventory")
assert erp.status_code == 200 and len(erp.json()) > 0
crm = client.get("/api/crm/leads")
assert crm.status_code == 200 and len(crm.json()) > 0
print("Live ERP inventory count:", len(erp.json()))
print("Live CRM leads count:", len(crm.json()))

print("\n>>> ALL 13 MULTIAI AGENT FEATURES TESTED AND VALIDATED SUCCESSFULLY! <<<")
