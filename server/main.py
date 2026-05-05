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


def run_server() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    port = int(os.getenv("PORT", "8000"))
    host = "0.0.0.0"

    if transport == "stdio":
        print("[inventory-mcp] Starting with STDIO transport", flush=True)
        mcp.run(transport="stdio")
        return

    if transport in {"http", "streamable-http"}:
        print(
            f"[inventory-mcp] Starting with HTTP transport "
            f"(requested={transport}, host={host}, port={port}, endpoint=/mcp/)",
            flush=True,
        )
        mcp.run(transport=transport, host=host, port=port)
        return

    raise ValueError(
        "Unsupported MCP_TRANSPORT value. Use 'stdio', 'http', or 'streamable-http'."
    )


if __name__ == "__main__":
    run_server()
