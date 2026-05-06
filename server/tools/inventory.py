from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from fastmcp.resources.base import ResourceContent, ResourceResult
from fastmcp.tools.base import ToolResult
from fastmcp.utilities.mime import UI_MIME_TYPE
from mcp.types import ResourceLink, TextContent

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PRODUCT_CARD_WIDGET_URI = "ui://inventory/product-card/{product_id}"
INLINE_PRODUCT_CARD_WIDGET_ID = "ui://inventory/product-card.html"


def _load_products() -> list[dict[str, Any]]:
    products = json.loads((DATA_DIR / "products.json").read_text())
    return [_normalize_product(product) for product in products]


def _normalize_stock_status_code(
    raw_status: str | None,
    stock_level: int,
    reorder_level: int,
) -> str:
    normalized = (raw_status or "").strip().lower()

    if normalized in {"out", "out-of-stock", "out of stock"} or stock_level <= 0:
        return "out"

    if normalized in {"low", "reorder-soon", "reorder soon", "low stock"}:
        return "low"

    if normalized in {"healthy", "in stock", "in-stock"}:
        return "healthy"

    if stock_level <= reorder_level:
        return "low"

    return "healthy"


def _normalize_stock_status_label(stock_status_code: str) -> str:
    labels = {
        "healthy": "In stock",
        "low": "Low stock",
        "out": "Out of stock",
    }
    return labels.get(stock_status_code, "In stock")


def _normalize_product(product: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(product)
    stock_status_code = _normalize_stock_status_code(
        raw_status=str(product.get("stock_status", "")),
        stock_level=int(product["stock_level"]),
        reorder_level=int(product["reorder_level"]),
    )
    normalized["stock_status_code"] = stock_status_code
    normalized["stock_status"] = _normalize_stock_status_label(stock_status_code)
    return normalized


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


def _build_product_card_widget_uri(product_id: str) -> str:
    return PRODUCT_CARD_WIDGET_URI.format(product_id=product_id)


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


def register_inventory_tools(
    mcp: Any,
    render_widget: Callable[..., str],
    render_widget_document: Callable[..., str],
) -> None:
    @mcp.resource(
        PRODUCT_CARD_WIDGET_URI,
        name="inventory_product_card_widget",
        title="Inventory Product Card",
        description="Read-only product detail card for Inventory IQ.",
        mime_type=UI_MIME_TYPE,
        app={"prefersBorder": True},
    )
    def product_card_widget_resource(product_id: str) -> ResourceResult:
        products = _load_products()
        widget_uri = _build_product_card_widget_uri(product_id.strip())
        product = next(
            (item for item in products if item["id"].lower() == product_id.strip().lower()),
            None,
        )

        if product is None:
            html = """<!DOCTYPE html>
<html lang="en">
  <body>
    <section class="widget product-card">
      <header class="widget-header product-card-header">
        <div class="product-card-title-block">
          <p class="eyebrow">Inventory IQ · Zava Athletic Supply</p>
          <div class="product-card-title-row">
            <h2>Product not found</h2>
            <span class="status-pill status-danger">Unavailable</span>
          </div>
          <p class="product-card-sku">Requested product ID was not found.</p>
        </div>
      </header>
    </section>
  </body>
</html>
"""
            return ResourceResult(
                [
                    ResourceContent(
                        html,
                        mime_type=UI_MIME_TYPE,
                        meta={
                            "ui": {
                                "prefersBorder": True,
                            }
                        },
                    )
                ]
            )

        html = render_widget_document(
            "product_card.html",
            title=f"{product['product_name']} · Inventory IQ",
            product=product,
        )
        return ResourceResult(
            [
                ResourceContent(
                    html,
                    mime_type=UI_MIME_TYPE,
                    meta={
                        "ui": {
                            "prefersBorder": True,
                        }
                    },
                )
            ],
            meta={
                "ui": {
                    "resourceUri": widget_uri,
                    "prefersBorder": True,
                }
            },
        )

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
            or product["stock_status_code"] == "low"
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
            normalized_filter = stock_status.strip().lower()
            filtered = [
                product
                for product in filtered
                if product["stock_status"].lower() == normalized_filter
                or product["stock_status_code"] == normalized_filter
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

    @mcp.tool(
        app={
            "visibility": ["model"],
            "prefersBorder": True,
        }
    )
    def get_product_card(
        product_id: str | None = None,
        product_name: str | None = None,
        query: str | None = None,
    ) -> ToolResult:
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
        widget_uri = _build_product_card_widget_uri(product["id"])
        inline_widget_document = render_widget_document(
            "product_card.html",
            title=f"{product['product_name']} · Inventory IQ",
            product=product,
        )
        structured_payload = {
            "status": "ok",
            "product": product,
            "widget_resource_uri": widget_uri,
        }

        return ToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Product card ready for {product['product_name']}.",
                ),
                ResourceLink(
                    type="resource_link",
                    name="product_card_widget",
                    title=f"{product['product_name']} product card",
                    uri=widget_uri,
                    description="Renderable Inventory IQ product card widget.",
                    mimeType=UI_MIME_TYPE,
                ),
            ],
            structured_content=structured_payload,
            meta={
                "ui": {
                    "html": inline_widget_document,
                    "widget": INLINE_PRODUCT_CARD_WIDGET_ID,
                    "params": {
                        "product_id": product["id"],
                    },
                    "priority": "primary",
                    "presentation": "inline",
                    "prefersBorder": True,
                }
            },
        )

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
