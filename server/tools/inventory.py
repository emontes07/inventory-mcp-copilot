from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_products() -> list[dict[str, Any]]:
    return json.loads((DATA_DIR / "products.json").read_text())


def _coerce_lookup_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    normalized = value.strip()
    return normalized or None


def _matches_partial_query(product: dict[str, Any], query: str) -> bool:
    query_lower = query.lower()
    searchable_fields = (
        product["id"],
        product["sku"],
        product["product_name"],
        product["category"],
        product["subcategory"],
        product["color"],
        product["supplier_name"],
        product["season"],
    )
    return any(query_lower in str(field).lower() for field in searchable_fields)


def _build_available_products(products: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "product_id": product["id"],
            "product_name": product["product_name"],
        }
        for product in products
    ]


def _build_multiple_matches(matches: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "multiple_matches",
        "message": "Multiple products matched your request.",
        "matches": [
            {
                "product_id": product["id"],
                "sku": product["sku"],
                "product_name": product["product_name"],
                "category": product["category"],
                "stock_status": product["stock_status"],
            }
            for product in matches
        ],
    }


def _build_not_found(products: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "not_found",
        "message": "No product matched your request.",
        "available_products": _build_available_products(products),
    }


def resolve_product(
    products: list[dict[str, Any]],
    product_id: str | None = None,
    product_name: str | None = None,
    query: str | None = None,
) -> dict[str, Any]:
    normalized_id = _coerce_lookup_text(product_id)
    if normalized_id:
        matches = [product for product in products if product["id"].lower() == normalized_id.lower()]
        if len(matches) == 1:
            return {"status": "ok", "product": matches[0]}
        if len(matches) > 1:
            return _build_multiple_matches(matches)
        return _build_not_found(products)

    normalized_name = _coerce_lookup_text(product_name)
    if normalized_name:
        exact_name_matches = [
            product
            for product in products
            if product["product_name"].lower() == normalized_name.lower()
        ]
        if len(exact_name_matches) == 1:
            return {"status": "ok", "product": exact_name_matches[0]}
        if len(exact_name_matches) > 1:
            return _build_multiple_matches(exact_name_matches)

        partial_name_matches = [
            product
            for product in products
            if normalized_name.lower() in product["product_name"].lower()
        ]
        if len(partial_name_matches) == 1:
            return {"status": "ok", "product": partial_name_matches[0]}
        if len(partial_name_matches) > 1:
            return _build_multiple_matches(partial_name_matches)
        return _build_not_found(products)

    normalized_query = _coerce_lookup_text(query)
    if normalized_query:
        matches = [product for product in products if _matches_partial_query(product, normalized_query)]
        if len(matches) == 1:
            return {"status": "ok", "product": matches[0]}
        if len(matches) > 1:
            return _build_multiple_matches(matches)
        return _build_not_found(products)

    return {
        "status": "not_found",
        "message": "No product matched your request.",
        "available_products": _build_available_products(products),
    }


def register_inventory_tools(mcp: Any, render_widget: Callable[..., str]) -> None:
    @mcp.tool()
    def inventory_summary() -> dict[str, Any]:
        """Return a high-level inventory snapshot."""

        products = _load_products()
        inventory_value = sum(product["inventory_valuation"] for product in products)
        revenue = sum(product["revenue_this_period"] for product in products)
        low_stock = [
            product
            for product in products
            if product["stock_level"] <= product["reorder_level"]
            or product["stock_status"] in {"low", "reorder-soon"}
        ]
        total_units_on_order = sum(product["units_on_order"] for product in products)
        average_discount = sum(product["average_discount"] for product in products) / max(
            len(products), 1
        )
        average_sell_through = sum(product["sell_through_rate"] for product in products) / max(
            len(products), 1
        )
        category_counts = Counter(product["category"] for product in products)
        channel_counts = Counter(product["channel"] for product in products)

        return {
            "summary": {
                "company_name": "Zava Athletic Supply",
                "product_count": len(products),
                "total_units_on_hand": sum(product["stock_level"] for product in products),
                "total_units_on_order": total_units_on_order,
                "inventory_valuation": round(inventory_value, 2),
                "revenue_this_period": round(revenue, 2),
                "average_discount": round(average_discount, 4),
                "average_sell_through_rate": round(average_sell_through, 4),
                "low_stock_count": len(low_stock),
                "categories": dict(sorted(category_counts.items())),
                "channels": dict(sorted(channel_counts.items())),
            },
            "notes": [
                "Zava Athletic Supply is a fictional demo company for apparel, footwear, and accessories inventory.",
                "Business logic remains intentionally lightweight in this scaffold.",
            ],
        }

    @mcp.tool()
    def list_products(
        category: str | None = None,
        channel: str | None = None,
        stock_status: str | None = None,
        query: str | None = None,
        low_stock_only: bool = False,
    ) -> dict[str, Any]:
        """List products with optional category, channel, status, and query filtering."""

        products = _load_products()
        filtered = products

        if category:
            filtered = [
                product
                for product in filtered
                if product["category"].lower() == category.strip().lower()
            ]

        if channel:
            filtered = [
                product
                for product in filtered
                if product["channel"].lower() == channel.strip().lower()
            ]

        if stock_status:
            filtered = [
                product
                for product in filtered
                if product["stock_status"].lower() == stock_status.strip().lower()
            ]

        if low_stock_only:
            filtered = [
                product
                for product in filtered
                if product["stock_level"] <= product["reorder_level"]
            ]

        if query:
            normalized_query = query.strip()
            filtered = [
                product
                for product in filtered
                if normalized_query and _matches_partial_query(product, normalized_query)
            ]

        return {
            "products": filtered,
            "count": len(filtered),
        }

    @mcp.tool()
    def get_product_card(
        product_id: str | None = None,
        product_name: str | None = None,
        query: str | None = None,
    ) -> dict[str, Any]:
        """Return structured product data plus a rendered HTML card widget."""

        products = _load_products()
        resolution = resolve_product(
            products,
            product_id=product_id,
            product_name=product_name,
            query=query,
        )
        if resolution["status"] != "ok":
            return resolution

        product = resolution["product"]

        return {
            "status": "ok",
            "product": product,
            "widget": {
                "template": "product_card.html",
                "framework_hint": "server-rendered-html",
                "html": render_widget("product_card.html", product=product),
            },
        }

    @mcp.tool()
    def get_edit_product_form(
        product_id: str | None = None,
        product_name: str | None = None,
        query: str | None = None,
    ) -> dict[str, Any]:
        """Return a placeholder edit form widget for future write scenarios."""

        products = _load_products()
        resolution = resolve_product(
            products,
            product_id=product_id,
            product_name=product_name,
            query=query,
        )
        if resolution["status"] != "ok":
            return resolution

        product = resolution["product"]

        return {
            "status": "placeholder",
            "product": product,
            "message": "Edit workflows are scaffolded but not persisted yet.",
            "widget": {
                "template": "edit_product.html",
                "framework_hint": "server-rendered-html",
                "html": render_widget("edit_product.html", product=product),
            },
        }
