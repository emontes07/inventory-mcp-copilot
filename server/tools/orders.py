from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_products() -> list[dict[str, Any]]:
    return json.loads((DATA_DIR / "products.json").read_text())


def _load_movements() -> list[dict[str, Any]]:
    return json.loads((DATA_DIR / "inventory_movements.json").read_text())


def register_order_tools(mcp: Any, render_widget: Callable[..., str]) -> None:
    @mcp.tool()
    def get_reorder_recommendations(limit: int = 5) -> dict[str, Any]:
        """Suggest products that may need replenishment soon."""

        products = _load_products()
        candidates = []
        for product in products:
            gap = product["reorder_level"] - product["stock_level"]
            if gap >= 0:
                candidates.append(
                    {
                        "id": product["id"],
                        "product_name": product["product_name"],
                        "supplier_id": product["supplier_id"],
                        "supplier_name": product["supplier_name"],
                        "stock_level": product["stock_level"],
                        "reorder_level": product["reorder_level"],
                        "units_on_order": product["units_on_order"],
                        "stock_status": product["stock_status"],
                        "recommended_action": product["recommended_action"],
                        "suggested_order_qty": max(gap + 10 - product["units_on_order"], 0),
                    }
                )

        recommendations = sorted(
            candidates,
            key=lambda item: (item["stock_level"] - item["reorder_level"], item["units_on_order"]),
        )[:limit]

        return {
            "recommendations": recommendations,
            "widget": {
                "template": "reorder_recommendation.html",
                "framework_hint": "server-rendered-html",
                "html": render_widget(
                    "reorder_recommendation.html",
                    recommendations=recommendations,
                ),
            },
        }

    @mcp.tool()
    def revenue_snapshot() -> dict[str, Any]:
        """Return a simple revenue snapshot based on product aggregates."""

        products = _load_products()
        total_revenue = sum(product["revenue_this_period"] for product in products)
        average_discount = sum(product["average_discount"] for product in products) / max(
            len(products), 1
        )

        return {
            "revenue_this_period": round(total_revenue, 2),
            "average_discount": round(average_discount, 4),
            "notes": [
                "Revenue values are sample data for the initial demo scaffold.",
                "Replace with period-aware logic once transaction history is modeled in detail.",
            ],
        }

    @mcp.tool()
    def create_purchase_order_draft(product_id: str, requested_units: int | None = None) -> dict[str, Any]:
        """Build a draft replenishment recommendation without persisting anything."""

        products = _load_products()
        movements = _load_movements()
        product = next((item for item in products if item["id"] == product_id), None)
        if not product:
            return {"error": f"Product '{product_id}' was not found."}

        recent_activity = [item for item in movements if item["product_id"] == product_id][:5]
        suggested_units = requested_units or max(
            (product["reorder_level"] + 10) - (product["stock_level"] + product["units_on_order"]),
            0,
        )

        return {
            "status": "draft",
            "purchase_order": {
                "product_id": product_id,
                "product_name": product["product_name"],
                "supplier_id": product["supplier_id"],
                "supplier_name": product["supplier_name"],
                "suggested_units": suggested_units,
                "unit_price": product["unit_price"],
                "estimated_total": round(suggested_units * product["unit_price"], 2),
            },
            "recent_activity": recent_activity,
            "message": "Draft only. Persistence and approval workflows are still to be implemented.",
        }
