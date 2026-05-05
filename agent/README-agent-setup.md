# Agent Setup Notes

This repo does not create the Microsoft 365 Copilot declarative agent directly. Instead, it prepares the MCP backend that the agent will call.

Suggested setup flow:

1. Deploy the MCP server to a reachable HTTPS endpoint.
2. Open Microsoft 365 Agents Toolkit and create a new declarative agent project.
3. Configure the agent to use the remote MCP server endpoint exposed by this repo.
4. Map initial prompts toward inventory lookup, supplier lookup, reorder guidance, and draft replenishment actions.
5. Validate widget rendering and tool output formatting inside Microsoft 365 Copilot.

Keep the agent definition and this server loosely coupled so either side can evolve independently.
