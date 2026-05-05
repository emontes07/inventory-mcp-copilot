# Declarative Agent Notes

## Initial capabilities

- Summarize inventory posture.
- Look up product details.
- Show supplier information.
- Recommend reorder candidates.
- Draft replenishment actions without persistence.

## Suggested tool mapping

- `inventory_summary`: dashboard and daily-brief style prompts.
- `list_products`: filtered inventory discovery.
- `get_product_card`: rich product inspection.
- `get_supplier_details`: vendor context for purchasing questions.
- `get_reorder_recommendations`: replenishment guidance.
- `create_purchase_order_draft`: action-oriented follow-up flow.

## Widget strategy

- Current approach: server-rendered HTML fragments from Jinja2 templates.
- Future approach: preserve response props so widgets can later be reimplemented in React.
- Avoid embedding business logic inside widgets; keep widgets presentational.
