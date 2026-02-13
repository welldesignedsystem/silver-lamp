# api_server.py
#
# A single-file FastAPI server with:
#   - Full OpenAPI docs auto-generated at /docs and /redoc
#   - In-memory dictionary as the database (resets on restart)
#   - CRUD for users, products, orders, notes
#   - Input validation via Pydantic
#   - Cross-table analytics endpoints
#
# pip install fastapi uvicorn
# Run: uvicorn orderapi:app --reload
# Docs: http://localhost:8000/docs

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

app = FastAPI(
    title="In-Memory Store API",
    description="""
A fully functional REST API backed by an in-memory dictionary.

## Tables
- **Users** — manage people with roles
- **Products** — catalog with stock tracking
- **Orders** — place and track orders (stock auto-managed)
- **Notes** — free-form tagged notes

## Notes
- All data lives in memory — resets when server restarts
- Visit `/reset` to restore seed data at any time
- Full OpenAPI schema auto-generated from this code
""",
    version="1.0.0",
)


# ─────────────────────────────────────────────────────────────
#  IN-MEMORY DATABASE
# ─────────────────────────────────────────────────────────────

DB = {
    "users": {
        1: {"id": 1, "name": "Alice",   "email": "alice@example.com", "role": "admin", "created_at": "2024-01-01"},
        2: {"id": 2, "name": "Bob",     "email": "bob@example.com",   "role": "user",  "created_at": "2024-01-02"},
        3: {"id": 3, "name": "Charlie", "email": "charlie@example.com","role": "user",  "created_at": "2024-01-03"},
    },
    "products": {
        1: {"id": 1, "name": "Laptop",     "price": 999.99, "stock": 15, "category": "electronics"},
        2: {"id": 2, "name": "Headphones", "price": 79.99,  "stock": 42, "category": "electronics"},
        3: {"id": 3, "name": "Desk Chair", "price": 249.99, "stock": 8,  "category": "furniture"},
        4: {"id": 4, "name": "Notebook",   "price": 4.99,   "stock": 200,"category": "stationery"},
    },
    "orders": {
        1: {"id": 1, "user_id": 1, "product_id": 1, "quantity": 1, "total": 999.99, "status": "shipped",  "created_at": "2024-01-10"},
        2: {"id": 2, "user_id": 2, "product_id": 2, "quantity": 2, "total": 159.98, "status": "pending",  "created_at": "2024-01-11"},
        3: {"id": 3, "user_id": 1, "product_id": 3, "quantity": 1, "total": 249.99, "status": "paid",     "created_at": "2024-01-12"},
    },
    "notes": {},
}

COUNTERS = {"users": 3, "products": 4, "orders": 3, "notes": 0}

def next_id(table: str) -> int:
    COUNTERS[table] += 1
    return COUNTERS[table]

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ─────────────────────────────────────────────────────────────
#  PYDANTIC MODELS  (define request body shapes + validation)
# ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "user"

    @field_validator("role")
    def role_must_be_valid(cls, v):
        if v not in ("admin", "user"):
            raise ValueError("role must be 'admin' or 'user'")
        return v

    model_config = {"json_schema_extra": {"example": {
        "name": "Diana", "email": "diana@example.com", "role": "user"
    }}}


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

    @field_validator("role")
    def role_must_be_valid(cls, v):
        if v and v not in ("admin", "user"):
            raise ValueError("role must be 'admin' or 'user'")
        return v


class ProductCreate(BaseModel):
    name: str
    price: float
    category: str
    stock: int = 0

    @field_validator("price")
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("price must be positive")
        return v

    model_config = {"json_schema_extra": {"example": {
        "name": "Keyboard", "price": 49.99, "category": "electronics", "stock": 30
    }}}


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None


class RestockRequest(BaseModel):
    quantity: int

    @field_validator("quantity")
    def qty_positive(cls, v):
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

    @field_validator("quantity")
    def qty_positive(cls, v):
        if v <= 0:
            raise ValueError("quantity must be at least 1")
        return v

    model_config = {"json_schema_extra": {"example": {
        "user_id": 1, "product_id": 2, "quantity": 3
    }}}


class OrderStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    def status_must_be_valid(cls, v):
        if v not in ("paid", "shipped", "cancelled"):
            raise ValueError("status must be 'paid', 'shipped', or 'cancelled'")
        return v


class NoteCreate(BaseModel):
    title: str
    content: str
    tags: list[str] = []

    model_config = {"json_schema_extra": {"example": {
        "title": "Q4 Goals", "content": "Hit 1M revenue", "tags": ["sales", "urgent"]
    }}}


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None


# ─────────────────────────────────────────────────────────────
#  ROOT
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"], summary="API info and available endpoints")
def root():
    return {
        "name": "In-Memory Store API",
        "docs": "http://localhost:8000/docs",
        "tables": list(DB.keys()),
        "record_counts": {t: len(v) for t, v in DB.items()},
    }


# ═════════════════════════════════════════════════════════════
#  USERS
# ═════════════════════════════════════════════════════════════

@app.get("/users", tags=["Users"], summary="List all users")
def list_users(role: Optional[str] = Query(None, description="Filter by role: admin or user")):
    users = list(DB["users"].values())
    if role:
        users = [u for u in users if u["role"] == role]
    return {"count": len(users), "users": users}


@app.get("/users/{user_id}", tags=["Users"], summary="Get a user by ID")
def get_user(user_id: int):
    user = DB["users"].get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


@app.post("/users", tags=["Users"], summary="Create a new user", status_code=201)
def create_user(body: UserCreate):
    # Email uniqueness check
    for u in DB["users"].values():
        if u["email"] == body.email:
            raise HTTPException(status_code=409, detail=f"Email '{body.email}' already exists")
    uid = next_id("users")
    user = {"id": uid, **body.model_dump(), "created_at": now()}
    DB["users"][uid] = user
    return user


@app.patch("/users/{user_id}", tags=["Users"], summary="Update a user")
def update_user(user_id: int, body: UserUpdate):
    user = DB["users"].get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    user.update(updates)
    return user


@app.delete("/users/{user_id}", tags=["Users"], summary="Delete a user")
def delete_user(user_id: int):
    if user_id not in DB["users"]:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    del DB["users"][user_id]
    # Cancel pending orders
    cancelled = []
    for order in DB["orders"].values():
        if order["user_id"] == user_id and order["status"] == "pending":
            order["status"] = "cancelled"
            cancelled.append(order["id"])
    return {"deleted_user_id": user_id, "cancelled_orders": cancelled}


# ═════════════════════════════════════════════════════════════
#  PRODUCTS
# ═════════════════════════════════════════════════════════════

@app.get("/products", tags=["Products"], summary="List all products")
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    low_stock: bool = Query(False, description="Only show products with stock < 10"),
):
    products = list(DB["products"].values())
    if category:
        products = [p for p in products if p["category"] == category]
    if low_stock:
        products = [p for p in products if p["stock"] < 10]
    return {"count": len(products), "products": products}


@app.get("/products/{product_id}", tags=["Products"], summary="Get a product by ID")
def get_product(product_id: int):
    product = DB["products"].get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product


@app.post("/products", tags=["Products"], summary="Create a new product", status_code=201)
def create_product(body: ProductCreate):
    pid = next_id("products")
    product = {"id": pid, **body.model_dump()}
    DB["products"][pid] = product
    return product


@app.patch("/products/{product_id}", tags=["Products"], summary="Update a product")
def update_product(product_id: int, body: ProductUpdate):
    product = DB["products"].get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    product.update(updates)
    return product


@app.delete("/products/{product_id}", tags=["Products"], summary="Delete a product")
def delete_product(product_id: int):
    if product_id not in DB["products"]:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    pending = [o for o in DB["orders"].values()
               if o["product_id"] == product_id and o["status"] == "pending"]
    if pending:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete: {len(pending)} pending order(s) exist for this product"
        )
    del DB["products"][product_id]
    return {"deleted_product_id": product_id}


