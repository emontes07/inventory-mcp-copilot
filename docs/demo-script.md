# Demo Script

## Demo storyline

Inventory IQ helps an operations or purchasing user ask natural-language questions about stock position, supplier context, and reorder needs through Microsoft 365 Copilot.

## Suggested sequence

1. Ask for an inventory summary.
2. Ask which products are below or near reorder level.
3. Open a product card for a low-stock item.
4. Ask who supplies that item and what the supplier lead time is.
5. Ask for reorder recommendations.
6. Ask for a draft purchase order for a selected product.

## Talking points

- The agent is backed by a remote MCP server rather than hard-coded prompt logic.
- Tool responses combine structured JSON with HTML widgets for richer Copilot experiences.
- The scaffold uses local JSON now, but the same tool contracts can later move to a database or ERP integration.
