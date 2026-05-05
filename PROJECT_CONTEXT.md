# Inventory IQ - MCP + Microsoft 365 Copilot Declarative Agent Demo

This project builds a Microsoft 365 Copilot declarative agent demo called Inventory IQ.

The goal is to modernize a previous inventory adaptive card demo into a Copilot-native MCP-based architecture.

## Target architecture

Microsoft 365 Copilot Declarative Agent
→ Remote MCP Server
→ Inventory tools
→ Structured JSON data
→ Rich HTML/React-style widgets rendered in Copilot

## Important design goals

- Do not use Costa Coffee or frontline branding.
- Do not fork or inherit visuals from Scott Adams' retail MCP repo.
- Use the retail MCP repo only as a reference for MCP server patterns, tool responses, and widget binding.
- Build a clean Northwind-style inventory scenario.
- Prioritize reusable demo value for retail, CPG, manufacturing, logistics, and operations customers.
- Use Python + FastMCP for the server.
- Use JSON files as the first data source.
- Use HTML/Jinja2 widgets first, with a path to React later.
- Prepare the MCP server for Azure Container Apps hosting.
- The Microsoft 365 Copilot declarative agent will be created separately using Microsoft 365 Agents Toolkit.

## Agent name

Inventory IQ

## Repo name

inventory-mcp-copilot

## MCP server name

inventory-mcp