from fastmcp.server import FastMCP
from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from threading import Timer

# Initialize the FastMCP server
app = FastMCP()

# Define the data models
class RelocationRequest(BaseModel):
    """Model for relocation request"""
    name: str
    from_address: str
    to_address: str
    move_date: str
    move_mode: Literal["sea", "air", "road"]

class RelocationStatus(BaseModel):
    """Model for relocation status"""
    customer_id: str
    name: str
    status: str
    move_date: str
    move_mode: str

# In-memory storage for registered relocations
relocations_db: dict[str, dict] = {}
customer_counter = 0

def auto_confirm_status(customer_id: str):
    """Auto-confirm status after 2 minutes"""
    if customer_id in relocations_db:
        relocations_db[customer_id]["status"] = "confirmed"
        print(f"Status for customer {customer_id} auto-updated to confirmed")

@app.tool()
def register_relocation(request: RelocationRequest) -> dict:
    """
    Register a new relocation request.

    Args:
        request: RelocationRequest with customer details

    Returns:
        Dictionary with registration confirmation and customer ID
    """
    global customer_counter
    customer_counter += 1
    customer_id = f"RELOC-{customer_counter:05d}"

    # Store the relocation request
    relocations_db[customer_id] = {
        "name": request.name,
        "from_address": request.from_address,
        "to_address": request.to_address,
        "move_date": request.move_date,
        "move_mode": request.move_mode,
        "status": "pending",
        "registered_at": datetime.now().isoformat()
    }

    # Schedule auto-confirmation after 2 minutes (120 seconds)
    timer = Timer(120.0, auto_confirm_status, args=[customer_id])
    timer.daemon = True
    timer.start()

    return {
        "success": True,
        "customer_id": customer_id,
        "message": f"Relocation registered successfully. Status will be updated to 'confirmed' in 2 minutes.",
        "initial_status": "pending"
    }

@app.tool()
def get_relocation_status(customer_id: str) -> RelocationStatus:
    """
    Get the current status of a registered relocation.

    Args:
        customer_id: The unique customer ID

    Returns:
        RelocationStatus with current details and status
    """
    if customer_id not in relocations_db:
        raise ValueError(f"Customer ID {customer_id} not found")

    data = relocations_db[customer_id]
    return RelocationStatus(
        customer_id=customer_id,
        name=data["name"],
        status=data["status"],
        move_date=data["move_date"],
        move_mode=data["move_mode"]
    )

@app.tool()
def list_all_relocations() -> list[dict]:
    """
    Get all registered relocations.

    Returns:
        List of all relocations with their current status
    """
    return [
        {
            "customer_id": cid,
            "name": data["name"],
            "status": data["status"],
            "move_mode": data["move_mode"],
            "move_date": data["move_date"]
        }
        for cid, data in relocations_db.items()
    ]

@app.tool()
def remove_relocation(customer_id: str) -> dict:
    """
    Remove a relocation by customer ID.

    Args:
        customer_id: The unique customer ID to remove

    Returns:
        Dictionary with removal confirmation
    """
    if customer_id not in relocations_db:
        raise ValueError(f"Customer ID {customer_id} not found")

    removed_data = relocations_db.pop(customer_id)
    return {
        "success": True,
        "customer_id": customer_id,
        "message": f"Relocation for {removed_data['name']} has been removed successfully."
    }

@app.tool()
def change_relocation_status(customer_id: str, new_status: Literal["pending", "confirmed", "in_transit", "completed", "cancelled"]) -> dict:
    """
    Change the status of a relocation.

    Args:
        customer_id: The unique customer ID
        new_status: New status for the relocation

    Returns:
        Dictionary with status change confirmation
    """
    if customer_id not in relocations_db:
        raise ValueError(f"Customer ID {customer_id} not found")

    old_status = relocations_db[customer_id]["status"]
    relocations_db[customer_id]["status"] = new_status

    return {
        "success": True,
        "customer_id": customer_id,
        "old_status": old_status,
        "new_status": new_status,
        "message": f"Status updated from '{old_status}' to '{new_status}'."
    }

if __name__ == '__main__':
    app.run(transport="streamable-http", port=8082)
