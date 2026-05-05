# Inventory IQ

Inventory IQ is a Microsoft 365 Copilot declarative agent demo backed by a remote MCP server for a generic Northwind-style inventory scenario. This repo is intentionally scaffold-first: it gives us a clean starting point for inventory tools, HTML widgets, and Azure deployment without locking us into final business logic too early.

## Project purpose

- Demonstrate how a Microsoft 365 Copilot declarative agent can call a remote MCP server for inventory workflows.
- Model a reusable inventory scenario with products, suppliers, stock levels, reorder levels, units on order, unit price, average discount, inventory valuation, and revenue this period.
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

3. Start the scaffolded MCP server:

```bash
python server/main.py
```

Notes:

- The current scaffold uses FastMCP with placeholder inventory tools and local JSON data.
- Widgets are rendered from files in `server/widgets/`.
- The widget contract is intentionally simple so we can replace the HTML layer with React later without rewriting the tool shapes.

## Planned Azure Container Apps deployment

- Package the FastMCP server into a container using `server/Dockerfile`.
- Deploy the container to Azure Container Apps with the starter files in `infra/`.
- Configure environment variables for host, port, and transport as the remote MCP hosting model is finalized.
- Connect the public remote MCP endpoint to a Microsoft 365 Copilot declarative agent.

## Microsoft 365 Copilot note

This project is intended to be connected to a Microsoft 365 Copilot declarative agent through Microsoft 365 Agents Toolkit. The agent definition itself is expected to be created separately, with this repo serving as the MCP backend and implementation reference.
