from __future__ import annotations

from pathlib import Path

from fastmcp.resources.base import ResourceResult
from fastmcp.utilities.mime import UI_MIME_TYPE
from jinja2 import Environment, FileSystemLoader, select_autoescape

from tools.inventory import PRODUCT_CARD_WIDGET_URI, register_inventory_tools

SERVER_DIR = Path(__file__).resolve().parent
WIDGETS_DIR = SERVER_DIR / "widgets"
STYLES_PATH = SERVER_DIR / "static" / "styles.css"

templates = Environment(
    loader=FileSystemLoader(WIDGETS_DIR),
    autoescape=select_autoescape(enabled_extensions=("html", "xml")),
)
INLINE_STYLES = STYLES_PATH.read_text()


class StubMCP:
    def __init__(self) -> None:
        self.tools: dict[str, dict[str, object]] = {}
        self.resources: dict[str, dict[str, object]] = {}

    def tool(self, *args, **kwargs):
        def decorator(fn):
            self.tools[fn.__name__] = {"fn": fn, "kwargs": kwargs}
            return fn

        return decorator

    def resource(self, uri, **kwargs):
        def decorator(fn):
            self.resources[uri] = {"fn": fn, "kwargs": kwargs}
            return fn

        return decorator


def render_widget(template_name: str, **context: object) -> str:
    return templates.get_template(template_name).render(**context)


def render_widget_document(template_name: str, *, title: str, **context: object) -> str:
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


def main() -> None:
    stub = StubMCP()
    register_inventory_tools(stub, render_widget, render_widget_document)

    resource_entry = stub.resources[PRODUCT_CARD_WIDGET_URI]
    resource_fn = resource_entry["fn"]
    template_mime = resource_entry["kwargs"]["mime_type"]

    raw_result = resource_fn("P-2001")
    if not isinstance(raw_result, ResourceResult):
        raise TypeError(f"Expected ResourceResult, got {type(raw_result).__name__}")

    mcp_result = raw_result.to_mcp_result("ui://inventory/product-card/P-2001")
    first_content = mcp_result.contents[0]

    assert template_mime == UI_MIME_TYPE, template_mime
    assert first_content.mimeType == UI_MIME_TYPE, first_content.mimeType
    assert str(first_content.uri) == "ui://inventory/product-card/P-2001", first_content.uri
    assert first_content.text.startswith("<!DOCTYPE html>"), first_content.text[:40]
    assert not first_content.text.startswith("&lt;!DOCTYPE html&gt;"), first_content.text[:40]

    tool_result = stub.tools["get_product_card"]["fn"](product_id="P-2001")
    assert tool_result.structured_content["status"] == "ok"
    assert tool_result.structured_content["widget"]["resource_uri"] == "ui://inventory/product-card/P-2001"
    assert tool_result.meta["ui"]["resourceUri"] == "ui://inventory/product-card/P-2001"

    print("template_mime", template_mime)
    print("read_mime", first_content.mimeType)
    print("resource_uri", first_content.uri)
    print("raw_html", first_content.text[:30])
    print("tool_status", tool_result.structured_content["status"])


if __name__ == "__main__":
    main()
