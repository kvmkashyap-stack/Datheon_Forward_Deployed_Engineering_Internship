import time
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from backend.database import get_db_connection
from backend.safety.validator import InventoryQuerySchema, StockAvailabilitySchema

def retry_operation(func, max_retries: int = 3, backoff_factor: float = 0.5):
    """Execute function with retries and exponential backoff for resilience."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(backoff_factor * (2 ** attempt))

@tool("check_inventory", args_schema=InventoryQuerySchema)
def check_inventory(product_identifier: str) -> Dict[str, Any]:
    """Check stock quantity, warehouse location, and pricing for a product by SKU or product name."""
    def _execute():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            clean_id = product_identifier.strip()
            # Try exact SKU match first
            cursor.execute("SELECT * FROM inventory WHERE UPPER(sku) = UPPER(?)", (clean_id,))
            row = cursor.fetchone()

            # If not found, search by name
            if not row:
                cursor.execute(
                    "SELECT * FROM inventory WHERE LOWER(product_name) LIKE LOWER(?) LIMIT 1",
                    (f"%{clean_id}%",)
                )
                row = cursor.fetchone()

            if not row:
                return {
                    "success": False,
                    "found": False,
                    "message": f"Product '{product_identifier}' was not found in ERP inventory."
                }

            item = dict(row)
            return {
                "success": True,
                "found": True,
                "sku": item["sku"],
                "product_name": item["product_name"],
                "category": item["category"],
                "quantity_on_hand": item["quantity"],
                "unit_price": item["unit_price"],
                "warehouse_location": item["warehouse_location"],
                "last_updated": item["last_updated"]
            }

    return retry_operation(_execute)

@tool("check_stock_availability", args_schema=StockAvailabilitySchema)
def check_stock_availability(product_identifier: str, requested_quantity: int) -> Dict[str, Any]:
    """Determine whether enough stock is available in ERP inventory for a requested order quantity."""
    def _execute():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            clean_id = product_identifier.strip()
            
            cursor.execute("SELECT * FROM inventory WHERE UPPER(sku) = UPPER(?)", (clean_id,))
            row = cursor.fetchone()

            if not row:
                cursor.execute(
                    "SELECT * FROM inventory WHERE LOWER(product_name) LIKE LOWER(?) LIMIT 1",
                    (f"%{clean_id}%",)
                )
                row = cursor.fetchone()

            if not row:
                return {
                    "success": False,
                    "found": False,
                    "available": False,
                    "message": f"Product '{product_identifier}' was not found in ERP inventory."
                }

            item = dict(row)
            current_qty = item["quantity"]
            is_available = current_qty >= requested_quantity
            diff = current_qty - requested_quantity

            return {
                "success": True,
                "found": True,
                "sku": item["sku"],
                "product_name": item["product_name"],
                "requested_quantity": requested_quantity,
                "quantity_on_hand": current_qty,
                "is_available": is_available,
                "difference": diff,
                "status": "In Stock" if is_available else "Insufficient Stock",
                "warehouse_location": item["warehouse_location"]
            }

    return retry_operation(_execute)
