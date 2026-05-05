from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_products() -> list[dict[str, Any]]:
    return json.loads((DATA_DIR / "products.json").read_text())


def register_inventory_tools(mcp: Any, render_widget: Callable[..., str]) -> None:
    @mcp.tool()
    def inventory_summary() -> dict[str, Any]:
        """Return a high-level inventory snapshot."""

        products = _load_products()
        inventory_value = sum(product["inventory_valuation"] for product in products)
        revenue = sum(product["revenue_this_period"] for product in products)
        low_stock = [
            product for product in products if product["stock_level"] <= product["reorder_level"]
        ]

        return {
            "summary": {
                "product_count": len(products),
                "inventory_valuation": round(inventory_value, 2),
                "revenue_this_period": round(revenue, 2),
                "low_stock_count": len(low_stock),
            },
            "notes": [
                "Business logic is intentionally lightweight in this scaffold.",
                "Use this tool as the starting point for dashboard-style Copilot answers.",
            ],
        }

    @mcp.tool()
    def list_products(category: str | None = None, low_stock_only: bool = False) -> dict[str, Any]:
        """List products with optional category and low-stock filtering."""

        products = _load_products()
        filtered = products

        if category:
            filtered = [
                product
                for product in filtered
                if product["category"].lower() == category.strip().lower()
            ]

        if low_stock_only:
            filtered = [
                product
                for product in filtered
                if product["stock_level"] <= product["reorder_level"]
            ]

        return {
            "products": filtered,
            "count": len(filtered),
        }

    @mcp.tool()
    def get_product_card(product_id: str) -> dict[str, Any]:
        """Return structured product data plus a rendered HTML card widget."""

        products = _load_products()
        product = next((item for item in products if item["id"] == product_id), None)
        if not product:
            return {
                "error": f"Product '{product_id}' was not found.",
                "available_product_ids": [item["id"] for item in products],
            }

        return {
            "product": product,
            "widget": {
                "template": "product_card.html",
                "framework_hint": "server-rendered-html",
                "html": render_widget("product_card.html", product=product),
            },
        }

    @mcp.tool()
    def get_edit_product_form(product_id: str) -> dict[str, Any]:
        """Return a placeholder edit form widget for future write scenarios."""

        products = _load_products()
        product = next((item for item in products if item["id"] == product_id), None)
        if not product:
            return {"error": f"Product '{product_id}' was not found."}

        return {
            "product": product,
            "status": "placeholder",
            "message": "Edit workflows are scaffolded but not persisted yet.",
            "widget": {
                "template": "edit_product.html",
                "framework_hint": "server-rendered-html",
                "html": render_widget("edit_product.html", product=product),
            },
        }
