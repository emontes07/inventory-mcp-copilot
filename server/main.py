from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from jinja2 import Environment, FileSystemLoader, select_autoescape

from tools import register_inventory_tools, register_order_tools, register_supplier_tools

SERVER_DIR = Path(__file__).resolve().parent
WIDGETS_DIR = SERVER_DIR / "widgets"
STATIC_DIR = SERVER_DIR / "static"
STYLES_PATH = STATIC_DIR / "styles.css"

templates = Environment(
    loader=FileSystemLoader(WIDGETS_DIR),
    autoescape=select_autoescape(enabled_extensions=("html", "xml")),
)
INLINE_STYLES = STYLES_PATH.read_text()


def render_widget(template_name: str, **context: Any) -> str:
    """Render a server-side widget from a template.

    Tool responses return both structured data and a rendered HTML fragment so
    the presentation layer can later be swapped from Jinja/HTML to React while
    preserving the same data contract.
    """

    return templates.get_template(template_name).render(**context)


def render_widget_document(template_name: str, *, title: str, **context: Any) -> str:
    """Render a full HTML document for MCP App UI resources."""

    fragment = render_widget(template_name, **context)
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <style>
{INLINE_STYLES}
    </style>
  </head>
  <body>
    {fragment}
  </body>
</html>
"""


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

    register_inventory_tools(mcp, render_widget, render_widget_document)
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