@app.post("/products/{product_id}/restock", tags=["Products"], summary="Add stock to a product")
def restock_product(product_id: int, body: RestockRequest):
    product = DB["products"].get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    product["stock"] += body.quantity
    return {"product": product, "added": body.quantity}


# ═════════════════════════════════════════════════════════════
#  ORDERS
# ═════════════════════════════════════════════════════════════

@app.get("/orders", tags=["Orders"], summary="List all orders")
def list_orders(
    status: Optional[str] = Query(None, description="Filter by status: pending, paid, shipped, cancelled"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
):
    orders = list(DB["orders"].values())
    if status:
        orders = [o for o in orders if o["status"] == status]
    if user_id:
        orders = [o for o in orders if o["user_id"] == user_id]
    return {"count": len(orders), "orders": orders}


@app.get("/orders/{order_id}", tags=["Orders"], summary="Get an order with full details")
def get_order(order_id: int):
    order = DB["orders"].get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return {
        **order,
        "user":    DB["users"].get(order["user_id"], {}),
        "product": DB["products"].get(order["product_id"], {}),
    }


@app.post("/orders", tags=["Orders"], summary="Place a new order", status_code=201)
def create_order(body: OrderCreate):
    if body.user_id not in DB["users"]:
        raise HTTPException(status_code=404, detail=f"User {body.user_id} not found")
    product = DB["products"].get(body.product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {body.product_id} not found")
    if product["stock"] < body.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {product['stock']}, requested: {body.quantity}"
        )
    # Deduct stock and place order
    product["stock"] -= body.quantity
    oid = next_id("orders")
    order = {
        "id": oid,
        "user_id": body.user_id,
        "product_id": body.product_id,
        "quantity": body.quantity,
        "total": round(product["price"] * body.quantity, 2),
        "status": "pending",
        "created_at": now(),
    }
    DB["orders"][oid] = order
    return {"order": order, "remaining_stock": product["stock"]}


@app.patch("/orders/{order_id}/status", tags=["Orders"], summary="Update order status")
def update_order_status(order_id: int, body: OrderStatusUpdate):
    order = DB["orders"].get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    # Enforce valid transitions
    transitions = {
        "pending":   ["paid", "cancelled"],
        "paid":      ["shipped", "cancelled"],
        "shipped":   [],
        "cancelled": [],
    }
    current = order["status"]
    if body.status not in transitions[current]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot move from '{current}' to '{body.status}'. Allowed: {transitions[current]}"
        )
    # Restore stock on cancellation
    if body.status == "cancelled" and current in ("pending", "paid"):
        product = DB["products"].get(order["product_id"])
        if product:
            product["stock"] += order["quantity"]

    order["status"] = body.status
    return order


# ═════════════════════════════════════════════════════════════
#  NOTES
# ═════════════════════════════════════════════════════════════

@app.get("/notes", tags=["Notes"], summary="List all notes")
def list_notes(tag: Optional[str] = Query(None, description="Filter by tag")):
    notes = list(DB["notes"].values())
    if tag:
        notes = [n for n in notes if tag in n.get("tags", [])]
    return {"count": len(notes), "notes": notes}


@app.get("/notes/{note_id}", tags=["Notes"], summary="Get a note by ID")
def get_note(note_id: int):
    note = DB["notes"].get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
    return note


@app.post("/notes", tags=["Notes"], summary="Create a note", status_code=201)
def create_note(body: NoteCreate):
    nid = next_id("notes")
    note = {"id": nid, **body.model_dump(), "created_at": now()}
    DB["notes"][nid] = note
    return note


@app.patch("/notes/{note_id}", tags=["Notes"], summary="Update a note")
def update_note(note_id: int, body: NoteUpdate):
    note = DB["notes"].get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    note.update(updates)
    note["updated_at"] = now()
    return note


