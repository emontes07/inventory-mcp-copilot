# Inventory IQ

Inventory IQ is a Microsoft 365 Copilot declarative agent demo backed by a remote MCP server for a fictional Zava Athletic Supply inventory scenario. This repo is intentionally scaffold-first: it gives us a clean starting point for inventory tools, HTML widgets, and Azure deployment without locking us into final business logic too early.

## Project purpose

- Demonstrate how a Microsoft 365 Copilot declarative agent can call a remote MCP server for inventory workflows.
- Model a reusable apparel, footwear, and accessories inventory scenario with products, suppliers, stock levels, reorder levels, units on order, unit price, average discount, inventory valuation, and revenue this period.
- Start with local JSON data and server-rendered HTML widgets so the demo stays easy to understand and easy to evolve.

## Architecture

```text
Microsoft 365 Copilot Declarative Agent
        |
        v
Remote FastMCP Server
        |
        +-- Inventory tools
        +-- Supplier tools
        +-- Reorder / order tools
        |
        +-- Local JSON data
        +-- HTML widgets (Jinja2-ready)
        +-- Static assets
```

Key directories:

- `server/`: FastMCP server, tool modules, local data, widgets, and static assets.
- `agent/`: notes for wiring this repo to a Microsoft 365 Copilot declarative agent.
- `infra/`: placeholder Azure Container Apps deployment artifacts.
- `docs/`: demo flow and future development prompts.

## Local run instructions

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r server/requirements.txt
```

3. For local development, run the server from the `server/` directory.

### STDIO mode

Run the server locally with the default STDIO transport:

```bash
cd server
python3 main.py
```

Test STDIO mode with MCP Inspector:

```bash
cd server
npx @modelcontextprotocol/inspector python3 main.py
```

### HTTP mode

Run the server locally in remote-style HTTP mode:

```bash
cd server
MCP_TRANSPORT=streamable-http PORT=8000 python3 main.py
```

Test whether HTTP mode is listening:

```bash
curl -i http://127.0.0.1:8000/mcp/
```

Any HTTP response means the listener is up. Depending on the request method and FastMCP version, you may see a `200`, `404`, or `405` rather than a full MCP response.

### Notes

If you prefer running from the repo root, use:

```bash
python3 server/main.py
```

- The current scaffold uses FastMCP with placeholder inventory tools and local JSON data.
- The sample company is the fictional brand `Zava Athletic Supply`.
- `MCP_TRANSPORT` defaults to `stdio`; set it to `http` or `streamable-http` for remote hosting.
- HTTP mode binds to `0.0.0.0:${PORT}` and is intended for Azure Container Apps or other remote runtimes.
- Widgets are rendered from files in `server/widgets/`.
- The widget contract is intentionally simple so we can replace the HTML layer with React later without rewriting the tool shapes.

## Example tool inputs

Use these example arguments when testing the current inventory tools in MCP Inspector or another MCP client:

`list_products`

```json
{}
```

`get_product_card` with product ID

```json
{
  "product_id": "P-2001"
}
```

`get_product_card` with product name

```json
{
  "product_name": "Zava Runner Pro"
}
```

`get_product_card` with partial query

```json
{
  "query": "runner"
}
```

`get_edit_product_form` with product name

```json
{
  "product_name": "Zava Runner Pro"
}
```

`inventory_summary`

```json
{}
```

## Planned Azure Container Apps deployment

- Package the FastMCP server into a container using `server/Dockerfile`.
- Deploy the container to Azure Container Apps with the starter files in `infra/`.
- Configure `MCP_TRANSPORT=streamable-http` and `PORT=8000` or an Azure-provided port.
- Connect the public remote MCP endpoint to a Microsoft 365 Copilot declarative agent.

## Azure deployment status

- Container App name: `inventory-iq-mcp`
- Resource group: `rg-inventory-iq-mcp`
- Azure Container Apps environment: `env-inventory-iq-mcp`
- MCP endpoint: `https://inventory-iq-mcp.salmonplant-7b75dc6d.westus3.azurecontainerapps.io/mcp`

### Endpoint behavior

- A plain `curl` request against `/mcp` returns HTTP `406`.
- The `406` response with `Client must accept text/event-stream` is expected.
- That `406` confirms the MCP route is alive, but it is not a full MCP validation.
- Use MCP Inspector for real validation with `Transport Type = Streamable HTTP`.

Example:

```bash
curl -i https://inventory-iq-mcp.salmonplant-7b75dc6d.westus3.azurecontainerapps.io/mcp
```

### MCP Inspector validation

Use these settings in MCP Inspector:

- URL: `https://inventory-iq-mcp.salmonplant-7b75dc6d.westus3.azurecontainerapps.io/mcp`
- Transport Type: `Streamable HTTP`
- Connection Type: `Via Proxy`

After connecting, test `get_product_card` with:

```json
{
  "product_name": "Zava Runner Pro"
}
```

## Microsoft 365 Copilot note

This project is intended to be connected to a Microsoft 365 Copilot declarative agent through Microsoft 365 Agents Toolkit. The agent definition itself is expected to be created separately, with this repo serving as the MCP backend and implementation reference.

## macOS localhost note

When testing the Streamable HTTP transport locally, use:

http://127.0.0.1:8000/mcp

instead of:

http://localhost:8000/mcp

On macOS, some tools resolve localhost to the IPv6 address ::1. If the MCP server is listening on IPv4, this can cause ECONNREFUSED ::1:8000.
