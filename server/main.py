from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from jinja2 import Environment, FileSystemLoader, select_autoescape

from tools import register_inventory_tools, register_order_tools, register_supplier_tools

SERVER_DIR = Path(__file__).resolve().parent
WIDGETS_DIR = SERVER_DIR / "widgets"

templates = Environment(
    loader=FileSystemLoader(WIDGETS_DIR),
    autoescape=select_autoescape(enabled_extensions=("html", "xml")),
)


def render_widget(template_name: str, **context: Any) -> str:
    """Render a server-side widget from a template.

    Tool responses return both structured data and a rendered HTML fragment so
    the presentation layer can later be swapped from Jinja/HTML to React while
    preserving the same data contract.
    """

    return templates.get_template(template_name).render(**context)


def create_server() -> FastMCP:
    mcp = FastMCP("inventory-mcp")

    @mcp.tool()
    def health_check() -> dict[str, Any]:
        """Return a simple health payload for local validation."""

        return {
            "status": "ok",
            "server": "inventory-mcp",
            "widgets_directory": str(WIDGETS_DIR),
        }

    register_inventory_tools(mcp, render_widget)
    register_supplier_tools(mcp, render_widget)
    register_order_tools(mcp, render_widget)
    return mcp


mcp = create_server()


if __name__ == "__main__":
    transport = os.getenv("FASTMCP_TRANSPORT", "stdio")
    try:
        mcp.run(transport=transport)
    except TypeError:
        # Keeps the scaffold usable across FastMCP versions with slightly
        # different run signatures while we wire up the final remote transport.
        mcp.run()
