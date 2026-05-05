from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_products() -> list[dict[str, Any]]:
    return json.loads((DATA_DIR / "products.json").read_text())


def _load_suppliers() -> list[dict[str, Any]]:
    return json.loads((DATA_DIR / "suppliers.json").read_text())


def register_supplier_tools(mcp: Any, render_widget: Callable[..., str]) -> None:
    @mcp.tool()
    def list_suppliers() -> dict[str, Any]:
        """List all suppliers in the inventory dataset."""

        suppliers = _load_suppliers()
        return {
            "suppliers": suppliers,
            "count": len(suppliers),
        }

    @mcp.tool()
    def get_supplier_details(supplier_id: str) -> dict[str, Any]:
        """Return a supplier plus the products currently sourced from them."""

        suppliers = _load_suppliers()
        products = _load_products()
        supplier = next((item for item in suppliers if item["id"] == supplier_id), None)

        if not supplier:
            return {"error": f"Supplier '{supplier_id}' was not found."}

        supplied_products = [product for product in products if product["supplier_id"] == supplier_id]
        return {
            "supplier": supplier,
            "products": supplied_products,
            "product_count": len(supplied_products),
            "notes": [
                "Supplier analytics are intentionally thin in the initial scaffold.",
                "This tool is ready for lead time, fill rate, and vendor risk extensions.",
            ],
        }