@app.delete("/notes/{note_id}", tags=["Notes"], summary="Delete a note")
def delete_note(note_id: int):
    if note_id not in DB["notes"]:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
    del DB["notes"][note_id]
    return {"deleted_note_id": note_id}


# ═════════════════════════════════════════════════════════════
#  ANALYTICS
# ═════════════════════════════════════════════════════════════

@app.get("/analytics/summary", tags=["Analytics"], summary="Full database summary")
def summary():
    orders = list(DB["orders"].values())
    revenue = sum(o["total"] for o in orders if o["status"] in ("paid", "shipped"))
    by_status = {}
    for o in orders:
        by_status[o["status"]] = by_status.get(o["status"], 0) + 1
    low_stock = [p for p in DB["products"].values() if p["stock"] < 10]
    return {
        "users":    {"total": len(DB["users"])},
        "products": {"total": len(DB["products"]), "low_stock": low_stock},
        "orders":   {"total": len(orders), "by_status": by_status, "total_revenue": round(revenue, 2)},
        "notes":    {"total": len(DB["notes"])},
    }


@app.get("/analytics/users/{user_id}/orders", tags=["Analytics"], summary="User order history and spend")
def user_orders(user_id: int):
    user = DB["users"].get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    orders = [o for o in DB["orders"].values() if o["user_id"] == user_id]
    enriched = [{**o, "product_name": DB["products"].get(o["product_id"], {}).get("name")} for o in orders]
    total_spent = sum(o["total"] for o in orders if o["status"] in ("paid", "shipped"))
    return {"user": user, "order_count": len(orders), "total_spent": round(total_spent, 2), "orders": enriched}


@app.get("/search", tags=["Analytics"], summary="Full-text search across all tables")
def search(q: str = Query(..., description="Search term")):
    term = q.lower()
    return {
        "query": q,
        "users":    [u for u in DB["users"].values()    if term in u["name"].lower() or term in u["email"].lower()],
        "products": [p for p in DB["products"].values() if term in p["name"].lower() or term in p["category"].lower()],
        "notes":    [n for n in DB["notes"].values()    if term in n["title"].lower() or term in n["content"].lower()],
    }


# ─────────────────────────────────────────────────────────────
#  RESET
# ─────────────────────────────────────────────────────────────

@app.post("/reset", tags=["Info"], summary="Reset database to seed data")
def reset():
    DB["users"] = {
        1: {"id": 1, "name": "Alice",   "email": "alice@example.com", "role": "admin", "created_at": "2024-01-01"},
        2: {"id": 2, "name": "Bob",     "email": "bob@example.com",   "role": "user",  "created_at": "2024-01-02"},
        3: {"id": 3, "name": "Charlie", "email": "charlie@example.com","role": "user",  "created_at": "2024-01-03"},
    }
    DB["products"] = {
        1: {"id": 1, "name": "Laptop",     "price": 999.99, "stock": 15, "category": "electronics"},
        2: {"id": 2, "name": "Headphones", "price": 79.99,  "stock": 42, "category": "electronics"},
        3: {"id": 3, "name": "Desk Chair", "price": 249.99, "stock": 8,  "category": "furniture"},
        4: {"id": 4, "name": "Notebook",   "price": 4.99,   "stock": 200,"category": "stationery"},
    }
    DB["orders"] = {
        1: {"id": 1, "user_id": 1, "product_id": 1, "quantity": 1, "total": 999.99, "status": "shipped", "created_at": "2024-01-10"},
        2: {"id": 2, "user_id": 2, "product_id": 2, "quantity": 2, "total": 159.98, "status": "pending", "created_at": "2024-01-11"},
        3: {"id": 3, "user_id": 1, "product_id": 3, "quantity": 1, "total": 249.99, "status": "paid",    "created_at": "2024-01-12"},
    }
    DB["notes"] = {}
    COUNTERS.update({"users": 3, "products": 4, "orders": 3, "notes": 0})
    return {"success": True, "message": "Database reset to seed data"}